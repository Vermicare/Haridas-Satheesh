/**
 * QHAP-TRADER v2: offline, fail-closed, chronology-first single-equity paper replay.
 *
 * A missing candle AFTER simulated entry is not a clean "no trade" or a
 * simulated exit: this engine records UNRESOLVED_POSITION, sets net P&L null,
 * and locks further testing. This is a research model, NOT a live broker router.
 *
 * The original historical replay is preserved separately for audit parity.
 */

const minuteText = n => String(Math.floor(n/60)).padStart(2,"0")+":"+String(n%60).padStart(2,"0");
const money = x => Math.round(x*1e6)/1e6;

export function charges2026Scenario(buy,sell,qty) {
  if (![buy,sell,qty].every(Number.isFinite)||buy<=0||sell<=0||
      !Number.isInteger(qty)||qty<=0) throw Error("Bad fee inputs");
  const b=buy*qty, s=sell*qty, turnover=b+s;
  const brokerage=Math.min(20,b*0.0003)+Math.min(20,s*0.0003);
  const exchange=turnover*0.0000307, sebi=turnover*0.000001;
  const gst=(brokerage+exchange+sebi)*0.18;
  const stamp=b*0.00003;
  const stt=Math.floor(s*0.00025+0.5);
  return {brokerage,exchange,sebi,gst,stamp,stt,
    total:brokerage+exchange+sebi+gst+stamp+stt};
}

export function parse2021Source(symbol,day,source) {
  if(!/^[A-Z]+$/.test(symbol)||!/^[0-3][0-9]$/.test(day)||
    typeof source!=="string")throw Error("Bad source parameters");
  const date="202102"+day, map=new Map();
  for(const line of source.trim().split(/\r?\n/)) {
    if(!line.trim())continue;
    const p=line.split(",");
    if(p.length!==9||p[0]!==symbol||p[1]!==date||
      !/^\d\d:\d\d$/.test(p[2]))throw Error("Source symbol/date/schema mismatch");
    const tm=p[2],v=p.slice(3,8).map(Number);
    if(tm<"09:30"||tm>"14:55")continue;
    const [o,h,l,c,volume]=v;
    const valid=v.every(Number.isFinite)&&o>0&&l>0&&h>=Math.max(o,c)&&
      l<=Math.min(o,c)&&volume>=0;
    const bar=valid?{tm,o,h,l,c,volume}:null;
    // Preserve duplicate/bad candle at its real time instead of excluding
    // whole session with future knowledge.
    if(map.has(tm))map.set(tm,null);
    else map.set(tm,bar);
  }
  return map;
}

export function replayDay({symbol,day,source,initialEquity=10000,
                           slippageBps=5,variant="BASELINE"}) {
  if(!["BASELINE","DTT_VETO"].includes(variant)||!Number.isFinite(initialEquity)||
     initialEquity<0||!Number.isFinite(slippageBps)||
     slippageBps<0||slippageBps>200)throw Error("Bad replay settings");
  const bars=parse2021Source(symbol,day,source);
  const opening=[],history=[];
  let cumPriceVolume=0,cumVolume=0,priorClose=null,position=null,
    pending=null,skipped=0;

  const halt=(status,tm)=>({
    symbol,day,status,at:tm,
    position:position?{signalAt:position.signalAt,entry:position.entry,
      qty:position.qty,buy:money(position.buy)}:null,
    skippedSignals:skipped,netPnl:null,
    reason:status==="UNRESOLVED_POSITION"
      ?"Market data missing/invalid after simulated entry; cannot certify exit"
      :status==="ENTRY_UNCONFIRMED"
      ?"Data unavailable when simulated next-bar entry would occur; no fill assumed"
      :"Cannot trust price data; no new trades"
  });
  const finish=(bar,reason,raw)=>{
    const sell=raw*(1-slippageBps/10000);
    const fee=charges2026Scenario(position.buy,sell,position.qty);
    const gross=(sell-position.buy)*position.qty,net=gross-fee.total;
    return {symbol,day,status:"CLOSED",signalAt:position.signalAt,
      entry:position.entry,exit:bar.tm,exitReason:reason,
      qty:position.qty,buy:money(position.buy),sell:money(sell),
      gross:money(gross),fees:money(fee.total),netPnl:money(net),
      dtt:money(position.dtt),skippedSignals:skipped};
  };

  for(let n=570;n<=895;n++){
    const tm=minuteText(n),b=bars.get(tm);
    if(!b) {
      if(position)return halt("UNRESOLVED_POSITION",tm);
      if(pending)return halt("ENTRY_UNCONFIRMED",tm);
      return halt("HALTED_DATA",tm);
    }

    // Pending intention is allowed to execute only at the NEXT bar open.
    if(pending){
      if(b.volume<=0)return halt("ENTRY_UNCONFIRMED",tm);
      const buy=b.o*(1+slippageBps/10000);
      const riskPerShare=buy*(0.01+2*slippageBps/10000+0.002);
      const qty=Math.max(0,Math.min(
        Math.floor(2000/buy),
        Math.floor((initialEquity-4000)/(buy*1.001)),
        Math.floor(50/riskPerShare)
      ));
      if(qty===0){pending=null;skipped++;}
      else{
        position={signalAt:pending.signalAt,entry:tm,buy,qty,
          dtt:pending.dtt,stop:buy*0.99,target:buy*1.015};
        pending=null;
      }
    }

    // 14:55 scheduled open exit must not inspect this bar's later high/low.
    if(position&&tm==="14:55")return finish(b,"TIME",b.o);
    if(position){
      if(b.l<=position.stop){
        return finish(b,"STOP",Math.min(b.o,position.stop));
      }
      if(b.h>=position.target){
        return finish(b,"TARGET",position.target);
      }
    }

    // Next decisions use the COMPLETED bar; 09:30–09:39 defines only a
    // deliberately late *proxy* range (source omits some 09:15 opens).
    cumVolume+=b.volume;
    cumPriceVolume+=b.c*b.volume;
    if(n<=579)opening.push(b);
    else if(!position && !pending && n<=870 && b.volume>0 &&
            priorClose!==null) {
      const high=Math.max(...opening.map(x=>x.h));
      const low=Math.min(...opening.map(x=>x.l));
      if(b.c>high&&priorClose<=high) {
        const past=history.slice(-10);
        const vwap=cumVolume>0?cumPriceVolume/cumVolume:b.c;
        const ups=[high,Math.max(...past.map(x=>x.h)),vwap,Math.ceil(b.c/10)*10];
        const downs=[low,Math.min(...past.map(x=>x.l)),vwap,Math.floor(b.c/10)*10];
        let flips=0;
        for(const shock of [-20,-10,10,20]){
          const perturbed=b.c*(1+shock/10000);
          for(const t of ups)if((b.c>=t)!==(perturbed>=t))flips++;
          for(const t of downs)if((b.c<=t)!==(perturbed<=t))flips++;
        }
        const dtt=flips/32;
        if(variant==="DTT_VETO"&&dtt>=0.10)skipped++;
        else pending={signalAt:tm,dtt};
      }
    }
    priorClose=b.c;
    history.push(b);
  }
  if(position)return halt("UNRESOLVED_POSITION","END_OF_FEED");
  if(pending)return halt("ENTRY_UNCONFIRMED","END_OF_FEED");
  return {symbol,day,status:"NO_TRADE",skippedSignals:skipped,netPnl:0};
}

