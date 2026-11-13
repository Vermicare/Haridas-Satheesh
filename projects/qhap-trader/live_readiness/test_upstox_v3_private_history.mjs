import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {parseCompleteSession,simulateSession} from '../experiments/intraday_clock_replay.mjs';
import {
  validateRequest,createReadOnlyUrl,normalizeUpstoxCandles,
  buildLocalDevelopmentBatch,savePrivateDevelopmentBatch,
  fetchReadOnlyUpstoxHistory,parseLocalArgs
} from './upstox_v3_private_history.mjs';
const request={instrumentKey:'NSE_EQ|INE002A01018',symbol:'RELIANCE',
  from:'2025-01-06',to:'2025-01-10'};
const hhmm=n=>String(Math.floor(n/60)).padStart(2,'0')+':'+
  String(n%60).padStart(2,'0');
const stamp=(date,minute)=>date+'T'+hhmm(minute)+':00+05:30';
function rows(date='2025-01-06',omit=-1){
  const out=[];
  for(let minute=555;minute<=929;minute++){
    if(minute===omit)continue;
    out.push([stamp(date,minute),100,100.4,99.7,100.2,100,0]);
  }
  return out.reverse();
}
const packet=arr=>({status:'success',data:{candles:arr}});
const temp=t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-history-test-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  return dir;
};
test('exact read-only GET URL for NSE cash one-minute history, no orders',()=>{
  const url=createReadOnlyUrl(request);
  assert.equal(url,'https://api.upstox.com/v3/historical-candle/NSE_EQ%7CINE002A01018/minutes/1/2025-01-10/2025-01-06');
  assert.ok(!/order|place|modify|cancel/i.test(url));
});
test('only strict NSE EQ ISIN, safe symbols, one month and historical dates',()=>{
  assert.throws(()=>validateRequest({...request,instrumentKey:'NSE_FO|123'}),/INVALID_NSE/);
  assert.throws(()=>validateRequest({...request,symbol:'../secret'}),/INVALID_RESEARCH/);
  assert.throws(()=>validateRequest({...request,from:'2025-01-31',to:'2025-02-01'}),/OVERLONG/);
  assert.throws(()=>validateRequest({...request,from:'2025-02-31',to:'2025-02-31'}),/OVERLONG/);
  assert.throws(()=>validateRequest({...request,from:'2021-01-01',to:'2021-01-04'}),/OVERLONG/);
});
test('normalizes reversed vendor candles in ascending local IST chronology',()=>{
  const a=normalizeUpstoxCandles(packet(rows()),request);
  assert.equal(a.length,375);
  assert.equal(a[0].minute,555);
  assert.equal(a.at(-1).minute,929);
  assert.equal(a[0].date,'2025-01-06');
});
test('normalizes a complete day into existing generic offline replay schema',()=>{
  const a=buildLocalDevelopmentBatch(
    normalizeUpstoxCandles(packet(rows()),request),request);
  assert.equal(a.candlesticksSeen,375);
  assert.equal(a.sessions.length,1);
  assert.equal(a.sessions[0].candidateState,'CANDIDATE_COMPLETE_UNVERIFIED');
  assert.equal(a.sessions[0].missingRequiredMinutes,0);
  assert.deepEqual(a.eligible,[{date:'20250106',symbol:'RELIANCE'}]);
  assert.ok(a.sessions[0].csv.startsWith('RELIANCE,20250106,09:15,'));
  assert.equal(a.unknownWeekdays.length,4);
});
test('missing one regular minute is quarantined, never forward-filled',()=>{
  const arr=buildLocalDevelopmentBatch(normalizeUpstoxCandles(
    packet(rows('2025-01-06',700)),request),request);
  assert.equal(arr.sessions[0].candidateState,'INCOMPLETE_MINUTE_COVERAGE');
  assert.equal(arr.sessions[0].firstMissingRequiredMinute,'11:40');
  assert.equal(arr.eligible.length,0);
});
test('a 374-candle vendor day missing the 09:15 opening minute is NOT eligible',()=>{
  const batch=buildLocalDevelopmentBatch(
    normalizeUpstoxCandles(packet(rows('2025-01-06',555)),request),request);
  assert.equal(batch.candlesticksSeen,374);
  assert.equal(batch.sessions[0].openingMinutePresent,false);
  assert.equal(batch.sessions[0].expectedRegularSessionMinuteBars,375);
  assert.equal(batch.sessions[0].candidateState,'INCOMPLETE_MINUTE_COVERAGE');
  assert.equal(batch.sessions[0].missingRequiredMinutes,1);
  assert.equal(batch.sessions[0].firstMissingRequiredMinute,'09:15');
  assert.deepEqual(batch.eligible,[]);
  assert.throws(
    ()=>parseCompleteSession(batch.sessions[0].csv,'RELIANCE','20250106'),
    /MISSING_OPENING_MINUTE_09_15/);
});
test('a full source with 09:15 preserves unchanged 09:16-first replay features',()=>{
  const batch=buildLocalDevelopmentBatch(
    normalizeUpstoxCandles(packet(rows()),request),request);
  assert.equal(batch.sessions[0].openingMinutePresent,true);
  assert.equal(batch.sessions[0].expectedRegularSessionMinuteBars,375);
  assert.equal(parseCompleteSession(batch.sessions[0].csv,'RELIANCE','20250106').bars.length,374);
});

