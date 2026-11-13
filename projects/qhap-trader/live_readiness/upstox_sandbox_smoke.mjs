#!/usr/bin/env node
/**
 * QHAP-TRADER — isolated Upstox SANDBOX-only order lifecycle smoke test.
 * This file intentionally has NO live trading host, no base-URL override,
 * and no ability to retrieve trading-capable credentials.
 *
 * The user must explicitly run "--sandbox-smoke --confirm-sandbox-only"
 * to submit exactly ONE fake sandbox LIMIT order and attempt cancellation.
 * Preview/default mode has NO network effects. No automatic retries.
 */
import crypto from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export const SANDBOX_ORIGIN='https://api-sandbox.upstox.com';
export const PLACE_PATH='/v3/order/place';
export const CANCEL_PATH='/v3/order/cancel';
export const TEST_INSTRUMENT='NSE_EQ|INE669E01016'; // Official sandbox SDK example.
export const MINIMAL_ORDER=Object.freeze({
  quantity:1,product:'D',validity:'DAY',price:9.12,
  tag:'QHAP_SANDBOX_SMOKE',
  instrument_token:TEST_INSTRUMENT,
  order_type:'LIMIT',transaction_type:'BUY',
  disclosed_quantity:0,trigger_price:0,is_amo:false,
  slice:false
});
const fingerprint=x=>crypto.createHash('sha256').update(x).digest('hex').slice(0,12);
const safeToken=token=>typeof token==='string'&&
  token.length>=16&&token.length<=16000&&!/[\s\r\n]/.test(token);
const validOrderId=x=>typeof x==='string'&&/^[A-Za-z0-9-]{4,80}$/.test(x);

/**
 * Pure plan: fail closed on changed order payloads or wrong host.
 * Preview deliberately does not expose or inspect a credential.
 */
export function sandboxPreview(){
  return Object.freeze({
    status:'SANDBOX_ONLY_PREVIEW_NO_NETWORK',
    sandboxHost:SANDBOX_ORIGIN,
    action:'ONE_FAKE_LIMIT_BUY_THEN_FAKE_CANCEL',
    instrumentKey:TEST_INSTRUMENT,
    quantity:1,limitPriceRupees:9.12,
    simulatedOrderRequestOnly:true,
    requestsAttempted:0,realOrdersSent:0,
    realOrderRoutePresent:false,canTradeRealMoney:false,
    credentialsRead:false
  });
}
function fixedRequest(method,relative,token,body){
  if(!safeToken(token))throw Error('MISSING_OR_INVALID_SANDBOX_TOKEN');
  if(![['POST',PLACE_PATH],['DELETE',CANCEL_PATH]].some(
    ([m,p])=>m===method&&
      (relative===p||(m==='DELETE'&&relative.startsWith(p+'?order_id=')))))
    throw Error('UNSUPPORTED_SANDBOX_REQUEST');
  const url=new URL(relative,SANDBOX_ORIGIN);
  if(url.origin!==SANDBOX_ORIGIN||url.username||url.password||
     url.hash||url.protocol!=='https:')
    throw Error('SANDBOX_ORIGIN_MISMATCH');
  if(method==='POST'&&(url.pathname!==PLACE_PATH||url.search))throw Error('INVALID_PLACE_PATH');
  if(method==='DELETE'&&(url.pathname!==CANCEL_PATH||
     !validOrderId(url.searchParams.get('order_id'))||
     [...url.searchParams.keys()].join(',')!=='order_id'))
    throw Error('INVALID_CANCEL_PATH');
  return {
    url:url.toString(),
    options:{
      method,redirect:'error',signal:AbortSignal.timeout(12000),
      headers:{Accept:'application/json',
        Authorization:'Bearer '+token,
        ...(method==='POST'?{'Content-Type':'application/json'}:{})},
      ...(method==='POST'?{body:JSON.stringify(body)}:{})
    }
  };
}
async function callSandbox(fetchImpl,method,relative,token,body){
  const {url,options}=fixedRequest(method,relative,token,body);
  let res;
  try{res=await fetchImpl(url,options);}
  catch{throw Error('SANDBOX_NETWORK_OUTCOME_UNKNOWN_MANUAL_REVIEW_NO_RETRY');}
  if(!res||!Number.isInteger(res.status)||res.status<200||res.status>299||
     res.ok!==true)
    throw Error('SANDBOX_HTTP_'+String(Number.isInteger(res?.status)?res.status:'UNKNOWN'));
  if(res.headers?.get&&
     Number(res.headers.get('content-length')||0)>64000)
    throw Error('SANDBOX_RESPONSE_OVERSIZE');
  let value;
  try{
    const txt=await res.text();
    if(typeof txt!=='string'||txt.length>64000)throw Error('OVERSIZE');
    value=JSON.parse(txt);
  }catch{throw Error('SANDBOX_RESPONSE_UNREADABLE_OUTCOME_UNKNOWN');}
  if(!value||value.status!=='success'||!value.data||
     typeof value.data!=='object')
    throw Error('SANDBOX_NO_CONFIRMED_SUCCESS_MANUAL_REVIEW');
  return value;
}
/**
 * Sandbox only: exactly one fake order, one attempted fake cancellation.
 * Never retry because a lost response could conceal an accepted fake order.
 */
