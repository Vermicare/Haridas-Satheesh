#!/usr/bin/env node
/**
 * QHAP-TRADER: user-local private audit-to-manifest completeness reconciliation.
 * Reads only source audit METADATA and date-only manifest, never raw NSE candles.
 * Verifies known holiday 2024-07-17 against NSE CMTR59722, but does not
 * pretend the entire exchange calendar or market data is independently verified.
 * No API requests, credentials, order routes or broker network.
 */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';

const DEFAULT_MONTHS=Object.freeze(['2022-07','2023-07','2024-07','2025-07']);
const DECLARED_NSE_CASH_HOLIDAYS=Object.freeze({
 '2024-07-17':'NSE/CMTR/59722_MOHARRAM'
});
const safeSymbol=s=>typeof s==='string'&&/^[A-Z][A-Z0-9&_-]{0,20}$/.test(s);
const isoDay=s=>typeof s==='string'&&/^\d{4}-\d\d-\d\d$/.test(s)&&
  !Number.isNaN(Date.parse(s+'T00:00:00Z'))&&
  new Date(s+'T00:00:00Z').toISOString().slice(0,10)===s;
const monthValid=s=>typeof s==='string'&&/^20\d\d-(0[1-9]|1[0-2])$/.test(s);
const withinMonth=(date,month)=>isoDay(date)&&date.slice(0,7)===month;
const weekdays=month=>{
 const [year,mm]=month.split('-').map(Number);
 const days=new Date(Date.UTC(year,mm,0)).getUTCDate();
 const result=[];
 for(let d=1;d<=days;d++){
   const date=month+'-'+String(d).padStart(2,'0');
   const w=new Date(date+'T00:00:00Z').getUTCDay();
   if(w!==0&&w!==6)result.push(date);
 }
 return result;
};
const fail=reason=>{throw Error(reason);};
const exactKeys=(obj,keys)=>obj&&typeof obj==='object'&&!Array.isArray(obj)&&
 keys.every(k=>Object.hasOwn(obj,k));
const isoCompact=s=>s.replaceAll('-','');