test('no vendor bars for a weekday are unknown, NOT invented zero return',()=>{
  const arr=buildLocalDevelopmentBatch(normalizeUpstoxCandles(
    packet([]),request),request);
  assert.equal(arr.eligible.length,0);
  assert.equal(arr.unknownWeekdays.length,5);
  assert.equal(arr.candlesticksSeen,0);
});
test('duplicate provider minute and malformed OHLC are rejected',()=>{
  const a=rows();
  assert.throws(()=>normalizeUpstoxCandles(packet([...a,a[0]]),request),
    /DUPLICATE_PROVIDER_CANDLE/);
  const b=rows();b[0][2]=80;
  assert.throws(()=>normalizeUpstoxCandles(packet(b),request),
    /INVALID_OHLCV/);
});
test('rejects timestamps without explicit India offset or outside date range',()=>{
  const a=rows();a[0][0]=a[0][0].replace('+05:30','Z');
  assert.throws(()=>normalizeUpstoxCandles(packet(a),request),/INVALID_OR_OUT_OF_RANGE/);
  const b=rows();b[0][0]='2025-01-11T15:29:00+05:30';
  assert.throws(()=>normalizeUpstoxCandles(packet(b),request),/INVALID_OR_OUT_OF_RANGE/);
});
test('rejects premarket/aftermarket minute and unsafe candle metadata',()=>{
  const a=rows();a[0][0]='2025-01-06T09:00:00+05:30';
  assert.throws(()=>normalizeUpstoxCandles(packet(a),request),/OUTSIDE_REGULAR/);
  const b=rows();b[0][5]=-1;
  assert.throws(()=>normalizeUpstoxCandles(packet(b),request),/INVALID_OHLCV/);
  assert.throws(()=>normalizeUpstoxCandles(packet({status:'error'}),request),/INVALID_UPSTOX/);
});
test('reads fixed-origin API with GET only using user-local read-only token',async()=>{
  const token='analytics-test-token-12345';
  let observed;
  const a=await fetchReadOnlyUpstoxHistory(request,token,async(url,options)=>{
    observed={url,method:options.method,authorization:options.headers.Authorization,
      redirect:options.redirect};
    return {ok:true,status:200,headers:{get:()=>null},text:async()=>JSON.stringify(packet(rows()))};
  });
  assert.equal(observed.method,'GET');
  assert.equal(observed.redirect,'error');
  assert.equal(observed.authorization,'Bearer '+token);
  assert.equal(a.eligible.length,1);
  assert.equal(JSON.stringify(a).includes(token),false);
});
test('server error and timeouts are sanitized, never print response bodies',async()=>{
  for(const response of [
    {ok:false,status:401,headers:{get:()=>null},text:async()=>'{SECRET_BEARER}'},
    {ok:false,status:429,headers:{get:()=>null},text:async()=>'{SECRET_BEARER}'}
  ])await assert.rejects(
    fetchReadOnlyUpstoxHistory(request,'analytics-test-token-12345',async()=>response),
    /UPSTOX_HISTORY_HTTP_(401|429)/);
  await assert.rejects(fetchReadOnlyUpstoxHistory(
    request,'analytics-test-token-12345',async()=>{throw Error('SECRET_BEARER');}),
    /UPSTOX_HISTORY_READ_ONLY_NETWORK_FAILURE/);
});
test('local private saving produces manifest and never writes into the code repository',t=>{
  const privateRoot=temp(t);
  const batch=buildLocalDevelopmentBatch(
    normalizeUpstoxCandles(packet(rows()),request),request);
  const out=savePrivateDevelopmentBatch(batch,privateRoot);
  assert.equal(out.status,'LOCAL_DEVELOPMENT_HISTORY_STORED_NOT_HOLDOUT');
  assert.equal(out.candidateCompleteDays,1);
  assert.equal(out.candlesStored,375);
  assert.equal(out.canTrade,false);
  const rowsSaved=fs.readFileSync(path.join(privateRoot,'historical','2025','01',
    '06','RELIANCE.csv'),'utf8');
  assert.equal(rowsSaved.split('\n').filter(Boolean).length,375);
  const manifest=JSON.parse(fs.readFileSync(out.manifest,'utf8'));
  assert.deepEqual(manifest,[{date:'20250106',symbol:'RELIANCE'}]);
  const audit=JSON.parse(fs.readFileSync(out.audit,'utf8'));
  assert.equal(audit.writtenEndUserPermissionIndependentlyVerified,false);
  assert.equal(audit.specificStrategyResearchFrozenBeforeDataInspection,false);
  assert.equal(audit.perDay[0].csv,undefined);
  assert.equal(out.rawPricesPrinted,false);
  assert.throws(()=>savePrivateDevelopmentBatch(batch,privateRoot),
    /PRIVATE_SOURCE_ALREADY_EXISTS_REFUSE_OVERWRITE/);
});
test('weekend bars do not silently become regular-session evaluated data',()=>{
  const req={...request,from:'2025-01-04',to:'2025-01-05'};
  const a=buildLocalDevelopmentBatch(normalizeUpstoxCandles(packet(
    rows('2025-01-04')),req),req);
  assert.equal(a.eligible.length,0);
  assert.equal(a.sessions[0].candidateState,'WEEKEND_REQUIRES_EXCHANGE_CALENDAR');
});
test('PowerShell argument format enforces 4 exact options',()=>{
  assert.deepEqual(parseLocalArgs([
    '--instrument','NSE_EQ|INE002A01018','--symbol','RELIANCE',
    '--from','2025-01-06','--to','2025-01-10'
  ]),request);
  assert.throws(()=>parseLocalArgs(['--symbol','RELIANCE']),/USAGE/);
  assert.throws(()=>parseLocalArgs([
    '--instrument','NSE_EQ|INE002A01018','--symbol','RELIANCE',
    '--from','2025-01-06','--from','2025-01-10'
  ]),/DUPLICATE/);
});


test('saved local minute rows bridge to existing chronology-first simulator, with no-trade baseline',t=>{
  const source=buildLocalDevelopmentBatch(normalizeUpstoxCandles(
    packet(rows()),request),request).sessions[0].csv;
  const parsed=parseCompleteSession(source,'RELIANCE','20250106');
  assert.equal(parsed.bars.length,374);
  assert.equal(parsed.bars[0].t,556);
  assert.equal(parsed.bars.at(-1).t,929);
  const noTrade=simulateSession(parsed,'NO_TRADE',{slippageBpsPerSide:15});
  assert.equal(noTrade.netRupees,0);
  assert.equal(noTrade.roundTrips,0);
  assert.equal(noTrade.terminalFlat,true);
});
