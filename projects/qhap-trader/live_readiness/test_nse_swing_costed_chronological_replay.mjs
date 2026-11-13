import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {
  COST_REFERENCE,indicativeDeliverySideFees,
  hypotheticalNextOpenExecution,replayDailySwingDevelopment
} from './nse_swing_costed_chronological_replay.mjs';
import {syntheticEquityFixture}
 from './nse_swing_interdependent_agent_network.mjs';

const run=()=>replayDailySwingDevelopment(syntheticEquityFixture());
const localDir=t=>{
  const folder=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-swing-'));
  t.after(()=>fs.rmSync(folder,{recursive:true,force:true}));
  return folder;
};
test('2026 Upstox public fee arithmetic always distinguishes BUY and SELL delivery',()=>{
 const buy=indicativeDeliverySideFees('BUY',2500);
 const sell=indicativeDeliverySideFees('SELL',2500);
 assert.equal(buy.components.brokerage,20);
 assert.equal(sell.components.brokerage,20);
 assert.equal(buy.components.stt,2.5);
 assert.equal(sell.components.stt,2.5);
 assert.ok(Math.abs(buy.components.stamp-.375)<1e-10);
 assert.equal(sell.components.stamp,0);
 assert.equal(buy.components.dp,0);
 assert.equal(sell.components.dp,20);
 assert.ok(Math.abs(buy.components.exchange-.07675)<1e-10);
 assert.ok(Math.abs(buy.components.sebi-.0025)<1e-10);
 assert.ok(buy.total+sell.total>76);
 assert.ok(buy.total+sell.total<77);
 assert.equal(COST_REFERENCE.notAnExactHistoricalTariff,true);
 assert.equal(COST_REFERENCE.contractNoteFeeRoundingIndependentlyCertified,false);
});
test('static fee model does NOT pretend to know the user account schedule or 2024 rates',()=>{
 assert.equal(COST_REFERENCE.asOf,'2026-11-13');
 assert.equal(COST_REFERENCE.exchangeHistoricRate2024Certified,false);
 assert.equal(COST_REFERENCE.ipftAndOtherAccountSpecificChargesFullyCertified,false);
 assert.equal(COST_REFERENCE.brokeragePerExecutedOrderRupees,20);
 assert.equal(COST_REFERENCE.dpChargePerScripSellDayRupees,20);
});
test('invalid fees cannot create negative or nonfinite prices',()=>{
 for(const x of [
  ['SELL',-1],['BUY',0],['SELL',Infinity],['FORWARD',2500]
 ])assert.throws(()=>indicativeDeliverySideFees(...x),/INVALID_DELIVERY_FEE_INPUT/);
 for(const a of [
  [0,'BUY',1],[NaN,'SELL',1],[100,'BUY',0],
  [100,'OPEN',1],[100,'SELL',4]
 ])assert.throws(()=>hypotheticalNextOpenExecution(...a),
   /INVALID_HYPOTHETICAL_FILL_INPUT/);
});
test('adverse modeled buy/slippage above open, sell below; triple stress larger',()=>{
 const buy1=hypotheticalNextOpenExecution(100,'BUY',1),
  buy3=hypotheticalNextOpenExecution(100,'BUY',3),
  sell1=hypotheticalNextOpenExecution(100,'SELL',1),
  sell3=hypotheticalNextOpenExecution(100,'SELL',3);
 assert.ok(buy3>buy1&&buy1>100);
 assert.ok(sell3<sell1&&sell1<100);
});
test('one synthetic 100-bar dataset is hypothetically replayed with next-open only, NO broker orders',async()=>{
 const r=await run();
 assert.equal(r.status,'LOCAL_DAILY_DEVELOPMENT_REPLAY_COMPLETED_NO_TRADE');
 assert.equal(r.finalBrokerDecision,'NO_TRADE');
 assert.equal(r.realOrdersSent,0);
 assert.equal(r.paperOrdersSent,0);
 assert.equal(r.brokerOrderRoutePresent,false);
 assert.equal(r.networkRequestsMade,0);
 assert.equal(r.modelApiCallsMade,0);
 assert.equal(r.initialVirtualCapitalRupees,10000);
 assert.equal(r.maxSingleHypotheticalOrderTotalBudgetRupees,2500);
 assert.equal(r.scenarios.length,3);
 assert.deepEqual(r.scenarios.map(x=>x.agentWatchPolicy.frictionMultiplier),
  [1,2,3]);
 assert.equal(r.sourceDays,100);
 assert.equal(r.independentEvidenceOfProfit,false);
 assert.equal(r.historicalTariffAndTaxesAccountAccurate,false);
 assert.equal(r.researchSampleType,'INSPECTED_DEVELOPMENT_NOT_UNSEEN_HOLDOUT');
});
test('watch policy records honest hypothetical trades and NO_TRADE baseline at zero',async()=>{
 const r=await run();
 for(const caseOf of r.scenarios){
   const a=caseOf.agentWatchPolicy;
   assert.ok(a.hypotheticalRoundTrips>=1);
   assert.ok(a.agentAuditVerifiedDecisions>=1);
   assert.equal(a.finalPosition,'FLAT_BY_LAST_OBSERVED_SESSION_OPEN');
   assert.equal(a.finalStateNotARealExchangeFill,true);
   assert.equal(a.realizedPnlIsHypothetical,true);
   assert.equal(caseOf.noTradeRupees,0);
   assert.equal(caseOf.remainingCapitalUnleveraged,true);
   assert.equal(caseOf.passiveSameBudget.hypotheticalRoundTrips,1);
   assert.equal(caseOf.passiveSameBudget.initialOrderBudgetRupees,2500);
 }
});
test('replay never uses same-day close to enter; changing LAST close leaves P&L unchanged',async()=>{
 const initial=syntheticEquityFixture();
 const changed=structuredClone(initial);
 changed.dailyBars.at(-1).close*=1.07;
 changed.dailyBars.at(-1).high=changed.dailyBars.at(-1).close*1.002;
 const base=await replayDailySwingDevelopment(initial);
 const alt=await replayDailySwingDevelopment(changed);
 assert.deepEqual(base.scenarios.map(x=>x.agentWatchPolicy.aggregateIllustrativeNetRupees),
   alt.scenarios.map(x=>x.agentWatchPolicy.aggregateIllustrativeNetRupees));
 assert.deepEqual(base.scenarios.map(x=>x.passiveSameBudget.netRupees),
   alt.scenarios.map(x=>x.passiveSameBudget.netRupees));
});
test('even rising synthetic prices can lose money after fixed brokerage and DP costs',async()=>{
 const r=await run();
 assert.ok(r.scenarios.every(x=>
   x.agentWatchPolicy.public2026ProFormaBrokerFeesAndTaxesRupees>0));
 assert.ok(r.scenarios.every(x=>
   x.passiveSameBudget.feesAndTaxesRupees>0));
 assert.equal(r.profitableEdgeDemonstrated,undefined);
 assert.equal(r.independentEvidenceOfProfit,false);
});
test('all stress scenarios use the same original bars and independent audit guardian checks',async()=>{
 const r=await run();
 assert.ok(r.scenarios.every(x=>x.agentWatchPolicy.eligibleDailyBars===100));
 assert.ok(r.scenarios.every(x=>x.agentWatchPolicy.agentAuditVerifiedDecisions>0));
 assert.ok(r.scenarios.every(x=>x.agentWatchPolicy.agentAuditVerifiedDecisions<=20));
 assert.ok(r.scenarios.every(x=>x.agentWatchPolicy.endVirtualCashRupees>=0));
});
test('strict source validation refuses unbounded, broken date or invented candle',async()=>{
 for(const change of [
   d=>{d.dailyBars=d.dailyBars.slice(0,45);},
   d=>{d.dailyBars[40].close=-1;},
   d=>{d.dailyBars[20].date=d.dailyBars[19].date;},
   d=>{d.asOfDate='2024-01-02';},
   d=>{d.instrumentKey='BTC-USDT';}
 ]){
   const d=syntheticEquityFixture();change(d);
   await assert.rejects(replayDailySwingDevelopment(d));
 }
});
test('lookahead guard refuses future close signal on incomplete daily history',async()=>{
 const d=syntheticEquityFixture();
 d.dailyBars[90].close=Infinity;
 await assert.rejects(replayDailySwingDevelopment(d));
});
test('no secret, exchange trading route or model key appears in program source',()=>{
 const source=fs.readFileSync(new URL(
   './nse_swing_costed_chronological_replay.mjs',import.meta.url),'utf8');
 for(const sensitive of ['https://api-hft.upstox.com',
  'https://api-sandbox.upstox.com','UPSTOX_ACCESS_TOKEN',
  'OPENROUTER_API_KEY','https://api.binance','fetch(']){
   assert.equal(source.includes(sensitive),false,sensitive);
 }
});
test('existing private fixture can be locally serialized without exporting bars in result',async t=>{
 const root=localDir(t);
 const d=syntheticEquityFixture();
 d.sourceClass='PRIVATE_REPLAY';
 const sourceFile=path.join(root,'nse-priv.json');
 fs.writeFileSync(sourceFile,JSON.stringify(d));
 const loaded=JSON.parse(fs.readFileSync(sourceFile,'utf8'));
 const result=await replayDailySwingDevelopment(loaded);
 assert.equal(result.sourceClassification,'PRIVATE_REPLAY');
 assert.equal(result.sourceDays,100);
 assert.equal(result.realOrdersSent,0);
 assert.ok(!JSON.stringify(result).includes('"volume"'));
 assert.ok(!JSON.stringify(result).includes('"close"'));
});
