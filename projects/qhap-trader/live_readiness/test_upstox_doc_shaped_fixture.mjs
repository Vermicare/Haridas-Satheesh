import test from 'node:test';
import assert from 'node:assert/strict';
import {auditUpstoxDocShapedFixture as audit,
  auditPairedUpstoxDocShapedFixtures as pair} from './upstox_doc_shaped_fixture.mjs';

const options={observedAtMs:10000,maxAgeMs:500};
const token='NSE_EQ|INE1234567890';
const order=(changes={})=>({
  order_id:'A1',quantity:3,filled_quantity:3,pending_quantity:0,
  status:'complete',exchange:'NSE',product:'D',
  instrument_token:token,transaction_type:'BUY',order_type:'LIMIT',...changes
});
const position=(changes={})=>({instrument_token:token,exchange:'NSE',
  product:'D',quantity:3,...changes});
const holding=(changes={})=>({instrument_token:token,exchange:'NSE',
  product:'D',quantity:3,t1_quantity:0,collateral_quantity:0,...changes});
const fresh=()=>({
  fixtureKind:'SYNTHETIC_UPSTOX_DOC_SHAPE',
  captureId:'S1',sessionKey:'2026-11-12',capturedAtMs:9800,
  coverage:{ordersComplete:true,positionsComplete:true,holdingsComplete:true,
    fundsComplete:true},
  orderBook:{status:'success',data:[]},
  positions:{status:'success',data:[]},
  holdings:{status:'success',data:[]},
  fundsV3:{status:'success',data:{
    available_to_trade:{
      cash_available_to_trade:{total:10000},
      pledge_available_to_trade:{total:0}
    },
    unavailable_to_trade:{
      cash_unavailable_to_trade:{unsettled_profit:{
        todays_profit:0,previous_days:0
      }}
    }
  }}
});
const check=(x,o=options)=>audit(x,o);
function reason(x,r){const out=check(x);assert.equal(out.status,'SYNTHETIC_SHAPE_HALT');
  assert.ok(out.reasons.includes(r),JSON.stringify(out));assert.equal(out.canTrade,false);}
