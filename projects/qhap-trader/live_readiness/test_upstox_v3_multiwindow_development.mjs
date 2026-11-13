import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {
 buildMultiYearDevelopmentPlan,runDevelopmentBatch,parseArgs
} from './upstox_v3_multiwindow_development.mjs';

const opts={instrumentKey:'NSE_EQ|INE002A01018',
 symbol:'RELIANCE',months:'2022-07,2023-07,2024-07,2025-07'};
const token='LOCAL_MOCK_READ_ONLY_ANALYTICS_TOKEN_123';
const privateDir=t=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-years-test-'));
 t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 return dir;
};
test('preview is network-free with exactly four bounded one-month windows',()=>{
 const p=buildMultiYearDevelopmentPlan(opts);
 assert.equal(p.status,'PREVIEW_READ_ONLY_DEVELOPMENT_MULTIYEAR_NO_NETWORK');
 assert.equal(p.requestsMade,0);
 assert.equal(p.requestsPlanned,4);
 assert.equal(p.noNetwork,true);
 assert.equal(p.noOrders,true);
 assert.equal(p.canTradeRealMoney,false);
 assert.equal(p.distinctCalendarYears,4);
 assert.equal(p.windows[0].from,'2022-07-01');
 assert.equal(p.windows[0].to,'2022-07-31');
 assert.equal(p.windows[2].to,'2024-07-31');
 assert.equal(p.researchClassification,'INSPECTED_DEVELOPMENT_NOT_FROZEN_HOLDOUT');
});
test('strict sorted month list disallows duplicates, malformed, cross-unsafe and >4',()=>{
 for(const months of [
  '2025-07','2022-07,2022-07',
  '2024-07,2023-07',
  '2022-01,2023-01,2024-01,2025-01,2026-01',
  '2021-12,2022-01','2023-00,2024-01','2027-01,2027-02',
  '2022-07;2023-07','../../secret,2025-07','2022-06, 2022-06'
 ])assert.throws(()=>buildMultiYearDevelopmentPlan({...opts,months}),/MONTHS/);
 assert.throws(()=>buildMultiYearDevelopmentPlan({...opts,symbol:'../HOME'}),/INVALID_RESEARCH_SYMBOL/);
});
test('fixed CLI named args parse and preserve no-secret plan',()=>{
 const {mode,plan}=parseArgs([
  '--preview','--instrument',opts.instrumentKey,'--symbol',
  opts.symbol,'--months',opts.months
 ]);
 assert.equal(mode,'--preview');
 assert.equal(plan.windows.length,4);
 assert.equal(JSON.stringify(plan).includes(token),false);
 assert.throws(()=>parseArgs(['--preview']),/USAGE_INVALID/);
});
test('four injected private monthly fetches create reproducible local aggregate manifest',async t=>{
 const root=privateDir(t);
 const plan=buildMultiYearDevelopmentPlan(opts);
 const calls=[];
 const result=await runDevelopmentBatch(plan,token,{
  privateRoot:root,pause:async()=>{},
  fetcher:async (window,provided)=>{
   calls.push({...window,provided});
   return {instrumentKey:window.instrumentKey,symbol:window.symbol,
     from:window.from,to:window.to,
     sessions:[{date:window.from,csv:'PRIVATE_FAKE_CSV',
       sha256:'a'.repeat(64),minuteBars:375,
       candidateState:'CANDIDATE_COMPLETE_UNVERIFIED',
       missingRequiredMinutes:0,firstMissingRequiredMinute:null}],
     eligible:[{date:window.from.replaceAll('-',''),
       symbol:window.symbol}],unknownWeekdays:[],candlesticksSeen:375};
  },
  saver:batch=>{
   const safePath=path.join(root,batch.from+'.json');
   fs.writeFileSync(safePath,JSON.stringify(batch.eligible));
   return {status:'LOCAL_DEVELOPMENT_HISTORY_STORED_NOT_HOLDOUT',
     candlesStored:375,candidateCompleteDays:1,
     weekdayDatesWithNoProviderBarsUnverified:0};
  }
 });
 assert.equal(calls.length,4);
 assert.ok(calls.every(x=>x.provided===token));
 assert.equal(result.status,'DEVELOPMENT_MULTIYEAR_BATCH_LOCAL_ONLY_COMPLETE');
 assert.equal(result.requestsAttempted,4);
 assert.equal(result.inputCandlesStored,1500);
 assert.equal(result.candidateCompleteDays,4);
 assert.equal(result.realOrdersSent,0);
 assert.equal(result.canTradeRealMoney,false);
 assert.equal(result.rawCandlesPrinted,false);
 assert.equal(result.estimatedRegimesIndependentlyVerified,false);
 const combined=JSON.parse(fs.readFileSync(result.combinedManifest,'utf8'));
 assert.equal(combined.length,4);
 assert.deepEqual(combined[0],{date:'20220701',symbol:'RELIANCE'});
 assert.equal(JSON.stringify(result).includes(token),false);
 assert.equal(JSON.stringify(result).includes('PRIVATE_FAKE_CSV'),false);
});
test('zero token and tampered plan fail before local API access',async()=>{
 const plan=buildMultiYearDevelopmentPlan(opts);
 let hits=0;
 await assert.rejects(runDevelopmentBatch(plan,'BAD',{
  fetcher:async()=>{hits++;}}),/INVALID_DEVELOPMENT/);
 assert.equal(hits,0);
 const forged={...plan,windows:[{...plan.windows[0],from:'wrong'},...plan.windows.slice(1)]};
 await assert.rejects(runDevelopmentBatch(forged,token,{
  fetcher:async()=>{hits++;}}),/INVALID/);
 assert.equal(hits,0);
});
test('month-2 network error blocks months 3 and 4 without leaking credentials',async t=>{
 const root=privateDir(t);
 let calls=0;
 const p=buildMultiYearDevelopmentPlan(opts);
 const r=await runDevelopmentBatch(p,token,{
  privateRoot:root,pause:async()=>{},
  fetcher:async w=>{
   calls++;
   if(calls===2)throw Error('SECRET_BEARER_NEVER_PRINT_THIS');
   return {instrumentKey:w.instrumentKey,symbol:w.symbol,
     from:w.from,to:w.to,eligible:[],sessions:[],
     unknownWeekdays:[],candlesticksSeen:0};
  },
  saver:()=>({status:'LOCAL_DEVELOPMENT_HISTORY_STORED_NOT_HOLDOUT',
   candlesStored:0,candidateCompleteDays:0,weekdayDatesWithNoProviderBarsUnverified:0})
 });
 assert.equal(calls,2);
 assert.equal(r.status,'DEVELOPMENT_BATCH_PARTIAL_HALT_NO_TRADE');
 assert.equal(r.monthCountCompleted,1);
 assert.equal(r.failedMonth,'2023-07');
 assert.equal(r.failureReason,'PRIVATE_DEVELOPMENT_REQUEST_FAILED');
 assert.equal(JSON.stringify(r).includes('SECRET_BEARER'),false);
 assert.equal(r.realOrdersSent,0);
});
test('existing private combined output stops before network request',async t=>{
 const root=privateDir(t),plan=buildMultiYearDevelopmentPlan(opts);
 const file=path.join(root,'manifests',
  'development-multiwindow-RELIANCE-2022-07_to_2025-07.json');
 fs.mkdirSync(path.dirname(file),{recursive:true});
 fs.writeFileSync(file,'[]');
 let hits=0;
 await assert.rejects(runDevelopmentBatch(plan,token,{
  privateRoot:root,fetcher:async()=>{hits++;}}
 ),/PRIVATE_BATCH_INDEX_ALREADY_EXISTS/);
 assert.equal(hits,0);
 assert.equal(fs.readFileSync(file,'utf8'),'[]');
});
test('does not certify untouched holdout or live edge on a four-year sample',async t=>{
 const root=privateDir(t);
 const p=buildMultiYearDevelopmentPlan(opts);
 const r=await runDevelopmentBatch(p,token,{
  privateRoot:root,pause:async()=>{},
  fetcher:async w=>({...w,eligible:[],sessions:[],
    candlesticksSeen:0,unknownWeekdays:[w.from]}),
  saver:()=>({status:'LOCAL_DEVELOPMENT_HISTORY_STORED_NOT_HOLDOUT',
    candlesStored:0,candidateCompleteDays:0,
    weekdayDatesWithNoProviderBarsUnverified:1})
 });
 assert.equal(r.status,'DEVELOPMENT_MULTIYEAR_NO_ELIGIBLE_SESSIONS');
 assert.equal(r.monthCountCompleted,4);
 assert.equal(r.tradingEdgeVerified,false);
 assert.equal(r.writtenEntitlementIndependentlyVerified,false);
 assert.equal(r.estimatedRegimesIndependentlyVerified,false);
 assert.equal(r.canTradeRealMoney,false);
});
