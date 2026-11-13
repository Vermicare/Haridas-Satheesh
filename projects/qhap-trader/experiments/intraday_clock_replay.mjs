#!/usr/bin/env node
/**
 * Offline, deliberately constrained intraday candle research.
 * No networking, broker/API access, trading orders, credentials or raw-data persistence.
 * All paths, bars, execution prices and charges are indicative, not exchange-validated.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const OPENING_MINUTE=9*60+15, START=9*60+16, END=15*60+29, TIME_EXIT=14*60+55, LAST_ENTRY_SIGNAL=14*60+30;
const STARTING_RUPEES=10000, MAX_POSITION_RUPEES=2500;
const hhmm=m=>`00`; 
const minutes=s=>{if(!/^\d{2}:\d{2}$/.test(s))throw Error('BAD_TIME');const h=Number(s.slice(0,2)),m=Number(s.slice(3));if(h>23||m>59)throw Error('BAD_TIME');return h*60+m;};
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const rup=x=>Math.round(x*100)/100;

export function parseCompleteSession(content,symbol,yyyymmdd){
 if(typeof content!=='string'||!/^[A-Z][A-Z0-9&_-]{0,20}$/.test(symbol)||!/^(202[0-9])[01][0-9][0-3][0-9]$/.test(yyyymmdd))throw Error('INVALID_INPUT');
 const map=new Map();
 for(const line of content.trim().split(/\r?\n/)){
  const p=line.split(',');if(p.length!==9||p[0]!==symbol||p[1]!==yyyymmdd)throw Error('SOURCE_SCHEMA_MISMATCH');
  const t=minutes(p[2]);if(t<OPENING_MINUTE||t>END)continue;
  const a=p.slice(3,8).map(Number),[o,h,l,c,v]=a;
  if(a.some(x=>!finite(x))||o<=0||c<=0||l<=0||h<Math.max(o,c)||l>Math.min(o,c)||v<0)throw Error('BAD_OHLCV');
  if(map.has(t))throw Error('DUPLICATE_MINUTE');
  map.set(t,{t,o,h,l,c,v});
 }
 // A complete source session must include 09:15 even though this *frozen*
 // research signal begins at 09:16. Excluding 09:15 from strategy features
 // must never be confused with declaring a 374-bar source complete.
 if(!map.has(OPENING_MINUTE))throw Error('MISSING_OPENING_MINUTE_09_15');
 const missing=[];for(let t=START;t<=END;t++)if(!map.has(t))missing.push(String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0'));
 if(missing.length)throw Error('MISSING_MINUTES_'+missing.length+'_'+missing[0]);
 const bars=[...map.values()].filter(b=>b.t>=START).sort((a,b)=>a.t-b.t);let cumulativePV=0,cumulativeVolume=0;
 for(const bar of bars){cumulativePV+=bar.c*bar.v;cumulativeVolume+=bar.v;bar.vwap=cumulativeVolume>0?cumulativePV/cumulativeVolume:null;}
 return Object.freeze({symbol,yyyymmdd,bars});
}

export function indicativeFees(buy,sell,qty){
 if(![buy,sell,qty].every(finite)||buy<=0||sell<=0||!Number.isSafeInteger(qty)||qty<=0)throw Error('BAD_FEE_INPUT');
 const a=buy*qty,z=sell*qty,broker=Math.min(20,a*0.0003)+Math.min(20,z*0.0003);
 const exchange=(a+z)*0.0000307,sebi=(a+z)*0.000001;
 const gst=0.18*(broker+exchange+sebi),stamp=a*0.00003,stt=Math.floor(z*0.00025+0.5);
 return broker+exchange+sebi+gst+stamp+stt;
}

const POLICIES=Object.freeze(['FAST','ONE','TIME_MOMENTUM_GATE','NO_TRADE']);
export function simulateSession(session,policy,{slippageBpsPerSide=15}={}){
 if(!POLICIES.includes(policy))throw Error('UNSUPPORTED_POLICY');
 if(!finite(slippageBpsPerSide)||slippageBpsPerSide<0||slippageBpsPerSide>100)throw Error('INVALID_SLIPPAGE');
 if(!session||!Array.isArray(session.bars)||session.bars.length!==END-START+1||session.bars[0]?.t!==START||session.bars.at(-1)?.t!==END||!session.bars.every((b,i)=>b.t===START+i))throw Error('INVALID_COMPLETE_SESSION');
 if(policy==='NO_TRADE')return {policy,session:session.yyyymmdd,symbol:session.symbol,roundTrips:0,positiveTrades:0,netRupees:0,grossPriceMovementRupees:0,feesRupees:0,slippageDragRupees:0,signals:0,filteredSignals:0,terminalFlat:true,exitsByReason:{}};
 const bars=session.bars,prefix=[0];for(const bar of bars)prefix.push(prefix.at(-1)+bar.c);
 const sma=(i,n)=>(prefix[i+1]-prefix[i+1-n])/n;
 const limit=policy==='FAST'?6:1;
 let pos=null,pending=null,closed=0,net=0,gross=0,fees=0,drag=0,wins=0,signals=0,filtered=0;
 const exitsByReason={};
 function exitAt(raw,reason){
  if(!pos)throw Error('EMPTY_EXIT');
  const sell=raw*(1-slippageBpsPerSide/10000),charge=indicativeFees(pos.buy,sell,pos.qty);
  const pnl=(sell-pos.buy)*pos.qty-charge;
  net+=pnl;gross+=(raw-pos.rawEntry)*pos.qty;fees+=charge;
  drag+=((raw-pos.rawEntry)-(sell-pos.buy))*pos.qty;
  closed++;wins+=Number(pnl>0);exitsByReason[reason]=(exitsByReason[reason]||0)+1;pos=null;
 }
 // A signal at the completed candle CLOSE can only schedule action for the next OPEN.
 for(let i=20;i<bars.length;i++){
  const b=bars[i];let exitedThisBar=false;
  if(pending){
   if(pending.action==='EXIT'&&pos){exitAt(b.o,'SMA_CROSS_NEXT_OPEN');exitedThisBar=true;}
   if(pending.action==='BUY'&&!pos&&b.t<TIME_EXIT){
    const buy=b.o*(1+slippageBpsPerSide/10000),qty=Math.min(Math.floor(MAX_POSITION_RUPEES/buy),Math.floor(STARTING_RUPEES/(buy*1.002)));
    if(qty>=1)pos={rawEntry:b.o,buy,qty,stop:buy*0.992,target:buy*1.015};else filtered++;
   }
   pending=null;
  }
  // Scheduled 14:55 exit uses only the opening price.
  if(pos&&b.t===TIME_EXIT){exitAt(b.o,'TIME_1455_OPEN');exitedThisBar=true;}
  else if(pos){
   if(b.l<=pos.stop){exitAt(Math.min(b.o,pos.stop),'STOP_FIRST_OR_GAP');exitedThisBar=true;}
   else if(b.h>=pos.target){exitAt(pos.target,'OPTIMISTIC_TARGET_TOUCH');exitedThisBar=true;}
  }
  if(b.t>=TIME_EXIT)break;
  if(exitedThisBar||pos&&pending)continue;
  const up=sma(i,5)>sma(i,20)&&sma(i-1,5)<=sma(i-1,20);
  const down=sma(i,5)<sma(i,20)&&sma(i-1,5)>=sma(i-1,20);
  if(pos){if(down)pending={action:'EXIT'};continue;}
  if(closed>=limit||b.t>LAST_ENTRY_SIGNAL||!up)continue;
  signals++;
  if(policy==='TIME_MOMENTUM_GATE'){
   const inWindow=(b.t>=600&&b.t<=690)||(b.t>=810&&b.t<=860);
   const tenMinuteReturn=b.c/bars[i-10].c-1;
   if(!inWindow||tenMinuteReturn<0.0035||b.vwap===null||b.c<=b.vwap){filtered++;continue;}
  }
  pending={action:'BUY'};
 }
 if(pos||pending?.action==='EXIT')throw Error('UNRESOLVED_POSITION_OR_EXIT');
 return {policy,session:session.yyyymmdd,symbol:session.symbol,roundTrips:closed,positiveTrades:wins,netRupees:rup(net),grossPriceMovementRupees:rup(gross),feesRupees:rup(fees),slippageDragRupees:rup(drag),signals,filteredSignals:filtered,terminalFlat:true,exitsByReason};
}

export function summarizeSessions(sessions,{slippageBpsPerSide=15}={}){
 const results=[];
 for(const s of sessions)for(const p of POLICIES)results.push(simulateSession(s,p,{slippageBpsPerSide}));
 const byPolicy={};for(const p of POLICIES){const a=results.filter(x=>x.policy===p);byPolicy[p]={stockDays:a.length,roundTrips:a.reduce((z,x)=>z+x.roundTrips,0),positiveTrades:a.reduce((z,x)=>z+x.positiveTrades,0),noTradeStockDays:a.filter(x=>x.roundTrips===0).length,netRupees:rup(a.reduce((z,x)=>z+x.netRupees,0)),modeledFeesRupees:rup(a.reduce((z,x)=>z+x.feesRupees,0)),grossPriceMovementRupees:rup(a.reduce((z,x)=>z+x.grossPriceMovementRupees,0)),slippageDragRupees:rup(a.reduce((z,x)=>z+x.slippageDragRupees,0))};}
 return {classification:'EXPLORATORY_OFFLINE_SIMULATION_NOT_FINANCIAL_PROFIT_EVIDENCE',inputs:sessions.length,distinctDates:new Set(sessions.map(s=>s.yyyymmdd)).size,slippageBpsPerSide,eachStockDayIndependentlyResetsVirtualCapitalRupees:STARTING_RUPEES,resultsByPolicy:byPolicy,sourceRightsVerified:false,exchangeBookPriceExecutable:false,rawCandlesPrinted:false,brokerRoutes:0,realTrades:0};
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [root,manifestPath,slipStr]=process.argv.slice(2);
 if(!root||!manifestPath)throw Error('USAGE: node intraday_clock_replay.mjs /licensed/data/root /path/to/manifest.json [slippage_bps]');
 const manifest=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
 if(!Array.isArray(manifest)||!manifest.length||manifest.length>3000)throw Error('INVALID_MANIFEST');
 const sessions=[],exclusions=[];
 for(const entry of manifest){
  if(!/^(202[0-9])[01][0-9][0-3][0-9]$/.test(entry.date)||!/^[A-Z][A-Z0-9&_-]{0,20}$/.test(entry.symbol))throw Error('INVALID_MANIFEST_ENTRY');
  const rel=path.join(entry.date.slice(0,4),entry.date.slice(4,6),entry.date.slice(6,8),entry.symbol+'.csv');
  const absolute=path.join(root,rel);
  try{sessions.push(parseCompleteSession(fs.readFileSync(absolute,'utf8'),entry.symbol,entry.date));}
  catch(e){if(e.code==='ENOENT'||/^(MISSING_MINUTES|MISSING_OPENING_MINUTE|BAD_OHLCV|DUPLICATE_MINUTE|SOURCE_SCHEMA_MISMATCH)/.test(e.message))exclusions.push({date:entry.date,symbol:entry.symbol,reason:e.message.slice(0,90)});else throw e;}
 }
 if(!sessions.length)throw Error('NO_VALID_SESSIONS');
 const result=summarizeSessions(sessions,{slippageBpsPerSide:slipStr===undefined?15:Number(slipStr)});
 console.log(JSON.stringify({...result,excluded:exclusions},null,2));
}