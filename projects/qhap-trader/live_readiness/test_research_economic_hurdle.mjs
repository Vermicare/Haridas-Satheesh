import test from 'node:test';
import assert from 'node:assert/strict';
import {screenCostedHypothesis,describeObservedBreakEvenGap}
 from './research_economic_hurdle.mjs';

const assumption={
 entryNotionalRupees:2500,
 expectedGrossMoveBps:20,
 roundTripBrokerTaxesRupees:1,
 slippageBpsPerSide:15,
 roundTripSpreadBps:5,
 uncertaintyReserveBps:5,
 parametersFrozenBeforeNewData:true,
 independentlyEvaluatedGrossForecast:true,
 brokerRatesIndependentlyVerified:true
};
test('cost hurdle accounts for both directions and tax fees at 1x/2x/3x',()=>{
 const r=screenCostedHypothesis(assumption);
 assert.equal(r.mode,'RESEARCH_ECONOMIC_FEASIBILITY_ONLY');
 assert.equal(r.costBreakdownBps.brokerTaxes,4);
 assert.equal(r.costBreakdownBps.twoSidedSlippage,30);
 assert.equal(r.costBreakdownBps.spread,5);
 assert.equal(r.costBreakdownBps.uncertaintyReserve,5);
 assert.equal(r.minimumBreakEvenGrossBpsAt1x,44);
 assert.equal(r.minimumBreakEvenGrossBpsAt3x,132);
 assert.deepEqual(r.stress.map(x=>x.multiplier),[1,2,3]);
 assert.deepEqual(r.stress.map(x=>x.positiveAfterAssumedCosts),[false,false,false]);
 assert.equal(r.status,'RESEARCH_EDGE_FALSIFIED_BY_ASSUMED_FRICTION_NO_TRADE');
 assert.equal(r.realOrdersSent,0);
 assert.equal(r.liveTradingAuthorized,false);
});
test('a positive forecast still cannot clear 3x costs unless it exceeds 3x hurdle',()=>{
 const r=screenCostedHypothesis({...assumption,expectedGrossMoveBps:100});
 assert.deepEqual(r.stress.map(x=>x.positiveAfterAssumedCosts),[true,true,false]);
 assert.equal(r.status,'RESEARCH_EDGE_FALSIFIED_BY_ASSUMED_FRICTION_NO_TRADE');
 assert.equal(r.canRecommendEntry,false);
});
test('clearing every hypothetical stress is still NOT a trading instruction',()=>{
 const r=screenCostedHypothesis({...assumption,expectedGrossMoveBps:200});
 assert.equal(r.status,'RESEARCH_CLEARS_3X_ASSUMED_FRICTION_ONLY_NO_TRADE');
 assert.ok(r.stress.every(x=>x.positiveAfterAssumedCosts));
 assert.equal(r.liveTradingAuthorized,false);
 assert.equal(r.canRecommendEntry,false);
 assert.equal(r.brokerEndpointsPresent,false);
 assert.equal(r.guaranteedReturn,false);
 assert.equal(r.forecastReliabilityCertified,false);
});
test('boundary exactly equal to costs never passes',()=>{
 const r=screenCostedHypothesis({...assumption,expectedGrossMoveBps:44});
 assert.equal(r.stress[0].positiveAfterAssumedCosts,false);
});
test('without independently verified fee schedule, positive research estimate cannot be promoted',()=>{
 const r=screenCostedHypothesis({...assumption,
   expectedGrossMoveBps:200,brokerRatesIndependentlyVerified:false});
 assert.equal(r.status,'RESEARCH_PROVENANCE_OR_FEES_UNVERIFIED_NO_TRADE');
 assert.equal(r.realOrdersSent,0);
});
test('unfrozen/reused development test data never becomes independent evidence',()=>{
 const r=screenCostedHypothesis({...assumption,
   expectedGrossMoveBps:200,parametersFrozenBeforeNewData:false,
   independentlyEvaluatedGrossForecast:false});
 assert.equal(r.status,'RESEARCH_PROVENANCE_OR_FEES_UNVERIFIED_NO_TRADE');
});
test('nonfinite, negative costs, impossible notional or inputs fail closed',()=>{
 for(const v of [
   {entryNotionalRupees:0},
   {entryNotionalRupees:Infinity},
   {slippageBpsPerSide:-1},
   {roundTripSpreadBps:NaN},
   {uncertaintyReserveBps:-.001},
   {roundTripBrokerTaxesRupees:-.01},
   {expectedGrossMoveBps:12000},
   {brokerRatesIndependentlyVerified:'true'}
 ]) {
   const r=screenCostedHypothesis({...assumption,...v});
   assert.equal(r.status,'INVALID_OR_INCOMPLETE_ASSUMPTIONS_NO_TRADE');
   assert.equal(r.liveTradingAuthorized,false);
 }
});
test('actual 84-day aggregate FAST arithmetic deficit is ₹6.958111/trip (rounded)',()=>{
 const r=describeObservedBreakEvenGap({
   policy:'FAST',roundTrips:503,aggregateModeledNetRupees:-3499.93,
   candidateCompleteStockDays:84
 });
 assert.equal(r.additionalGrossRupeesPerRoundTripForArithmeticBreakEven,6.958111);
 assert.equal(r.canUseToSelectParametersOnSameDates,false);
 assert.equal(r.singleCompoundedAccountDemonstrated,false);
});
test('actual 84-day aggregate ONE and TIME_GATE are also negative; abstention remains zero',()=>{
 const one=describeObservedBreakEvenGap({
   policy:'ONE',roundTrips:84,aggregateModeledNetRupees:-573.82,
   candidateCompleteStockDays:84
 });
 const gated=describeObservedBreakEvenGap({
   policy:'TIME_MOMENTUM_GATE',roundTrips:3,
   aggregateModeledNetRupees:-25.61,candidateCompleteStockDays:84
 });
 const abstain=describeObservedBreakEvenGap({
   policy:'NO_TRADE',roundTrips:0,aggregateModeledNetRupees:0,
   candidateCompleteStockDays:84
 });
 assert.equal(one.additionalGrossRupeesPerRoundTripForArithmeticBreakEven,6.83119);
 assert.equal(gated.additionalGrossRupeesPerRoundTripForArithmeticBreakEven,8.536667);
 assert.equal(abstain.additionalGrossRupeesPerRoundTripForArithmeticBreakEven,null);
 assert.equal(abstain.realOrdersSent,0);
});
test('malformed aggregate, impossible P&L without trades are rejected',()=>{
 for(const a of [
   {policy:'INVALID!!',roundTrips:3,candidateCompleteStockDays:84,aggregateModeledNetRupees:-1},
   {policy:'ONE',roundTrips:3,candidateCompleteStockDays:0,aggregateModeledNetRupees:-1},
   {policy:'NO_TRADE',roundTrips:0,candidateCompleteStockDays:84,aggregateModeledNetRupees:-1}
 ]){
   const r=describeObservedBreakEvenGap(a);
   assert.equal(r.status,'INVALID_OR_INCOMPLETE_ASSUMPTIONS_NO_TRADE');
 }
});
