#!/usr/bin/env node
/**
 * QHAP-TRADER 2022+ PRIVATE historical development batch, read-only.
 * Strict Upstox V3 1-minute monthly calls, with no live order routes.
 * Four user-selected months maximum per invocation; 1 second minimum gap.
 * Not a preregistered independent holdout. Outputs no raw prices/tokens.
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {setTimeout as sleep} from 'node:timers/promises';
import {
  validateRequest,fetchReadOnlyUpstoxHistory,savePrivateDevelopmentBatch
} from './upstox_v3_private_history.mjs';

const HOME_ROOT=()=>path.join(os.homedir(),'QHAP-TRADER-PRIVATE');
const monthPattern=/^20\d{2}-(0[1-9]|1[0-2])$/;
const monthEnd=m=>{
  const [year,month]=m.split('-').map(Number);
  return new Date(Date.UTC(year,month,0)).toISOString().slice(0,10);
};
const privateManifestName=(symbol,first,last)=>
  'development-multiwindow-'+symbol+'-'+first+'_to_'+last+'.json';
export function buildMultiYearDevelopmentPlan({instrumentKey,symbol,months}={}){
  if(typeof months!=='string')throw Error('INVALID_MONTHS_LIST');
  const names=months.split(',').map(x=>x.trim());
  if(names.length<2||names.length>4||
     names.some(x=>!monthPattern.test(x)||x<'2022-01'||
       x>new Date().toISOString().slice(0,7))||
     new Set(names).size!==names.length||
     names.some((x,i)=>i>0&&x<=names[i-1]))
    throw Error('REQUIRE_2_TO_4_UNIQUE_SORTED_HISTORICAL_MONTHS');
  // The months need not be contiguous. Dates alone are NOT verified regimes.
  const windows=names.map(month=>{
    const args=validateRequest({instrumentKey,symbol,
      from:month+'-01',to:monthEnd(month)});
    return {...args,month};
  });
  return Object.freeze({
    status:'PREVIEW_READ_ONLY_DEVELOPMENT_MULTIYEAR_NO_NETWORK',
    userSelectedMonths:names,
    distinctCalendarYears:new Set(names.map(x=>x.slice(0,4))).size,
    researchClassification:'INSPECTED_DEVELOPMENT_NOT_FROZEN_HOLDOUT',
    windows:windows.map(({instrumentKey,symbol,from,to,month})=>
      ({instrumentKey,symbol,from,to,month})),
    requestsPlanned:windows.length,
    requestsMade:0,candlesPrinted:0,
    noNetwork:true,noOrders:true,realOrdersSent:0,
    canTradeRealMoney:false
  });
}
const createNewJson=(file,value)=>{
  fs.mkdirSync(path.dirname(file),{recursive:true,mode:0o700});
  const fd=fs.openSync(file,'wx',0o600);
  try{
    const bytes=Buffer.from(JSON.stringify(value,null,2)+'\n','utf8');
    let cursor=0;
    while(cursor<bytes.length){
      const n=fs.writeSync(fd,bytes,cursor,bytes.length-cursor,null);
      if(!Number.isSafeInteger(n)||n<=0||n>bytes.length-cursor)
        throw Error('PRIVATE_BATCH_INDEX_WRITE_UNCERTAIN');
      cursor+=n;
    }
    fs.fsyncSync(fd);
  }finally{fs.closeSync(fd);}
};
export async function runDevelopmentBatch(plan,token,{
  fetcher=fetchReadOnlyUpstoxHistory,
  saver=savePrivateDevelopmentBatch,
  pause=()=>sleep(1200),
  privateRoot=HOME_ROOT()
}={}){
  if(!plan||plan.status!=='PREVIEW_READ_ONLY_DEVELOPMENT_MULTIYEAR_NO_NETWORK'||
     !Array.isArray(plan.windows)||plan.windows.length<2||plan.windows.length>4||
     !plan.windows.every(x=>x&&validateRequest(x))||
     typeof token!=='string'||token.length<16||token.length>16000||/\s/.test(token))
    throw Error('INVALID_DEVELOPMENT_PLAN_OR_READ_ONLY_TOKEN');
  const selected=plan.userSelectedMonths||[];
  if(!Array.isArray(selected)||selected.length!==plan.windows.length||
     plan.windows.some((x,i)=>x.month!==selected[i]))
    throw Error('INVALID_FROZEN_MONTH_SELECTION');
  const target=path.join(privateRoot,'manifests',
    privateManifestName(plan.windows[0].symbol,selected[0],selected.at(-1)));
  // Don't make even one request if the combined dataset already exists.
  if(fs.existsSync(target))throw Error('PRIVATE_BATCH_INDEX_ALREADY_EXISTS');
  const result={
    status:'DEVELOPMENT_BATCH_IN_PROGRESS',
    classification:'INSPECTED_DEVELOPMENT_NOT_UNSEEN_EDGE',
    userAttestsUpstoxVerbalResearchPermission:true,
    writtenEntitlementIndependentlyVerified:false,
    instrumentAlias:plan.windows[0].symbol,
    monthCountRequested:plan.windows.length,
    monthCountCompleted:0,
    requestsAttempted:0,
    inputCandlesStored:0,candidateCompleteDays:0,
    months:[],combinedManifest:null,
    estimatedRegimesIndependentlyVerified:false,
    tradingEdgeVerified:false,
    rawCandlesPrinted:false,tokenPrinted:false,
    realOrderRoutePresent:false,realOrdersSent:0,canTradeRealMoney:false
  };
  const eligible=[];
  for(let i=0;i<plan.windows.length;i++){
    const window=plan.windows[i];
    if(i)await pause();
    result.requestsAttempted++;
    try{
      // Exactly ONE fixed-origin Upstox GET by the already tested importer.
      const batch=await fetcher(window,token);
      const saved=saver(batch,privateRoot);
      result.months.push({month:window.month,
        status:saved.status,candlesStored:saved.candlesStored,
        candidateCompleteDays:saved.candidateCompleteDays,
        weekdayDatesWithNoProviderBarsUnverified:saved.weekdayDatesWithNoProviderBarsUnverified});
      result.monthCountCompleted++;
      result.inputCandlesStored+=saved.candlesStored;
      result.candidateCompleteDays+=saved.candidateCompleteDays;
      eligible.push(...batch.eligible);
    }catch(e){
      result.status='DEVELOPMENT_BATCH_PARTIAL_HALT_NO_TRADE';
      // Whitelist only codes emitted by our local read-only adapter.
      // A backend error message that merely looks like ALL_CAPS could
      // contain a credential; never return arbitrary injected text.
      const reason=e?.message||'';
      const allowed=reason==='PRIVATE_SOURCE_ALREADY_EXISTS_REFUSE_OVERWRITE'||
        /^UPSTOX_HISTORY_HTTP_[1-5][0-9]{2}$/.test(reason)||
        ['UPSTOX_HISTORY_READ_ONLY_NETWORK_FAILURE','UPSTOX_HISTORY_TOO_LARGE',
          'UPSTOX_HISTORY_NOT_JSON','UPSTOX_HISTORY_RESPONSE_READ_FAILURE',
          'DUPLICATE_PROVIDER_CANDLE','INVALID_OHLCV_OR_OI_CANDLE',
          'INVALID_UPSTOX_HISTORY_ENVELOPE','INVALID_OR_OUT_OF_RANGE_IST_CANDLE',
          'OUTSIDE_REGULAR_NSE_MINUTE_REQUIRES_SESSION_REVIEW'].includes(reason);
      result.failureReason=allowed?reason:'PRIVATE_DEVELOPMENT_REQUEST_FAILED';
      result.failedMonth=window.month;
      return result;
    }
  }
  // Local output contains dates/symbol only, no licensed raw candles.
  try{
    createNewJson(target,eligible);
    result.combinedManifest=target;
    result.status=eligible.length?
      'DEVELOPMENT_MULTIYEAR_BATCH_LOCAL_ONLY_COMPLETE':
      'DEVELOPMENT_MULTIYEAR_NO_ELIGIBLE_SESSIONS';
  }catch{
    result.status='DEVELOPMENT_BATCH_INDEX_UNCERTAIN_MANUAL_REVIEW';
    result.combinedManifest=null;
  }
  return result;
}
export function parseArgs(args){
  if(args.length!==7||!['--preview','--fetch-development'].includes(args[0])||
     args[1]!=='--instrument'||args[3]!=='--symbol'||args[5]!=='--months')
    throw Error('USAGE_INVALID_MULTIYEAR_ARGUMENTS');
  const mode=args[0],instrumentKey=args[2],symbol=args[4],months=args[6];
  return {mode,plan:buildMultiYearDevelopmentPlan({instrumentKey,symbol,months})};
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  try{
    const args=process.argv.slice(2);
    const confirmed=args.at(-1)==='--confirm-read-only-private-import';
    const {mode,plan}=parseArgs(confirmed?args.slice(0,-1):args);
    if(mode==='--preview'){
      if(confirmed)throw Error('PREVIEW_MUST_NOT_HAVE_CONFIRMATION');
      console.log(JSON.stringify(plan,null,2));
    }else{
      if(!confirmed)throw Error('EXPLICIT_PRIVATE_IMPORT_CONFIRMATION_REQUIRED');
      const result=await runDevelopmentBatch(
        plan,process.env.UPSTOX_ANALYTICS_TOKEN);
      console.log(JSON.stringify(result,null,2));
      process.exitCode=result.status===
        'DEVELOPMENT_MULTIYEAR_BATCH_LOCAL_ONLY_COMPLETE'?0:1;
    }
  }catch(e){
    const reason=/^[A-Z0-9_]+$/.test(e?.message||'')?
      e.message:'INVALID_REQUEST_OR_LOCAL_BATCH_FAILURE';
    console.error(JSON.stringify({status:'DEVELOPMENT_BATCH_BLOCKED_NO_TRADE',
      reason,canTradeRealMoney:false,realOrdersSent:0},null,2));
    process.exitCode=1;
  }
}
