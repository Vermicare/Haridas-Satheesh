#!/usr/bin/env node
/** Offline exploratory cash-equity paper replay. Not an investment result. See research report. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const DAYS = ["01","02","03","04","05","08","09","10","11","12","15","16"];
const runPilot = function runPilot(symbol, sourceFiles, slipBps=5) {
  const T0=10000, positionLimit=2000, reserve=4000;
  const fees=(buy,sell,qty)=>{
    const buyValue=buy*qty,sellValue=sell*qty;
    const brokerBuy=Math.min(20,buyValue*0.0003),brokerSell=Math.min(20,sellValue*0.0003);
    const exch=(buyValue+sellValue)*0.0000307;
    const sebi=(buyValue+sellValue)*0.000001;
    const gst=0.18*(brokerBuy+brokerSell+exch+sebi);
    const stamp=buyValue*0.00003;
    const stt=Math.floor(sellValue*0.00025+0.5);
    return {total:brokerBuy+brokerSell+exch+sebi+gst+stamp+stt,stt,brokerage:brokerBuy+brokerSell};
  };
  const hhmm=(min)=>`${String(Math.floor(min/60)).padStart(2,"0")}:${String(min%60).padStart(2,"0")}`;
  const round=x=>Math.round(x*1e6)/1e6;
  const sessions=[],issues=[];
  for(const f of sourceFiles){
    const lines=f.content.trim().split(/\r?\n/), m=new Map();
    for(const line of lines){
      const v=line.split(",");
      if(v.length!==9||v[0]!==symbol||!v[1].endsWith(f.day))throw Error("Bad symbol/row in "+f.day);
      const [o,h,l,c,vol]=v.slice(3,8).map(Number),tm=v[2];
      if(![o,h,l,c,vol].every(Number.isFinite)||!(o>0&&l>0&&h>=Math.max(o,c)&&l<=Math.min(o,c)&&vol>=0))throw Error("Malformed bar "+f.day+" "+tm);
      if(tm>="09:30"&&tm<="15:00") {
        if(m.has(tm))throw Error("Duplicate bar "+f.day+" "+tm);
        m.set(tm,{tm,o,h,l,c,vol});
      }
    }
    const required=[];
    for(let n=9*60+30;n<=15*60;n++)required.push(hhmm(n));
    const missing=required.filter(k=>!m.has(k));
    if(missing.length){issues.push({day:f.day,missing:missing.slice(0,10),count:missing.length});continue;}
    sessions.push({day:f.day,map:m,sha:f.sha,records:lines.length});
  }
  function strategy(s,gate,initialCash){
    const a=s.map, bars=[...a.values()].sort((x,y)=>x.tm.localeCompare(y.tm)),open=bars.slice(0,10);
    const openingHigh=Math.max(...open.map(x=>x.h)),openingLow=Math.min(...open.map(x=>x.l));
    let pv=0,volume=0, signal=null,skipped=0;
    const VW=new Map();
    for(const b of bars){pv+=b.c*b.vol;volume+=b.vol;VW.set(b.tm,pv/volume);}
    let entry=null,order=null;
    let prev=bars[9];
    for(let i=10;i<bars.length-1;i++){
      const b=bars[i],tm=b.tm;
      if(tm>"14:30")break;
      const crossover=b.c>openingHigh&&prev.c<=openingHigh;
      prev=b;
      if(!crossover)continue;
      const prior=bars.slice(Math.max(0,i-10),i);
      const ups=[openingHigh,Math.max(...prior.map(x=>x.h)),VW.get(tm),Math.ceil(b.c/10)*10];
      const downs=[openingLow,Math.min(...prior.map(x=>x.l)),VW.get(tm),Math.floor(b.c/10)*10];
      let switches=0;
      for(const shock of [-20,-10,10,20]){
        const p=b.c*(1+shock/10000);
        for(const t of ups)if((b.c>=t)!==(p>=t))switches++;
        for(const t of downs)if((b.c<=t)!==(p<=t))switches++;
      }
      const dtt=switches/32;
      if(gate==="DTT_VETO" && dtt>=0.10){skipped++;continue;}
      const next=bars[i+1];
      if(next.tm>"14:31")break;
      const buy=next.o*(1+slipBps/10000);
      const qty=Math.min(Math.floor(positionLimit/buy),Math.floor((initialCash-reserve)/(buy*1.001)),Math.floor(50/(buy*0.013)));
      if(qty<1){skipped++;continue;}
      entry={tm:next.tm,buy,qty,stop:buy*0.99,target:buy*1.015,signalAt:tm,dtt};
      order=bars.findIndex(x=>x.tm===next.tm);
      break;
    }
    if(!entry)return {day:s.day,trade:false,skipped};
    let exit=null;
    for(let i=order;i<bars.length;i++){
      const b=bars[i]; if(b.tm>"14:55")break;
      if(b.l<=entry.stop){exit={tm:b.tm,reason:"STOP",raw:Math.min(entry.stop,b.o)};break;}
      if(b.h>=entry.target){exit={tm:b.tm,reason:"TARGET",raw:entry.target};break;}
      if(b.tm==="14:55"){exit={tm:b.tm,reason:"TIME",raw:b.o};break;}
    }
    if(!exit)throw Error("Incomplete exit window "+s.day);
    const sell=exit.raw*(1-slipBps/10000);
    const charges=fees(entry.buy,sell,entry.qty);
    const gross=(sell-entry.buy)*entry.qty,net=gross-charges.total;
    return {day:s.day,trade:true,signal:entry.signalAt,entry:entry.tm,exit:exit.tm,exitReason:exit.reason,qty:entry.qty,dtt:round(entry.dtt),gross:round(gross),fees:round(charges.total),net:round(net),stt:charges.stt};
  }
  const scenarios={};
  for(const gate of ["BASELINE","DTT_VETO"]){
    let equity=T0,peak=T0,halted=false,weeklyLoss=0,currentWeek="";
    const ledger=[];
    for(const s of sessions){
      const d=new Date(`2021-02-${s.day}T00:00:00Z`);
      const week=Math.floor((Number(s.day)-1)/7); // conservative fixed 7-day blocks, not exchange calendar weeks
      const wk=`2021-02-${week}`;
      if(wk!==currentWeek){currentWeek=wk;weeklyLoss=0;}
      if(halted||weeklyLoss<=-300){ledger.push({day:s.day,trade:false,skipped:"portfolio_risk_lock"});continue;}
      const rec=strategy(s,gate,equity);
      ledger.push(rec);
      if(rec.trade){equity+=rec.net;weeklyLoss+=rec.net;peak=Math.max(peak,equity);}
      if(peak-equity>=800)halted=true;
    }
    const traded=ledger.filter(x=>x.trade),gain=traded.filter(x=>x.net>0),totalNet=equity-T0;
    scenarios[gate]={count:traded.length,wins:gain.length,losses:traded.length-gain.length,winRate:traded.length?gain.length/traded.length:null,netPnl:round(totalNet),grossPnl:round(traded.reduce((sum,x)=>sum+x.gross,0)),costs:round(traded.reduce((sum,x)=>sum+x.fees,0)),finalEquity:round(equity),maxDrawdown:round((()=>{let c=T0,p=T0,dd=0;for(const x of ledger){if(x.trade)c+=x.net;p=Math.max(p,c);dd=Math.max(dd,p-c);}return dd;})()),skippedSignals:ledger.reduce((n,x)=>n+(typeof x.skipped==="number"?x.skipped:0),0),ledger};
  }
  return {symbol,sourceDays:sourceFiles.length,validSessions:sessions.length,excluded:issues,slippageBpsPerSide:slipBps,
    tradingRules:"09:30-09:39 proxy range; 1 long breakout/day; next-bar open; 1% stop; 1.5% target; exit 14:55; worst-case same-minute stop; initial capital 10k each ticker independently",
    feeAssumptions:"Zerodha reference 2026 schedule 0.03% capped 20/order; intraday STT 0.025% sell INR-rounded; NSE 0.00307%; SEBI 0.0001%; stamp 0.003% buy; GST 18% qualifying levies",
    scenarios};
};
const root=process.argv[2];
if (!root) throw Error('Usage: node costed_intraday_pilot.mjs /path/to/nse-intraday-data [slippage_bps_per_side]');
const slip=process.argv[3]?Number(process.argv[3]):5;
if(!Number.isFinite(slip)||slip<0)throw Error('Bad slippage setting');
const output=[];
for(const symbol of ['ACC','RELIANCE']){
 const files=DAYS.map(day=>{
   const p=path.join(root,'2021','FEB',day+'FEB',day+'FEB',symbol+'.txt');
   const content=fs.readFileSync(p,'utf8');
   return {day,content,sha256:crypto.createHash('sha256').update(content).digest('hex')};
 });
 output.push({inputFiles:files.map(f=>({day:f.day,sha256:f.sha256})),...runPilot(symbol,files,slip)});
}
console.log(JSON.stringify({classification:'EXPLORATORY THIRD-PARTY DATA; SIMULATION ONLY; NOT PROFIT EVIDENCE',slipBpsPerSide:slip,output},null,2));
