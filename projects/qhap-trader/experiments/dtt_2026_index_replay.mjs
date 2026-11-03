#!/usr/bin/env node
/**
 * QHAP-TRADER DTT INDEX DIAGNOSTIC — RESEARCH ONLY.
 * Run: node dtt_2026_index_replay.mjs AUG.csv SEP.csv OCT.csv
 * No network, no broker APIs, no paper fills or trading instructions.
 * NIFTY 50 is an index, NOT a directly purchasable cash equity.
 * Label is future 5-minute SUM OF ABSOLUTE 1-minute moves, not profit.
 *
 * This is exploratory and NOT independently preregistered or certified.
 */
import fs from "node:fs";
import crypto from "node:crypto";

const paths=process.argv.slice(2);
if(paths.length!==3)throw Error("Pass August, September and October 2026 CSV paths in order");
const months=["08","09","10"], byDay=new Map(), files=[];
for(let k=0;k<3;k++){
  const raw=fs.readFileSync(paths[k],"utf8"), lines=raw.trim().split(/\r?\n/);
  if(lines[0].trim()!=="Epoch,Timestamp,Open,High,Low,Close,Volume")
    throw Error("Unexpected source CSV schema");
  for(let i=1;i<lines.length;i++){
    const a=lines[i].split(",");
    if(a.length!==7)throw Error("Invalid row "+i);
    const x={m:months[k],d:a[1].slice(0,10),tm:a[1].slice(11,16),
      e:+a[0],o:+a[2],h:+a[3],l:+a[4],c:+a[5],v:+a[6]};
    if(![x.e,x.o,x.h,x.l,x.c,x.v].every(Number.isFinite)||
       !x.d.startsWith("2026-"+months[k])||
       !(x.l<=x.o&&x.l<=x.c&&x.h>=x.o&&x.h>=x.c&&x.v>=0))
      throw Error("Invalid date or OHLCV in "+x.d);
    if(!byDay.has(x.d))byDay.set(x.d,[]);
    byDay.get(x.d).push(x);
  }
  files.push({month:months[k],rows:lines.length-1,
    sha256:crypto.createHash("sha256").update(raw).digest("hex")});
}
const rec=[], exclusions=[], gaps=[];
for(const [day,b] of byDay){
  b.sort((x,y)=>x.e-y.e);
  const opening=b.filter(x=>x.tm>="09:15"&&x.tm<"09:25");
  if(opening.length!==10||opening.some((x,j)=>x.tm!=="09:"+(15+j))){
    exclusions.push({day,reason:"Incomplete 09:15 to 09:24 opening"});continue;
  }
  const high=Math.max(...opening.map(x=>x.h)), low=Math.min(...opening.map(x=>x.l));
  let cv=0,pv=0;const vwap=[];
  for(const x of b){
    pv+=((x.h+x.l+x.c)/3)*x.v;cv+=x.v;
    if(cv<=0)throw Error("Zero cumulative volume in "+day);
    vwap.push(pv/cv);
  }
  for(let i=20;i<b.length-6;i++){
    const x=b[i];
    if(x.tm<"09:35"||x.tm>"14:40"||Number(x.tm.slice(3,5))%5!==0)continue;
    if(b.slice(i-20,i+6).some((z,j,arr)=>j>0&&z.e-arr[j-1].e!==60)){
      gaps.push({day,time:x.tm});continue;
    }
    const prev=b.slice(i-10,i);
    const up=[high,Math.max(...prev.map(z=>z.h)),vwap[i],Math.ceil(x.c/50)*50];
    const down=[low,Math.min(...prev.map(z=>z.l)),vwap[i],Math.floor(x.c/50)*50];
    let flips=0;
    for(const shock of [-20,-10,10,20]){
      const p=x.c*(1+shock/10000);
      for(const t of up)if((x.c>=t)!==(p>=t))flips++;
      for(const t of down)if((x.c<=t)!==(p<=t))flips++;
    }
    let trailing=0,future=0;
    for(let j=i-4;j<=i;j++)trailing+=Math.abs(b[j].c/b[j-1].c-1)*10000;
    for(let j=i+1;j<=i+5;j++)future+=Math.abs(b[j].c/b[j-1].c-1)*10000;
    rec.push({d:day,m:x.m,dtt:flips/32,
      base:trailing+0.5*(x.h-x.l)/x.c*10000,future});
  }
}
const tr=rec.filter(x=>x.m!=="10"),hold=rec.filter(x=>x.m==="10");
if(tr.length<500||hold.length<100)throw Error("Insufficient data");
const avg=a=>a.reduce((s,x)=>s+x,0)/a.length;
const quant=(a,q)=>{const s=[...a].sort((x,y)=>x-y),p=(s.length-1)*q,j=Math.floor(p);
  return s[j]+(s[Math.min(j+1,s.length-1)]-s[j])*(p-j);};
