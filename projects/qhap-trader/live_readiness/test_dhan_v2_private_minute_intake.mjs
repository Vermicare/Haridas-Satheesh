import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {validateDhanLocalManifest,inspectDhanPrivateMinuteExport,
  runPrivateDhanIntake} from './dhan_v2_private_minute_intake.mjs';

const manifest=(overrides={})=>({
  provider:'DHANHQ_V2',
  dataClass:'USER_LOCAL_CANDLES_UNVERIFIED',
  researchPurpose:'DEVELOPMENT_INTAKE_ONLY',
  exchangeSegment:'NSE_EQ',instrument:'EQUITY',securityId:'1234',
  intervalMinutes:1,fromDate:'2026-11-12',toDate:'2026-11-12',
  supportTicketReference:'USER_PRIVATE_DHAN_SUPPORT_REPLY_2026-11-13',
  corporateActionTreatment:'BONUS_SPLIT_ADJUSTED_DIVIDENDS_UNKNOWN',
  externalCalendarCertified:false,sourceInstrumentMappingCertified:false,
  ...overrides
});
const fixture=(date='2026-11-12',length=375)=>{
  const first=Math.floor(Date.parse(date+'T03:45:00Z')/1000);
  const timestamp=Array.from({length},(_,i)=>first+i*60);
  const open=timestamp.map((_,i)=>100+i*.01);
  const high=open.map(x=>x+.02),low=open.map(x=>x-.02);
  const close=open.map(x=>x+.001),volume=open.map(()=>100);
  return {timestamp,open,high,low,close,volume,open_interest:open.map(()=>0)};
};
const inspect=(p=fixture(),m=manifest())=>inspectDhanPrivateMinuteExport(p,m);
const folder=t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-dhan-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  return dir;
};

