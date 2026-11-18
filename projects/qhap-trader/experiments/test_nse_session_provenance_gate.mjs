import test from 'node:test';
import assert from 'node:assert/strict';
import {checkSessionProvenance} from './nse_session_provenance_gate.mjs';
// All dates and attestations below are FICTIONAL test vectors, not NSE evidence.
const days=Array.from({length:30},(_,i)=>({date:new Date(Date.UTC(2026,0,1+i)).toISOString().slice(0,10),kind:'REGULAR',status:'CONFIRMED'}));
const valid=()=>({targetDate:days[20].date,sessions:days.map(x=>({...x})),evidenceStatus:'INDEPENDENTLY_VERIFIED',sourceType:'NSE_PRIMARY',sourceUrl:'https://www.nseindia.com/',reviewedAt:'FICTIONAL',sourceDigest:'FICTIONAL',instrumentEvidenceStatus:'INDEPENDENTLY_VERIFIED',instrumentId:'FICTIONAL',dataQualityStatus:'INDEPENDENTLY_VERIFIED',developmentExclusionStatus:'INDEPENDENTLY_VERIFIED',regimeStatus:'INDEPENDENTLY_VERIFIED',costStatus:'INDEPENDENTLY_VERIFIED',rightsStatus:'INDEPENDENTLY_VERIFIED'});
test('missing primary source digest fails closed',()=>{const x=valid();delete x.sourceDigest;assert.equal(checkSessionProvenance(x).reason,'UNVERIFIED_EXCHANGE_EVIDENCE')});
test('special Sunday is not silently accepted as regular',()=>{const x=valid();x.sessions[17].kind='SPECIAL';assert.equal(checkSessionProvenance(x).reason,'PRIOR_SPECIAL_OR_UNCONFIRMED')});
test('unconfirmed preceding session fails',()=>{const x=valid();x.sessions[19].status='UNKNOWN';assert.equal(checkSessionProvenance(x).reason,'PRIOR_SPECIAL_OR_UNCONFIRMED')});
test('missing required prior count fails',()=>{const x=valid();x.targetDate=x.sessions[12].date;assert.equal(checkSessionProvenance(x).reason,'INSUFFICIENT_IMMEDIATELY_PRECEDING_SESSIONS')});
test('unverified rights fails',()=>{const x=valid();x.rightsStatus='UNKNOWN';assert.equal(checkSessionProvenance(x).reason,'EXTERNAL_GATES_NOT_VERIFIED')});
test('fictional asserted provenance never enables orders or holdout',()=>{const x=checkSessionProvenance(valid());assert.equal(x.realOrderSubmissionPossible,false);assert.notEqual(x.decision,'HOLDOUT_APPROVED')});
