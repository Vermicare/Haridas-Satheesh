import test from 'node:test';
import assert from 'node:assert/strict';
import {freezeProspectiveResearchPlan as freeze,
  auditProspectiveResearchLedger as audit} from './prospective_evidence_ledger.mjs';

const weekdays=(first,n)=>{
  const d=new Date(first+'T00:00:00Z'),list=[];
  while(list.length<n){
    if(d.getUTCDay()>0&&d.getUTCDay()<6)list.push(d.toISOString().slice(0,10));
    d.setUTCDate(d.getUTCDate()+1);
  }
  return list;
};
const dates=weekdays('2026-11-16',60);
const observedAt=new Date(dates.at(-1)+'T11:00:00Z').getTime();
const close=d=>new Date(d+'T10:30:00Z').getTime();
const params=()=>({
  studyId:'QHAP_ORB_2026_FORWARD_V1',
  frozenAtMs:Date.parse('2026-11-12T10:00:00Z'),
  firstSessionDate:dates[0],lastSessionDate:dates.at(-1),
  declaredClosedWeekdays:[],
  baselineGitBlobSha:'13c3e9d8857f22610435e9c9b1f2d4ee03888d0f',
  costModelGitBlobSha:'80f20e3df0d043da2a116370781dbf68e46a8684',
  strategyId:'ORB_10MIN_NEXT_BAR_V1',
  costPolicyId:'UPSTOX_2026_INDICATIVE_STRESS_V1',
  selectionPolicy:'ALL_WEEKDAYS_UNLESS_FROZEN_CLOSURE',
  comparisonPolicy:'NO_TRADE_ZERO',
  marketScope:'NSE_EQ_CASH_LONG_ONLY'
});
const mk=()=>freeze(params());
const noTrade=d=>({
  sessionDate:d,recordedAtMs:close(d),
  sourceSha256:'a'.repeat(64),sourceCoverage:'DECLARED_COMPLETE',
  state:'NO_TRADE',signalsSeen:2,signalsRejected:2,
  closedPaperTrades:0,grossRupees:0,chargesRupees:0,netRupees:0
});
const trade=d=>({...noTrade(d),state:'CLOSED_PAPER_TRADES',
  signalsSeen:3,signalsRejected:2,closedPaperTrades:1,
  grossRupees:8.50,chargesRupees:5.96,netRupees:2.54});
