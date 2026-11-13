#!/usr/bin/env node
/**
 * QHAP NSE EQUITY — Claude-style INTERDEPENDENT research roles.
 * Low-turnover swing-research architecture, NOT an autonomous trader.
 *
 * No crypto venues, wallet, real/paper broker orders, API credentials,
 * network requests, paid LLMs, or automatic strategy promotion.
 * This is a deterministic role/message graph with an immutable final
 * no-order risk veto. Real Claude/GPT agents stay in the isolated,
 * separately cost-approved research council sidecar.
 */
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const INSTRUMENT=/^NSE_EQ\|[A-Z0-9]{12}$/;
const SYMBOL=/^[A-Z][A-Z0-9&_-]{0,20}$/;
const BASE=Object.freeze({
  project:'QHAP-TRADER',
  market:'NSE_CASH_EQUITY_ONLY',
  analysis:'MULTI_AGENT_SWING_RESEARCH_NOT_TRADING',
  finalDecision:'NO_TRADE',
  realOrdersSent:0,paperOrdersSent:0,
  brokerOrderRoutePresent:false,
  cryptoMarketUsed:false,
  accountCredentialsRead:false,
  networkRequestsMade:0,modelApiCallsMade:0,
  canTradeRealMoney:false,
  profitableEdgeDemonstrated:false
});
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const fixed=x=>Math.round(x*10000)/10000;
const digest=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const isoDay=x=>typeof x==='string'&&/^(20\d\d)-(\d\d)-(\d\d)$/.test(x)&&
  !Number.isNaN(Date.parse(x+'T00:00:00Z'))&&
  new Date(x+'T00:00:00Z').toISOString().slice(0,10)===x;
const dayMs=x=>Date.parse(x+'T00:00:00Z');
const hasExactKeys=(x,keys)=>x&&typeof x==='object'&&!Array.isArray(x)&&
  Object.keys(x).sort().join('|')===keys.slice().sort().join('|');
const STOP_ERRORS=new Set(['INVALID_EQUITY_RESEARCH_SCOPE','INVALID_DAILY_HISTORY',
  'LOOKAHEAD_DAILY_BAR','STALE_DAILY_REPLAY_CLOCK','INVALID_COST_RESEARCH_INPUT']);
