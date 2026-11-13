import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {assessPrecommittedSyntheticPayoffViability as run}
  from './precommitted_payoff_viability.mjs';
import {estimateSyntheticIntradayRoundTrip as calc}
  from './upstox_intraday_cost_stress.mjs';

const out=()=>run();
const choose=(bps,gap)=>out().cases.find(c=>
  c.extraAdversityBpsEachSide===bps&&
  c.assumed200BpsGapAmongLosingTradesPercent===gap);
const x=p=>p.theoreticalBreakEvenWinRatePercent;
const curve=(c,p)=>c.assumptionCurves.find(r=>r.assumedWinRatePercent===p);
test('precommitted matrix has 4 economic shocks x 2 gap frequencies',()=>{
  const r=out();
  assert.equal(r.status,'NO_TRADE_ECONOMIC_FALSIFICATION_ONLY');
  assert.equal(r.cases.length,8);
  assert.deepEqual(r.frozenAdversityBpsEachSide,[0,5,15,50]);
  assert.deepEqual(r.frozenGapRateAssumptionsPercent,[0,5]);
  assert.deepEqual(r.frozenWinRateAssumptionsPercent,[40,50,60,70,90]);
});
test('fixed synthetic notional and 1.5 percent target / 1 percent stop',()=>{
  const r=out();
  assert.deepEqual(r.frozenTarget,{
    entryPriceRupees:100,quantity:20,exitPriceRupees:101.5,
    exitReason:'TARGET'
  });
  assert.deepEqual(r.frozenStop,{
    entryPriceRupees:100,quantity:20,exitPriceRupees:99,
    exitReason:'STOP'
  });
  assert.equal(r.notionalPerHypotheticalTradeRupees,2000);
});
test('correct win/loss inputs match original unchanged 2026 fee engine',()=>{
  const c=choose(0,0);
  assert.equal(c.hypotheticalTargetNetRupees,
    calc(out().frozenTarget,{extraBuySlipBps:0,extraSellSlipBps:0}).netRupees);
  assert.equal(c.hypotheticalOrdinaryStopNetRupees,
    calc(out().frozenStop,{extraBuySlipBps:0,extraSellSlipBps:0}).netRupees);
  assert.ok(c.hypotheticalTargetNetRupees<30);
  assert.ok(c.hypotheticalOrdinaryStopNetRupees< -20);
});
test('target result is gross profit minus fees not a guaranteed edge',()=>{
  const c=choose(0,0);
  assert.ok(c.hypotheticalTargetNetRupees>0);
  assert.equal(c.prospectiveSignalQualityUnknown,true);
  assert.equal(out().strategyHasDemonstratedEdge,false);
});
test('even perfect synthetic hit rate is not real market evidence',()=>{
  const r=out();
  assert.equal(r.historicalOutOfSampleSessions,0);
  assert.equal(r.independentlyVerifiedForwardSessions,0);
  assert.equal(r.observedSessions,0);
  assert.equal(r.strategyWinRateEmpiricallyMeasured,false);
});
test('real execution, contract note and broker reconciliation remain disabled',()=>{
  const r=out();
  assert.equal(r.canTrade,false);
  assert.equal(r.liveTradingAuthorized,false);
  assert.equal(r.realOrdersSent,0);
  assert.equal(r.realOrderRoutePresent,false);
  assert.equal(r.chargesVerifiedAgainstBrokerContractNotes,false);
  assert.equal(r.brokerReconciled,false);
});
test('positive assumed math does not replace a no-trade comparator',()=>{
  const r=out();
  assert.equal(r.noTradeComparatorRupees,0);
  assert.equal(r.recommendedAction,'NO_TRADE');
  assert.ok(r.cases.some(c=>c.assumptionCurves.some(x=>x.beatsNoTradeOnlyUnderAssumptions)));
});
test('zero friction still needs a strictly positive win rate',()=>{
  const c=choose(0,0);
  assert.ok(x(c)>0);
  assert.ok(x(c)<100);
  assert.equal(c.mathematicalBreakEvenPossible,true);
});
test('break-even threshold rises under more adverse slip for fixed gap assumption',()=>{
  for(const q of [0,5]){
    const thresholds=[0,5,15,50].map(slip=>x(choose(slip,q)));
    for(let i=1;i<thresholds.length;i++)
      assert.ok(thresholds[i]>=thresholds[i-1],JSON.stringify(thresholds));
  }
});
test('adding assumed tail gap cannot improve required win rate',()=>{
  for(const slip of [0,5,15,50]){
    assert.ok(x(choose(slip,5))>=x(choose(slip,0)));
  }
});
test('higher slippage never improves synthetic target net or ordinary stop',()=>{
  const c=[0,5,15,50].map(slip=>choose(slip,0));
  for(let i=1;i<c.length;i++){
    assert.ok(c[i].hypotheticalTargetNetRupees<=
      c[i-1].hypotheticalTargetNetRupees);
    assert.ok(c[i].hypotheticalOrdinaryStopNetRupees<=
      c[i-1].hypotheticalOrdinaryStopNetRupees);
  }
});
test('200bp stop-gap scenario breaches candidate risk budget',()=>{
  for(const c of out().cases){
    assert.equal(c.gapCaseBreaches50RupeeCandidateLossBudget,true);
    assert.ok(c.hypothetical200BpsGapStopNetRupees< -50);
  }
});
test('higher win rate improves only theoretical expected return at fixed shocks',()=>{
  for(const c of out().cases){
    for(let i=1;i<c.assumptionCurves.length;i++){
      assert.ok(c.assumptionCurves[i].expectationPerTradeRupees>=
        c.assumptionCurves[i-1].expectationPerTradeRupees);
    }
  }
});
test('neutral 50 percent win assumption under 1.5 to 1 gross is not guaranteed viable',()=>{
  const c=choose(15,0);
  assert.ok(curve(c,50).expectationPerTradeRupees<0);
  assert.ok(curve(c,50).expectationFor60ImaginaryTradesRupees<0);
});
test('severe 50-bp stress can make 70 percent wins insufficient',()=>{
  const c=choose(50,0);
  assert.ok(curve(c,70).expectationPerTradeRupees<0);
  assert.equal(curve(c,70).beatsNoTradeOnlyUnderAssumptions,false);
});
test('higher friction and gaps expose fragile high-hit-rate claims',()=>{
  assert.ok(x(choose(50,5))>x(choose(15,0)));
  assert.ok(x(choose(50,5))>70);
});
test('hypothetical sixty trades are NOT sixty verified live market sessions',()=>{
  const r=out();
  assert.equal(r.hypotheticalTradeCount,60);
  assert.equal(r.observedSessions,0);
  assert.equal(r.marketDataRightsVerified,false);
  assert.equal(r.simulatedTradeFillsAuthenticated,false);
});
test('expected totals follow exactly sixty hypothetical repetitions',()=>{
  for(const c of out().cases){
    for(const row of c.assumptionCurves){
      assert.ok(Math.abs(row.expectationFor60ImaginaryTradesRupees-
        60*row.expectationPerTradeRupees)<=0.31);
    }
  }
});
test('fixed output is deterministic and frozen top-level',()=>{
  assert.deepEqual(out(),out());
  assert.equal(Object.isFrozen(out()),true);
  assert.equal(Object.isFrozen(out().cases[0]),true);
});
test('no network, market-feed adapter, token or broker transport in economic module',()=>{
  const src=fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),
    'precommitted_payoff_viability.mjs'),'utf8');
  for(const forbidden of [
    /from ['"]node:https?['"]/,
    /from ['"]https?['"]/,
    /\bfetch\s*\(/,
    /\bplaceOrder\s*\(/,
    /\bsubmitOrder\s*\(/,
    /\bUpstox_ACCESS_TOKEN\b/
  ])assert.equal(forbidden.test(src),false,String(forbidden));
});
test('conservative gap scenario is strictly worse than normal stop across shocks',()=>{
  for(const c of out().cases){
    assert.ok(c.hypothetical200BpsGapStopNetRupees<
      c.hypotheticalOrdinaryStopNetRupees);
  }
});
test('expose every theoretical scenario instead of cherry picking only wins',()=>{
  const r=out();
  for(const c of r.cases){
    assert.equal(c.assumptionCurves.length,5);
    assert.ok(c.assumptionCurves.some(x=>x.assumedWinRatePercent===40));
    assert.ok(c.assumptionCurves.some(x=>x.assumedWinRatePercent===90));
  }
});
test('no accidental real-money bankroll accounting is represented as outcomes',()=>{
  const r=out();
  assert.equal(r.kind,'FIXED_SYNTHETIC_ECONOMIC_THOUGHT_EXPERIMENT');
  assert.equal(r.source,'MERGED_INDICATIVE_UPSTOX_2026_FEE_ENGINE');
  assert.equal(JSON.stringify(r).includes('marketDataPrice'),false);
  assert.equal(r.strategyHasDemonstratedEdge,false);
});
