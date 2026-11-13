import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {sandboxModifyPreview,runSandboxModifySmoke}
  from './upstox_sandbox_modify_smoke.mjs';
const token='MOCK_SANDBOX_ONLY_ACCESS_TOKEN_123456789';
const id='1234567890123';
const answer=data=>({status:200,ok:true,
  headers:{get:()=>null},text:async()=>JSON.stringify({status:'success',data})});
const success=[
  answer({order_ids:[id]}),
  answer({order_id:id}),
  answer({order_id:id})
];
const run=async arr=>{
  const calls=[];
  const result=await runSandboxModifySmoke(token,async(url,options)=>{
    calls.push({url,options});
    const item=arr[calls.length-1];
    if(item instanceof Error)throw item;
    return item;
  });
  return {result,calls};
};
test('preview reads no token, makes no requests, does not claim live orders',()=>{
  const x=sandboxModifyPreview();
  assert.equal(x.status,'SANDBOX_MODIFY_PREVIEW_NO_NETWORK');
  assert.equal(x.credentialsRead,false);
  assert.equal(x.requestsAttempted,0);
  assert.equal(x.canTradeRealMoney,false);
  assert.equal(x.realOrdersSent,0);
});
test('source and request target cannot contain production API host or token',()=>{
  const raw=fs.readFileSync(fileURLToPath(
    new URL('./upstox_sandbox_modify_smoke.mjs',import.meta.url)),'utf8');
  assert.ok(!raw.includes('https://api-hft.upstox.com'));
  assert.ok(!raw.includes('https://api.upstox.com'));
  assert.ok(!raw.includes('UPSTOX_ACCESS_TOKEN'));
  assert.ok(!raw.includes('UPSTOX_ANALYTICS_TOKEN'));
});
test('authentic happy path uses only sandbox POST PUT DELETE with fixed fake payload',async()=>{
  const {result,calls}=await run(success);
  assert.equal(calls.length,3);
  assert.deepEqual(calls.map(x=>x.options.method),['POST','PUT','DELETE']);
  assert.ok(calls.every(x=>x.url.startsWith('https://api-sandbox.upstox.com/v3/order/')));
  assert.ok(calls.every(x=>x.options.redirect==='error'));
  assert.ok(calls.every(x=>x.options.headers.Authorization==='Bearer '+token));
  assert.equal(calls[0].url,'https://api-sandbox.upstox.com/v3/order/place');
  assert.equal(calls[1].url,'https://api-sandbox.upstox.com/v3/order/modify');
  assert.equal(calls[2].url,
    'https://api-sandbox.upstox.com/v3/order/cancel?order_id='+id);
  const original=JSON.parse(calls[0].options.body);
  assert.equal(original.order_type,'LIMIT');
  assert.equal(original.quantity,1);
  assert.equal(original.slice,false);
  assert.equal(original.tag,'QHAP_SANDBOX_MODIFY_SMOKE');
  const modified=JSON.parse(calls[1].options.body);
  assert.equal(modified.order_id,id);
  assert.equal(modified.price,9.10);
  assert.equal(modified.quantity,1);
  assert.equal(calls[2].options.body,undefined);
  assert.equal(result.status,'SANDBOX_PLACE_MODIFY_CANCEL_ACKS_CONFIRMED');
  assert.equal(result.placeAcknowledged,true);
  assert.equal(result.modifyAcknowledged,true);
  assert.equal(result.cancelAcknowledged,true);
  assert.equal(result.terminalStatusIndependentlyVerified,false);
  assert.equal(result.finalFilledQuantityKnown,false);
  assert.equal(result.realOrdersSent,0);
  assert.equal(result.canTradeRealMoney,false);
  assert.equal(JSON.stringify(result).includes(id),false);
  assert.equal(JSON.stringify(result).includes(token),false);
});
test('bad token never sends any sandbox request',async()=>{
  for(const candidate of ['',null,undefined,'short','contains spaces']){
    let seen=0;
    await assert.rejects(runSandboxModifySmoke(candidate,async()=>{
      seen++;return success[0];
    }),/SANDBOX_INVALID_LOCAL_TOKEN/);
    assert.equal(seen,0);
  }
});
test('place denied: no modify or cancel and no imaginary order',async()=>{
  const {result,calls}=await run([{ok:false,status:401}]);
  assert.equal(calls.length,1);
  assert.equal(result.placeRequests,1);
  assert.equal(result.modifyRequests,0);
  assert.equal(result.cancelRequests,0);
  assert.equal(result.status,'SANDBOX_PLACE_UNCONFIRMED_MANUAL_REVIEW');
  assert.equal(result.reason,'SANDBOX_HTTP_401');
});
test('place network outage cannot trigger retry, no order IDs fabricated',async()=>{
  const {result,calls}=await run([new Error('SHOULD_NOT_LEAK_SECRET')]);
  assert.equal(calls.length,1);
  assert.equal(result.placeAcknowledged,false);
  assert.equal(result.reason,'SANDBOX_NETWORK_RESULT_UNKNOWN_NO_RETRY');
  assert.equal(JSON.stringify(result).includes('SHOULD_NOT_LEAK_SECRET'),false);
});
test('multiple fake IDs blocks unsafe modification and cancellation',async()=>{
  const {result,calls}=await run([answer({order_ids:[id,'1234567890124']})]);
  assert.equal(calls.length,1);
  assert.equal(result.reason,'SANDBOX_UNEXPECTED_PLACE_ORDER_IDENTIFIERS');
  assert.equal(result.cancelRequests,0);
});
test('failed modify still attempts one sandbox cancellation for known fake ID',async()=>{
  const {result,calls}=await run([success[0],{ok:false,status:429},success[2]]);
  assert.deepEqual(calls.map(x=>x.options.method),['POST','PUT','DELETE']);
  assert.equal(result.placeAcknowledged,true);
  assert.equal(result.modifyAcknowledged,false);
  assert.equal(result.cancelAcknowledged,true);
  assert.equal(result.status,'SANDBOX_PARTIAL_ACK_MANUAL_REVIEW');
  assert.equal(result.reason,'SANDBOX_HTTP_429');
});
test('lost modify response triggers one safe fake cancellation; no retries',async()=>{
  const {result,calls}=await run([success[0],new Error('PRIVATE'),success[2]]);
  assert.equal(calls.length,3);
  assert.equal(result.modifyRequests,1);
  assert.equal(result.cancelRequests,1);
  assert.equal(result.reason,'SANDBOX_NETWORK_RESULT_UNKNOWN_NO_RETRY');
});
test('modify response for other order cannot be trusted',async()=>{
  const {result,calls}=await run([success[0],answer({order_id:'1234567899999'}),success[2]]);
  assert.equal(calls.length,3);
  assert.equal(result.modifyAcknowledged,false);
  assert.equal(result.cancelAcknowledged,true);
  assert.equal(result.reason,'SANDBOX_MODIFY_ACK_ORDER_MISMATCH');
});
test('cancel refusal leaves fake lifecycle unresolved',async()=>{
  const {result,calls}=await run([success[0],success[1],{ok:false,status:400}]);
  assert.equal(calls.length,3);
  assert.equal(result.placeAcknowledged,true);
  assert.equal(result.modifyAcknowledged,true);
  assert.equal(result.cancelAcknowledged,false);
  assert.equal(result.status,'SANDBOX_PARTIAL_ACK_MANUAL_REVIEW');
  assert.equal(result.reason,'SANDBOX_HTTP_400');
});
test('cancel response matching incorrect order ID blocks confirmation',async()=>{
  const {result}=await run([success[0],success[1],answer({order_id:'88888888'})]);
  assert.equal(result.cancelAcknowledged,false);
  assert.equal(result.reason,'SANDBOX_CANCEL_ACK_ORDER_MISMATCH');
});
test('token and server response bodies cannot leak on malformed response',async()=>{
  const malformed={status:200,ok:true,
    headers:{get:()=>null},text:async()=>'{token='+token};
  const {result,calls}=await run([malformed]);
  assert.equal(calls.length,1);
  assert.equal(result.reason,'SANDBOX_BODY_INVALID_UNCERTAIN');
  assert.ok(!JSON.stringify(result).includes(token));
});
test('provider sandbox schema can be ACK-success but is never terminal reconciliation',async()=>{
  const {result}=await run(success);
  assert.equal(result.status,'SANDBOX_PLACE_MODIFY_CANCEL_ACKS_CONFIRMED');
  assert.equal(result.terminalStatusIndependentlyVerified,false);
  assert.equal(result.finalFilledQuantityKnown,false);
  assert.equal(result.realOrderRoutePresent,false);
});