export function reconcilePrivateHistoryCoverage(
  root,{symbol='RELIANCE',months=DEFAULT_MONTHS}={}
){
 if(!safeSymbol(symbol)||!Array.isArray(months)||
   months.length<2||months.length>4||
   months.some((m,i)=>!monthValid(m)||(i>0&&m<=months[i-1]))||
   new Set(months).size!==months.length)
   fail('INVALID_AUDIT_SCOPE');
 const folder=path.join(root,'manifests');
 const combinedName='development-multiwindow-'+symbol+'-'+months[0]+
   '_to_'+months.at(-1)+'.json';
 const manifest=JSON.parse(fs.readFileSync(path.join(folder,combinedName),'utf8'));
 if(!Array.isArray(manifest)||manifest.length>150||manifest.some(e=>
   !e||Object.keys(e).sort().join(',')!=='date,symbol'||
   typeof e.date!=='string'||!/^\d{8}$/.test(e.date)||
   !safeSymbol(e.symbol)||e.symbol!==symbol))
   fail('INVALID_PRIVATE_CANDIDATE_MANIFEST');
 const manifestDates=manifest.map(x=>x.date);
 if(new Set(manifestDates).size!==manifestDates.length)
   fail('DUPLICATE_PRIVATE_CANDIDATE_DATE');
 const candidateDates=new Set(),seenDates=new Set();
 const excluded=[],calendarClosures=[],unknownWeekdays=[],monthly=[];
 let totalRows=0,totalRequiredGaps=0,optionalOpeningGaps=0;
 for(const month of months){
   const [y,m]=month.split('-').map(Number);
   const last=new Date(Date.UTC(y,m,0)).getUTCDate();
   const auditFile=path.join(folder,'development-'+symbol+'-'+month+
     '-01-to-'+month+'-'+String(last).padStart(2,'0')+'.audit.json');
   const audit=JSON.parse(fs.readFileSync(auditFile,'utf8'));
   if(!exactKeys(audit,['kind','requestedFrom','requestedTo','perDay',
      'excludedUnknownWeekdays'])||
      audit.kind!=='QHAP_LOCAL_DEVELOPMENT_ONLY_UNVERIFIED'||
      audit.requestedFrom!==month+'-01'||
      audit.requestedTo!==month+'-'+String(last).padStart(2,'0')||
      !Array.isArray(audit.perDay)||!Array.isArray(audit.excludedUnknownWeekdays))
     fail('INVALID_OR_MISMATCHED_PRIVATE_AUDIT');
   const expected=weekdays(month),expectedSet=new Set(expected);
   const observed=new Set();
   let candidates=0,incomplete=0,monthRows=0;
   for(const row of audit.perDay){
     if(!row||!withinMonth(row.date,month)||row.symbol!==symbol||
        !Number.isSafeInteger(row.minuteBars)||row.minuteBars<0||
        row.minuteBars>375||!Number.isSafeInteger(row.missingRequiredMinutes)||
        row.missingRequiredMinutes<0||row.missingRequiredMinutes>374||
        !/^[a-f0-9]{64}$/i.test(row.sha256||'')||
        typeof row.candidateState!=='string'||
        !['CANDIDATE_COMPLETE_UNVERIFIED',
         'INCOMPLETE_MINUTE_COVERAGE',
         'WEEKEND_REQUIRES_EXCHANGE_CALENDAR',
         'ZERO_VOLUME_NO_EXECUTION_EVIDENCE'].includes(row.candidateState))
       fail('INVALID_PRIVATE_AUDIT_DAY');
     if(observed.has(row.date)||seenDates.has(row.date))
       fail('DUPLICATE_AUDIT_DAY');
     observed.add(row.date);seenDates.add(row.date);
     monthRows+=row.minuteBars;
     if(!expectedSet.has(row.date)){
       if(row.candidateState!=='WEEKEND_REQUIRES_EXCHANGE_CALENDAR')
         fail('UNREVIEWED_WEEKEND_OR_EXTRA_SESSION');
       excluded.push({date:row.date,reason:'WEEKEND_REQUIRES_EXCHANGE_CALENDAR',
         missingRequiredMinutes:row.missingRequiredMinutes,
         firstMissingRequiredMinute:row.firstMissingRequiredMinute??null});
       continue;
     }
     const openingMissing=375-row.minuteBars-row.missingRequiredMinutes;
     if(openingMissing<0||openingMissing>1)
       fail('CANDLE_COUNT_INCONSISTENT_WITH_REQUIRED_MINUTES');
     totalRequiredGaps+=row.missingRequiredMinutes;
     optionalOpeningGaps+=openingMissing;
     if(row.candidateState==='CANDIDATE_COMPLETE_UNVERIFIED'){
       if(row.missingRequiredMinutes!==0)
         fail('CANDIDATE_WITH_MISSING_MINUTES');
       candidates++;candidateDates.add(isoCompact(row.date));
     }else{
       incomplete++;
       excluded.push({date:row.date,reason:row.candidateState,
         missingRequiredMinutes:row.missingRequiredMinutes,
         firstMissingRequiredMinute:row.firstMissingRequiredMinute??null});
     }
   }
   const missing=expected.filter(date=>!observed.has(date));
   const declared=audit.excludedUnknownWeekdays;
   if(declared.some(x=>!withinMonth(x,month))||
      new Set(declared).size!==declared.length||
      declared.length!==missing.length||
      declared.some(x=>!missing.includes(x)))
     fail('MISSING_WEEKDAY_AUDIT_MISMATCH');
   for(const date of missing){
     if(Object.hasOwn(DECLARED_NSE_CASH_HOLIDAYS,date)){
       calendarClosures.push({date,
         source:DECLARED_NSE_CASH_HOLIDAYS[date]});
     }else unknownWeekdays.push(date);
   }
   totalRows+=monthRows;
   monthly.push({month,weekdays:expected.length,observedDays:observed.size,
     candidateCompleteDays:candidates,incompleteDays:incomplete,
     missingWeekdays:missing.length,storedCandles:monthRows});
 }
 if(candidateDates.size!==manifestDates.length||
    manifestDates.some(x=>!candidateDates.has(x)))
   fail('PRIVATE_MANIFEST_DOES_NOT_MATCH_AUDITS');
 const weekdayTotal=monthly.reduce((sum,x)=>sum+x.weekdays,0);
 const candidateTotal=candidateDates.size;
 const regularExpected=weekdayTotal-calendarClosures.length-
   unknownWeekdays.length;
 const incompleteRegular=excluded.filter(x=>
   x.reason!=='WEEKEND_REQUIRES_EXCHANGE_CALENDAR').length;
 if(candidateTotal+incompleteRegular!==regularExpected)
   fail('SOURCE_COVERAGE_ACCOUNTING_INCOMPLETE');
 return {
   status:'PRIVATE_METADATA_COVERAGE_RECONCILED_NOT_PROFIT_EVIDENCE',
   symbol,months:[...months],calendarVerificationScope:
     'PINNED_NSE_2024_07_17_CIRCULAR_ONLY_NOT_FULL_CALENDAR',
   weekdayCount:weekdayTotal,
   independentlyPinnedHolidayCount:calendarClosures.length,
   pinnedExchangeClosures:calendarClosures,
   unverifiedAbsentWeekdayCount:unknownWeekdays.length,
   unverifiedAbsentWeekdays:unknownWeekdays,
   incompleteSourceSessions:incompleteRegular,
   excludedSourceDays:excluded,
   eligibleCandidateDays:candidateTotal,
   eligibleManifestDatesMatchAudit:true,
   expectedTradingWeekdaysAfterPinnedClosures:regularExpected,
   completenessRatioOfKnownWeekdays:Number(
     (candidateTotal/Math.max(regularExpected,1)).toFixed(6)),
   missingRequiredMinutesAcrossIncompleteAndCandidateDays:totalRequiredGaps,
   missing0915OpeningMinutesInObservedRegularDays:optionalOpeningGaps,
   candleRowsRecordedInAudits:totalRows,monthly,
   allExchangeSessionsIndependentlyVerified:false,
   sourceDataEntitlementIndependentlyVerified:false,
   researchClassification:'INSPECTED_DEVELOPMENT_ONLY_NOT_HOLDOUT',
   rawCandlesRead:false,rawPricesPrinted:false,credentialsRead:false,
   networkRequests:0,realOrdersSent:0,canTradeRealMoney:false
 };
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
 try{
   if(process.argv.length!==3||process.argv[2]!=='--audit-private-development')
     fail('USAGE_REQUIRE_AUDIT_PRIVATE_DEVELOPMENT');
   const root=path.join(os.homedir(),'QHAP-TRADER-PRIVATE');
   console.log(JSON.stringify(reconcilePrivateHistoryCoverage(root),null,2));
 }catch(e){
   const reason=/^(INVALID_|DUPLICATE_|UNREVIEWED_|CANDLE_|CANDIDATE_|MISSING_|PRIVATE_|SOURCE_|USAGE_)/.test(
      e?.message||'')?'PRIVATE_METADATA_AUDIT_INVALID_OR_MISSING':
     'PRIVATE_METADATA_AUDIT_FAILED_NO_TRADE';
   console.error(JSON.stringify({status:'PRIVATE_COVERAGE_AUDIT_BLOCKED',
     reason,noNetwork:true,realOrdersSent:0,canTradeRealMoney:false},null,2));
   process.exitCode=1;
 }
}
