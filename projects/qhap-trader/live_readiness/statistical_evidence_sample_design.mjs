/**
 * QHAP-TRADER — predeclared OFFLINE sample-design sanity check.
 * This calculates how many mathematically independent, identically
 * distributed FIXED-payoff target wins would be needed before a two-sided
 * 95% Wilson lower bound rises above a fee-aware *hypothetical* break-even
 * target-hit fraction. It does not evaluate or ingest actual trades.
 *
 * The IID/Bernoulli assumptions usually fail for clustered intraday
 * trades, continuous or partially filled exits, drifting win/loss sizes,
 * incomplete dates and strategy selection. Real approval demands a
 * licensed, precommitted, per-day costed holdout with day-block estimates.
 * A success in this mathematical planner NEVER certifies trading edge.
 *
 * No network, broker SDK, credentials, raw price inputs or real orders.
 */
import {assessPrecommittedSyntheticPayoffViability}
  from './precommitted_payoff_viability.mjs';

export const FROZEN_SAMPLE_SIZES=Object.freeze([30,60,100,250,500]);
const Z95=1.959963984540054; // standard two-sided 95% normal interval
const round=(x,places=2)=>Number(x.toFixed(places));

/** A Wilson bound for an ASSUMED IID binary frequency only. */
export function wilsonLower95(wins,count){
  if(!Number.isSafeInteger(wins)||!Number.isSafeInteger(count)||
     count<1||count>10000||wins<0||wins>count)
    throw Error('INVALID_IID_BINOMIAL_COUNTS');
  // Exact zero successes must have an exact zero lower bound; avoid\n  // floating-point cancellation producing a spurious tiny positive value.\n  if(wins===0)return 0;\n  const p=wins/count,z2=Z95*Z95,denom=1+z2/count;
  const center=p+z2/(2*count);
  const radius=Z95*Math.sqrt(p*(1-p)/count+z2/(4*count*count));
  return Math.max(0,(center-radius)/denom);
}
/**
 * Minimal hypothetical count with lower bound STRICTLY above break-even.
 * A null threshold means even all-100%-winning cases are insufficient.
 * Never pass observed trading outcomes through this helper as "approved".
 */
export function minimumHypotheticalWins(count,breakEvenFraction){
  if(!Number.isSafeInteger(count)||count<1||count>10000||
     typeof breakEvenFraction!=='number'||
     !Number.isFinite(breakEvenFraction)||
     breakEvenFraction<0||breakEvenFraction>=1)
    throw Error('INVALID_HYPOTHETICAL_SAMPLE_PLAN');
  if(wilsonLower95(count,count)<=breakEvenFraction)return null;
  let lo=0,hi=count;
  while(lo<hi){
    const mid=Math.floor((lo+hi)/2);
    if(wilsonLower95(mid,count)>breakEvenFraction)hi=mid;
    else lo=mid+1;
  }
  return lo;
}
function report(status,reasons,more={}){
  return Object.freeze({
    status,reasons:[...new Set(reasons)].sort(),
    mode:'STATIC_SYNTHETIC_SAMPLE_SIZE_DESIGN',
    independenceAndStationarityVerified:false,
    anyActualTradeObservationsUsed:false,
    realMarketDataUsed:false,
    genuineIndependentDaysVerified:0,
    independentlyVerifiedForwardSessions:0,
    strategyPositiveEdgeIndependentlyVerified:false,
    strategyReturnDistributionVerified:false,
    marketDataEntitlementVerified:false,
    brokerContractNotesReconciled:false,
    realOrdersSent:0,realOrderRoutePresent:false,
    canTrade:false,liveTradingAuthorized:false,
    noTradeComparatorRupees:0,recommendedAction:'NO_TRADE',
    ...more
  });
}
/**
 * Frozen grid from the earlier merged payoff model. All scenarios included,
 * including the harsh 50bps case. No fitting or parameter search.
 */
export function designPrecommittedEvidenceSample(){
  const p=assessPrecommittedSyntheticPayoffViability();
  if(p.status!=='NO_TRADE_ECONOMIC_FALSIFICATION_ONLY'||
    !Array.isArray(p.cases)||p.cases.length!==8)
    return report('BLOCKED_PAYOFF_MODEL_MISSING',
      ['UNVERIFIED_OR_CHANGED_SYNTHETIC_PAYOFF_MODEL']);
  const cases=[];
  for(const c of p.cases){
    const percent=c.theoreticalBreakEvenWinRatePercent;
    if(typeof percent!=='number'||!Number.isFinite(percent)||
       percent<0||percent>=100||
       ![0,5,15,50].includes(c.extraAdversityBpsEachSide)||
       ![0,5].includes(c.assumed200BpsGapAmongLosingTradesPercent))
      return report('BLOCKED_INVALID_PAYOFF_THRESHOLDS',
        ['INVALID_OR_UNSCOPED_BREAK_EVEN_SCENARIO']);
    const threshold=percent/100;
    const sampleSizes=FROZEN_SAMPLE_SIZES.map(n=>{
      const k=minimumHypotheticalWins(n,threshold);
      return Object.freeze({
        imaginaryIndependentTrades:n,
        requiredImaginaryTargetWins:k,
        minimumImaginaryTargetHitRatePercent:k===null?null:
          round(100*k/n),
        wilsonLowerAtMinimumPercent:k===null?null:
          round(100*wilsonLower95(k,n)),
        allWinsWilsonLowerPercent:round(100*wilsonLower95(n,n)),
        anyEvidenceActuallyObserved:false,
        notSufficientForProfitCertification:true
      });
    });
    cases.push(Object.freeze({
      extraAdversityBpsEachSide:c.extraAdversityBpsEachSide,
      assumed200BpsGapAmongLosingTradesPercent:
        c.assumed200BpsGapAmongLosingTradesPercent,
      theoreticalBreakEvenHitRatePercent:percent,
      confidenceConstruction:'TWO_SIDED_95_PERCENT_WILSON_ILLUSTRATION_ONLY',
      samples:sampleSizes
    }));
  }
  return report('RESEARCH_SAMPLE_REQUIREMENTS_ONLY',[
    'WILSON_IID_ASSUMPTION_UNVERIFIED_FOR_INTRADAY_TRADES',
    'HYPOTHETICAL_WIN_COUNTS_ARE_NOT_OBSERVED_TRADES',
    'STATISTICAL_HIT_RATE_CANNOT_SUBSTITUTE_FOR_NET_DAY_BLOCK_PNL',
    'SOURCE_RIGHTS_AND_PRECOMMITTED_UNTOUCHED_DATA_UNVERIFIED'
  ],{
    nominalWilsonCoveragePercent:95,
    hypothesis:'NET_TARGET_STOP_RETURN_GREATER_THAN_ZERO_AFTER_FEES',
    confidenceLevelPrecommitted:true,
    minimumForwardSessionProtocolCount:60,
    forwardSessionCountIsNotIndependentTradeCount:true,
    predeclaredImaginaryTradeCountGrid:[...FROZEN_SAMPLE_SIZES],
    cases,
    externalDecision:'NO_STATISTICAL_ACCEPTANCE_OR_LIVE_TRADING'
  });
}
