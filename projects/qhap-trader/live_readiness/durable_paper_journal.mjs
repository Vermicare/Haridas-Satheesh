/**
 * QHAP-TRADER durable, append-only *offline hypothetical* order event journal.
 * No broker, exchange feed, executable orders, or credentials. SHA-256 hash chaining
 * catches accidental changes, not malicious tampering (no trusted signing key).
 * Restart ALWAYS requires independently reviewed reconciliation; no auto-resume.
 */
import fs from 'node:fs';
import crypto from 'node:crypto';
import {emptyJournal, applyPaperEvent, paperStatus} from './paper_order_lifecycle.mjs';

const GENESIS='0'.repeat(64);
const MAX_BYTES=5_000_000;
const ALLOWED=new Set(['eventId','seq','type','orderId','quantity','side','limitPrice','cumulativeFilled','fillPrice']);
const hash = o=>crypto.createHash('sha256').update(JSON.stringify(o)).digest('hex');
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const object=o=>o!==null&&typeof o==='object'&&!Array.isArray(o);
const blocked=(code)=>({status:'RECOVERY_BLOCKED',reason:code,halted:true,
  longUnits:null,orders:null,reconciled:false,canAppend:false,
  brokerReconciled:false,realOrdersSent:0,liveTradingAuthorized:false});

function validateEvent(event){
  if(!object(event)||Object.keys(event).some(k=>!ALLOWED.has(k))||!own(event,'eventId')||
    !own(event,'seq')||!own(event,'type')||!own(event,'orderId'))
    throw Error('INVALID_PAPER_EVENT_SCHEMA');
  const text=JSON.stringify(event);
  if(!text||text.length>2048)throw Error('INVALID_PAPER_EVENT_SIZE');
  const parsed=JSON.parse(text);
  if(!object(parsed))throw Error('INVALID_PAPER_EVENT');
  return parsed;
}
function summary(state){
  const p=paperStatus(state);
  return {longUnits:p.longUnits,orders:p.orders,halted:p.halted,
    haltReason:p.haltReason,eventsApplied:p.eventsApplied,
    cashAvailableRupees:p.cashAvailableRupees,
    cashReservedRupees:p.cashReservedRupees,
    cashSpentRupees:p.cashSpentRupees,
    unsettledSaleProceedsRupees:p.unsettledSaleProceedsRupees,
    positionCostRupees:p.positionCostRupees,
    committedExposureRupees:p.committedExposureRupees};
}

export function createNewPaperJournal(filePath){
  if(typeof filePath!=='string'||!filePath.length)throw Error('INVALID_JOURNAL_PATH');
  // wx ensures an existing journal can NEVER silently be reopened for writing.
  const fd=fs.openSync(filePath,'wx',0o600);
  let state=emptyJournal(),lastDigest=GENESIS,count=0,closed=false;
  return {
    append(event){
      if(closed||state.halted)throw Error('JOURNAL_CLOSED_OR_HALTED');
      const safe=validateEvent(event);
      const next=applyPaperEvent(state,safe);
      if(next===state)return {status:'DUPLICATE_IGNORED',state:summary(state)};
      const recordBase={version:1,recordNumber:count+1,previousHash:lastDigest,event:safe};
      const digest=hash(recordBase);
      const line=JSON.stringify({...recordBase,hash:digest})+'\n';
      try{
        fs.writeSync(fd,line,null,'utf8');fs.fsyncSync(fd);
      }catch(e){closed=true;try{fs.closeSync(fd);}catch{}throw Error('JOURNAL_WRITE_UNCERTAIN_REVIEW_REQUIRED');}
      count++;lastDigest=digest;state=next;
      return {status:state.halted?'HALTED':'APPENDED',state:summary(state)};
    },
    status(){return {status:closed?'CLOSED':state.halted?'HALTED':'NEW_SESSION_ONLY',
      ...summary(state),entries:count,brokerReconciled:false,
      realOrdersSent:0,liveTradingAuthorized:false};},
    close(){if(!closed){fs.fsyncSync(fd);fs.closeSync(fd);closed=true;}}
  };
}

