/**
 * QHAP-TRADER: documentation-shaped UPSTOX *SYNTHETIC* audit only.
 *
 * This module has no network, tokens, OAuth, SDK, broker accounts or order route.
 * Inputs must be hand-authored/redacted mock subsets of documented Upstox
 * response fields; actual broker responses are deliberately NOT accepted here.
 * Even a perfectly formed mock cannot establish account identity, complete
 * order coverage, real positions, funds, data entitlements or launch readiness.
 *
 * Docs consulted 2026-11-12:
 * https://upstox.com/developer/api-documentation/get-order-book/
 * https://upstox.com/developer/api-documentation/get-positions/
 * https://upstox.com/developer/api-documentation/get-holdings/
 * https://upstox.com/developer/api-documentation/get-funds-and-margin-v3/
 * https://upstox.com/developer/api-documentation/appendix/order-status/
 */
const record=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const exact=(x,names)=>record(x)&&Object.keys(x).length===names.length&&
  Object.keys(x).every(k=>names.includes(k));
const integer=n=>Number.isSafeInteger(n)&&n>=0;
const nonnegative=n=>typeof n==='number'&&Number.isFinite(n)&&n>=0;
const ID=/^[A-Za-z0-9_-]{1,40}$/;
const TOKEN=/^NSE_EQ\|[A-Za-z0-9]+$/;
const TOP=['fixtureKind','captureId','sessionKey','capturedAtMs','coverage',
  'orderBook','positions','holdings','fundsV3'];
const COVER=['ordersComplete','positionsComplete','holdingsComplete','fundsComplete'];
const ORDER=['order_id','quantity','filled_quantity','pending_quantity',
  'status','exchange','product','instrument_token','transaction_type','order_type'];
const POSITION=['instrument_token','exchange','product','quantity'];
const HOLDING=['instrument_token','exchange','product','quantity',
  't1_quantity','collateral_quantity'];
