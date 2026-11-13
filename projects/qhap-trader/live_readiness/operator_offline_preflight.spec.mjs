import test from 'node:test';
import assert from 'node:assert/strict';
import {
  summarizeOfflineReleasePreflight as summarize,
  runLocalEngineeringPreflight as local,
  SUITE_NAMES
} from './operator_offline_preflight.mjs';

const green=()=>SUITE_NAMES.map((name,i)=>({
  name,status:'PASSED',exitCode:0,tests:10+i,passed:10+i,failed:0,
  noNetwork:true,noBrokerCredentialsPassed:true
}));

test('complete mock green tests are engineering-only, still NO_TRADE',()=>{
  const r=summarize(green());
  assert.equal(r.testsPassed,true);
  assert.equal(r.status,'ENGINEERING_OFFLINE_CHECKS_PASSED_EXTERNAL_GATES_OPEN');
  assert.equal(r.testCount,33);
  assert.equal(r.marketDataResearchLicenceIndependentlyVerified,false);
  assert.equal(r.liveFeedVirtualTradingRightsIndependentlyVerified,false);
  assert.equal(r.netProfitableStrategyIndependentlyVerified,false);
  assert.equal(r.realOrderSubmissionPossible,false);
  assert.equal(r.brokerOrderEndpointPresent,false);
  assert.equal(r.canTrade,false);
  assert.equal(r.recommendedAction,'NO_TRADE');
  assert.equal(r.reviewItemsClaimed,0);
  assert.equal(r.reviewItemsRequired,20);
});
test('missing test categories can never be reclassified as a pass',()=>{
  const r=summarize(green().slice(0,2));
  assert.equal(r.testsPassed,false);
  assert.equal(r.testCount,null);
  assert.equal(r.realOrdersSent,0);
});
test('duplicate test categories cannot disguise missing fee checks',()=>{
  const x=green();
  x[2]={...x[0]};
  assert.equal(summarize(x).testsPassed,false);
});
test('a test process success with zero tests fails closed',()=>{
  const x=green();
  x[1].tests=0;x[1].passed=0;
  assert.equal(summarize(x).testsPassed,false);
});
test('missing, failed, nonzero or stale pass totals fail closed',()=>{
  for(const change of [{status:'FAILED'},{failed:1},{passed:4},
    {exitCode:1},{tests:0},{exitCode:null}]){
    const x=green();x[0]={...x[0],...change};
    assert.equal(summarize(x).testsPassed,false);
    assert.equal(summarize(x).recommendedAction,'NO_TRADE');
  }
});
test('caller supplied fake order and verified claims are ignored',()=>{
  const x=green().map(o=>({...o,canTrade:true,realOrderSubmissionPossible:true,
    marketDataResearchLicenceIndependentlyVerified:true,netProfitableStrategyIndependentlyVerified:true}));
  const r=summarize(x);
  assert.equal(r.realOrderSubmissionPossible,false);
  assert.equal(r.brokerOrderEndpointPresent,false);
  assert.equal(r.liveTradingAuthorized,false);
  assert.equal(r.marketDataResearchLicenceIndependentlyVerified,false);
  assert.equal(r.netProfitableStrategyIndependentlyVerified,false);
});
test('ill-formed reports still refuse external and real trading',()=>{
  for(const x of [null,undefined,[],{},'ok',false]){
    const r=summarize(x);
    assert.equal(r.testsPassed,false);
    assert.equal(r.canTrade,false);
    assert.equal(r.realOrdersSent,0);
  }
});
test('local operator entrypoint can run actual entire offline suite with no secrets',()=>{
  const r=local();
  assert.equal(r.status,'ENGINEERING_OFFLINE_CHECKS_PASSED_EXTERNAL_GATES_OPEN');
  assert.equal(r.testsPassed,true);
  assert.equal(r.suites.length,3);
  assert.ok(r.testCount>=400);
  assert.ok(r.suites.every(x=>x.noNetwork&&x.noBrokerCredentialsPassed));
  assert.equal(r.brokerOrderEndpointPresent,false);
  assert.equal(r.realOrdersSent,0);
  assert.equal(r.recommendedAction,'NO_TRADE');
});
