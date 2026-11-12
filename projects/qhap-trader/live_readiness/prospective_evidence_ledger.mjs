/**
 * QHAP-TRADER prospective evidence protocol (strictly offline).
 * No network, tokens, raw candles, account routing or exchange-data usage.
 * A frozen deterministic manifest detects *declared* omitted weekdays,
 * cherry-picked reporting, malformed paper P&L and incomplete sessions.
 * It DOES NOT independently authenticate market-data rights, original bars,
 * exchange holidays, timestamps, fills, licenses, or economic profitability.
 */
import {createHash} from 'node:crypto';

const SHA256=/^[a-f0-9]{64}$/;
const GIT_SHA=/^[a-f0-9]{40}$/;
const ID=/^[A-Za-z0-9_-]{3,64}$/;
const KEYS=['studyId','frozenAtMs','firstSessionDate','lastSessionDate',
  'declaredClosedWeekdays','baselineGitBlobSha','costModelGitBlobSha',
  'strategyId','costPolicyId','selectionPolicy','comparisonPolicy','marketScope'];
const REPORT_KEYS=['sessionDate','recordedAtMs','sourceSha256','sourceCoverage',
  'state','signalsSeen','signalsRejected','closedPaperTrades',
  'grossRupees','chargesRupees','netRupees'];
const terminal=new Set(['NO_TRADE','CLOSED_PAPER_TRADES']);
const unresolved=new Set(['DATA_GAP','FEED_OUTAGE','UNRESOLVED_POSITION']);
const isRecord=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const exact=(x,k)=>isRecord(x)&&Object.keys(x).length===k.length&&
  Object.keys(x).every(y=>k.includes(y));
const integer=n=>Number.isSafeInteger(n)&&n>=0;
const paise=n=>typeof n==='number'&&Number.isFinite(n)&&
  Number.isSafeInteger(Math.round(n*100))&&Math.abs(n*100-Math.round(n*100))<=1e-6;
