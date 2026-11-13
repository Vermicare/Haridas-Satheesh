#!/usr/bin/env node
/**
 * QHAP-TRADER: reject / fail-closed evaluation of USER-SHARED
 * SANITIZED AGGREGATE DEVELOPMENT REPLAY RESULTS.
 *
 * This is an independent research classification tool, not wired to an
 * order broker, paper trader, model agency, exchange, wallet or API.
 * Never treat a positive development replay as release eligibility.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const immutableSafety=Object.freeze({
  market:'NSE_CASH_EQUITY',
  livePromotionAuthorized:false,
  finalBrokerDecision:'NO_TRADE',
  realOrdersSent:0,
  paperOrdersSent:0,
  brokerRoutePresent:false,
  guaranteedReturn:false,
  independentlyValidatedProfitability:false
});
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const n= (x,reason)=>{if(!finite(x))throw Error(reason);};
const tolerance=(a,b)=>Math.abs(a-b)<=0.001;
const fail=reason=>Object.freeze({...immutableSafety,
  status:'INVALID_OR_UNTRUSTED_DEVELOPMENT_AGGREGATE_NO_TRADE',reason});
/**
 * Use only personally audited locally saved summaries. Tampered or incomplete
 * summaries fail closed. Never infer the fee model is historically accurate.
 */