test('Dhan one-minute documented epoch opening candles are structurally inspected',()=>{
  const v=inspect();
  assert.equal(v.status,'LOCAL_DHAN_STRUCTURE_INSPECTED_EXTERNAL_REVIEW_BLOCKED_NO_TRADE');
  assert.equal(v.barsInspected,375);
  assert.equal(v.structurallyCompleteCandidateDates,1);
  assert.equal(v.observedDistinctDates,1);
  assert.equal(v.candleOpenTimestampIst,true);
  assert.equal(v.completeHoldoutSessionsCertified,0);
  assert.equal(v.finalBrokerDecision,'NO_TRADE');
  assert.equal(v.realOrdersSent,0);
  assert.equal(v.networkRequestsMade,0);
  assert.equal(v.canTrade,false);
  assert.equal(v.strategyPerformanceTested,false);
});
test('SDK success envelope also accepted without trusting identity or rights',()=>{
  const v=inspect({status:'success',data:fixture()});
  assert.equal(v.providerSourceAndRequestAuthenticatedByThisTool,false);
  assert.equal(v.independentlyVerifiedNseEntitlement,false);
  assert.equal(v.independentlyVerifiedInstrumentMapping,false);
  assert.equal(v.barsInspected,375);
});
test('partial NSE minute coverage is visible and never a certified date',()=>{
  const p=fixture();
  for(const k of ['timestamp','open','high','low','close','volume','open_interest'])
    p[k].splice(155,1);
  const v=inspect(p);
  assert.equal(v.structurallyCompleteCandidateDates,0);
  assert.equal(v.structurallyIncompleteDates,1);
  assert.equal(v.sessions[0].state,'PARTIAL_OR_MISSING_MINUTE_DATA');
});
test('missing source weekdays never become zero-PnL sessions',()=>{
  const v=inspect(fixture(),manifest({fromDate:'2026-11-11'}));
  assert.equal(v.absentWeekdaysRequiringOfficialCalendarReconciliation,1);
  assert.equal(v.canMakeEconomicEdgeClaims,false);
  assert.equal(v.actualExchangeSessionsReconciled,false);
});
test('weekend cannot masquerade as a regular complete eligible session',()=>{
  const v=inspect(fixture('2026-11-14'),manifest({
    fromDate:'2026-11-14',toDate:'2026-11-14'}));
  assert.equal(v.weekendOrSpecialSessionDates,1);
  assert.equal(v.structurallyCompleteCandidateDates,0);
  assert.equal(v.sessions[0].state,'WEEKEND_OR_SPECIAL_SESSION_REVIEW');
});
test('zero-volume complete-looking day requires explicit review',()=>{
  const p=fixture();p.volume.fill(0);
  const v=inspect(p);
  assert.equal(v.zeroVolumeCompleteShapeDates,1);
  assert.equal(v.structurallyCompleteCandidateDates,0);
});
test('duplicate timestamps cannot be silently de-duplicated',()=>{
  const p=fixture();p.timestamp[3]=p.timestamp[2];
  assert.throws(()=>inspect(p),/NONMONOTONIC_OR_DUPLICATE_DHAN_TIMESTAMP/);
});
test('unsorted timestamps cannot be silently sorted',()=>{
  const p=fixture();[p.timestamp[4],p.timestamp[5]]=[p.timestamp[5],p.timestamp[4]];
  assert.throws(()=>inspect(p),/NONMONOTONIC_OR_DUPLICATE_DHAN_TIMESTAMP/);
});
test('wrong bar shape, prices, or missing volume reject',()=>{
  for(const change of [
    p=>p.volume.pop(),
    p=>p.high[0]=p.low[0]-.1,
    p=>p.open[2]=-1,
    p=>p.volume[4]=-9,
    p=>p.close[3]=Infinity,
    p=>p.timestamp[0]++,
    p=>p.timestamp[0]=1000000000
  ]){
    const p=fixture();change(p);
    assert.throws(()=>inspect(p));
  }
});
test('wrong date window or outside session is rejected',()=>{
  assert.throws(()=>inspect(fixture(),manifest({
    fromDate:'2026-11-13',toDate:'2026-11-13'
  })),/OUTSIDE_FROZEN_DATE_WINDOW/);
  const p=fixture();p.timestamp[0]-=60;
  assert.throws(()=>inspect(p),/OUTSIDE_REGULAR_NSE_SESSION/);
});
test('manifest blocks accidental live/holdout promotion, extra secret fields and 91-day requests',()=>{
  for(const change of [
    {researchPurpose:'HOLDOUT_UNSEEN'},
    {externalCalendarCertified:true},
    {sourceInstrumentMappingCertified:true},
    {clientId:'secret'},
    {provider:'UPSTOX'},
    {intervalMinutes:5},
    {toDate:'2027-03-01',fromDate:'2026-11-12'},
    {corporateActionTreatment:'ALL_ADJUSTED'},
    {securityId:'1234/secret'},
    {supportTicketReference:'APPROVED_FOR_LIVE'}
  ]) assert.throws(()=>validateDhanLocalManifest(manifest(change)));
});
test('raw source prices, IDs, tokens, and source paths are never emitted',()=>{
  const p=fixture();p.access_token='PRIVATE_TOKEN_DO_NOT_PRINT';
  const v=inspect({status:'success',data:p},manifest());
  const output=JSON.stringify(v);
  for(const item of ['PRIVATE_TOKEN_DO_NOT_PRINT','"open"','"high"','"close"',
    '"volume"','"securityId"','"clientId"','"access_token"']){
    assert.equal(output.includes(item),false,item);
  }
  assert.equal(v.canPublishProviderData,false);
  assert.equal(v.privateAggregateOnly,true);
});
test('CLI local-read-only intake emits hashes and no candles, without touching inputs',t=>{
  const root=folder(t);
  const a=path.join(root,'manifest.json'),b=path.join(root,'response.json');
  const rawManifest=JSON.stringify(manifest());
  const rawSource=JSON.stringify(fixture());
  fs.writeFileSync(a,rawManifest);fs.writeFileSync(b,rawSource);
  const beforeA=fs.readFileSync(a,'utf8'),beforeB=fs.readFileSync(b,'utf8');
  const r=runPrivateDhanIntake(a,b);
  assert.equal(r.privateSourceSha256.length,64);
  assert.equal(r.localManifestSha256.length,64);
  assert.equal(r.barsInspected,375);
  assert.equal(fs.readFileSync(a,'utf8'),beforeA);
  assert.equal(fs.readFileSync(b,'utf8'),beforeB);
  const out=execFileSync(process.execPath,[fileURLToPath(new URL(
    './dhan_v2_private_minute_intake.mjs',import.meta.url)),
    '--manifest',a,'--private-response',b],
    {encoding:'utf8',timeout:15000});
  assert.deepEqual(JSON.parse(out),r);
});
test('CLI refuses to read private market file when manifest invalid',t=>{
  const root=folder(t),a=path.join(root,'manifest.json'),b=path.join(root,'response.json');
  fs.writeFileSync(a,JSON.stringify(manifest({researchPurpose:'LIVE'})));
  fs.writeFileSync(b,JSON.stringify(fixture()));
  assert.throws(()=>runPrivateDhanIntake(a,b),/INVALID_LOCAL_DHAN_MANIFEST/);
  assert.throws(()=>runPrivateDhanIntake(b,b),/PRIVATE_INPUT_FILES_IDENTICAL/);
});
test('no market-data fetch, broker route or credentials exist in intake module',()=>{
  const source=fs.readFileSync(new URL('./dhan_v2_private_minute_intake.mjs',
    import.meta.url),'utf8');
  for(const forbidden of [
    'fetch(', 'WebSocket', 'https://api.dhan.co/',
    'access-token:','OPENROUTER_API_KEY','placeOrder(', 'axios',
    'submitOrder(', 'process.env.DHAN_ACCESS_TOKEN'
  ])assert.equal(source.includes(forbidden),false,forbidden);
});
