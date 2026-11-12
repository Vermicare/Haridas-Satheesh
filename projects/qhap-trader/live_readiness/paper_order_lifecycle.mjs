/**
 * QHAP-TRADER OFFLINE hypothetical paper order reducer.
 * No broker endpoint, network, execution authority, live credentials or market feed.
 * From 2026-11-12: capital conservation and pending-order reservations are enforced
 * INSIDE the reducer. This does not certify broker cash/margin, charges or fills.
 */
const IS_ID=/^[a-zA-Z0-9_-]{1,40}$/;
const validQty=n=>Number.isSafeInteger(n)&&n>0;
const validPrice=n=>typeof n==='number'&&Number.isFinite(n)&&n>0&&
  Number.isSafeInteger(Math.round(n*100))&&Math.abs(n*100-Math.round(n*100))<1e-6;
const toPaise=n=>Math.round(n*100);
const START_CASH=1_000_000; // 10,000 INR
const POSITION_CAP=250_000; // 2,500 INR
const MIN_CASH=400_000; // 4,000 INR kept liquid
const RESERVE_BPS=100; // reserve 1% hypothetical entry-cost buffer
const FILL_FRICTION_BPS=30; // illustrative, not current verified broker schedule
const safe=n=>Number.isSafeInteger(n)&&n>=0;
const remaining=o=>o.quantity-o.cumulativeFilled;
const terminal=o=>['FILLED','CANCELED','REJECTED'].includes(o.status);
const rupees=paise=>Math.round(paise)/100;
const buyOrders=orders=>Object.values(orders).filter(o=>o.side==='BUY'&&!terminal(o));
const committed=(positionCostPaise,orders)=>
  positionCostPaise+buyOrders(orders).reduce((a,o)=>a+o.notionalReservePaise,0);
const guard=s=>{
  const names=['cashAvailablePaise','cashReservedPaise','capitalSpentPaise',
    'unsettledSaleProceedsPaise','positionCostPaise'];
  if(names.some(k=>!safe(s[k]))||s.cashAvailablePaise+s.cashReservedPaise+s.capitalSpentPaise!==START_CASH||
    s.positionCostPaise>POSITION_CAP||committed(s.positionCostPaise,s.orders)>POSITION_CAP||
    !safe(s.longUnits))return 'CAPITAL_CONSERVATION_BREACH';
  return null;
};
const failed=(s,reason)=>({...s,halted:true,haltReason:reason});
export function emptyJournal(){
  return {orders:{},seen:{},expectedSeq:1,halted:false,haltReason:null,
    longUnits:0,eventsApplied:0,connection:'OFFLINE',
    cashAvailablePaise:START_CASH,cashReservedPaise:0,capitalSpentPaise:0,
    unsettledSaleProceedsPaise:0,positionCostPaise:0,
    buyIntentCount:0,
    realOrderRoutePresent:false,realOrdersSent:0,tradingAuthorized:false};
}

