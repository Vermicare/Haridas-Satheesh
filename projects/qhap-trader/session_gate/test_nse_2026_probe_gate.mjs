import test from 'node:test';
import assert from 'node:assert/strict';
import {classifyReadOnlyProbe, classifyStatusOnlyConnection, POLICY} from './nse_2026_probe_gate.mjs';

const when=(date,time,zone='+05:30')=>Date.parse(date+'T'+time+zone);
const testAt=(date,time)=>classifyReadOnlyProbe(when(date,time));
test('policy cites NSE first-party holiday page and uses no live data',()=>{
  assert.equal(POLICY.market,'NSE_EQ');
  assert.match(POLICY.sourceUrl,/^https:\/\/www\.nseindia\.com\//);
  assert.equal(POLICY.conservativeReadOnlyProbeStart,'09:30');
  assert.equal(POLICY.conservativeReadOnlyProbeEndExclusive,'15:00');
});
test('November 10 Diwali Balipratipada holiday blocks even 11:00',()=>{
  const r=testAt('2026-11-10','11:00:00');
  assert.equal(r.verdict,'ABSTAIN');assert.equal(r.reason,'EXCHANGE_PUBLISHED_HOLIDAY');
});
test('November 8 Sunday Muhurat is not auto-certified',()=>{
  assert.equal(testAt('2026-11-08','11:00:00').reason,'WEEKEND_EXCEPTION_NOT_CERTIFIED');
});
test('November 11 weekday 09:30 permits only one read-only attempt',()=>{
  const r=testAt('2026-11-11','09:30:00');
  assert.equal(r.verdict,'ONE_READ_ONLY_PROBE_MAY_BE_ATTEMPTED');
  assert.equal(r.safeToTryAuthorizedReadOnlyProbe,true);
  assert.equal(r.exchangeOpenCertified,false);
  assert.equal(r.licensedDataRightsCertified,false);
  assert.equal(r.liveOrderAuthorization,false);
});
test('regular market start 09:15 is outside conservative pilot',()=>{
  assert.equal(testAt('2026-11-11','09:15:00').verdict,'ABSTAIN');
});
test('09:29:59 is blocked; 09:30:00 opens probe pilot',()=>{
  assert.equal(testAt('2026-11-11','09:29:59').verdict,'ABSTAIN');
  assert.equal(testAt('2026-11-11','09:30:00').safeToTryAuthorizedReadOnlyProbe,true);
});
test('14:59:59 permitted; 15:00:00 blocked',()=>{
  assert.equal(testAt('2026-11-11','14:59:59').safeToTryAuthorizedReadOnlyProbe,true);
  assert.equal(testAt('2026-11-11','15:00:00').verdict,'ABSTAIN');
});
test('November 24 published holiday blocked',()=>{
  assert.equal(testAt('2026-11-24','10:30:00').reason,'EXCHANGE_PUBLISHED_HOLIDAY');
});
test('December 25 holiday blocked',()=>{
  assert.equal(testAt('2026-12-25','10:30:00').reason,'EXCHANGE_PUBLISHED_HOLIDAY');
});
test('all sixteen published 2026 equity holiday dates blocked',()=>{
  const days=['01-15','01-26','03-03','03-26','03-31','04-03','04-14','05-01',
    '05-28','06-26','09-14','10-02','10-20','11-10','11-24','12-25'];
  for(const day of days)assert.equal(
    testAt('2026-'+day,'12:00:00').reason,'EXCHANGE_PUBLISHED_HOLIDAY',day);
});
test('ordinary Saturday blocked',()=>{
  assert.equal(testAt('2026-11-14','10:00:00').reason,'WEEKEND_EXCEPTION_NOT_CERTIFIED');
});
test('ordinary Sunday blocked',()=>{
  assert.equal(testAt('2026-11-15','10:00:00').reason,'WEEKEND_EXCEPTION_NOT_CERTIFIED');
});
test('unverified 2027 calendar blocked',()=>{
  assert.equal(testAt('2027-01-04','10:00:00').reason,'UNSUPPORTED_CALENDAR_YEAR');
});
test('unverified 2025 calendar blocked',()=>{
  assert.equal(testAt('2025-11-11','10:00:00').reason,'UNSUPPORTED_CALENDAR_YEAR');
});
test('UTC and IST strings identify the same instant in NSE local time',()=>{
  const a=classifyReadOnlyProbe(when('2026-11-11','09:30:00'));
  const b=classifyReadOnlyProbe(when('2026-11-11','04:00:00','+00:00'));
  assert.deepEqual(a,b);
});
test('invalid instants rejected',()=>{
  for(const v of [NaN,Infinity,-1,0.1,null,'2026-11-11',4102444800001])
    assert.throws(()=>classifyReadOnlyProbe(v),/INVALID_INSTANT_MS/);
});
const success={status:'READ_ONLY_HTTP_200_CONNECTED_NOT_DATA_VALIDATED',
  httpCode:200,networkCalls:1,tradesSent:0,
  marketDataFreshnessVerified:false,marketDataStored:false,ordersPossible:false};
test('HTTP 200 status is user-reported connectivity, never a certified quote',()=>{
  const r=classifyStatusOnlyConnection(success);
  assert.equal(r.connectionConfirmed,true);
  assert.equal(r.quoteVerified,false);
  assert.equal(r.sessionCertified,false);
  assert.equal(r.ordersAuthorized,false);
});
test('token, market prices and other unknown fields rejected',()=>{
  for(const obj of [{token:'SECRET'},{last_price:72},{data:{foo:'bar'}},{secret:'x'}])
    assert.throws(()=>classifyStatusOnlyConnection(obj),/UNKNOWN_OR_PRIVATE_STATUS_FIELD/);
});
test('malformed or non-200 status cannot certify a connection',()=>{
  for(const patch of [{httpCode:401},{tradesSent:1},
    {marketDataFreshnessVerified:true},{ordersPossible:true},
    {status:'READY_TO_TRADE'},{networkCalls:100}]){
    const r=classifyStatusOnlyConnection({...success,...patch});
    assert.equal(r.connectionConfirmed,false);
    assert.equal(r.ordersAuthorized,false);
  }
});
test('nested and invalid status types fail closed',()=>{
  assert.throws(()=>classifyStatusOnlyConnection([]),/BAD_STATUS_OBJECT/);
  assert.throws(()=>classifyStatusOnlyConnection(null),/BAD_STATUS_OBJECT/);
});
