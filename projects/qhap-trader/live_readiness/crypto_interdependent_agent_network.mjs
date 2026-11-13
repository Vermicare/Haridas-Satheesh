#!/usr/bin/env node
/**
 * QHAP CRYPTO — interdependent research agents, a local deterministic
 * demonstration of an agent decision network. Not LLM inference.
 *
 * Absolutely no external requests, AI model calls, keys, wallets, broker
 * adapters, order submissions, persistence, automatic or paper fills.
 * A positive research watch is NOT a trade recommendation.
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const MARKETS=new Set(['BTC-USDT','ETH-USDT']);
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const round=x=>Math.round(x*1e4)/1e4;
const BASE=Object.freeze({
  project:'QHAP-CRYPTO-RESEARCH',
  marketType:'UNLEVERAGED_SPOT_RESEARCH',
  execution:'DISABLED',
  realOrdersSent:0,paperOrdersSent:0,
  realOrderRoutePresent:false,exchangeCredentialsRead:false,
  apiRequestsMade:0,modelRequestsMade:0,
  claimedProfitableEdge:false,
  autonomousLiveTradingAllowed:false
});
function refuse(reason,agents=[]){
  return {
    ...BASE,status:'NO_TRADE_RESEARCH_HALT',reason,
    watchCandidate:false,agents,independentValidationPassed:false
  };
}
function readSnapshot(x,clockMs){
  if(!x||!MARKETS.has(x.market)||!['SYNTHETIC','PRIVATE_REPLAY'].includes(x.sourceClass)||
     !finite(clockMs)||!Number.isSafeInteger(clockMs)||
     !Array.isArray(x.candles)||x.candles.length<40||x.candles.length>180||
     !x.costAssumptions||typeof x.costAssumptions!=='object')
    throw Error('INVALID_REPLAY_INPUT');
  const a=x.costAssumptions;
  if(![a.feeBpsPerSide,a.slippageBpsPerSide,a.spreadRoundTripBps,a.uncertaintyBps]
       .every(finite)||
     a.feeBpsPerSide<0||a.feeBpsPerSide>200||
     a.slippageBpsPerSide<0||a.slippageBpsPerSide>300||
     a.spreadRoundTripBps<0||a.spreadRoundTripBps>300||
     a.uncertaintyBps<0||a.uncertaintyBps>300||
     a.independentlyVerified!==true&&a.independentlyVerified!==false)
    throw Error('INVALID_COST_ASSUMPTIONS');
  let last=0;
  for(const c of x.candles){
    if(!c||!Number.isSafeInteger(c.closeTimeMs)||c.closeTimeMs<=0||
       ![c.open,c.high,c.low,c.close,c.volume].every(finite)||
       c.low<=0||c.volume<=0||
       c.low>Math.min(c.open,c.close)||c.high<Math.max(c.open,c.close)||
       c.high<c.low||c.close<=0||
       last>0&&c.closeTimeMs-last!==60000)
      throw Error('INVALID_CANDLE_OR_GAP');
    last=c.closeTimeMs;
  }
  if(last>clockMs)throw Error('LOOKAHEAD_CANDLE_NOT_YET_CLOSED');
  if(clockMs-last>120000)throw Error('STALE_CANDLE_FEED');
  const closes=x.candles.map(c=>c.close);
  const volumes=x.candles.map(c=>c.volume);
  return {market:x.market,sourceClass:x.sourceClass,
    timeBoundaryMs:clockMs,closes,volumes,assumptions:a};
}

function trend(m){
  const c=m.closes,n=c.length-1;
  const r5=c[n]/c[n-5]-1,r20=c[n]/c[n-20]-1;
  return {name:'TREND_RESEARCHER',vote:r5>=0.003&&r20>=0.006?
    'SUPPORT_WATCH':'ABSTAIN',family:'PRICE_TREND',
    metadata:{r5Bps:round(r5*10000),r20Bps:round(r20*10000)}};
}
function reversion(m){
  const a=m.closes.slice(-20),mean=a.reduce((z,x)=>z+x,0)/20;
  const sigma=Math.sqrt(a.reduce((z,x)=>z+(x-mean)**2,0)/20);
  const z=sigma>0?(a.at(-1)-mean)/sigma:0;
  return {name:'MEAN_REVERSION_CHALLENGER',vote:z>2?'VETO_OVEREXTENDED':
    'NO_OBJECTION',family:'PRICE_MEAN_REVERSION',
    metadata:{lastPriceDeviationZ:round(z)}};
}
function liquidity(m){
  const v=m.volumes,last=v.at(-1);
  const mean=v.slice(-20).reduce((x,y)=>x+y,0)/20;
  const ratio=last/mean;
  return {name:'LIQUIDITY_PROXY',vote:ratio<0.25||ratio>12?
    'VETO_VOLUME_ANOMALY':'NO_OBJECTION',family:'CANDLE_VOLUME_PROXY',
    metadata:{relativeVolume:round(ratio),orderBookDepthObserved:false}};
}
function volatility(m){
  const c=m.closes.slice(-21);
  const abs=c.slice(1).map((v,i)=>Math.abs(Math.log(v/c[i])));
  const max=Math.max(...abs),rms=Math.sqrt(abs.reduce((z,x)=>z+x*x,0)/abs.length);
  return {name:'VOLATILITY_WATCHDOG',
    vote:max>=0.035||rms>=0.025?'VETO_VOLATILITY':'NO_OBJECTION',
    family:'PRICE_VOLATILITY',
    metadata:{largestBarMoveBps:round(max*10000),
      rmsBarMoveBps:round(rms*10000)}};
}
function costs(m){
  const c=m.assumptions;
  // Two-sided fee/slippage plus already ROUNDTRIP spread and reserve.
  // If measured slippage already includes spread, caller MUST set
  // spreadRoundTripBps=0 to avoid double-counting.
  const roundtrip=2*(c.feeBpsPerSide+c.slippageBpsPerSide)+
    c.spreadRoundTripBps+c.uncertaintyBps;
  return {name:'COST_GATE',family:'BROKER_FRICTION_ASSUMPTION',
    vote:c.independentlyVerified?
      'ASSUMED_COST_REVIEWED':'COST_PROVENANCE_UNVERIFIED',
    metadata:{roundTripBps:round(roundtrip),stress3xBps:round(3*roundtrip),
      ratesIndependentlyVerified:c.independentlyVerified,
      taxModelVerified:false,venueExecutionPricesVerified:false}};
}
function skeptic(nodes){
  const t=nodes.TREND_RESEARCHER,
    r=nodes.MEAN_REVERSION_CHALLENGER,
    l=nodes.LIQUIDITY_PROXY;
  const reasons=[];
  if(t.vote!=='SUPPORT_WATCH')reasons.push('NO_PRECOMMITTED_MOMENTUM_CONFIRMATION');
  if(r.vote!=='NO_OBJECTION')reasons.push('OVEREXTENSION');
  if(l.vote!=='NO_OBJECTION')reasons.push('VOLUME_ANOMALY');
  return {name:'ADVERSARIAL_SKEPTIC',family:'META_CRITIQUE',
    vote:reasons.length?'OPPOSE':'NO_OBJECTION',
    metadata:{objections:reasons,independentPriceSources:1,
      agentVotesDoNotEstablishSignalIndependence:true}};
}

export async function runCryptoAgentNetwork(input,{clockMs}={}){
  let market;
  try{market=readSnapshot(input,clockMs);}
  catch(e){
    const allowed=new Set(['INVALID_REPLAY_INPUT','INVALID_COST_ASSUMPTIONS',
      'INVALID_CANDLE_OR_GAP','LOOKAHEAD_CANDLE_NOT_YET_CLOSED','STALE_CANDLE_FEED']);
    return refuse(allowed.has(e?.message)?e.message:'UNTRUSTED_INPUT');
  }
  const ledger=[];
  const push=(name,dependsOn,packet)=>{
    if(!dependsOn.every(id=>ledger.some(row=>row.id===id)))
      throw Error('MISSING_INTERDEPENDENT_AGENT_INPUT');
    const id='A'+String(ledger.length+1);
    const content={id,name,dependsOn,vote:packet.vote,
      evidenceFamily:packet.family,metadata:packet.metadata||{}};
    const prev=ledger.at(-1)?.digest??'GENESIS';
    const digest=hash({prev,content});
    ledger.push({...content,digest});
    return id;
  };
  const a1=push('SOURCE_INTEGRITY',[],{
    vote:'FRESH_COMPLETE_LOCAL_REPLAY',family:'CANDLE_PROVENANCE',
    metadata:{sourceClass:market.sourceClass,candleCount:market.closes.length,
      market:market.market,sourceEntitlementIndependentlyVerified:false}});
  // Three separately scoped analytic modules: run independently with
  // no inter-agent reply access; only their outputs go to the challenger.
  const parallel=await Promise.all([
    Promise.resolve().then(()=>trend(market)),
    Promise.resolve().then(()=>reversion(market)),
    Promise.resolve().then(()=>liquidity(market)),
    Promise.resolve().then(()=>volatility(market)),
    Promise.resolve().then(()=>costs(market))
  ]);
  const ids={};const by={};
  for(const packet of parallel){
    by[packet.name]=packet;
    ids[packet.name]=push(packet.name,[a1],packet);
  }
  const attack=skeptic(by);
  const skepticId=push(attack.name,[
    ids.TREND_RESEARCHER,ids.MEAN_REVERSION_CHALLENGER,
    ids.LIQUIDITY_PROXY],attack);
  const objection=parallel.some(x=>x.vote.startsWith('VETO_'))||
    attack.vote==='OPPOSE';
  const researchWatch=!objection&&
    by.TREND_RESEARCHER.vote==='SUPPORT_WATCH'&&
    by.COST_GATE.metadata.stress3xBps<=150;
  const coordinatorId=push('RESEARCH_COORDINATOR',[
    skepticId,ids.VOLATILITY_WATCHDOG,ids.COST_GATE],{
    vote:researchWatch?'WATCH_HYPOTHESIS_ONLY':'ABSTAIN',
    family:'META_RESEARCH',
    metadata:{rawModelConsensusNotEvidence:true,independentMarketTestPassed:false,
      noFinancialOrderAuthority:true}});
  // Independent risk guardian is mandatory and NON-LLM, final veto
  // of all proposed activity. Unsupported tax, actual fill, and edge
  // evidence means even a WATCH cannot become an executed paper order.
  const riskReasons=[];
  if(!market.assumptions.independentlyVerified)riskReasons.push('UNVERIFIED_FEES');
  if(!researchWatch)riskReasons.push('NO_STRONG_RESEARCH_WATCH');
  riskReasons.push('NO_INDEPENDENT_AFTER_COST_EDGE');
  riskReasons.push('NO_VERIFIED_EXCHANGE_ORDER_BOOK');
  riskReasons.push('CRYPTO_TAX_ACCOUNTING_NOT_CERTIFIED');
  push('NON_OVERRIDABLE_RISK_GUARDIAN',[
    coordinatorId,ids.VOLATILITY_WATCHDOG,ids.COST_GATE],{
    vote:'VETO_REAL_AND_PAPER_EXECUTION',
    family:'DETERMINISTIC_RISK',
    metadata:{reasons:riskReasons}});
  const output={
    ...BASE,status:researchWatch?'PAPER_RESEARCH_WATCH_ONLY':
      'NO_TRADE_RESEARCH_ABSTAIN',
    instrument:market.market,
    sourceClass:market.sourceClass,
    researchWatch,
    riskVetoes:[...riskReasons],
    forecastIndependentOutOfSample:false,
    marketDataLicenseIndependentlyVerified:false,
    independentlyVerifiedCryptoTaxes:false,
    finalDecision:'NO_TRADE',
    counts:{agents:ledger.length,independentEvidenceSources:1,
      candleBarsValidated:market.closes.length},
    costsBps:by.COST_GATE.metadata,
    agentMessages:ledger,
    auditChainHash:ledger.at(-1).digest
  };
  return output;
}
export function syntheticFixture(){
  const base=Date.parse('2026-11-13T12:00:00.000Z')-59*60000;
  const candles=Array.from({length:60},(_,i)=>{
    const close=60000*(1+0.00035*i),open=close*0.99985;
    return {closeTimeMs:base+i*60000,open,high:close*1.0002,
      low:open*0.9998,close,volume:100+i%5};
  });
  return {market:'BTC-USDT',sourceClass:'SYNTHETIC',candles,
    costAssumptions:{feeBpsPerSide:10,slippageBpsPerSide:10,
      spreadRoundTripBps:6,uncertaintyBps:10,
      independentlyVerified:false}};
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  try{
    const args=process.argv.slice(2);
    let snapshot,clock;
    if(args.length===1&&args[0]==='--synthetic-demo'){
      snapshot=syntheticFixture();clock=snapshot.candles.at(-1).closeTimeMs;
    }else if(args.length===3&&args[0]==='--private-replay'&&
      args[1]==='--file'&&path.isAbsolute(args[2])){
      snapshot=JSON.parse(fs.readFileSync(args[2],'utf8'));
      clock=Number(snapshot.asOfMs);
      if(snapshot.sourceClass!=='PRIVATE_REPLAY')
        throw Error('PRIVATE_REPLAY_SOURCE_CLASS_REQUIRED');
    }else throw Error('INVALID_COMMAND');
    const result=await runCryptoAgentNetwork(snapshot,{clockMs:clock});
    console.log(JSON.stringify(result,null,2));
    process.exitCode=result.status==='NO_TRADE_RESEARCH_HALT'?1:0;
  }catch{
    console.error(JSON.stringify({
      ...BASE,status:'LOCAL_RESEARCH_INPUT_FAILED_NO_TRADE'}));
    process.exitCode=1;
  }
}