export function applyPaperEvent(state,e){
  if(!state||typeof state!=='object'||!e||typeof e!=='object')
    throw Error('INVALID_EVENT_OR_STATE');
  if(!IS_ID.test(e.eventId||''))return failed(state,'INVALID_EVENT_ID');
  const serialized=JSON.stringify(e);
  if(Object.hasOwn(state.seen,e.eventId))
    return state.seen[e.eventId]===serialized?state:failed(state,'CONFLICTING_EVENT_REPLAY');
  if(state.halted)return state;
  if(guard(state))return failed(state,'CAPITAL_STATE_INVALID');
  if(!Number.isSafeInteger(e.seq)||e.seq!==state.expectedSeq)
    return failed(state,'OUT_OF_ORDER_EVENT');

  const orders={...state.orders};
  const order=e.orderId&&orders[e.orderId];
  let longUnits=state.longUnits;
  let cashAvailablePaise=state.cashAvailablePaise;
  let cashReservedPaise=state.cashReservedPaise;
  let capitalSpentPaise=state.capitalSpentPaise;
  let unsettledSaleProceedsPaise=state.unsettledSaleProceedsPaise;
  let positionCostPaise=state.positionCostPaise;
  let buyIntentCount=state.buyIntentCount;
  let failure=null;

  switch(e.type){
    case 'CREATE':{
      if(!IS_ID.test(e.orderId||'')||order||!validQty(e.quantity)||
        !validPrice(e.limitPrice)||!['BUY','SELL'].includes(e.side)){
        failure='INVALID_CREATE';break;
      }
      if(e.side==='BUY'){
        const limitNotional=toPaise(e.limitPrice)*e.quantity;
        const perUnitReservePaise=Math.ceil(toPaise(e.limitPrice)*(10000+RESERVE_BPS)/10000);
        const buyReserve=perUnitReservePaise*e.quantity;
        if(!safe(limitNotional)||!safe(buyReserve)){failure='NOTIONAL_OVERFLOW';break;}
        if(committed(positionCostPaise,orders)+limitNotional>POSITION_CAP){
          failure='POSITION_NOTIONAL_CAP';break;
        }
        if(buyReserve>cashAvailablePaise||
          cashAvailablePaise-buyReserve<MIN_CASH){
          failure='INSUFFICIENT_RESERVED_CASH';break;
        }
        if(buyIntentCount>=2){failure='PAPER_ENTRY_COUNT_CAP';break;}
        cashAvailablePaise-=buyReserve;
        cashReservedPaise+=buyReserve;
        buyIntentCount++;
        orders[e.orderId]={orderId:e.orderId,side:e.side,quantity:e.quantity,
          cumulativeFilled:0,limitPrice:e.limitPrice,status:'PENDING_ACK',
          cancelRequested:false,cashReservePaise:buyReserve,perUnitReservePaise,
          notionalReservePaise:limitNotional};
      }else{
        const alreadyReserved=Object.values(orders).filter(o=>o.side==='SELL'&&!terminal(o))
          .reduce((a,o)=>a+remaining(o),0);
        if(e.quantity>longUnits-alreadyReserved){failure='UNBACKED_SELL';break;}
        orders[e.orderId]={orderId:e.orderId,side:e.side,quantity:e.quantity,
          cumulativeFilled:0,limitPrice:e.limitPrice,status:'PENDING_ACK',
          cancelRequested:false,cashReservePaise:0,perUnitReservePaise:0,
          notionalReservePaise:0};
      }
      break;
    }
    case 'ACK':{
      if(!order||order.status!=='PENDING_ACK'){failure='INVALID_ACK';break;}
      orders[e.orderId]={...order,status:'ACKNOWLEDGED'};
      break;
    }
    case 'FILL':{
      if(!order||terminal(order)||
        !['PENDING_ACK','ACKNOWLEDGED','PARTIALLY_FILLED','CANCEL_PENDING'].includes(order.status)||
        !validQty(e.cumulativeFilled)||!validPrice(e.fillPrice)||
        e.cumulativeFilled<=order.cumulativeFilled||e.cumulativeFilled>order.quantity){
        failure='INVALID_FILL';break;
      }
      const delta=e.cumulativeFilled-order.cumulativeFilled;
      const price=toPaise(e.fillPrice),limit=toPaise(order.limitPrice);
      // A limit BUY cannot execute above its limit; a limit SELL cannot execute below it.
      if(order.side==='BUY'&&price>limit){failure='BUY_LIMIT_BREACH';break;}
      if(order.side==='SELL'&&price<limit){failure='SELL_LIMIT_BREACH';break;}
      if(order.side==='BUY'){
        const released=order.perUnitReservePaise*delta;
        const spend=Math.ceil(price*(10000+FILL_FRICTION_BPS)/10000)*delta;
        if(!safe(spend)||spend>released){failure='BUY_RESERVE_INSUFFICIENT';break;}
        cashReservedPaise-=released;
        cashAvailablePaise+=released-spend;
        capitalSpentPaise+=spend;
        positionCostPaise+=price*delta;
        longUnits+=delta;
        orders[e.orderId]={...order,cumulativeFilled:e.cumulativeFilled,
          cashReservePaise:order.cashReservePaise-released,
          notionalReservePaise:order.notionalReservePaise-limit*delta,
          status:e.cumulativeFilled===order.quantity?'FILLED':
            order.cancelRequested?'CANCEL_PENDING':'PARTIALLY_FILLED'};
      }else{
        if(delta>longUnits){failure='SELL_FILL_EXCEEDS_HOLDINGS';break;}
        const costRelief=delta===longUnits?positionCostPaise:
          Math.floor(positionCostPaise*delta/longUnits);
        positionCostPaise-=costRelief;
        longUnits-=delta;
        // Cash proceeds are deliberately QUARANTINED: no intraday reuse by inference.
        const proceeds=Math.floor(price*delta*(10000-FILL_FRICTION_BPS)/10000);
        unsettledSaleProceedsPaise+=proceeds;
        orders[e.orderId]={...order,cumulativeFilled:e.cumulativeFilled,
          status:e.cumulativeFilled===order.quantity?'FILLED':
            order.cancelRequested?'CANCEL_PENDING':'PARTIALLY_FILLED'};
      }
      break;
    }
    case 'CANCEL_REQUEST':{
      if(!order||terminal(order)||order.cancelRequested){
        failure='INVALID_CANCEL_REQUEST';break;
      }
      orders[e.orderId]={...order,cancelRequested:true,status:'CANCEL_PENDING'};
      break;
    }
    case 'CANCEL_ACK':{
      if(!order||!order.cancelRequested||terminal(order)){
        failure='INVALID_CANCEL_ACK';break;
      }
      if(order.side==='BUY'){
        cashReservedPaise-=order.cashReservePaise;
        cashAvailablePaise+=order.cashReservePaise;
      }
      orders[e.orderId]={...order,status:'CANCELED',
        cashReservePaise:0,notionalReservePaise:0};
      break;
    }
    case 'REJECT':{
      if(!order||terminal(order)||order.cumulativeFilled>0){
        failure='REJECT_CONFLICTS_WITH_FILLS';break;
      }
      if(order.side==='BUY'){
        cashReservedPaise-=order.cashReservePaise;
        cashAvailablePaise+=order.cashReservePaise;
      }
      orders[e.orderId]={...order,status:'REJECTED',
        cashReservePaise:0,notionalReservePaise:0};
      break;
    }
    case 'DISCONNECT':
      return failed({...state,connection:'DISCONNECTED'},
        'CONNECTION_LOST_RECONCILIATION_REQUIRED');
    default:failure='UNKNOWN_EVENT_TYPE';
  }
  if(failure)return failed(state,failure);
  const next={...state,orders,longUnits,cashAvailablePaise,cashReservedPaise,
    capitalSpentPaise,unsettledSaleProceedsPaise,positionCostPaise,buyIntentCount,
    seen:{...state.seen,[e.eventId]:serialized},
    expectedSeq:state.expectedSeq+1,eventsApplied:state.eventsApplied+1};
  return guard(next)?failed(state,'CAPITAL_CONSERVATION_BREACH'):next;
}

