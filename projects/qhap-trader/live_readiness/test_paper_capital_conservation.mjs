import test from 'node:test';
import assert from 'node:assert/strict';
import {emptyJournal,applyPaperEvent,paperStatus,reducePaperEvents} from './paper_order_lifecycle.mjs';

const e=(seq,type,orderId='A',fields={})=>({eventId:'e'+seq,seq,type,orderId,...fields});
const create=(seq=1,q=10,id='A',side='BUY',price=100)=>
  e(seq,'CREATE',id,{quantity:q,side,limitPrice:price});
const ack=(seq=2,id='A')=>e(seq,'ACK',id);
const fill=(seq=3,q=10,id='A',price=99.95)=>
  e(seq,'FILL',id,{cumulativeFilled:q,fillPrice:price});
const reject=(code,s)=>{assert.equal(s.halted,true);assert.equal(s.haltReason,code);};
const near=(a,b)=>assert.ok(Math.abs(a-b)<.011,[a,b]);
const money=s=>paperStatus(s);
const conservation=s=>{
  const v=money(s);
  near(v.cashAvailableRupees+v.cashReservedRupees+v.cashSpentRupees,10000);
  assert.ok(v.committedExposureRupees<=2500);
  assert.equal(v.realOrdersSent,0);
  return v;
};

test('initial journal has exactly ₹10,000 free and nothing committed',()=>{
 const a=conservation(emptyJournal());
 near(a.cashAvailableRupees,10000);near(a.cashReservedRupees,0);
});
test('rejects ₹10,00,000 BUY as a hard capital cap breach',()=>{
 reject('POSITION_NOTIONAL_CAP',reducePaperEvents([create(1,100,'A','BUY',10000)]));
});
test('even ₹2,501 candidate is rejected by position cap',()=>{
 reject('POSITION_NOTIONAL_CAP',reducePaperEvents([create(1,2501,'A','BUY',1)]));
});
test('a pending BUY reserves cash before exchange acknowledgment',()=>{
 const a=conservation(reducePaperEvents([create()]));
 near(a.cashAvailableRupees,8990);near(a.cashReservedRupees,1010);
 near(a.committedExposureRupees,1000);near(a.cashSpentRupees,0);
});
test('open BUY orders jointly count against exposure cap',()=>{
 const a=reducePaperEvents([create(1,20,'A'),create(2,10,'B')]);
 reject('POSITION_NOTIONAL_CAP',a);const v=conservation(a);
 near(v.cashReservedRupees,2020);
});
test('pending orders cannot slip past the ₹4,000 liquidity reserve',()=>{
 const x={...emptyJournal(),cashAvailablePaise:450000,capitalSpentPaise:550000};
 const a=applyPaperEvent(x,create());reject('INSUFFICIENT_RESERVED_CASH',a);
});
test('first partial fill conserves reserved cash and tracks cost basis',()=>{
 const s=reducePaperEvents([create(),ack(),fill(3,4)]);
 const v=conservation(s);
 assert.equal(v.longUnits,4);near(v.cashReservedRupees,606);
 near(v.positionCostRupees,399.80);assert.ok(v.cashSpentRupees>=399.80);
});
test('repeated identical fill event cannot spend twice',()=>{
 const f=fill(3,4);
 const a=reducePaperEvents([create(),ack(),f,f]);
 const b=reducePaperEvents([create(),ack(),f]);
 assert.deepEqual(money(a),money(b));conservation(a);
});
test('completed buy releases all reserved cash and retains fee debit',()=>{
 const a=reducePaperEvents([create(),ack(),fill(3,4),fill(4,10)]);
 const v=conservation(a);
 near(v.cashReservedRupees,0);near(v.positionCostRupees,999.50);
 assert.equal(v.longUnits,10);assert.ok(v.cashSpentRupees>999.50);
});
test('cancel ACK releases unfilled remainder but leaves partial holdings',()=>{
 const a=reducePaperEvents([create(),ack(),fill(3,4),e(4,'CANCEL_REQUEST'),e(5,'CANCEL_ACK')]);
 const v=conservation(a);
 near(v.cashReservedRupees,0);assert.equal(v.longUnits,4);
 near(v.positionCostRupees,399.8);assert.ok(v.cashAvailableRupees>9500);
});
test('cancel request alone NEVER releases reserved cash',()=>{
 const a=reducePaperEvents([create(),ack(),e(3,'CANCEL_REQUEST')]);
 near(conservation(a).cashReservedRupees,1010);
});
test('BUY rejection releases reserved cash with zero capital spent',()=>{
 const a=reducePaperEvents([create(),ack(),e(3,'REJECT')]);
 const v=conservation(a);near(v.cashAvailableRupees,10000);
 near(v.cashReservedRupees,0);near(v.cashSpentRupees,0);
});
test('SELL cash proceeds stay quarantined, not reusable for another BUY',()=>{
 const a=reducePaperEvents([create(),ack(),fill(),
  create(4,10,'B','SELL',100),ack(5,'B'),fill(6,10,'B',100.05)]);
 const v=conservation(a);assert.equal(v.longUnits,0);
 near(v.positionCostRupees,0);assert.ok(v.unsettledSaleProceedsRupees>0);
 assert.ok(v.cashAvailableRupees<10000);near(v.cashReservedRupees,0);
});
test('BUY cannot fill above its limit',()=>{
 reject('BUY_LIMIT_BREACH',reducePaperEvents([create(),ack(),fill(3,10,'A',100.01)]));
});
test('SELL cannot fill below its limit',()=>{
 const a=reducePaperEvents([create(),ack(),fill(),
  create(4,2,'B','SELL',100),ack(5,'B'),fill(6,2,'B',99.95)]);
 reject('SELL_LIMIT_BREACH',a);
});
test('two BUY intents max even after a cancel releases reservations',()=>{
 const s=reducePaperEvents([create(),e(2,'CANCEL_REQUEST'),e(3,'CANCEL_ACK'),
  create(4,2,'B'),e(5,'CANCEL_REQUEST','B'),e(6,'CANCEL_ACK','B'),create(7,1,'C')]);
 reject('PAPER_ENTRY_COUNT_CAP',s);
});
test('invalid price units fail closed, including fractions of one paisa',()=>{
 reject('INVALID_CREATE',reducePaperEvents([create(1,10,'A','BUY',100.001)]));
});
test('foreign injected account state cannot bypass cash conservation',()=>{
 const dirty={...emptyJournal(),cashAvailablePaise:1000000,cashReservedPaise:100};
 reject('CAPITAL_STATE_INVALID',applyPaperEvent(dirty,create()));
});
test('cancel following partial fill, then restart replay is deterministic',()=>{
 const events=[create(),ack(),fill(3,4),e(4,'CANCEL_REQUEST'),e(5,'CANCEL_ACK')];
 const a=reducePaperEvents(events),b=reducePaperEvents(events);
 assert.deepEqual(money(a),money(b));conservation(a);
});
