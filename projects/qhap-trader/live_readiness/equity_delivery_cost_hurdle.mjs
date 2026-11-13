#!/usr/bin/env node
/**
 * QHAP-TRADER: offline arithmetic-only feasibility of tiny NSE-equity
 * delivery swings using the repository's 2026-11 Upstox PUBLIC pro-forma
 * fee assumptions. NO market data, strategy fitting, broker SDK or network.
 * This is NOT a historical 2024 contract note, a price forecast, or a trade.
 * One hypothetical buy and one sell order of the same scrip are assumed.
 */
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {indicativeDeliverySideFees,hypotheticalNextOpenExecution}
  from './nse_swing_costed_chronological_replay.mjs';

export const COST_HURDLE_POLICY=Object.freeze({
  startingVirtualCashRupees:10000,
  maxHypotheticalBuyOrderTotalRupees:2500,
  entryReferencePricesRupees:Object.freeze([250,500,1000,1500,2000,2500]),
  frictionMultipliers:Object.freeze([1,2,3]),
  feeSchedule:'UPSTOX_PUBLIC_2026_11_PRO_FORMA_NOT_HISTORICAL_NOT_ACCOUNT_CERTIFIED',
  source:'https://upstox.com/brokerage-charges/',
  oneBuyOneSellExecutedOrder:true,
  dividendAndCorporateActionAdjustmentCertified:false,
  actualExecutionAndContractNoteCertified:false,
  orderBookOrProfitableStrategyVerified:false
});
const finitePositive=x=>typeof x==='number'&&Number.isFinite(x)&&x>0;
const round4=x=>Math.round((x+Number.EPSILON)*1e4)/1e4;
const SAFETY=Object.freeze({
  status:'OFFLINE_FIXED_COST_FEASIBILITY_NOT_AN_EDGE_TEST',
  finalBrokerDecision:'NO_TRADE',realOrdersSent:0,paperOrdersSent:0,
  realOrderSubmissionPossible:false,brokerOrderRoutePresent:false,
  marketDataAccessed:false,strategyBacktested:false,
  profitsOrFutureReturnsGuaranteed:false
});

function initialHypotheticalPosition(entryReferenceRupees,multiplier){
  const entryFill=hypotheticalNextOpenExecution(entryReferenceRupees,'BUY',multiplier);
  let quantity=Math.floor(COST_HURDLE_POLICY.maxHypotheticalBuyOrderTotalRupees/entryFill);
  while(quantity>0){
    const buyNotional=quantity*entryFill;
    const buyFees=indicativeDeliverySideFees('BUY',buyNotional).total;
    const buyTotal=buyNotional+buyFees;
    if(buyTotal<=COST_HURDLE_POLICY.maxHypotheticalBuyOrderTotalRupees)
      return {entryFill,quantity,buyNotional,buyFees,buyTotal};
    quantity--;
  }
  return null;
}

/** Pure hypothetical P&L for a PRESET reference future open; not a signal. */
export function hypotheticalDeliveryNet(entryReferenceRupees,
  exitReferenceRupees,frictionMultiplier=1){
  if(!finitePositive(entryReferenceRupees)||
    !finitePositive(exitReferenceRupees)||
    ![1,2,3].includes(frictionMultiplier))
    throw Error('INVALID_COST_HURDLE_INPUT');
  const position=initialHypotheticalPosition(entryReferenceRupees,frictionMultiplier);
  if(!position)return {...SAFETY,feasibility:'UNAFFORDABLE_WITH_FEES',
    hypotheticalQuantity:0,hypotheticalNetRupees:null};
  const sellFill=hypotheticalNextOpenExecution(
    exitReferenceRupees,'SELL',frictionMultiplier);
  const sellNotional=position.quantity*sellFill;
  const sellFees=indicativeDeliverySideFees('SELL',sellNotional).total;
  const pnl=sellNotional-sellFees-position.buyTotal;
  return {...SAFETY,feasibility:'MODELED_ONE_ROUND_TRIP',
    hypotheticalQuantity:position.quantity,
    hypotheticalNetRupees:pnl,
    indicativeCombinedFeesRupees:position.buyFees+sellFees,
    hypotheticalEntryCashUsedRupees:position.buyTotal};
}

/** Find future *raw reference open* needed to cover modeled costs. */
export function assessDeliveryCostHurdle(entryReferenceRupees,
  frictionMultiplier=1){
  if(!finitePositive(entryReferenceRupees)||
     entryReferenceRupees>1e8||![1,2,3].includes(frictionMultiplier))
    throw Error('INVALID_COST_HURDLE_INPUT');
  const pos=initialHypotheticalPosition(entryReferenceRupees,frictionMultiplier);
  if(!pos)return {...SAFETY,
    entryReferenceRupees,frictionMultiplier,
    affordability:'NO_WHOLE_SHARE_WITHIN_2500_TOTAL_BUDGET',
    hypotheticalQuantity:0,breakEvenReferenceExitRupees:null,
    breakEvenRawOpenAppreciationPercent:null,
    historicalFeeAccuracyCertified:false};
  let lo=entryReferenceRupees,hi=entryReferenceRupees*2;
  for(let i=0;i<20&&hypotheticalDeliveryNet(
    entryReferenceRupees,hi,frictionMultiplier).hypotheticalNetRupees<0;i++)hi*=2;
  if(!Number.isFinite(hi)||hypotheticalDeliveryNet(
    entryReferenceRupees,hi,frictionMultiplier).hypotheticalNetRupees<0)
    throw Error('COST_HURDLE_NUMERICAL_FAILURE');
  for(let i=0;i<60;i++){
    const mid=lo+(hi-lo)/2;
    if(hypotheticalDeliveryNet(entryReferenceRupees,mid,
      frictionMultiplier).hypotheticalNetRupees>=0)hi=mid;
    else lo=mid;
  }
  const atThreshold=hypotheticalDeliveryNet(
    entryReferenceRupees,hi,frictionMultiplier);
  return {...SAFETY,entryReferenceRupees,frictionMultiplier,
    affordability:'WHOLE_SHARE_FEASIBLE_UNDER_2500_BUDGET',
    hypotheticalQuantity:pos.quantity,
    indicativeEntryCashUsedRupees:round4(pos.buyTotal),
    indicativeCombinedFeesAtThresholdRupees:round4(atThreshold.indicativeCombinedFeesRupees),
    breakEvenReferenceExitRupees:round4(hi),
    breakEvenRawOpenAppreciationPercent:round4(
      100*(hi/entryReferenceRupees-1)),
    historicalFeeAccuracyCertified:false,
    note:'Pure fee/slippage hurdle: no evidence the market can reach this price or fill the hypothetical trade'
  };
}

export function fixedDeliveryCostHurdleGrid(){
  return {...SAFETY,
    warning:'Hypothetical price grid only: do not optimize rejected strategies on inspected bars',
    feeReference:COST_HURDLE_POLICY.feeSchedule,
    results:COST_HURDLE_POLICY.entryReferencePricesRupees.flatMap(price=>
      COST_HURDLE_POLICY.frictionMultipliers.map(mult=>
        assessDeliveryCostHurdle(price,mult)))};
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  if(process.argv.length!==2){
    console.error('NO_ARGS_ACCEPTED_FIXED_OFFLINE_RESEARCH_ONLY');
    process.exitCode=1;
  }else console.log(JSON.stringify(fixedDeliveryCostHurdleGrid(),null,2));
}