export function reducePaperEvents(events,starting=emptyJournal()){
  if(!Array.isArray(events)||events.length>100000)throw Error('INVALID_EVENT_BATCH');
  return events.reduce(applyPaperEvent,starting);
}
export function paperStatus(state){
  if(!state||typeof state!=='object')throw Error('INVALID_STATE');
  return {halted:state.halted,haltReason:state.haltReason,
    longUnits:state.longUnits,eventsApplied:state.eventsApplied,
    orders:Object.values(state.orders).map(o=>({orderId:o.orderId,status:o.status,
      quantity:o.quantity,cumulativeFilled:o.cumulativeFilled})),
    cashAvailableRupees:rupees(state.cashAvailablePaise),
    cashReservedRupees:rupees(state.cashReservedPaise),
    cashSpentRupees:rupees(state.capitalSpentPaise),
    unsettledSaleProceedsRupees:rupees(state.unsettledSaleProceedsPaise),
    positionCostRupees:rupees(state.positionCostPaise),
    committedExposureRupees:rupees(committed(state.positionCostPaise,state.orders)),
    simulatedCapitalRupees:rupees(START_CASH),
    realOrderRoutePresent:false,realOrdersSent:0,tradingAuthorized:false,
    brokerReconciled:false,productionSafe:false};
}