export function replayBook({symbol,sourceFiles,initialEquity=10000,
                            slippageBps=5,variant="BASELINE"}) {
  if(!Array.isArray(sourceFiles)||!sourceFiles.length)throw Error("No source files");
  const sorted=[...sourceFiles].sort((a,b)=>a.day.localeCompare(b.day));
  const unique=new Set(sorted.map(x=>x.day));
  if(unique.size!==sorted.length)throw Error("Duplicate research day");
  let equity=initialEquity,peak=equity,drawdown=0,week=null,
    weeklyPnL=0,locked=null;
  const ledger=[];
  for(const s of sorted){
    const date=new Date("2021-02-"+s.day+"T00:00:00Z");
    if(Number.isNaN(date.valueOf()))throw Error("Invalid research day");
    const monday=new Date(date.valueOf()-((date.getUTCDay()+6)%7)*86400000)
      .toISOString().slice(0,10);
    if(monday!==week){week=monday;weeklyPnL=0;}
    if(locked){
      ledger.push({symbol,day:s.day,status:"LOCKED",reason:locked,netPnl:null});
      continue;
    }
    if(weeklyPnL<=-300){
      ledger.push({symbol,day:s.day,status:"WEEKLY_LOCK",netPnl:0});
      continue;
    }
    const x=replayDay({symbol,day:s.day,source:s.content,
      initialEquity:equity,slippageBps,variant});
    ledger.push(x);
    if(["HALTED_DATA","ENTRY_UNCONFIRMED","UNRESOLVED_POSITION"].includes(x.status)){
      locked=x.status;
      continue;
    }
    if(x.status==="CLOSED"){
      equity+=x.netPnl;
      weeklyPnL+=x.netPnl;
      peak=Math.max(peak,equity);
      drawdown=Math.max(drawdown,peak-equity);
      if(x.netPnl<=-100)locked="DAILY_LOSS_BREACH";
      else if(drawdown>=800)locked="MAX_DRAWDOWN_BREACH";
    }
  }
  const unknown=ledger.some(x=>x.status==="UNRESOLVED_POSITION");
  const certified=ledger.every(x=>["CLOSED","NO_TRADE"].includes(x.status));
  return {symbol,variant,slippageBps,initialEquity,
    knownRealizedPnl:money(equity-initialEquity),
    // Explicitly DO NOT invent a final account valuation when an open paper
    // position's exit is unknown. Other locks also fail certification.
    finalEquity:unknown?null:money(equity),
    maxKnownDrawdown:money(drawdown),certified,
    lockedReason:locked,unresolvedPositions:ledger.filter(x=>x.status==="UNRESOLVED_POSITION").length,
    closedTrades:ledger.filter(x=>x.status==="CLOSED").length,ledger};
}
