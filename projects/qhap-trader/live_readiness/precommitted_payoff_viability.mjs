/**
 * QHAP-TRADER: precommitted economic FALSIFICATION, not optimization.
 * Computes break-even algebra for fixed, imaginary binary outcomes using the
 * already-merged 2026 indicative Upstox fee engine. Nothing is estimated from
 * licensed or real historical market data. The assumed hit rates are NOT
 * measured, calibrated, predicted or probabilities of future profitability.
 *
 * NSE Data Sharing & Usage Policy and brokerage terms still require separate
 * verification. NO network, orders, broker account, raw prices or credentials.
 */
import {estimateSyntheticIntradayRoundTrip as estimate}
  from './upstox_intraday_cost_stress.mjs';

const TRADE_BASE=Object.freeze({
  entryPriceRupees:100,
  quantity:20
});
const TARGET=Object.freeze({...TRADE_BASE,exitPriceRupees:101.5,
  exitReason:'TARGET'});
const STOP=Object.freeze({...TRADE_BASE,exitPriceRupees:99,
  exitReason:'STOP'});
const SHOCKS=Object.freeze([0,5,15,50]);
const GAP_FREQUENCIES=Object.freeze([0,0.05]);
const ASSUMED_WIN_RATES=Object.freeze([0.40,0.50,0.60,0.70,0.90]);
const HYPOTHETICAL_TRADE_COUNT=60; // one thought-experiment trade per calendar day
const rupees=x=>Math.round(x*100)/100;
const pct=x=>Math.round(x*10000)/100;
const allNonNegative=arr=>arr.every(x=>Number.isFinite(x)&&x>=0);
const status=(state,reason,more={})=>Object.freeze({
  status:state,
  reasons:[reason],
  kind:'FIXED_SYNTHETIC_ECONOMIC_THOUGHT_EXPERIMENT',
  accountCapitalRupees:10000,
  notionalPerHypotheticalTradeRupees:2000,
  source:'MERGED_INDICATIVE_UPSTOX_2026_FEE_ENGINE',
  hypotheticalTradeCount:HYPOTHETICAL_TRADE_COUNT,
  observedSessions:0,
  independentlyVerifiedForwardSessions:0,
  historicalOutOfSampleSessions:0,
  strategyWinRateEmpiricallyMeasured:false,
  strategyHasDemonstratedEdge:false,
  simulatedTradeFillsAuthenticated:false,
  marketDataRightsVerified:false,
  chargesVerifiedAgainstBrokerContractNotes:false,
  brokerReconciled:false,
  realOrdersSent:0,
  realOrderRoutePresent:false,
  canTrade:false,
  liveTradingAuthorized:false,
  recommendedAction:'NO_TRADE',
  noTradeComparatorRupees:0,
  ...more
});

/**
 * Fixed 1.5% gross target vs -1% gross stop at INR100 x20 shares.
 * Mathematically solve for p where:
 * E(net) = p * targetNet + (1-p)*((1-q)*stopNet + q*gapStopNet) = 0.
 *
 * q is merely an assumed proportion of losing synthetic outcomes with a
 * 200-bp ADDITIONAL gap, not an estimate of actual gap frequency.
 * The result is a break-even BOUND under these stipulated mechanics, not a
 * forecast of the probability of achieving that bound.
 */
export function assessPrecommittedSyntheticPayoffViability(){
  const cases=[];
  for(const adversityBpsEachSide of SHOCKS){
    const slip={extraBuySlipBps:adversityBpsEachSide,
      extraSellSlipBps:adversityBpsEachSide};
    const winning=estimate(TARGET,slip);
    const stopped=estimate(STOP,slip);
    const gap=estimate(STOP,{...slip,stopGapBps:200});
    if([winning,stopped,gap].some(x=>
      x.status!=='SYNTHETIC_COST_ESTIMATE_ONLY')||
      !allNonNegative([winning.estimatedChargesRupees,
        stopped.estimatedChargesRupees,gap.estimatedChargesRupees])||
      ![winning.netRupees,stopped.netRupees,gap.netRupees].every(Number.isFinite)||
      gap.netRupees>stopped.netRupees||
      winning.netRupees<=stopped.netRupees)
      return status('BLOCKED_INVALID_ECONOMIC_FIXTURE',
        'INVALID_FEE_MODEL_OR_SYNTHETIC_SCENARIO');
    for(const assumedGapFractionOfLosingTrades of GAP_FREQUENCIES){
      const lossMean=(1-assumedGapFractionOfLosingTrades)*stopped.netRupees+
        assumedGapFractionOfLosingTrades*gap.netRupees;
      const benefit=winning.netRupees-lossMean;
      if(!Number.isFinite(lossMean)||!Number.isFinite(benefit)||benefit<=0)
        return status('BLOCKED_INVALID_ECONOMIC_FIXTURE',
          'PAYOFF_ALGEBRA_UNSAFE');
      const breakEvenRate=-lossMean/benefit;
      const breakEvenPossible=(breakEvenRate>=0&&breakEvenRate<=1);
      const curves=ASSUMED_WIN_RATES.map(assumedWinFraction=>{
        const expectedPerTrade=assumedWinFraction*winning.netRupees+
          (1-assumedWinFraction)*lossMean;
        return Object.freeze({
          assumedWinRatePercent:pct(assumedWinFraction),
          expectationPerTradeRupees:rupees(expectedPerTrade),
          expectationFor60ImaginaryTradesRupees:
            rupees(expectedPerTrade*HYPOTHETICAL_TRADE_COUNT),
          beatsNoTradeOnlyUnderAssumptions:expectedPerTrade>0
        });
      });
      cases.push(Object.freeze({
        extraAdversityBpsEachSide:adversityBpsEachSide,
        assumed200BpsGapAmongLosingTradesPercent:
          pct(assumedGapFractionOfLosingTrades),
        targetGrossMovePercent:1.5,
        stopGrossMovePercent:-1,
        hypotheticalTargetNetRupees:winning.netRupees,
        hypotheticalOrdinaryStopNetRupees:stopped.netRupees,
        hypothetical200BpsGapStopNetRupees:gap.netRupees,
        hypotheticalMeanStopNetRupees:rupees(lossMean),
        theoreticalBreakEvenWinRatePercent:
          breakEvenPossible?pct(breakEvenRate):null,
        mathematicalBreakEvenPossible:breakEvenPossible,
        gapCaseBreaches50RupeeCandidateLossBudget:
          gap.hypotheticalCandidateLossBudgetExceeded,
        prospectiveSignalQualityUnknown:true,
        assumptionCurves:curves
      }));
    }
  }
  return status('NO_TRADE_ECONOMIC_FALSIFICATION_ONLY',
    'ASSUMED_OUTCOMES_ARE_NOT_A_VALIDATED_STRATEGY_OR_LIVE_DATA',{
      frozenTarget:TARGET,
      frozenStop:STOP,
      frozenAdversityBpsEachSide:[...SHOCKS],
      frozenGapRateAssumptionsPercent:GAP_FREQUENCIES.map(pct),
      frozenWinRateAssumptionsPercent:ASSUMED_WIN_RATES.map(pct),
      cases,
      riskBudgetRupees:50,
      methodology:'BINARY_TARGET_STOP_EXPECTATION_WITH_FIXED_FEES_AND_ADVERSE_GAPS',
      interpretation:'Break-even thresholds only; one-trade-per-day is not a forecast of trades or real NSE sessions.'
    });
}
