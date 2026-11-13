#!/usr/bin/env node
/**
 * QHAP NSE: illustrative costed CHRONOLOGICAL daily-bar development replay.
 * Offline and no-orders by construction. Uses only *previously closed*
 * daily bars to form a watch, and NEXT observed daily open to hypothetically
 * enter/exit. This is NOT a paper order nor a promise of executable fills.
 *
 * COSTS ARE 2026-11 CURRENT UPSTOX PUBLISHED STANDARD SCHEDULE APPLIED
 * PRO FORMA TO OLD OBSERVED 2024 DEVELOPMENT BAR PRICES. IT IS **NOT**
 * THE HISTORICAL 2024 CONTRACT NOTE, EXCHANGE FEE SCHEDULE OR TAX RESULT.
 *
 * Official current public fee reference:
 * https://upstox.com/brokerage-charges/
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {
  validateEquityReplay,runEquitySwingAgentNetwork,
  syntheticEquityFixture,verifyEquitySwingAgentAudit
} from './nse_swing_interdependent_agent_network.mjs';

const INITIAL_CASH=10000;
const MAX_ORDER_BUDGET=2500;
const HOLD_SESSIONS=5;
const SIGNAL_WARMUP_BARS=80;
const round=x=>Math.round((x+Number.EPSILON)*10000)/10000;
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const SECURITY=Object.freeze({
  model:'OFFLINE_CHRONOLOGICAL_SWING_DEVELOPMENT_NOT_LIVE',
  finalBrokerDecision:'NO_TRADE',
  syntheticOrPrivateReplayOnly:true,
  realOrdersSent:0,paperOrdersSent:0,brokerOrderRoutePresent:false,
  networkRequestsMade:0,modelApiCallsMade:0,
  noRealMoneyOrRealBrokerOrders:true,
  tradingEdgeIndependentlyVerified:false
});
export const COST_REFERENCE=Object.freeze({
  label:'UPSTOX_PUBLIC_2026_11_NSE_DELIVERY_PRO_FORMA_NOT_2024_HISTORICAL_FEES',
  asOf:'2026-11-13',
  source:'https://upstox.com/brokerage-charges/',
  brokeragePerExecutedOrderRupees:20,
  dpChargePerScripSellDayRupees:20,
  deliverySttRatePerSide:0.001,
  nseTransactionRatePerSide:0.0000307, // from 2026-03-01
  sebiTurnoverRate:0.000001, // INR 10 per INR crore
  buyStampDutyRate:0.00015,
  gstRateOnBrokerageExchangeAndDp:0.18,
  ipftAndOtherAccountSpecificChargesFullyCertified:false,
  contractNoteFeeRoundingIndependentlyCertified:false,
  exchangeHistoricRate2024Certified:false,
  notAnExactHistoricalTariff:true
});
/**
 * Isolated arithmetic, not exchange/broker API. Based on posted public
 * standard DELIVERY tariffs applicable in 2026-11. No user-plan overrides.
 */
