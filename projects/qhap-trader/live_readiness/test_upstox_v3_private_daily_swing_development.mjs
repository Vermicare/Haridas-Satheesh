import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {
  validateDailyWindow,previewDailyWindow,historyDailyUrl,
  validateAndSortDaily,fetchUpstoxPrivateDaily,runPrivateDailyResearch
} from './upstox_v3_private_daily_swing_development.mjs';
import {syntheticEquityFixture}
 from './nse_swing_interdependent_agent_network.mjs';

const request={
  instrumentKey:'NSE_EQ|INE002A01018',symbol:'RELIANCE',
  from:'2024-01-01',to:'2024-11-30'
};
const token='PRIVATE_READ_ONLY_TEST_ANALYTICS_TOKEN_123456';
const goodRows=()=>syntheticEquityFixture().dailyBars.map(x=>[
  x.date+'T00:00:00+05:30',x.open,x.high,x.low,
  x.close,Math.round(x.volume),0
]).reverse();
const goodPacket=()=>({status:'success',data:{candles:goodRows()}});
const mockResponse=packet=>({ok:true,status:200,
  headers:{get:()=>null},text:async()=>JSON.stringify(packet)});
const localDir=t=>{
  const p=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-daily-'));
  t.after(()=>fs.rmSync(p,{recursive:true,force:true}));
  return p;
};
test('preview is pure zero-network with strict one-year development scope',()=>{
 const p=previewDailyWindow(request);
 assert.equal(p.status,'PRIVATE_DAILY_RESEARCH_PREVIEW_NO_NETWORK');
 assert.equal(p.requestsAttempted,0);
 assert.equal(p.readsToken,false);
 assert.equal(p.brokerOrderRoutePresent,false);
 assert.equal(p.datasetClassification,'INSPECTED_DEVELOPMENT_NOT_UNSEEN_HOLDOUT');
 assert.equal(historyDailyUrl(request),
  'https://api.upstox.com/v3/historical-candle/NSE_EQ%7CINE002A01018/days/1/2024-11-30/2024-01-01');
});
test('only exact NSE cash instrument, valid range and one-year dates accepted',()=>{
 for(const args of [
  {...request,instrumentKey:'NSE_FO|INE002A01018'},
  {...request,symbol:'../secret'},
  {...request,to:'2023-12-31'},
  {...request,to:'2025-12-31'},
  {...request,from:'2019-12-01'},
  {...request,from:'2024-02-30'},
  {...request,to:'2027-01-01'}
 ])assert.throws(()=>validateDailyWindow(args),/INVALID_PRIVATE_DAILY/);
});
test('daily candle normalization reverses API descending order without guessing prices',()=>{
 const rows=validateAndSortDaily(goodPacket(),request);
 assert.equal(rows.length,100);
 assert.equal(rows[0].date,'2024-01-01');
 assert.equal(rows[0].open,goodRows().at(-1)[1]);
 assert.equal(rows.at(-1).date,syntheticEquityFixture().dailyBars.at(-1).date);
});
test('mock authenticated historical URL uses ONLY GET, Bearer header and redirect error',async()=>{
 let requests=0;
 const rows=await fetchUpstoxPrivateDaily(request,token,async(url,options)=>{
   requests++;
   assert.equal(url,historyDailyUrl(request));
   assert.equal(options.method,'GET');
   assert.equal(options.redirect,'error');
   assert.equal(options.headers.Authorization,'Bearer '+token);
   assert.equal(options.body,undefined);
   return mockResponse(goodPacket());
 });
 assert.equal(requests,1);
 assert.equal(rows.length,100);
});
test('missing token blocked BEFORE even read-only HTTP request',async()=>{
 let hits=0;
 await assert.rejects(fetchUpstoxPrivateDaily(request,'bad',async()=>{
   hits++;return mockResponse(goodPacket());
 }),/INVALID_LOCAL_ANALYTICS_TOKEN/);
 assert.equal(hits,0);
});
test('network errors are sanitized and never retried or print token',async()=>{
 let hits=0;
 await assert.rejects(fetchUpstoxPrivateDaily(request,token,async()=>{
   hits++;throw Error('BEARER '+token);
 }),/DAILY_NETWORK_OUTCOME_UNKNOWN_NO_RETRY/);
 assert.equal(hits,1);
});
test('HTTP error does not return server-provided raw market payload or credential',async()=>{
 let hits=0;
 await assert.rejects(fetchUpstoxPrivateDaily(request,token,async()=>{
  hits++;return {ok:false,status:429,body:'VERY PRIVATE'};
 }),/UPSTOX_DAILY_HTTP_429/);
 assert.equal(hits,1);
});
test('duplicate day and future/out of range date are rejected',()=>{
 for(const mutate of [
  rows=>rows[1][0]=rows[0][0],
  rows=>rows[0][0]='2025-01-02T00:00:00+05:30',
  rows=>rows[0][1]=NaN,
  rows=>rows[0][3]=-5,
  rows=>rows[0][5]=-10
 ]){
  const rows=goodRows(); mutate(rows);
  assert.throws(()=>validateAndSortDaily({
    status:'success',data:{candles:rows}
  },request),/INVALID_OR_DUPLICATE_DAILY_CANDLE/);
 }
});
test('bad response shape and fewer than 80 daily bars stop rather than forward-fill',()=>{
 assert.throws(()=>validateAndSortDaily({status:'success',data:{candles:[]}},request),
  /NOT_ENOUGH_OR_EXCESSIVE_DAILY_BARS_FOR_RESEARCH/);
 assert.throws(()=>validateAndSortDaily({status:'fail',data:{candles:goodRows()}},request),
  /INVALID_UPSTOX_DAILY_RESPONSE/);
 const rows=goodRows().slice(0,70);
 assert.throws(()=>validateAndSortDaily({status:'success',data:{candles:rows}},request),
  /NOT_ENOUGH_OR_EXCESSIVE_DAILY_BARS_FOR_RESEARCH/);
});
test('private daily research bridge stores only in temp private root and returns sanitized summary',async t=>{
 const root=localDir(t);
 let called=0;
 const result=await runPrivateDailyResearch(request,token,{
  root,fetcher:async(req,key)=>{
   called++;assert.deepEqual(req,request);assert.equal(key,token);
   return validateAndSortDaily(goodPacket(),request);
  }
 });
 assert.equal(called,1);
 assert.equal(result.status,'PRIVATE_DAILY_DEVELOPMENT_STORED_AND_AGENT_RESEARCH_RUN');
 assert.equal(result.dailyBarsStored,100);
 assert.equal(result.agentDecision,'NO_TRADE');
 assert.equal(result.agentAuditValid,true);
 assert.equal(result.realOrdersSent,0);
 assert.equal(result.brokerOrderRoutePresent,false);
 assert.equal(result.realizedReturnsOrProfitsDemonstrated,false);
 assert.ok(result.localPrivateFile.startsWith(root));
 assert.ok(fs.existsSync(result.localPrivateFile));
 const stored=JSON.parse(fs.readFileSync(result.localPrivateFile,'utf8'));
 assert.equal(stored.sourceClass,'PRIVATE_REPLAY');
 assert.equal(stored.dailyBars.length,100);
 assert.equal(stored.costAssumptions.sourceScheduleIndependentlyVerified,false);
 assert.equal(JSON.stringify(result).includes('PRIVATE_READ_ONLY_TEST'),false);
 assert.equal(JSON.stringify(result).includes('500000'),false);
});
test('refuse overwrite before fetching private provider data',async t=>{
 const root=localDir(t);
 const opts={root,fetcher:async()=>validateAndSortDaily(goodPacket(),request)};
 await runPrivateDailyResearch(request,token,opts);
 let times=0;
 await assert.rejects(runPrivateDailyResearch(request,token,{
   root,fetcher:async()=>{times++;return [];}
 }),/PRIVATE_DAILY_RESEARCH_ALREADY_EXISTS_NO_OVERWRITE/);
 assert.equal(times,0);
});
test('no network or broker/crypto orders exist in source code',async()=>{
 const s=fs.readFileSync(new URL('./upstox_v3_private_daily_swing_development.mjs',import.meta.url),'utf8');
 assert.equal(s.includes('https://api-hft.upstox.com'),false);
 assert.equal(s.includes('https://api-sandbox.upstox.com'),false);
 assert.equal(s.includes('UPSTOX_SANDBOX_ACCESS_TOKEN'),false);
 assert.equal(s.includes('BTC-USDT'),false);
});
