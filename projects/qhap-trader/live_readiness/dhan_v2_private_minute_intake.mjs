#!/usr/bin/env node
/**
 * QHAP-TRADER DhanHQ V2 private 1-minute historical SOURCE STRUCTURE intake.
 * Strictly read-only local files. No HTTP, tokens, broker SDK, trade routing,
 * market-data downloads, strategy signals or P&L generation.
 *
 * Public API documentation: https://dhanhq.co/docs/v2/historical-data/
 * Vendor support ticket #6635943 (2026-11-13) described private individual
 * historical backtesting permission. The ticket does NOT independently prove
 * NSE exchange rights, source authenticity, data accuracy or publication rights.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const SHA256=x=>crypto.createHash('sha256').update(x).digest('hex');
const MAX_BYTES=12_000_000;
const MAX_BARS=40_000;
const ONE_MINUTE_SECONDS=60;
const IST_OFFSET_SECONDS=5.5*3600;
const DAY_START=9*60+15;
const DAY_LAST=15*60+29;
const SESSION_BARS=375;
const MAX_WINDOW_CALENDAR_DAYS=90;
const FIELDS=['open','high','low','close','volume','timestamp'];
const MANIFEST_FIELDS=[
  'provider','dataClass','researchPurpose','exchangeSegment','instrument',
  'securityId','intervalMinutes','fromDate','toDate','supportTicketReference',
  'corporateActionTreatment','externalCalendarCertified',
  'sourceInstrumentMappingCertified'
];
const SAFE_CODES=new Set([
  'INVALID_CLI_ARGS','PRIVATE_INPUT_FILE_NOT_ABSOLUTE',
  'PRIVATE_INPUT_FILES_IDENTICAL','PRIVATE_INPUT_TOO_LARGE_OR_EMPTY',
  'PRIVATE_INPUT_READ_FAILED','PRIVATE_INPUT_NOT_JSON',
  'INVALID_LOCAL_DHAN_MANIFEST','INVALID_DHAN_RESPONSE_ENVELOPE',
  'INVALID_DHAN_PARALLEL_ARRAYS','INVALID_DHAN_OHLCV',
  'INVALID_DHAN_TIMESTAMP','OUTSIDE_FROZEN_DATE_WINDOW',
  'OUTSIDE_REGULAR_NSE_SESSION','NONMONOTONIC_OR_DUPLICATE_DHAN_TIMESTAMP',
  'OVERLONG_90_DAY_PROVIDER_WINDOW'
]);
const SAFETY=Object.freeze({
  finalBrokerDecision:'NO_TRADE',
  canTrade:false,
  canPlacePaperOrders:false,
  canPublishProviderData:false,
  canMakeEconomicEdgeClaims:false,
  realOrdersSent:0,paperOrdersSent:0,
  realOrderRoutePresent:false,brokerOrderRoutePresent:false,
  networkRequestsMade:0,modelApiCallsMade:0,
  independentlyAuthenticatedExchangeCalendar:false,
  independentlyVerifiedNseEntitlement:false,
  independentlyVerifiedInstrumentMapping:false,
  independentlyVerifiedCorporateActionHistory:false,
  independentlyVerifiedUnseenHoldout:false,
  strategyPerformanceTested:false,
  historicChargesCertified:false
});
const record=v=>!!v&&typeof v==='object'&&!Array.isArray(v);
const validDate=x=>typeof x==='string'&&/^20\d\d-\d\d-\d\d$/.test(x)&&
  !Number.isNaN(Date.parse(x+'T00:00:00Z'))&&
  new Date(x+'T00:00:00Z').toISOString().slice(0,10)===x;
const dayMs=x=>Date.parse(x+'T00:00:00Z');
const istDatetime=sec=>{
  const d=new Date((sec+IST_OFFSET_SECONDS)*1000).toISOString();
  return {date:d.slice(0,10),minute:Number(d.slice(11,13))*60+
    Number(d.slice(14,16)),second:Number(d.slice(17,19))};
};
const weekday=day=>new Date(dayMs(day)).getUTCDay();

export function validateDhanLocalManifest(m){
  if(!record(m)||Object.keys(m).sort().join('|')!==[...MANIFEST_FIELDS].sort().join('|')||
    m.provider!=='DHANHQ_V2'||m.dataClass!=='USER_LOCAL_CANDLES_UNVERIFIED'||
    m.researchPurpose!=='DEVELOPMENT_INTAKE_ONLY'||
    m.exchangeSegment!=='NSE_EQ'||m.instrument!=='EQUITY'||
    typeof m.securityId!=='string'||!/^\d{1,12}$/.test(m.securityId)||
    m.intervalMinutes!==1||!validDate(m.fromDate)||!validDate(m.toDate)||
    m.fromDate>m.toDate||m.fromDate<'2021-11-13'||
    m.supportTicketReference!=='DHAN_SUPPORT_6635943_2026-11-13'||
    m.corporateActionTreatment!=='BONUS_SPLIT_ADJUSTED_DIVIDENDS_UNKNOWN'||
    m.externalCalendarCertified!==false||
    m.sourceInstrumentMappingCertified!==false)
    throw Error('INVALID_LOCAL_DHAN_MANIFEST');
  const count=1+(dayMs(m.toDate)-dayMs(m.fromDate))/86400000;
  if(count>MAX_WINDOW_CALENDAR_DAYS)
    throw Error('OVERLONG_90_DAY_PROVIDER_WINDOW');
  return Object.freeze({...m});
}
function extractData(response){
  if(!record(response))throw Error('INVALID_DHAN_RESPONSE_ENVELOPE');
  // Accept documented direct parallel arrays, or SDK's {status,data} wrapper.
  if(FIELDS.every(k=>Array.isArray(response[k])))return response;
  if((response.status==='success'||response.status===true)&&
     record(response.data)&&FIELDS.every(k=>Array.isArray(response.data[k])))
    return response.data;
  throw Error('INVALID_DHAN_RESPONSE_ENVELOPE');
}
export function inspectDhanPrivateMinuteExport(response,manifest){
  const m=validateDhanLocalManifest(manifest);
  const data=extractData(response);
  const n=data.timestamp.length;
  if(!Number.isSafeInteger(n)||n<1||n>MAX_BARS||
    FIELDS.some(k=>!Array.isArray(data[k])||data[k].length!==n))
    throw Error('INVALID_DHAN_PARALLEL_ARRAYS');
  if(data.open_interest!==undefined&&
     (!Array.isArray(data.open_interest)||data.open_interest.length!==n||
      data.open_interest.some(x=>typeof x!=='number'||!Number.isFinite(x)||x<0)))
    throw Error('INVALID_DHAN_PARALLEL_ARRAYS');
  const groups=new Map();
  let previous=null;
  for(let i=0;i<n;i++){
    const t=data.timestamp[i];
    if(!Number.isSafeInteger(t)||t<1_600_000_000||t>2_000_000_000||
       t%ONE_MINUTE_SECONDS!==0)
      throw Error('INVALID_DHAN_TIMESTAMP');
    if(previous!==null&&t<=previous)
      throw Error('NONMONOTONIC_OR_DUPLICATE_DHAN_TIMESTAMP');
    previous=t;
    const d=istDatetime(t);
    if(d.second!==0)throw Error('INVALID_DHAN_TIMESTAMP');
    if(d.date<m.fromDate||d.date>m.toDate)
      throw Error('OUTSIDE_FROZEN_DATE_WINDOW');
    if(d.minute<DAY_START||d.minute>DAY_LAST)
      throw Error('OUTSIDE_REGULAR_NSE_SESSION');
    const [o,h,l,c]=['open','high','low','close'].map(k=>data[k][i]);
    const volume=data.volume[i];
    if(![o,h,l,c].every(x=>typeof x==='number'&&Number.isFinite(x)&&x>0)||
       h<Math.max(o,l,c)||l>Math.min(o,h,c)||
       !Number.isSafeInteger(volume)||volume<0)
      throw Error('INVALID_DHAN_OHLCV');
    if(!groups.has(d.date))groups.set(d.date,{first:d.minute,last:d.minute,
      count:0,volume:0,previousMinute:null,missingWithinSession:0});
    const g=groups.get(d.date);
    if(g.previousMinute!==null){
      if(d.minute<=g.previousMinute)
        throw Error('NONMONOTONIC_OR_DUPLICATE_DHAN_TIMESTAMP');
      g.missingWithinSession+=d.minute-g.previousMinute-1;
    }
    g.previousMinute=d.minute;g.last=d.minute;g.count++;g.volume+=volume;
  }
  let candidateComplete=0,incomplete=0,weekend=0,zeroVolume=0;
  const sessions=[];
  for(const [day,g] of groups){
    const w=weekday(day);
    const offCalendar=w===0||w===6;
    const hasCompleteShape=g.first===DAY_START&&g.last===DAY_LAST&&
      g.count===SESSION_BARS&&g.missingWithinSession===0;
    const state=offCalendar?'WEEKEND_OR_SPECIAL_SESSION_REVIEW':
      !hasCompleteShape?'PARTIAL_OR_MISSING_MINUTE_DATA':
      g.volume===0?'ZERO_VOLUME_INDIVIDUAL_REVIEW':
      'STRUCTURALLY_COMPLETE_CALENDAR_UNVERIFIED';
    if(offCalendar)weekend++;
    else if(!hasCompleteShape)incomplete++;
    else if(g.volume===0)zeroVolume++;
    else candidateComplete++;
    sessions.push({date:day,barCount:g.count,state});
  }
  let weekdaysNoBars=0;
  const observed=new Set(groups.keys());
  for(let ms=dayMs(m.fromDate);ms<=dayMs(m.toDate);ms+=86400000){
    const day=new Date(ms).toISOString().slice(0,10);
    if(![0,6].includes(weekday(day))&&!observed.has(day))weekdaysNoBars++;
  }
  // The public market calendar, special sessions, instrument listing history,
  // data rights and source integrity are NOT established by a local JSON file.
  return Object.freeze({...SAFETY,
    status:'LOCAL_DHAN_STRUCTURE_INSPECTED_EXTERNAL_REVIEW_BLOCKED_NO_TRADE',
    sourceClassification:'INSPECTED_DEVELOPMENT_NOT_UNSEEN_HOLDOUT',
    provider:'DHANHQ_V2',
    format:'PARALLEL_EPOCH_OPEN_TIMESTAMP_OHLCV_ARRAYS',
    candleOpenTimestampIst:true,
    requestedCalendarWindowDays:1+(dayMs(m.toDate)-dayMs(m.fromDate))/86400000,
    barsInspected:n,observedDistinctDates:groups.size,
    structurallyCompleteCandidateDates:candidateComplete,
    structurallyIncompleteDates:incomplete,
    weekendOrSpecialSessionDates:weekend,
    zeroVolumeCompleteShapeDates:zeroVolume,
    absentWeekdaysRequiringOfficialCalendarReconciliation:weekdaysNoBars,
    dataStructureValidated:true,
    providerSourceAndRequestAuthenticatedByThisTool:false,
    actualExchangeSessionsReconciled:false,
    completeHoldoutSessionsCertified:0,
    privateAggregateOnly:true,
    sessions
  });
}
function readPrivateJson(filename){
  if(typeof filename!=='string'||!path.isAbsolute(filename))
    throw Error('PRIVATE_INPUT_FILE_NOT_ABSOLUTE');
  let raw;
  try{
    const stat=fs.statSync(filename);
    if(!stat.isFile()||stat.size<2||stat.size>MAX_BYTES)
      throw Error('PRIVATE_INPUT_TOO_LARGE_OR_EMPTY');
    raw=fs.readFileSync(filename);
    if(raw.byteLength!==stat.size)throw Error('PRIVATE_INPUT_READ_FAILED');
  }catch(e){
    if(e?.message==='PRIVATE_INPUT_TOO_LARGE_OR_EMPTY')throw e;
    throw Error('PRIVATE_INPUT_READ_FAILED');
  }
  try{return {parsed:JSON.parse(raw.toString('utf8')),sha256:SHA256(raw)};}
  catch{throw Error('PRIVATE_INPUT_NOT_JSON');}
}
export function runPrivateDhanIntake(manifestAbsolutePath,privateResponseAbsolutePath){
  if(manifestAbsolutePath===privateResponseAbsolutePath)
    throw Error('PRIVATE_INPUT_FILES_IDENTICAL');
  // Manifest is read and validated BEFORE touching the private market-data file.
  const manifest=readPrivateJson(manifestAbsolutePath);
  const accepted=validateDhanLocalManifest(manifest.parsed);
  const historical=readPrivateJson(privateResponseAbsolutePath);
  return {...inspectDhanPrivateMinuteExport(historical.parsed,accepted),
    // Keep raw bars, actual prices, identity, paths and credentials PRIVATE.
    localManifestSha256:manifest.sha256,
    privateSourceSha256:historical.sha256};
}
const called=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(called){
  try{
    if(process.argv.length!==6||process.argv[2]!=='--manifest'||
      process.argv[4]!=='--private-response')
      throw Error('INVALID_CLI_ARGS');
    const result=runPrivateDhanIntake(process.argv[3],process.argv[5]);
    console.log(JSON.stringify(result,null,2));
  }catch(error){
    const reason=SAFE_CODES.has(error?.message)?error.message:
      'PRIVATE_DHAN_INTAKE_FAILED_UNVERIFIED';
    console.error(JSON.stringify({...SAFETY,
      status:'PRIVATE_DHAN_INTAKE_BLOCKED_NO_TRADE',reason}));
    process.exitCode=1;
  }
}
