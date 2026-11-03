import test from 'node:test';
import assert from 'node:assert/strict';
import {runPilot} from './costed_intraday_pilot.mjs';

/* All tests are synthetic; none establishes market or profit validity. */
function source({symbol='TEST',day='01',breakout=false,remove=null,bothTouched=false,lateExit=false}={}) {
  const data=[symbol+',202102'+day+',09:08,100,100,100,100,100,0'];
  for (let minute=570;minute<=900;minute++){
    const tm=String(Math.floor(minute/60)).padStart(2,'0')+':'+String(minute%60).padStart(2,'0');
    if(tm===remove)continue;
    let o=100,h=100.4,l=99.6,c=100;
    if(breakout&&tm==='09:40'){o=100;h=102;l=99.8;c=101;}
    if(breakout&&tm==='09:41'){o=101;h=bothTouched?110:101.5;l=bothTouched?90:100.9;c=101;}
    if(breakout&&tm==='09:42'){o=101;h=101.1;l=99.5;c=100;}
    // At the scheduled 14:55 exit, intraminute extremes must be ignored:
    // only the opening price exists when the exit decision is due.
    if(lateExit&&tm==='14:30'){o=100;h=102;l=99.6;c=101;}
    if(lateExit&&tm>='14:31'&&tm<'14:55'){o=101;h=101.5;l=100.9;c=101;}
    if(lateExit&&tm==='14:55'){o=101;h=110;l=90;c=100;}
    data.push([symbol,'202102'+day,tm,o,h,l,c,500,0].join(','));
  }
  return {day,content:data.join('\n'),sha:'SYNTHETIC'};
}
const testResult=(opts={},slip=5)=>runPilot('TEST',[source(opts)],slip).scenarios.BASELINE;

test('steady market produces no paper order',()=>{
  const r=testResult();assert.equal(r.count,0);assert.equal(r.netPnl,0);
});
test('completed signal never fills in the same minute',()=>{
  const r=testResult({breakout:true});assert.equal(r.count,1);
  assert.ok(r.ledger[0].entry>r.ledger[0].signal);
});
test('ambiguous stop and target in the same candle uses STOP',()=>{
  const r=testResult({breakout:true,bothTouched:true});
  assert.equal(r.ledger[0].exitReason,'STOP');
});
test('a missing minute rejects the entire market session',()=>{
  const r=runPilot('TEST',[source({breakout:true,remove:'09:55'})],5);
  assert.equal(r.validSessions,0);assert.equal(r.excluded.length,1);
  assert.equal(r.scenarios.BASELINE.count,0);
});
test('worse slippage worsens this same-stopped-path result',()=>{
  const low=testResult({breakout:true,bothTouched:true},5);
  const high=testResult({breakout:true,bothTouched:true},15);
  assert.ok(high.netPnl<low.netPnl);
});
test('position and fee controls are applied to paper orders',()=>{
  const r=testResult({breakout:true});
  assert.ok(r.ledger[0].qty>0 && r.ledger[0].qty<=20);
  assert.ok(r.costs>0);assert.ok(r.netPnl<r.grossPnl);
});
test('no-trade and full loss report remain internally consistent',()=>{
  const r=testResult({breakout:true});
  assert.ok(Math.abs(r.finalEquity-(10000+r.netPnl))<1e-3);
  assert.ok(r.maxDrawdown>=0);
});

test('14:55 opening exit cannot be selected from later 14:55 high/low',()=>{
  const r=testResult({lateExit:true});
  assert.equal(r.count,1);
  assert.equal(r.ledger[0].entry,'14:31');
  assert.equal(r.ledger[0].exit,'14:55');
  assert.equal(r.ledger[0].exitReason,'TIME');
  assert.ok(r.netPnl<0);  // round-trip fees and slippage, not an instant win
});
