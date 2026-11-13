import test from 'node:test';
import assert from 'node:assert/strict';
import {parseCompleteSession,simulateSession,summarizeSessions,indicativeFees} from './intraday_clock_replay.mjs';
const tstr=t=>String(t/60|0).padStart(2,'0')+':'+String(t%60).padStart(2,'0');
function fixture({missing=-1,duplicated=-1,badAt=-1,moveAt=-1,dropAt=-1,targetAndStopAt=-1,gapAt=-1}={}){
 const rows=[];for(let t=555;t<=929;t++){
  if(t===missing)continue;
  let o=100,h=100.05,l=99.95,c=100,v=100;
  if(t===moveAt){o=101.0;h=102.5;l=100;c=102;}
  if(t>moveAt&&moveAt>=0){o=101.7;h=102.5;l=101.6;c=102;}
  if(t===dropAt){o=101;h=101.5;l=99;c=99.5;}
  if(t===targetAndStopAt){o=102;h=110;l=90;c=102;}
  if(t===gapAt){o=90;h=93;l=89;c=91;}
  if(t===badAt)h=90;
  const row=['TEST','20230203',tstr(t),o,h,l,c,v,0].join(',');rows.push(row);if(t===duplicated)rows.push(row);
 }
 return rows.join('\n');
}
const s=(opts)=>parseCompleteSession(fixture(opts),'TEST','20230203');
test('requires every historical minute (no forward filling)',()=>{assert.throws(()=>s({missing:761}),/MISSING_MINUTES/);});
test('requires the 09:15 source opening even when research features start 09:16',()=>{
 assert.throws(()=>s({missing:555}),/MISSING_OPENING_MINUTE_09_15/);
});
test('validates and de-duplicates the 09:15 opening candle',()=>{
 assert.throws(()=>s({badAt:555}),/BAD_OHLCV/);
 assert.throws(()=>s({duplicated:555}),/DUPLICATE_MINUTE/);
});
test('rejects duplicate minute bars',()=>{assert.throws(()=>s({duplicated:801}),/DUPLICATE/);});
test('rejects impossible OHLC bar',()=>{assert.throws(()=>s({badAt:700}),/BAD_OHLCV/);});
test('rejects cross-source symbol/date changes',()=>{assert.throws(()=>parseCompleteSession(fixture(),'BAD','20230203'),/SOURCE_SCHEMA/);});
test('rejects malformed times',()=>{assert.throws(()=>parseCompleteSession(fixture().replace('09:16','09:99'),'TEST','20230203'),/BAD_TIME/);});
test('parses complete 374-minute session and cumulative VWAP',()=>{const a=s();assert.equal(a.bars.length,374);assert.equal(a.bars[0].t,556);assert.equal(a.bars.at(-1).t,929);assert.equal(a.bars[0].vwap,100);});
test('no trade is exactly zero and never exposes source prices',()=>{const r=simulateSession(s(),'NO_TRADE');assert.equal(r.netRupees,0);assert.equal(r.roundTrips,0);assert.equal(r.terminalFlat,true);});
test('flat market yields zero crossover trades',()=>{for(const p of ['FAST','ONE','TIME_MOMENTUM_GATE'])assert.equal(simulateSession(s(),p).roundTrips,0);});
test('modeled roundtrip costs rise with notional',()=>{assert.ok(indicativeFees(100,101,20)>indicativeFees(100,101,1));});
test('rejects invalid slippage and unsupported policy',()=>{assert.throws(()=>simulateSession(s(),'BAD'),/UNSUPPORTED/);assert.throws(()=>simulateSession(s(),'FAST',{slippageBpsPerSide:-5}),/INVALID_SLIPPAGE/);});
test('positive momentum can create virtual entry but bounded exit by 14:55',()=>{const a=s({moveAt:650});const r=simulateSession(a,'ONE');assert.equal(r.roundTrips,1);assert.equal(r.terminalFlat,true);});
test('scheduled 14:55 exit ignores later 14:55 extremes',()=>{
 const a=s({moveAt:650,targetAndStopAt:895});const r=simulateSession(a,'ONE');
 assert.equal(r.roundTrips,1);assert.equal(r.exitsByReason.TIME_1455_OPEN,1);
 assert.equal(r.exitsByReason.STOP_FIRST_OR_GAP,undefined);
});
test('stop takes precedence when both stop and target are inside a minute',()=>{
 const a=s({moveAt:650,targetAndStopAt:652});const r=simulateSession(a,'ONE');assert.equal(r.roundTrips,1);assert.ok(r.exitsByReason.STOP_FIRST_OR_GAP>=1);
});
test('an adverse gap uses the worse opening exit price',()=>{
 const a=s({moveAt:650,gapAt:652});const r=simulateSession(a,'ONE');assert.equal(r.roundTrips,1);assert.ok(r.netRupees<0);
});
test('one-roundtrip and gate policy cannot exceed one completed trade',()=>{
 const a=s({moveAt:650});for(const p of ['ONE','TIME_MOMENTUM_GATE'])assert.ok(simulateSession(a,p).roundTrips<=1);
});
test('slippage changes fill and stop paths; do not assume monotonic losses',()=>{
 const a=s({moveAt:650,gapAt:652});const low=simulateSession(a,'ONE',{slippageBpsPerSide:5});const high=simulateSession(a,'ONE',{slippageBpsPerSide:30});
 assert.equal(low.roundTrips,1);assert.equal(high.roundTrips,1);
 for(const v of [low,high])assert.ok(Math.abs(v.grossPriceMovementRupees-v.slippageDragRupees-v.feesRupees-v.netRupees)<0.05);
});
test('no-trade comparator remains separate from funded paper accounts',()=>{
 const r=summarizeSessions([s({moveAt:650}),s({moveAt:651})]);assert.equal(r.inputs,2);assert.equal(r.resultsByPolicy.NO_TRADE.netRupees,0);assert.equal(r.brokerRoutes,0);assert.equal(r.realTrades,0);
});
test('returns only sanitized aggregates; never stores or prints source candles',()=>{
 const str=JSON.stringify(summarizeSessions([s({moveAt:650})]));assert.equal(str.includes('"bars"'),false);assert.equal(str.includes('"o"'),false);assert.equal(str.includes('"token"'),false);
});