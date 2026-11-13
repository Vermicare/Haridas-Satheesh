import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {
  SANDBOX_ORIGIN,PLACE_PATH,CANCEL_PATH,MINIMAL_ORDER,TEST_INSTRUMENT,
  sandboxPreview,runSandboxSmoke
} from './upstox_sandbox_smoke.mjs';
const token='LOCAL_FAKE_SANDBOX_TOKEN_123456789';
const accepted=(body)=>({ok:true,status:200,
  headers:{get:()=>null},text:async()=>JSON.stringify(body)});
const orderId='SBX1234567890';
const placeOk=()=>accepted({status:'success',data:{order_ids:[orderId]}});
const cancelOk=()=>accepted({status:'success',data:{order_id:orderId}});
const fakeRun=async(responses)=>{
  const calls=[];
  const result=await runSandboxSmoke(token,async(url,options)=>{
    calls.push({url,options});
    return responses[calls.length-1];
  });
  return {result,calls};
};
test('default preview has no credentials, no network, no order capability',()=>{
  const x=sandboxPreview();
  assert.equal(x.requestsAttempted,0);
  assert.equal(x.credentialsRead,false);
  assert.equal(x.sandboxHost,'https://api-sandbox.upstox.com');
  assert.equal(x.realOrderRoutePresent,false);
  assert.equal(x.realOrdersSent,0);
  assert.equal(x.canTradeRealMoney,false);
  assert.equal(JSON.stringify(x).includes(token),false);
});
test('only official sandbox origin exists in code (never a live trading host)',()=>{
  const text=fs.readFileSync(fileURLToPath(new URL('./upstox_sandbox_smoke.mjs',import.meta.url)),'utf8');
  assert.equal(SANDBOX_ORIGIN,'https://api-sandbox.upstox.com');
  assert.ok(!text.includes('https://api-hft.upstox.com'));
  assert.ok(!text.includes('https://api.upstox.com'));
  assert.ok(!text.includes('UPSTOX_ACCESS_TOKEN'));
  assert.ok(!text.includes('UPSTOX_ANALYTICS_TOKEN'));
});
test('one fake sandbox buy then one fake cancellation uses strict URLs and methods',async()=>{
  const {result,calls}=await fakeRun([placeOk(),cancelOk()]);
  assert.equal(result.status,'SANDBOX_PLACE_AND_CANCEL_CONFIRMED');
  assert.equal(result.sandboxOrdersAttempted,1);
  assert.equal(result.sandboxCancelsAttempted,1);
  assert.equal(result.realOrdersSent,0);
  assert.equal(result.canTradeRealMoney,false);
  assert.equal(calls.length,2);
  assert.equal(calls[0].url,SANDBOX_ORIGIN+PLACE_PATH);
  assert.equal(calls[0].options.method,'POST');
  assert.equal(calls[0].options.redirect,'error');
  assert.equal(calls[0].options.headers.Authorization,'Bearer '+token);
  assert.deepEqual(JSON.parse(calls[0].options.body),MINIMAL_ORDER);
  assert.equal(MINIMAL_ORDER.instrument_token,TEST_INSTRUMENT);
  assert.equal(MINIMAL_ORDER.quantity,1);
  assert.equal(MINIMAL_ORDER.order_type,'LIMIT');
  assert.equal(MINIMAL_ORDER.slice,false);
  assert.equal(calls[1].url,SANDBOX_ORIGIN+CANCEL_PATH+'?order_id='+orderId);
  assert.equal(calls[1].options.method,'DELETE');
  assert.equal(calls[1].options.body,undefined);
  assert.equal(calls[1].options.redirect,'error');
  assert.equal(JSON.stringify(result).includes(orderId),false);
  assert.equal(JSON.stringify(result).includes(token),false);
});
test('missing token fails before sending even sandbox order',async()=>{
  for(const bad of [undefined,null,'','short','whitespace token here']){
    let sent=0;
    await assert.rejects(runSandboxSmoke(bad,async()=>{sent++;return placeOk();}),/INVALID_SANDBOX_TOKEN/);
    assert.equal(sent,0);
  }
});
test('sandbox place 401 and 429 fail closed and never cancel',async()=>{
  for(const status of [401,429]){
    const {result,calls}=await fakeRun([{ok:false,status}]);
    assert.equal(calls.length,1);
    assert.equal(result.status,'SANDBOX_PLACE_OUTCOME_UNKNOWN_MANUAL_REVIEW');
    assert.equal(result.reason,'SANDBOX_HTTP_'+status);
    assert.equal(result.sandboxCancelsAttempted,0);
  }
});
test('lost place response must never retry or invent an order ID',async()=>{
  let calls=0;
  const result=await runSandboxSmoke(token,async()=>{
    calls++;throw Error('SENSITIVE_BACKEND_MESSAGE_BEARER_TOKEN');
  });
  assert.equal(calls,1);
  assert.equal(result.status,'SANDBOX_PLACE_OUTCOME_UNKNOWN_MANUAL_REVIEW');
  assert.equal(result.reason,'SANDBOX_NETWORK_OUTCOME_UNKNOWN_MANUAL_REVIEW_NO_RETRY');
  assert.equal(JSON.stringify(result).includes('SENSITIVE_BACKEND'),false);
});
test('two returned order IDs prevent accidentally cancelling one of several fake orders',async()=>{
  const {result,calls}=await fakeRun([accepted({
    status:'success',data:{order_ids:[orderId,'SBX2222222222']}
  })]);
  assert.equal(calls.length,1);
  assert.equal(result.reason,'SANDBOX_PLACE_UNEXPECTED_ORDER_IDS_MANUAL_REVIEW');
});
test('null order IDs and malformed payload fail closed',async()=>{
  for(const obj of [null,{}, {status:'error',data:{order_ids:[orderId]}},
    {status:'success',data:{order_ids:['../suspicious']}},
    {status:'success',data:{order_ids:[]}}]){
    const {result,calls}=await fakeRun([accepted(obj)]);
    assert.equal(calls.length,1);
    assert.equal(result.sandboxCancelsAttempted,0);
    assert.notEqual(result.status,'SANDBOX_PLACE_AND_CANCEL_CONFIRMED');
    assert.equal(result.realOrdersSent,0);
  }
});
test('cancel refused or HTTP failure remains unconfirmed (never claim a cancelled order)',async()=>{
  for(const response of [
    {ok:false,status:400},
    accepted({status:'error',data:{order_id:orderId}}),
    accepted({status:'success',data:{order_id:'SBX999999'}})
  ]){
    const {result,calls}=await fakeRun([placeOk(),response]);
    assert.equal(calls.length,2);
    assert.equal(result.status,'SANDBOX_PLACE_ACCEPTED_CANCEL_NOT_CONFIRMED');
    assert.equal(result.sandboxCancelsAttempted,1);
    assert.equal(result.realOrdersSent,0);
  }
});
test('HTTP successful but unreadable result is uncertain, never retries',async()=>{
  const {result,calls}=await fakeRun([{ok:true,status:200,
    headers:{get:()=>null},text:async()=>'{malformed secret'}]);
  assert.equal(calls.length,1);
  assert.equal(result.reason,'SANDBOX_RESPONSE_UNREADABLE_OUTCOME_UNKNOWN');
  assert.equal(result.sandboxCancelsAttempted,0);
});
test('Content-Length size cap blocks suspicious sandbox responses',async()=>{
  const {result,calls}=await fakeRun([{ok:true,status:200,
    headers:{get:()=>String(1_000_000)},text:async()=>{throw Error('SHOULD_NOT_READ');}}]);
  assert.equal(calls.length,1);
  assert.equal(result.reason,'SANDBOX_RESPONSE_OVERSIZE');
  assert.equal(result.realOrdersSent,0);
});
test('server body cannot leak token or live broker data through error summary',async()=>{
  const malicious={status:'fail',data:{},token,broker_key:'SECRET'};
  const {result}=await fakeRun([accepted(malicious)]);
  assert.equal(JSON.stringify(result).includes(token),false);
  assert.equal(JSON.stringify(result).includes('SECRET'),false);
  assert.equal(result.canTradeRealMoney,false);
});
