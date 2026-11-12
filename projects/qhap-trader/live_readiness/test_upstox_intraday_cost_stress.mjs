import test from 'node:test';
import assert from 'node:assert/strict';
import {estimateSyntheticIntradayRoundTrip as calc,
  auditSyntheticCostSensitivity as matrix} from './upstox_intraday_cost_stress.mjs';

const flat=()=>({entryPriceRupees:100,exitPriceRupees:100,
  quantity:20,exitReason:'TIME'});
const winning=()=>({...flat(),exitPriceRupees:100.4});
const stopped=()=>({...flat(),exitPriceRupees:98,exitReason:'STOP'});
const halt=(trade,shock,status)=>assert.equal(calc(trade,shock).status,status);
test('flat ₹2000 paper roundtrip is negative after conservative Upstox estimate',()=>{
  const r=calc(flat());
  assert.equal(r.status,'SYNTHETIC_COST_ESTIMATE_ONLY');
  assert.equal(r.estimatedChargesRupees,5.96);
  assert.equal(r.netRupees,-5.96);
  assert.equal(r.grossRupees,0);
  assert.ok(r.reasons.includes('NO_POSITIVE_NET_ADVANTAGE_OVER_NO_TRADE'));
});
test('explicit fee components sum exactly to reported total paise',()=>{
  const r=calc(flat());
  assert.equal(Math.round(Object.values(r.feeComponentsRupees)
    .reduce((a,b)=>a+b,0)*100),Math.round(r.estimatedChargesRupees*100));
});
test('1000-rupee flat turnover has lower total charges than 2000',()=>{
  const a=calc({...flat(),quantity:10}),b=calc(flat());
  assert.ok(a.estimatedChargesRupees<b.estimatedChargesRupees);
});
test('2026 broker rate is modeled at 0.1 percent each leg under cap',()=>{
  const r=calc(flat());
  assert.equal(r.feeComponentsRupees.brokerage,4);
});
test('gross profit can disappear with extra 15 bps each side',()=>{
  const reference=calc(winning());
  const stressed=calc(winning(),{extraBuySlipBps:15,extraSellSlipBps:15});
  assert.ok(reference.netRupees>0);
  assert.ok(stressed.netRupees<0);
  assert.ok(stressed.adverseSlippagePenaltyRupees>5);
  assert.equal(stressed.canTrade,false);
});
test('more adverse slippage cannot improve modeled net outcome',()=>{
  const trade=winning();
  const cases=[0,5,15,30,50,200].map(n=>calc(trade,{
    extraBuySlipBps:n,extraSellSlipBps:n}).netRupees);
  for(let i=1;i<cases.length;i++)assert.ok(cases[i]<=cases[i-1]);
});
test('stop gap loss is additional to charges and slippage',()=>{
  const trade=stopped();
  const a=calc(trade,{extraBuySlipBps:15,extraSellSlipBps:15});
  const b=calc(trade,{extraBuySlipBps:15,extraSellSlipBps:15,stopGapBps:200});
  assert.equal(b.stopGapPenaltyRupees,39.2);
  assert.ok(b.netRupees<a.netRupees);
});
test('₹50 candidate loss budget signals breach without authorizing anything',()=>{
  const r=calc(stopped(),{extraBuySlipBps:15,extraSellSlipBps:15,stopGapBps:200});
  assert.equal(r.hypotheticalCandidateLossBudgetExceeded,true);
  assert.ok(r.reasons.includes('EXCEEDS_50_RUPEE_HYPOTHETICAL_LOSS_BUDGET'));
  assert.equal(r.canTrade,false);
});
test('positive modeled trade still never authorizes live execution',()=>{
  const r=calc({...flat(),exitPriceRupees:110});
  assert.ok(r.netRupees>0);
  assert.equal(r.liveTradingAuthorized,false);
  assert.equal(r.realOrderRoutePresent,false);
  assert.equal(r.independentlyVerifiedEdge,false);
});
test('reference-case matrix has 4 fixed shocks; no fitted optimization',()=>{
  const r=matrix(winning());
  assert.equal(r.status,'SYNTHETIC_NO_TRADE_REMAINS_REQUIRED');
  assert.deepEqual(r.scenarios.map(x=>x.scenario),[
    'REFERENCE_ONLY','ADVERSE_5_BPS_EACH_SIDE',
    'ADVERSE_15_BPS_EACH_SIDE','ADVERSE_50_BPS_EACH_SIDE']);
  assert.equal(r.recommendedLiveAction,'NO_TRADE');
});
test('stop-case matrix adds a 200bps gap stress automatically',()=>{
  const r=matrix(stopped());
  assert.equal(r.scenarios.length,5);
  assert.equal(r.worstHypotheticalLossBudgetExceeded,true);
  assert.ok(r.worstNetRupees<r.bestNetRupees);
});
test('no trade comparator remains zero regardless of sample',()=>{
  const r=matrix(winning());
  assert.equal(r.noTradeNetRupees,0);
  assert.equal(r.canTrade,false);
  assert.ok(r.scenarios.every(x=>x.noTradeNetRupees===0));
});
test('invalid negative or zero entry is rejected',()=>{
  for(const p of [-1,0])halt({...flat(),entryPriceRupees:p},{},'HALT_INVALID_INPUT');
});
test('NaN, Infinity and scientific overflow are rejected',()=>{
  for(const p of [NaN,Infinity,1e20])halt({...flat(),exitPriceRupees:p},
    {},'HALT_INVALID_INPUT');
});
test('fractional paisa prices and fractional quantity rejected',()=>{
  halt({...flat(),entryPriceRupees:100.001},{},'HALT_INVALID_INPUT');
  halt({...flat(),quantity:1.5},{},'HALT_INVALID_INPUT');
});
test('unknown trade state or missing exit cannot be treated as closed',()=>{
  halt({...flat(),exitReason:'OPEN'},{},'HALT_INVALID_INPUT');
  const x=flat();delete x.exitPriceRupees;
  halt(x,{},'HALT_INVALID_INPUT');
});
test('credentials and broker messages rejected at strict trade boundary',()=>{
  halt({...flat(),accessToken:'CANNOT_STORE'},{},'HALT_INVALID_INPUT');
  halt({...flat(),brokerOrderResponse:{}},{},'HALT_INVALID_INPUT');
});
test('unbounded hypothetical position fails account exposure guard',()=>{
  halt({...flat(),quantity:26},{},'HALT_LIMIT_BREACH');
  halt({...flat(),entryPriceRupees:10000,quantity:100},{},'HALT_LIMIT_BREACH');
});
test('₹2500 cap permitted exactly for synthetic stress',()=>{
  const r=calc({...flat(),quantity:25});
  assert.equal(r.status,'SYNTHETIC_COST_ESTIMATE_ONLY');
  assert.equal(r.entryNotionalRupees,2500);
});
test('no use of extra stop gap for non-stopped trade',()=>{
  halt(flat(),{stopGapBps:200},'HALT_INVALID_INPUT');
});
test('negative, fractional or absurd basis point shocks are blocked',()=>{
  for(const x of [-1,0.1,10001,Infinity,NaN])
    halt(flat(),{extraBuySlipBps:x},'HALT_INVALID_INPUT');
});
test('unknown shock fields (including token) are not accepted',()=>{
  halt(flat(),{extraSellSlipBps:10,oauth_token:'secret'},'HALT_INVALID_INPUT');
});
test('matrix with invalid input fails closed and exposes no pseudo-profit',()=>{
  const r=matrix({...flat(),quantity:100});
  assert.equal(r.status,'HALT_INCOMPLETE_COST_SENSITIVITY');
  assert.equal(r.scenarios,undefined);
  assert.equal(r.canTrade,false);
});
test('output contains no raw instrument, order, or credential fields',()=>{
  const r=calc(flat());
  assert.equal(JSON.stringify(r).includes('accessToken'),false);
  assert.equal(r.brokerReconciled,false);
  assert.equal(r.realOrdersSent,0);
});
