import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {reconcilePrivateHistoryCoverage} from './private_history_coverage_reconcile.mjs';

const months=['2022-07','2023-07','2024-07','2025-07'];
const weekdays=month=>{
 const [y,m]=month.split('-').map(Number),last=new Date(Date.UTC(y,m,0)).getUTCDate();
 return Array.from({length:last},(_,i)=>month+'-'+String(i+1).padStart(2,'0'))
   .filter(date=>![0,6].includes(new Date(date+'T00:00:00Z').getUTCDay()));
};
const gaps=new Map([
 ['2023-07-12',{count:1,first:'14:57',omit0915:true}],
 ['2023-07-20',{count:44,first:'09:16'}],
 ['2023-07-24',{count:3,first:'12:49'}]
]);
function make(t){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-private-coverage-'));
 const manifests=path.join(root,'manifests');
 fs.mkdirSync(manifests,{recursive:true});
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const candidates=[];
 const audits={};
 for(const month of months){
   const days=weekdays(month),perDay=[];
   for(const date of days){
     if(date==='2024-07-17')continue;
     const defect=gaps.get(date),n=defect?.count??0;
     const row={date,symbol:'RELIANCE',minuteBars:375-n-
       (defect?.omit0915?1:0),missingRequiredMinutes:n,
       firstMissingRequiredMinute:defect?.first??null,
       candidateState:n?'INCOMPLETE_MINUTE_COVERAGE':
         'CANDIDATE_COMPLETE_UNVERIFIED',
       sha256:'a'.repeat(64)};
     perDay.push(row);
     if(!n)candidates.push({date:date.replaceAll('-',''),symbol:'RELIANCE'});
   }
   // Do not infer date boundaries from fake market bars.
   const [y,m]=month.split('-').map(Number);
   const requestedTo=month+'-'+String(new Date(Date.UTC(y,m,0)).getUTCDate()).padStart(2,'0');
   const name='development-RELIANCE-'+month+'-01-to-'+requestedTo+'.audit.json';
   const audit={kind:'QHAP_LOCAL_DEVELOPMENT_ONLY_UNVERIFIED',
     requestedFrom:month+'-01',requestedTo,
     perDay,excludedUnknownWeekdays:month==='2024-07'?['2024-07-17']:[]};
   audits[month]=path.join(manifests,name);
   fs.writeFileSync(audits[month],JSON.stringify(audit));
 }
 const manifest=path.join(manifests,
   'development-multiwindow-RELIANCE-2022-07_to_2025-07.json');
 fs.writeFileSync(manifest,JSON.stringify(candidates));
 return {root,manifests,manifest,audits,candidates};
}
test('reconciles actual user-supplied four-month metadata totals with 84 eligible days',t=>{
 const f=make(t),out=reconcilePrivateHistoryCoverage(f.root);
 assert.equal(out.status,'PRIVATE_METADATA_COVERAGE_RECONCILED_NOT_PROFIT_EVIDENCE');
 assert.equal(out.weekdayCount,88);
 assert.equal(out.independentlyPinnedHolidayCount,1);
 assert.deepEqual(out.pinnedExchangeClosures,
   [{date:'2024-07-17',source:'NSE/CMTR/59722_MOHARRAM'}]);
 assert.equal(out.unverifiedAbsentWeekdayCount,0);
 assert.equal(out.incompleteSourceSessions,3);
 assert.equal(out.eligibleCandidateDays,84);
 assert.equal(out.expectedTradingWeekdaysAfterPinnedClosures,87);
 assert.equal(out.completenessRatioOfKnownWeekdays,Number((84/87).toFixed(6)));
 assert.equal(out.missingRequiredMinutesAcrossIncompleteAndCandidateDays,48);
 assert.equal(out.missing0915OpeningMinutesInObservedRegularDays,1);
 assert.equal(out.candleRowsRecordedInAudits,32576);
 assert.deepEqual(out.monthly.map(x=>x.candidateCompleteDays),[21,18,22,23]);
 assert.deepEqual(out.monthly.map(x=>x.storedCandles),[7875,7826,8250,8625]);
 assert.equal(out.rawCandlesRead,false);
 assert.equal(out.networkRequests,0);
 assert.equal(out.realOrdersSent,0);
 assert.equal(out.canTradeRealMoney,false);
});
test('metadata excluded days preserve original 1/44/3 missing-minute flags',t=>{
 const f=make(t),out=reconcilePrivateHistoryCoverage(f.root);
 assert.deepEqual(out.excludedSourceDays,[
  {date:'2023-07-12',reason:'INCOMPLETE_MINUTE_COVERAGE',
    missingRequiredMinutes:1,firstMissingRequiredMinute:'14:57'},
  {date:'2023-07-20',reason:'INCOMPLETE_MINUTE_COVERAGE',
    missingRequiredMinutes:44,firstMissingRequiredMinute:'09:16'},
  {date:'2023-07-24',reason:'INCOMPLETE_MINUTE_COVERAGE',
    missingRequiredMinutes:3,firstMissingRequiredMinute:'12:49'}
 ]);
});
test('manifest tampering or unexpected extra date fails rather than silently passing',t=>{
 const f=make(t);
 const list=JSON.parse(fs.readFileSync(f.manifest,'utf8'));
 list.pop();
 fs.writeFileSync(f.manifest,JSON.stringify(list));
 assert.throws(()=>reconcilePrivateHistoryCoverage(f.root),
   /PRIVATE_MANIFEST_DOES_NOT_MATCH_AUDITS/);
 list.push({date:'20220701',symbol:'RELIANCE'});
 fs.writeFileSync(f.manifest,JSON.stringify(list));
 assert.throws(()=>reconcilePrivateHistoryCoverage(f.root),
   /DUPLICATE_PRIVATE_CANDIDATE_DATE/);
});
test('unrecognized missing weekday remains unverified, not exchange holiday',t=>{
 const f=make(t);
 const july=JSON.parse(fs.readFileSync(f.audits['2023-07'],'utf8'));
 july.perDay=july.perDay.filter(x=>x.date!=='2023-07-11');
 july.excludedUnknownWeekdays.push('2023-07-11');
 fs.writeFileSync(f.audits['2023-07'],JSON.stringify(july));
 fs.writeFileSync(f.manifest,JSON.stringify(f.candidates.filter(x=>x.date!=='20230711')));
 const out=reconcilePrivateHistoryCoverage(f.root);
 assert.equal(out.unverifiedAbsentWeekdayCount,1);
 assert.deepEqual(out.unverifiedAbsentWeekdays,['2023-07-11']);
 assert.equal(out.independentlyPinnedHolidayCount,1);
 assert.equal(out.eligibleCandidateDays,83);
 assert.equal(out.allExchangeSessionsIndependentlyVerified,false);
});
test('undeclared absent weekday or malformed audit blocks research',t=>{
 const f=make(t);
 const audit=JSON.parse(fs.readFileSync(f.audits['2024-07'],'utf8'));
 audit.excludedUnknownWeekdays=[];
 fs.writeFileSync(f.audits['2024-07'],JSON.stringify(audit));
 assert.throws(()=>reconcilePrivateHistoryCoverage(f.root),
   /MISSING_WEEKDAY_AUDIT_MISMATCH/);
});
test('inconsistent day bar count vs missing minute totals fails closed',t=>{
 const f=make(t);
 const audit=JSON.parse(fs.readFileSync(f.audits['2023-07'],'utf8'));
 const row=audit.perDay.find(x=>x.date==='2023-07-20');
 row.minuteBars=100;
 fs.writeFileSync(f.audits['2023-07'],JSON.stringify(audit));
 assert.throws(()=>reconcilePrivateHistoryCoverage(f.root),
   /CANDLE_COUNT_INCONSISTENT_WITH_REQUIRED_MINUTES/);
});
test('candidate incorrectly marked complete when regular minute missing is rejected',t=>{
 const f=make(t);
 const audit=JSON.parse(fs.readFileSync(f.audits['2023-07'],'utf8'));
 const row=audit.perDay.find(x=>x.date==='2023-07-12');
 row.candidateState='CANDIDATE_COMPLETE_UNVERIFIED';
 fs.writeFileSync(f.audits['2023-07'],JSON.stringify(audit));
 assert.throws(()=>reconcilePrivateHistoryCoverage(f.root),
   /CANDIDATE_WITH_MISSING_MINUTES/);
});
test('invalid scope, duplicated source day and raw extra fields rejected',t=>{
 const f=make(t);
 assert.throws(()=>reconcilePrivateHistoryCoverage(f.root,{
   symbol:'../secret',months}),/INVALID_AUDIT_SCOPE/);
 const audit=JSON.parse(fs.readFileSync(f.audits['2022-07'],'utf8'));
 audit.perDay.push({...audit.perDay[0]});
 fs.writeFileSync(f.audits['2022-07'],JSON.stringify(audit));
 assert.throws(()=>reconcilePrivateHistoryCoverage(f.root),
   /DUPLICATE_AUDIT_DAY/);
});
test('coverage audit remains metadata-only; not a backtest or broker licence',t=>{
 const f=make(t),out=reconcilePrivateHistoryCoverage(f.root);
 assert.equal(out.researchClassification,'INSPECTED_DEVELOPMENT_ONLY_NOT_HOLDOUT');
 assert.equal(out.sourceDataEntitlementIndependentlyVerified,false);
 assert.equal(out.allExchangeSessionsIndependentlyVerified,false);
 assert.equal(out.credentialsRead,false);
 assert.equal(out.rawPricesPrinted,false);
 assert.ok(!JSON.stringify(out).includes('100.0,110.0,90.0'));
 assert.equal(out.canTradeRealMoney,false);
});
