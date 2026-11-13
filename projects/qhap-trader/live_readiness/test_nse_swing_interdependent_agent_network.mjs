import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {
  syntheticEquityFixture,runEquitySwingAgentNetwork,
  verifyEquitySwingAgentAudit
} from './nse_swing_interdependent_agent_network.mjs';

const run=async fixture=>runEquitySwingAgentNetwork(fixture||syntheticEquityFixture());
test('synthetic NSE daily-bar demo creates nine real dependent roles and no orders',async()=>{
 const out=await run();
 assert.equal(out.market,'NSE_CASH_EQUITY_ONLY');
 assert.equal(out.project,'QHAP-TRADER');
 assert.equal(out.agentMessages.length,9);
 assert.equal(out.finalDecision,'NO_TRADE');
 assert.equal(out.realOrdersSent,0);
 assert.equal(out.paperOrdersSent,0);
 assert.equal(out.canTradeRealMoney,false);
 assert.equal(out.networkRequestsMade,0);
 assert.equal(out.modelApiCallsMade,0);
 assert.equal(out.cryptoMarketUsed,false);
 assert.equal(out.profitableEdgeDemonstrated,false);
 assert.equal(verifyEquitySwingAgentAudit(out),true);
});
test('source policy is NSE cash equity only; no crypto or derivates as literal trading scope',async()=>{
 for(const instrumentKey of ['BTC-USDT','NSE_FO|999','NSE_EQ|../secret','NSE_EQ|INE123']){
   const f=syntheticEquityFixture(); f.instrumentKey=instrumentKey;
   const out=await run(f);
   assert.equal(out.status,'EQUITY_RESEARCH_HALT_NO_TRADE');
   assert.equal(out.finalDecision,'NO_TRADE');
   assert.equal(out.realOrdersSent,0);
 }
});
test('strong illustrative trend produces research-watch only, never an executable signal',async()=>{
 const out=await run();
 assert.equal(out.researchWatch,true);
 assert.equal(out.status,'EQUITY_SWING_RESEARCH_WATCH_NOT_ORDER');
 assert.equal(out.agentMessages[7].vote,'LOW_TURNOVER_SWING_HYPOTHESIS_WATCH');
 assert.equal(out.agentMessages.at(-1).vote,'VETO_ALL_PAPER_AND_REAL_ORDER_ROUTES');
 assert.equal(out.realOrdersSent,0);
 assert.equal(out.paperOrdersSent,0);
 assert.equal(out.brokerOrderRoutePresent,false);
});
test('each module has explicit parent dependencies and an audit-chain digest',async()=>{
 const out=await run();
 const seen=new Set();
 for(const node of out.agentMessages){
   assert.ok(node.dependsOn.every(parent=>seen.has(parent)));
   seen.add(node.id);
   assert.ok(/^[a-f0-9]{64}$/.test(node.hash));
 }
 assert.equal(verifyEquitySwingAgentAudit(out),true);
});
test('correlated trend, volatility and liquidity observations count as one data source',async()=>{
 const out=await run();
 const skeptic=out.agentMessages.find(x=>x.name==='ADVERSARIAL_SKEPTIC');
 assert.equal(skeptic.evidence.signalFamiliesFromDistinctSourceCount,1);
 assert.equal(skeptic.evidence.economicEdgeFromEnsembleValidated,false);
 assert.equal(out.independentSourceFamiliesVerified,false);
});
test('news agent refuses invented corporate announcements or headlines',async()=>{
 const out=await run();
 const news=out.agentMessages.find(x=>x.name==='PUBLIC_NEWS_FACT_CHECKER');
 assert.equal(news.vote,'NO_VERIFIED_PUBLIC_NEWS_INPUT');
 assert.equal(news.evidence.earningsCalendarObserved,false);
 assert.equal(news.evidence.inventsNoHeadlines,true);
});
test('unverified cost schedule still causes guardian veto for hypothetical swing watch',async()=>{
 const out=await run();
 assert.equal(out.assumedCostBps.feeInputUserFlag,false);
 assert.equal(out.assumedCostBps.upstoxContractNoteValidatedByCode,false);
 assert.equal(out.assumedCostBps.dpDeliverySellChargeMustBeIncluded,true);
 assert.ok(out.assumedCostBps.stressThreeXCostBps>out.assumedCostBps.illustrativeRoundTripCostBps);
 assert.equal(out.finalDecision,'NO_TRADE');
});
test('user-provided fee-verified bool is NOT independent audit or live authorization',async()=>{
 const f=syntheticEquityFixture();
 f.costAssumptions.sourceScheduleIndependentlyVerified=true;
 const out=await run(f);
 assert.equal(out.assumedCostBps.feeInputUserFlag,true);
 assert.equal(out.assumedCostBps.upstoxContractNoteValidatedByCode,false);
 assert.equal(out.finalDecision,'NO_TRADE');
 assert.equal(out.profitableEdgeDemonstrated,false);
});
test('invalid cost inputs fail closed, even when synthetic trend is strong',async()=>{
 for(const field of [
   ['estimatedBrokerageAndTaxesRoundTripRupees',-1],
   ['slippageBpsPerSide',NaN],
   ['spreadRoundTripBps',Infinity],
   ['uncertaintyReserveBps',-5],
   ['sourceScheduleIndependentlyVerified','true']
 ]){
  const f=syntheticEquityFixture();
  f.costAssumptions[field[0]]=field[1];
  const out=await run(f);
  assert.equal(out.status,'EQUITY_RESEARCH_HALT_NO_TRADE');
  assert.equal(out.finalDecision,'NO_TRADE');
  assert.equal(out.brokerOrderRoutePresent,false);
 }
});
test('missing provider date, non-chronological bars or invalid OHLCV are rejected',async()=>{
 for(const fn of [
  f=>f.dailyBars.reverse(),
  f=>{f.dailyBars[10].volume=-1;},
  f=>{f.dailyBars[20].close=Infinity;},
  f=>{f.dailyBars[15].high=f.dailyBars[15].low*.9;},
  f=>{f.dailyBars[30].date=f.dailyBars[29].date;}
 ]){
  const f=syntheticEquityFixture();fn(f);
  const out=await run(f);
  assert.equal(out.status,'EQUITY_RESEARCH_HALT_NO_TRADE');
  assert.equal(out.finalDecision,'NO_TRADE');
 }
});
test('future-candle input cannot be used to make earlier decision',async()=>{
 const f=syntheticEquityFixture();
 f.asOfDate=f.dailyBars.at(-2).date;
 const out=await run(f);
 assert.equal(out.status,'EQUITY_RESEARCH_HALT_NO_TRADE');
 assert.equal(out.reason,'INVALID_DAILY_HISTORY');
});
test('stale historical decision boundary is rejected',async()=>{
 const f=syntheticEquityFixture();
 f.asOfDate='2024-12-31';
 const out=await run(f);
 assert.equal(out.status,'EQUITY_RESEARCH_HALT_NO_TRADE');
 assert.equal(out.reason,'STALE_DAILY_REPLAY_CLOCK');
});
test('replay with too few bars cannot become a passing strategy',async()=>{
 const f=syntheticEquityFixture();
 f.dailyBars=f.dailyBars.slice(-25);
 const out=await run(f);
 assert.equal(out.reason,'INVALID_EQUITY_RESEARCH_SCOPE');
 assert.equal(out.realOrdersSent,0);
});
test('stock unit price above small hypothetical cash-per-position vetoes watch',async()=>{
 const f=syntheticEquityFixture();
 f.dailyBars=f.dailyBars.map(b=>({
   ...b,open:b.open*15,high:b.high*15,low:b.low*15,close:b.close*15
 }));
 const out=await run(f);
 const agent=out.agentMessages.find(x=>x.name==='LIQUIDITY_AND_CASH_AGENT');
 assert.equal(agent.vote,'VETO_CASH_OR_LIQUIDITY');
 assert.equal(out.researchWatch,false);
 assert.equal(out.finalDecision,'NO_TRADE');
});
test('low turnover history vetoes watch (not evidence of executable order-book depth)',async()=>{
 const f=syntheticEquityFixture();
 f.dailyBars=f.dailyBars.map(b=>({...b,volume:1}));
 const out=await run(f);
 const agent=out.agentMessages.find(x=>x.name==='LIQUIDITY_AND_CASH_AGENT');
 assert.equal(agent.vote,'VETO_CASH_OR_LIQUIDITY');
 assert.equal(agent.evidence.orderBookExecutableLiquidityObserved,false);
 assert.equal(out.finalDecision,'NO_TRADE');
});
test('unusually large closing-bar jump causes volatility veto',async()=>{
 const f=syntheticEquityFixture();
 const last=f.dailyBars.at(-1);
 last.close*=1.4;last.high=last.close*1.002;
 const out=await run(f);
 const agent=out.agentMessages.find(x=>x.name==='DOWNSIDE_AND_GAP_CHALLENGER');
 assert.equal(agent.vote,'VETO_VOLATILITY_AND_GAP');
 assert.equal(out.researchWatch,false);
});
test('mutated agent message or final guardian vote invalidates audit verification',async()=>{
 const out=await run();
 const a=structuredClone(out);
 a.agentMessages[4].vote='BUY';
 assert.equal(verifyEquitySwingAgentAudit(a),false);
 const b=structuredClone(out);
 b.agentMessages.at(-1).vote='APPROVE';
 assert.equal(verifyEquitySwingAgentAudit(b),false);
 const c=structuredClone(out);
 c.auditChainHash='1234';
 assert.equal(verifyEquitySwingAgentAudit(c),false);
});
test('code has no exchange, crypto, Upstox production order hostname, tokens or client',()=>{
 const src=fs.readFileSync(fileURLToPath(
   new URL('./nse_swing_interdependent_agent_network.mjs',import.meta.url)),'utf8');
 assert.equal(src.includes('https://api-hft.upstox.com'),false);
 assert.equal(src.includes('https://api-sandbox.upstox.com'),false);
 assert.equal(src.includes('UPSTOX_ACCESS_TOKEN'),false);
 assert.equal(src.includes('OPENROUTER_API_KEY'),false);
 assert.equal(src.includes('https://api.binance'),false);
});