const FINAL=new Set(['complete','cancelled','cancelled after market order','rejected']);
const ACTIVE=new Set([
  'validation pending','modify pending','trigger pending','put order req received',
  'modify after market order req received','open','modify validation pending',
  'after market order req received','modified','not cancelled','cancel pending',
  'open pending','not modified'
]);
function output(status,reasons,counts={}) {
  return Object.freeze({
    status,reasons:[...new Set(reasons)].sort(),
    syntheticFixtureOnly:true,docShapeInspected:status!=='BLOCKED_INVALID_FIXTURE',
    orderCount:counts.orderCount||0,positionCount:counts.positionCount||0,
    holdingCount:counts.holdingCount||0,unresolvedOrderCount:counts.unresolvedOrderCount||0,
    realOrdersSent:0,realOrderRoutePresent:false,canTrade:false,
    liveTradingAuthorized:false,brokerReconciled:false,
    accountIdentityVerified:false,completenessExternallyVerified:false,
    manualReviewRequired:true
  });
}
function parse(p,opts) {
  const reasons=[];
  if(!record(opts)||!integer(opts.observedAtMs)||!integer(opts.maxAgeMs)||
    opts.maxAgeMs<1||opts.maxAgeMs>60000) {
    return {reasons:['INVALID_OBSERVATION_CLOCK']};
  }
  if(!exact(p,TOP)||p.fixtureKind!=='SYNTHETIC_UPSTOX_DOC_SHAPE'||
    typeof p.captureId!=='string'||!ID.test(p.captureId)||
    typeof p.sessionKey!=='string'||!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(p.sessionKey)||
    !integer(p.capturedAtMs)||!exact(p.coverage,COVER)||
    COVER.some(k=>p.coverage[k]!==true)) {
    return {reasons:['INVALID_OR_PARTIAL_FIXTURE_ENVELOPE']};
  }
  if(p.capturedAtMs>opts.observedAtMs)reasons.push('FUTURE_CAPTURE');
  if(opts.observedAtMs-p.capturedAtMs>opts.maxAgeMs)reasons.push('STALE_CAPTURE');
  const apiArray=x=>exact(x,['status','data'])&&x.status==='success'&&Array.isArray(x.data);
  if(!apiArray(p.orderBook)||!apiArray(p.positions)||!apiArray(p.holdings)||
    !exact(p.fundsV3,['status','data'])||p.fundsV3.status!=='success') {
    return {reasons:[...reasons,'MISSING_OR_FAILED_API_RESPONSE']};
  }
  const orders=new Map();
  let unresolved=0;
  const instruments=new Set();
  for(const x of p.orderBook.data) {
    if(!exact(x,ORDER)||!ID.test(x.order_id||'')||
      !integer(x.quantity)||x.quantity===0||!integer(x.filled_quantity)||
      !integer(x.pending_quantity)||x.filled_quantity>x.quantity||
      x.filled_quantity+x.pending_quantity>x.quantity||
      x.exchange!=='NSE'||x.product!=='D'||!TOKEN.test(x.instrument_token||'')||
      !['BUY','SELL'].includes(x.transaction_type)||x.order_type!=='LIMIT') {
      reasons.push('INVALID_OR_UNSUPPORTED_ORDER');continue;
    }
    if(!FINAL.has(x.status)&&!ACTIVE.has(x.status)) {
      reasons.push('UNKNOWN_ORDER_STATUS');continue;
    }
    if((x.status==='complete'&&(x.filled_quantity!==x.quantity||x.pending_quantity!==0))||
      (x.status==='rejected'&&x.filled_quantity!==0)) {
      reasons.push('INCONSISTENT_TERMINAL_ORDER');continue;
    }
    if(orders.has(x.order_id)){reasons.push('DUPLICATE_ORDER_ID');continue;}
    orders.set(x.order_id,x);
    instruments.add(x.instrument_token);
    if(ACTIVE.has(x.status))unresolved++;
  }
  const positionBook=new Set(),holdingBook=new Set();
  for(const x of p.positions.data) {
    if(!exact(x,POSITION)||!TOKEN.test(x.instrument_token||'')||
      x.exchange!=='NSE'||x.product!=='D'||!integer(x.quantity)) {
      reasons.push('INVALID_OR_UNSUPPORTED_POSITION');continue;
    }
    if(positionBook.has(x.instrument_token))reasons.push('DUPLICATE_POSITION');
    positionBook.add(x.instrument_token);instruments.add(x.instrument_token);
  }
  for(const x of p.holdings.data) {
    if(!exact(x,HOLDING)||!TOKEN.test(x.instrument_token||'')||
      x.exchange!=='NSE'||x.product!=='D'||!integer(x.quantity)||
      !integer(x.t1_quantity)||!integer(x.collateral_quantity)) {
      reasons.push('INVALID_OR_UNSUPPORTED_HOLDING');continue;
    }
    if(x.collateral_quantity>0)reasons.push('PLEDGED_HOLDING_NOT_SUPPORTED');
    if(holdingBook.has(x.instrument_token))reasons.push('DUPLICATE_HOLDING');
    holdingBook.add(x.instrument_token);instruments.add(x.instrument_token);
  }
  if([...holdingBook].some(k=>positionBook.has(k)))
    reasons.push('POSITION_HOLDING_OVERLAP_UNRESOLVED');
  if(instruments.size>1)reasons.push('MULTI_INSTRUMENT_BOOK_UNSUPPORTED');
  const funds=p.fundsV3.data;
  if(!exact(funds,['available_to_trade','unavailable_to_trade'])||
    !exact(funds.available_to_trade,['cash_available_to_trade','pledge_available_to_trade'])||
    !exact(funds.available_to_trade.cash_available_to_trade,['total'])||
    !exact(funds.available_to_trade.pledge_available_to_trade,['total'])||
    !exact(funds.unavailable_to_trade,['cash_unavailable_to_trade'])||
    !exact(funds.unavailable_to_trade.cash_unavailable_to_trade,['unsettled_profit'])||
    !exact(funds.unavailable_to_trade.cash_unavailable_to_trade.unsettled_profit,
      ['todays_profit','previous_days'])) {
    reasons.push('INVALID_FUNDS_V3_FIXTURE');
  } else {
    const cash=funds.available_to_trade.cash_available_to_trade.total;
    const pledge=funds.available_to_trade.pledge_available_to_trade.total;
    const profits=funds.unavailable_to_trade.cash_unavailable_to_trade.unsettled_profit;
    if(!nonnegative(cash)||!nonnegative(pledge)||
      !Number.isFinite(profits.todays_profit)||
      !Number.isFinite(profits.previous_days))
      reasons.push('INVALID_FUND_VALUES');
    if(pledge>0)reasons.push('PLEDGED_MARGIN_NOT_SUPPORTED');
  }
  if(unresolved>0)reasons.push('UNRESOLVED_ORDER_STATES');
  const counts={orderCount:orders.size,positionCount:positionBook.size,
    holdingCount:holdingBook.size,unresolvedOrderCount:unresolved};
  return {reasons,orders,counts,sessionKey:p.sessionKey,capturedAtMs:p.capturedAtMs,
    captureId:p.captureId};
}
/** Return sanitized result only. Always fail-closed for actual trading. */
export function auditUpstoxDocShapedFixture(packet,options={}) {
  const x=parse(packet,options);
  return output(x.reasons.length?'SYNTHETIC_SHAPE_HALT':'SYNTHETIC_SHAPE_ONLY_NOT_AUTHENTICATED',
    x.reasons.length?x.reasons:['NO_ACTUAL_BROKER_RECONCILIATION'],x.counts);
}
/**
 * Within one synthetic session, a newer *complete* order book cannot omit an
 * earlier order, reverse cumulative fills, regress a final status, or move
 * backward in wall-clock capture order. This does NOT certify exchange events.
 */
export function auditPairedUpstoxDocShapedFixtures(a,b,options={}) {
  const x=parse(a,options),y=parse(b,options);
  const reasons=[...x.reasons,...y.reasons];
  if(x.orders&&y.orders) {
    if(x.sessionKey!==y.sessionKey)reasons.push('SESSION_BOUNDARY_REQUIRES_REBASE');
    if(x.captureId===y.captureId)reasons.push('REUSED_CAPTURE_ID');
    if(y.capturedAtMs<=x.capturedAtMs)reasons.push('NON_MONOTONIC_CAPTURE');
    for(const [id,o] of x.orders) {
      const next=y.orders.get(id);
      if(!next){reasons.push('ORDER_DISAPPEARED_FROM_COMPLETE_BOOK');continue;}
      if(next.filled_quantity<o.filled_quantity)reasons.push('CUMULATIVE_FILL_REGRESSION');
      if(next.quantity!==o.quantity||next.instrument_token!==o.instrument_token||
        next.transaction_type!==o.transaction_type)
        reasons.push('ORDER_IDENTITY_CHANGED');
      if(FINAL.has(o.status)&&next.status!==o.status)
        reasons.push('FINAL_ORDER_STATUS_REWRITTEN');
    }
  } else reasons.push('UNPARSEABLE_CAPTURE_PAIR');
  return output(reasons.length?'PAIRED_SYNTHETIC_HALT':'PAIRED_SYNTHETIC_SHAPE_ONLY',
    reasons.length?reasons:['NO_ACTUAL_BROKER_RECONCILIATION'],y.counts);
}
