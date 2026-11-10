/**
 * QHAP-TRADER — deterministic OFFLINE NSE 2026 cash-equity probe calendar.
 * Source: https://www.nseindia.com/resources/exchange-communication-holidays
 * Listed 2026 equity holidays verified from first-party exchange page 2026-11-10.
 * Only decides whether a user MAY ATTEMPT a single authorized READ-ONLY probe.
 * It cannot establish an actively open exchange, authentic data, or order rights.
 * No HTTP, no API secrets, no market values, no broker functionality.
 */
import path from 'node:path';
import {pathToFileURL} from 'node:url';

export const POLICY = Object.freeze({
  version: 'QHAP_NSE_2026_EQUITY_PROBE_V1',
  sourceUrl: 'https://www.nseindia.com/resources/exchange-communication-holidays',
  sourceDescription: 'Published NSE 2026 equity holiday schedule and regular session hours; exceptions remain unverified',
  timezone: 'Asia/Kolkata',
  market: 'NSE_EQ',
  supportedYear: 2026,
  regularMarketStart: '09:15',
  regularMarketEnd: '15:30',
  conservativeReadOnlyProbeStart: '09:30',
  conservativeReadOnlyProbeEndExclusive: '15:00',
  sourceMayHaveUnpublishedOrNewExceptionalChanges: true,
});

const HOLIDAYS = new Set([
  '2026-01-15', '2026-01-26', '2026-03-03', '2026-03-26',
  '2026-03-31', '2026-04-03', '2026-04-14', '2026-05-01',
  '2026-05-28', '2026-06-26', '2026-09-14', '2026-10-02',
  '2026-10-20', '2026-11-10', '2026-11-24', '2026-12-25',
]);

const formatter = new Intl.DateTimeFormat('en-GB', {
  timeZone: POLICY.timezone, year: 'numeric', month: '2-digit', day: '2-digit',
  weekday: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit',
  hourCycle: 'h23',
});

/** Pure calendar check with injected instant; cannot be treated as exchange certification. */
export function classifyReadOnlyProbe(epochMs) {
  if (!Number.isSafeInteger(epochMs) || epochMs < 0 || epochMs > 4102444800000)
    throw Error('INVALID_INSTANT_MS');
  const parts = Object.fromEntries(formatter.formatToParts(new Date(epochMs))
    .filter(p => p.type !== 'literal').map(p => [p.type, p.value]));
  const date = parts.year + '-' + parts.month + '-' + parts.day;
  const localTime = parts.hour + ':' + parts.minute + ':' + parts.second;
  const minuteOfDay = Number(parts.hour) * 60 + Number(parts.minute);
  const result = {
    policy: POLICY.version,
    date, localTime, timezone: POLICY.timezone,
    verdict: 'ABSTAIN', reason: 'UNKNOWN',
    safeToTryAuthorizedReadOnlyProbe: false,
    exchangeOpenCertified: false,
    dataFreshnessCertified: false,
    licensedDataRightsCertified: false,
    liveOrderAuthorization: false,
    holidaySource: POLICY.sourceUrl,
  };
  if (Number(parts.year) !== POLICY.supportedYear) result.reason = 'UNSUPPORTED_CALENDAR_YEAR';
  else if (HOLIDAYS.has(date)) result.reason = 'EXCHANGE_PUBLISHED_HOLIDAY';
  else if (parts.weekday === 'Sat' || parts.weekday === 'Sun')
    result.reason = 'WEEKEND_EXCEPTION_NOT_CERTIFIED';
  else if (minuteOfDay < 570 || minuteOfDay >= 900)
    result.reason = 'OUTSIDE_CONSERVATIVE_PROBE_WINDOW';
  else {
    result.verdict = 'ONE_READ_ONLY_PROBE_MAY_BE_ATTEMPTED';
    result.reason = 'SCHEDULED_REGULAR_SESSION_ONLY_NOT_CERTIFIED';
    result.safeToTryAuthorizedReadOnlyProbe = true;
  }
  return result;
}

/** A status-only message from user's own Upstox connectivity test; never accept secrets/prices. */
export function classifyStatusOnlyConnection(status) {
  if (!status || typeof status !== 'object' || Array.isArray(status))
    throw Error('BAD_STATUS_OBJECT');
  const allowed = new Set([
    'status', 'httpCode', 'networkCalls', 'tradesSent',
    'marketDataFreshnessVerified', 'marketDataStored', 'ordersPossible',
  ]);
  if (Object.keys(status).some(k => !allowed.has(k))) throw Error('UNKNOWN_OR_PRIVATE_STATUS_FIELD');
  if (status.status !== 'READ_ONLY_HTTP_200_CONNECTED_NOT_DATA_VALIDATED' ||
      status.httpCode !== 200 || status.networkCalls !== 1 ||
      status.tradesSent !== 0 || status.marketDataFreshnessVerified !== false ||
      status.marketDataStored !== false || status.ordersPossible !== false)
    return {classification: 'UNVERIFIED_OR_UNEXPECTED_STATUS', connectionConfirmed: false,
      quoteVerified: false, sessionCertified: false, ordersAuthorized: false};
  return {classification: 'READ_ONLY_CONNECTIVITY_USER_REPORTED', connectionConfirmed: true,
    quoteVerified: false, sessionCertified: false, ordersAuthorized: false};
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    if (process.argv.length > 3) throw Error('Usage: node nse_2026_probe_gate.mjs [--now]');
    if (process.argv[2] && process.argv[2] !== '--now') throw Error('ONLY_NOW_OPTION_SUPPORTED');
    console.log(JSON.stringify(classifyReadOnlyProbe(Date.now()), null, 2));
  } catch (e) { console.error('GATE_ERROR:', e.message); process.exitCode = 1; }
}
