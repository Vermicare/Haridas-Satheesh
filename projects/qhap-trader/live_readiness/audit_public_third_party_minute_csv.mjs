#!/usr/bin/env node
/**
 * Inspect a USER-LOCAL one-day copy of a third-party NSE cash-equity 1-minute
 * CSV (e.g. GitHub "SYMBOL,YYYYMMDD,HH:MM,O,H,L,C,V,OI" archives).
 *
 * This is a file-structure and gap audit only, NOT licensed historical-data
 * ingestion, a data-rights grant, a fill simulator or holdout qualification.
 * No network, provider credentials, payments, paper orders or live orders.
 * Do not commit the third-party CSV to GitHub.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const START=9*60+15;
const END=15*60+29;
const MAX_BYTES=5_000_000;
const MAX_LINES=40_000;
const SYMBOL=/^[A-Z][A-Z0-9&-]{0,29}$/;
const hhm=m=>String(Math.floor(m/60)).padStart(2,'0')+':'+
  String(m%60).padStart(2,'0');
const SAFETY=Object.freeze({
  status:'PUBLIC_THIRD_PARTY_STRUCTURE_AUDIT_ONLY_NO_TRADE',
  sourceClassification:'UNAUTHENTICATED_THIRD_PARTY_INSPECTED_DEVELOPMENT',
  sourceRightsIndependentlyVerified:false,
  provenanceIndependentlyVerified:false,
  corporateActionHistoryVerified:false,
  exchangeCalendarIndependentlyVerified:false,
  genuineUnseenHoldoutSessions:0,
  observedForwardSessions:0,
  historicalCostsCertified:false,
  economicEdgeVerified:false,
  dataUseAuthorizedByThisTool:false,
  eligibleForTradingResearchPromotion:false,
  canTrade:false,canPlacePaperOrders:false,
  finalBrokerDecision:'NO_TRADE',
  realOrderRoutePresent:false,realOrdersSent:0,paperOrdersSent:0,
  networkRequestsMade:0,apiCredentialsRead:false,
  rawPricesPrinted:false
});
const SAFE_ERRORS=new Set([
  'INVALID_AUDIT_ARGUMENTS',
  'INVALID_EXPECTED_SYMBOL_OR_DATE',
  'INPUT_FILE_NOT_ABSOLUTE',
  'INPUT_MUST_BE_REGULAR_FILE',
  'INPUT_FILE_TOO_LARGE_OR_EMPTY',
  'LOCAL_FILE_READ_FAILED',
  'INVALID_CSV_CONTENT_OR_TOO_MANY_ROWS',
  'INVALID_CSV_ROW_SHAPE',
  'WRONG_SYMBOL_OR_DATE_IN_FILE',
  'DUPLICATE_MINUTE_TIMESTAMP',
  'INVALID_OHLC_OR_VOLUME',
  'INVALID_MINUTE_TIMESTAMP'
]);
const validDate=s=>{
  if(typeof s!=='string'||!/^20\d\d-\d\d-\d\d$/.test(s))return false;
  const t=Date.parse(s+'T00:00:00Z');
  return Number.isFinite(t)&&new Date(t).toISOString().slice(0,10)===s;
};
const validNumber=s=>typeof s==='string'&&
  /^(?:\d+(?:\.\d*)?|\.\d+)$/.test(s)&&
  Number.isFinite(Number(s));
const validInt=s=>typeof s==='string'&&/^\d+$/.test(s)&&
  Number.isSafeInteger(Number(s));

export function inspectPublicThirdPartyMinuteCsv(content,{expectedSymbol,expectedDate}={}){
  if(!SYMBOL.test(expectedSymbol||'')||!validDate(expectedDate))
    throw Error('INVALID_EXPECTED_SYMBOL_OR_DATE');
  if(typeof content!=='string'||Buffer.byteLength(content,'utf8')>MAX_BYTES||
    content.length<20)
    throw Error('INVALID_CSV_CONTENT_OR_TOO_MANY_ROWS');

  const lines=content.replace(/^\uFEFF/,'').trimEnd().split(/\r?\n/);
  if(!lines.length||lines.length>MAX_LINES)
    throw Error('INVALID_CSV_CONTENT_OR_TOO_MANY_ROWS');

  const seen=new Set();
  const regular=new Set();
  let preOpen=0,postClose=0;
  let observedZeroVolume=0;
  const ymd=expectedDate.replaceAll('-','');
  for(const line of lines){
    const p=line.split(',');
    if(p.length!==9)
      throw Error('INVALID_CSV_ROW_SHAPE');
    const [symbol,date,clock,o,h,l,c,v,oi]=p;
    if(symbol!==expectedSymbol||date!==ymd)
      throw Error('WRONG_SYMBOL_OR_DATE_IN_FILE');
    if(typeof clock!=='string'||!/^\d{2}:\d{2}$/.test(clock)||
      Number(clock.slice(0,2))>23||Number(clock.slice(3,5))>59)
      throw Error('INVALID_MINUTE_TIMESTAMP');
    const minute=Number(clock.slice(0,2))*60+Number(clock.slice(3,5));
    if(seen.has(minute))throw Error('DUPLICATE_MINUTE_TIMESTAMP');
    seen.add(minute);

    if(![o,h,l,c].every(validNumber)||!validInt(v)||
      !(oi===''||validInt(oi)))
      throw Error('INVALID_OHLC_OR_VOLUME');
    const prices=[o,h,l,c].map(Number);
    if(prices.some(x=>x<=0)||
      prices[1]<Math.max(prices[0],prices[2],prices[3])||
      prices[2]>Math.min(prices[0],prices[1],prices[3]))
      throw Error('INVALID_OHLC_OR_VOLUME');

    if(minute<START)preOpen++;
    else if(minute>END)postClose++;
    else{
      regular.add(minute);
      if(Number(v)===0)observedZeroVolume++;
    }
  }
  const missing=[];
  for(let i=START;i<=END;i++)if(!regular.has(i))missing.push(i);
  const weekday=new Date(expectedDate+'T00:00:00Z').getUTCDay();
  const weekend=weekday===0||weekday===6;
  const candidateComplete=missing.length===0&&!weekend&&
    observedZeroVolume===0;
  return Object.freeze({...SAFETY,
    expectedDate,sourceSymbolAlias:expectedSymbol,
    totalRows:lines.length,
    regularSessionStartIst:'09:15',
    regularSessionLastMinuteStartIst:'15:29',
    expectedRegularSessionMinuteRows:END-START+1,
    observedRegularSessionMinuteRows:regular.size,
    missingRegularSessionMinutes:missing.length,
    firstMissingRegularMinuteIst:missing.length?hhm(missing[0]):null,
    lastMissingRegularMinuteIst:missing.length?hhm(missing.at(-1)):null,
    openingMinutePresent:regular.has(START),
    closingMinutePresent:regular.has(END),
    preOpeningSessionRows:preOpen,
    afterRegularSessionRows:postClose,
    zeroVolumeRegularSessionRows:observedZeroVolume,
    weekendDateRequiresSpecialSessionReview:weekend,
    candidateRegularSessionShapeComplete: candidateComplete,
    certifiedCompleteTradingSessions:0,
    requiresExternalExchangeCalendarReview:true,
    requiresLicensedSourceAndRightsReview:true,
    localSourceSha256:crypto.createHash('sha256').update(content,'utf8').digest('hex')
  });
}
export function auditLocalThirdPartyCsvFile(filename,options){
  if(typeof filename!=='string'||!path.isAbsolute(filename))
    throw Error('INPUT_FILE_NOT_ABSOLUTE');
  // Reject local symlink indirection. No user-supplied path is emitted.
  let source;
  try{
    const stat=fs.lstatSync(filename);
    if(!stat.isFile()||stat.isSymbolicLink())
      throw Error('INPUT_MUST_BE_REGULAR_FILE');
    if(stat.size<20||stat.size>MAX_BYTES)
      throw Error('INPUT_FILE_TOO_LARGE_OR_EMPTY');
    source=fs.readFileSync(filename);
    if(source.byteLength!==stat.size)
      throw Error('LOCAL_FILE_READ_FAILED');
  }catch(e){
    if(['INPUT_MUST_BE_REGULAR_FILE','INPUT_FILE_TOO_LARGE_OR_EMPTY',
      'LOCAL_FILE_READ_FAILED'].includes(e?.message))throw e;
    throw Error('LOCAL_FILE_READ_FAILED');
  }
  return inspectPublicThirdPartyMinuteCsv(source.toString('utf8'),options);
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  try{
    if(process.argv.length!==8||process.argv[2]!=='--file'||
       process.argv[4]!=='--symbol'||process.argv[6]!=='--date')
      throw Error('INVALID_AUDIT_ARGUMENTS');
    const result=auditLocalThirdPartyCsvFile(process.argv[3],{
      expectedSymbol:process.argv[5],expectedDate:process.argv[7]});
    console.log(JSON.stringify(result,null,2));
  }catch(e){
    console.error(JSON.stringify({...SAFETY,
      status:'LOCAL_PUBLIC_DATA_AUDIT_BLOCKED_NO_TRADE',
      reason:SAFE_ERRORS.has(e?.message)?e.message:'UNVERIFIED_AUDIT_FAILURE'}));
    process.exitCode=1;
  }
}
