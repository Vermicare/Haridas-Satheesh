// Fictional-only statistical contract verification; not a market backtest or authorization.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const config = JSON.parse(readFileSync(new URL('./intraday_candidate_registration_20261116.json', import.meta.url)));
const spec = config.validation.statisticalDecisionContract;
const fail = reason => ({decision:'HALT_UNKNOWN',reason,accepted:false});
const finite = x => typeof x === 'number' && Number.isFinite(x);
const percentile = (sorted,p) => sorted[Math.max(0,Math.min(sorted.length-1,Math.ceil(p*sorted.length)-1))];
function evaluateFictionalDailyNet(rows, {testOnlyFrozen=false}={}) {
  if (!testOnlyFrozen || spec.status !== 'PROPOSED_NOT_FROZEN') return fail('STATISTICAL_PROTOCOL_NOT_FROZEN');
  if (!Array.isArray(rows) || rows.length < config.validation.minUntouchedUniqueTradingDays) return fail('INSUFFICIENT_DAYS');
  const names=[...spec.candidateIds,...spec.comparators];
  const dates=new Set();
  let previousDate=null;
  for(const row of rows) {
    if(!row || typeof row.date !== 'string' || dates.has(row.date)) return fail('MISSING_OR_DUPLICATE_DATE');
    // Block resampling assumes input is in chronological order; do not silently sort outcomes.
    if(previousDate !== null && row.date <= previousDate) return fail('NONCHRONOLOGICAL_DAYS');
    previousDate=row.date;
    dates.add(row.date);
    if(row.complete !== true || row.fillsKnown !== true || row.rightsVerified !== true) return fail('UNKNOWN_DAY_FILL_OR_RIGHTS');
    if(names.some(n=>!finite(row[n]))) return fail('MISSING_NONFINITE_NET_INR');
    // Fictional fixture only: require independently supplied 1x/2x/3x net outcomes;
    // never infer stressed costs from a 1x P&L or treat this as fee certification.
    if(!Array.isArray(row.costStress) || row.costStress.length !== 3 ||
       row.costStress.some((scenario,i)=>scenario?.multiplier !== [1,2,3][i] ||
         names.some(name=>!finite(scenario[name])))) return fail('MISSING_COST_STRESS_SCENARIOS');
    if(row.costStress.some(scenario=>spec.candidateIds.some(c=>spec.comparators.some(k=>scenario[c]-scenario[k]<=0)))) return fail('NONPOSITIVE_STRESSED_PAIRED_NET');
  }
  if(spec.familyHypotheses !== spec.candidateIds.length*spec.comparators.length) return fail('FAMILY_SIZE_MISMATCH');
  if(spec.bootstrapReplicates !== 10000 || spec.blockLengthExchangeDays !== 5) return fail('UNREVIEWED_BOOTSTRAP_PARAMETERS');
  // Same sampled chronological exchange-day indices for all six paired hypotheses.
  // 32-bit deterministic PRNG; this is a proposed algorithm, not frozen inference.
  let state=spec.seedInteger>>>0;
  const next=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state/4294967296;};
  const n=rows.length, b=spec.blockLengthExchangeDays;
  const pairs=spec.candidateIds.flatMap(c=>spec.comparators.map(k=>({c,k,key:c+'__'+k})));
  const samples=Object.fromEntries(pairs.map(p=>[p.key,[]]));
  for(let rep=0;rep<spec.bootstrapReplicates;rep++){
    const sums=Object.fromEntries(pairs.map(p=>[p.key,0]));
    let count=0;
    while(count<n){
      const start=Math.floor(next()*n);
      for(let j=0;j<b && count<n;j++,count++){
        const row=rows[(start+j)%n];
        for(const p of pairs) sums[p.key]+=row[p.c]-row[p.k];
      }
    }
    for(const p of pairs) samples[p.key].push(sums[p.key]/n);
  }
  const lower={};
  for(const p of pairs) {
    samples[p.key].sort((a,b)=>a-b);
    lower[p.key]=percentile(samples[p.key],spec.lowerBoundPercentile/100);
  }
  const allPositive=Object.values(lower).every(x=>x>0);
  return {decision:allPositive?'FICTIONAL_STATISTICAL_GATE_PASS_ONLY':'REJECT_STATISTICAL_GATE',accepted:false,allPositive,lower};
}
const fictional=(fn,n=60)=>Array.from({length:n},(_,i)=>({date:'FICT-'+String(i).padStart(3,'0'),complete:true,fillsKnown:true,rightsVerified:true,NO_TRADE:0,PASSIVE_INTRADAY_SAME_BUDGET:0,EXISTING_SIMPLE_BREAKOUT:0,M:fn(i),R:fn(i),costStress:[1,2,3].map(multiplier=>({multiplier,NO_TRADE:0,PASSIVE_INTRADAY_SAME_BUDGET:0,EXISTING_SIMPLE_BREAKOUT:0,M:fn(i),R:fn(i)}))}));
test('current proposed contract cannot certify real eligibility',()=>{
 assert.equal(evaluateFictionalDailyNet(fictional(()=>100)).reason,'STATISTICAL_PROTOCOL_NOT_FROZEN');
});
test('zero-trade days remain zero, no positive statistical edge',()=>{
 const r=evaluateFictionalDailyNet(fictional(()=>0),{testOnlyFrozen:true});
 assert.equal(r.decision,'REJECT_STATISTICAL_GATE');
 assert.equal(Object.values(r.lower).every(x=>x===0),true);
});
test('fictional strictly positive daily paired margins exercise arithmetic only',()=>{
 const r=evaluateFictionalDailyNet(fictional(()=>10),{testOnlyFrozen:true});
 assert.equal(r.allPositive,true);
 assert.equal(r.accepted,false);
 assert.equal(Object.values(r.lower).every(x=>Math.abs(x-10)<1e-9),true);
});
test('fictional negative net results reject',()=>{
 assert.equal(evaluateFictionalDailyNet(fictional(()=>-1),{testOnlyFrozen:true}).allPositive,false);
});
test('unknown fills cannot be imputed as zero',()=>{
 const rows=fictional(()=>10);rows[1].fillsKnown=false;
 assert.equal(evaluateFictionalDailyNet(rows,{testOnlyFrozen:true}).reason,'UNKNOWN_DAY_FILL_OR_RIGHTS');
});
test('missing and nonfinite candidate outcome reject',()=>{
 const rows=fictional(()=>10);delete rows[4].M;
 assert.equal(evaluateFictionalDailyNet(rows,{testOnlyFrozen:true}).reason,'MISSING_NONFINITE_NET_INR');
});
test('duplicate day and short holdout reject',()=>{
 const rows=fictional(()=>10);rows[1].date=rows[0].date;
 assert.equal(evaluateFictionalDailyNet(rows,{testOnlyFrozen:true}).reason,'MISSING_OR_DUPLICATE_DATE');
 assert.equal(evaluateFictionalDailyNet(fictional(()=>10,59),{testOnlyFrozen:true}).reason,'INSUFFICIENT_DAYS');
});
test('no real order route and virtual capital only',()=>{
 assert.equal(config.constraints.defaultDecision,'NO_TRADE');
 assert.equal(config.constraints.brokers,'NO_BROKER_ORDER_ROUTE');
 assert.equal(config.capital.virtualInr,10000);
});

test('out-of-order fictional days cannot silently enter a chronological block bootstrap',()=>{
 const rows=fictional(i=>i);
 [rows[2],rows[3]]=[rows[3],rows[2]];
 assert.equal(evaluateFictionalDailyNet(rows,{testOnlyFrozen:true}).reason,'NONCHRONOLOGICAL_DAYS');
});

test('fictional missing cost stress fails closed even when base margins are positive',()=>{
 const rows=fictional(()=>10);delete rows[0].costStress;
 assert.equal(evaluateFictionalDailyNet(rows,{testOnlyFrozen:true}).reason,'MISSING_COST_STRESS_SCENARIOS');
});
test('fictional positive 1x but losing 3x stress fails closed',()=>{
 const rows=fictional(()=>10);for(const row of rows){row.costStress[2].M=-1;row.costStress[2].R=-1;}
 assert.equal(evaluateFictionalDailyNet(rows,{testOnlyFrozen:true}).reason,'NONPOSITIVE_STRESSED_PAIRED_NET');
});
