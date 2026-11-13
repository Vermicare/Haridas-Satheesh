import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {COST_HURDLE_POLICY,hypotheticalDeliveryNet,
  assessDeliveryCostHurdle,fixedDeliveryCostHurdleGrid}
  from './equity_delivery_cost_hurdle.mjs';

test('tiny fixed whole-share position never exceeds ₹2500 including BUY fees',()=>{
  for(const px of [250,500,1000,1500,2000])for(const stress of [1,2,3]){
    const x=assessDeliveryCostHurdle(px,stress);
    assert.ok(x.indicativeEntryCashUsedRupees<=2500);
    assert.ok(x.hypotheticalQuantity>=1);
    assert.equal(x.realOrderSubmissionPossible,false);
    assert.equal(x.finalBrokerDecision,'NO_TRADE');
  }
});
test('a ₹2500 reference share cannot be purchased within ₹2500 after fees',()=>{
  const x=assessDeliveryCostHurdle(2500);
  assert.equal(x.hypotheticalQuantity,0);
  assert.equal(x.breakEvenReferenceExitRupees,null);
  assert.equal(x.affordability,'NO_WHOLE_SHARE_WITHIN_2500_TOTAL_BUDGET');
});
test('exact threshold zeros costed hypothetical net, not gross return',()=>{
  for(const px of [250,500,1000,1500])for(const stress of [1,2,3]){
    const x=assessDeliveryCostHurdle(px,stress);
    const idealExit=px*(1+x.breakEvenRawOpenAppreciationPercent/100);
    const p=hypotheticalDeliveryNet(px,idealExit,stress);
    assert.ok(Math.abs(p.hypotheticalNetRupees)<0.005,JSON.stringify(x));
    assert.ok(x.indicativeCombinedFeesAtThresholdRupees>0);
    assert.ok(x.breakEvenRawOpenAppreciationPercent>0);
  }
});
test('higher assumed friction strictly raises price appreciation hurdle',()=>{
  for(const px of [250,500,1000,1500,2000]){
    const hurdles=[1,2,3].map(s=>assessDeliveryCostHurdle(px,s)
      .breakEvenRawOpenAppreciationPercent);
    assert.ok(hurdles[0]<hurdles[1]&&hurdles[1]<hurdles[2],
      `${px}: ${hurdles.join(',')}`);
  }
});
test('flat raw price yields negative modeled net because of costs and fills',()=>{
  for(const px of [250,500,1000,1500,2000]){
    const a=hypotheticalDeliveryNet(px,px,1);
    assert.ok(a.hypotheticalNetRupees<0);
  }
});
test('cost hurdle output is immutable fixed research grid with no price data',()=>{
  const r=fixedDeliveryCostHurdleGrid();
  assert.equal(r.results.length,18);
  assert.equal(r.marketDataAccessed,false);
  assert.equal(r.strategyBacktested,false);
  assert.equal(r.realOrdersSent,0);
  assert.equal(r.paperOrdersSent,0);
  assert.equal(r.brokerOrderRoutePresent,false);
  assert.equal(COST_HURDLE_POLICY.actualExecutionAndContractNoteCertified,false);
  assert.equal(COST_HURDLE_POLICY.dividendAndCorporateActionAdjustmentCertified,false);
});
test('malformed numbers or stress factors fail closed',()=>{
  for(const v of [-1,0,NaN,Infinity,'1000',1e9])
    assert.throws(()=>assessDeliveryCostHurdle(v),/INVALID_COST_HURDLE_INPUT/);
  for(const v of [0,4,'1',null])
    assert.throws(()=>assessDeliveryCostHurdle(1000,v),/INVALID_COST_HURDLE_INPUT/);
  assert.throws(()=>hypotheticalDeliveryNet(1000,0),/INVALID_COST_HURDLE_INPUT/);
});
test('module never contains market connectivity, secrets or orders',()=>{
  const src=fs.readFileSync(new URL('./equity_delivery_cost_hurdle.mjs',import.meta.url),'utf8');
  for(const forbidden of ['fetch(', 'https://api-hft.', 'UPSTOX_ACCESS_TOKEN',
    'OPENROUTER_API_KEY', 'placeOrder(', 'axios', 'WebSocket'])
    assert.equal(src.includes(forbidden),false,forbidden);
});
test('standalone command has identical safe grid',()=>{
  const raw=execFileSync(process.execPath,[fileURLToPath(new URL(
    './equity_delivery_cost_hurdle.mjs',import.meta.url))],
    {encoding:'utf8',timeout:10000});
  assert.deepEqual(JSON.parse(raw),fixedDeliveryCostHurdleGrid());
});
