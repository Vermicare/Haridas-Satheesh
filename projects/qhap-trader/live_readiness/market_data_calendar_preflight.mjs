/**
 * QHAP-TRADER: offline, fail-closed MARKET DATA RIGHTS and 2026 NSE calendar
 * preflight. This is a source-level research boundary, NOT an NSE oracle.
 *
 * Primary public references inspected 2026-11-12:
 * https://www.nseindia.com/resources/exchange-communication-holidays?apiversion=v2
 * https://www.nseindia.com/static/market-data/nse-data-policy
 *
 * No network calls, accounts, API authentication, licensed bars, real orders,
 * paid subscriptions, or claim that a user possesses legal data entitlements.
 * The 2026 holiday transcription must be reviewed against the current official
 * schedule, subsequent notices, instrument halts and special sessions.
 */
import {freezeProspectiveResearchPlan} from './prospective_evidence_ledger.mjs';

const HOLIDAY_2026=Object.freeze([
  '2026-01-15','2026-01-26','2026-03-03','2026-03-26',
  '2026-03-31','2026-04-03','2026-04-14','2026-05-01',
  '2026-05-28','2026-06-26','2026-09-14','2026-10-02',
  '2026-10-20','2026-11-10','2026-11-24','2026-12-25'
]);
const holidays=new Set(HOLIDAY_2026);
const hash=/^[a-f0-9]{64}$/;
const code=/^[A-Za-z0-9_-]{3,80}$/;
const isObj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const hasExact=(o,keys)=>isObj(o)&&Object.keys(o).length===keys.length&&
  Object.keys(o).every(k=>keys.includes(k));
const validDate=s=>{
  if(typeof s!=='string'||!/^20\d{2}-\d{2}-\d{2}$/.test(s))return false;
  const d=new Date(s+'T00:00:00Z');
  return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===s;
};
const wk=s=>new Date(s+'T00:00:00Z').getUTCDay();
const validMs=n=>Number.isSafeInteger(n)&&n>=0;
const RAW_KEYS=['providerReference','dataProvidedBy','instrumentSegment',
  'productGranularity','usagePurpose','agreementSha256','schemaSha256',
  'effectiveFrom','effectiveUntil','nonDisplayResearchPermission',
  'virtualSimulationPermission','localRetentionPermission',
  'publicRedistributionPermission','independentReviewRecorded','reviewedAtMs'];
const claim=new Set(['UNKNOWN','CLAIMED_PERMITTED','DENIED']);
const redistrib=new Set(['UNKNOWN','CLAIMED_PERMITTED','DENIED']);
function verdict(status,reasons=[],more={}) {
  return Object.freeze({
    status,reasons:[...new Set(reasons)].sort(),
    paperOnly:true,realOrdersSent:0,realOrderRoutePresent:false,
    canTrade:false,liveTradingAuthorized:false,
    marketDataUseAuthorizedBySoftware:false,
    independentlyAuthenticatedMarketFeed:false,
    independentlyVerifiedExchangeSessions:0,
    genuineForwardSessionsVerified:0,
    brokerReconciled:false, ...more
  });
}

/** A published holiday table is not proof a particular security was open. */
export function inspectPinned2026EquityDate(date){
  if(!validDate(date))return verdict('BLOCKED_INVALID_DATE',['INVALID_CALENDAR_DATE']);
  if(!date.startsWith('2026-'))
    return verdict('BLOCKED_OUTSIDE_PINNED_2026_YEAR',['NO_OFFICIAL_YEAR_REFERENCE_PINNED']);
  if(wk(date)===0||wk(date)===6)
    return verdict('WEEKEND_NOT_REGULAR_SESSION',['WEEKEND_NOT_REGULAR_SESSION']);
  if(holidays.has(date))
    return verdict('PUBLISHED_2026_EQUITY_HOLIDAY',['PUBLISHED_NSE_HOLIDAY']);
  return verdict('PUBLISHED_2026_WEEKDAY_NOT_LISTED_AS_HOLIDAY',[
    'PUBLIC_TABLE_ONLY_SPECIAL_SESSIONS_AND_HALTS_UNVERIFIED',
    'EXCHANGE_SESSION_NOT_INDEPENDENTLY_ATTESTED'
  ]);
}

