/** Fictional candidate R stop snapshot; pure research arithmetic, never a fill or order. */
export function snapshotRStop({signalDelta, hypotheticalFill, entryDecision, fillClockStatus}={}) {
 const halt=reason=>({status:'HALT_UNKNOWN',reason,decision:'NO_TRADE',realOrderSubmissionPossible:false});
 if(fillClockStatus!=='ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL') return halt('ENTRY_CLOCK_UNVERIFIED');
 if(!hypotheticalFill || hypotheticalFill.fillBasis!=='EXPLICIT_HYPOTHETICAL_OBSERVATION' ||
    hypotheticalFill.confirmedRealFill===true) return halt('HYPOTHETICAL_FILL_UNVERIFIED');
 if(typeof signalDelta!=='number'||!Number.isFinite(signalDelta)||signalDelta<=0 ||
    typeof hypotheticalFill.priceInr!=='number'||!Number.isFinite(hypotheticalFill.priceInr)||hypotheticalFill.priceInr<=0 ||
    typeof entryDecision!=='string'||!/^[0-9]{2}:[0-9]{2}$/.test(entryDecision)) return halt('INVALID_ENTRY_SNAPSHOT');
 const stopInr=hypotheticalFill.priceInr*(1-2*signalDelta);
 if(!Number.isFinite(stopInr)||stopInr<=0) return halt('INVALID_STOP');
 return Object.freeze({status:'FICTIONAL_STOP_SNAPSHOT_ONLY',entryDecision,deltaAtEntry:signalDelta,
   entryFillPriceInr:hypotheticalFill.priceInr,stopInr,decision:'NO_TRADE',realOrderSubmissionPossible:false});
}
export function evaluateRStop({snapshot,completedCheckpointClose,checkpointVWAP,afterVerifiedFill=false}={}) {
 const halt=reason=>({status:'HALT_UNKNOWN',reason,decision:'NO_TRADE',realOrderSubmissionPossible:false});
 if(snapshot?.status!=='FICTIONAL_STOP_SNAPSHOT_ONLY'||!afterVerifiedFill) return halt('ENTRY_OR_LATER_CHECKPOINT_UNVERIFIED');
 if(![completedCheckpointClose,checkpointVWAP].every(x=>typeof x==='number'&&Number.isFinite(x)&&x>0)) return halt('INVALID_CHECKPOINT');
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
   fillClockStatus:'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL',
   hypotheticalFill:entryEvent.assertedHypotheticalFill});
}
