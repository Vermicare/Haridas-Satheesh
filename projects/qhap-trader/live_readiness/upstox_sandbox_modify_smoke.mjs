#!/usr/bin/env node
/**
 * QHAP-TRADER explicit user-local UPSTOX SANDBOX-ONLY
 * create -> modify -> cancel ACK smoke. No real API host is present.
 * Never retry requests when receipt is uncertain.
 * The sandbox supports order mutation endpoints; it does NOT independently
 * certify terminal order state, settled quantities, or broker reconciliation.
 */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {SANDBOX_ORIGIN,PLACE_PATH,CANCEL_PATH,MINIMAL_ORDER}
  from './upstox_sandbox_smoke.mjs';
export const MODIFY_PATH='/v3/order/modify';
const VALID_ID=/^[A-Za-z0-9-]{4,80}$/;
const tokenOk=s=>typeof s==='string'&&s.length>=16&&s.length<=16000&&!/\s/.test(s);
const code=e=>/^(?:SANDBOX_[A-Z0-9_]+)$/.test(e?.message||'')?
  e.message:'SANDBOX_UNCLASSIFIED_ERROR_MANUAL_REVIEW';

export function sandboxModifyPreview(){
  return Object.freeze({
    status:'SANDBOX_MODIFY_PREVIEW_NO_NETWORK',
    host:SANDBOX_ORIGIN,
    plan:'ONE_FAKE_PLACE_THEN_ONE_FAKE_MODIFY_THEN_ONE_FAKE_CANCEL',
    initialLimit:MINIMAL_ORDER.price,modifiedLimit:9.10,
    instrumentKey:MINIMAL_ORDER.instrument_token,quantity:1,
    requestsAttempted:0,credentialsRead:false,realOrdersSent:0,
    realOrderRoutePresent:false,canTradeRealMoney:false
  });
}
async function api(fetchFn,token,method,pathname,body){
  if(!tokenOk(token))throw Error('SANDBOX_INVALID_LOCAL_TOKEN');
  if(!([['POST',PLACE_PATH],['PUT',MODIFY_PATH]].some(
    pair=>pair[0]===method&&pair[1]===pathname)||
    (method==='DELETE'&&pathname.startsWith(CANCEL_PATH+'?order_id='))))
    throw Error('SANDBOX_UNSUPPORTED_OPERATION');
  const url=new URL(pathname,SANDBOX_ORIGIN);
  if(url.origin!==SANDBOX_ORIGIN||url.protocol!=='https:'||
     url.username||url.password||url.hash)
    throw Error('SANDBOX_UNEXPECTED_ORIGIN');
  if(method==='DELETE'){
    if(url.pathname!==CANCEL_PATH||
       !VALID_ID.test(url.searchParams.get('order_id')||'')||
       [...url.searchParams.keys()].join(',')!=='order_id')
      throw Error('SANDBOX_BAD_CANCEL_URL');
  }else if(url.search)throw Error('SANDBOX_UNEXPECTED_QUERY');
  const options={method,redirect:'error',signal:AbortSignal.timeout(12000),
    headers:{Accept:'application/json',Authorization:'Bearer '+token,
      ...(body?{'Content-Type':'application/json'}:{})},
    ...(body?{body:JSON.stringify(body)}:{})};
  let response;
  try{response=await fetchFn(url.toString(),options);}
  catch{throw Error('SANDBOX_NETWORK_RESULT_UNKNOWN_NO_RETRY');}
  if(!response||response.ok!==true||response.status<200||response.status>299)
    throw Error('SANDBOX_HTTP_'+
      (Number.isInteger(response?.status)?response.status:'UNKNOWN'));
  if(Number(response.headers?.get?.('content-length')||0)>64000)
    throw Error('SANDBOX_BODY_TOO_LARGE');
  let parsed;
  try{
    const raw=await response.text();
    if(typeof raw!=='string'||raw.length>64000)throw Error('TOO_LARGE');
    parsed=JSON.parse(raw);
  }catch{throw Error('SANDBOX_BODY_INVALID_UNCERTAIN');}
  if(parsed?.status!=='success'||!parsed.data||
    typeof parsed.data!=='object')
    throw Error('SANDBOX_RESPONSE_NOT_ACCEPTED');
  return parsed;
}
const validConfirmedId=id=>typeof id==='string'&&VALID_ID.test(id);
const originalOrder=Object.freeze({...MINIMAL_ORDER,
  tag:'QHAP_SANDBOX_MODIFY_SMOKE',quantity:1,price:9.12,
  order_type:'LIMIT',transaction_type:'BUY',slice:false});
