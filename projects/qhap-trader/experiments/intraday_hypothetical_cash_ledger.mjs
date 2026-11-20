/** Research-only, scenario-priced cash ledger. Not broker fill or fee certification. */
const halt=(reason,state)=>({status:'HALT_UNKNOWN',reason,state,decision:'NO_TRADE',realOrderSubmissionPossible:false});
const money=n=>typeof n==='number'&&Number.isFinite(n)&&n>=0;
const shares=n=>Number.isSafeInteger(n)&&n>=0;
export function applyHypotheticalLedgerEvent({state,side,quantity,priceInr,chargesInr,chargesBasis,fillBasis,fillComplete}={}) {
  if (!state || !money(state.cashInr) || !shares(state.positionShares) || !money(state.costBasisInr) ||
      !['BUY','SELL'].includes(side) || !Number.isSafeInteger(quantity) || quantity<=0 ||
      !money(priceInr) || priceInr===0 || !money(chargesInr) ||
      chargesBasis!=='EXPLICIT_UNCERTIFIED_RESEARCH_SCENARIO' ||
      fillBasis!=='EXPLICIT_HYPOTHETICAL_OBSERVATION' || fillComplete!==true)
    return halt('UNVERIFIED_OR_INCOMPLETE_EVENT',state);
  const notional=quantity*priceInr;
  if (!Number.isFinite(notional)) return halt('NUMERIC_OVERFLOW',state);
  if (side==='BUY') {
    const allIn=notional+chargesInr;
    if (state.positionShares!==0 || !Number.isFinite(allIn) || allIn>2500 || allIn>state.cashInr)
      return halt('POSITION_OR_ALL_IN_BUDGET_EXCEEDED',state);
    return {status:'HYPOTHETICAL_SCENARIO_ONLY',state:{cashInr:state.cashInr-allIn,positionShares:quantity,costBasisInr:allIn},decision:'NO_TRADE',realOrderSubmissionPossible:false,feesCertified:false,confirmedRealFill:false};
  }
  if (quantity!==state.positionShares || quantity===0) return halt('EXIT_NOT_FULLY_RESOLVED',state);
  const proceeds=notional-chargesInr;
  if (!Number.isFinite(proceeds) || proceeds<0) return halt('INVALID_NET_PROCEEDS',state);
  return {status:'HYPOTHETICAL_SCENARIO_ONLY',state:{cashInr:state.cashInr+proceeds,positionShares:0,costBasisInr:0},realizedNetInr:proceeds-state.costBasisInr,decision:'NO_TRADE',realOrderSubmissionPossible:false,feesCertified:false,confirmedRealFill:false};
}
