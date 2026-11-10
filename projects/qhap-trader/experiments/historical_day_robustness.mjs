#!/usr/bin/env node
/**
 * QHAP-TRADER: day-block retrospective robustness diagnostics on the EXISTING
 * ACC/RELIANCE Feb 2021 developmental simulation outputs.
 *
 * Sources: CLI result JSON from costed_intraday_pilot.mjs at 5 and 15bps/side.
 * Does not fetch, publish or store raw OHLCV prices or private account data.
 * These are not fresh/unseen data, forward tests, or live trading results.
 * Preserve paired symbol-day resampling and separate ₹10,000 accounts.
 */
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const DAYS=['01','02','03','04','05','08','09','10','11','12','15','16'];
const STRATEGIES=['BASELINE','DTT_VETO'];
const SYMBOLS=['ACC','RELIANCE'];
const EPS=1e-4;
const round=(x,n=6)=>Number(x.toFixed(n));

function requireShape(cond,code){if(!cond)throw Error(code);}
function stableSeed(s){
  let h=2166136261;
  for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}
  return h>>>0 || 1;
}
function rng(seed){
  let x=seed;
  return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)/4294967296;};
}
function quantile(xs,p){
  const a=[...xs].sort((x,y)=>x-y);
  if(!a.length)throw Error('EMPTY_DISTRIBUTION');
  const i=p*(a.length-1),lo=Math.floor(i),hi=Math.ceil(i);
  return a[lo]+(a[hi]-a[lo])*(i-lo);
}
function bootstrapOfDays(xs,seed='fixed',resamples=10000){
  requireShape(Array.isArray(xs)&&xs.length===12&&xs.every(Number.isFinite),
    'TWELVE_DAILY_NUMBERS_REQUIRED');
  requireShape(Number.isSafeInteger(resamples)&&resamples>=1000&&resamples<=100000,
    'INVALID_RESAMPLES');
  const rand=rng(stableSeed(seed)),totals=[];
  for(let i=0;i<resamples;i++){
    let total=0;
    for(let d=0;d<xs.length;d++)total+=xs[Math.floor(rand()*xs.length)];
    totals.push(total);
  }
  const positives=totals.filter(x=>x>0).length;
  return {
    repetitions:resamples,
    interval95ForTwelveSessionSum:[round(quantile(totals,.025)),round(quantile(totals,.975))],
    fractionBootstrapSumsPositive:round(positives/resamples,4),
    notAProbabilityOfFutureProfit:true
  };
}
function checkRun(run,slip){
  requireShape(run&&run.slipBpsPerSide===slip&&Array.isArray(run.output)&&
    run.output.length===2,'INVALID_HISTORICAL_JSON_OR_SLIPPAGE');
  const results=new Map();
  for(const rec of run.output){
    requireShape(SYMBOLS.includes(rec.symbol)&&!results.has(rec.symbol)&&
      rec.validSessions===12&&rec.sourceDays===12&&
      Array.isArray(rec.excluded)&&rec.excluded.length===0&&
      Array.isArray(rec.inputFiles)&&rec.inputFiles.length===12,
      'UNEXPECTED_SYMBOL_OR_INCOMPLETE_SESSIONS');
    requireShape(DAYS.every((day,i)=>rec.inputFiles[i].day===day&&
      /^[a-f0-9]{64}$/.test(rec.inputFiles[i].sha256)),
      'SOURCE_FILE_ORDER_OR_FINGERPRINT_MISSING');
    const ledger={};
    for(const strategy of STRATEGIES){
      const sc=rec.scenarios?.[strategy];
      requireShape(sc&&Array.isArray(sc.ledger)&&sc.ledger.length===12 &&
        Number.isFinite(sc.netPnl)&&Number.isFinite(sc.finalEquity)&&
        Number.isInteger(sc.count)&&sc.count>=0&&sc.count<=12,
        'BAD_STRATEGY_LEDGER');
      const daily=[];
      for(let i=0;i<12;i++){
        const d=sc.ledger[i];
        requireShape(d.day===DAYS[i]&&typeof d.trade==='boolean',
          'DAY_ORDER_MISMATCH');
        requireShape(!d.trade || (Number.isFinite(d.net)&&Number.isFinite(d.gross)&&
          Number.isFinite(d.fees)&&d.fees>=0&&
          Math.abs(d.gross-d.fees-d.net)<EPS),'TRADE_PNL_INCONSISTENT');
        daily.push(d.trade?d.net:0);
      }
      const count=sc.ledger.filter(x=>x.trade).length,net=daily.reduce((a,b)=>a+b,0);
      requireShape(count===sc.count && Math.abs(net-sc.netPnl)<EPS &&
        Math.abs(10000+sc.netPnl-sc.finalEquity)<EPS,
        'SUMMARY_PNL_MISMATCH');
      ledger[strategy]={daily,count,total:round(net),costs:sc.costs};
    }
    results.set(rec.symbol,ledger);
  }
  requireShape(results.size===2,'MISSING_SYMBOL');
  return results;
}
function summary(scenario,seed){
  const xs=scenario.daily,total=xs.reduce((a,b)=>a+b,0);
  const omittedTotals=xs.map(x=>total-x);
  return {
    trades:scenario.count,netPnlInr:round(total),
    netPerSymbolDayInr:round(total/12),
    daysWithPositiveNet:xs.filter(x=>x>0).length,
    dayCount:12,
    leaveOneDayOutRangeInr:[
      round(Math.min(...omittedTotals)),round(Math.max(...omittedTotals))
    ],
    leaveOneDayOutPositiveCount:omittedTotals.filter(x=>x>0).length,
    leaveOneDayOutNegativeCount:omittedTotals.filter(x=>x<0).length,
    bootstrap:bootstrapOfDays(xs,seed),
    baselineNoTradePnlInr:0,
    notes:'Already inspected 2021 development days; includes zero-trade days; no execution realism'
  };
}
export function analyzeHistoricalRuns(low,high){
  const bySlip=new Map([[5,checkRun(low,5)],[15,checkRun(high,15)]]);
  const out={kind:'PAST_DATA_DEVELOPMENT_SAMPLE_ONLY',
    dataset:'Feb 1-16 2021; 12 distinct market days, two independent symbol accounts',
    inputStatus:'24 pinned third-party stock-day blobs; data rights/exchange authenticity NOT independently certified',
    method:'10k fixed-seed day-block bootstrap, paired by trading date, separately per stock and strategy; no parameter optimization',
    assumesTwoIndependentInr10000Accounts:true,
    futurePredictiveEvidence:false,untouchedHoldout:false,
    brokerExecutedTrades:0,marketDataRedistributed:false,
    analyzedSymbols:{}};
  for(const symbol of SYMBOLS){
    const item={scenarios:{},policyComparison:{},frictionSensitivity:{}};
    for(const slip of [5,15]){
      const ledger=bySlip.get(slip).get(symbol);
      item.scenarios[String(slip)]={};
      for(const k of STRATEGIES)
        item.scenarios[String(slip)][k]=summary(ledger[k],symbol+':'+slip+':'+k);
      const difference=ledger.DTT_VETO.daily.map((v,i)=>v-ledger.BASELINE.daily[i]);
      item.policyComparison[String(slip)]={
        label:'DTT_VETO minus BASELINE by matched historical date (different trade timing possible)',
        netDifferenceInr:round(difference.reduce((a,b)=>a+b,0)),
        bootstrap:bootstrapOfDays(difference,symbol+':'+slip+':DIFF'),
        matchingNote:'Matched calendar dates; NOT matched trades or causal effect'
      };
    }
    for(const k of STRATEGIES){
      const prev=bySlip.get(5).get(symbol)[k],next=bySlip.get(15).get(symbol)[k];
      item.frictionSensitivity[k]={
        note:'5bps minus 15bps net: sensitivity to extra 10bps PER SIDE. Paths/sizing may change.',
        low5BpsPnlInr:prev.total,high15BpsPnlInr:next.total,
        higherFrictionDragInr:round(prev.total-next.total),
        highFrictionOutperformsNoTrade:next.total>0
      };
    }
    out.analyzedSymbols[symbol]=item;
  }
  out.conclusion='Retrospective diagnostics only. No genuine untouched holdout or licensed forward market observation; do not optimize on the February 2021 development sample.';
  return out;
}
if(process.argv[1] && import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
  try{
    requireShape(process.argv.length===4,'USAGE: node historical_day_robustness.mjs qhap-5.json qhap-15.json');
    const low=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
    const high=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
    console.log(JSON.stringify(analyzeHistoricalRuns(low,high),null,2));
  }catch(e){console.error('HISTORICAL_DIAGNOSTIC_ERROR:',e.message);process.exitCode=1;}
}
