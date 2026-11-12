import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createMockOrder,applyMockEvent,mockLifecycleSummary} from './mock_order_lifecycle.mjs';

const draft=()=>createMockOrder({
  clientOrderKey:'QHAP-ABC123456',
  quantity:10,limitPrice:100,instrumentKey:'NSE_EQ|INE848E01016'
});
const ev=(sequence,type,extra={})=>({
  source:'SYNTHETIC_ONLY',eventId:'E-event'+sequence,sequence,type,...extra
});
const ack=()=>applyMockEvent(draft(),ev(1,'ACK'));
const partial=()=>applyMockEvent(ack(),ev(2,'FILL',{fillQuantity:4,fillPrice:99.9}));

test('draft is MOCK_ONLY, risk locked, no orders',()=>{
 const r=draft();assert.equal(r.status,'DRAFT');assert.equal(r.riskLocked,true);
 assert.equal(r.realOrdersSent,0);assert.equal(r.brokerOrderRoutePresent,false);
});
test('rejects malformed mock order',()=>{
 assert.throws(()=>createMockOrder({clientOrderKey:'abc',quantity:1,limitPrice:1,instrumentKey:'NSE_EQ|INE848E01016'}),/CLIENT_KEY/);
 assert.throws(()=>createMockOrder({clientOrderKey:'QHAP-ABC123456',quantity:0,limitPrice:1,instrumentKey:'NSE_EQ|INE848E01016'}),/QUANTITY/);
});
test('ack receipt never unlocks broker',()=>{
 const r=ack();assert.equal(r.status,'WORKING');assert.equal(r.riskLocked,true);assert.equal(r.realOrdersSent,0);
});
test('partial fill retains remaining exposure',()=>{
 const r=partial();assert.equal(r.status,'PARTIAL');assert.equal(r.filledQuantity,4);
 assert.equal(r.remainingQuantity,6);assert.equal(r.filledNotional,399.6);
});
test('event-id duplicates are ignored without another fill',()=>{
 const p=partial();const dupe=applyMockEvent(p,ev(2,'FILL',{fillQuantity:4,fillPrice:99.9}));
 assert.equal(dupe.duplicateEventIgnored,true);assert.equal(dupe.filledQuantity,4);
 assert.equal(dupe.lastSequence,2);
});
test('a full fill makes complete synthetic order but never a live trade',()=>{
 let x=partial();x=applyMockEvent(x,ev(3,'FILL',{fillQuantity:6,fillPrice:100}));
 assert.equal(x.status,'FILLED');assert.equal(x.remainingQuantity,0);
 assert.equal(mockLifecycleSummary(x).liveTradingAuthorized,false);
 assert.equal(mockLifecycleSummary(x).complete,false);
});
test('cancel request and acknowledgement with zero fill',()=>{
 let x=ack();x=applyMockEvent(x,ev(2,'CANCEL_REQUESTED'));
 assert.equal(x.status,'CANCEL_PENDING');
 x=applyMockEvent(x,ev(3,'CANCEL_ACK'));
 assert.equal(x.status,'CANCELLED');assert.equal(x.remainingQuantity,10);
});
test('cancel race may have partial fills but must retain them',()=>{
 let x=partial();
 x=applyMockEvent(x,ev(3,'CANCEL_REQUESTED'));
 x=applyMockEvent(x,ev(4,'FILL',{fillQuantity:2,fillPrice:100.2}));
 assert.equal(x.status,'CANCEL_PENDING');assert.equal(x.filledQuantity,6);
 x=applyMockEvent(x,ev(5,'CANCEL_ACK'));
 assert.equal(x.status,'CANCELLED_PARTIAL');assert.equal(x.filledQuantity,6);
 assert.equal(x.remainingQuantity,4);
});
test('reject after partial fill must not erase actual modeled exposure',()=>{
 let x=partial();x=applyMockEvent(x,ev(3,'REJECT'));
 assert.equal(x.status,'REJECTED_PARTIAL');assert.equal(x.filledQuantity,4);
});
test('overfill event halts with unchanged filled quantity',()=>{
 const x=applyMockEvent(partial(),ev(3,'FILL',{fillQuantity:7,fillPrice:100}));
 assert.equal(x.status,'HALTED');assert.equal(x.haltReason,'INVALID_OR_OVERFILL_RECEIPT');
 assert.equal(x.filledQuantity,4);assert.equal(x.reconciliationRequired,true);
});
test('fill without broker ack is blocked',()=>{
 const x=applyMockEvent(draft(),ev(1,'FILL',{fillQuantity:1,fillPrice:100}));
 assert.equal(x.status,'HALTED');
});
test('sequence gaps halt rather than assuming exchange state',()=>{
 const x=applyMockEvent(ack(),ev(4,'FILL',{fillQuantity:1,fillPrice:100}));
 assert.equal(x.status,'HALTED');assert.equal(x.haltReason,'MISSING_OR_OUT_OF_ORDER_EVENT');
});
test('disconnect after partial fill requires reconciliation',()=>{
 const x=applyMockEvent(partial(),ev(3,'DISCONNECT'));
 assert.equal(x.status,'HALTED');assert.equal(x.filledQuantity,4);
 assert.equal(x.reconciliationRequired,true);
});
test('inconsistent account snapshot halts and retains position',()=>{
 const x=applyMockEvent(partial(),ev(3,'INCONSISTENT_ACCOUNT_SNAPSHOT'));
 assert.equal(x.status,'HALTED');assert.equal(x.filledQuantity,4);
});
test('unknown or untrusted event source locks risk',()=>{
 assert.equal(applyMockEvent(ack(),ev(2,'UNSUPPORTED')).status,'HALTED');
 assert.equal(applyMockEvent(ack(),{...ev(2,'FILL'),source:'LIVE_BROKER'}).status,'HALTED');
});
test('events after terminal state halt reconciliation',()=>{
 let x=ack();x=applyMockEvent(x,ev(2,'REJECT'));
 x=applyMockEvent(x,ev(3,'FILL',{fillQuantity:1,fillPrice:100}));
 assert.equal(x.status,'HALTED');assert.equal(x.haltReason,'EVENT_AFTER_TERMINAL');
});
test('repeated halted state can never resume trading',()=>{
 const x=applyMockEvent(ack(),ev(3,'DISCONNECT'));
 const y=applyMockEvent(x,ev(4,'ACK'));
 assert.equal(y.status,'HALTED');assert.equal(y.riskLocked,true);
});
test('mock source has no transport, broker endpoints or secret storage',()=>{
 const src=fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),'mock_order_lifecycle.mjs'),'utf8');
 for(const re of [/from ['"]node:https?['"]/,/from ['"]https?['"]/,/\bfetch\s*\(/,/\b(placeOrder|modifyOrder|cancelOrder|submitOrder)\s*\(/]){
  assert.equal(re.test(src),false,String(re));
 }
});
