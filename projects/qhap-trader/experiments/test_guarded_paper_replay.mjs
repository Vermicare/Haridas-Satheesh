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

test("uncertain entry must not certify an ending portfolio balance",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({breakout:true,missing:"09:41"}),
    fixture({day:"02",breakout:true})]});
  assert.equal(book.ledger[0].status,"ENTRY_UNCONFIRMED");
  assert.equal(book.finalEquity,null);
  assert.equal(book.certified,false);
  assert.equal(book.ledger[1].status,"LOCKED");
});


/** Adversarial order-failure scenarios are TEST-ONLY; not actual broker fills. */
test("synthetic entry rejection halts with no invented filled position",()=>{
  const src=fixture({breakout:true});
  const r=replayDay({symbol:"TEST",day:src.day,source:src.content,
    executionFault:{kind:"REJECTED",at:"09:41"}});
  assert.equal(r.status,"ENTRY_REJECTED");
  assert.equal(r.position,null);
  assert.equal(r.netPnl,null);
  assert.equal(r.detail.requestedQty>0,true);
});
test("synthetic stale entry quote blocks a fake next-minute fill",()=>{
  const src=fixture({breakout:true});
  const r=replayDay({symbol:"TEST",day:src.day,source:src.content,
    executionFault:{kind:"STALE_QUOTE",at:"09:41"}});
  assert.equal(r.status,"STALE_QUOTE");
  assert.equal(r.position,null);
  assert.equal(r.netPnl,null);
});
test("synthetic partial fill preserves known exposure and unknown exit",()=>{
  const src=fixture({breakout:true});
  const r=replayDay({symbol:"TEST",day:src.day,source:src.content,
    executionFault:{kind:"PARTIAL_FILL",at:"09:41",filledQty:2}});
  assert.equal(r.status,"UNRESOLVED_POSITION");
  assert.equal(r.position.entry,"09:41");
  assert.equal(r.position.qty,2);
  assert.ok(r.position.requestedQty>2);
  assert.equal(r.detail.filledQty,2);
  assert.equal(r.netPnl,null);
});
test("partial-fill uncertainty locks subsequent sessions and withholds equity",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01",breakout:true}),
    fixture({day:"02",breakout:true})],
    executionFaultsByDay:{"01":{kind:"PARTIAL_FILL",at:"09:41",filledQty:2}}});
  assert.equal(book.ledger[0].status,"UNRESOLVED_POSITION");
  assert.equal(book.ledger[1].status,"LOCKED");
  assert.equal(book.finalEquity,null);
  assert.equal(book.certified,false);
});
test("a rejected entry never becomes an invented PnL in the book",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01",breakout:true}),
    fixture({day:"02",breakout:true})],
    executionFaultsByDay:{"01":{kind:"REJECTED",at:"09:41"}}});
  assert.equal(book.ledger[0].status,"ENTRY_REJECTED");
  assert.equal(book.ledger[1].status,"LOCKED");
  assert.equal(book.finalEquity,null);
  assert.equal(book.certified,false);
});
test("invalid synthetic fill quantities and unsupported fault types fail",()=>{
  const src=fixture({breakout:true});
  const go=(fault)=>replayDay({symbol:"TEST",day:src.day,source:src.content,
    executionFault:fault});
  assert.throws(()=>go({kind:"PARTIAL_FILL",at:"09:41",filledQty:0}));
  assert.throws(()=>go({kind:"PARTIAL_FILL",at:"09:41",filledQty:100000}));
  assert.throws(()=>go({kind:"FAKE_SUCCESS",at:"09:41"}));
  assert.throws(()=>go({kind:"STALE_QUOTE",at:"09:41",filledQty:1}));
});

