#!/usr/bin/env node
/**
 * QHAP-TRADER: offline live-readiness inventory + PAPER-ONLY pretrade firewall.
 *
 * Non-executable by construction: imports no HTTP or broker SDK, has no credential
 * handling, and never exposes a function that submits or authorizes a live order.
 * A client-supplied "verified" value does not establish external certification.
 * Research prototype; NOT a production RMS or a regulatory approval.
 */
import { fileURLToPath } from 'node:url';
import path from 'node:path';

export const POLICY = Object.freeze({
  simulatedCapitalRupees: 10000,
  maxSinglePositionRupees: 2500,
  maxGrossExposureRupees: 2500,
  minUncommittedCashRupees: 4000,
  maxLossPerCandidateRupees: 50,
  dailyLossLockRupees: 100,
  weeklyLossLockRupees: 300,
  peakDrawdownLockRupees: 800,
  maxVirtualEntriesPerSession: 2,
  maxSpreadBps: 15,
  maxExchangeBookAgeMs: 2000,
  maxClockSkewMs: 500,
  entryStartIstMinute: 9 * 60 + 30,
  lastEntryIstMinute: 14 * 60 + 30,
});

/** These are requirements to document, not a certificate creator. */
export const REVIEW_ITEMS = Object.freeze([
  'independently_verified_post_cost_holdout',
  'forward_paper_sessions_at_least_60',
  'strategy_version_frozen_and_reviewed',
  'market_data_use_rights_confirmed_by_provider',
  'broker_trading_account_eligible_and_active',
  'broker_api_trading_app_approved',
  'upstox_oauth_trading_scope_not_analytics_token',
  'registered_unique_static_ip_and_network_verified',
  'applicable_algo_name_registration_and_order_tagging',
  'applicable_exchange_and_sebi_compliance_review',
  'broker_specific_cash_margin_and_risk_limits',
  'independent_clock_and_market_session_source',
  'certified_book_updates_and_instrument_metadata',
  'order_state_reconciliation_and_idempotency',
  'emergency_kill_switch_and_operator_alerts',
  'recovery_from_partial_fills_disconnects_and_rejections',
  'closeout_rehearsal_and_broker_squareoff_constraints',
  'credentials_secret_storage_rotation_and_access_review',
  'independent_end_to_end_security_and_operations_review',
  'explicit_separate_human_authorization_to_deploy',
]);

const isRecord = v => v !== null && typeof v === 'object' && !Array.isArray(v);
const finite = v => typeof v === 'number' && Number.isFinite(v);
const validMoney = v => finite(v) && v >= 0;
const add = (items, code, condition) => { if (condition) items.push(code); };
const verdict = (status, reasons, extra={}) => ({
  status,
  reasons: [...new Set(reasons)].sort(),
  paperOnly: true,
  brokerOrderEndpointPresent: false,
  realOrderSubmissionPossible: false,
  liveTradingAuthorized: false,
  ...extra
});

/**
 * Inventory only. Every item is externally unverified until independent source
 * documents/authorizations are inspected out of band. Do not trust JSON booleans
 * or user-provided "VERIFIED" strings as legal/financial attestations.
 */
export function assessLiveReadinessInventory(claims={}) {
  if (!isRecord(claims)) return verdict('BLOCKED_INVALID_INPUT', ['INVALID_CLAIMS']);
  const missing = REVIEW_ITEMS.filter(item => claims[item] !== true);
  const claimed = REVIEW_ITEMS.filter(item => claims[item] === true);
  return verdict(missing.length ? 'BLOCKED_REQUIREMENTS_INCOMPLETE' : 'EXTERNAL_REVIEW_REQUIRED', [
    ...missing.map(item => 'MISSING_' + item.toUpperCase()),
    'CLAIMS_ARE_NOT_INDEPENDENT_EVIDENCE',
    'STRATEGY_PROFITABILITY_NOT_CERTIFIED_BY_THIS_SOFTWARE',
    'NO_IMPLEMENTED_OR_APPROVED_LIVE_ORDER_ROUTER'
  ], {
    itemsRequired: REVIEW_ITEMS.length,
    itemsClaimed: claimed.length,
    itemsMissing: missing.length,
    externalSignOffVerifiedBySoftware: false,
    capability: 'PAPER_ONLY_NON_EXECUTABLE_READINESS_INVENTORY'
  });
}