/**
 * Recompute existing *self-declared* frozen manifest and flag any holiday
 * mislabeled as a normal prospective session. 2027+ remains unpinned.
 */
export function auditPinned2026CalendarAgainstPlan(plan) {
  if(!isObj(plan)||!isObj(plan.manifest)||
    typeof plan.manifestSha256!=='string'||
    !Array.isArray(plan.expectedSessionDates))
    return verdict('BLOCKED_INVALID_PLAN',['INVALID_OR_MISSING_FROZEN_PLAN']);
  const rebuilt=freezeProspectiveResearchPlan(plan.manifest);
  if(rebuilt.status!=='FROZEN_MANIFEST_INDEPENDENT_REVIEW_REQUIRED'||
    rebuilt.manifestSha256!==plan.manifestSha256||
    JSON.stringify(rebuilt.expectedSessionDates)!==
      JSON.stringify(plan.expectedSessionDates))
    return verdict('BLOCKED_INVALID_PLAN',['MUTATED_OR_INVALID_FROZEN_PLAN']);
  const {firstSessionDate,lastSessionDate,declaredClosedWeekdays}=plan.manifest;
  const closed=new Set(declaredClosedWeekdays);
  const problems=[];
  let known2026ProvisionalWeekdays=0;
  let known2026ExcludedHolidays=0;
  let unpinnedFutureWeekdays=0;
  let omittedHolidayCount=0;
  let unexplainedExtraClosureCount=0;
  for(let t=Date.parse(firstSessionDate+'T00:00:00Z');
      t<=Date.parse(lastSessionDate+'T00:00:00Z');t+=86400000){
    const date=new Date(t).toISOString().slice(0,10);
    if(wk(date)===0||wk(date)===6)continue;
    if(!date.startsWith('2026-')){
      unpinnedFutureWeekdays++;
      continue;
    }
    if(holidays.has(date)){
      if(closed.has(date))known2026ExcludedHolidays++;
      else{
        omittedHolidayCount++;
        problems.push('PUBLISHED_NSE_HOLIDAY_INCLUDED_IN_SESSION_PLAN');
      }
    }else if(closed.has(date)){
      unexplainedExtraClosureCount++;
      problems.push('UNVERIFIED_EXTRA_WEEKDAY_CLOSURE');
    }else known2026ProvisionalWeekdays++;
  }
  if(unpinnedFutureWeekdays)
    problems.push('CALENDAR_YEAR_OUTSIDE_PINNED_2026_COVERAGE');
  return verdict(problems.length?'BLOCKED_CALENDAR_MISMATCH_OR_SCOPE':
    'DECLARED_2026_HOLIDAY_MATCH_EXTERNAL_REVIEW_STILL_REQUIRED',
    problems.length?problems:[
      'PUBLISHED_HOLIDAY_REFERENCE_NOT_SESSION_AUTHENTICATION'
    ],{
      pinnedYear:2026,sourceCoverageEnd:'2026-12-31',
      known2026ProvisionalWeekdays,known2026ExcludedHolidays,
      unpinnedFutureWeekdays,omittedHolidayCount,
      unexplainedExtraClosureCount,officialExchangeCalendarCertified:false,
      publicHolidaySource:'NSE_2026_EQUITIES_HOLIDAYS',
      dataUseApproved:false
    });
}

/**
 * Strict meta-only rights screening. Hashes and a checkbox do not prove a
 * legal entitlement. No raw licenses, broker payloads or secrets accepted.
 */