test("synthetic rejected stop exit retains position and unknown net PnL",()=>{
  const s=fixture({breakout:true,earlyStop:true});
  const r=replayDay({symbol:"TEST",day:s.day,source:s.content,
    exitFault:{kind:"REJECTED",at:"09:42"}});
  assert.equal(r.status,"UNRESOLVED_POSITION");
  assert.equal(r.position.qty>0,true);
  assert.equal(r.detail.fault,"EXIT_REJECTED");
  assert.equal(r.netPnl,null);
});
test("synthetic partial stop exit records remaining exposure without invented profit",()=>{
  const s=fixture({breakout:true,earlyStop:true});
  const r=replayDay({symbol:"TEST",day:s.day,source:s.content,
    exitFault:{kind:"PARTIAL_FILL",at:"09:42",filledQty:2}});
  assert.equal(r.status,"UNRESOLVED_POSITION");
  assert.equal(r.detail.filledExitQty,2);
  assert.equal(r.position.qty,r.detail.remainingQty);
  assert.equal(r.netPnl,null);
});
test("synthetic stale scheduled exit leaves paper exposure unresolved",()=>{
  const s=fixture({breakout:true});
  const r=replayDay({symbol:"TEST",day:s.day,source:s.content,
    exitFault:{kind:"STALE_QUOTE",at:"14:55"}});
  assert.equal(r.status,"UNRESOLVED_POSITION");
  assert.equal(r.detail.fault,"EXIT_STALE_QUOTE");
  assert.equal(r.netPnl,null);
});
test("uncertain synthetic exit locks later days and hides ending equity",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01",breakout:true,earlyStop:true}),
    fixture({day:"02",breakout:true})],
    exitFaultsByDay:{"01":{kind:"REJECTED",at:"09:42"}}});
  assert.equal(book.ledger[0].status,"UNRESOLVED_POSITION");
  assert.equal(book.ledger[1].status,"LOCKED");
  assert.equal(book.finalEquity,null);
  assert.equal(book.certified,false);
});
test("invalid synthetic exit quantities and timestamps are rejected",()=>{
  const s=fixture({breakout:true,earlyStop:true});
  const go=(exitFault)=>replayDay({symbol:"TEST",day:s.day,source:s.content,exitFault});
  assert.throws(()=>go({kind:"PARTIAL_FILL",at:"09:42",filledQty:0}));
  assert.throws(()=>go({kind:"PARTIAL_FILL",at:"09:42",filledQty:1000}));
  assert.throws(()=>go({kind:"REJECTED",at:"09:42",filledQty:1}));
  assert.throws(()=>go({kind:"REJECTED",at:"garbage"}));
});

test("source-data halt with no known position locks book and withholds final equity",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01",missing:"09:39"}),
    fixture({day:"02"})]});
  assert.equal(book.ledger[0].status,"HALTED_DATA");
  assert.equal(book.ledger[0].position,null);
  assert.equal(book.ledger[1].status,"LOCKED");
  assert.equal(book.lockedReason,"HALTED_DATA");
  assert.equal(book.knownRealizedPnl,0);
  assert.equal(book.finalEquity,null);
  assert.equal(book.certified,false);
});
test("complete synthetic no-trade book retains certified starting equity",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01"}),fixture({day:"02"})]});
  assert.equal(book.finalEquity,10000);
  assert.equal(book.certified,true);
  assert.equal(book.lockedReason,null);
});

// Calendar-integrity regression: reject impossible February 2021 dates.
test("nonexistent February 2021 dates are rejected before replay",()=>{
  for(const day of ["00","29","30","31","3","aa"]){
    const src=fixture({day});
    assert.throws(()=>replayDay({symbol:"TEST",day,source:src.content}));
    assert.throws(()=>replayBook({symbol:"TEST",sourceFiles:[src]}));
  }
});
test("unverified Saturday and Sunday research sessions fail closed",()=>{
  for(const day of ["06","07","27","28"]){
    const src=fixture({day});
    assert.throws(()=>replayDay({symbol:"TEST",day,source:src.content}),
      /Unverified weekend exchange session/);
    assert.throws(()=>replayBook({symbol:"TEST",sourceFiles:[src]}),
      /Unverified weekend exchange session/);
  }
});
test("weekday-only validation does not falsely certify exchange holidays",()=>{
  // 2021-02-01 is a Monday; valid weekday is NOT proof of an NSE session.
  const src=fixture({day:"01"});
  const r=replayBook({symbol:"TEST",sourceFiles:[src]});
  assert.equal(r.ledger[0].status,"NO_TRADE");
  assert.equal(r.certified,true); // Technical replay certification only.
});

// Source-backed exceptional session: NSE's 24 Feb 2021 outage cannot be
// replayed by a continuous 09:30–14:55 minute-bar engine.
// SEBI PR 9/2021 (25 Feb 2021), not a trading holiday:
// https://www.sebi.gov.in/media/press-releases/feb-2021/trading-halt-at-nse-on-february-24-2021_49287.html
test("NSE February 24 2021 intraday halt is quarantined rather than certified",()=>{
  const exceptional=fixture({day:"24",breakout:true});
  assert.throws(()=>replayDay({symbol:"TEST",day:"24",source:exceptional.content}),
    /exceptional intraday halt/);
  assert.throws(()=>replayBook({symbol:"TEST",sourceFiles:[exceptional]}),
    /exceptional intraday halt/);
  const ordinary=fixture({day:"23"});
  assert.equal(replayDay({symbol:"TEST",day:"23",source:ordinary.content}).status,"NO_TRADE");
});


