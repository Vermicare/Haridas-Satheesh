import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {inspectPublicThirdPartyMinuteCsv,auditLocalThirdPartyCsvFile}
  from './audit_public_third_party_minute_csv.mjs';

const DATE='2022-01-03',SYMBOL='RELIANCE';
const fmt=n=>String(Math.floor(n/60)).padStart(2,'0')+':'+
  String(n%60).padStart(2,'0');
const make=({
  date='20220103',symbol='RELIANCE',start=555,end=929,pre=[],
  post=[],skip=[],zeroVolume=[],badRow=null
}={})=>{
  const skipped=new Set(skip),zeros=new Set(zeroVolume);
  const minutes=[...pre,...Array.from({length:end-start+1},(_,i)=>start+i)
    .filter(i=>!skipped.has(i)),...post];
  const rows=minutes.map((m,i)=>[
    symbol,date,fmt(m),'100.00','100.10','99.90','100.05',
    zeros.has(m)?'0':'100','0'
  ].join(','));
  if(badRow)rows[0]=badRow;
  return rows.join('\n')+'\n';
};
const inspect=(csv,override={})=>inspectPublicThirdPartyMinuteCsv(csv,{
  expectedSymbol:SYMBOL,expectedDate:DATE,...override
});
const temp=t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-public-csv-'));
  t.after(()=>fs.rmSync(dir,{force:true,recursive:true}));
  return dir;
};