export function auditDeclaredMarketDataRights(receipt,options={}){
  if(!hasExact(receipt,RAW_KEYS))
    return verdict('BLOCKED_INVALID_RIGHTS_RECEIPT',['INVALID_OR_EXTRA_RECEIPT_FIELDS']);
  if(!code.test(receipt.providerReference||'')||
    !['NSE_DIRECT','AUTHORIZED_DATA_VENDOR','BROKER'].includes(receipt.dataProvidedBy)||
    receipt.instrumentSegment!=='NSE_EQ_CASH'||
    receipt.productGranularity!=='I1_MINUTE'||
    receipt.usagePurpose!=='NON_DISPLAY_RESEARCH_AND_PAPER_SIMULATION'||
    !hash.test(receipt.agreementSha256||'')||
    !hash.test(receipt.schemaSha256||'')||
    !validDate(receipt.effectiveFrom)||!validDate(receipt.effectiveUntil)||
    receipt.effectiveFrom>receipt.effectiveUntil||
    !claim.has(receipt.nonDisplayResearchPermission)||
    !claim.has(receipt.virtualSimulationPermission)||
    !claim.has(receipt.localRetentionPermission)||
    !redistrib.has(receipt.publicRedistributionPermission)||
    typeof receipt.independentReviewRecorded!=='boolean'||
    !(receipt.reviewedAtMs===null||validMs(receipt.reviewedAtMs))||
    (receipt.independentReviewRecorded&&receipt.reviewedAtMs===null)||
    (!receipt.independentReviewRecorded&&receipt.reviewedAtMs!==null))
    return verdict('BLOCKED_INVALID_RIGHTS_RECEIPT',['MALFORMED_OR_UNTRUSTED_METADATA']);
  if(!hasExact(options,['sessionDate'])||!validDate(options.sessionDate))
    return verdict('BLOCKED_INVALID_RIGHTS_RECEIPT',['SESSION_DATE_REQUIRED_FOR_RIGHTS_SCOPE']);
  const reasons=[];
  if(options.sessionDate<receipt.effectiveFrom||
    options.sessionDate>receipt.effectiveUntil)
    reasons.push('SESSION_OUTSIDE_DECLARED_CONTRACT_DATES');
  for(const key of ['nonDisplayResearchPermission','virtualSimulationPermission',
    'localRetentionPermission']){
    if(receipt[key]!=='CLAIMED_PERMITTED')
      reasons.push('MISSING_OR_DENIED_'+key.toUpperCase());
  }
  if(receipt.publicRedistributionPermission==='UNKNOWN')
    reasons.push('UNKNOWN_REDISTRIBUTION_RESTRICTIONS');
  if(!receipt.independentReviewRecorded)
    reasons.push('INDEPENDENT_REVIEW_NOT_RECORDED');
  // Even an independently reviewed hash/receipt does not authenticate source
  // contract, permitted simulation usage, or account/user-specific coverage.
  reasons.push('EXTERNAL_CONTRACT_AND_PROVIDER_ATTESTATION_REQUIRED');
  return verdict(reasons.length>1?'BLOCKED_RIGHTS_SCOPE_OR_UNVERIFIED':
    'DECLARED_RIGHTS_CLAIM_EXTERNAL_ATTESTATION_REQUIRED',reasons,{
      permissionClaimsAreNotLegalCertification:true,
      noRawMarketDataExamined:true,sourceTermsIndependentlyVerified:false,
      paidSubscriptionPurchased:false
    });
}

/** Composite gate never converts a declaration into authorization. */
export function auditProspectiveInputBoundary(plan,receipt,options={}){
  const calendar=auditPinned2026CalendarAgainstPlan(plan);
  const rights=auditDeclaredMarketDataRights(receipt,options);
  return verdict('NO_DATA_INGESTION_OR_LIVE_EXECUTION_AUTHORIZED',[
    ...calendar.reasons,...rights.reasons,
    'INDEPENDENT_RIGHTS_AND_EXCHANGE_SESSION_AUDIT_REQUIRED'
  ],{
    calendarStatus:calendar.status,rightsStatus:rights.status,
    independentHumanSignoffRequired:true,
    recommendedAction:'NO_TRADE_AND_NO_UNLICENSED_DATA_INGESTION'
  });
}
