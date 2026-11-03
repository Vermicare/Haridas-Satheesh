#!/usr/bin/env node
/**
 * QHAP-TRADER individual-equity historical diagnostic (RESEARCH ONLY).
 *
 * Run with Node.js 20+:
 *   node equity_dtt_feb2021_pilot.mjs /path/to/nse-intraday-data
 *
 * Input layout: root/2021/FEB/01FEB/01FEB/RELIANCE.txt, etc.
 * This script never fetches data, trades, contacts brokers or changes accounts.
 * It is NOT an intraday trading P&L backtest, a psychology measurement, or
 * evidence of profitability. Third-party source data is NOT exchange-audited.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const DAYS=["01","02","03","04","05","08","09","10","11","12","15","16"];
const SYMBOLS=["ACC","RELIANCE"];
const ROOT=process.argv[2];
if(!ROOT)throw new Error("Required: local root of gsidhu/nse-intraday-data");

const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const percentile=(a,p)=>{
  if(!a.length)throw new Error("Empty percentile");
  const sorted=[...a].sort((x,y)=>x-y),v=(sorted.length-1)*p,i=Math.floor(v);
  return sorted[i]+(sorted[Math.min(i+1,sorted.length-1)]-sorted[i])*(v-i);
};
const std=a=>{const m=mean(a);return Math.sqrt(mean(a.map(x=>(x-m)**2)));};
const formatTime=minutes=>String(Math.floor(minutes/60)).padStart(2,"0")+":"+String(minutes%60).padStart(2,"0");

function rocAuc(rows,key){
  const sorted=[...rows].sort((a,b)=>a[key]-b[key]);
  const pos=sorted.filter(x=>x.label).length,neg=sorted.length-pos;
  if(!pos||!neg)return null;
  let rank=1,sum=0;
  for(let i=0;i<sorted.length;){
    let j=i+1;
    while(j<sorted.length&&sorted[j][key]===sorted[i][key])j++;
    for(let k=i;k<j;k++)if(sorted[k].label)sum+=(rank+rank+j-i-1)/2;
    rank+=j-i;i=j;
  }
  return (sum-pos*(pos+1)/2)/(pos*neg);
}

function loadSession(root,day,symbol){
  const file=path.join(root,"2021","FEB",day+"FEB",day+"FEB",symbol+".txt");
  const raw=fs.readFileSync(file,"utf8");
  const result=[];
  const seen=new Set();
  for(const line of raw.trim().split(/\r?\n/)){
    const z=line.split(",");
    if(z.length!==9||z[0]!==symbol||z[1]!=="202102"+day)
      throw new Error("Invalid row schema or symbol/date in "+file);
    const t=z[2],v=z.slice(3,8).map(Number);
    if(!/^\d\d:\d\d$/.test(t)||v.some(n=>!Number.isFinite(n)))
      throw new Error("Bad timestamp or number in "+file);
    const [o,h,l,c,volume]=v;
    if(!(o>0&&l>0&&l<=o&&l<=c&&h>=o&&h>=c&&volume>=0))
      throw new Error("Invalid OHLCV in "+file+" "+t);
    if(t>="09:15"&&t<"15:30"){
      if(seen.has(t))throw new Error("Duplicate bar time in "+file);
      seen.add(t);
      result.push({tm:t,open:o,high:h,low:l,close:c,volume});
    }
  }
  result.sort((a,b)=>a.tm.localeCompare(b.tm));
  return {bars:result,sourceFile:file,sha256:crypto.createHash("sha256").update(raw).digest("hex"),
    firstMinute:result[0]?.tm,lastMinute:result.at(-1)?.tm};
}

function featuresOfSession(bars,day){
  const map=new Map(bars.map(b=>[b.tm,b]));
  const opening=bars.filter(b=>b.tm>="09:30"&&b.tm<"09:40");
  if(opening.length!==10||opening.some((b,i)=>b.tm!=="09:"+(30+i)))
    throw new Error("Missing 09:30–09:39 opening for "+day);
  const rangeHigh=Math.max(...opening.map(x=>x.high));
  const rangeLow=Math.min(...opening.map(x=>x.low));
  const vwap=new Map();
  let cumVolume=0,cumPriceVolume=0;
  for(const b of bars){
    cumVolume+=b.volume;
    cumPriceVolume+=b.close*b.volume;
    if(cumVolume<=0)throw new Error("Zero total traded volume at "+b.tm);
    // CLOSE-weighted VWAP PROXY, not true transaction VWAP.
    vwap.set(b.tm,cumPriceVolume/cumVolume);
  }
  const observations=[];
  for(let m=9*60+55;m<=14*60+35;m+=5){
    const window=[];
    for(let offset=-10;offset<=5;offset++)window.push(map.get(formatTime(m+offset)));
    if(window.some(x=>!x))continue; // conservatively discard missing windows
    const current=window[10],past=window.slice(0,10),p=current.close;
    const ups=[rangeHigh,Math.max(...past.map(x=>x.high)),vwap.get(current.tm),Math.ceil(p/10)*10];
    const downs=[rangeLow,Math.min(...past.map(x=>x.low)),vwap.get(current.tm),Math.floor(p/10)*10];
    let flips=0;
    for(const shock of [-20,-10,10,20]){
      const shocked=p*(1+shock/10000);
      for(const threshold of ups)if((p>=threshold)!==(shocked>=threshold))flips++;
      for(const threshold of downs)if((p<=threshold)!==(shocked<=threshold))flips++;
    }
    let recent=0,future=0;
    for(let i=6;i<=10;i++)recent+=Math.abs(window[i].close/window[i-1].close-1)*10000;
    for(let i=11;i<=15;i++)future+=Math.abs(window[i].close/window[i-1].close-1)*10000;
    observations.push({
      day,tm:current.tm,dtt:flips/32,
      baseline:recent+0.5*(current.high-current.low)/p*10000,
      futureAbsMovementBps:future
    });
  }
  return observations;
}

const output={study:"EXPLORATORY_FEB2021_EQUITY_ABSOLUTE_MOVEMENT",
  warning:"Not trading profit, investor psychology, real order flow or licensed verified exchange data",
  source:"gsidhu/nse-intraday-data; original source rights must be independently checked",
  results:[]};

for(const symbol of SYMBOLS){
  const observations=[],files=[],excluded=[];
  for(const day of DAYS){
    const input=loadSession(ROOT,day,symbol);
    files.push({day,sha256:input.sha256,bars:input.bars.length,
      firstMinute:input.firstMinute,lastMinute:input.lastMinute});
    const x=featuresOfSession(input.bars,day);
    if(!x.length)excluded.push(day);
    observations.push(...x);
  }
  const train=observations.filter(r=>DAYS.indexOf(r.day)<7);
  const holdout=observations.filter(r=>DAYS.indexOf(r.day)>=7);
  if(train.length<100||holdout.length<100)throw new Error("Insufficient "+symbol+" data");
  const eventThreshold=percentile(train.map(x=>x.futureAbsMovementBps),.75);
  const muB=mean(train.map(x=>x.baseline)),sdB=std(train.map(x=>x.baseline));
  const muD=mean(train.map(x=>x.dtt)),sdD=std(train.map(x=>x.dtt));
  const evaluation=holdout.map(x=>({...x,label:Number(x.futureAbsMovementBps>=eventThreshold),
    combined:(x.baseline-muB)/sdB+0.5*(x.dtt-muD)/(sdD||1)}));
  const area={baseline:rocAuc(evaluation,"baseline"),
    dtt:rocAuc(evaluation,"dtt"),combined:rocAuc(evaluation,"combined")};
  output.results.push({symbol,files,excluded,training:{days:DAYS.slice(0,7),n:train.length,
    eventThresholdBps:eventThreshold},holdout:{days:DAYS.slice(7),n:holdout.length,
    largeEventRate:mean(evaluation.map(x=>x.label)),rocAuc:area,
    incrementalCombinedMinusBaseline:area.combined-area.baseline}});
}
console.log(JSON.stringify(output,null,2));
