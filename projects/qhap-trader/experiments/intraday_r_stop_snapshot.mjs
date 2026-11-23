import {assessIntradayClock} from './intraday_execution_clock.mjs';
/** Fictional candidate R stop snapshot; pure research arithmetic, never a fill or order. */
const minute = t => { if(typeof t!=='string'||!/^[0-9]{2}:[0-9]{2}$/.test(t)) return null; const h=+t.slice(0,2),m=+t.slice(3); return h<24&&m<60?h*60+m:null; };
export function snapshotRStop({signalDelta, hypotheticalFill, entryDecision, entryFillBarStart, fillClockStatus}={}) {
 const halt=reason=>({status:'HALT_UNKNOWN',reason,decision:'NO_TRADE',realOrderSubmissionPossible:false});
 if(fillClockStatus!=='ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL') return halt('ENTRY_CLOCK_UNVERIFIED');
 if(!hypotheticalFill || hypotheticalFill.fillBasis!=='EXPLICIT_HYPOTHETICAL_OBSERVATION' ||
    hypotheticalFill.confirmedRealFill===true) return halt('HYPOTHETICAL_FILL_UNVERIFIED');
 if(typeof signalDelta!=='number'||!Number.isFinite(signalDelta)||signalDelta<=0 ||
    typeof hypotheticalFill.priceInr!=='number'||!Number.isFinite(hypotheticalFill.priceInr)||hypotheticalFill.priceInr<=0 ||
    typeof entryDecision!=='string'||!/^[0-9]{2}:[0-9]{2}$/.test(entryDecision)) return halt('INVALID_ENTRY_SNAPSHOT');
 if(minute(entryDecision)===null || minute(entryFillBarStart)===null || minute(entryFillBarStart)<=minute(entryDecision)) return halt('ENTRY_FILL_CLOCK_UNVERIFIED');
 const stopInr=hypotheticalFill.priceInr*(1-2*signalDelta);
 if(!Number.isFinite(stopInr)||stopInr<=0) return halt('INVALID_STOP');
 return Object.freeze({status:'FICTIONAL_STOP_SNAPSHOT_ONLY',entryDecision,deltaAtEntry:signalDelta,
   entryFillPriceInr:hypotheticalFill.priceInr,entryFillBarStart,stopInr,decision:'NO_TRADE',realOrderSubmissionPossible:false});
}
export function evaluateRStop({snapshot,completedCheckpointClose,checkpointVWAP,completedCheckpointBarStart}={}) {
 const halt=reason=>({status:'HALT_UNKNOWN',reason,decision:'NO_TRADE',realOrderSubmissionPossible:false});
 if(snapshot?.status!=='FICTIONAL_STOP_SNAPSHOT_ONLY' || minute(snapshot.entryFillBarStart)===null ||
    minute(completedCheckpointBarStart)===null || minute(completedCheckpointBarStart)<=minute(snapshot.entryFillBarStart))
    return halt('ENTRY_OR_LATER_CHECKPOINT_UNVERIFIED');
 // A completed 1-minute bar stamped 10:14 is observed at the registered 10:15 decision.
 // Reject arbitrary later timestamps (e.g. 09:47) even when after entry.
 const checkpointMinute=minute(completedCheckpointBarStart);
 const decisionMinute=checkpointMinute+1;
 const hhmm=n=>String(Math.floor(n/60)).padStart(2,'0')+':'+String(n%60).padStart(2,'0');
 const clock=assessIntradayClock({decision:hhmm(decisionMinute),observedBarStart:completedCheckpointBarStart,
   proposedFillBarStart:hhmm(decisionMinute+1),kind:'EXIT'});
 if(clock.status!=='ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL') return halt('UNREGISTERED_OR_UNVERIFIED_EXIT_CHECKPOINT');
 if(![completedCheckpointClose,checkpointVWAP].every(x=>typeof x==='number'&&Number.isFinite(x)&&x>0)) return halt('INVALID_CHECKPOINT');
 // No independently source-bound completed-candle contract exists yet. A caller's
 // timestamp, close and VWAP cannot establish provenance; do not emit an exit signal.
 return halt('COMPLETED_OBSERVATION_PROVENANCE_NOT_CERTIFIED');
 return {status:'FICTIONAL_CHECKPOINT_ONLY',exitSignal:completedCheckpointClose>=checkpointVWAP||
    completedCheckpointClose<=snapshot.stopInr,decision:'NO_TRADE',realOrderSubmissionPossible:false};
}

/** Only an eligible, fully accounted hypothetical BUY may establish an R stop.
 * The adapter is the single gate for source, session, chronology, budget and partial fills.
 */
export async function snapshotRStopFromAccountedEntry({entryEvent,signalDelta}={}) {
 const {assessCostAccountedCandidateEvent}=await import('./intraday_cost_accounted_adapter.mjs');
 const halt=reason=>({status:'HALT_UNKNOWN',reason,decision:'NO_TRADE',realOrderSubmissionPossible:false});
 if(!entryEvent || entryEvent.side!=='BUY') return halt('ENTRY_EVENT_REQUIRED');
 const accounted=assessCostAccountedCandidateEvent(entryEvent);
 if(accounted.status!=='HYPOTHETICAL_SCENARIO_ONLY' ||
    accounted.confirmedRealFill!==false || accounted.feesCertified!==false ||
    accounted.state?.positionShares!==entryEvent.requestedShares ||
    !(accounted.state?.costBasisInr>0)) return halt(accounted.reason||'ENTRY_NOT_COST_ACCOUNTED');
 return snapshotRStop({signalDelta,entryDecision:entryEvent.clock?.decision,
   entryFillBarStart:entryEvent.clock?.proposedFillBarStart,
   fillClockStatus:'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL',
   hypotheticalFill:entryEvent.assertedHypotheticalFill});
}
