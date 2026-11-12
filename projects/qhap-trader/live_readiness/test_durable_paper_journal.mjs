import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createNewPaperJournal,recoverPaperJournal,compareSyntheticReference,compareSyntheticCapitalReference} from './durable_paper_journal.mjs';
const tmp=(t)=>{const dir=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-test-'));t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));return path.join(dir,'events.jsonl');};
const evt=(seq,type,orderId='A',more={})=>({eventId:'e'+seq,seq,type,orderId,...more});
const create=()=>evt(1,'CREATE','A',{quantity:10,side:'BUY',limitPrice:100});
const ack=()=>evt(2,'ACK');
const fill=(seq=3,cumulativeFilled=10)=>evt(seq,'FILL','A',{cumulativeFilled,fillPrice:99.95});
const full=(file)=>{const w=createNewPaperJournal(file);w.append(create());w.append(ack());w.append(fill());w.close();return recoverPaperJournal(file);};
test('empty journal is created but NOT reopenable for writing',t=>{const file=tmp(t),w=createNewPaperJournal(file);w.close();assert.throws(()=>createNewPaperJournal(file),/EEXIST/);const r=recoverPaperJournal(file);assert.equal(r.longUnits,0);assert.equal(r.canAppend,false);});
test('hash-chained replay preserves confirmed simulated holdings',t=>{const r=full(tmp(t));assert.equal(r.status,'RECOVERED_RECONCILIATION_REQUIRED');assert.equal(r.longUnits,10);assert.equal(r.entries,3);assert.equal(r.hashChainVerified,true);});
test('restart cannot auto-trade even when journal and synthetic reference match',t=>{const r=full(tmp(t));const c=compareSyntheticReference(r,{longUnits:r.longUnits,orders:r.orders});assert.equal(c.status,'SYNTHETIC_MATCH_EXTERNAL_VERIFICATION_REQUIRED');assert.equal(c.brokerReconciled,false);assert.equal(c.canTrade,false);});
test('reference mismatched confirmed holdings triggers halt',t=>{const r=full(tmp(t));const c=compareSyntheticReference(r,{longUnits:0,orders:r.orders});assert.equal(c.status,'MISMATCH_HALT');assert.equal(c.canTrade,false);});
test('reference mismatched pending order status triggers halt',t=>{const r=full(tmp(t));const orders=r.orders.map(x=>({...x,status:'CANCELED'}));const c=compareSyntheticReference(r,{longUnits:r.longUnits,orders});assert.equal(c.status,'MISMATCH_HALT');});
test('bad synthetic comparison is blocked',()=>{assert.equal(compareSyntheticReference({},{}).status,'BLOCKED_BAD_REFERENCE');});
test('malformed persisted JSON fails closed',t=>{const file=tmp(t);fs.writeFileSync(file,'not json\n');const r=recoverPaperJournal(file);assert.equal(r.status,'RECOVERY_BLOCKED');assert.equal(r.longUnits,null);});
test('truncated record blocks recovery and does not silently recover earlier orders',t=>{const file=tmp(t);full(file);const text=fs.readFileSync(file,'utf8');fs.writeFileSync(file,text.slice(0,-5));const r=recoverPaperJournal(file);assert.equal(r.reason,'TRUNCATED_LAST_RECORD');assert.equal(r.canAppend,false);});
test('edited fill quantity is detected by digest',t=>{const file=tmp(t);full(file);const text=fs.readFileSync(file,'utf8').replace('"cumulativeFilled":10','"cumulativeFilled":9');fs.writeFileSync(file,text);const r=recoverPaperJournal(file);assert.equal(r.reason,'JOURNAL_HASH_MISMATCH');});
test('deleting a complete middle line breaks sequence',t=>{const file=tmp(t);full(file);const lines=fs.readFileSync(file,'utf8').trimEnd().split('\n');fs.writeFileSync(file,lines.filter((_,i)=>i!==1).join('\n')+'\n');const r=recoverPaperJournal(file);assert.equal(r.status,'RECOVERY_BLOCKED');});
test('reordering records cannot be accepted',t=>{const file=tmp(t);full(file);const lines=fs.readFileSync(file,'utf8').trimEnd().split('\n');fs.writeFileSync(file,[lines[1],lines[0],lines[2]].join('\n')+'\n');assert.equal(recoverPaperJournal(file).status,'RECOVERY_BLOCKED');});
test('identical duplicate is ignored, not persisted or double-counted',t=>{const file=tmp(t),w=createNewPaperJournal(file);w.append(create());w.append(ack());w.append(fill());const x=w.append(fill());assert.equal(x.status,'DUPLICATE_IGNORED');w.close();assert.equal(recoverPaperJournal(file).entries,3);assert.equal(recoverPaperJournal(file).longUnits,10);});
test('conflicting duplicate event causes durable fail-closed halt',t=>{const file=tmp(t),w=createNewPaperJournal(file);w.append(create());w.append(ack());w.append(fill());const e={...fill(),cumulativeFilled:9};const s=w.append(e);assert.equal(s.status,'HALTED');assert.throws(()=>w.append(evt(4,'ACK')),/HALTED/);w.close();const r=recoverPaperJournal(file);assert.equal(r.journalHalted,true);assert.equal(r.entries,4);});
test('disconnect persists unresolved units without inventing a sell',t=>{const file=tmp(t),w=createNewPaperJournal(file);w.append(create());w.append(ack());w.append(fill());w.append(evt(4,'DISCONNECT'));w.close();const r=recoverPaperJournal(file);assert.equal(r.longUnits,10);assert.equal(r.journalHalted,true);assert.equal(r.reason,'CONNECTION_LOST_RECONCILIATION_REQUIRED');});
test('partial fills survive restart with correct cumulative quantities',t=>{const file=tmp(t),w=createNewPaperJournal(file);w.append(create());w.append(ack());w.append(fill(3,4));w.close();const r=recoverPaperJournal(file);assert.equal(r.longUnits,4);assert.equal(r.orders[0].cumulativeFilled,4);});
test('schema disallows token, arbitrary market frames and extra fields',t=>{const file=tmp(t),w=createNewPaperJournal(file);assert.throws(()=>w.append({...create(),token:'SECRET'}),/SCHEMA/);assert.throws(()=>w.append({...create(),marketPrice:88}),/SCHEMA/);w.close();assert.equal(recoverPaperJournal(file).entries,0);});
test('missing journal blocks instead of assuming flat',t=>{const file=tmp(t);const r=recoverPaperJournal(file);assert.equal(r.status,'RECOVERY_BLOCKED');assert.equal(r.longUnits,null);});
test('symlink is rejected at recovery, not followed',t=>{const file=tmp(t),original=file+'-real';fs.writeFileSync(original,'');fs.symlinkSync(original,file);assert.equal(recoverPaperJournal(file).reason,'UNSAFE_OR_OVERSIZE_JOURNAL');});
test('new journal cannot silently overwrite preexisting records',t=>{const file=tmp(t);full(file);assert.throws(()=>createNewPaperJournal(file),/EEXIST/);assert.equal(recoverPaperJournal(file).longUnits,10);});
test('paper journal status never reports real order capability',t=>{const file=tmp(t),w=createNewPaperJournal(file);w.append(create());const s=w.status();assert.equal(s.liveTradingAuthorized,false);assert.equal(s.realOrdersSent,0);w.close();});

test('durable recovery includes cash available, reserved and spent',t=>{
 const r=full(tmp(t));
 assert.equal(r.cashReservedRupees,0);
 assert.equal(r.positionCostRupees,999.50);
 assert.ok(r.cashSpentRupees>999.50);
 assert.ok(Math.abs(r.cashSpentRupees+r.cashAvailableRupees+r.cashReservedRupees-10000)<.01);
 assert.equal(r.canAppend,false);
});
test('recovered pending buy preserves reserved funds, not invented flat cash',t=>{
 const file=tmp(t),j=createNewPaperJournal(file);j.append(create());j.close();
 const r=recoverPaperJournal(file);
 assert.equal(r.cashAvailableRupees,8990);
 assert.equal(r.cashReservedRupees,1010);
 assert.equal(r.committedExposureRupees,1000);
 assert.equal(r.canAppend,false);
});
test('mock capital reference must match funds as well as shares',t=>{
 const r=full(tmp(t));
 const ok=compareSyntheticCapitalReference(r,{longUnits:r.longUnits,orders:r.orders,
  cashAvailableRupees:r.cashAvailableRupees,cashReservedRupees:r.cashReservedRupees,
  cashSpentRupees:r.cashSpentRupees,positionCostRupees:r.positionCostRupees,
  unsettledSaleProceedsRupees:r.unsettledSaleProceedsRupees,
  committedExposureRupees:r.committedExposureRupees});
 assert.equal(ok.status,'SYNTHETIC_CAPITAL_MATCH_EXTERNAL_VERIFICATION_REQUIRED');
 assert.equal(ok.canTrade,false);assert.equal(ok.brokerReconciled,false);
});
test('mock reconciliation rejects a false cash balance even if order IDs match',t=>{
 const r=full(tmp(t));
 const fake={longUnits:r.longUnits,orders:r.orders,
  cashAvailableRupees:r.cashAvailableRupees+500,
  cashReservedRupees:r.cashReservedRupees,
  cashSpentRupees:r.cashSpentRupees,positionCostRupees:r.positionCostRupees,
  unsettledSaleProceedsRupees:r.unsettledSaleProceedsRupees,
  committedExposureRupees:r.committedExposureRupees};
 assert.equal(compareSyntheticCapitalReference(r,fake).status,'CAPITAL_OR_ORDER_MISMATCH_HALT');
});
test('incomplete mock funds cannot be misrepresented as reconciled',t=>{
 const r=full(tmp(t));
 assert.equal(compareSyntheticCapitalReference(r,{orders:r.orders,longUnits:r.longUnits}).status,
   'BLOCKED_INCOMPLETE_REFERENCE');
});
