/**
 * QHAP-TRADER: ORIGINAL, dependency-free economics-screening calculator.
 *
 * Research pattern cross-referenced against QuantConnect LEAN fee/fill
 * modeling, NautilusTrader liquidity/friction realism, and financial ML
 * validation/purging frameworks. NO external project code was copied.
 *
 * This does NOT predict price direction, trade, authenticate broker costs,
 * or authorize live orders. All inputs are assumptions, never inferred
 * from private market prices, and no signal or trading adapter is imported.
 */
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const rounded=x=>Math.round(x*1e6)/1e6;
const ALWAYS=Object.freeze({
  mode:'RESEARCH_ECONOMIC_FEASIBILITY_ONLY',
  liveTradingAuthorized:false,
  canRecommendEntry:false,
  realOrdersSent:0,
  brokerEndpointsPresent:false
});
const invalid=reason=>Object.freeze({
  ...ALWAYS,status:'INVALID_OR_INCOMPLETE_ASSUMPTIONS_NO_TRADE',
  reason
});
/**
 * Given hypothetical per-share edge in basis points, require the modeled
 * future expected price movement to EXCEED cost under 1x, 2x and 3x
 * total-friction stresses. Positive result is NOT a trading signal.
 *
 * The origin of expectedGrossMoveBps cannot be validated by this function,
 * so explicit provenance flags affect classification, never live permission.
 */
export function screenCostedHypothesis({
  entryNotionalRupees,expectedGrossMoveBps,roundTripBrokerTaxesRupees,
  slippageBpsPerSide,roundTripSpreadBps,uncertaintyReserveBps,
  parametersFrozenBeforeNewData=false,
  independentlyEvaluatedGrossForecast=false,
  brokerRatesIndependentlyVerified=false
}={}){
  const fields={entryNotionalRupees,expectedGrossMoveBps,
    roundTripBrokerTaxesRupees,slippageBpsPerSide,
    roundTripSpreadBps,uncertaintyReserveBps};
  if(Object.values(fields).some(v=>!finite(v))||
     entryNotionalRupees<=0||entryNotionalRupees>10_000_000||
     expectedGrossMoveBps < -10000||expectedGrossMoveBps>10000||
     roundTripBrokerTaxesRupees<0||roundTripBrokerTaxesRupees>1_000_000||
     slippageBpsPerSide<0||slippageBpsPerSide>500||
     roundTripSpreadBps<0||roundTripSpreadBps>1000||
     uncertaintyReserveBps<0||uncertaintyReserveBps>1000)
    return invalid('NONFINITE_NEGATIVE_OR_IMPLAUSIBLE_ASSUMPTIONS');
  if([parametersFrozenBeforeNewData,independentlyEvaluatedGrossForecast,
    brokerRatesIndependentlyVerified].some(x=>typeof x!=='boolean'))
    return invalid('EVIDENCE_FLAGS_MUST_BE_BOOLEAN');

  const brokerTaxesBps=roundTripBrokerTaxesRupees/
    entryNotionalRupees*10000;
  const oneWaySlippageTotalBps=2*slippageBpsPerSide;
  const frictionBps=brokerTaxesBps+oneWaySlippageTotalBps+
    roundTripSpreadBps+uncertaintyReserveBps;
  const stress=[1,2,3].map(multiplier=>{
    const costBps=frictionBps*multiplier;
    return {
      multiplier,costBps:rounded(costBps),
      projectedNetBps:rounded(expectedGrossMoveBps-costBps),
      projectedNetRupees:rounded(entryNotionalRupees*
        (expectedGrossMoveBps-costBps)/10000),
      positiveAfterAssumedCosts:expectedGrossMoveBps>costBps
    };
  });
  const documented=parametersFrozenBeforeNewData&&
    independentlyEvaluatedGrossForecast&&brokerRatesIndependentlyVerified;
  const allPositive=stress.every(x=>x.positiveAfterAssumedCosts);
  const status=!documented
    ?'RESEARCH_PROVENANCE_OR_FEES_UNVERIFIED_NO_TRADE'
    :allPositive
      ?'RESEARCH_CLEARS_3X_ASSUMED_FRICTION_ONLY_NO_TRADE'
      :'RESEARCH_EDGE_FALSIFIED_BY_ASSUMED_FRICTION_NO_TRADE';
  return Object.freeze({
    ...ALWAYS,status,
    projectedGrossBps:rounded(expectedGrossMoveBps),
    projectedGrossRupees:rounded(
      entryNotionalRupees*expectedGrossMoveBps/10000),
    costBreakdownBps:{
      brokerTaxes:rounded(brokerTaxesBps),
      twoSidedSlippage:rounded(oneWaySlippageTotalBps),
      spread:rounded(roundTripSpreadBps),
      uncertaintyReserve:rounded(uncertaintyReserveBps)
    },
    minimumBreakEvenGrossBpsAt1x:rounded(frictionBps),
    minimumBreakEvenGrossBpsAt3x:rounded(frictionBps*3),
    stress,
    actualTradeProbabilityKnown:false,
    forecastReliabilityCertified:false,
    guaranteedReturn:false
  });
}
/**
 * Descriptive, NOT predictive, extra gross P&L per round trip required
 * to erase an *observed* aggregate model loss if each additional gain
 * arrived without changing fees, fills or the trade sequence.
 *
 * This is NOT a strategy optimization target and cannot be used to
 * select parameters on the same development data.
 */
export function describeObservedBreakEvenGap({
  policy,roundTrips,aggregateModeledNetRupees,
  candidateCompleteStockDays
}={}){
  if(typeof policy!=='string'||!/^([A-Z_]{2,40})$/.test(policy)||
     !Number.isSafeInteger(roundTrips)||roundTrips<0||
     !Number.isSafeInteger(candidateCompleteStockDays)||
     candidateCompleteStockDays<=0||
     !finite(aggregateModeledNetRupees))
    return invalid('INVALID_AGGREGATE_DESCRIPTIVE_INPUT');
  if(roundTrips===0&&aggregateModeledNetRupees!==0)
    return invalid('CANNOT_HAVE_NONZERO_PNL_WITHOUT_RECORDED_ROUNDTRIPS');
  return Object.freeze({
    ...ALWAYS,
    status:'DESCRIPTIVE_DEVELOPMENT_LOSS_GAP_NOT_A_SIGNAL',
    policy,
    roundTrips,candidateCompleteStockDays,
    modeledNetRupees:rounded(aggregateModeledNetRupees),
    additionalGrossRupeesPerRoundTripForArithmeticBreakEven:
      roundTrips===0?null:
        rounded(Math.max(0,-aggregateModeledNetRupees/roundTrips)),
    singleCompoundedAccountDemonstrated:false,
    sourceMarketPricesAccessed:false,
    canUseToSelectParametersOnSameDates:false
  });
}