const minor=n=>Math.round(n*100);
const dayDate=s=>{
  if(typeof s!=='string'||!/^(20\d\d)-(\d\d)-(\d\d)$/.test(s))return null;
  const date=new Date(s+'T00:00:00Z');
  return Number.isFinite(date.valueOf())&&date.toISOString().slice(0,10)===s?date:null;
};
const weekday=date=>{const d=date.getUTCDay();return d>0&&d<6;};
const closeMs=s=>dayDate(s).getTime()+10.5*3600000; // 16:00 IST
const digest=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const status=(state,reasons=[],more={})=>Object.freeze({
  status:state,reasons:[...new Set(reasons)].sort(),
  mode:'OFFLINE_RESEARCH_ONLY',canTrade:false,liveTradingAuthorized:false,
  realOrderRoutePresent:false,realOrdersSent:0,
  independentlyVerifiedForwardSessions:0,
  independentDataRightsVerified:false,exchangeCalendarAuthenticated:false,
  brokerReconciled:false,strategyNetEdgeVerified:false,
  ...more
});
function evaluatePlanSpec(x){
  if(!exact(x,KEYS)||!ID.test(x.studyId||'')||
    !integer(x.frozenAtMs)||!dayDate(x.firstSessionDate)||
    !dayDate(x.lastSessionDate)||x.firstSessionDate>x.lastSessionDate||
    x.firstSessionDate<'2026-11-13'||!GIT_SHA.test(x.baselineGitBlobSha||'')||
    !GIT_SHA.test(x.costModelGitBlobSha||'')||
    x.strategyId!=='ORB_10MIN_NEXT_BAR_V1'||
    x.costPolicyId!=='UPSTOX_2026_INDICATIVE_STRESS_V1'||
    x.selectionPolicy!=='ALL_WEEKDAYS_UNLESS_FROZEN_CLOSURE'||
    x.comparisonPolicy!=='NO_TRADE_ZERO'||
    x.marketScope!=='NSE_EQ_CASH_LONG_ONLY'||
    !Array.isArray(x.declaredClosedWeekdays)||x.declaredClosedWeekdays.length>30||
    x.frozenAtMs>=dayDate(x.firstSessionDate).getTime()-5.5*3600000)
    return {errors:['INVALID_OR_UNFROZEN_MANIFEST']};
  const excluded=new Set();
  for(const d of x.declaredClosedWeekdays) {
    if(typeof d!=='string'||!dayDate(d)||!weekday(dayDate(d))||
      d<x.firstSessionDate||d>x.lastSessionDate||excluded.has(d))
      return {errors:['INVALID_FROZEN_CLOSURE_DATES']};
    excluded.add(d);
  }
  const dates=[];
  for(let t=dayDate(x.firstSessionDate).getTime();
      t<=dayDate(x.lastSessionDate).getTime();t+=86400000) {
    const current=new Date(t);
    if(weekday(current)&&!excluded.has(current.toISOString().slice(0,10)))
      dates.push(current.toISOString().slice(0,10));
    if(dates.length>260)return {errors:['SESSION_WINDOW_TOO_LARGE']};
  }
  if(dates.length<60)return {errors:['FEWER_THAN_60_PREDECLARED_WEEKDAYS']};
  return {dates,errors:[]};
}
export function freezeProspectiveResearchPlan(input){
  const validation=evaluatePlanSpec(input);
  if(validation.errors.length)
    return status('BLOCKED_INVALID_PROSPECTIVE_PLAN',validation.errors);
  const manifest={
    studyId:input.studyId,frozenAtMs:input.frozenAtMs,
    firstSessionDate:input.firstSessionDate,lastSessionDate:input.lastSessionDate,
    declaredClosedWeekdays:[...input.declaredClosedWeekdays].sort(),
    baselineGitBlobSha:input.baselineGitBlobSha,
    costModelGitBlobSha:input.costModelGitBlobSha,
    strategyId:input.strategyId,costPolicyId:input.costPolicyId,
    selectionPolicy:input.selectionPolicy,
    comparisonPolicy:input.comparisonPolicy,marketScope:input.marketScope
  };
  return status('FROZEN_MANIFEST_INDEPENDENT_REVIEW_REQUIRED',[
    'SELF_DECLARED_CALENDAR_NOT_EXCHANGE_CERTIFIED',
    'GIT_PUBLICATION_AND_SOURCE_ENTITLEMENT_REQUIRE_EXTERNAL_VALIDATION'
  ],{
    manifest,manifestSha256:digest(manifest),
    expectedSessionDates:[...validation.dates],targetCompleteSessions:60,
    registeredWeekdays:validation.dates.length,
    closedWeekdaysDeclared:manifest.declaredClosedWeekdays.length,
    commitmentTimestampExternallyAttested:false,
    paperObservationAuthorizedBySoftware:false
  });
}
function validReport(r){
  if(!exact(r,REPORT_KEYS)||!dayDate(r.sessionDate)||
    !integer(r.recordedAtMs)||r.recordedAtMs<closeMs(r.sessionDate)||
    !(terminal.has(r.state)||unresolved.has(r.state))) return false;
  if(terminal.has(r.state)) {
    if(!SHA256.test(r.sourceSha256||'')||
      r.sourceCoverage!=='DECLARED_COMPLETE'||
      !integer(r.signalsSeen)||!integer(r.signalsRejected)||
      r.signalsSeen>100000||r.signalsRejected>r.signalsSeen||
      !integer(r.closedPaperTrades)||r.closedPaperTrades>2||
      !paise(r.grossRupees)||!paise(r.chargesRupees)||
      !paise(r.netRupees)||r.chargesRupees<0||r.chargesRupees>1000||
      Math.abs(r.grossRupees)>10000||
      minor(r.netRupees)!==minor(r.grossRupees)-minor(r.chargesRupees))return false;
    if(r.state==='NO_TRADE')return r.closedPaperTrades===0&&
      r.grossRupees===0&&r.chargesRupees===0&&r.netRupees===0&&
      r.signalsRejected===r.signalsSeen;
    return r.closedPaperTrades>=1&&r.chargesRupees>0&&
      r.signalsSeen>=r.closedPaperTrades&&
      r.signalsRejected<=r.signalsSeen-r.closedPaperTrades;
  }
  // Unknown exits, missing data, feed outage: DO NOT manufacture zero P&L.
  return r.sourceSha256===null&&r.sourceCoverage==='UNKNOWN'&&
    ['signalsSeen','signalsRejected','closedPaperTrades','grossRupees',
      'chargesRupees','netRupees'].every(k=>r[k]===null);
}
/**
 * Audit a redacted self-declared ledger at an injected evaluation timestamp.
 * No outward attestation is possible: independent count is ALWAYS zero.
 * Reported P&L is withheld if any missing/corrupted/incomplete session exists.
 */