export async function runSandboxSmoke(token,fetchImpl=fetch){
  if(!safeToken(token))throw Error('MISSING_OR_INVALID_SANDBOX_TOKEN');
  const result={
    status:'SANDBOX_PLACE_NOT_ATTEMPTED',
    sandboxHost:SANDBOX_ORIGIN,
    mode:'UPSTOX_SANDBOX_ONLY_NO_REAL_FUNDS',
    sandboxOrdersAttempted:0,sandboxCancelsAttempted:0,
    realOrdersSent:0,realOrderRoutePresent:false,
    canTradeRealMoney:false,tokenPrinted:false,
    responseBodiesPrinted:false
  };
  try{
    result.status='SANDBOX_PLACE_OUTCOME_UNKNOWN_MANUAL_REVIEW';
    result.sandboxOrdersAttempted=1;
    const placed=await callSandbox(fetchImpl,'POST',PLACE_PATH,token,MINIMAL_ORDER);
    const ids=placed?.data?.order_ids;
    if(!Array.isArray(ids)||ids.length!==1||!validOrderId(ids[0]))
      throw Error('SANDBOX_PLACE_UNEXPECTED_ORDER_IDS_MANUAL_REVIEW');
    result.sandboxOrderFingerprint=fingerprint(ids[0]);
    result.status='SANDBOX_PLACE_ACCEPTED_CANCEL_NOT_CONFIRMED';
    result.sandboxCancelsAttempted=1;
    const cancelled=await callSandbox(fetchImpl,'DELETE',
      CANCEL_PATH+'?order_id='+encodeURIComponent(ids[0]),token);
    if(cancelled?.data?.order_id!==ids[0])
      throw Error('SANDBOX_CANCEL_ORDER_ID_MISMATCH_MANUAL_REVIEW');
    result.status='SANDBOX_PLACE_AND_CANCEL_CONFIRMED';
    return result;
  }catch(error){
    // Never return API response bodies, token, raw credentials, request headers or order IDs.
    const detail=/^SANDBOX_[A-Z0-9_]+$/.test(error?.message||'')?
      error.message:'SANDBOX_UNEXPECTED_OUTCOME_MANUAL_REVIEW';
    result.reason=detail;
    return result;
  }
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  if(process.argv.length===3&&process.argv[2]==='--preview'){
    console.log(JSON.stringify(sandboxPreview(),null,2));
  }else if(process.argv.length===4&&
           process.argv[2]==='--sandbox-smoke'&&
           process.argv[3]==='--confirm-sandbox-only'){
    const r=await runSandboxSmoke(process.env.UPSTOX_SANDBOX_ACCESS_TOKEN);
    console.log(JSON.stringify(r,null,2));
    process.exitCode=r.status==='SANDBOX_PLACE_AND_CANCEL_CONFIRMED'?0:1;
  }else{
    console.error('USAGE: node upstox_sandbox_smoke.mjs --preview | --sandbox-smoke --confirm-sandbox-only');
    process.exitCode=2;
  }
}