test('complete synthetic session is a mere structural candidate, never holdout',()=>{
  const v=inspect(make());
  assert.equal(v.totalRows,375);
  assert.equal(v.observedRegularSessionMinuteRows,375);
  assert.equal(v.missingRegularSessionMinutes,0);
  assert.equal(v.openingMinutePresent,true);
  assert.equal(v.closingMinutePresent,true);
  assert.equal(v.candidateRegularSessionShapeComplete,true);
  assert.equal(v.certifiedCompleteTradingSessions,0);
  assert.equal(v.genuineUnseenHoldoutSessions,0);
  assert.equal(v.sourceRightsIndependentlyVerified,false);
  assert.equal(v.canTrade,false);
  assert.equal(v.canPlacePaperOrders,false);
  assert.equal(v.networkRequestsMade,0);
  assert.equal(v.finalBrokerDecision,'NO_TRADE');
});
test('replicated GitHub 2022 sample shape flags missing crucial 09:15 minute',()=>{
  const v=inspect(make({pre:[548],post:[930,931,932,933,934],skip:[555]}));
  assert.equal(v.totalRows,380);
  assert.equal(v.observedRegularSessionMinuteRows,374);
  assert.equal(v.preOpeningSessionRows,1);
  assert.equal(v.afterRegularSessionRows,5);
  assert.equal(v.missingRegularSessionMinutes,1);
  assert.equal(v.firstMissingRegularMinuteIst,'09:15');
  assert.equal(v.openingMinutePresent,false);
  assert.equal(v.candidateRegularSessionShapeComplete,false);
});
test('an interior gap never becomes a made-up completed candle',()=>{
  const v=inspect(make({skip:[610]}));
  assert.equal(v.missingRegularSessionMinutes,1);
  assert.equal(v.firstMissingRegularMinuteIst,'10:10');
  assert.equal(v.candidateRegularSessionShapeComplete,false);
});
test('a weekend full-shape file needs independent special-session review',()=>{
  const v=inspect(make({date:'20220108'}),{expectedDate:'2022-01-08'});
  assert.equal(v.weekendDateRequiresSpecialSessionReview,true);
  assert.equal(v.candidateRegularSessionShapeComplete,false);
});
test('zero observed volume is not certified execution evidence',()=>{
  const v=inspect(make({zeroVolume:[700]}));
  assert.equal(v.zeroVolumeRegularSessionRows,1);
  assert.equal(v.candidateRegularSessionShapeComplete,false);
});
test('duplicate regular timestamp is rejected rather than silently fixed',()=>{
  const s=make();
  const first=s.split('\n')[0];
  assert.throws(()=>inspect(first+'\n'+s),/DUPLICATE_MINUTE_TIMESTAMP/);
});
test('duplicate premarket timestamp is also rejected',()=>{
  assert.throws(()=>inspect(make({pre:[548,548]})),/DUPLICATE_MINUTE_TIMESTAMP/);
});
test('other symbol, other date, and bad time fail closed',()=>{
  assert.throws(()=>inspect(make({symbol:'INFY'})),/WRONG_SYMBOL_OR_DATE_IN_FILE/);
  assert.throws(()=>inspect(make({date:'20230103'})),/WRONG_SYMBOL_OR_DATE_IN_FILE/);
  assert.throws(()=>inspect(make({badRow:'RELIANCE,20220103,25:00,100,101,99,100,1,0'})),
    /INVALID_MINUTE_TIMESTAMP/);
  assert.throws(()=>inspect(make(),{expectedSymbol:'reliance'}),/INVALID_EXPECTED_SYMBOL_OR_DATE/);
  assert.throws(()=>inspect(make(),{expectedDate:'2022-02-30'}),/INVALID_EXPECTED_SYMBOL_OR_DATE/);
});
test('invalid prices, nonsensical volume and CSV shape fail closed',()=>{
  for(const row of [
    'RELIANCE,20220103,09:15,100,99,98,99,1,0',
    'RELIANCE,20220103,09:15,100,101,102,100,1,0',
    'RELIANCE,20220103,09:15,-1,101,99,100,1,0',
    'RELIANCE,20220103,09:15,100,101,99,100,-1,0',
    'RELIANCE,20220103,09:15,100,101,99,100,1.5,0',
    'RELIANCE,20220103,09:15,100,101,99,100,1',
    'RELIANCE,20220103,09:15,NaN,101,99,100,1,0'
  ]) assert.throws(()=>inspect(make({badRow:row})));
});
test('program reads only local absolute ordinary files, not directories',t=>{
  const dir=temp(t),file=path.join(dir,'r.txt');
  fs.writeFileSync(file,make());
  assert.equal(auditLocalThirdPartyCsvFile(file,{
    expectedSymbol:SYMBOL,expectedDate:DATE}).totalRows,375);
  assert.throws(()=>auditLocalThirdPartyCsvFile('relative.txt',{
    expectedSymbol:SYMBOL,expectedDate:DATE}),/INPUT_FILE_NOT_ABSOLUTE/);
  assert.throws(()=>auditLocalThirdPartyCsvFile(dir,{
    expectedSymbol:SYMBOL,expectedDate:DATE}),/INPUT_MUST_BE_REGULAR_FILE/);
});
test('cross-platform command line emits only aggregate metadata and matches API',t=>{
  const dir=temp(t),file=path.join(dir,'sample.txt');
  const source=make({pre:[548],post:[930],skip:[555]});
  fs.writeFileSync(file,source);
  const script=fileURLToPath(new URL('./audit_public_third_party_minute_csv.mjs',import.meta.url));
  const output=execFileSync(process.execPath,[script,'--file',file,
    '--symbol',SYMBOL,'--date',DATE],{encoding:'utf8',timeout:15000});
  const parsed=JSON.parse(output);
  assert.deepEqual(parsed,inspect(source));
  assert.equal(parsed.localSourceSha256.length,64);
  assert.equal(fs.readFileSync(file,'utf8'),source);
  for(const raw of [file,'100.05','99.90','100.10','access_token','API_KEY']){
    assert.equal(output.includes(raw),false,raw);
  }
});
test('no network, third-party SDK, trade order or download inside auditor',()=>{
  const source=fs.readFileSync(new URL(
    './audit_public_third_party_minute_csv.mjs',import.meta.url),'utf8');
  for(const forbidden of [
    'fetch(', 'WebSocket(', 'https://api.', 'axios(',
    'placeOrder(', 'submitOrder(', 'process.env.', 'createOrder(',
    'curl ', 'wget ', 'child_process'
  ])assert.equal(source.includes(forbidden),false,forbidden);
});
