import test from 'node:test';
import assert from 'node:assert/strict';
import {syntheticFixture,runCryptoAgentNetwork,verifyCryptoAgentLedger}
 from './crypto_interdependent_agent_network.mjs';

const execute=async(snapshot)=>{
 const s=snapshot??syntheticFixture();
 return runCryptoAgentNetwork(s,{clockMs:s.candles.at(-1).closeTimeMs});
};
function growthFixture(rate=.0015){
 const s=syntheticFixture();
 s.candles=s.candles.map((b,i)=>{
  const close=60000*(1+rate*i),open=close*.9999;
  return {...b,open,low:open*.9998,high:close*1.0002,close,volume:100+i%5};
 });
 s.costAssumptions={
   feeBpsPerSide:5,slippageBpsPerSide:5,
   spreadRoundTripBps:4,uncertaintyBps:4,independentlyVerified:true
 };
 return s;
}
test('default synthetic demonstration: exactly 9 dependent modules, no API/order or real profit assertion',async()=>{
 const r=await execute();
 assert.equal(r.project,'QHAP-CRYPTO-RESEARCH');
 assert.equal(r.sourceClass,'SYNTHETIC');
 assert.equal(r.counts.agents,9);
 assert.equal(r.realOrdersSent,0);
 assert.equal(r.paperOrdersSent,0);
 assert.equal(r.apiRequestsMade,0);
 assert.equal(r.modelRequestsMade,0);
 assert.equal(r.claimedProfitableEdge,false);
 assert.equal(r.execution,'DISABLED');
 assert.equal(r.finalDecision,'NO_TRADE');
 assert.equal(r.counts.independentEvidenceSources,1);
 assert.equal(verifyCryptoAgentLedger(r),true);
});
test('strictly sequential DAG and mandatory final guardian cannot be skipped',async()=>{
 const r=await execute(growthFixture());
 assert.equal(r.agentMessages[0].name,'SOURCE_INTEGRITY');
 assert.equal(r.agentMessages.at(-1).name,'NON_OVERRIDABLE_RISK_GUARDIAN');
 const id=new Set();
 for(const row of r.agentMessages){
  assert.ok(row.dependsOn.every(x=>id.has(x)));
  id.add(row.id);
 }
 assert.equal(verifyCryptoAgentLedger(r),true);
});
test('strong synthetic trend can be WATCH only; never PAPER_FILL or REAL_ORDER',async()=>{
 const r=await execute(growthFixture());
 assert.equal(r.status,'PAPER_RESEARCH_WATCH_ONLY');
 assert.equal(r.researchWatch,true);
 assert.equal(r.realOrderRoutePresent,false);
 assert.equal(r.paperOrdersSent,0);
 assert.equal(r.finalDecision,'NO_TRADE');
 assert.equal(r.autonomousLiveTradingAllowed,false);
 assert.ok(r.riskVetoes.includes('NO_INDEPENDENT_AFTER_COST_EDGE'));
 assert.ok(r.riskVetoes.includes('CRYPTO_TAX_ACCOUNTING_NOT_CERTIFIED'));
});
test('independent source and quote depth not implied from five variants of same candle stream',async()=>{
 const r=await execute(growthFixture());
 const skeptic=r.agentMessages.find(x=>x.name==='ADVERSARIAL_SKEPTIC');
 const liquidity=r.agentMessages.find(x=>x.name==='LIQUIDITY_PROXY');
 assert.equal(skeptic.metadata.independentPriceSources,1);
 assert.equal(skeptic.metadata.agentVotesDoNotEstablishSignalIndependence,true);
 assert.equal(liquidity.metadata.orderBookDepthObserved,false);
 assert.equal(r.marketDataLicenseIndependentlyVerified,false);
});
test('missing historical bar refuses and never fabricates intermediate price',async()=>{
 const f=syntheticFixture();
 f.candles.splice(35,1);
 const r=await execute(f);
 assert.equal(r.status,'NO_TRADE_RESEARCH_HALT');
 assert.equal(r.reason,'INVALID_CANDLE_OR_GAP');
 assert.equal(r.realOrdersSent,0);
});
test('lookahead candle closes after decision time are rejected',async()=>{
 const f=syntheticFixture();
 const r=await runCryptoAgentNetwork(f,{
  clockMs:f.candles.at(-1).closeTimeMs-1000
 });
 assert.equal(r.reason,'LOOKAHEAD_CANDLE_NOT_YET_CLOSED');
 assert.equal(r.agentMessages?.length||0,0);
});
test('stale local candle feed fails closed',async()=>{
 const f=syntheticFixture();
 const r=await runCryptoAgentNetwork(f,{
  clockMs:f.candles.at(-1).closeTimeMs+120001
 });
 assert.equal(r.reason,'STALE_CANDLE_FEED');
});
test('timestamp order and negative volume, inconsistent OHLCV block decision',async()=>{
 for(const change of [
  s=>{s.candles[9].closeTimeMs=s.candles[8].closeTimeMs;},
  s=>{s.candles[10].volume=-2;},
  s=>{s.candles[12].high=s.candles[12].low*.9;},
  s=>{s.candles[20].close=NaN;}
 ]){
  const s=syntheticFixture();change(s);
  const r=await execute(s);
  assert.equal(r.reason,'INVALID_CANDLE_OR_GAP');
  assert.equal(r.realOrdersSent,0);
 }
});
test('unsupported market and source class cannot enable real or paper trades',async()=>{
 for(const change of [
  s=>{s.market='DOGE-PERP';},
  s=>{s.sourceClass='LIVE_EXCHANGE_AUTH';},
  s=>{s.candles=s.candles.slice(-10);}
 ]){
  const s=syntheticFixture();change(s);
  const r=await execute(s);
  assert.equal(r.status,'NO_TRADE_RESEARCH_HALT');
  assert.equal(r.reason,'INVALID_REPLAY_INPUT');
 }
});
test('unknown or unverified fee model never authorizes paper order',async()=>{
 const s=growthFixture();
 s.costAssumptions.independentlyVerified=false;
 const r=await execute(s);
 assert.equal(r.paperOrdersSent,0);
 assert.equal(r.realOrdersSent,0);
 assert.ok(r.riskVetoes.includes('UNVERIFIED_FEES'));
 assert.equal(r.finalDecision,'NO_TRADE');
});
test('all friction included one time: two-sided fee/slippage and roundtrip spread',async()=>{
 const s=growthFixture();
 const r=await execute(s);
 assert.equal(r.costsBps.roundTripBps,28);
 assert.equal(r.costsBps.stress3xBps,84);
 assert.equal(r.costsBps.taxModelVerified,false);
 assert.equal(r.costsBps.venueExecutionPricesVerified,false);
});
test('bad fee fields are rejected, even with a powerful trend',async()=>{
 for(const change of [
  a=>{a.spreadRoundTripBps=-1;},
  a=>{a.slippageBpsPerSide=Infinity;},
  a=>{a.feeBpsPerSide=9999;},
  a=>{a.independentlyVerified='true';}
 ]){
  const s=growthFixture();change(s.costAssumptions);
  const r=await execute(s);
  assert.equal(r.reason,'INVALID_COST_ASSUMPTIONS');
  assert.equal(r.finalDecision,'NO_TRADE');
 }
});
test('adversarial price overextension veto works without trusting momentum vote',async()=>{
 const s=growthFixture(.00010);
 const end=s.candles.length-1;
 s.candles[end].close*=1.025;
 s.candles[end].high=s.candles[end].close*1.0002;
 const r=await execute(s);
 const opponent=r.agentMessages.find(x=>x.name==='MEAN_REVERSION_CHALLENGER');
 assert.equal(opponent.vote,'VETO_OVEREXTENDED');
 assert.equal(r.researchWatch,false);
 assert.equal(r.finalDecision,'NO_TRADE');
});
test('severe relative volume anomaly causes guardian abstention',async()=>{
 const s=growthFixture();
 s.candles.at(-1).volume=10000;
 const r=await execute(s);
 assert.equal(r.agentMessages.find(x=>x.name==='LIQUIDITY_PROXY').vote,
   'VETO_VOLUME_ANOMALY');
 assert.equal(r.researchWatch,false);
});
test('wild intraminute price moves veto watch regardless of majority',async()=>{
 const s=growthFixture();
 s.candles.at(-1).close*=1.08;
 s.candles.at(-1).high=s.candles.at(-1).close*1.0002;
 const r=await execute(s);
 assert.equal(r.agentMessages.find(x=>x.name==='VOLATILITY_WATCHDOG').vote,
   'VETO_VOLATILITY');
 assert.equal(r.researchWatch,false);
});
test('integrity verification detects tampered message or terminal veto',async()=>{
 const result=await execute(growthFixture());
 assert.equal(verifyCryptoAgentLedger(result),true);
 const corrupted=structuredClone(result);
 corrupted.agentMessages[2].vote='BUY';
 assert.equal(verifyCryptoAgentLedger(corrupted),false);
 const corrupted2=structuredClone(result);
 corrupted2.agentMessages.at(-1).vote='APPROVE';
 assert.equal(verifyCryptoAgentLedger(corrupted2),false);
 const corrupted3=structuredClone(result);
 corrupted3.auditChainHash='0000';
 assert.equal(verifyCryptoAgentLedger(corrupted3),false);
});
test('output contains no raw prices, trade P&L promises, wallet keys or actual LLM responses',async()=>{
 const r=await execute(growthFixture());
 const t=JSON.stringify(r);
 assert.ok(!t.includes('60000.0'));
 assert.ok(!t.includes('secret_key'));
 assert.equal(r.modelRequestsMade,0);
 assert.equal(r.apiRequestsMade,0);
 assert.equal(r.claimedProfitableEdge,false);
 assert.equal(r.independentlyVerifiedCryptoTaxes,false);
 assert.equal(r.autonomousLiveTradingAllowed,false);
});