function istClock(iso) {
  if (typeof iso !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,3})?(?:Z|[+-]\d\d:\d\d)$/.test(iso)) return null;
  const date = new Date(iso);
  if (!Number.isFinite(date.getTime())) return null;
  const dateTime = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Asia/Kolkata', weekday: 'short',
    hour: '2-digit', minute: '2-digit', hourCycle: 'h23'
  }).formatToParts(date);
  const dict=Object.fromEntries(dateTime.map(x=>[x.type, x.value]));
  return { minute: Number(dict.hour)*60+Number(dict.minute), weekday:dict.weekday };
}

/**
 * Check a hypothetical BUY candidate with independently tested risk invariants.
 * This function has no broker dependency and CANNOT approve a real order.
 * Synthetic health/account booleans are suitable for unit tests only.
 */
export function assessPaperEntry(intent, account, feed, system, timestampIso) {
  const errors = [];
  if (!isRecord(intent)) return verdict('REJECT', ['INVALID_INTENT']);
  if (!isRecord(account)) return verdict('REJECT', ['INVALID_ACCOUNT']);
  if (!isRecord(feed)) return verdict('REJECT', ['INVALID_FEED']);
  if (!isRecord(system)) return verdict('REJECT', ['INVALID_SYSTEM']);

  add(errors, 'PAPER_MODE_REQUIRED', intent.mode !== 'PAPER');
  add(errors, 'LONG_ONLY_BUY', intent.side !== 'BUY');
  add(errors, 'CASH_INTRADAY_ONLY', intent.product !== 'CASH_INTRADAY');
  add(errors, 'LIMIT_ONLY', intent.orderType !== 'LIMIT');
  add(errors, 'INVALID_INSTRUMENT_KEY',
    typeof intent.instrumentKey !== 'string' ||
    !/^NSE_EQ\|[A-Z0-9]{8,20}$/.test(intent.instrumentKey));

  add(errors, 'INVALID_QUANTITY', !Number.isSafeInteger(intent.quantity) || intent.quantity <= 0);
  add(errors, 'INVALID_LIMIT_PRICE', !finite(intent.limitPrice) || intent.limitPrice <= 0);
  add(errors, 'INVALID_STOP_PRICE', !finite(intent.stopPrice) || intent.stopPrice <= 0 ||
    (finite(intent.limitPrice) && intent.stopPrice >= intent.limitPrice));
  add(errors, 'INVALID_TICK_SIZE', !finite(intent.tickSize) || intent.tickSize <= 0 ||
    intent.tickSize > 1);
  if (finite(intent.limitPrice) && finite(intent.tickSize) && intent.tickSize > 0) {
    const ticks = intent.limitPrice / intent.tickSize;
    add(errors, 'PRICE_NOT_ON_TICK', Math.abs(ticks-Math.round(ticks)) > 1e-6);
  }

  const acctFields=['equityRupees','cashAvailableRupees','grossExposureRupees',
   'dailyPnlRupees','weeklyPnlRupees','peakEquityRupees'];
  add(errors, 'ACCOUNT_NUMBERS_UNVERIFIED', acctFields.some(k=>!finite(account[k])));
  add(errors, 'IN_FLIGHT_ORDERS', account.inFlightOrders !== 0);
  add(errors, 'VIRTUAL_LEDGER_NOT_RECONCILED', account.paperLedgerReconciled !== true);
  add(errors, 'SESSION_ENTRY_COUNTER_UNVERIFIED',
    !Number.isSafeInteger(account.sessionEntries)||account.sessionEntries<0);
  if (acctFields.every(k=>finite(account[k]))) {
    add(errors, 'INVALID_ACCOUNT_BALANCES',
      account.equityRupees<=0 || account.cashAvailableRupees<0 ||
      account.grossExposureRupees<0 || account.peakEquityRupees<account.equityRupees);
    add(errors, 'DAILY_LOSS_LOCK', account.dailyPnlRupees <= -POLICY.dailyLossLockRupees);
    add(errors, 'WEEKLY_LOSS_LOCK', account.weeklyPnlRupees <= -POLICY.weeklyLossLockRupees);
    add(errors, 'DRAWDOWN_LOCK', account.peakEquityRupees-account.equityRupees >= POLICY.peakDrawdownLockRupees);
  }
  if (Number.isSafeInteger(account.sessionEntries)) {
    add(errors, 'ENTRY_COUNT_LOCK', account.sessionEntries >= POLICY.maxVirtualEntriesPerSession);
  }

  add(errors, 'UNVERIFIED_MARKET_STATE', system.verifiedRegularSession !== true);
  add(errors, 'KILL_SWITCH_ENGAGED', system.killSwitchEngaged !== false);
  add(errors, 'SYSTEM_INCIDENT', system.incidentFree !== true);
  add(errors, 'UNVERIFIED_CLOCK',
    !finite(system.clockSkewMs)||Math.abs(system.clockSkewMs)>POLICY.maxClockSkewMs);
  add(errors, 'FEED_NOT_PERMITTED', feed.dataUsePermitted !== true);
  add(errors, 'UNVERIFIED_INSTRUMENT', feed.instrumentTradable !== true ||
    feed.instrumentKey !== intent.instrumentKey);
  add(errors, 'BOOK_EVENT_FRESHNESS_UNKNOWN',
    !finite(feed.exchangeBookEventAgeMs)||feed.exchangeBookEventAgeMs<0 ||
    feed.exchangeBookEventAgeMs>POLICY.maxExchangeBookAgeMs);
  add(errors, 'BOOK_MARKET_NOT_CERTIFIED', feed.bookQualityCertified !== true);
  add(errors, 'INVALID_SPREAD',
    !finite(feed.spreadBps)||feed.spreadBps<0||feed.spreadBps>POLICY.maxSpreadBps);
  const local=istClock(timestampIso);
  add(errors, 'INVALID_TIMESTAMP', !local);
  if (local) {
    add(errors, 'OUTSIDE_CONSERVATIVE_ENTRY_WINDOW',
      local.minute < POLICY.entryStartIstMinute || local.minute > POLICY.lastEntryIstMinute);
    add(errors, 'WEEKEND', local.weekday === 'Sat' || local.weekday === 'Sun');
  }

  if (finite(intent.limitPrice) && Number.isSafeInteger(intent.quantity) && intent.quantity>0) {
    const notional=intent.limitPrice*intent.quantity;
    add(errors, 'SINGLE_POSITION_CAP', notional>POLICY.maxSinglePositionRupees);
    if (validMoney(account.grossExposureRupees))
      add(errors, 'GROSS_EXPOSURE_CAP', notional+account.grossExposureRupees>POLICY.maxGrossExposureRupees);
    if (validMoney(account.cashAvailableRupees))
      add(errors, 'CASH_RESERVE_BREACH', account.cashAvailableRupees-notional*1.01<POLICY.minUncommittedCashRupees);
    if (finite(intent.stopPrice) && intent.stopPrice>0 && intent.stopPrice<intent.limitPrice) {
      // Synthetic conservative planning approximation, NOT a guaranteed stop fill.
      const illustrativeGapRisk=0.005*notional;
      const assumedRoundtripFriction=0.003*notional;
      const modeledCandidateRisk=(intent.limitPrice-intent.stopPrice)*intent.quantity
        +illustrativeGapRisk+assumedRoundtripFriction;
      add(errors, 'PER_TRADE_RISK_CAP', modeledCandidateRisk>POLICY.maxLossPerCandidateRupees);
    }
  }
  return verdict(errors.length?'REJECT':'PAPER_CANDIDATE_PASSED_INVARIANTS_ONLY',errors,{
    strategyProfitabilityVerified:false,
    exchangeBookProvenanceVerifiedBySoftware:false,
    paperSimulationAllowedIfDataRightsActuallyPermit:false,
    note:'Pure offline assessment; NOT authorization to simulate against restricted data, place live orders, or execute virtual fills.'
  });
}

if (process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  // No secrets, no external input, no network. Show current system capability.
  console.log(JSON.stringify(assessLiveReadinessInventory(),null,2));
}