export function indicativeDeliverySideFees(side,notional){
  if(!['BUY','SELL'].includes(side)||!finite(notional)||notional<=0||
     notional>1e8)throw Error('INVALID_DELIVERY_FEE_INPUT');
  const brokerage=20;
  const stt=0.001*notional;
  const exchange=.0000307*notional;
  const sebi=.000001*notional;
  const stamp=side==='BUY'?.00015*notional:0;
  const dp=side==='SELL'?20:0;
  const gst=.18*(brokerage+exchange+dp);
  const total=brokerage+stt+exchange+sebi+stamp+dp+gst;
  return {total,components:{brokerage,stt,exchange,sebi,stamp,dp,gst},
    ...{feesDateAccurateFor2024:false,contractNoteCertified:false}};
}
// Slippage, spread and reserves are purposely exposed as assumptions; a
// measured slippage estimate incorporating spread must set spread=0.
const assumptions=Object.freeze({
  oneSideSlippageBps:15,
  roundTripSpreadBps:8,
  roundTripUncertaintyReserveBps:10
});
export function hypotheticalNextOpenExecution(open,side,frictionMultiplier=1){
  if(!finite(open)||open<=0||!['BUY','SELL'].includes(side)||
    ![1,2,3].includes(frictionMultiplier))
    throw Error('INVALID_HYPOTHETICAL_FILL_INPUT');
  const bps=frictionMultiplier*(
    assumptions.oneSideSlippageBps+
    assumptions.roundTripSpreadBps/2+
    assumptions.roundTripUncertaintyReserveBps/2);
  return open*(side==='BUY'?1+bps/10000:1-bps/10000);
}
function enter(open,cash,frictionMultiplier,budget=MAX_ORDER_BUDGET){
  const fill=hypotheticalNextOpenExecution(open,'BUY',frictionMultiplier);
  let qty=Math.floor(Math.min(budget,cash)/fill);
  while(qty>0){
    const notional=qty*fill;
    const charge=indicativeDeliverySideFees('BUY',notional).total;
    if(notional+charge<=Math.min(budget,cash))
      return {qty,fill,buyCost:notional+charge,entryFee:charge,rawOpen:open};
    qty--;
  }
  return null;
}
function exit(position,open,frictionMultiplier){
  const fill=hypotheticalNextOpenExecution(open,'SELL',frictionMultiplier);
  const saleNotional=position.qty*fill;
  const exitFee=indicativeDeliverySideFees('SELL',saleNotional).total;
  return {
    proceeds:saleNotional-exitFee,
    fees:position.entryFee+exitFee,
    priceMovement:position.qty*(open-position.rawOpen),
    executionDrag:position.qty*((position.fill-position.rawOpen)+(open-fill)),
    netPnl:saleNotional-exitFee-position.buyCost
  };
}
function finishScenario({
  gross,fees,drag,cash,roundTrips,winners,watchCount,
  rejectedBudget,position,sourceDays,frictionMultiplier,
  maxDrawdownPct,guardianVerifiedCount
}){
  if(position!==null)throw Error('REPLAY_POSITION_NOT_FLAT_AT_END');
  const net=cash-INITIAL_CASH;
  // Within rounding tolerance the P&L decomposition must reconcile.
  if(Math.abs(net-(gross-fees-drag))>.00001)
    throw Error('REPLAY_ACCOUNTING_DOES_NOT_RECONCILE');
  return {
    frictionMultiplier,
    eligibleDailyBars:sourceDays,
    decisionWarmupBars:SIGNAL_WARMUP_BARS,
    watchDecisionsWhileFlat:watchCount,
    agentAuditVerifiedDecisions:guardianVerifiedCount,
    hypotheticalRoundTrips:roundTrips,
    hypotheticalNetWinningRoundTrips:winners,
    budgetOrPriceRejectedWatches:rejectedBudget,
    grossOpenToOpenPriceMovementRupees:round(gross),
    public2026ProFormaBrokerFeesAndTaxesRupees:round(fees),
    assumedAdverseExecutionDragRupees:round(drag),
    aggregateIllustrativeNetRupees:round(net),
    endVirtualCashRupees:round(cash),
    modeledReturnOnInitialVirtualCashPercent:round(100*net/INITIAL_CASH),
    estimatedCloseMarkToMarketMaxDrawdownPct:round(maxDrawdownPct),
    finalPosition:'FLAT_BY_LAST_OBSERVED_SESSION_OPEN',
    finalStateNotARealExchangeFill:true,
    realizedPnlIsHypothetical:true
  };
}
async function simulateAgentWatch(data,frictionMultiplier){
  const bars=data.dailyBars;
  let cash=INITIAL_CASH,position=null,roundTrips=0,winners=0,
    gross=0,fees=0,drag=0,watchCount=0,rejectedBudget=0,
    guardianVerifiedCount=0,peak=INITIAL_CASH,maxDrawdownPct=0;
  for(let i=SIGNAL_WARMUP_BARS;i<bars.length;i++){
    const b=bars[i];
    let exited=false;
    if(position&&(i-position.entryIndex>=HOLD_SESSIONS||i===bars.length-1)){
      const r=exit(position,b.open,frictionMultiplier);
      cash+=r.proceeds;
      gross+=r.priceMovement;fees+=r.fees;drag+=r.executionDrag;
      if(r.netPnl>0)winners++;
      roundTrips++;position=null;exited=true;
    }
    // An exit cannot also enter on the same observed open; last open is
    // only the end-of-replay flattening convention, NOT a future fill.
    if(!position&&!exited&&i<bars.length-1){
      const view={...data,asOfDate:bars[i-1].date,
        dailyBars:bars.slice(0,i)};
      const a=await runEquitySwingAgentNetwork(view);
      if(a.finalDecision!=='NO_TRADE'||
         !verifyEquitySwingAgentAudit(a)||
         a.realOrdersSent!==0||a.paperOrdersSent!==0)
        throw Error('REPLAY_AGENT_RISK_VETO_INVALID');
      guardianVerifiedCount++;
      if(a.researchWatch){
        watchCount++;
        const candidate=enter(b.open,cash,frictionMultiplier);
        if(candidate){
          position={...candidate,entryIndex:i};
          cash-=position.buyCost;
        }else rejectedBudget++;
      }
    }
    const marked=cash+(position?position.qty*b.close:0);
    peak=Math.max(peak,marked);
    maxDrawdownPct=Math.max(maxDrawdownPct,
      100*(peak-marked)/peak);
  }
  return finishScenario({gross,fees,drag,cash,roundTrips,winners,
    watchCount,rejectedBudget,position,sourceDays:bars.length,
    frictionMultiplier,maxDrawdownPct,guardianVerifiedCount});
}
function simulatePassive(data,frictionMultiplier){
  const bars=data.dailyBars;
  const first=enter(bars[SIGNAL_WARMUP_BARS].open,INITIAL_CASH,
    frictionMultiplier);
  if(!first)return {
    policy:'PASSIVE_SAME_POSITION_BUDGET',
    status:'PASSIVE_UNAFFORDABLE',
    netRupees:0,roundTrips:0
  };
  const sold=exit(first,bars.at(-1).open,frictionMultiplier);
  return {
    policy:'PASSIVE_SAME_POSITION_BUDGET',
    status:'ONE_OPEN_TO_LAST_OPEN_HYPOTHETICAL_ROUNDTRIP',
    initialOrderBudgetRupees:MAX_ORDER_BUDGET,
    hypotheticalRoundTrips:1,
    netRupees:round(sold.netPnl),
    grossRupees:round(sold.priceMovement),
    feesAndTaxesRupees:round(sold.fees),
    adverseExecutionDragRupees:round(sold.executionDrag),
    note:'NOT a reinvested dividend/adjusted ETF benchmark; source selection biased'
  };
}
export async function replayDailySwingDevelopment(data){
  const validated=validateEquityReplay(data);
  if(validated.dailyBars.length<=SIGNAL_WARMUP_BARS+1)
    throw Error('INSUFFICIENT_DAILY_BARS_FOR_CHRONOLOGICAL_REPLAY');
  const scenarios=[];
  for(const stress of [1,2,3]){
    const agent=await simulateAgentWatch(validated,stress);
    const passive=simulatePassive(validated,stress);
    scenarios.push({
      scenario:'ILLUSTRATIVE_'+stress+'X_EXECUTION_FRICTION',
      ...{agentWatchPolicy:agent,passiveSameBudget:passive,
        noTradeRupees:0,remainingCapitalUnleveraged:true}
    });
  }
  return {
    ...SECURITY,status:'LOCAL_DAILY_DEVELOPMENT_REPLAY_COMPLETED_NO_TRADE',
    instrumentAlias:validated.symbol,
    sourceClassification:validated.sourceClass,
    sourceDays:validated.dailyBars.length,
    firstSourceDate:validated.dailyBars[0].date,
    finalSourceDate:validated.dailyBars.at(-1).date,
    researchSampleType:'INSPECTED_DEVELOPMENT_NOT_UNSEEN_HOLDOUT',
    initialVirtualCapitalRupees:INITIAL_CASH,
    maxSingleHypotheticalOrderTotalBudgetRupees:MAX_ORDER_BUDGET,
    modelHoldSessions:HOLD_SESSIONS,
    buysAndSellsAt:'NEXT_OBSERVED_DAILY_OPEN_ASSUMED_NOT_EXECUTABLE_FILL',
    currentPublishedCostModel:COST_REFERENCE,
    frictionAssumptions:assumptions,
    historicalTariffAndTaxesAccountAccurate:false,
    corporateActionsIndependentlyVerified:false,
    calendarAndExchangeBookIndependentlyVerified:false,
    noModelReoptimizationFromObservedDates:true,
    comparisonCapitalBasis:'SAME_2500_SINGLE_POSITION_CAP_IDLE_CASH_10000_START',
    independentEvidenceOfProfit:false,
    scenarios
  };
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  try{
    let input,sourceSha=null;
    if(process.argv.length===3&&process.argv[2]==='--synthetic-demo'){
      input=syntheticEquityFixture();
    }else if(process.argv.length===4&&
      process.argv[2]==='--private-development-file'&&
      path.isAbsolute(process.argv[3])){
      const bytes=fs.readFileSync(process.argv[3],'utf8');
      if(bytes.length>1_000_000)throw Error('PRIVATE_REPLAY_TOO_LARGE');
      sourceSha=crypto.createHash('sha256').update(bytes).digest('hex');
      input=JSON.parse(bytes);
      if(input?.sourceClass!=='PRIVATE_REPLAY')
        throw Error('PRIVATE_SOURCE_CLASS_REQUIRED');
    }else throw Error('INVALID_REPLAY_COMMAND');
    const r=await replayDailySwingDevelopment(input);
    console.log(JSON.stringify({...r,sourceSha256:sourceSha},null,2));
  }catch(e){
    const reason=/^(INVALID_|INSUFFICIENT_|REPLAY_|PRIVATE_REPLAY_TOO_LARGE|PRIVATE_SOURCE_CLASS_REQUIRED)$/.test(e?.message||'')?
      e.message:'SOURCE_OR_REPLAY_UNVERIFIED_MANUAL_REVIEW';
    console.error(JSON.stringify({...SECURITY,
      status:'OFFLINE_DAILY_REPLAY_BLOCKED_NO_TRADE',reason},null,2));
    process.exitCode=1;
  }
}
