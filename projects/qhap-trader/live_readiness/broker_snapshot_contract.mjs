/**
 * QHAP-TRADER broker-shaped reconciliation CONTRACT — mock data ONLY.
 *
 * No network, vendor SDK, broker tokens, data-source authentication or executable
 * trade path. Source fixtures are never accepted as proof of actual broker state.
 * This module detects paper-ledger/snapshot discrepancies for future adapter tests.
 */
const ORDER_STATUSES=new Set([
  'PENDING_ACK','ACKNOWLEDGED','PARTIALLY_FILLED','CANCEL_PENDING',
  'FILLED','CANCELED','REJECTED'
]);
const FINAL=new Set(['FILLED','CANCELED','REJECTED']);
const CASH_FIELDS=Object.freeze([
  'cashAvailableRupees','cashReservedRupees','cashSpentRupees',
  'unsettledSaleProceedsRupees','positionCostRupees','committedExposureRupees'
]);
const HEADER_FIELDS=new Set(['schemaVersion','source','snapshotId','capturedAtMs',
  'coverage','orders','longUnits','cash']);
const ORDER_FIELDS=new Set(['orderId','status','quantity','cumulativeFilled']);
const accountValue=n=>typeof n==='number'&&Number.isFinite(n)&&n>=0&&
  Number.isSafeInteger(Math.round(n*100))&&Math.abs(n*100-Math.round(n*100))<=1e-6;
const safeInt=n=>Number.isSafeInteger(n)&&n>=0;
const validId=s=>typeof s==='string'&&/^[a-zA-Z0-9_-]{1,40}$/.test(s);
const record=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const exactKeys=(x,keys)=>record(x)&&Object.keys(x).length===keys.size&&
  Object.keys(x).every(k=>keys.has(k));
const empty=(status,reasons=[])=>Object.freeze({
  status,
  reasons:[...new Set(reasons)].sort(),
  realOrdersSent:0,
  liveTradingAuthorized:false,
  canTrade:false,
  brokerReconciled:false,
  snapshotCryptographicallyAuthenticated:false,
  externalAccountIdentityVerified:false,
  manualReviewRequired:true
});
const minor=n=>Math.round(n*100);
const equalOrder=(a,b)=>a.status===b.status&&a.quantity===b.quantity&&
  a.cumulativeFilled===b.cumulativeFilled;
function validOrder(o){
  if(!exactKeys(o,ORDER_FIELDS)||!validId(o.orderId)||!ORDER_STATUSES.has(o.status)||
    !safeInt(o.quantity)||o.quantity===0||!safeInt(o.cumulativeFilled)||
    o.cumulativeFilled>o.quantity) return false;
  if(o.status==='FILLED'&&o.cumulativeFilled!==o.quantity)return false;
  if(o.status==='REJECTED'&&o.cumulativeFilled!==0)return false;
  if(o.status==='PARTIALLY_FILLED'&&(o.cumulativeFilled===0||o.cumulativeFilled===o.quantity))return false;
  if(!FINAL.has(o.status)&&o.status!=='CANCEL_PENDING'&&o.cumulativeFilled===o.quantity)return false;
  return true;
}
function indexOrders(orders){
  const out=new Map();
  for(const o of orders){
    if(!validOrder(o)||out.has(o.orderId))return null;
    out.set(o.orderId,o);
  }
  return out;
}

/**
 * Accepts a previously hash-replayed paper journal and a sanitized synthetic,
 * complete broker-shaped fixture. Nothing here authenticates a real vendor
 * response. Never pass tokens or raw broker responses to this function.
 *
 * Requires injected observation time and checked snapshot freshness; snapshots
 * representing a partial API page are rejected rather than interpreted as no
 * open orders.
 */
