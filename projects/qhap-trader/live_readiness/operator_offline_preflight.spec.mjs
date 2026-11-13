import test from 'node:test';
import assert from 'node:assert/strict';
import {
  summarizeOfflineReleasePreflight as summarize,
  runLocalEngineeringPreflight as local,
  SUITE_NAMES,parseTapSummary
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



test('Windows CRLF Node26 TAP totals are parsed regardless of line ending',()=>{
  const text='TAP version 13\r\nok 1 - safe\r\n# tests 2\r\n# pass 2\r\n# fail 0\r\n';
  assert.deepEqual(parseTapSummary(text),{tests:2,passed:2,failed:0});
});
test('ANSI-wrapped TAP summaries are parsed without mistaking escape bytes',()=>{
  const text='\x1b[36m# tests 3\x1b[0m\r\n  # pass 3 \r\n# fail 0\r\n';
  assert.deepEqual(parseTapSummary(text),{tests:3,passed:3,failed:0});
});
test('Node26 default spec reporter cannot falsely pass as a TAP summary',()=>{
  const text='✔ safe test (1.233ms)\nℹ tests 1\nℹ pass 1\nℹ fail 0\n';
  assert.equal(parseTapSummary(text),null);
});
test('malformed, incomplete or implausible test totals cannot pass',()=>{
  for(const text of [null,'','# tests 2\n# pass 2\n',
    '# tests 2\n# pass 3\n# fail 0\n','# tests -1\n# pass 0\n# fail 0\n',
    '# tests 0\n# pass 0\n# fail 0\n']){
    assert.equal(parseTapSummary(text),null);
  }
});
test('TAP exit failure summary is parsed but never approved by preflight',()=>{
  const counts=parseTapSummary('# tests 2\r\n# pass 1\r\n# fail 1\r\n');
  assert.deepEqual(counts,{tests:2,passed:1,failed:1});
  const rows=green();
  rows[0]={...rows[0],...counts,status:'FAILED',exitCode:1};
  assert.equal(summarize(rows).testsPassed,false);
  assert.equal(summarize(rows).realOrderSubmissionPossible,false);
});