export function recoverPaperJournal(filePath){
  let bytes;
  try{
    const stat=fs.lstatSync(filePath);
    if(!stat.isFile()||stat.isSymbolicLink()||stat.size>MAX_BYTES)return blocked('UNSAFE_OR_OVERSIZE_JOURNAL');
    bytes=fs.readFileSync(filePath,'utf8');
  }catch{return blocked('JOURNAL_UNREADABLE');}
  if(bytes&&!bytes.endsWith('\n'))return blocked('TRUNCATED_LAST_RECORD');
  const lines=bytes?bytes.trimEnd().split('\n'):[];
  let state=emptyJournal(),prev=GENESIS;
  for(let i=0;i<lines.length;i++){
    let r;
    try{r=JSON.parse(lines[i]);}catch{return blocked('MALFORMED_JSON_RECORD');}
    if(!object(r)||Object.keys(r).length!==5||r.version!==1||r.recordNumber!==i+1||
       r.previousHash!==prev||typeof r.hash!=='string'||!(/^[0-9a-f]{64}$/.test(r.hash)))
      return blocked('BROKEN_JOURNAL_CHAIN');
    let e;
    try{e=validateEvent(r.event);}catch{return blocked('INVALID_EVENT_SCHEMA');}
    const base={version:1,recordNumber:i+1,previousHash:prev,event:e};
    if(hash(base)!==r.hash)return blocked('JOURNAL_HASH_MISMATCH');
    const next=applyPaperEvent(state,e);
    if(next===state)return blocked('UNEXPECTED_DUPLICATE_RECORD');
    state=next;prev=r.hash;
    if(state.halted&&i!==lines.length-1)return blocked('EVENTS_AFTER_HALTED_STATE');
  }
  const s=summary(state);
  return {status:'RECOVERED_RECONCILIATION_REQUIRED',reason:state.haltReason,
    longUnits:s.longUnits,orders:s.orders,eventsApplied:s.eventsApplied,
    cashAvailableRupees:s.cashAvailableRupees,cashReservedRupees:s.cashReservedRupees,
    cashSpentRupees:s.cashSpentRupees,positionCostRupees:s.positionCostRupees,
    unsettledSaleProceedsRupees:s.unsettledSaleProceedsRupees,
    committedExposureRupees:s.committedExposureRupees,
    journalHalted:state.halted,entries:lines.length,hashChainVerified:true,
    canAppend:false,brokerReconciled:false,realOrdersSent:0,
    liveTradingAuthorized:false,
    nextAction:'INDEPENDENT_ACCOUNT_AND_OPEN_ORDER_RECONCILIATION_REQUIRED'};
}

/** Only compare provided synthetic snapshots. Does not authenticate broker data. */
export function compareSyntheticReference(recovered,reference){
  if(!recovered||recovered.status!=='RECOVERED_RECONCILIATION_REQUIRED'||
     !object(reference)||!Number.isSafeInteger(reference.longUnits)||
     !Array.isArray(reference.orders))return {status:'BLOCKED_BAD_REFERENCE',brokerReconciled:false,canTrade:false};
  const ordered=a=>[...a].map(o=>({orderId:o.orderId,status:o.status,
    quantity:o.quantity,cumulativeFilled:o.cumulativeFilled})).sort((a,b)=>String(a.orderId).localeCompare(String(b.orderId)));
  const equal=recovered.longUnits===reference.longUnits&&
    JSON.stringify(ordered(recovered.orders))===JSON.stringify(ordered(reference.orders));
  return {status:equal?'SYNTHETIC_MATCH_EXTERNAL_VERIFICATION_REQUIRED':'MISMATCH_HALT',
    brokerReconciled:false,canTrade:false,liveTradingAuthorized:false};
}

/**
 * Optional full cash/position comparison against an UNAUTHENTICATED synthetic
 * reference. A matching paper snapshot is NOT a signed broker balance or
 * sufficient to resume an executable strategy. No live approval is possible.
 */
export function compareSyntheticCapitalReference(recovered,reference){
  const fields=['longUnits','cashAvailableRupees','cashReservedRupees',
    'cashSpentRupees','positionCostRupees','unsettledSaleProceedsRupees',
    'committedExposureRupees'];
  if(!recovered||recovered.status!=='RECOVERED_RECONCILIATION_REQUIRED'||
     !object(reference)||!Array.isArray(reference.orders)||
     fields.some(k=>!Number.isFinite(reference[k])||!Number.isFinite(recovered[k])))
    return {status:'BLOCKED_INCOMPLETE_REFERENCE',
      canTrade:false,brokerReconciled:false,liveTradingAuthorized:false};
  const old=compareSyntheticReference(recovered,reference);
  const numericEqual=fields.every(k=>Math.abs(recovered[k]-reference[k])<0.001);
  return {status:old.status==='SYNTHETIC_MATCH_EXTERNAL_VERIFICATION_REQUIRED'&&numericEqual?
    'SYNTHETIC_CAPITAL_MATCH_EXTERNAL_VERIFICATION_REQUIRED':'CAPITAL_OR_ORDER_MISMATCH_HALT',
    canTrade:false,brokerReconciled:false,liveTradingAuthorized:false};
}