export function auditSyntheticBrokerSnapshot(recovered,snapshot,options={}){
  const reasons=[];
  if(!record(recovered)||recovered.status!=='RECOVERED_RECONCILIATION_REQUIRED'||
     recovered.hashChainVerified!==true||recovered.canAppend!==false||
     !safeInt(recovered.longUnits)||!Array.isArray(recovered.orders)||
     CASH_FIELDS.some(k=>!accountValue(recovered[k]))){
    return empty('BLOCKED_UNTRUSTED_RECOVERY',['INVALID_OR_INCOMPLETE_RECOVERED_JOURNAL']);
  }
  const local=indexOrders(recovered.orders);
  if(!local)return empty('BLOCKED_UNTRUSTED_RECOVERY',['INVALID_JOURNAL_ORDER_SET']);
  if(!record(options)||!safeInt(options.observedAtMs)||!safeInt(options.maxAgeMs)||
     options.maxAgeMs===0||options.maxAgeMs>60000)return empty(
       'BLOCKED_INVALID_CLOCK',['INVALID_CLOCK_OR_MAX_AGE']);
  if(!record(snapshot)||!exactKeys(snapshot,HEADER_FIELDS)){
    return empty('BLOCKED_SNAPSHOT_SCHEMA',['INCOMPLETE_OR_EXTRA_SNAPSHOT_FIELDS']);
  }
  if(snapshot.source!=='SYNTHETIC_FIXTURE'){
    return empty('BLOCKED_UNVERIFIED_SOURCE',['ONLY_SYNTHETIC_FIXTURES_SUPPORTED']);
  }
  if(snapshot.schemaVersion!==1||!validId(snapshot.snapshotId)||
     snapshot.coverage!=='ALL_ORDERS_AND_POSITIONS'||
     !safeInt(snapshot.capturedAtMs)||!safeInt(snapshot.longUnits)||
     !Array.isArray(snapshot.orders)||!record(snapshot.cash)||
     Object.keys(snapshot.cash).length!==CASH_FIELDS.length||
     Object.keys(snapshot.cash).some(k=>!CASH_FIELDS.includes(k))||
     CASH_FIELDS.some(k=>!accountValue(snapshot.cash[k]))){
    return empty('BLOCKED_SNAPSHOT_SCHEMA',['INVALID_OR_PARTIAL_SNAPSHOT']);
  }
  const ext=indexOrders(snapshot.orders);
  if(!ext)return empty('BLOCKED_SNAPSHOT_SCHEMA',['INVALID_OR_DUPLICATE_EXTERNAL_ORDER']);
  const age=options.observedAtMs-snapshot.capturedAtMs;
  if(age<0)reasons.push('FUTURE_SNAPSHOT');
  if(age>options.maxAgeMs)reasons.push('STALE_SNAPSHOT');
  if(recovered.journalHalted===true)reasons.push('JOURNAL_HALT_REQUIRES_OPERATOR_REVIEW');
  if(snapshot.longUnits!==recovered.longUnits)reasons.push('POSITION_QUANTITY_MISMATCH');

  for(const k of CASH_FIELDS)
    if(minor(snapshot.cash[k])!==minor(recovered[k]))
      reasons.push('CASH_FIELD_MISMATCH_'+k.toUpperCase());

  for(const [id,o] of local){
    if(!ext.has(id))reasons.push('ORDER_MISSING_FROM_EXTERNAL_SNAPSHOT');
    else if(!equalOrder(o,ext.get(id)))reasons.push('ORDER_STATE_OR_FILL_MISMATCH');
  }
  for(const [id] of ext)
    if(!local.has(id))reasons.push('EXTERNAL_ORDER_NOT_IN_JOURNAL');

  if([...local.values(),...ext.values()].some(o=>!FINAL.has(o.status)))
    reasons.push('UNRESOLVED_OPEN_ORDERS');
  // Even matching fixtures are not independent exchange/broker evidence.
  if(reasons.length)return empty('MISMATCH_HALT',reasons);
  return empty('SYNTHETIC_MATCH_EXTERNAL_AUTHENTICATION_REQUIRED',[
    'SYNTHETIC_DATA_CANNOT_AUTHORIZE_LIVE_TRADING'
  ]);
}

/** Two snapshots can expose drift; neither is authenticated broker evidence. */
export function auditPairedSyntheticSnapshots(recovered,a,b,options={}){
  const first=auditSyntheticBrokerSnapshot(recovered,a,options);
  const second=auditSyntheticBrokerSnapshot(recovered,b,options);
  const reasons=[...first.reasons,...second.reasons];
  if(!record(a)||!record(b)||!validId(a.snapshotId)||!validId(b.snapshotId)||
     a.snapshotId===b.snapshotId)reasons.push('NON_INDEPENDENT_SNAPSHOT_IDS');
  if(record(a)&&record(b)&&safeInt(a.capturedAtMs)&&safeInt(b.capturedAtMs)&&
     b.capturedAtMs<=a.capturedAtMs)reasons.push('NON_MONOTONIC_CAPTURE_TIMES');
  if(first.status!=='SYNTHETIC_MATCH_EXTERNAL_AUTHENTICATION_REQUIRED'||
     second.status!=='SYNTHETIC_MATCH_EXTERNAL_AUTHENTICATION_REQUIRED'||
     reasons.some(x=>x!=='SYNTHETIC_DATA_CANNOT_AUTHORIZE_LIVE_TRADING'))
    return empty('PAIRED_SNAPSHOT_HALT',reasons);
  return empty('PAIRED_SYNTHETIC_MATCH_EXTERNAL_AUTHENTICATION_REQUIRED',[
    'SYNTHETIC_DATA_CANNOT_AUTHORIZE_LIVE_TRADING',
    'REAL_BROKER_ACCOUNT_AND_ORDER_RECONCILIATION_NOT_IMPLEMENTED'
  ]);
}
