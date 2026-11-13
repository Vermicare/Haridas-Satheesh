#!/usr/bin/env node
/**
 * QHAP NSE local DAILY Upstox V3 historical-development research bridge.
 * Strictly read-only, no orders, no retries, no provider data in GitHub.
 * Does not certify fees, equity corporate actions, exchange calendar,
 * original licensing or a profitable trading edge.
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {
  runEquitySwingAgentNetwork,verifyEquitySwingAgentAudit
} from './nse_swing_interdependent_agent_network.mjs';

const HOST='https://api.upstox.com';
const MS_DAY=86400000;
const SHA=x=>crypto.createHash('sha256').update(x).digest('hex');
const validDate=x=>{
  if(typeof x!=='string'||!/^\d{4}-\d\d-\d\d$/.test(x))return false;
  const ms=Date.parse(x+'T00:00:00Z');
  return Number.isFinite(ms)&&new Date(ms).toISOString().slice(0,10)===x;
};
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const noOrders=Object.freeze({
  brokerOrderRoutePresent:false,realOrdersSent:0,
  realMoneyTradingAuthorized:false,apiOrdersSubmitted:0,
  modelApiCallsMade:0,canTradeRealMoney:false
});
export function validateDailyWindow({
  instrumentKey,symbol,from,to
}={}){
  if(typeof instrumentKey!=='string'||
     !/^NSE_EQ\|[A-Z0-9]{12}$/.test(instrumentKey)||
     typeof symbol!=='string'||!/^[A-Z][A-Z0-9&_-]{0,20}$/.test(symbol)||
     !validDate(from)||!validDate(to)||from>to||from<'2022-01-01'||
     to>new Date().toISOString().slice(0,10)||
     (Date.parse(to+'T00:00:00Z')-
      Date.parse(from+'T00:00:00Z'))/MS_DAY>365)
    throw Error('INVALID_PRIVATE_DAILY_RESEARCH_WINDOW');
  return Object.freeze({instrumentKey,symbol,from,to});
}
export function previewDailyWindow(raw){
  const request=validateDailyWindow(raw);
  return {
    ...noOrders,
    status:'PRIVATE_DAILY_RESEARCH_PREVIEW_NO_NETWORK',
    source:'UPSTOX_HISTORICAL_V3_DAYS_1',
    request,requestsPlanned:1,requestsAttempted:0,
    readsToken:false,printsRawCandles:false,
    datasetClassification:'INSPECTED_DEVELOPMENT_NOT_UNSEEN_HOLDOUT',
    chartFillsVerified:false,
    corporateActionsIndependentlyVerified:false
  };
}
export function historyDailyUrl(request){
  const r=validateDailyWindow(request);
  return HOST+'/v3/historical-candle/'+encodeURIComponent(r.instrumentKey)+
    '/days/1/'+r.to+'/'+r.from;
}
export function validateAndSortDaily(packet,request){
  const r=validateDailyWindow(request);
  if(!packet||packet.status!=='success'||
     !Array.isArray(packet.data?.candles)||
     packet.data.candles.length>270)
    throw Error('INVALID_UPSTOX_DAILY_RESPONSE');
  const seen=new Set(),out=[];
  for(const raw of packet.data.candles){
    if(!Array.isArray(raw)||raw.length!==7)
      throw Error('INVALID_DAILY_PROVIDER_ROW');
    const [timestamp,open,high,low,close,volume,oi]=raw;
    const m=typeof timestamp==='string'&&timestamp.match(
      /^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,3})?\+05:30$/
    );
    if(!m||!validDate(m[1])||m[1]<r.from||m[1]>r.to||
       Number(m[2])>23||Number(m[3])>59||Number(m[4])>59||
       seen.has(m[1])||
       ![open,high,low,close].every(v=>finite(v)&&v>0)||
       high<Math.max(open,low,close)||
       low>Math.min(open,high,close)||
       !Number.isSafeInteger(volume)||volume<=0||
       !(oi===null||(finite(oi)&&oi>=0)))
      throw Error('INVALID_OR_DUPLICATE_DAILY_CANDLE');
    seen.add(m[1]);
    out.push({date:m[1],open,high,low,close,volume});
  }
  out.sort((a,b)=>a.date.localeCompare(b.date));
  if(out.length<80||out.length>260)
    throw Error('NOT_ENOUGH_OR_EXCESSIVE_DAILY_BARS_FOR_RESEARCH');
  for(let i=1;i<out.length;i++){
    const days=(Date.parse(out[i].date+'T00:00:00Z')-
      Date.parse(out[i-1].date+'T00:00:00Z'))/MS_DAY;
    if(days>12)throw Error('DAILY_CALENDAR_GAP_REQUIRES_REVIEW');
  }
  return out;
}
export async function fetchUpstoxPrivateDaily(
  request,token,fetchImpl=fetch
){
  const url=historyDailyUrl(request);
  if(typeof token!=='string'||token.length<16||
     token.length>16000||/\s/.test(token))
    throw Error('INVALID_LOCAL_ANALYTICS_TOKEN');
  let response;
  try{
    response=await fetchImpl(url,{
      method:'GET',redirect:'error',
      headers:{Authorization:'Bearer '+token,Accept:'application/json'},
      signal:AbortSignal.timeout(20000)
    });
  }catch{throw Error('DAILY_NETWORK_OUTCOME_UNKNOWN_NO_RETRY');}
  if(response?.ok!==true||response.status!==200)
    throw Error('UPSTOX_DAILY_HTTP_'+String(
      Number.isInteger(response?.status)?response.status:'UNKNOWN'));
  if(Number(response.headers?.get?.('content-length')||0)>1000000)
    throw Error('UPSTOX_DAILY_RESPONSE_TOO_LARGE');
  let body;
  try{body=await response.text();}
  catch{throw Error('UPSTOX_DAILY_RESPONSE_UNREADABLE');}
  if(typeof body!=='string'||body.length>1000000)
    throw Error('UPSTOX_DAILY_RESPONSE_TOO_LARGE');
  let packet;
  try{packet=JSON.parse(body);}
  catch{throw Error('UPSTOX_DAILY_RESPONSE_NOT_JSON');}
  return validateAndSortDaily(packet,request);
}
const costAssumptions=()=>({
  // This is intentionally a conservative illustrative placeholder, NOT
  // a signed Upstox account-specific tariff or backtested execution cost.
  estimatedBrokerageAndTaxesRoundTripRupees:70,
  slippageBpsPerSide:15,spreadRoundTripBps:8,
  uncertaintyReserveBps:10,
  sourceScheduleIndependentlyVerified:false
});
const writeNew=(name,content)=>{
  fs.mkdirSync(path.dirname(name),{recursive:true,mode:0o700});
  const fd=fs.openSync(name,'wx',0o600);
  try{
    const bytes=Buffer.from(content);
    let pos=0;
    while(pos<bytes.length){
      const n=fs.writeSync(fd,bytes,pos,bytes.length-pos,null);
      if(!Number.isSafeInteger(n)||n<=0)
        throw Error('PRIVATE_DAILY_WRITE_UNCERTAIN');
      pos+=n;
    }
    fs.fsyncSync(fd);
  }finally{fs.closeSync(fd);}
};
export async function runPrivateDailyResearch(
  request,token,{fetcher=fetchUpstoxPrivateDaily,
    evaluator=runEquitySwingAgentNetwork,
    root=path.join(os.homedir(),'QHAP-TRADER-PRIVATE')}={}
){
  const req=validateDailyWindow(request);
  const file=path.join(root,'equity_daily',
    'development-'+req.symbol+'-'+req.from+'-to-'+req.to+'.json');
  if(fs.existsSync(file))
    throw Error('PRIVATE_DAILY_RESEARCH_ALREADY_EXISTS_NO_OVERWRITE');
  const rows=await fetcher(req,token);
  const asset={
    instrumentKey:req.instrumentKey,symbol:req.symbol,
    sourceClass:'PRIVATE_REPLAY',asOfDate:rows.at(-1)?.date,
    dailyBars:rows,costAssumptions:costAssumptions()
  };
  const content=JSON.stringify(asset,null,2)+'\n';
  // Do not return the raw rows in the results or log them to GitHub.
  writeNew(file,content);
  const evaluated=await evaluator(asset);
  return {
    ...noOrders,
    status:'PRIVATE_DAILY_DEVELOPMENT_STORED_AND_AGENT_RESEARCH_RUN',
    source:'UPSTOX_HISTORICAL_V3_DAYS_1',
    datesCovered:{first:rows[0].date,last:rows.at(-1).date},
    dailyBarsStored:rows.length,
    requestsAttempted:1,tokenPrinted:false,rawCandlesPrinted:false,
    localPrivateFile:file,sha256OfPrivateArtifact:SHA(content),
    researchClassification:'INSPECTED_DEVELOPMENT_NOT_UNSEEN_HOLDOUT',
    sourceEntitlementIndependentlyVerified:false,
    corporateActionsIndependentlyVerified:false,
    exchangeCalendarIndependentlyVerified:false,
    userFeeContractNoteIndependentlyVerified:false,
    agentAuditValid:verifyEquitySwingAgentAudit(evaluated),
    agentDecision:evaluated.finalDecision,
    agentResearchWatch:evaluated.researchWatch,
    agentStatus:evaluated.status,
    realizedReturnsOrProfitsDemonstrated:false
  };
}
function args(argv){
  if(argv.length!==9||
     !['--preview','--fetch-read-only-development'].includes(argv[0])||
     argv[1]!=='--instrument'||argv[3]!=='--symbol'||
     argv[5]!=='--from'||argv[7]!=='--to')
    throw Error('INVALID_DAILY_CLI_ARGUMENTS');
  return {
    mode:argv[0],
    request:validateDailyWindow({instrumentKey:argv[2],
      symbol:argv[4],from:argv[6],to:argv[8]})
  };
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  try{
    const argv=process.argv.slice(2);
    const explicit=argv.at(-1)==='--confirm-private-research-only';
    const {mode,request}=args(explicit?argv.slice(0,-1):argv);
    if(mode==='--preview'){
      if(explicit)throw Error('INVALID_PREVIEW_CONFIRMATION');
      console.log(JSON.stringify(previewDailyWindow(request),null,2));
    }else{
      if(!explicit)throw Error('EXPLICIT_USER_LOCAL_RESEARCH_CONFIRMATION_REQUIRED');
      const result=await runPrivateDailyResearch(
        request,process.env.UPSTOX_ANALYTICS_TOKEN);
      console.log(JSON.stringify(result,null,2));
      process.exitCode=result.agentAuditValid&&
        result.agentDecision==='NO_TRADE'?0:1;
    }
  }catch(e){
    const known=/^(INVALID_|PRIVATE_DAILY_RESEARCH_ALREADY_EXISTS_NO_OVERWRITE|DAILY_NETWORK_OUTCOME_UNKNOWN_NO_RETRY|UPSTOX_DAILY_HTTP_[1-5]\d\d|UPSTOX_DAILY_RESPONSE_[A-Z_]+|NOT_ENOUGH_OR_EXCESSIVE_DAILY_BARS_FOR_RESEARCH|DAILY_CALENDAR_GAP_REQUIRES_REVIEW|EXPLICIT_USER_LOCAL_RESEARCH_CONFIRMATION_REQUIRED|PRIVATE_DAILY_WRITE_UNCERTAIN)$/.test(e?.message||'');
    console.error(JSON.stringify({...noOrders,status:'PRIVATE_DAILY_RESEARCH_HALT_NO_TRADE',
      reason:known?e.message:'UNKNOWN_READ_ONLY_IMPORT_ERROR'},null,2));
    process.exitCode=1;
  }
}
