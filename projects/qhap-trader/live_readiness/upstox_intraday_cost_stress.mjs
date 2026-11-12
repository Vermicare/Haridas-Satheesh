/**
 * QHAP-TRADER paper-only 2026 Upstox NSE cash-intraday cost sensitivity.
 * This is a strict, illustrative estimate, not an exchange invoice, tax advice,
 * broker acknowledgement, fill model, live capability, or proof of edge.
 * Source reviewed 2026-11-12: https://upstox.com/brokerage-charges/
 * Broker-specific/account-specific taxes, rate changes, per-fill brokerage,
 * product eligibility, IPFT treatment and rounding require verification.
 * Historical 2021 replays must NOT present 2026 costs as historical charges.
 */
const safePaise=n=>typeof n==='number'&&Number.isFinite(n)&&n>0&&
  Number.isSafeInteger(Math.round(n*100))&&Math.abs(n*100-Math.round(n*100))<1e-6;
const safeInt=n=>Number.isSafeInteger(n)&&n>0&&n<=100000;
const bps=n=>Number.isSafeInteger(n)&&n>=0&&n<=10000;
const money=p=>Math.round(p)/100;
const RISK_CAP_PAISE=250000; // ₹2500 maximum original paper notional
const MAX_CANDIDATE_LOSS_PAISE=5000;
const ceilRate=(minor,num,den)=>Math.ceil(minor*num/den-1e-10);
const result=(status,reasons,extra={})=>Object.freeze({
  status,reasons:[...new Set(reasons)].sort(),simulationOnly:true,
  pricingModel:'UPSTOX_2026_INDICATIVE_CONSERVATIVE_NOT_CONTRACT_NOTE',
  capitalRupees:10000,noTradeNetRupees:0,
  canTrade:false,brokerReconciled:false,realOrderRoutePresent:false,
  liveTradingAuthorized:false,realOrdersSent:0,
  independentlyVerifiedEdge:false,...extra
});
/**
 * Exact accepted keys prevent accidental live response/credential ingestion.
 * Prices here are hypothetical executed prices (not a claim that a limit order
 * would receive a worse-than-limit fill). Additional slippage and stop-gap are
 * explicitly non-executable economic *penalties*, not broker fill predictions.
 */
