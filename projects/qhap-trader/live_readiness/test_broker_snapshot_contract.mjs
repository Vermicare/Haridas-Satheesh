import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createNewPaperJournal,recoverPaperJournal} from './durable_paper_journal.mjs';
import {auditSyntheticBrokerSnapshot,auditPairedSyntheticSnapshots} from './broker_snapshot_contract.mjs';

const opts={observedAtMs:10000,maxAgeMs:500};
const fields=['cashAvailableRupees','cashReservedRupees','cashSpentRupees',
  'unsettledSaleProceedsRupees','positionCostRupees','committedExposureRupees'];
const ev=(seq,type,orderId='A',rest={})=>({seq,eventId:'e'+seq,type,orderId,...rest});
const create=(seq=1,q=5,id='A',side='BUY',price=100)=>ev(seq,'CREATE',id,{quantity:q,side,limitPrice:price});
const ack=(seq=2,id='A')=>ev(seq,'ACK',id);
const fill=(seq=3,q=5,id='A',price=99.95)=>ev(seq,'FILL',id,{cumulativeFilled:q,fillPrice:price});
function journal(t,events=[]){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-broker-contract-'));
 t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const fp=path.join(dir,'paper-events.jsonl'),w=createNewPaperJournal(fp);
 for(const e of events)w.append(e);
 w.close();
 return recoverPaperJournal(fp);
}
const snapshot=(r,changes={})=>{
 const cash=Object.fromEntries(fields.map(k=>[k,r[k]]));
 return {
  schemaVersion:1,source:'SYNTHETIC_FIXTURE',snapshotId:'s1',
  capturedAtMs:9850,coverage:'ALL_ORDERS_AND_POSITIONS',
  orders:r.orders.map(o=>({...o})),longUnits:r.longUnits,cash,...changes
 };
};
const check=(r,s,options=opts)=>auditSyntheticBrokerSnapshot(r,s,options);
const expectReason=(r,s,reason)=>{const v=check(r,s);assert.equal(v.status,'MISMATCH_HALT',JSON.stringify(v));assert.ok(v.reasons.includes(reason),JSON.stringify(v));assert.equal(v.canTrade,false);return v;};
test('complete synthetic flat book matches but NEVER authorizes broker',t=>{
 const r=journal(t),s=snapshot(r),v=check(r,s);
 assert.equal(v.status,'SYNTHETIC_MATCH_EXTERNAL_AUTHENTICATION_REQUIRED');
 assert.equal(v.brokerReconciled,false);assert.equal(v.canTrade,false);
 assert.equal(v.liveTradingAuthorized,false);
});
test('confirmed synthetic bought position exactly matches external fixture, not broker',t=>{
 const r=journal(t,[create(),ack(),fill()]);
 const v=check(r,snapshot(r));
 assert.equal(v.status,'SYNTHETIC_MATCH_EXTERNAL_AUTHENTICATION_REQUIRED');
 assert.equal(v.externalAccountIdentityVerified,false);
});
test('missing external filled order triggers hard halt',t=>{
 const r=journal(t,[create(),ack(),fill()]);
 expectReason(r,snapshot(r,{orders:[]}), 'ORDER_MISSING_FROM_EXTERNAL_SNAPSHOT');
});
test('unrecognized external order triggers hard halt',t=>{
 const r=journal(t);
 const extra={orderId:'STRANGER',status:'FILLED',quantity:1,cumulativeFilled:1};
 expectReason(r,snapshot(r,{orders:[extra]}),'EXTERNAL_ORDER_NOT_IN_JOURNAL');
});
test('partial fills mismatch even if status identical',t=>{
 const r=journal(t,[create(),ack(),fill(3,2)]);
 const s=snapshot(r);
 s.orders[0].cumulativeFilled=1;
 expectReason(r,s,'ORDER_STATE_OR_FILL_MISMATCH');
});
test('filled quantity mismatch',t=>{
 const r=journal(t,[create(),ack(),fill()]);
 const s=snapshot(r);s.orders[0].quantity=6;s.orders[0].cumulativeFilled=6;
 expectReason(r,s,'ORDER_STATE_OR_FILL_MISMATCH');
});
test('order canceled locally but fixture says filled',t=>{
 const r=journal(t,[create(),ack(),ev(3,'CANCEL_REQUEST'),ev(4,'CANCEL_ACK')]);
 const s=snapshot(r);s.orders[0].status='FILLED';s.orders[0].cumulativeFilled=5;
 expectReason(r,s,'ORDER_STATE_OR_FILL_MISMATCH');
});
test('unknown positions cannot be interpreted as flat',t=>{
 const r=journal(t);
 expectReason(r,snapshot(r,{longUnits:1}),'POSITION_QUANTITY_MISMATCH');
});
test('cash mismatch is detected despite identical orders and positions',t=>{
 const r=journal(t,[create(),ack(),fill()]);
 const s=snapshot(r);s.cash.cashAvailableRupees-=1;
 expectReason(r,s,'CASH_FIELD_MISMATCH_CASHAVAILABLERUPEES');
});
test('reservation mismatch is detected even before an ACK',t=>{
 const r=journal(t,[create()]);
 const s=snapshot(r);s.cash.cashReservedRupees-=1;
 expectReason(r,s,'CASH_FIELD_MISMATCH_CASHRESERVEDRUPEES');
});
test('unsettled cash proceeds mismatch detected and quarantined',t=>{
 const r=journal(t,[create(),ack(),fill(),create(4,5,'B','SELL',100),ack(5,'B'),
   fill(6,5,'B',100.05)]);
 const s=snapshot(r);s.cash.unsettledSaleProceedsRupees=0;
 expectReason(r,s,'CASH_FIELD_MISMATCH_UNSETTLEDSALEPROCEEDSRUPEES');
});
test('in-flight buy blocks even with identical mock snapshot',t=>{
 const r=journal(t,[create()]),s=snapshot(r);
 expectReason(r,s,'UNRESOLVED_OPEN_ORDERS');
});
test('partially filled order blocks even with identical mock snapshot',t=>{
 const r=journal(t,[create(),ack(),fill(3,2)]),s=snapshot(r);
 expectReason(r,s,'UNRESOLVED_OPEN_ORDERS');
});
test('pending cancel still counts as open',t=>{
 const r=journal(t,[create(),ack(),ev(3,'CANCEL_REQUEST')]);
 expectReason(r,snapshot(r),'UNRESOLVED_OPEN_ORDERS');
});
test('journal disconnect halt remains a halt after matching fixture',t=>{
 const r=journal(t,[create(),ack(),fill(),ev(4,'DISCONNECT')]);
 expectReason(r,snapshot(r),'JOURNAL_HALT_REQUIRES_OPERATOR_REVIEW');
});
test('future snapshot blocks and cannot be mistaken for fresh',t=>{
 const r=journal(t),s=snapshot(r,{capturedAtMs:10001});
 expectReason(r,s,'FUTURE_SNAPSHOT');
});
test('stale snapshot blocks and cannot be mistaken for fresh',t=>{
 const r=journal(t),s=snapshot(r,{capturedAtMs:9000});
 expectReason(r,s,'STALE_SNAPSHOT');
});
test('snapshot with incomplete order coverage is blocked as invalid',t=>{
 const r=journal(t),s=snapshot(r,{coverage:'OPEN_ONLY'});
 assert.equal(check(r,s).status,'BLOCKED_SNAPSHOT_SCHEMA');
});
test('source claims of actual broker are untrusted and rejected',t=>{
 const r=journal(t),s=snapshot(r,{source:'UPSTOX_LIVE'});
 assert.equal(check(r,s).status,'BLOCKED_UNVERIFIED_SOURCE');
});
test('unexpected secrets or embedded raw responses are rejected at boundary',t=>{
 const r=journal(t),s={...snapshot(r),accessToken:'sensitive'};
 assert.equal(check(r,s).status,'BLOCKED_SNAPSHOT_SCHEMA');
});
test('bad timestamp or missing observation clock never defaults to real time',t=>{
 const r=journal(t),s=snapshot(r);
 assert.equal(check(r,s,{}).status,'BLOCKED_INVALID_CLOCK');
 assert.equal(check(r,s,{observedAtMs:10000,maxAgeMs:0}).status,'BLOCKED_INVALID_CLOCK');
});
test('duplicate order ids cause invalid snapshot rejection',t=>{
 const r=journal(t,[create(),ack(),fill()]),s=snapshot(r);
 s.orders.push({...s.orders[0]});
 assert.equal(check(r,s).status,'BLOCKED_SNAPSHOT_SCHEMA');
});
test('terminal filled status cannot contain incomplete quantity',t=>{
 const r=journal(t,[create(),ack(),fill()]),s=snapshot(r);
 s.orders[0].cumulativeFilled=2;
 assert.equal(check(r,s).status,'BLOCKED_SNAPSHOT_SCHEMA');
});
test('negative or fractional outstanding quantities are invalid',t=>{
 const r=journal(t,[create(),ack(),fill()]),s=snapshot(r);
 s.orders[0].cumulativeFilled=-1;
 assert.equal(check(r,s).status,'BLOCKED_SNAPSHOT_SCHEMA');
});
test('fake journal without verified recovery chain never reconciles',t=>{
 const r=journal(t),s=snapshot(r);
 assert.equal(check({...r,hashChainVerified:false},s).status,'BLOCKED_UNTRUSTED_RECOVERY');
});
test('paired clean snapshots still never permit live trading',t=>{
 const r=journal(t,[create(),ack(),fill()]),a=snapshot(r),b=snapshot(r,{
  snapshotId:'s2',capturedAtMs:9950
 });
 const v=auditPairedSyntheticSnapshots(r,a,b,opts);
 assert.equal(v.status,'PAIRED_SYNTHETIC_MATCH_EXTERNAL_AUTHENTICATION_REQUIRED');
 assert.equal(v.canTrade,false);
});
test('paired snapshots require distinct IDs',t=>{
 const r=journal(t),a=snapshot(r),b=snapshot(r,{capturedAtMs:9950});
 assert.equal(auditPairedSyntheticSnapshots(r,a,b,opts).status,'PAIRED_SNAPSHOT_HALT');
});
test('paired snapshots require chronological captures',t=>{
 const r=journal(t),a=snapshot(r),b=snapshot(r,{snapshotId:'s2',capturedAtMs:9850});
 assert.equal(auditPairedSyntheticSnapshots(r,a,b,opts).status,'PAIRED_SNAPSHOT_HALT');
});
test('paired snapshots cannot hide transient unknown order',t=>{
 const r=journal(t),a=snapshot(r),b=snapshot(r,{snapshotId:'s2',capturedAtMs:9950,
  orders:[{orderId:'EXTRA',status:'FILLED',quantity:1,cumulativeFilled:1}]});
 assert.equal(auditPairedSyntheticSnapshots(r,a,b,opts).status,'PAIRED_SNAPSHOT_HALT');
});
test('no output echoes raw cash balances, tokens, snapshot ids or order IDs',t=>{
 const r=journal(t,[create(),ack(),fill()]),s=snapshot(r),v=check(r,s);
 const text=JSON.stringify(v);
 assert.equal(text.includes('cashAvailableRupees'),false);
 assert.equal(text.includes('snapshotId'),false);
 assert.equal(text.includes('"A"'),false);
 assert.equal(text.includes('"10000"'),false);
});
