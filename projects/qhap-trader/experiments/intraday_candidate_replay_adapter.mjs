/** Research-only candidate event adapter. Never submits or confirms real orders.
 * Consumes explicit hypothetical event assertions; does not manufacture fills.
 * Separate from the pinned February 2021 replay.
 */
import { assessIntradayClock } from './intraday_execution_clock.mjs';
const halt = (reason, positionShares=0) => ({status:'HALT_UNKNOWN',reason,positionShares,decision:'NO_TRADE',realOrderSubmissionPossible:false});
const validQty = n => Number.isSafeInteger(n) && n > 0;
const validPrice = n => typeof n === 'number' && Number.isFinite(n) && n > 0;
export function assessCandidateEvent({sourceAuthorized=false,sessionIntegrityVerified=false,clock,side,requestedShares,assertedHypotheticalFill=null,positionShares=0,capitalInr=10000}={}) {
  if (!sourceAuthorized || !sessionIntegrityVerified) return halt('SOURCE_OR_SESSION_UNVERIFIED',positionShares);
  if (!clock || !['BUY','SELL'].includes(side) || !validQty(requestedShares) || !Number.isSafeInteger(positionShares) || positionShares < 0 || !validPrice(capitalInr)) return halt('INVALID_EVENT',positionShares);
  if (side==='BUY' && positionShares!==0) return halt('ONE_POSITION_ONLY',positionShares);
  if (side==='SELL' && requestedShares!==positionShares) return halt('EXIT_MUST_REQUEST_ALL_OPEN_SHARES',positionShares);
  const assessment=assessIntradayClock({...clock,kind:side==='BUY'?'ENTRY':clock.kind==='FORCED_EXIT'?'FORCED_EXIT':'EXIT'});
  if (assessment.status!=='ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL') return halt(assessment.reason,positionShares);
  if (assertedHypotheticalFill===null) return halt('NO_HYPOTHETICAL_FILL_EVIDENCE',positionShares);
  const {shares,priceInr,fillBasis}=assertedHypotheticalFill;
  if (!validQty(shares) || shares>requestedShares || !validPrice(priceInr) || fillBasis!=='EXPLICIT_HYPOTHETICAL_OBSERVATION') return halt('INVALID_OR_UNSUPPORTED_FILL',positionShares);
  if (side==='BUY' && (shares*priceInr>Math.min(capitalInr,2500))) return halt('BUDGET_EXCEEDED',positionShares);
  const remaining=side==='BUY'?shares:positionShares-shares;
  if (shares<requestedShares || (side==='SELL' && remaining!==0)) return halt('PARTIAL_FILL_UNRESOLVED',remaining);
  return {status:'HYPOTHETICAL_EVENT_ACCOUNTED_NOT_BROKER_CONFIRMED',reason:null,positionShares:remaining,decision:'NO_TRADE',realOrderSubmissionPossible:false,confirmedRealFill:false};
}