export function estimateSyntheticIntradayRoundTrip(trade,shock={}) {
  const req=['entryPriceRupees','exitPriceRupees','quantity','exitReason'];
  if(!trade||typeof trade!=='object'||Array.isArray(trade)||
    Object.keys(trade).length!==req.length||
    Object.keys(trade).some(k=>!req.includes(k))||
    !safePaise(trade.entryPriceRupees)||!safePaise(trade.exitPriceRupees)||
    !safeInt(trade.quantity)||!['TIME','STOP','TARGET'].includes(trade.exitReason))
    return result('HALT_INVALID_INPUT',['INVALID_OR_UNCLOSED_SYNTHETIC_TRADE']);
  const valid=['extraBuySlipBps','extraSellSlipBps','stopGapBps'];
  if(!shock||typeof shock!=='object'||Array.isArray(shock)||
    Object.keys(shock).some(k=>!valid.includes(k))||
    valid.some(k=>Object.hasOwn(shock,k)&&!bps(shock[k]))||
    ((shock.stopGapBps??0)>0&&trade.exitReason!=='STOP'))
    return result('HALT_INVALID_INPUT',['INVALID_OR_INAPPLICABLE_SHOCK']);
  const buy= Math.round(trade.entryPriceRupees*100)*trade.quantity;
  const sell=Math.round(trade.exitPriceRupees*100)*trade.quantity;
  if(!Number.isSafeInteger(buy)||!Number.isSafeInteger(sell)||
    buy>RISK_CAP_PAISE||buy<=0)
    return result('HALT_LIMIT_BREACH',['POSITION_EXCEEDS_2500_RUPEES_OR_OVERFLOW']);
  const turnover=buy+sell;
  const brokerBuy=Math.min(2000,ceilRate(buy,10,10000)); // 0.1%, max ₹20
  const brokerSell=Math.min(2000,ceilRate(sell,10,10000));
  const exchange=ceilRate(turnover,307,10000000); // NSE: 0.00307%
  const sebi=ceilRate(turnover,1,1000000); // ₹10 / crore
  // Conservative IPFT buffer used because published Upstox presentations
  // differ on its integration into exchange transaction charges.
  const ipftBuffer=ceilRate(turnover,1,1000000); // ₹0.10 / lakh, may double count
  const gst=ceilRate(brokerBuy+brokerSell+exchange+sebi+ipftBuffer,18,100);
  const stamp=ceilRate(buy,3,100000); // 0.003% buy
  const stt=Math.ceil(ceilRate(sell,25,100000)/100)*100; // round up to rupee
  const charges=brokerBuy+brokerSell+exchange+sebi+ipftBuffer+gst+stamp+stt;
  const slippage=ceilRate(buy,shock.extraBuySlipBps??0,10000)+
    ceilRate(sell,shock.extraSellSlipBps??0,10000);
  const stopGap=trade.exitReason==='STOP'?
    ceilRate(sell,shock.stopGapBps??0,10000):0;
  const gross=sell-buy;
  const net=gross-charges-slippage-stopGap;
  if(![turnover,charges,slippage,stopGap,gross,net].every(Number.isSafeInteger))
    return result('HALT_ARITHMETIC',['UNSAFE_MONETARY_ARITHMETIC']);
  const netRupees=money(net);
  const reasons=['NOT_ACTUAL_UPSTOX_CONTRACT_NOTE','NO_INDEPENDENT_MARKET_DATA_OR_FILL_CERTIFICATION'];
  if(net<=0)reasons.push('NO_POSITIVE_NET_ADVANTAGE_OVER_NO_TRADE');
  if(net < -MAX_CANDIDATE_LOSS_PAISE) reasons.push('EXCEEDS_50_RUPEE_HYPOTHETICAL_LOSS_BUDGET');
  return result('SYNTHETIC_COST_ESTIMATE_ONLY',reasons,{
    quantity:trade.quantity,entryNotionalRupees:money(buy),
    exitNotionalRupees:money(sell),grossRupees:money(gross),
    estimatedChargesRupees:money(charges),
    adverseSlippagePenaltyRupees:money(slippage),
    stopGapPenaltyRupees:money(stopGap),netRupees,
    betterThanNoTradeUnderAssumptions:net>0,
    hypotheticalCandidateLossBudgetExceeded:net < -MAX_CANDIDATE_LOSS_PAISE,
    feeComponentsRupees:Object.freeze({
      brokerage:money(brokerBuy+brokerSell),exchange:money(exchange),
      sebi:money(sebi),ipftConservativeBuffer:money(ipftBuffer),
      gst:money(gst),stamp:money(stamp),stt:money(stt)
    }),
    chargeRounding:'CONSERVATIVELY_UP_TO_PAISE_EACH_COMPONENT_STT_TO_RUPEE',
    pricingNeedsContractNoteReconciliation:true
  });
}
const SHOCKS=Object.freeze([
  ['REFERENCE_ONLY',{}],
  ['ADVERSE_5_BPS_EACH_SIDE',{extraBuySlipBps:5,extraSellSlipBps:5}],
  ['ADVERSE_15_BPS_EACH_SIDE',{extraBuySlipBps:15,extraSellSlipBps:15}],
  ['ADVERSE_50_BPS_EACH_SIDE',{extraBuySlipBps:50,extraSellSlipBps:50}]
]);
/** No search or optimization: fixed, disclosed stress presets. */
export function auditSyntheticCostSensitivity(trade) {
  const variants=SHOCKS.map(([label,shock])=>({scenario:label,
    ...estimateSyntheticIntradayRoundTrip(trade,shock)}));
  if(trade?.exitReason==='STOP') variants.push({
    scenario:'ADVERSE_15_BPS_PLUS_200_BPS_STOP_GAP',
    ...estimateSyntheticIntradayRoundTrip(trade,{
      extraBuySlipBps:15,extraSellSlipBps:15,stopGapBps:200
    })
  });
  if(variants.some(x=>x.status!=='SYNTHETIC_COST_ESTIMATE_ONLY'))
    return result('HALT_INCOMPLETE_COST_SENSITIVITY',
      ['UNRELIABLE_SYNTHETIC_INPUT_OR_RISK_LIMIT']);
  const values=variants.map(x=>x.netRupees);
  return result('SYNTHETIC_NO_TRADE_REMAINS_REQUIRED',
    ['REFERENCE_AND_STRESS_RESULTS_ARE_NOT_FORWARD_EVIDENCE'],{
      scenarios:variants,worstNetRupees:Math.min(...values),
      bestNetRupees:Math.max(...values),
      allScenariosBetterThanNoTrade:values.every(v=>v>0),
      worstHypotheticalLossBudgetExceeded:values.some(v=>v< -50),
      recommendedLiveAction:'NO_TRADE'
    });
}