export async function runSandboxModifySmoke(token,fetchFn=fetch){
  if(!tokenOk(token))throw Error('SANDBOX_INVALID_LOCAL_TOKEN');
  const result={
    status:'SANDBOX_MODIFY_NO_REQUESTS',
    host:SANDBOX_ORIGIN,mode:'SANDBOX_ONLY_FAKE_ORDERS',
    placeRequests:0,modifyRequests:0,cancelRequests:0,
    placeAcknowledged:false,modifyAcknowledged:false,
    cancelAcknowledged:false,terminalStatusIndependentlyVerified:false,
    finalFilledQuantityKnown:false,realOrdersSent:0,
    realOrderRoutePresent:false,canTradeRealMoney:false,
    tokenPrinted:false,rawOrderIdsPrinted:false
  };
  let id=null,failed=null;
  try{
    result.placeRequests=1;
    result.status='SANDBOX_PLACE_OUTCOME_UNKNOWN';
    const response=await api(fetchFn,token,'POST',PLACE_PATH,originalOrder);
    const ids=response.data?.order_ids;
    if(!Array.isArray(ids)||ids.length!==1||!validConfirmedId(ids[0]))
      throw Error('SANDBOX_UNEXPECTED_PLACE_ORDER_IDENTIFIERS');
    id=ids[0];
    result.placeAcknowledged=true;
    result.status='SANDBOX_PLACE_ACK_MODIFY_PENDING';
    result.modifyRequests=1;
    const modified=await api(fetchFn,token,'PUT',MODIFY_PATH,{
      order_id:id,quantity:1,validity:'DAY',price:9.10,
      order_type:'LIMIT',disclosed_quantity:0,trigger_price:0
    });
    if(modified.data?.order_id!==id)
      throw Error('SANDBOX_MODIFY_ACK_ORDER_MISMATCH');
    result.modifyAcknowledged=true;
  }catch(e){failed=code(e);}
  // After a verified fake place ID, ALWAYS attempt one sandbox cancel,
  // even if modifying failed. Do not silently leave fake order unaddressed.
  if(id){
    result.cancelRequests=1;
    result.status='SANDBOX_CANCEL_OUTCOME_UNKNOWN';
    try{
      const cancelled=await api(fetchFn,token,'DELETE',
        CANCEL_PATH+'?order_id='+encodeURIComponent(id));
      if(cancelled.data?.order_id!==id)
        throw Error('SANDBOX_CANCEL_ACK_ORDER_MISMATCH');
      result.cancelAcknowledged=true;
    }catch(e){failed=failed||code(e);}
  }
  if(result.placeAcknowledged&&result.modifyAcknowledged&&
     result.cancelAcknowledged){
    result.status='SANDBOX_PLACE_MODIFY_CANCEL_ACKS_CONFIRMED';
  }else{
    result.status=id?'SANDBOX_PARTIAL_ACK_MANUAL_REVIEW':
      'SANDBOX_PLACE_UNCONFIRMED_MANUAL_REVIEW';
  }
  if(failed)result.reason=failed;
  return result;
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  if(process.argv.length===3&&process.argv[2]==='--preview')
    console.log(JSON.stringify(sandboxModifyPreview(),null,2));
  else if(process.argv.length===4&&
    process.argv[2]==='--sandbox-modify-smoke'&&
    process.argv[3]==='--confirm-sandbox-only'){
    const result=await runSandboxModifySmoke(
      process.env.UPSTOX_SANDBOX_ACCESS_TOKEN);
    console.log(JSON.stringify(result,null,2));
    process.exitCode=
      result.status==='SANDBOX_PLACE_MODIFY_CANCEL_ACKS_CONFIRMED'?0:1;
  }else{
    console.error('Usage: node upstox_sandbox_modify_smoke.mjs --preview | --sandbox-modify-smoke --confirm-sandbox-only');
    process.exitCode=2;
  }
}
