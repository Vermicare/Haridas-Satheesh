/**
 * QHAP-TRADER offline PAPER order-state reducer. No network, broker SDK,
 * authentication, external market feed, account connection, or real orders.
 * Events are hypothetical fixtures; success is not broker reconciliation.
 */
const IS_ID = /^[a-zA-Z0-9_-]{1,40}$/;
const validQty = n => Number.isSafeInteger(n) && n > 0;
const validPrice = n => typeof n === 'number' && Number.isFinite(n) && n > 0;

export function emptyJournal() {
  return {orders: {}, seen: {}, expectedSeq: 1, halted: false, haltReason: null,
    longUnits: 0, eventsApplied: 0, connection: 'OFFLINE',
    realOrderRoutePresent: false, realOrdersSent: 0, tradingAuthorized: false};
}
const failed = (s, why) => ({...s, halted: true, haltReason: why});
const terminal = o => ['FILLED','CANCELED','REJECTED'].includes(o.status);

export function applyPaperEvent(state, e) {
  if (!state || typeof state !== 'object' || !e || typeof e !== 'object') throw Error('INVALID_EVENT_OR_STATE');
  if (!IS_ID.test(e.eventId || '')) return failed(state, 'INVALID_EVENT_ID');
  const serialized = JSON.stringify(e);
  if (Object.hasOwn(state.seen, e.eventId))
    return state.seen[e.eventId] === serialized ? state : failed(state,'CONFLICTING_EVENT_REPLAY');
  if (state.halted) return state; // No magic restart or permission override.
  if (!Number.isSafeInteger(e.seq) || e.seq !== state.expectedSeq)
    return failed(state, 'OUT_OF_ORDER_EVENT');
  const orders = {...state.orders};
  const x = e.orderId && orders[e.orderId];
  let longUnits = state.longUnits;
  let failure = null;
  switch (e.type) {
    case 'CREATE': {
      if (!IS_ID.test(e.orderId || '') || x || !validQty(e.quantity) ||
          !validPrice(e.limitPrice) || !['BUY','SELL'].includes(e.side)) {failure='INVALID_CREATE'; break;}
      // New SELL intents may only reduce previously confirmed hypothetical long holdings.
      if (e.side === 'SELL') {
        const reserved = Object.values(orders).filter(o => o.side==='SELL' && !terminal(o))
          .reduce((a,o)=>a+(o.quantity-o.cumulativeFilled),0);
        if (e.quantity > longUnits-reserved) {failure='UNBACKED_SELL';break;}
      }
      orders[e.orderId] = {orderId:e.orderId, side:e.side, quantity:e.quantity,
        cumulativeFilled:0, limitPrice:e.limitPrice, status:'PENDING_ACK',
        cancelRequested:false};
      break;
    }
    case 'ACK': {
      if (!x || x.status!=='PENDING_ACK') {failure='INVALID_ACK';break;}
      orders[e.orderId] = {...x,status:'ACKNOWLEDGED'};break;
    }
    case 'FILL': {
      if (!x || terminal(x) || !['PENDING_ACK','ACKNOWLEDGED','PARTIALLY_FILLED','CANCEL_PENDING'].includes(x.status)
        || !validQty(e.cumulativeFilled) || !validPrice(e.fillPrice)
        || e.cumulativeFilled <= x.cumulativeFilled || e.cumulativeFilled > x.quantity) {
        failure='INVALID_FILL';break;
      }
      const delta = e.cumulativeFilled-x.cumulativeFilled;
      if (x.side==='SELL' && delta>longUnits) {failure='SELL_FILL_EXCEEDS_HOLDINGS';break;}
      longUnits += x.side==='BUY' ? delta : -delta;
      orders[e.orderId]={...x,cumulativeFilled:e.cumulativeFilled,
        status:e.cumulativeFilled===x.quantity?'FILLED':x.cancelRequested?'CANCEL_PENDING':'PARTIALLY_FILLED'};
      break;
    }
    case 'CANCEL_REQUEST': {
      if (!x || terminal(x) || x.cancelRequested) {failure='INVALID_CANCEL_REQUEST';break;}
      orders[e.orderId]={...x,cancelRequested:true,status:'CANCEL_PENDING'};break;
    }
    case 'CANCEL_ACK': {
      if (!x || !x.cancelRequested || terminal(x)) {failure='INVALID_CANCEL_ACK';break;}
      orders[e.orderId]={...x,status:'CANCELED'};break;
    }
    case 'REJECT': {
      if (!x || terminal(x) || x.cumulativeFilled>0) {failure='REJECT_CONFLICTS_WITH_FILLS';break;}
      orders[e.orderId]={...x,status:'REJECTED'};break;
    }
    case 'DISCONNECT':
      // An uncertain connection never implies cancellation or flat holdings.
      return failed({...state,connection:'DISCONNECTED'},'CONNECTION_LOST_RECONCILIATION_REQUIRED');
    default: failure='UNKNOWN_EVENT_TYPE';
  }
  if (failure) return failed(state, failure);
  return {...state,orders,longUnits,seen:{...state.seen,[e.eventId]:serialized},
    expectedSeq:state.expectedSeq+1,eventsApplied:state.eventsApplied+1};
}

export function reducePaperEvents(events, starting=emptyJournal()) {
  if (!Array.isArray(events) || events.length>100000) throw Error('INVALID_EVENT_BATCH');
  return events.reduce(applyPaperEvent, starting);
}
export function paperStatus(state) {
  if (!state || typeof state !== 'object') throw Error('INVALID_STATE');
  return {halted:state.halted,haltReason:state.haltReason,
    longUnits:state.longUnits,eventsApplied:state.eventsApplied,
    orders:Object.values(state.orders).map(o=>({orderId:o.orderId,status:o.status,
      quantity:o.quantity,cumulativeFilled:o.cumulativeFilled})),
    realOrderRoutePresent:false,realOrdersSent:0,tradingAuthorized:false,
    brokerReconciled:false,productionSafe:false};
}
