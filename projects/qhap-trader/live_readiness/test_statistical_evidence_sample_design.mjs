import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {wilsonLower95 as wilson, minimumHypotheticalWins as minimum,
  designPrecommittedEvidenceSample as design,FROZEN_SAMPLE_SIZES as sizes}
  from './statistical_evidence_sample_design.mjs';
import {assessPrecommittedSyntheticPayoffViability as payoff}
  from './precommitted_payoff_viability.mjs';

const out=()=>design();
const one=(bps,gap)=>out().cases.find(x=>
  x.extraAdversityBpsEachSide===bps&&
  x.assumed200BpsGapAmongLosingTradesPercent===gap);
const at=(bps,gap,n)=>one(bps,gap).samples.find(x=>x.imaginaryIndependentTrades===n);

test('Wilson 95 percent checks independently calculated hourly research examples',()=>{
  assert.ok(Math.abs(wilson(42,60)*100-57.491292053085516)<1e-10);
  assert.ok(Math.abs(wilson(48,60)*100-68.2181941943721)<1e-10);
  assert.ok(Math.abs(wilson(175,250)*100-64.05184593182177)<1e-10);
});
test('empty wins give lower Wilson bound zero, all wins do not certify 100 percent',()=>{
  for(const n of sizes){
    assert.equal(wilson(0,n),0);
    assert.ok(wilson(n,n)<1);
    assert.ok(wilson(n,n)>0);
  }
});
test('bad sample counts cannot silently be rounded or truncated',()=>{
  for(const [k,n] of [[-1,60],[61,60],[10.5,60],[1,0],
    [1,10001],[2,1],[NaN,60],[Infinity,60],[5,'60']]){
    assert.throws(()=>wilson(k,n),/INVALID_IID_BINOMIAL_COUNTS/);
  }
});
test('hypothetical required-win search rejects bad break-even thresholds',()=>{
  for(const t of [-.1,1,1.01,NaN,Infinity,undefined,'0.5'])
    assert.throws(()=>minimum(60,t),/INVALID_HYPOTHETICAL_SAMPLE_PLAN/);
  for(const n of [-1,0,30.5,10001])
    assert.throws(()=>minimum(n,.5),/INVALID_HYPOTHETICAL_SAMPLE_PLAN/);
});
test('fixed scenario grid uses all four adverse slippage and two gaps',()=>{
  const r=out();
  assert.equal(r.status,'RESEARCH_SAMPLE_REQUIREMENTS_ONLY');
  assert.deepEqual(r.predeclaredImaginaryTradeCountGrid,[30,60,100,250,500]);
  assert.equal(r.cases.length,8);
  assert.equal(r.cases.reduce((x,c)=>x+c.samples.length,0),40);
  assert.equal(r.nominalWilsonCoveragePercent,95);
});
test('break-even thresholds are imported, never independently retuned',()=>{
  const src=payoff();
  for(const c of src.cases){
    assert.equal(one(c.extraAdversityBpsEachSide,
      c.assumed200BpsGapAmongLosingTradesPercent)
      .theoreticalBreakEvenHitRatePercent,
      c.theoreticalBreakEvenWinRatePercent);
  }
});
test('60 hypothetical trades require 46 of 60 wins at 15bps/no gaps',()=>{
  const r=at(15,0,60);
  assert.equal(r.requiredImaginaryTargetWins,46);
  assert.equal(r.minimumImaginaryTargetHitRatePercent,76.67);
});
test('60 hypothetical trades require 47 wins at 15bps/assumed tail gaps',()=>{
  assert.equal(at(15,5,60).requiredImaginaryTargetWins,47);
});
test('at extreme friction 60 imaginary trades need 60 of 60 wins',()=>{
  for(const gap of [0,5])
    assert.equal(at(50,gap,60).requiredImaginaryTargetWins,60);
});
test('30 independent observations cannot meet 50bps threshold even if all win',()=>{
  for(const gap of [0,5]){
    const r=at(50,gap,30);
    assert.equal(r.requiredImaginaryTargetWins,null);
    assert.equal(r.minimumImaginaryTargetHitRatePercent,null);
    assert.ok(r.allWinsWilsonLowerPercent<r.theoreticalBreakEvenHitRatePercent||
      r.allWinsWilsonLowerPercent<93);
  }
});
test('250 hypothetical observations still require 175 wins at 15bps',()=>{
  assert.equal(at(15,0,250).requiredImaginaryTargetWins,175);
  assert.equal(at(15,5,250).requiredImaginaryTargetWins,179);
});
test('250 observations at 50bps need 239 or 240 target outcomes',()=>{
  assert.equal(at(50,0,250).requiredImaginaryTargetWins,239);
  assert.equal(at(50,5,250).requiredImaginaryTargetWins,240);
});
test('reported minimum wins are strictly above assumed break-even',()=>{
  const r=out();
  for(const c of r.cases){
    for(const s of c.samples){
      const n=s.imaginaryIndependentTrades,k=s.requiredImaginaryTargetWins;
      const thresh=c.theoreticalBreakEvenHitRatePercent/100;
      if(k===null){
        assert.ok(wilson(n,n)<=thresh);
      }else{
        assert.ok(wilson(k,n)>thresh);
        if(k>0)assert.ok(wilson(k-1,n)<=thresh);
      }
    }
  }
});
test('more adverse friction cannot reduce required target-win count',()=>{
  for(const gap of [0,5]){
    for(const n of sizes){
      const counts=[0,5,15,50].map(bps=>at(bps,gap,n).requiredImaginaryTargetWins);
      for(let i=1;i<counts.length;i++){
        const prev=counts[i-1]===null?Infinity:counts[i-1];
        const cur=counts[i]===null?Infinity:counts[i];
        assert.ok(cur>=prev,JSON.stringify({gap,n,counts}));
      }
    }
  }
});
test('assumed extra tail gaps cannot reduce required target-win count',()=>{
  for(const bps of [0,5,15,50]){
    for(const n of sizes){
      const a=at(bps,0,n).requiredImaginaryTargetWins;
      const b=at(bps,5,n).requiredImaginaryTargetWins;
      assert.ok((b===null?Infinity:b)>=(a===null?Infinity:a));
    }
  }
});
test('repeated complete output is deterministic',()=>{
  assert.deepEqual(out(),out());
  assert.deepEqual([...sizes],[30,60,100,250,500]);
});
test('a 95 percent per-trade Wilson bound cannot independently certify market source',()=>{
  const r=out();
  assert.equal(r.anyActualTradeObservationsUsed,false);
  assert.equal(r.realMarketDataUsed,false);
  assert.equal(r.genuineIndependentDaysVerified,0);
  assert.equal(r.independentlyVerifiedForwardSessions,0);
  assert.equal(r.independenceAndStationarityVerified,false);
});
test('no manufactured edge from a mathematical passing hypothetical count',()=>{
  const r=out();
  assert.equal(r.strategyPositiveEdgeIndependentlyVerified,false);
  assert.equal(r.strategyReturnDistributionVerified,false);
  assert.equal(r.marketDataEntitlementVerified,false);
  assert.equal(r.noTradeComparatorRupees,0);
  assert.equal(r.recommendedAction,'NO_TRADE');
});
test('completed hypothetical trade count never substitutes for 60 real sessions',()=>{
  const r=out();
  assert.equal(r.minimumForwardSessionProtocolCount,60);
  assert.equal(r.forwardSessionCountIsNotIndependentTradeCount,true);
  assert.equal(r.independentlyVerifiedForwardSessions,0);
});
test('no credential path, network import, trader execution method, licensed bars',()=>{
  const src=fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),
    'statistical_evidence_sample_design.mjs'),'utf8');
  for(const forbidden of [
    /from ['"]node:https?['"]/,/from ['"]https?['"]/,
    /\bfetch\s*\(/,/\bplaceOrder\s*\(/,
    /\bsubmitOrder\s*\(/,/\bACCESS_TOKEN\b/
  ])assert.equal(forbidden.test(src),false,String(forbidden));
  assert.equal(out().canTrade,false);
  assert.equal(out().realOrderRoutePresent,false);
  assert.equal(out().realOrdersSent,0);
});