function stop(reason){
  return {...BASE,status:'EQUITY_RESEARCH_HALT_NO_TRADE',reason,
    researchWatch:false,agentMessages:[],sourceAudited:false};
}
export function validateEquityReplay(data){
  if(!data||!INSTRUMENT.test(data.instrumentKey||'')||
    !SYMBOL.test(data.symbol||'')||
    !['SYNTHETIC','PRIVATE_REPLAY'].includes(data.sourceClass)||
    !isoDay(data.asOfDate)||!Array.isArray(data.dailyBars)||
    data.dailyBars.length<80||data.dailyBars.length>260)
    throw Error('INVALID_EQUITY_RESEARCH_SCOPE');
  const cost=data.costAssumptions;
  if(!hasExactKeys(cost,['estimatedBrokerageAndTaxesRoundTripRupees',
    'slippageBpsPerSide','spreadRoundTripBps',
    'uncertaintyReserveBps','sourceScheduleIndependentlyVerified'])||
    ![cost.estimatedBrokerageAndTaxesRoundTripRupees,
      cost.slippageBpsPerSide,cost.spreadRoundTripBps,
      cost.uncertaintyReserveBps].every(finite)||
    cost.estimatedBrokerageAndTaxesRoundTripRupees<0||
    cost.estimatedBrokerageAndTaxesRoundTripRupees>1000||
    cost.slippageBpsPerSide<0||cost.slippageBpsPerSide>500||
    cost.spreadRoundTripBps<0||cost.spreadRoundTripBps>500||
    cost.uncertaintyReserveBps<0||cost.uncertaintyReserveBps>500||
    typeof cost.sourceScheduleIndependentlyVerified!=='boolean')
    throw Error('INVALID_COST_RESEARCH_INPUT');
  let last=null;
  for(const c of data.dailyBars){
    if(!hasExactKeys(c,['date','open','high','low','close','volume'])||
      !isoDay(c.date)||!finite(c.open)||!finite(c.high)||
      !finite(c.low)||!finite(c.close)||!finite(c.volume)||
      c.open<=0||c.low<=0||c.close<=0||c.volume<=0||
      c.low>Math.min(c.open,c.close)||
      c.high<Math.max(c.open,c.close)||
      c.low>c.high||c.date>data.asOfDate||
      last!==null&&(c.date<=last||dayMs(c.date)-dayMs(last)>12*86400000))
      throw Error('INVALID_DAILY_HISTORY');
    last=c.date;
  }
  if(last>data.asOfDate)throw Error('LOOKAHEAD_DAILY_BAR');
  if(dayMs(data.asOfDate)-dayMs(last)>7*86400000)
    throw Error('STALE_DAILY_REPLAY_CLOCK');
  return data;
}
function sourceAgent(data){
  return {name:'PROVENANCE_AND_TIME',
    vote:'LOCAL_DATE_ORDER_CHECKED_UNVERIFIED_EXCHANGE',
    family:'POINT_IN_TIME_DATA',
    evidence:{sourceClass:data.sourceClass,observedDailyBars:data.dailyBars.length,
      exchangeCalendarIndependentlyVerified:false,
      corporateActionsIndependentlyVerified:false,
      rawLicensedDataShared:false}};
}
function momentum(data){
  const c=data.dailyBars.map(x=>x.close),last=c.at(-1);
  const sma=n=>c.slice(-n).reduce((sum,x)=>sum+x,0)/n;
  const sma20=sma(20),sma60=sma(60),r20=last/c.at(-21)-1;
  return {name:'TREND_RESEARCHER',family:'SAME_PRICE_HISTORY',
    vote:last>sma60&&sma20>sma60&&r20>0?
      'SUPPORT_WATCH_ONLY':'NO_TREND_CONFIRMATION',
    evidence:{twentyOverSixtyDayMovingAverage:sma20>sma60,
      closesAboveSixtyDayAverage:last>sma60,
      historicalTwentyDayReturnBps:fixed(r20*10000),
      forwardReturnPredictionCertified:false}};
}
function volatility(data){
  const c=data.dailyBars.slice(-21).map(x=>x.close);
  const ret=c.slice(1).map((v,i)=>Math.log(v/c[i]));
  const rms=Math.sqrt(ret.reduce((a,x)=>a+x*x,0)/ret.length);
  const largest=Math.max(...ret.map(x=>Math.abs(x)));
  return {name:'DOWNSIDE_AND_GAP_CHALLENGER',family:'SAME_PRICE_HISTORY',
    vote:rms>0.06||largest>0.16?'VETO_VOLATILITY_AND_GAP':'NO_OBJECTION',
    evidence:{historicalDailyRmsBps:fixed(rms*10000),
      largestObservedDailyAbsMoveBps:fixed(largest*10000),
      overnightGapStillPossible:true}};
}
function liquidity(data){
  const twenty=data.dailyBars.slice(-20),latest=twenty.at(-1);
  const turnover=twenty.reduce((z,x)=>z+x.close*x.volume,0)/20;
  const buyBudget=2500,wholeShares=Math.floor(buyBudget/latest.close);
  const veto=wholeShares<1||turnover<2000000;
  return {name:'LIQUIDITY_AND_CASH_AGENT',family:'SAME_PRICE_HISTORY',
    vote:veto?'VETO_CASH_OR_LIQUIDITY':'NO_OBJECTION',
    evidence:{lastCloseBpsOf2500:fixed(latest.close/buyBudget*10000),
      hypotheticalMaxWholeShares:wholeShares,
      averageHistoricalDailyTurnoverMillions:fixed(turnover/1e6),
      orderBookExecutableLiquidityObserved:false,
      maxHypotheticalPositionRupees:buyBudget}};
}
function independentNews(){
  return {name:'PUBLIC_NEWS_FACT_CHECKER',family:'UNOBSERVED_EXTERNAL_EVIDENCE',
    vote:'NO_VERIFIED_PUBLIC_NEWS_INPUT',
    evidence:{earningsCalendarObserved:false,
      announcementsPointInTimeVerified:false,
      inventsNoHeadlines:true}};
}
function fees(data){
  const x=data.costAssumptions;
  const notional=2500;
  const feesBps=10000*x.estimatedBrokerageAndTaxesRoundTripRupees/notional;
  const friction=feesBps+2*x.slippageBpsPerSide+x.spreadRoundTripBps+
    x.uncertaintyReserveBps;
  return {name:'UPSTOX_CASH_COST_AUDITOR',family:'UNVERIFIED_USER_COST_ASSUMPTION',
    vote:x.sourceScheduleIndependentlyVerified?
      'FEE_INPUT_FLAG_REPORTED_NOT_INDEPENDENTLY_CHECKED':
      'FEE_SCHEDULE_UNVERIFIED',
    evidence:{illustrativeRoundTripCostBps:fixed(friction),
      stressThreeXCostBps:fixed(3*friction),
      feeInputUserFlag:x.sourceScheduleIndependentlyVerified,
      upstoxContractNoteValidatedByCode:false,
      dpDeliverySellChargeMustBeIncluded:true,
      taxAndGapRiskExcludedFromThisFormula:true}};
}
function skeptic(agents){
  const trend=agents.TREND_RESEARCHER;
  const risk=agents.DOWNSIDE_AND_GAP_CHALLENGER;
  const liquidity=agents.LIQUIDITY_AND_CASH_AGENT;
  const concerns=[];
  if(trend.vote!=='SUPPORT_WATCH_ONLY')concerns.push('NO_POSITIVE_TREND_RESEARCH_WATCH');
  if(risk.vote.startsWith('VETO_'))concerns.push('GAP_OR_VOLATILITY_RISK');
  if(liquidity.vote.startsWith('VETO_'))concerns.push('CASH_OR_LIQUIDITY_RESTRICTION');
  concerns.push('ONE_SHARED_PRICE_SOURCE_NOT_INDEPENDENT_AGENT_CORROBORATION');
  return {name:'ADVERSARIAL_SKEPTIC',family:'EVIDENCE_REBUTTAL',
    vote:concerns.some(x=>x!=='ONE_SHARED_PRICE_SOURCE_NOT_INDEPENDENT_AGENT_CORROBORATION')?
      'OPPOSE_WATCH':'NOT_AN_INDEPENDENT_SIGNAL',
    evidence:{objections:concerns,signalFamiliesFromDistinctSourceCount:1,
      economicEdgeFromEnsembleValidated:false}};
}
export async function runEquitySwingAgentNetwork(input){
  let d;
  try{d=validateEquityReplay(input);}
  catch(e){return stop(STOP_ERRORS.has(e?.message)?e.message:'INVALID_EQUITY_RESEARCH_SCOPE');}
  const rows=[],lookup={};
  function put(agent,parents=[]){
    if(!parents.every(x=>rows.some(y=>y.id===x)))
      throw Error('AGENT_DEPENDENCY_MISSING');
    const id='R'+(rows.length+1);
    const core={id,name:agent.name,dependsOn:parents,
      family:agent.family,vote:agent.vote,evidence:agent.evidence};
    const previous=rows.at(-1)?.hash||'GENESIS';
    rows.push({...core,hash:digest({previous,core})});
    lookup[agent.name]={...agent,id};
    return id;
  }
  const provenance=put(sourceAgent(d));
  const modules=await Promise.all([
    Promise.resolve(momentum(d)),Promise.resolve(volatility(d)),
    Promise.resolve(liquidity(d)),Promise.resolve(independentNews()),
    Promise.resolve(fees(d))
  ]);
  for(const x of modules)put(x,[provenance]);
  const by=Object.fromEntries(modules.map(x=>[x.name,x]));
  const contest=skeptic(by);
  const skepticId=put(contest,[lookup.TREND_RESEARCHER.id,
    lookup.DOWNSIDE_AND_GAP_CHALLENGER.id,
    lookup.LIQUIDITY_AND_CASH_AGENT.id,
    lookup.PUBLIC_NEWS_FACT_CHECKER.id]);
  const possible=by.TREND_RESEARCHER.vote==='SUPPORT_WATCH_ONLY'&&
    by.LIQUIDITY_AND_CASH_AGENT.vote==='NO_OBJECTION'&&
    by.DOWNSIDE_AND_GAP_CHALLENGER.vote==='NO_OBJECTION'&&
    contest.vote!=='OPPOSE_WATCH';
  const coordinator=put({
    name:'RESEARCH_COORDINATOR',family:'RESEARCH_ONLY_COMPOSITION',
    vote:possible?'LOW_TURNOVER_SWING_HYPOTHESIS_WATCH':'ABSTAIN',
    evidence:{candidateNotOrder:true,expectedProfitKnown:false,
      actuallyTestedOnUnseenMarketData:false,
      benchmarkNoTradeRequired:true}
  },[skepticId,lookup.UPSTOX_CASH_COST_AUDITOR.id]);
  put({
    name:'NON_OVERRIDABLE_RISK_GUARDIAN',
    family:'DETERMINISTIC_RISK',
    vote:'VETO_ALL_PAPER_AND_REAL_ORDER_ROUTES',
    evidence:{reasons:[
      'NO_PROVEN_INDEPENDENT_AFTER_COST_SWING_EDGE',
      'UPSTOX_DELIVERY_ACTUAL_CHARGES_NOT_CERTIFIED',
      'EQUITY_CORPORATE_ACTION_AND_EXCHANGE_CALENDAR_NOT_VERIFIED',
      'NO_ACTUAL_EXCHANGE_ORDER_BOOK_OR_FINAL_FILLS',
      'NO_LIVE_ORDER_AUTHORIZATION'
    ]}
  },[coordinator,lookup.UPSTOX_CASH_COST_AUDITOR.id,
    lookup.DOWNSIDE_AND_GAP_CHALLENGER.id]);
  return {...BASE,
    status:possible?'EQUITY_SWING_RESEARCH_WATCH_NOT_ORDER':
      'EQUITY_SWING_ABSTAIN_RESEARCH_ONLY',
    instrumentAlias:d.symbol,
    sourceClass:d.sourceClass,
    researchWatch:possible,
    inputBars: d.dailyBars.length,
    assumedCostBps:by.UPSTOX_CASH_COST_AUDITOR.evidence,
    independentSourceFamiliesVerified:false,
    independentOutOfSampleValidationPassed:false,
    sourceAudited:false,
    agentMessages:rows,
    auditChainHash:rows.at(-1).hash
  };
}
export function verifyEquitySwingAgentAudit(x){
  if(!x||!Array.isArray(x.agentMessages)||x.agentMessages.length!==9||
     x.finalDecision!=='NO_TRADE'||x.realOrdersSent!==0||
     x.paperOrdersSent!==0||x.brokerOrderRoutePresent!==false||
     x.canTradeRealMoney!==false)return false;
  let previous='GENESIS',seen=new Set();
  for(let i=0;i<x.agentMessages.length;i++){
    const item=x.agentMessages[i];
    if(!item||item.id!=='R'+(i+1)||!Array.isArray(item.dependsOn)||
      !item.dependsOn.every(p=>seen.has(p)))return false;
    const {hash,...core}=item;
    if(hash!==digest({previous,core}))return false;
    seen.add(item.id);previous=hash;
  }
  const last=x.agentMessages.at(-1);
  return x.auditChainHash===previous&&
    last.name==='NON_OVERRIDABLE_RISK_GUARDIAN'&&
    last.vote==='VETO_ALL_PAPER_AND_REAL_ORDER_ROUTES';
}
export function syntheticEquityFixture(){
  const bars=[],day=new Date('2024-01-01T00:00:00Z');
  let i=0;
  while(bars.length<100){
    const w=day.getUTCDay();
    if(w!==0&&w!==6){
      const close=240*(1+0.0018*i);
      const open=close*0.998;
      bars.push({date:day.toISOString().slice(0,10),
        open,high:close*1.002,low:open*.997,
        close,volume:500000+i*1200});
    }
    day.setUTCDate(day.getUTCDate()+1);
    i++;
  }
  return {instrumentKey:'NSE_EQ|INE002A01018',symbol:'SYNTHETIC',
    sourceClass:'SYNTHETIC',asOfDate:bars.at(-1).date,dailyBars:bars,
    costAssumptions:{
      estimatedBrokerageAndTaxesRoundTripRupees:70,
      slippageBpsPerSide:15,spreadRoundTripBps:8,
      uncertaintyReserveBps:10,
      sourceScheduleIndependentlyVerified:false
    }};
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  try{
    let data;
    if(process.argv.length===3&&process.argv[2]==='--synthetic-demo')
      data=syntheticEquityFixture();
    else if(process.argv.length===4&&process.argv[2]==='--private-replay'&&
      path.isAbsolute(process.argv[3])){
      data=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
      if(data.sourceClass!=='PRIVATE_REPLAY')
        throw Error('ONLY_PRIVATE_REPLAY');
    }else throw Error('INVALID_COMMAND');
    const result=await runEquitySwingAgentNetwork(data);
    console.log(JSON.stringify(result,null,2));
    process.exitCode=0;
  }catch{
    console.error(JSON.stringify(stop('INVALID_LOCAL_REPLAY_OR_ARGUMENTS')));
    process.exitCode=1;
  }
}