test("portfolio rejects invalid capital before any replay",()=>{
  const src=fixture({day:"01"});
  for(const initialEquity of [0,-1,NaN,Infinity,-Infinity,"10000",null]){
    assert.throws(()=>replayBook({symbol:"TEST",sourceFiles:[src],initialEquity}),
      /Invalid portfolio initial equity/);
  }
});
test("daily loss lock never publishes uncertified final equity",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01",breakout:true,gapDown:true}),
    fixture({day:"02",breakout:true})]});
  assert.equal(book.ledger[0].status,"CLOSED");
  assert.equal(book.ledger[1].status,"LOCKED");
  assert.equal(book.lockedReason,"DAILY_LOSS_BREACH");
  assert.equal(book.certified,false);
  assert.equal(book.finalEquity,null);
  assert.ok(Number.isFinite(book.knownRealizedPnl));
});

// Five consecutive February 2021 weekdays, four known sub-₹100 losses.
// Synthetic-only weekly lock; no exchange provenance or real fills implied.
test("weekly loss lock withholds uncertified portfolio equity",()=>{
  const losingDay=day=>{
    const src=fixture({day,breakout:true});
    const rows=src.content.split("\n").map(row=>{
      const p=row.split(",");
      if(p[2]==="09:42"){
        p[3]="97";p[4]="97.1";p[5]="96.9";p[6]="97";
      }
      return p.join(",");
    });
    return {day,content:rows.join("\n")};
  };
  const book=replayBook({symbol:"TEST",sourceFiles:
    ["01","02","03","04","05"].map(losingDay)});
  assert.deepEqual(book.ledger.slice(0,4).map(x=>x.status),
    ["CLOSED","CLOSED","CLOSED","CLOSED"]);
  assert.ok(book.ledger.slice(0,4).every(x=>x.netPnl<0&&x.netPnl>-100));
  assert.equal(book.ledger[4].status,"WEEKLY_LOCK");
  assert.equal(book.certified,false);
  assert.equal(book.finalEquity,null);
  assert.ok(book.knownRealizedPnl<=-300);
});

// Drawdown is accumulated across weekly resets; weekly veto must not reset peak.
// Synthetic prices only; no assumption about exchange-authorized historical bars.
test("cross-week maximum drawdown locks later sessions and hides final equity",()=>{
  const losingDay=day=>{
    const src=fixture({day,breakout:true});
    const rows=src.content.split("\n").map(row=>{
      const p=row.split(",");
      if(p[2]==="09:42"){
        p[3]="97";p[4]="97.1";p[5]="96.9";p[6]="97";
      }
      return p.join(",");
    });
    return {day,content:rows.join("\n")};
  };
  // Four sub-₹100 losses in each of the first two weeks; weekly counters
  // reset but the portfolio drawdown does not. Third week crosses ₹800.
  const days=["01","02","03","04","08","09","10","11","15","16","17","18"];
  const book=replayBook({symbol:"TEST",sourceFiles:days.map(losingDay)});
  assert.deepEqual(book.ledger.slice(0,11).map(x=>x.status),
    Array(11).fill("CLOSED"));
  assert.equal(book.ledger[11].status,"LOCKED");
  assert.equal(book.ledger[11].reason,"MAX_DRAWDOWN_BREACH");
  assert.equal(book.lockedReason,"MAX_DRAWDOWN_BREACH");
  assert.ok(book.maxKnownDrawdown>=800);
  assert.equal(book.closedTrades,11);
  assert.equal(book.certified,false);
  assert.equal(book.finalEquity,null);
  assert.ok(Number.isFinite(book.knownRealizedPnl));
});

test("post-exit missing candle preserves known trade but prevents session certification",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01",breakout:true,earlyStop:true,missing:"14:00"}),
    fixture({day:"02"})]});
  assert.equal(book.ledger[0].status,"CLOSED");
  assert.equal(book.ledger[0].exit,"09:42");
  assert.equal(book.ledger[0].sessionComplete,false);
  assert.equal(book.ledger[0].firstPostExitGap,"14:00");
  assert.ok(Number.isFinite(book.ledger[0].netPnl));
  assert.equal(book.ledger[1].status,"LOCKED");
  assert.equal(book.lockedReason,"POST_EXIT_DATA_GAP");
  assert.equal(book.certified,false);
  assert.equal(book.finalEquity,null);
  assert.ok(Number.isFinite(book.knownRealizedPnl));
});
test("complete post-exit session remains eligible for technical certification",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[fixture({day:"01",breakout:true,earlyStop:true})]});
  assert.equal(book.ledger[0].status,"CLOSED");
  assert.equal(book.ledger[0].sessionComplete,true);
  assert.equal(book.ledger[0].firstPostExitGap,null);
  assert.equal(book.certified,true);
  assert.ok(Number.isFinite(book.finalEquity));
});

