import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {POLICY,REVIEW_ITEMS,assessLiveReadinessInventory,assessPaperEntry} from './readiness_gate.mjs';

const TIMESTAMP='2026-11-13T10:15:00+05:30'; // Synthetic: never certifies venue/session/holiday
const instrument='NSE_EQ|INE848E01016';
const candidate=()=>({
  mode:'PAPER',side:'BUY',product:'CASH_INTRADAY',orderType:'LIMIT',
  instrumentKey:instrument,limitPrice:100,stopPrice:99,quantity:10,tickSize:0.05
});
const account=()=>({
  equityRupees:10000,cashAvailableRupees:10000,grossExposureRupees:0,
  dailyPnlRupees:0,weeklyPnlRupees:0,peakEquityRupees:10000,
  inFlightOrders:0,paperLedgerReconciled:true,sessionEntries:0
});
const feed=()=>({
  dataUsePermitted:true,instrumentTradable:true,instrumentKey:instrument,
  exchangeBookEventAgeMs:100,bookQualityCertified:true,spreadBps:6
});
const system=()=>({
  verifiedRegularSession:true,killSwitchEngaged:false,incidentFree:true,clockSkewMs:10
});
const check=(patch={})=>{
 const c=candidate(),a=account(),f=feed(),s=system();
 Object.assign(c,patch.candidate??{});Object.assign(a,patch.account??{});
 Object.assign(f,patch.feed??{});Object.assign(s,patch.system??{});
 return assessPaperEntry(c,a,f,s,patch.timestamp??TIMESTAMP);
};
const deny=(code,patch)=>{const r=check(patch);assert.equal(r.status,'REJECT');assert.ok(r.reasons.includes(code),JSON.stringify(r));assert.equal(r.realOrderSubmissionPossible,false);};