export function reviewDailySwingAggregate(e){
  try{
    if(e?.schema!=='QHAP_DEVELOPMENT_AGGREGATE_V1'||
      e?.market!=='NSE_CASH_EQUITY'||
      e?.symbol!=='RELIANCE'||
      e?.sourceClass!=='PRIVATE_REPLAY'||
      e?.researchClass!=='INSPECTED_DEVELOPMENT_NOT_UNSEEN_HOLDOUT'||
      e?.sourceDailyBarCount!==204||
      e?.sourcePeriod?.first!=='2024-01-01'||
      e?.sourcePeriod?.last!=='2024-10-24'||
      !/^[a-f0-9]{64}$/.test(e?.localArtifactSha256||'')||
      e?.virtualInitialCashRupees!==10000||
      e?.maxSingleHypotheticalPositionBudgetRupees!==2500||
      e?.hypotheticalHoldingSessions!==5||
      e?.fullAgentAuditVerifiedDecisions!==98||
      e?.realOrdersSent!==0||e?.paperOrdersSent!==0||
      e?.finalBrokerDecision!=='NO_TRADE'||
      e?.tradingEdgeIndependentlyVerified!==false||
      e?.exactHistoricalFeesCertified!==false||
      e?.corporateActionsIndependentlyVerified!==false||
      e?.assumedFeeSchedule!==
        'UPSTOX_PUBLIC_NOV2026_DELIVERY_RATES_PRO_FORMA_ON_2024_PRICES'||
      !Array.isArray(e.scenarios)||e.scenarios.length!==3)
      throw Error('SOURCE_OR_SCOPE_MISMATCH');

    const losses=[],deltaPassive=[],trades=[],grossNeg=[],recon=[];
    for(let i=0;i<3;i++){
      const s=e.scenarios[i],a=s?.agent,p=s?.passive;
      if(s?.multiplier!==i+1||!a||!p||
         s?.noTradeNetRupees!==0||
         !Number.isSafeInteger(a.hypotheticalRoundTrips)||
         a.hypotheticalRoundTrips<0||
         a.hypotheticalRoundTrips>1000||
         !Number.isSafeInteger(a.netWinningRoundTrips)||
         a.netWinningRoundTrips<0||
         a.netWinningRoundTrips>a.hypotheticalRoundTrips||
         !Number.isSafeInteger(a.watchDecisions)||
         a.watchDecisions<a.hypotheticalRoundTrips||
         p.hypotheticalRoundTrips!==1)
        throw Error('SCENARIO_CARDINALITY_INVALID');
      for(const field of [
        a.grossRupees,a.modeledFeesRupees,a.modeledExecutionDragRupees,
        a.netRupees,a.endingVirtualCashRupees,
        p.grossRupees,p.modeledFeesRupees,p.modeledExecutionDragRupees,
        p.netRupees
      ])n(field,'INVALID_NONFINITE_ACCOUNTING_FIELD');
      if(a.modeledFeesRupees<0||a.modeledExecutionDragRupees<0||
         p.modeledFeesRupees<0||p.modeledExecutionDragRupees<0||
         a.endingVirtualCashRupees<0)
        throw Error('NEGATIVE_FEES_OR_CASH');
      if(!tolerance(a.grossRupees-a.modeledFeesRupees-
          a.modeledExecutionDragRupees,a.netRupees)||
         !tolerance(p.grossRupees-p.modeledFeesRupees-
          p.modeledExecutionDragRupees,p.netRupees)||
         !tolerance(a.endingVirtualCashRupees,
          e.virtualInitialCashRupees+a.netRupees))
        throw Error('SOURCE_PROFORMA_PNL_DOES_NOT_RECONCILE');
      losses.push(a.netRupees);
      deltaPassive.push(a.netRupees-p.netRupees);
      trades.push(a.hypotheticalRoundTrips);
      grossNeg.push(a.grossRupees<0);
      recon.push(true);
    }
    const allLost=losses.every(x=>x<0);
    const allUnderperformedPassive=deltaPassive.every(x=>x<0);
    const allGrossNegative=grossNeg.every(Boolean);
    const allHadZeroWinners=e.scenarios.every(x=>
      x.agent.netWinningRoundTrips===0);
    const monotoneLoss=losses[0]>losses[1]&&losses[1]>losses[2];
    const allRejected=allLost&&allUnderperformedPassive&&
      allGrossNegative&&allHadZeroWinners;

    return Object.freeze({
      ...immutableSafety,
      status:allRejected?
        'REJECT_9_AGENT_SWING_LIVE_CANDIDATE_DEVELOPMENT_EVIDENCE':
        'UNPROVEN_MODEL_DEVELOPMENT_ONLY_NO_TRADE',
      classification:'REJECT_CURRENT_RULES_NOT_THE_ENTIRE_ASSET_CLASS',
      instrumentAlias:e.symbol,
      sourceSha256:e.localArtifactSha256,
      inspectedDailyBars:e.sourceDailyBarCount,
      amountOfIndependentHoldoutEvidence:0,
      noRealOrderRouteToDisable:true,
      allCostScenarioAccountingsReconcile:recon.every(Boolean),
      allScenariosNetNegative:allLost,
      allScenariosWorseThanPassive:allUnderperformedPassive,
      grossProfitBeforeCostsAbsent:allGrossNegative,
      allHypotheticalRoundTripsNetLosing:allHadZeroWinners,
      stricterFrictionWorsenedLoss:monotoneLoss,
      hypotheticalRoundTripsPerStress:trades,
      modeledNetRupeesPerStress:losses.map(x=>Number(x.toFixed(4))),
      underperformanceVsSameBudgetPassiveRupees:deltaPassive.map(x=>
        Number(x.toFixed(4))),
      baseCaseCostShareOfAbsoluteLossPct:Number(
        (100*(e.scenarios[0].agent.modeledFeesRupees+
          e.scenarios[0].agent.modeledExecutionDragRupees)/
          Math.abs(e.scenarios[0].agent.netRupees)).toFixed(2)),
      neverTuneAndRetestSameDatesAsUnseen:true,
      corporateActionAndHistoricalBrokerFeesVerified:false,
      canProveSwingStrategyNeverWorks:false
    });
  }catch(e){
    const reasons=new Set([
      'SOURCE_OR_SCOPE_MISMATCH','SCENARIO_CARDINALITY_INVALID',
      'INVALID_NONFINITE_ACCOUNTING_FIELD','NEGATIVE_FEES_OR_CASH',
      'SOURCE_PROFORMA_PNL_DOES_NOT_RECONCILE'
    ]);
    return fail(reasons.has(e?.message)?e.message:
      'UNEXPECTED_AGGREGATE_REVIEW_ERROR');
  }
}
const invoked=process.argv[1]&&path.resolve(process.argv[1])===
  fileURLToPath(import.meta.url);
if(invoked){
  try{
    if(process.argv.length!==3||
       process.argv[2]!=='--review-archived-user-aggregate')
      throw Error('INVALID_COMMAND');
    const file=new URL(
      '../experiments/evidence/RELIANCE_UPSTOX_204DAY_SWING_DEVELOPMENT_20261113.json',
      import.meta.url);
    const bytes=fs.readFileSync(file,'utf8');
    if(bytes.length>25000)throw Error('AGGREGATE_TOO_LARGE');
    const r=reviewDailySwingAggregate(JSON.parse(bytes));
    console.log(JSON.stringify(r,null,2));
    process.exitCode=
      r.status==='REJECT_9_AGENT_SWING_LIVE_CANDIDATE_DEVELOPMENT_EVIDENCE'?
        0:1;
  }catch{
    console.error(JSON.stringify(fail('LOCAL_RESEARCH_EVIDENCE_UNAVAILABLE')));
    process.exitCode=1;
  }
}
