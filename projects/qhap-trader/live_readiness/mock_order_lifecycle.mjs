/**
 * Offline MOCK-ONLY order lifecycle model.
 * No broker SDK, HTTP, credentials, network, order submission or cancellation.
 * Represents failure modes a future broker integration must handle.
 */

const isRecord=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const integer=x=>Number.isSafeInteger(x);
const validPositive=x=>typeof x==='number'&&Number.isFinite(x)&&x>0;
const stop=(state,code)=>{
  return {...state,status:'HALTED',riskLocked:true,haltReason:code,
    reconciliationRequired:true,realOrdersSent:0};
};

export function createMockOrder({clientOrderKey,quantity,limitPrice,instrumentKey}={}) {
  if(typeof clientOrderKey!=='string'||!/^QHAP-[A-Za-z0-9_-]{6,60}$/.test(clientOrderKey))
    throw Error('INVALID_MOCK_CLIENT_KEY');
  if(!integer(quantity)||quantity<1||quantity>100000)throw Error('INVALID_MOCK_QUANTITY');
  if(!validPositive(limitPrice))throw Error('INVALID_MOCK_LIMIT_PRICE');
  if(typeof instrumentKey!=='string'||!/^NSE_EQ\|[A-Z0-9]{8,20}$/.test(instrumentKey))
    throw Error('INVALID_MOCK_INSTRUMENT');
  return Object.freeze({
    mode:'MOCK_ONLY',clientOrderKey,quantity,limitPrice,instrumentKey,
    status:'DRAFT',filledQuantity:0,filledNotional:0,remainingQuantity:quantity,
    cancelPending:false,lastSequence:0,seenEventIds:[],
    riskLocked:true,reconciliationRequired:false,haltReason:null,
    realOrdersSent:0,brokerOrderRoutePresent:false,
  });
}

const TERMINAL=new Set(['FILLED','CANCELLED','CANCELLED_PARTIAL','REJECTED','REJECTED_PARTIAL','HALTED']);
/**
 * Event is an isolated synthetic broker-like receipt, never an exchange message.
 * No replay of a completed event; rejects sequence gaps instead of guessing order state.
 * Returns a new state, preserving observed partial fills even if a cancel/reject races.
 */
export function applyMockEvent(state,event) {
  if(!isRecord(state)||state.mode!=='MOCK_ONLY'||!integer(state.quantity)||
     !integer(state.filledQuantity)||!integer(state.remainingQuantity)||
     state.realOrdersSent!==0 || state.brokerOrderRoutePresent!==false)
    throw Error('INVALID_MOCK_STATE');
  if(!isRecord(event)||event.source!=='SYNTHETIC_ONLY')return stop(state,'UNTRUSTED_EVENT_SOURCE');
  if(typeof event.eventId!=='string'||!/^E-[A-Za-z0-9_-]{4,40}$/.test(event.eventId))
    return stop(state,'BAD_EVENT_ID');
  if(state.seenEventIds.includes(event.eventId))
    return {...state,duplicateEventIgnored:true};
  if(state.status==='HALTED')return {...state,duplicateEventIgnored:false};
  if(!integer(event.sequence)||event.sequence!==state.lastSequence+1)
    return stop(state,'MISSING_OR_OUT_OF_ORDER_EVENT');
  if(TERMINAL.has(state.status))return stop(state,'EVENT_AFTER_TERMINAL');
  let newState={...state,seenEventIds:[...state.seenEventIds,event.eventId],
    lastSequence:event.sequence,duplicateEventIgnored:false};
  switch(event.type) {
    case 'ACK':
      if(state.status!=='DRAFT')return stop(newState,'ACK_IN_ILLEGAL_STATE');
      newState.status='WORKING';break;
    case 'FILL': {
      if(!['WORKING','PARTIAL','CANCEL_PENDING'].includes(state.status))
        return stop(newState,'FILL_BEFORE_ACK_OR_INVALID_STATE');
      if(!integer(event.fillQuantity)||event.fillQuantity<1||
         !validPositive(event.fillPrice)||event.fillQuantity>state.remainingQuantity)
        return stop(newState,'INVALID_OR_OVERFILL_RECEIPT');
      newState.filledQuantity=state.filledQuantity+event.fillQuantity;
      newState.remainingQuantity=state.quantity-newState.filledQuantity;
      newState.filledNotional=state.filledNotional+event.fillQuantity*event.fillPrice;
      if(newState.remainingQuantity===0){newState.status='FILLED';newState.cancelPending=false;}
      else newState.status=state.cancelPending?'CANCEL_PENDING':'PARTIAL';
      break;
    }
    case 'CANCEL_REQUESTED':
      if(!['WORKING','PARTIAL'].includes(state.status))
        return stop(newState,'CANCEL_IN_ILLEGAL_STATE');
      newState.status='CANCEL_PENDING';newState.cancelPending=true;break;
    case 'CANCEL_ACK':
      if(state.status!=='CANCEL_PENDING')
        return stop(newState,'CANCEL_ACK_NOT_PENDING');
      newState.status=newState.filledQuantity>0?'CANCELLED_PARTIAL':'CANCELLED';
      newState.cancelPending=false;break;
    case 'REJECT':
      if(!['DRAFT','WORKING','PARTIAL','CANCEL_PENDING'].includes(state.status))
        return stop(newState,'REJECTION_INVALID_STATE');
      newState.status=newState.filledQuantity>0?'REJECTED_PARTIAL':'REJECTED';
      newState.cancelPending=false;break;
    case 'DISCONNECT':
      return stop(newState,'CONNECTION_LOSS_RECONCILIATION_NEEDED');
    case 'INCONSISTENT_ACCOUNT_SNAPSHOT':
      return stop(newState,'ACCOUNT_RECONCILIATION_MISMATCH');
    default: return stop(newState,'UNKNOWN_EVENT_TYPE');
  }
  // Risk lock never becomes false merely because synthetic lifecycle looks healthy.
  newState.riskLocked=true;
  newState.realOrdersSent=0;
  newState.brokerOrderRoutePresent=false;
  return Object.freeze(newState);
}

export function mockLifecycleSummary(state) {
  if(!isRecord(state)||state.mode!=='MOCK_ONLY')throw Error('INVALID_MOCK_STATE');
  return Object.freeze({
    mode:'MOCK_ONLY',status:state.status,
    filledQuantity:state.filledQuantity,remainingQuantity:state.remainingQuantity,
    reconciliationRequired:state.reconciliationRequired,
    riskLocked:true,
    complete:false,
    liveTradingAuthorized:false,
    brokerOrderRoutePresent:false,
    realOrdersSent:0,
  });
}