const sd=a=>{const mu=avg(a);return Math.sqrt(avg(a.map(x=>(x-mu)**2)));};
const cut=quant(tr.map(x=>x.future),.75),
  mb=avg(tr.map(x=>x.base)),md=avg(tr.map(x=>x.dtt)),
  sb=sd(tr.map(x=>x.base)),sD=sd(tr.map(x=>x.dtt));
if(sb===0||sD===0)throw Error("Zero score variance");
const test=hold.map(x=>({...x,y:Number(x.future>=cut),
  combo:(x.base-mb)/sb+0.5*(x.dtt-md)/sD}));
function auc(rows,key){
  const a=[...rows].sort((x,y)=>x[key]-y[key]),pos=a.filter(x=>x.y).length,neg=a.length-pos;
  if(!pos||!neg)return null;
  let rank=1,sum=0;
  for(let i=0;i<a.length;){
    let j=i+1;while(j<a.length&&a[j][key]===a[i][key])j++;
    for(let k=i;k<j;k++)if(a[k].y)sum+=(rank+rank+j-i-1)/2;
    rank+=j-i;i=j;
  }
  return (sum-pos*(pos+1)/2)/(pos*neg);
}
const roc={baseline:auc(test,"base"),dtt:auc(test,"dtt"),combined:auc(test,"combo")};
const top={};
for(const key of ["base","dtt","combo"]){
  const sel=[...test].sort((x,y)=>y[key]-x[key]).slice(0,Math.ceil(.1*test.length));
  top[key]={n:sel.length,largeMoveRate:avg(sel.map(x=>x.y))};
}
const groups=new Map();
for(const x of test){if(!groups.has(x.d))groups.set(x.d,[]);groups.get(x.d).push(x);}
const days=[...groups.keys()];
let seed=20261103;
function rng(){seed=(1664525*seed+1013904223)>>>0;return seed/2**32;}
const diffs=[];
for(let j=0;j<500;j++){
  const subset=[];
  for(let k=0;k<days.length;k++)subset.push(...groups.get(days[Math.floor(rng()*days.length)]));
  const a=auc(subset,"base"),b=auc(subset,"combo");
  if(a!==null&&b!==null)diffs.push(b-a);
}
console.log(JSON.stringify({
  evidence:"Exploratory, index-only prediction, not profit or investor psychology",
  dataSource:"technovusin/nifty50-historical-data (unverified third-party)",
  files,marketSessions:byDay.size,excludedDays:exclusions,
  missingMinuteWindows:gaps.length,
  train:{period:"Aug-Sep 2026",days:new Set(tr.map(x=>x.d)).size,
    observations:tr.length,largeMoveThresholdSumAbsBps:cut},
  test:{period:"Oct 2026",days:days.length,observations:test.length,
    largeMoveRate:avg(test.map(x=>x.y)),rocAuc:roc,
    combinedMinusBaseline:roc.combined-roc.baseline,
    bootstrap500DayBlockCI95:[quant(diffs,.025),quant(diffs,.975)],
    topDecile:top}
},null,2));