const unknown=(d,state='DATA_GAP')=>({
  sessionDate:d,recordedAtMs:close(d),sourceSha256:null,
  sourceCoverage:'UNKNOWN',state,signalsSeen:null,
  signalsRejected:null,closedPaperTrades:null,
  grossRupees:null,chargesRupees:null,netRupees:null
});
const all=()=>dates.map(noTrade);
const check=(r,plan=mk(),now=observedAt)=>audit(plan,r,{evaluatedAtMs:now});
const expectProblem=(reports,reason,plan=mk(),now=observedAt)=>{
  const x=check(reports,plan,now);
  assert.equal(x.status,'HALT_INCOMPLETE_OR_BIASED_SESSION_LEDGER',JSON.stringify(x));
  assert.ok(x.reasons.includes(reason),JSON.stringify(x));
  assert.equal(x.canTrade,false);
};
test('60 consecutive declared weekday slots are frozen; weekend excluded',()=>{
  const p=mk();
  assert.equal(p.status,'FROZEN_MANIFEST_INDEPENDENT_REVIEW_REQUIRED');
  assert.equal(p.expectedSessionDates.length,60);
  assert.ok(p.expectedSessionDates.every(d=>new Date(d+'T00:00:00Z').getUTCDay()%6!==0));
  assert.equal(p.targetCompleteSessions,60);
  assert.equal(p.commitmentTimestampExternallyAttested,false);
});
test('same manifest creates deterministic fingerprint',()=>{
  assert.equal(mk().manifestSha256,mk().manifestSha256);
});
test('even perfect mock manifest never authenticates calendar or trading',()=>{
  const p=mk();assert.equal(p.exchangeCalendarAuthenticated,false);
  assert.equal(p.canTrade,false);assert.equal(p.realOrderRoutePresent,false);
});
test('any required omitted plan key fails closed',()=>{
  const p=params();delete p.baselineGitBlobSha;
  assert.equal(freeze(p).status,'BLOCKED_INVALID_PROSPECTIVE_PLAN');
});
test('unexpected credentials or client account fields fail plan creation',()=>{
  const p=params();p.accessToken='SECRET';
  assert.equal(freeze(p).status,'BLOCKED_INVALID_PROSPECTIVE_PLAN');
});
test('unfrozen/tardy commitment date is invalid',()=>{
  const p=params();p.frozenAtMs=Date.parse(dates[0]+'T10:00:00Z');
  assert.equal(freeze(p).status,'BLOCKED_INVALID_PROSPECTIVE_PLAN');
});
test('previously explored February 2021 cannot be a prospective window',()=>{
  const p=params();p.firstSessionDate='2021-02-01';
  assert.equal(freeze(p).status,'BLOCKED_INVALID_PROSPECTIVE_PLAN');
});
test('fewer than 60 declared weekdays is blocked',()=>{
  const p=params();p.lastSessionDate=weekdays(dates[0],59).at(-1);
  assert.equal(freeze(p).status,'BLOCKED_INVALID_PROSPECTIVE_PLAN');
});
test('weekend cannot be declared a market closure',()=>{
  const p=params();p.declaredClosedWeekdays=['2026-11-21'];
  assert.equal(freeze(p).status,'BLOCKED_INVALID_PROSPECTIVE_PLAN');
});
test('duplicate declared closure is rejected',()=>{
  const p=params();p.declaredClosedWeekdays=['2026-11-17','2026-11-17'];
  assert.equal(freeze(p).status,'BLOCKED_INVALID_PROSPECTIVE_PLAN');
});
test('closure outside the manifest window is rejected',()=>{
  const p=params();p.declaredClosedWeekdays=['2026-11-13'];
  assert.equal(freeze(p).status,'BLOCKED_INVALID_PROSPECTIVE_PLAN');
});
test('each declared closure consumes a pre-registered slot, not silently ignored',()=>{
  const p=params();p.declaredClosedWeekdays=['2026-11-17'];
  assert.equal(freeze(p).status,'BLOCKED_INVALID_PROSPECTIVE_PLAN');
});
test('future closure is allowed only when additional session range is predeclared',()=>{
  const p=params();p.declaredClosedWeekdays=['2026-11-17'];
  p.lastSessionDate=weekdays(dates.at(-1),2).at(-1);
  const q=freeze(p);assert.equal(q.expectedSessionDates.length,60);
  assert.ok(!q.expectedSessionDates.includes('2026-11-17'));
});
test('test complete all-no-trade ledger stays only self-declared',()=>{
  const a=check(all());
  assert.equal(a.status,'DECLARED_60_SESSIONS_NEEDS_INDEPENDENT_AUDIT');
  assert.equal(a.completeDeclaredSessions,60);
  assert.equal(a.independentlyVerifiedForwardSessions,0);
  assert.equal(a.declaredNoTradeSessions,60);
  assert.equal(a.declaredNetRupees,0);
  assert.equal(a.noTradeComparatorRupees,0);
  assert.equal(a.economicResultEligibleForClaims,false);
  assert.equal(a.canTrade,false);
});
test('reported gains net of hypothetical charges remain unverified',()=>{
  const reports=all();reports[0]=trade(dates[0]);
  const a=check(reports);
  assert.equal(a.declaredTradeSessions,1);
  assert.equal(a.declaredGrossRupees,8.5);
  assert.equal(a.declaredChargesRupees,5.96);
  assert.equal(a.declaredNetRupees,2.54);
  assert.equal(a.strategyNetEdgeVerified,false);
});
test('declared losing paper trade is not hidden or made positive',()=>{
  const reports=all();reports[0]={...trade(dates[0]),grossRupees:-20,
    chargesRupees:5.96,netRupees:-25.96};
  const a=check(reports);
  assert.equal(a.declaredNetRupees,-25.96);
  assert.equal(a.recommendedLiveAction,'NO_TRADE');
});
test('missing single expected session makes aggregate net unavailable',()=>{
  const r=all();r.splice(23,1);
  expectProblem(r,'MISSING_DECLARED_ELIGIBLE_SESSION');
  assert.equal(check(r).declaredNetRupees,null);
  assert.equal(check(r).missingSessionCount,1);
});
test('missing a no-trade session is still missing evidence',()=>{
  const r=all().slice(1);
  expectProblem(r,'MISSING_DECLARED_ELIGIBLE_SESSION');
});
test('duplicated report cannot inflate performance',()=>{
  const r=all();r.splice(2,0,noTrade(dates[1]));
  expectProblem(r,'DUPLICATE_SESSION_REPORT');
});
test('out-of-order reports are rejected, not silently sorted',()=>{
  const r=all();[r[4],r[5]]=[r[5],r[4]];
  expectProblem(r,'SESSION_REPORTS_OUT_OF_ORDER');
});
test('an unscheduled extra calendar date cannot be inserted',()=>{
  const r=all();r.push(noTrade('2027-06-01'));
  expectProblem(r,'UNSCHEDULED_OR_UNELAPSED_SESSION');
});
test('report before market close does not count as completed session',()=>{
  const r=all();r[0].recordedAtMs=Date.parse(dates[0]+'T08:00:00Z');
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('future report clock is rejected',()=>{
  const r=all();r[0].recordedAtMs=observedAt+86400000;
  expectProblem(r,'REPORT_FROM_FUTURE');
});
test('raw credentials or exchange payloads never cross reporting boundary',()=>{
  const r=all();r[0].brokerResponse={order_id:'secret'};
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('unknown source fingerprint or missing coverage is not a completed day',()=>{
  for(const k of ['sourceSha256','sourceCoverage']){
    const r=all();r[0][k]=null;
    expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
  }
});
test('missing market data remains explicitly unresolved, never ₹0 P&L',()=>{
  const r=all();r[0]=unknown(dates[0]);
  expectProblem(r,'INCOMPLETE_DATA_OR_UNRESOLVED_PAPER_POSITION');
  assert.equal(check(r).declaredNetRupees,null);
});
test('feed outage is not treated as legitimate no-trade',()=>{
  const r=all();r[0]=unknown(dates[0],'FEED_OUTAGE');
  expectProblem(r,'INCOMPLETE_DATA_OR_UNRESOLVED_PAPER_POSITION');
});
test('unresolved end-of-day position quarantines all performance claims',()=>{
  const r=all();r[0]=unknown(dates[0],'UNRESOLVED_POSITION');
  expectProblem(r,'INCOMPLETE_DATA_OR_UNRESOLVED_PAPER_POSITION');
});
test('failed session carrying fake zero P&L is rejected as malformed',()=>{
  const r=all();r[0]={...unknown(dates[0]),netRupees:0};
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('no trade with hidden simulated realized loss is inconsistent',()=>{
  const r=all();r[0].netRupees=-1;
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('no trade cannot hide an unaccounted decision signal',()=>{
  const r=all();r[0].signalsRejected=1;
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('closed trade requires positive estimated charges',()=>{
  const r=all();r[0]={...trade(dates[0]),chargesRupees:0,netRupees:8.5};
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('claimed paper win net arithmetic must match gross minus fees',()=>{
  const r=all();r[0]={...trade(dates[0]),netRupees:99};
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('portfolio cap limits reported trade count to at most two',()=>{
  const r=all();r[0]={...trade(dates[0]),closedPaperTrades:3,
    signalsSeen:3,signalsRejected:0};
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('negative transaction charges are impossible',()=>{
  const r=all();r[0]={...trade(dates[0]),chargesRupees:-1,netRupees:9.5};
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('fractional-paise net is rejected',()=>{
  const r=all();r[0]={...trade(dates[0]),netRupees:2.541};
  expectProblem(r,'MALFORMED_OR_PREMATURE_SESSION_REPORT');
});
test('auditing partway through period expects only elapsed sessions',()=>{
  const k=9,now=close(dates[k-1]);
  const a=check(dates.slice(0,k).map(noTrade),mk(),now);
  assert.equal(a.status,'INSUFFICIENT_DECLARED_FORWARD_COVERAGE');
  assert.equal(a.declaredExpectedElapsedSessions,k);
  assert.equal(a.completeDeclaredSessions,k);
  assert.equal(a.canTrade,false);
});
test('early evaluation with absent elapsed date detects missing',()=>{
  const now=close(dates[8]);
  expectProblem(dates.slice(0,8).map(noTrade),
    'MISSING_DECLARED_ELIGIBLE_SESSION',mk(),now);
});
test('evaluation before first session cannot forge forward evidence',()=>{
  const a=check([],mk(),Date.parse('2026-11-12T11:00:00Z'));
  assert.equal(a.status,'INSUFFICIENT_DECLARED_FORWARD_COVERAGE');
  assert.equal(a.completeDeclaredSessions,0);
  assert.equal(a.independentlyVerifiedForwardSessions,0);
});
test('tampering with a frozen manifest is detected by SHA-256',()=>{
  const plan=mk();plan.manifest.costPolicyId='OTHER';
  const a=check(all(),plan);
  assert.equal(a.status,'BLOCKED_INVALID_AUDIT_INPUT');
});
test('removing a frozen expected session is detected',()=>{
  const plan=mk();plan.expectedSessionDates.pop();
  const a=check(all(),plan);
  assert.equal(a.status,'BLOCKED_INVALID_AUDIT_INPUT');
});
test('arbitrary stamped outside approval cannot self-authorize anything',()=>{
  const plan={...mk(),canTrade:true,liveTradingAuthorized:true};
  const a=check(all(),plan);
  assert.equal(a.canTrade,false);
  assert.equal(a.liveTradingAuthorized,false);
  assert.equal(a.independentDataRightsVerified,false);
});
test('missing or fraudulent evaluation clock does not default to now',()=>{
  const r=all();assert.equal(audit(mk(),r,{}).status,'BLOCKED_INVALID_AUDIT_INPUT');
  assert.equal(audit(mk(),r,{evaluatedAtMs:NaN}).status,'BLOCKED_INVALID_AUDIT_INPUT');
});
test('empty or enormous report batch cannot imply coverage',()=>{
  assert.equal(check([]).missingSessionCount,60);
  const a=check(Array.from({length:301},()=>noTrade(dates[0])));
  assert.equal(a.status,'BLOCKED_INVALID_AUDIT_INPUT');
});
