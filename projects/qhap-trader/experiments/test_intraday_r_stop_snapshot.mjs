// Fictional deterministic arithmetic only; no market prices, network or broker routes.
import test from 'node:test';
import assert from 'node:assert/strict';
import {snapshotRStop,evaluateRStop} from './intraday_r_stop_snapshot.mjs';
const fixture=()=>snapshotRStop({signalDelta:0.02,entryDecision:'09:45',fillClockStatus:'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL',hypotheticalFill:{priceInr:100,fillBasis:'EXPLICIT_HYPOTHETICAL_OBSERVATION'}});
test('entry signal delta is immutable despite later changed delta',()=>{
 const s=fixture();assert.equal(s.stopInr,96);assert.equal(s.deltaAtEntry,0.02);assert.equal(Object.isFrozen(s),true);
 assert.equal(evaluateRStop({snapshot:s,completedCheckpointClose:95,checkpointVWAP:110,afterVerifiedFill:true}).exitSignal,true);
 assert.equal(s.stopInr,96);
});
test('next-minute eligibility alone cannot create an asserted hypothetical fill',()=>{
 assert.equal(snapshotRStop({signalDelta:0.02,entryDecision:'09:45',fillClockStatus:'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL'}).status,'HALT_UNKNOWN');
 assert.equal(snapshotRStop({signalDelta:0.02,entryDecision:'09:45',fillClockStatus:'HALT_UNKNOWN',hypotheticalFill:{priceInr:100,fillBasis:'EXPLICIT_HYPOTHETICAL_OBSERVATION'}}).status,'HALT_UNKNOWN');
});
test('same-entry checkpoint exit prohibited; subsequent completed checkpoint only',()=>{
 assert.equal(evaluateRStop({snapshot:fixture(),completedCheckpointClose:95,checkpointVWAP:110}).status,'HALT_UNKNOWN');
 assert.equal(evaluateRStop({snapshot:fixture(),completedCheckpointClose:97,checkpointVWAP:110,afterVerifiedFill:true}).exitSignal,false);
});
test('unknown price, zero delta and impossible stop fail closed',()=>{
 assert.equal(snapshotRStop({signalDelta:0,entryDecision:'09:45',fillClockStatus:'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL',hypotheticalFill:{priceInr:100,fillBasis:'EXPLICIT_HYPOTHETICAL_OBSERVATION'}}).status,'HALT_UNKNOWN');
 assert.equal(snapshotRStop({signalDelta:0.6,entryDecision:'09:45',fillClockStatus:'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL',hypotheticalFill:{priceInr:100,fillBasis:'EXPLICIT_HYPOTHETICAL_OBSERVATION'}}).status,'HALT_UNKNOWN');
 assert.equal(evaluateRStop({snapshot:fixture(),completedCheckpointClose:NaN,checkpointVWAP:110,afterVerifiedFill:true}).status,'HALT_UNKNOWN');
});

test('accounted-entry integration rejects missing source, missing fill, partial fill and budget excess',async()=>{
 const {snapshotRStopFromAccountedEntry:run}=await import('./intraday_r_stop_snapshot.mjs');
 const clock={decision:'09:45',observedBarStart:'09:44',proposedFillBarStart:'09:46'};
 const base={sourceAuthorized:true,sessionIntegrityVerified:true,clock,side:'BUY',requestedShares:2,capitalInr:10000,
   state:{cashInr:10000,positionShares:0,costBasisInr:0},chargesInr:5,chargesBasis:'EXPLICIT_UNCERTIFIED_RESEARCH_SCENARIO',
   assertedHypotheticalFill:{shares:2,priceInr:100,fillBasis:'EXPLICIT_HYPOTHETICAL_OBSERVATION'}};
 const invoke=entryEvent=>run({entryEvent,signalDelta:0.02});
 assert.equal((await invoke(base)).stopInr,96);
 assert.equal((await invoke({...base,sourceAuthorized:false})).status,'HALT_UNKNOWN');
 assert.equal((await invoke({...base,chargesInr:undefined})).status,'HALT_UNKNOWN');
 assert.equal((await invoke({...base,chargesBasis:undefined})).status,'HALT_UNKNOWN');
 assert.equal((await invoke({...base,chargesInr:2301})).status,'HALT_UNKNOWN');
 assert.equal((await invoke({...base,state:{cashInr:10000,positionShares:0,costBasisInr:1}})).status,'HALT_UNKNOWN');
 assert.equal((await invoke({...base,assertedHypotheticalFill:null})).status,'HALT_UNKNOWN');
 assert.equal((await invoke({...base,assertedHypotheticalFill:{...base.assertedHypotheticalFill,shares:1}})).status,'HALT_UNKNOWN');
 assert.equal((await invoke({...base,assertedHypotheticalFill:{...base.assertedHypotheticalFill,priceInr:1300}})).status,'HALT_UNKNOWN');
 assert.equal((await invoke({...base,clock:{...clock,proposedFillBarStart:'09:45'}})).status,'HALT_UNKNOWN');
 assert.equal((await invoke({...base,side:'SELL'})).status,'HALT_UNKNOWN');
});
