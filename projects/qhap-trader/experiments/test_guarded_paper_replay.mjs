import test from "node:test";
import assert from "node:assert/strict";
import {charges2026Scenario,replayDay,replayBook} from "./guarded_paper_replay.mjs";

/* These tests use synthetic candles only, and cannot validate live fills. */
function fixture({day="01",breakout=false,missing=null,dualTouch=false,
                  gapDown=false,lateExit=false,entryNoVolume=false,
                  earlyStop=false}={}){
  const rows=["TEST,202102"+day+",09:08,100,100,100,100,1000,0"];
  for(let m=570;m<=895;m++){
    const tm=String(Math.floor(m/60)).padStart(2,"0")+":"+String(m%60).padStart(2,"0");
    if(tm===missing)continue;
    let o=100,h=100.4,l=99.6,c=100,v=1000;
    if((breakout||lateExit)&&tm==="09:40"&&breakout) {
      o=100;h=102;l=99.9;c=101;
    }
    if(breakout&&tm>"09:40"){
      o=101;h=101.4;l=100.8;c=101;
    }
    if(breakout&&tm==="09:41"&&dualTouch){
      o=101;h=110;l=90;c=101;
    }
    if(breakout&&tm==="09:42"&&earlyStop){
      o=101;h=101.1;l=99.5;c=100.1;
    }
    if(breakout&&tm==="09:42"&&gapDown){
      o=90;h=91;l=85;c=89;
    }
    if(breakout&&tm==="09:41"&&entryNoVolume)v=0;
    if(lateExit){
      if(tm==="14:30"){o=100;h=102;l=99.6;c=101;}
      if(tm>="14:31"&&tm<"14:55"){o=101;h=101.3;l=100.8;c=101;}
      if(tm==="14:55"){o=101;h=110;l=90;c=100;}
    }
    rows.push(["TEST","202102"+day,tm,o,h,l,c,v,0].join(","));
  }
  return {day,content:rows.join("\n")};
}
function once(opts={},slip=5){
  const s=fixture(opts);
  return replayDay({symbol:"TEST",day:s.day,source:s.content,slippageBps:slip});
}

test("no breakout: complete data certifies a NO_TRADE only",()=>{
  const r=once();
  assert.equal(r.status,"NO_TRADE");
  assert.equal(r.netPnl,0);
});
test("simulated entry occurs only after a completed breakout bar",()=>{
  const r=once({breakout:true});
  assert.equal(r.status,"CLOSED");
  assert.equal(r.signalAt,"09:40");
  assert.equal(r.entry,"09:41");
  assert.equal(r.exit,"14:55");
  assert.equal(r.exitReason,"TIME");
});
test("missing pre-entry minute causes HALTED_DATA, not a certified no-trade",()=>{
  const r=once({breakout:true,missing:"09:39"});
  assert.equal(r.status,"HALTED_DATA");
  assert.equal(r.netPnl,null);
  assert.equal(r.position,null);
});
test("missing next-entry minute is ENTRY_UNCONFIRMED (not invented fill)",()=>{
  const r=once({breakout:true,missing:"09:41"});
  assert.equal(r.status,"ENTRY_UNCONFIRMED");
  assert.equal(r.netPnl,null);
});
test("missing minute AFTER an open paper position preserves entry and marks unresolved",()=>{
  const r=once({breakout:true,missing:"09:45"});
  assert.equal(r.status,"UNRESOLVED_POSITION");
  assert.equal(r.at,"09:45");
  assert.equal(r.position.entry,"09:41");
  assert.equal(r.netPnl,null);
});
test("missing scheduled 14:55 open leaves position unresolved, not forcibly closed",()=>{
  const r=once({breakout:true,missing:"14:55"});
  assert.equal(r.status,"UNRESOLVED_POSITION");
  assert.equal(r.netPnl,null);
});
test("unresolved entry propagates to locked book, no invented final valuation",()=>{
  const src=fixture({breakout:true,missing:"09:45"});
  const book=replayBook({symbol:"TEST",sourceFiles:[src,fixture({day:"02",breakout:true})]});
  assert.equal(book.certified,false);
  assert.equal(book.unresolvedPositions,1);
  assert.equal(book.finalEquity,null);
  assert.equal(book.ledger[1].status,"LOCKED");
});
test("when stop and target both touched in one bar, STOP wins",()=>{
  const r=once({breakout:true,dualTouch:true});
  assert.equal(r.exitReason,"STOP");
});
test("adverse gap below stop uses gap opening price, not intended stop",()=>{
  const r=once({breakout:true,gapDown:true});
  assert.equal(r.exitReason,"STOP");
  assert.ok(r.sell<95);
  assert.ok(r.netPnl<-100);
});
test("post-trade source omission does not erase a previously closed paper trade",()=>{
  const r=once({breakout:true,earlyStop:true,missing:"14:00"});
  assert.equal(r.status,"CLOSED");
  assert.equal(r.exit,"09:42");
});
test("time exit at 14:55 opening ignores later bar extremes",()=>{
  const r=once({lateExit:true});
  assert.equal(r.status,"CLOSED");
  assert.equal(r.signalAt,"14:30");
  assert.equal(r.exitReason,"TIME");
  assert.equal(r.exit,"14:55");
});
test("no volume on scheduled entry minute cannot certify an executable entry",()=>{
  const r=once({breakout:true,entryNoVolume:true});
  assert.equal(r.status,"ENTRY_UNCONFIRMED");
});
test("more slippage reduces return on the same stop path",()=>{
  const low=once({breakout:true,dualTouch:true},5);
  const high=once({breakout:true,dualTouch:true},15);
  assert.ok(high.netPnl<low.netPnl);
});
test("position remains small and fees are actually subtracted",()=>{
  const r=once({breakout:true,earlyStop:true});
  assert.ok(r.qty>0 && r.qty*r.buy<=2000.000001);
  assert.ok(r.fees>0 && r.netPnl<r.gross);
});
test("fee calculation matches 2026 reference rate and nearest-rupee STT",()=>{
  const fee=charges2026Scenario(100,105,500);
  assert.equal(fee.stt,13);
  assert.ok(Math.abs(fee.brokerage-30.75)<1e-10);
  assert.ok(Math.abs(fee.exchange-(50000+52500)*0.0000307)<1e-10);
  assert.ok(Math.abs(fee.stamp-1.5)<1e-10);
  assert.ok(Math.abs(fee.gst-0.18*(fee.brokerage+fee.exchange+fee.sebi))<1e-10);
  assert.ok(Math.abs(fee.total-(fee.brokerage+fee.exchange+fee.sebi+fee.gst+fee.stamp+fee.stt))<1e-10);
});
test("brokerage is capped at ₹20 on each side and STT rounds half-up",()=>{
  const fee=charges2026Scenario(100,100,1000);
  assert.equal(fee.brokerage,40);
  assert.equal(fee.stt,25);
  assert.equal(charges2026Scenario(100,100,20).stt,1);
});
test("large simulated daily loss locks subsequent paper session",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01",breakout:true,gapDown:true}),
    fixture({day:"02",breakout:true})]});
  assert.equal(book.ledger[0].status,"CLOSED");
  assert.equal(book.ledger[1].status,"LOCKED");
  assert.equal(book.lockedReason,"DAILY_LOSS_BREACH");
  assert.equal(book.certified,false);
});
test("bad settings and duplicate research days fail validation",()=>{
  const src=fixture();
  assert.throws(()=>replayBook({symbol:"TEST",sourceFiles:[src,src]}));
  assert.throws(()=>replayDay({symbol:"TEST",day:src.day,source:src.content,
    slippageBps:-5}));
});
