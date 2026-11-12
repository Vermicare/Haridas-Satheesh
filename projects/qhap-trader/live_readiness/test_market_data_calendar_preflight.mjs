import test from 'node:test';
import assert from 'node:assert/strict';
import {freezeProspectiveResearchPlan as freeze} from './prospective_evidence_ledger.mjs';
import {inspectPinned2026EquityDate as date,
  auditPinned2026CalendarAgainstPlan as calendar,
  auditDeclaredMarketDataRights as rights,
  auditProspectiveInputBoundary as combined} from './market_data_calendar_preflight.mjs';
const params=()=>({
  studyId:'QHAP_FORWARD_20261116',
  frozenAtMs:Date.parse('2026-11-12T10:00:00Z'),
  firstSessionDate:'2026-11-16',lastSessionDate:'2027-04-15',
  declaredClosedWeekdays:['2026-11-24','2026-12-25'],
  baselineGitBlobSha:'13c3e9d8857f22610435e9c9b1f2d4ee03888d0f',
  costModelGitBlobSha:'80f20e3df0d043da2a116370781dbf68e46a8684',
  strategyId:'ORB_10MIN_NEXT_BAR_V1',
  costPolicyId:'UPSTOX_2026_INDICATIVE_STRESS_V1',
  selectionPolicy:'ALL_WEEKDAYS_UNLESS_FROZEN_CLOSURE',
  comparisonPolicy:'NO_TRADE_ZERO',
  marketScope:'NSE_EQ_CASH_LONG_ONLY'
});
const plan=()=>freeze(params());
const receipt=()=>({
  providerReference:'UPSTOX_PUBLIC_DOCS_ONLY',
  dataProvidedBy:'BROKER',
  instrumentSegment:'NSE_EQ_CASH',
  productGranularity:'I1_MINUTE',
  usagePurpose:'NON_DISPLAY_RESEARCH_AND_PAPER_SIMULATION',
  agreementSha256:'a'.repeat(64),
  schemaSha256:'b'.repeat(64),
  effectiveFrom:'2026-11-01',effectiveUntil:'2026-12-31',
  nonDisplayResearchPermission:'CLAIMED_PERMITTED',
  virtualSimulationPermission:'CLAIMED_PERMITTED',
  localRetentionPermission:'CLAIMED_PERMITTED',
  publicRedistributionPermission:'DENIED',
  independentReviewRecorded:true,
  reviewedAtMs:Date.parse('2026-11-11T08:00:00Z')
});
const opts={sessionDate:'2026-11-16'};
const contains=(o,r)=>assert.ok(o.reasons.includes(r),JSON.stringify(o));
const never=o=>{
  assert.equal(o.canTrade,false);
  assert.equal(o.marketDataUseAuthorizedBySoftware,false);
  assert.equal(o.realOrderRoutePresent,false);
  assert.equal(o.independentlyVerifiedExchangeSessions,0);
};
test('published 2026 November 24 Tuesday is an equity holiday',()=>{
  const x=date('2026-11-24');
  assert.equal(x.status,'PUBLISHED_2026_EQUITY_HOLIDAY');
  never(x);
});
test('published 2026 December 25 Friday is an equity holiday',()=>{
  assert.equal(date('2026-12-25').status,'PUBLISHED_2026_EQUITY_HOLIDAY');
});
test('November 10 listed 2026 holiday is excluded',()=>{
  assert.equal(date('2026-11-10').status,'PUBLISHED_2026_EQUITY_HOLIDAY');
});
test('2026 January 15 election closure is represented',()=>{
  assert.equal(date('2026-01-15').status,'PUBLISHED_2026_EQUITY_HOLIDAY');
});
test('ordinary 2026 Monday is only a provisional published-list lookup',()=>{
  const x=date('2026-11-16');
  assert.equal(x.status,'PUBLISHED_2026_WEEKDAY_NOT_LISTED_AS_HOLIDAY');
  assert.equal(x.independentlyAuthenticatedMarketFeed,false);
  never(x);
});
test('2026 Sunday remains non-regular even with special muhurat sessions',()=>{
  const x=date('2026-11-08');
  assert.equal(x.status,'WEEKEND_NOT_REGULAR_SESSION');
});
test('2026 regular Saturday is not a weekday session',()=>{
  assert.equal(date('2026-11-21').status,'WEEKEND_NOT_REGULAR_SESSION');
});
test('2027 calendar cannot inherit 2026 publication',()=>{
  const x=date('2027-01-01');
  assert.equal(x.status,'BLOCKED_OUTSIDE_PINNED_2026_YEAR');
  never(x);
});
test('past 2025 date cannot inherit official 2026 calendar',()=>{
  assert.equal(date('2025-11-24').status,'BLOCKED_OUTSIDE_PINNED_2026_YEAR');
});
test('invalid leap day or invalid date rejected',()=>{
  for(const x of ['2026-02-29','2026-13-01','2026-11-31','2026/11/16',''])
    assert.equal(date(x).status,'BLOCKED_INVALID_DATE');
});
test('pre-frozen long plan exists, but future-year coverage remains blocked',()=>{
  const p=plan();
  assert.equal(p.status,'FROZEN_MANIFEST_INDEPENDENT_REVIEW_REQUIRED');
  const x=calendar(p);
  assert.equal(x.status,'BLOCKED_CALENDAR_MISMATCH_OR_SCOPE');
  contains(x,'CALENDAR_YEAR_OUTSIDE_PINNED_2026_COVERAGE');
  assert.equal(x.omittedHolidayCount,0);
  assert.equal(x.known2026ExcludedHolidays,2);
  assert.ok(x.unpinnedFutureWeekdays>0);
  never(x);
});
test('omitting November 24 falsely creates a trading day and is caught',()=>{
  const p=params();p.declaredClosedWeekdays=['2026-12-25'];
  const x=calendar(freeze(p));
  contains(x,'PUBLISHED_NSE_HOLIDAY_INCLUDED_IN_SESSION_PLAN');
  assert.equal(x.omittedHolidayCount,1);
});
test('omitting both late-2026 holidays flags two omissions',()=>{
  const p=params();p.declaredClosedWeekdays=[];
  const x=calendar(freeze(p));
  assert.equal(x.omittedHolidayCount,2);
  never(x);
});
test('inventing a November 17 closure is not silently accepted',()=>{
  const p=params();p.declaredClosedWeekdays.push('2026-11-17');
  const x=calendar(freeze(p));
  contains(x,'UNVERIFIED_EXTRA_WEEKDAY_CLOSURE');
  assert.equal(x.unexplainedExtraClosureCount,1);
});
test('adding a future 2027 claimed closure cannot certify that year',()=>{
  const p=params();p.declaredClosedWeekdays.push('2027-01-01');
  const x=calendar(freeze(p));
  contains(x,'CALENDAR_YEAR_OUTSIDE_PINNED_2026_COVERAGE');
});
test('mutated frozen manifest cannot be calendar-checked as published proof',()=>{
  const p=plan();p.manifest.declaredClosedWeekdays=[];
  const x=calendar(p);
  assert.equal(x.status,'BLOCKED_INVALID_PLAN');
  never(x);
});
test('mutated expected weekday set fails independent reconstruction',()=>{
  const p=plan();p.expectedSessionDates.shift();
  assert.equal(calendar(p).status,'BLOCKED_INVALID_PLAN');
});
test('invalid uncreated plan is blocked',()=>{
  assert.equal(calendar({}).status,'BLOCKED_INVALID_PLAN');
  assert.equal(calendar(null).status,'BLOCKED_INVALID_PLAN');
});
test('self-claimed complete rights still require external contract attestation',()=>{
  const x=rights(receipt(),opts);
  assert.equal(x.status,'DECLARED_RIGHTS_CLAIM_EXTERNAL_ATTESTATION_REQUIRED');
  contains(x,'EXTERNAL_CONTRACT_AND_PROVIDER_ATTESTATION_REQUIRED');
  assert.equal(x.sourceTermsIndependentlyVerified,false);
  never(x);
});
test('unknown non-display use is independently blocked',()=>{
  const r=receipt();r.nonDisplayResearchPermission='UNKNOWN';
  const x=rights(r,opts);
  contains(x,'MISSING_OR_DENIED_NONDISPLAYRESEARCHPERMISSION');
  assert.equal(x.status,'BLOCKED_RIGHTS_SCOPE_OR_UNVERIFIED');
});
test('denied virtual simulation rights are blocked',()=>{
  const r=receipt();r.virtualSimulationPermission='DENIED';
  const x=rights(r,opts);
  contains(x,'MISSING_OR_DENIED_VIRTUALSIMULATIONPERMISSION');
});
test('denied local retention rights are blocked',()=>{
  const r=receipt();r.localRetentionPermission='DENIED';
  const x=rights(r,opts);
  contains(x,'MISSING_OR_DENIED_LOCALRETENTIONPERMISSION');
});
test('unknown redistribution rights remain a disclosure blocker',()=>{
  const r=receipt();r.publicRedistributionPermission='UNKNOWN';
  const x=rights(r,opts);
  contains(x,'UNKNOWN_REDISTRIBUTION_RESTRICTIONS');
});
test('claimed rights outside effective date range cannot carry over',()=>{
  const x=rights(receipt(),{sessionDate:'2027-01-04'});
  contains(x,'SESSION_OUTSIDE_DECLARED_CONTRACT_DATES');
  never(x);
});
test('independent review not recorded remains blocked',()=>{
  const r=receipt();r.independentReviewRecorded=false;r.reviewedAtMs=null;
  contains(rights(r,opts),'INDEPENDENT_REVIEW_NOT_RECORDED');
});
test('claimed reviewed status cannot be true with missing timestamp',()=>{
  const r=receipt();r.reviewedAtMs=null;
  assert.equal(rights(r,opts).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
});
test('bogus reviewed timestamp with no review flag is rejected',()=>{
  const r=receipt();r.independentReviewRecorded=false;
  assert.equal(rights(r,opts).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
});
test('invalid agreement hash cannot be misrepresented as proof',()=>{
  const r=receipt();r.agreementSha256='public-doc';
  assert.equal(rights(r,opts).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
});
test('bad source schema digest is invalid',()=>{
  const r=receipt();r.schemaSha256='c';
  assert.equal(rights(r,opts).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
});
test('contract start date after end is invalid',()=>{
  const r=receipt();r.effectiveFrom='2027-12-01';
  assert.equal(rights(r,opts).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
});
test('no vague data products beyond 1-minute NSE cash within current contract',()=>{
  const r=receipt();r.productGranularity='ALL_MARKET_DATA';
  assert.equal(rights(r,opts).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
});
test('invalid provider type and unknown contract use rejected',()=>{
  const r=receipt();r.dataProvidedBy='SCRAPED_WEBSITE';
  assert.equal(rights(r,opts).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
  const s=receipt();s.usagePurpose='ANYTHING';
  assert.equal(rights(s,opts).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
});
test('raw access tokens and real account IDs cannot be added to receipt',()=>{
  for(const k of ['access_token','account_id','raw_market_candles','oauth_secret']){
    const r=receipt();r[k]='SECRET';
    assert.equal(rights(r,opts).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
  }
});
test('invalid session date cannot accidentally inherit contract scope',()=>{
  assert.equal(rights(receipt(),{sessionDate:'2026-02-29'}).status,
    'BLOCKED_INVALID_RIGHTS_RECEIPT');
  assert.equal(rights(receipt(),{}).status,'BLOCKED_INVALID_RIGHTS_RECEIPT');
});
test('composite even with positive claims blocks data ingestion and orders',()=>{
  const x=combined(plan(),receipt(),opts);
  assert.equal(x.status,'NO_DATA_INGESTION_OR_LIVE_EXECUTION_AUTHORIZED');
  assert.equal(x.recommendedAction,'NO_TRADE_AND_NO_UNLICENSED_DATA_INGESTION');
  assert.equal(x.marketDataUseAuthorizedBySoftware,false);
  assert.equal(x.liveTradingAuthorized,false);
  never(x);
});
test('composite detects both missing holiday and unlicensed use',()=>{
  const p=params();p.declaredClosedWeekdays=[];
  const r=receipt();r.virtualSimulationPermission='DENIED';
  const x=combined(freeze(p),r,opts);
  contains(x,'PUBLISHED_NSE_HOLIDAY_INCLUDED_IN_SESSION_PLAN');
  contains(x,'MISSING_OR_DENIED_VIRTUALSIMULATIONPERMISSION');
});
test('no user identifiers, contract hashes or receipt claims echoed in verdict',()=>{
  const r=receipt(),x=combined(plan(),r,opts),serialized=JSON.stringify(x);
  assert.equal(serialized.includes(r.agreementSha256),false);
  assert.equal(serialized.includes(r.providerReference),false);
  assert.equal(serialized.includes(r.schemaSha256),false);
});