test('clean empty document-shaped synthetic mock never authenticates broker',()=>{
  const out=check(fresh());
  assert.equal(out.status,'SYNTHETIC_SHAPE_ONLY_NOT_AUTHENTICATED');
  assert.equal(out.brokerReconciled,false);assert.equal(out.liveTradingAuthorized,false);
  assert.equal(out.realOrderRoutePresent,false);assert.equal(out.canTrade,false);
});
test('complete NSE delivery LIMIT buy accepted for mock shape only',()=>{
  const x=fresh();x.orderBook.data=[order()];x.positions.data=[position()];
  assert.equal(check(x).status,'SYNTHETIC_SHAPE_ONLY_NOT_AUTHENTICATED');
});
test('completed cancelled order with partial fill remains terminal for mock',()=>{
  const x=fresh();x.orderBook.data=[order({status:'cancelled',filled_quantity:1,pending_quantity:2})];
  assert.equal(check(x).status,'SYNTHETIC_SHAPE_ONLY_NOT_AUTHENTICATED');
});
test('open order blocks even when data is syntactically complete',()=>{
  const x=fresh();x.orderBook.data=[order({status:'open',filled_quantity:1,pending_quantity:2})];
  reason(x,'UNRESOLVED_ORDER_STATES');
  assert.equal(check(x).unresolvedOrderCount,1);
});
test('cancel pending and modify pending are never assumed terminal',()=>{
  for(const status of ['cancel pending','modify pending','not cancelled','validation pending']) {
    const x=fresh();x.orderBook.data=[order({status,filled_quantity:0,pending_quantity:3})];
    reason(x,'UNRESOLVED_ORDER_STATES');
  }
});
test('unknown/new order status is fail-closed',()=>{
  const x=fresh();x.orderBook.data=[order({status:'magically complete'})];
  reason(x,'UNKNOWN_ORDER_STATUS');
});
test('complete status with partial quantity is invalid',()=>{
  const x=fresh();x.orderBook.data=[order({filled_quantity:2,pending_quantity:1})];
  reason(x,'INCONSISTENT_TERMINAL_ORDER');
});
test('rejected with filled units cannot be trusted',()=>{
  const x=fresh();x.orderBook.data=[order({status:'rejected'})];
  reason(x,'INCONSISTENT_TERMINAL_ORDER');
});
test('overfilled quantity and impossible pending sum block',()=>{
  for(const changes of [{filled_quantity:4},{filled_quantity:2,pending_quantity:2}]) {
    const x=fresh();x.orderBook.data=[order(changes)];
    reason(x,'INVALID_OR_UNSUPPORTED_ORDER');
  }
});
test('duplicate broker-shaped order ids block',()=>{
  const x=fresh();x.orderBook.data=[order(),order()];
  reason(x,'DUPLICATE_ORDER_ID');
});
test('source marker must explicitly state mock only',()=>{
  const x=fresh();x.fixtureKind='UPSTOX_LIVE';
  reason(x,'INVALID_OR_PARTIAL_FIXTURE_ENVELOPE');
});
test('claimed partial order coverage never interpreted as zero orders',()=>{
  const x=fresh();x.coverage.ordersComplete=false;
  reason(x,'INVALID_OR_PARTIAL_FIXTURE_ENVELOPE');
});
test('missing holdings coverage and failed funds response halt',()=>{
  const x=fresh();delete x.coverage.holdingsComplete;
  reason(x,'INVALID_OR_PARTIAL_FIXTURE_ENVELOPE');
  const y=fresh();y.fundsV3.status='error';
  reason(y,'MISSING_OR_FAILED_API_RESPONSE');
});
test('credentials, raw messages, and extra response keys rejected',()=>{
  const x=fresh();x.access_token='SECRET_LOCAL_ONLY';
  reason(x,'INVALID_OR_PARTIAL_FIXTURE_ENVELOPE');
  const y=fresh();y.orderBook.data=[{...order(),placed_by:'sensitive'}];
  reason(y,'INVALID_OR_UNSUPPORTED_ORDER');
});
test('market order, leverage product, BSE, derivative rejected',()=>{
  for(const changes of [{order_type:'MARKET'},{product:'I'},
    {exchange:'BSE'},{instrument_token:'NSE_FO|1234'}]) {
    const x=fresh();x.orderBook.data=[order(changes)];
    reason(x,'INVALID_OR_UNSUPPORTED_ORDER');
  }
});
test('negative position and wrong exchange cannot masquerade as flat',()=>{
  for(const changes of [{quantity:-1},{exchange:'BSE'}]) {
    const x=fresh();x.positions.data=[position(changes)];
    reason(x,'INVALID_OR_UNSUPPORTED_POSITION');
  }
});
test('holding collateral blocks long-only unpledged paper model',()=>{
  const x=fresh();x.holdings.data=[holding({collateral_quantity:1})];
  reason(x,'PLEDGED_HOLDING_NOT_SUPPORTED');
});
test('same instrument in positions and holdings must not be double-counted',()=>{
  const x=fresh();x.positions.data=[position()];x.holdings.data=[holding()];
  reason(x,'POSITION_HOLDING_OVERLAP_UNRESOLVED');
});
test('repeated holding or position rows block',()=>{
  const x=fresh();x.positions.data=[position(),position()];
  reason(x,'DUPLICATE_POSITION');
  const y=fresh();y.holdings.data=[holding(),holding()];
  reason(y,'DUPLICATE_HOLDING');
});
test('multiple instruments exceed current single-instrument reconciler scope',()=>{
  const x=fresh();x.positions.data=[position(),position({instrument_token:'NSE_EQ|INE5555555555'})];
  reason(x,'MULTI_INSTRUMENT_BOOK_UNSUPPORTED');
});
test('pledged fund collateral never counted as cash',()=>{
  const x=fresh();x.fundsV3.data.available_to_trade.pledge_available_to_trade.total=500;
  reason(x,'PLEDGED_MARGIN_NOT_SUPPORTED');
});
test('malformed balances or missing funds components fail',()=>{
  const x=fresh();x.fundsV3.data.available_to_trade.cash_available_to_trade.total='10000';
  reason(x,'INVALID_FUND_VALUES');
  const y=fresh();delete y.fundsV3.data.unavailable_to_trade;
  reason(y,'INVALID_FUNDS_V3_FIXTURE');
});
test('fixture timestamp stale/future rejected',()=>{
  const x=fresh();x.capturedAtMs=9000;reason(x,'STALE_CAPTURE');
  const y=fresh();y.capturedAtMs=10001;reason(y,'FUTURE_CAPTURE');
});
test('no real-time fallback when injected clock omitted',()=>{
  assert.equal(check(fresh(),{}).status,'SYNTHETIC_SHAPE_HALT');
  assert.ok(check(fresh(),{}).reasons.includes('INVALID_OBSERVATION_CLOCK'));
});
test('invalid session or duplicate capture identity rejected',()=>{
  const x=fresh();x.sessionKey='12 Nov';reason(x,'INVALID_OR_PARTIAL_FIXTURE_ENVELOPE');
});
test('two fresh successive synthetic captures remain nonbroker data',()=>{
  const x=fresh(),y=fresh();y.captureId='S2';y.capturedAtMs=9900;
  const r=pair(x,y,options);
  assert.equal(r.status,'PAIRED_SYNTHETIC_SHAPE_ONLY');
  assert.equal(r.brokerReconciled,false);assert.equal(r.canTrade,false);
});
test('same capture ID fails two-capture test',()=>{
  const x=fresh(),y=fresh();y.capturedAtMs=9900;
  assert.ok(pair(x,y,options).reasons.includes('REUSED_CAPTURE_ID'));
});
test('reversed timestamp fails two-capture test',()=>{
  const x=fresh(),y=fresh();y.captureId='S2';
  assert.ok(pair(x,y,options).reasons.includes('NON_MONOTONIC_CAPTURE'));
});
test('cross-session snapshot pair must restart reconciliation',()=>{
  const x=fresh(),y=fresh();y.captureId='S2';y.capturedAtMs=9900;
  y.sessionKey='2026-11-13';
  assert.ok(pair(x,y,options).reasons.includes('SESSION_BOUNDARY_REQUIRES_REBASE'));
});
test('earlier order disappearing from next complete book blocks',()=>{
  const x=fresh(),y=fresh();x.orderBook.data=[order()];y.captureId='S2';y.capturedAtMs=9900;
  assert.ok(pair(x,y,options).reasons.includes('ORDER_DISAPPEARED_FROM_COMPLETE_BOOK'));
});
test('decreasing cumulative fills blocks even for cancelled orders',()=>{
  const x=fresh(),y=fresh();x.orderBook.data=[order({status:'cancelled',filled_quantity:2,pending_quantity:1})];
  y.captureId='S2';y.capturedAtMs=9900;
  y.orderBook.data=[order({status:'cancelled',filled_quantity:1,pending_quantity:2})];
  assert.ok(pair(x,y,options).reasons.includes('CUMULATIVE_FILL_REGRESSION'));
});
test('terminal status rewriting blocks despite matching fill count',()=>{
  const x=fresh(),y=fresh();x.orderBook.data=[order()];
  y.captureId='S2';y.capturedAtMs=9900;
  y.orderBook.data=[order({status:'cancelled'})];
  assert.ok(pair(x,y,options).reasons.includes('FINAL_ORDER_STATUS_REWRITTEN'));
});
test('order identity mutation blocks even when same id is reused',()=>{
  const x=fresh(),y=fresh();x.orderBook.data=[order()];
  y.captureId='S2';y.capturedAtMs=9900;
  y.orderBook.data=[order({quantity:4,filled_quantity:4})];
  assert.ok(pair(x,y,options).reasons.includes('ORDER_IDENTITY_CHANGED'));
});
test('outputs never expose mock IDs, tokens, balances, or credentials',()=>{
  const x=fresh();x.orderBook.data=[order()];
  const value=JSON.stringify(check(x));
  for(const secret of ['INE1234567890','S1','10000','A1','SECRET_LOCAL_ONLY'])
    assert.equal(value.includes(secret),false);
});
