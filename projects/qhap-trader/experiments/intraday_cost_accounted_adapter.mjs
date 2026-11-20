/** Research-only atomic composition. No real orders, fills, or certified fees. */
import { assessCandidateEvent } from './intraday_candidate_replay_adapter.mjs';
import { applyHypotheticalLedgerEvent } from './intraday_hypothetical_cash_ledger.mjs';
const halt=(reason,state)=>({status:'HALT_UNKNOWN',reason,state,decision:'NO_TRADE',realOrderSubmissionPossible:false});
export function assessCostAccountedCandidateEvent({state,chargesInr,chargesBasis,...event}={}) {
  if (!state || state.cashInr<0 || !Number.isFinite(state.cashInr) || !Number.isSafeInteger(state.positionShares) || state.positionShares<0 || !Number.isFinite(state.costBasisInr) || state.costBasisInr<0 || state.positionShares!== (event.positionShares ?? 0)) return halt('STATE_MISMATCH_OR_INVALID',state);
  const result=assessCandidateEvent({...event,positionShares:state.positionShares});
  if (result.status!=='HYPOTHETICAL_EVENT_ACCOUNTED_NOT_BROKER_CONFIRMED') return halt(result.reason || 'EVENT_NOT_ELIGIBLE',state);
  const fill=event.assertedHypotheticalFill;
  const accounted=applyHypotheticalLedgerEvent({state,side:event.side,quantity:fill.shares,priceInr:fill.priceInr,chargesInr,chargesBasis,fillBasis:fill.fillBasis,fillComplete:true});
  if (accounted.status!=='HYPOTHETICAL_SCENARIO_ONLY') return halt(accounted.reason || 'LEDGER_REJECTED',state);
  return {...accounted,positionShares:accounted.state.positionShares,confirmedRealFill:false,feesCertified:false};
}