export function auditProspectiveResearchLedger(plan,reports,opts={}) {
  if(!isRecord(plan)||plan.status!=='FROZEN_MANIFEST_INDEPENDENT_REVIEW_REQUIRED'||
    !isRecord(plan.manifest)||!SHA256.test(plan.manifestSha256||'')||
    digest(plan.manifest)!==plan.manifestSha256||
    !Array.isArray(plan.expectedSessionDates)||
    !Array.isArray(reports)||reports.length>300||
    !exact(opts,['evaluatedAtMs'])||!integer(opts.evaluatedAtMs))
    return status('BLOCKED_INVALID_AUDIT_INPUT',['UNTRUSTED_PLAN_LEDGER_OR_CLOCK']);
  const spec=evaluatePlanSpec(plan.manifest);
  if(spec.errors.length||JSON.stringify(spec.dates)!==
    JSON.stringify(plan.expectedSessionDates))
    return status('BLOCKED_INVALID_AUDIT_INPUT',['MUTATED_OR_INVALID_FROZEN_MANIFEST']);
  const elapsed=spec.dates.filter(d=>closeMs(d)<=opts.evaluatedAtMs);
  const allowed=new Set(elapsed),seen=new Set();
  let prev='',complete=0,withTrades=0,abstentions=0,declaredGross=0,declaredCosts=0;
  let unresolvedCount=0,reportCount=0;
  const problems=[];
  for(const r of reports) {
    if(!isRecord(r)||!dayDate(r.sessionDate)) {
      problems.push('INVALID_SESSION_DATE');continue;
    }
    if(!allowed.has(r.sessionDate))problems.push('UNSCHEDULED_OR_UNELAPSED_SESSION');
    if(seen.has(r.sessionDate))problems.push('DUPLICATE_SESSION_REPORT');
    if(prev&&r.sessionDate<=prev)problems.push('SESSION_REPORTS_OUT_OF_ORDER');
    seen.add(r.sessionDate);prev=r.sessionDate;
    if(!validReport(r)){
      problems.push('MALFORMED_OR_PREMATURE_SESSION_REPORT');continue;
    }
    if(r.recordedAtMs>opts.evaluatedAtMs)problems.push('REPORT_FROM_FUTURE');
    if(!allowed.has(r.sessionDate))continue;
    reportCount++;
    if(unresolved.has(r.state)){
      unresolvedCount++;
      problems.push('INCOMPLETE_DATA_OR_UNRESOLVED_PAPER_POSITION');
      continue;
    }
    complete++;
    if(r.state==='NO_TRADE')abstentions++;
    else withTrades++;
    declaredGross+=minor(r.grossRupees);
    declaredCosts+=minor(r.chargesRupees);
  }
  const missing=elapsed.filter(d=>!seen.has(d));
  if(missing.length)problems.push('MISSING_DECLARED_ELIGIBLE_SESSION');
  if(!Number.isSafeInteger(declaredGross)||!Number.isSafeInteger(declaredCosts))
    problems.push('UNSAFE_AGGREGATE_MONEY');
  const qualifiedShape=problems.length===0&&complete>=60;
  const phase=problems.length?'HALT_INCOMPLETE_OR_BIASED_SESSION_LEDGER':
    qualifiedShape?'DECLARED_60_SESSIONS_NEEDS_INDEPENDENT_AUDIT':
    'INSUFFICIENT_DECLARED_FORWARD_COVERAGE';
  const moneyKnown=problems.length===0;
  return status(phase,[
    ...problems,
    'SELF_DECLARED_REPORTS_NEVER_PROVE_AUTHENTIC_MARKET_DATA_OR_EDGE'
  ],{
    frozenManifestSha256:plan.manifestSha256,
    declaredExpectedElapsedSessions:elapsed.length,
    reportedElapsedSessions:reportCount,
    completeDeclaredSessions:complete,
    declaredNoTradeSessions:abstentions,declaredTradeSessions:withTrades,
    unresolvedDeclaredSessions:unresolvedCount,
    missingSessionCount:missing.length,
    targetCompleteSessions:60,
    declaredGrossRupees:moneyKnown?declaredGross/100:null,
    declaredChargesRupees:moneyKnown?declaredCosts/100:null,
    declaredNetRupees:moneyKnown?(declaredGross-declaredCosts)/100:null,
    noTradeComparatorRupees:0,
    economicResultEligibleForClaims:false,
    externallyValidForwardEvidence:false,
    recommendedLiveAction:'NO_TRADE'
  });
}