test('default live readiness denies all real orders',()=>{
 const r=assessLiveReadinessInventory();assert.equal(r.status,'BLOCKED_REQUIREMENTS_INCOMPLETE');
 assert.equal(r.itemsMissing,REVIEW_ITEMS.length);assert.equal(r.realOrderSubmissionPossible,false);
});
test('self-attested green evidence NEVER becomes live-approved',()=>{
 const r=assessLiveReadinessInventory(Object.fromEntries(REVIEW_ITEMS.map(x=>[x,true])));
 assert.equal(r.status,'EXTERNAL_REVIEW_REQUIRED');assert.equal(r.externalSignOffVerifiedBySoftware,false);
 assert.equal(r.liveTradingAuthorized,false);assert.ok(r.reasons.includes('CLAIMS_ARE_NOT_INDEPENDENT_EVIDENCE'));
});
test('anything but literal true is missing, and no false positive',()=>{
 const r=assessLiveReadinessInventory(Object.fromEntries(REVIEW_ITEMS.map(x=>[x,'VERIFIED'])));
 assert.equal(r.itemsClaimed,0);assert.equal(r.itemsMissing,REVIEW_ITEMS.length);
});
test('invalid readiness claims rejected',()=>{assert.equal(assessLiveReadinessInventory([]).status,'BLOCKED_INVALID_INPUT');});
test('valid synthetic paper intent returns PAPER CANDIDATE only',()=>{
 const r=check();assert.equal(r.status,'PAPER_CANDIDATE_PASSED_INVARIANTS_ONLY');
 assert.equal(r.liveTradingAuthorized,false);assert.equal(r.brokerOrderEndpointPresent,false);
 assert.equal(r.paperSimulationAllowedIfDataRightsActuallyPermit,false);
});
test('live mode is ALWAYS rejected',()=>deny('PAPER_MODE_REQUIRED',{candidate:{mode:'LIVE'}}));
test('short-selling and non-cash products rejected',()=>{
 deny('LONG_ONLY_BUY',{candidate:{side:'SELL'}});
 deny('CASH_INTRADAY_ONLY',{candidate:{product:'FUTURES'}});
});
test('market orders rejected',()=>deny('LIMIT_ONLY',{candidate:{orderType:'MARKET'}}));
test('wrong instrument mapping rejected',()=>deny('UNVERIFIED_INSTRUMENT',{feed:{instrumentKey:'NSE_EQ|OTHER123456'}}));
test('missing and nonsensical quantities rejected',()=>{
 deny('INVALID_QUANTITY',{candidate:{quantity:-1}});
 deny('INVALID_QUANTITY',{candidate:{quantity:1.5}});
});
test('invalid prices and tick sizes rejected',()=>{
 deny('INVALID_STOP_PRICE',{candidate:{stopPrice:100}});
 deny('INVALID_LIMIT_PRICE',{candidate:{limitPrice:NaN}});
 deny('PRICE_NOT_ON_TICK',{candidate:{limitPrice:100.02}});
});
test('single notional cap rejected',()=>deny('SINGLE_POSITION_CAP',{candidate:{quantity:26}}));
test('gross exposure cap rejected',()=>deny('GROSS_EXPOSURE_CAP',{account:{grossExposureRupees:2000},candidate:{quantity:10}}));
test('cash reserve cannot be breached',()=>deny('CASH_RESERVE_BREACH',{account:{cashAvailableRupees:4050}}));
test('risk budget includes adverse gap and friction',()=>deny('PER_TRADE_RISK_CAP',{candidate:{stopPrice:95,quantity:10}}));
test('daily and weekly negative P&L locks reject',()=>{
 deny('DAILY_LOSS_LOCK',{account:{dailyPnlRupees:-100}});
 deny('WEEKLY_LOSS_LOCK',{account:{weeklyPnlRupees:-300}});
});
test('peak equity drawdown rejects',()=>deny('DRAWDOWN_LOCK',{account:{equityRupees:9200}}));
test('order rate and in-flight lock reject',()=>{
 deny('ENTRY_COUNT_LOCK',{account:{sessionEntries:POLICY.maxVirtualEntriesPerSession}});
 deny('IN_FLIGHT_ORDERS',{account:{inFlightOrders:1}});
});
test('unreconciled paper journal rejects',()=>deny('VIRTUAL_LEDGER_NOT_RECONCILED',{account:{paperLedgerReconciled:false}}));
test('kill switch and incident block',()=>{
 deny('KILL_SWITCH_ENGAGED',{system:{killSwitchEngaged:true}});
 deny('SYSTEM_INCIDENT',{system:{incidentFree:false}});
});
test('market venue unverified blocks',()=>deny('UNVERIFIED_MARKET_STATE',{system:{verifiedRegularSession:false}}));
test('clock skew and invalid timestamp fail closed',()=>{
 deny('UNVERIFIED_CLOCK',{system:{clockSkewMs:900}});
 deny('INVALID_TIMESTAMP',{timestamp:'bogus'});
});
test('IST conservative time window blocks',()=>{
 deny('OUTSIDE_CONSERVATIVE_ENTRY_WINDOW',{timestamp:'2026-11-13T09:00:00+05:30'});
 deny('OUTSIDE_CONSERVATIVE_ENTRY_WINDOW',{timestamp:'2026-11-13T14:50:00+05:30'});
});
test('weekend blocks irrespective of vendor-provided market flag',()=>deny('WEEKEND',{timestamp:'2026-11-14T10:00:00+05:30'}));
test('must have legal data use consent and instrument eligibility',()=>{
 deny('FEED_NOT_PERMITTED',{feed:{dataUsePermitted:false}});
 deny('UNVERIFIED_INSTRUMENT',{feed:{instrumentTradable:false}});
});
test('book event age unknown, out of limits or invalid blocks',()=>{
 deny('BOOK_EVENT_FRESHNESS_UNKNOWN',{feed:{exchangeBookEventAgeMs:undefined}});
 deny('BOOK_EVENT_FRESHNESS_UNKNOWN',{feed:{exchangeBookEventAgeMs:3000}});
 deny('BOOK_MARKET_NOT_CERTIFIED',{feed:{bookQualityCertified:false}});
});
test('spread threshold blocks extreme bid-ask',()=>deny('INVALID_SPREAD',{feed:{spreadBps:25}}));
test('account values never silently default to healthy',()=>{
 deny('ACCOUNT_NUMBERS_UNVERIFIED',{account:{cashAvailableRupees:undefined}});
 deny('SESSION_ENTRY_COUNTER_UNVERIFIED',{account:{sessionEntries:undefined}});
});
test('output is deterministic and does not echo token, prices or account metadata',()=>{
 const r=check();assert.deepEqual(r,check());
 const j=JSON.stringify(r);assert.equal(j.includes(instrument),false);
 assert.equal(j.includes('"limitPrice"'),false);assert.equal(j.includes('"token"'),false);
});
test('module has no network import or broker submission method',()=>{
 const src=fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),'readiness_gate.mjs'),'utf8');
 for(const re of [/from ['"]node:https?['"]/,/from ['"]https?['"]/,/\bfetch\s*\(/,/\b(placeOrder|modifyOrder|cancelOrder|submitOrder)\s*\(/])assert.equal(re.test(src),false,String(re));
});