// A known adverse gap and missing post-exit candle can coexist. Data-quality
// provenance must not be replaced by a concurrent emergency-loss veto.
test("post-exit data gap remains primary lock despite simultaneous daily loss",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01",breakout:true,gapDown:true,missing:"14:00"}),
    fixture({day:"02"})]});
  assert.equal(book.ledger[0].status,"CLOSED");
  assert.ok(book.ledger[0].netPnl<=-100);
  assert.equal(book.ledger[0].sessionComplete,false);
  assert.equal(book.ledger[0].firstPostExitGap,"14:00");
  assert.equal(book.lockedReason,"POST_EXIT_DATA_GAP");
  assert.equal(book.ledger[1].status,"LOCKED");
  assert.equal(book.ledger[1].reason,"POST_EXIT_DATA_GAP");
  assert.equal(book.certified,false);
  assert.equal(book.finalEquity,null);
  assert.ok(Number.isFinite(book.knownRealizedPnl));
});


// A drawdown breach can coincide with a missing post-exit candle. The
// cumulative peak survives weekly resets; data provenance must still win.
test("post-exit data gap remains primary lock despite concurrent maximum drawdown",()=>{
  const losingDay=(day,missing=null)=>{
    const src=fixture({day,breakout:true,missing});
    const rows=src.content.split("\n").map(row=>{
      const p=row.split(",");
      if(p[2]==="09:42"){
        p[3]="97";p[4]="97.1";p[5]="96.9";p[6]="97";
      }
      return p.join(",");
    });
    return {day,content:rows.join("\n")};
  };
  const prior=["01","02","03","04","08","09","10","11","15","16"];
  const book=replayBook({symbol:"TEST",sourceFiles:[
    ...prior.map(day=>losingDay(day)),
    losingDay("17","14:00"),losingDay("18")
  ]});
  assert.ok(book.ledger.slice(0,10).every(x=>x.status==="CLOSED"));
  assert.equal(book.ledger[10].status,"CLOSED");
  assert.equal(book.ledger[10].sessionComplete,false);
  assert.equal(book.ledger[10].firstPostExitGap,"14:00");
  assert.ok(book.ledger[10].netPnl<0&&book.ledger[10].netPnl>-100);
  assert.ok(book.maxKnownDrawdown>=800);
  assert.equal(book.lockedReason,"POST_EXIT_DATA_GAP");
  assert.equal(book.ledger[11].status,"LOCKED");
  assert.equal(book.ledger[11].reason,"POST_EXIT_DATA_GAP");
  assert.equal(book.closedTrades,11);
  assert.equal(book.certified,false);
  assert.equal(book.finalEquity,null);
  assert.ok(Number.isFinite(book.knownRealizedPnl));
});


test("terminal-day daily loss lock withholds portfolio certification",()=>{
  const book=replayBook({symbol:"TEST",sourceFiles:[
    fixture({day:"01",breakout:true,gapDown:true})]});
  assert.equal(book.ledger.length,1);
  assert.equal(book.ledger[0].status,"CLOSED");
  assert.ok(book.ledger[0].netPnl<=-100);
  assert.equal(book.ledger[0].sessionComplete,true);
  assert.equal(book.lockedReason,"DAILY_LOSS_BREACH");
  assert.equal(book.certified,false);
  assert.equal(book.finalEquity,null);
  assert.ok(Number.isFinite(book.knownRealizedPnl));
});

test("terminal-day cross-week maximum drawdown lock withholds certification",()=>{
  const losingDay=day=>{
    const src=fixture({day,breakout:true});
    const rows=src.content.split("\n").map(row=>{
      const p=row.split(",");
      if(p[2]==="09:42"){
        p[3]="97";p[4]="97.1";p[5]="96.9";p[6]="97";
      }
      return p.join(",");
    });
    return {day,content:rows.join("\n")};
  };
  const days=["01","02","03","04","08","09","10","11","15","16","17"];
  const book=replayBook({symbol:"TEST",sourceFiles:days.map(losingDay)});
  assert.equal(book.ledger.length,days.length);
  assert.ok(book.ledger.every(x=>x.status==="CLOSED"&&x.sessionComplete===true));
  assert.ok(book.maxKnownDrawdown>=800);
  assert.equal(book.lockedReason,"MAX_DRAWDOWN_BREACH");
  assert.equal(book.certified,false);
  assert.equal(book.finalEquity,null);
  assert.ok(Number.isFinite(book.knownRealizedPnl));
});
