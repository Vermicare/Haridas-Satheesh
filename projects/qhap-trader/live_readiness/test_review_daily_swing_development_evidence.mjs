import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {reviewDailySwingAggregate}
 from './review_daily_swing_development_evidence.mjs';
const source=new URL(
 '../experiments/evidence/RELIANCE_UPSTOX_204DAY_SWING_DEVELOPMENT_20261113.json',
 import.meta.url);
const input=()=>JSON.parse(fs.readFileSync(source,'utf8'));
test('archived user-sanitized 204-day swing evidence correctly rejects current rules',()=>{
 const r=reviewDailySwingAggregate(input());
 assert.equal(r.status,
  'REJECT_9_AGENT_SWING_LIVE_CANDIDATE_DEVELOPMENT_EVIDENCE');
 assert.equal(r.finalBrokerDecision,'NO_TRADE');
 assert.equal(r.livePromotionAuthorized,false);
 assert.equal(r.realOrdersSent,0);
 assert.equal(r.paperOrdersSent,0);
 assert.equal(r.brokerRoutePresent,false);
 assert.equal(r.independentlyValidatedProfitability,false);
 assert.equal(r.inspectedDailyBars,204);
 assert.equal(r.amountOfIndependentHoldoutEvidence,0);
 assert.equal(r.allCostScenarioAccountingsReconcile,true);
 assert.equal(r.allScenariosNetNegative,true);
 assert.equal(r.allScenariosWorseThanPassive,true);
 assert.equal(r.grossProfitBeforeCostsAbsent,true);
 assert.equal(r.allHypotheticalRoundTripsNetLosing,true);
 assert.equal(r.stricterFrictionWorsenedLoss,true);
 assert.equal(r.canProveSwingStrategyNeverWorks,false);
 assert.equal(r.neverTuneAndRetestSameDatesAsUnseen,true);
});
test('actual user 1x/2x/3x INR net and underperformance preserved with decimal fidelity',()=>{
 const r=reviewDailySwingAggregate(input());
 assert.deepEqual(r.hypotheticalRoundTripsPerStress,[5,5,5]);
 assert.deepEqual(r.modeledNetRupeesPerStress,
  [-442.458,-478.9865,-515.5149]);
 assert.deepEqual(r.underperformanceVsSameBudgetPassiveRupees,
  [-247.166,-277.009,-306.8518]);
 assert.equal(r.baseCaseCostShareOfAbsoluteLossPct,92.09);
});
test('observed 2024 development cannot be upgraded to untouched holdout',()=>{
 const e=input();e.researchClass='UNSEEN_HOLDOUT';
 const r=reviewDailySwingAggregate(e);
 assert.equal(r.status,'INVALID_OR_UNTRUSTED_DEVELOPMENT_AGGREGATE_NO_TRADE');
 assert.equal(r.reason,'SOURCE_OR_SCOPE_MISMATCH');
});
test('an injected claim of positive independent edge is not silently trusted',()=>{
 const e=input();e.tradingEdgeIndependentlyVerified=true;
 const r=reviewDailySwingAggregate(e);
 assert.equal(r.status,'INVALID_OR_UNTRUSTED_DEVELOPMENT_AGGREGATE_NO_TRADE');
 assert.equal(r.livePromotionAuthorized,false);
});
test('tampered cash/fees/PnL breakdown refuses to classify as validated',()=>{
 for(const change of [
  e=>{e.scenarios[0].agent.netRupees=-1;},
  e=>{e.scenarios[2].agent.endingVirtualCashRupees=10000;},
  e=>{e.scenarios[1].passive.netRupees=-1;},
  e=>{e.scenarios[0].agent.modeledFeesRupees=-3;},
  e=>{e.scenarios[0].agent.grossRupees=NaN;}
 ]){
  const e=input();change(e);
  const r=reviewDailySwingAggregate(e);
  assert.equal(r.status,'INVALID_OR_UNTRUSTED_DEVELOPMENT_AGGREGATE_NO_TRADE');
  assert.equal(r.livePromotionAuthorized,false);
 }
});
test('bad stress cardinality, order count or scenario order blocks review',()=>{
 for(const change of [
  e=>{e.scenarios.pop();},
  e=>{e.scenarios[0].multiplier=2;},
  e=>{e.realOrdersSent=1;},
  e=>{e.paperOrdersSent=1;},
  e=>{e.finalBrokerDecision='BUY';},
  e=>{e.scenarios[1].agent.netWinningRoundTrips=7;},
  e=>{e.scenarios[0].noTradeNetRupees=-10;}
 ]){
  const e=input();change(e);
  const r=reviewDailySwingAggregate(e);
  assert.equal(r.status,'INVALID_OR_UNTRUSTED_DEVELOPMENT_AGGREGATE_NO_TRADE');
  assert.equal(r.realOrdersSent,0);
 }
});
test('positive development performance never certifies future profitability',()=>{
 const e=input();
 for(const s of e.scenarios){
   s.agent.grossRupees=1000;
   s.agent.netRupees=1000-s.agent.modeledFeesRupees-
     s.agent.modeledExecutionDragRupees;
   s.agent.endingVirtualCashRupees=10000+s.agent.netRupees;
   s.agent.netWinningRoundTrips=4;
 }
 const r=reviewDailySwingAggregate(e);
 assert.equal(r.status,'UNPROVEN_MODEL_DEVELOPMENT_ONLY_NO_TRADE');
 assert.equal(r.independentlyValidatedProfitability,false);
 assert.equal(r.livePromotionAuthorized,false);
 assert.equal(r.finalBrokerDecision,'NO_TRADE');
});
test('source SHA256 identity is mandatory but not exchange provenance attestation',()=>{
 const e=input();
 e.localArtifactSha256='1234';
 const r=reviewDailySwingAggregate(e);
 assert.equal(r.status,'INVALID_OR_UNTRUSTED_DEVELOPMENT_AGGREGATE_NO_TRADE');
});
test('aggregate-only input contains neither provider candles nor private token data',()=>{
 const e=input(),serialized=JSON.stringify(e);
 assert.equal(e.scenarios.length,3);
 assert.equal(serialized.includes('"dailyBars"'),false);
 assert.equal(serialized.includes('"open"'),false);
 assert.equal(serialized.includes('"high"'),false);
 assert.equal(serialized.includes('"low"'),false);
 assert.equal(serialized.includes('"volume"'),false);
 assert.equal(serialized.includes('PRIVATE_READ_ONLY_ANALYTICS_TOKEN'),false);
 assert.equal(serialized.includes('Bearer '),false);
});
test('negative user evidence is not a universal impossibility proof',()=>{
 const r=reviewDailySwingAggregate(input());
 assert.equal(r.classification,
  'REJECT_CURRENT_RULES_NOT_THE_ENTIRE_ASSET_CLASS');
 assert.equal(r.canProveSwingStrategyNeverWorks,false);
 assert.equal(r.guaranteedReturn,false);
 assert.equal(r.amountOfIndependentHoldoutEvidence,0);
});
