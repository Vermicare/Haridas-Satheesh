#!/usr/bin/env node
/**
 * QHAP-TRADER read-only Upstox V3 1-minute HISTORICAL DEVELOPMENT INGEST.
 * User-local only. No orders, broker SDK, websockets or automatic trading.
 * A user-attested verbal authorization is not a broker/exchange written receipt.
 * Never publish downloaded NSE source candles or an analytics token to GitHub.
 */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const API_ORIGIN='https://api.upstox.com';
const MAX_CANDLES=15000;
const MAX_RESPONSE_BYTES=8_000_000;
const ONE_MINUTE_MS=60_000;
const DATA_ROOT=()=>path.join(os.homedir(),'QHAP-TRADER-PRIVATE');
const SHA=x=>crypto.createHash('sha256').update(x).digest('hex');
const hhmm=m=>String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0');
const validDate=date=>{
  if(typeof date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(date))return false;
  const ms=Date.parse(date+'T00:00:00Z');
  return Number.isFinite(ms)&&new Date(ms).toISOString().slice(0,10)===date;
};
const dayMs=date=>Date.parse(date+'T00:00:00Z');
const minuteOf=s=>Number(s.slice(0,2))*60+Number(s.slice(3,5));
const ymd=date=>date.replaceAll('-','');
export function validateRequest({instrumentKey,symbol,from,to}={}){
  if(typeof instrumentKey!=='string'||!/^NSE_EQ\|[A-Z0-9]{12}$/.test(instrumentKey))
    throw Error('INVALID_NSE_EQUITY_INSTRUMENT_KEY');
  if(typeof symbol!=='string'||!/^[A-Z][A-Z0-9&_-]{0,20}$/.test(symbol))
    throw Error('INVALID_RESEARCH_SYMBOL');
  if(!validDate(from)||!validDate(to)||from>to||from.slice(0,7)!==to.slice(0,7)||
     from<'2022-01-01'||to>new Date().toISOString().slice(0,10))
    throw Error('INVALID_OR_OVERLONG_DATE_RANGE_USE_ONE_CALENDAR_MONTH');
  return Object.freeze({instrumentKey,symbol,from,to});
}
export function createReadOnlyUrl(args){
  const {instrumentKey,from,to}=validateRequest(args);
  return API_ORIGIN+'/v3/historical-candle/'+encodeURIComponent(instrumentKey)+
    '/minutes/1/'+to+'/'+from;
}
export function normalizeUpstoxCandles(packet,request){
  const {from,to}=validateRequest(request);
  if(!packet||packet.status!=='success'||!packet.data||
     !Array.isArray(packet.data.candles)||
     packet.data.candles.length>MAX_CANDLES)
    throw Error('INVALID_UPSTOX_HISTORY_ENVELOPE');
  const items=[],times=new Set();
  for(const row of packet.data.candles){
    if(!Array.isArray(row)||row.length!==7)
      throw Error('INVALID_UPSTOX_CANDLE_SHAPE');
    const [stamp,o,h,l,c,v,oi]=row;
    const m=typeof stamp==='string'&&stamp.match(
      /^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?\+05:30$/
    );
    if(!m||!validDate(m[1])||m[4]!=='00'||
       (m[5]&&!/^0+$/.test(m[5]))||
       m[1]<from||m[1]>to)
      throw Error('INVALID_OR_OUT_OF_RANGE_IST_CANDLE');
    const minute=Number(m[2])*60+Number(m[3]);
    if(!Number.isInteger(minute)||minute<555||minute>929)
      throw Error('OUTSIDE_REGULAR_NSE_MINUTE_REQUIRES_SESSION_REVIEW');
    if(![o,h,l,c].every(x=>typeof x==='number'&&Number.isFinite(x)&&x>0)||
       h<Math.max(o,l,c)||l>Math.min(o,h,c)||
       !Number.isSafeInteger(v)||v<0||
       !(oi===null||(typeof oi==='number'&&Number.isFinite(oi)&&oi>=0)))
      throw Error('INVALID_OHLCV_OR_OI_CANDLE');
    const key=m[1]+'T'+m[2]+':'+m[3];
    if(times.has(key))throw Error('DUPLICATE_PROVIDER_CANDLE');
    times.add(key);
    items.push({date:m[1],minute,stamp,o,h,l,c,v});
  }
  items.sort((a,b)=>a.date.localeCompare(b.date)||a.minute-b.minute);
  return items;
}
export function buildLocalDevelopmentBatch(candles,request){
  const {symbol,from,to,instrumentKey}=validateRequest(request);
  if(!Array.isArray(candles))throw Error('INVALID_NORMALIZED_CANDLES');
  const grouped=new Map();
  for(const b of candles){
    if(!b||!validDate(b.date)||b.date<from||b.date>to||
       !Number.isInteger(b.minute)||b.minute<555||b.minute>929)
      throw Error('INVALID_NORMALIZED_CANDLE');
    if(!grouped.has(b.date))grouped.set(b.date,[]);
    grouped.get(b.date).push(b);
  }
  const sessions=[],eligible=[];
  for(const [date,bars] of grouped){
    const observed=new Set(bars.filter(b=>b.minute>=555&&b.minute<=929).map(b=>b.minute));
    const missing=[];
    for(let m=555;m<=929;m++)if(!observed.has(m))missing.push(hhmm(m));
    const weekday=new Date(dayMs(date)).getUTCDay();
    const exceptional=weekday===0||weekday===6;
    const volume=bars.reduce((n,b)=>n+b.v,0);
    const state=exceptional?'WEEKEND_REQUIRES_EXCHANGE_CALENDAR':
      missing.length?'INCOMPLETE_MINUTE_COVERAGE':
      volume<=0?'ZERO_VOLUME_NO_EXECUTION_EVIDENCE':
      'CANDIDATE_COMPLETE_UNVERIFIED';
    const csv=bars.map(b=>[symbol,ymd(date),hhmm(b.minute),
      b.o,b.h,b.l,b.c,b.v,0].join(',')).join('\n')+'\n';
    const entry={date,symbol,minuteBars:bars.length,expectedRegularSessionMinuteBars:375,
      openingMinutePresent:observed.has(555),
      missingRequiredMinutes:missing.length,firstMissingRequiredMinute:missing[0]||null,
      candidateState:state,sha256:SHA(csv),csv};
    sessions.push(entry);
    if(state==='CANDIDATE_COMPLETE_UNVERIFIED')
      eligible.push({date:ymd(date),symbol});
  }
  const observedDays=new Set(grouped.keys()),unknownWeekdays=[];
  for(let ms=dayMs(from);ms<=dayMs(to);ms+=86400000){
    const day=new Date(ms).toISOString().slice(0,10),w=new Date(ms).getUTCDay();
    if(w!==0&&w!==6&&!observedDays.has(day))
      unknownWeekdays.push(day);
  }
  return {instrumentKey,symbol,from,to,sessions,eligible,unknownWeekdays,
    candlesticksSeen:candles.length};
}
function writePrivateNewFile(file,content){
  fs.mkdirSync(path.dirname(file),{recursive:true,mode:0o700});
  let fd;
  try{
    fd=fs.openSync(file,'wx',0o600);
    const bytes=Buffer.from(content,'utf8');
    let at=0;
    while(at<bytes.length){
      const n=fs.writeSync(fd,bytes,at,bytes.length-at,null);
      if(!Number.isSafeInteger(n)||n<=0||n>bytes.length-at)
        throw Error('PRIVATE_DATA_WRITE_UNCERTAIN');
      at+=n;
    }
    fs.fsyncSync(fd);
  }finally{if(fd!==undefined)fs.closeSync(fd);}
}
export function savePrivateDevelopmentBatch(batch,privateRoot=DATA_ROOT()){
  if(!batch||!Array.isArray(batch.sessions)||!Array.isArray(batch.eligible)||
     !Array.isArray(batch.unknownWeekdays)||!validDate(batch.from)||!validDate(batch.to))
    throw Error('INVALID_BATCH_TO_SAVE');
  // Fixed private location in CLI. The optional root is test-only injection.
  const historical=path.join(privateRoot,'historical');
  const manifests=path.join(privateRoot,'manifests');
  const stem='development-'+batch.symbol+'-'+batch.from+'-to-'+batch.to;
  const selected=path.join(manifests,stem+'.json');
  const audit=path.join(manifests,stem+'.audit.json');
  const targets=batch.sessions.map(x=>({
    file:path.join(historical,x.date.slice(0,4),x.date.slice(5,7),
      x.date.slice(8,10),batch.symbol+'.csv'),csv:x.csv
  }));
  // Never alter previous local sources, even if the same API is re-fetched.
  for(const f of [...targets.map(x=>x.file),selected,audit])
    if(fs.existsSync(f))throw Error('PRIVATE_SOURCE_ALREADY_EXISTS_REFUSE_OVERWRITE');
  const compact=batch.sessions.map(({csv,...x})=>x);
  const technical={kind:'QHAP_LOCAL_DEVELOPMENT_ONLY_UNVERIFIED',
    dataSource:'Upstox Historical Candle V3 one-minute NSE_EQ',
    requestedInstrument:batch.instrumentKey,
    requestedFrom:batch.from,requestedTo:batch.to,
    userReportsVerbalResearchPermission:true,
    writtenEndUserPermissionIndependentlyVerified:false,
    corporateActionsIndependentlyVerified:false,
    exchangeCalendarIndependentlyVerified:false,
    historicalSourceCompletenessIndependentlyVerified:false,
    specificStrategyResearchFrozenBeforeDataInspection:false,
    excludedUnknownWeekdays:batch.unknownWeekdays,
    perDay:compact,
    privateRawDataNotRedistributable:true,
    realOrdersSent:0,liveOrderRoutePresent:false,canTrade:false
  };
  for(const x of targets)writePrivateNewFile(x.file,x.csv);
  writePrivateNewFile(selected,JSON.stringify(batch.eligible,null,2)+'\n');
  writePrivateNewFile(audit,JSON.stringify(technical,null,2)+'\n');
  return Object.freeze({
    status:'LOCAL_DEVELOPMENT_HISTORY_STORED_NOT_HOLDOUT',
    privateRoot,manifest:selected,audit,
    candlesStored:batch.candlesticksSeen,
    candidateCompleteDays:batch.eligible.length,
    excludedOrExceptionalObservedDays:batch.sessions.length-batch.eligible.length,
    weekdayDatesWithNoProviderBarsUnverified:batch.unknownWeekdays.length,
    writtenPermissionIndependentlyVerified:false,
    validOutOfSampleEdgeDemonstrated:false,
    rawPricesPrinted:false,tokenPrinted:false,
    liveOrderRoutePresent:false,realOrdersSent:0,canTrade:false
  });
}
export async function fetchReadOnlyUpstoxHistory(request,token,fetchFn=fetch){
  const url=createReadOnlyUrl(request);
  if(typeof token!=='string'||token.length<16||token.length>16000||/[\s\r\n]/.test(token))
    throw Error('MISSING_OR_INVALID_READ_ONLY_ANALYTICS_TOKEN');
  let response;
  try{
    response=await fetchFn(url,{method:'GET',
      headers:{Accept:'application/json',Authorization:'Bearer '+token},
      redirect:'error',signal:AbortSignal.timeout(20000)});
  }catch{throw Error('UPSTOX_HISTORY_READ_ONLY_NETWORK_FAILURE');}
  if(!response||response.status!==200||!response.ok)
    throw Error('UPSTOX_HISTORY_HTTP_'+String(response?.status??'UNKNOWN'));
  if(response.headers?.get&&
     Number(response.headers.get('content-length')||0)>MAX_RESPONSE_BYTES)
    throw Error('UPSTOX_HISTORY_TOO_LARGE');
  let responseText;
  try{responseText=await response.text();}
  catch{throw Error('UPSTOX_HISTORY_RESPONSE_READ_FAILURE');}
  if(typeof responseText!=='string'||responseText.length>MAX_RESPONSE_BYTES)
    throw Error('UPSTOX_HISTORY_TOO_LARGE');
  let packet;
  try{packet=JSON.parse(responseText);}
  catch{throw Error('UPSTOX_HISTORY_NOT_JSON');}
  return buildLocalDevelopmentBatch(normalizeUpstoxCandles(packet,request),request);
}
export function parseLocalArgs(args){
  if(args.length!==8||args.some((x,i)=>i%2===0&&!['--instrument','--symbol','--from','--to'].includes(x)))
    throw Error('USAGE_REQUIRE_INSTRUMENT_SYMBOL_FROM_TO');
  const obj={};
  for(let i=0;i<args.length;i+=2){
    const key=args[i],value=args[i+1];
    if(Object.hasOwn(obj,key)||typeof value!=='string')
      throw Error('DUPLICATE_OR_INVALID_ARG');
    obj[key]=value;
  }
  if(Object.keys(obj).length!==4)throw Error('INCOMPLETE_ARGUMENTS');
  return validateRequest({instrumentKey:obj['--instrument'],
    symbol:obj['--symbol'],from:obj['--from'],to:obj['--to']});
}
const invoked=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  if(process.argv.length===3&&process.argv[2]==='--help'){
    console.log('Read-only development ingestion. Usage: node upstox_v3_private_history.mjs --instrument "NSE_EQ|INE002A01018" --symbol RELIANCE --from 2025-01-06 --to 2025-01-10');
    console.log('Requires UPSTOX_ANALYTICS_TOKEN in local process environment. No order methods or other API requests.');
  }else{
    try{
      const request=parseLocalArgs(process.argv.slice(2));
      const batch=await fetchReadOnlyUpstoxHistory(request,process.env.UPSTOX_ANALYTICS_TOKEN);
      console.log(JSON.stringify(savePrivateDevelopmentBatch(batch),null,2));
    }catch(error){
      // Never print tokens, raw HTTP bodies, source prices, sensitive headers.
      const code=/^[A-Z0-9_]+$/.test(error?.message||'')?
        error.message:'LOCAL_HISTORY_PIPELINE_FAILED_NO_RAW_DATA_PRINTED';
      console.error(JSON.stringify({status:'HALT_LOCAL_INGEST',reason:code,
        canTrade:false,realOrdersSent:0},null,2));
      process.exitCode=1;
    }
  }
}
