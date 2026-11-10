import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeHistoricalRuns} from './historical_day_robustness.mjs';

const DAYS=['01','02','03','04','05','08','09','10','11','12','15','16'];
function scenario(daily){
  const ledger=daily.map((net,i)=> net===null
    ? {day:DAYS[i],trade:false,skipped:0}
    : {day:DAYS[i],trade:true,net,gross:net+1,fees:1,qty:1});
  const trades=ledger.filter(x=>x.trade),net=ledger.reduce((s,d)=>s+(d.trade?d.net:0),0);
  return {count:trades.length,netPnl:net,finalEquity:10000+net,
    costs:trades.length,ledger};
}
function run(slip,override={}){
  return {slipBpsPerSide:slip,output:['ACC','RELIANCE'].map(symbol=>({
    symbol,validSessions:12,sourceDays:12,excluded:[],
    inputFiles:DAYS.map(day=>({day,sha256:'a'.repeat(64)})),
    scenarios:{
      BASELINE:scenario(Array.from({length:12},(_,i)=>(i===0?12:
        (i===1?-9:null))-(slip-5)*.01)),
      DTT_VETO:scenario(Array.from({length:12},(_,i)=>(i===0?8:
        (i===1?-15:null))-(slip-5)*.01)),
    }
  }))};
}
test('diagnostic accepts two independent complete 12-day stock accounts',()=>{
  const out=analyzeHistoricalRuns(run(5),run(15));
  assert.deepEqual(Object.keys(out.analyzedSymbols),['ACC','RELIANCE']);
  assert.equal(out.futurePredictiveEvidence,false);
  assert.equal(out.brokerExecutedTrades,0);
  assert.equal(out.untouchedHoldout,false);
});
test('12 DATE clusters retained including zero-trade days',()=>{
  const out=analyzeHistoricalRuns(run(5),run(15));
  const a=out.analyzedSymbols.ACC.scenarios['5'].BASELINE;
  assert.equal(a.dayCount,12);
  assert.equal(a.trades,2);
  assert.equal(a.daysWithPositiveNet,1);
  assert.equal(a.netPnlInr,3);
});
test('leave-one-day-out checks result fragility',()=>{
  const a=analyzeHistoricalRuns(run(5),run(15)).analyzedSymbols.ACC.scenarios['5'].BASELINE;
  assert.deepEqual(a.leaveOneDayOutRangeInr,[-9,12]);
  assert.equal(a.leaveOneDayOutNegativeCount,1);
});
test('bootstrap output deterministic at same fixed seed',()=>{
  const a=analyzeHistoricalRuns(run(5),run(15));
  const b=analyzeHistoricalRuns(run(5),run(15));
  assert.deepEqual(a,b);
  assert.equal(a.analyzedSymbols.ACC.scenarios['5'].BASELINE.bootstrap.repetitions,10000);
  assert.equal(a.analyzedSymbols.ACC.scenarios['5'].BASELINE.bootstrap.notAProbabilityOfFutureProfit,true);
});
test('paired DTT minus baseline compares calendar days, not individual trade matches',()=>{
  const a=analyzeHistoricalRuns(run(5),run(15)).analyzedSymbols.RELIANCE;
  assert.equal(a.policyComparison['5'].netDifferenceInr,-10);
  assert.match(a.policyComparison['5'].matchingNote,/NOT matched trades/);
});
test('higher friction deterioration detected but no trading conclusion made',()=>{
  const a=analyzeHistoricalRuns(run(5),run(15)).analyzedSymbols.ACC;
  assert.ok(a.frictionSensitivity.BASELINE.higherFrictionDragInr>0);
  assert.equal(a.futurePredictiveEvidence,undefined);
});
test('incomplete session summary is rejected',()=>{
  const a=run(5);a.output[0].validSessions=11;
  assert.throws(()=>analyzeHistoricalRuns(a,run(15)),/UNEXPECTED_SYMBOL_OR_INCOMPLETE_SESSIONS/);
});
test('missing or reordered source day is rejected',()=>{
  const a=run(5);a.output[0].inputFiles[0].day='02';
  assert.throws(()=>analyzeHistoricalRuns(a,run(15)),/SOURCE_FILE_ORDER_OR_FINGERPRINT_MISSING/);
});
test('missing source SHA256 is rejected',()=>{
  const a=run(5);a.output[0].inputFiles[0].sha256='';
  assert.throws(()=>analyzeHistoricalRuns(a,run(15)),/SOURCE_FILE_ORDER_OR_FINGERPRINT_MISSING/);
});
test('double counting or altered net total is rejected',()=>{
  const a=run(5);a.output[0].scenarios.BASELINE.netPnl+=100;
  assert.throws(()=>analyzeHistoricalRuns(a,run(15)),/SUMMARY_PNL_MISMATCH/);
});
test('gross less fee must equal net, even in synthetic journal',()=>{
  const a=run(5);a.output[0].scenarios.BASELINE.ledger[0].gross+=2;
  assert.throws(()=>analyzeHistoricalRuns(a,run(15)),/TRADE_PNL_INCONSISTENT/);
});
test('source output report contains no full quote or token',()=>{
  const o=JSON.stringify(analyzeHistoricalRuns(run(5),run(15)));
  assert.doesNotMatch(o,/(API_KEY|Authorization:|last_price|token|rawCandles)/i);
});
test('reject a wrong slippage label to prevent false evidence',()=>{
  const a=run(5);a.slipBpsPerSide=9;
  assert.throws(()=>analyzeHistoricalRuns(a,run(15)),/INVALID_HISTORICAL_JSON_OR_SLIPPAGE/);
});
test('no-trade days contribute zero profit and do not imply a filled order',()=>{
  const a=run(5);a.output[0].scenarios.BASELINE.ledger[2].net=1000;
  const outcome=analyzeHistoricalRuns(a,run(15));
  assert.equal(outcome.analyzedSymbols.ACC.scenarios['5'].BASELINE.netPnlInr,3);
});
