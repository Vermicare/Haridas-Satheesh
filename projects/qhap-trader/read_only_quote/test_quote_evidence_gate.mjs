import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluateSanitizedObservation, summarizeSanitizedObservations} from './quote_evidence_gate.mjs';

const base=()=>({
 tradesSent:0, ordersPossible:false,paperTradesCreated:0,
 safeToUseForPaperExecution:false,completeSessionCertified:false,
 marketDataStored:false,pricesPrinted:false,quoteLicensingCertified:false,
 exchangeOpenCertified:false,dataProvenance:'ONE_VENDOR_V3_REST_SNAPSHOT_USER_LOCAL_ONLY',
 tradeAgeSeconds:5,snapshotAgeSeconds:0,
 status:'RECENT_SNAPSHOT_OLDER_LAST_TRADE_OBSERVATION_ONLY',
 reason:'LAST_TRADE_OLDER_THAN_3_SECONDS',
 explanation:'Recent vendor response, but last completed trade is older. NOT a validated execution tick.'
});
const check=patch=>evaluateSanitizedObservation({...base(),...patch});
test('real-world-like last-trade age 5s and snapshot 0s stays observation only',()=>{
 const x=check({});
 assert.equal(x.classification,'RECENT_VENDOR_RESPONSE_OLD_TRADE_OBSERVATION_ONLY');
 assert.equal(x.responseAgeSecondsReported,0);
 assert.equal(x.lastTradeAgeSecondsReported,5);
 assert.equal(x.executablePriceCertified,false);
 assert.equal(x.continuousFeedValidated,false);
 assert.equal(x.liveOrderAuthorization,false);
 assert.equal(x.paperSessionCertified,false);
 assert.equal(x.ordersSent,0);
});
test('vendor response generation is not claimed as market-book update freshness',()=>{
 const x=check({});
 assert.equal(x.marketDataFreshnessCertified,false);
 assert.equal(x.recommendedNextGate,'AUTHORIZED_MULTI_SAMPLE_FEED_HEALTH_AND_BOOK_UPDATE_PROVENANCE');
});
test('does not print user price or broker secrets',()=>{
 const x=check({});
 assert.doesNotMatch(JSON.stringify(x),/token|bidPrice|askPrice|last_price|Authorization/i);
});
test('strict one-shot pass also does not promote a trading session',()=>{
 const p=base();delete p.tradeAgeSeconds;delete p.snapshotAgeSeconds;delete p.reason;
 p.status='STRICT_SINGLE_QUOTE_FRESHNESS_PASSED_NOT_A_SESSION';
 const x=evaluateSanitizedObservation(p);
 assert.equal(x.classification,'SINGLE_REST_CHECK_PASSED_NO_SESSION_CERTIFICATION');
 assert.equal(x.paperSessionCertified,false);
 assert.equal(x.executablePriceCertified,false);
});
test('rejects missing safety flags',()=>{
 const p=base();delete p.marketDataStored;
 assert.throws(()=>evaluateSanitizedObservation(p),/UNSAFE_OR_UNVERIFIED_DIAGNOSTIC_FLAGS/);
});
test('rejects attempt to claim orders or paper trades',()=>{
 for(const patch of [{tradesSent:1},{paperTradesCreated:2},
   {ordersPossible:true},{safeToUseForPaperExecution:true},
   {completeSessionCertified:true},{quoteLicensingCertified:true}])
  assert.throws(()=>check(patch),/UNSAFE_OR_UNVERIFIED_DIAGNOSTIC_FLAGS/);
});
test('rejects arbitrary secret or raw quote fields',()=>{
 for(const patch of [{token:'DO_NOT_PRINT'},{last_price:120},{bid:105},
   {Authorization:'Bearer secret'},{instrumentKey:'secret'}])
  assert.throws(()=>check(patch),/UNEXPECTED_PRIVATE_OR_RAW_FIELD/);
});
test('rejects incorrect reasons for observation-only',()=>{
 assert.throws(()=>check({reason:'SOMETHING_ELSE'}),
  /INCONSISTENT_RECENT_SNAPSHOT_OLDER_TRADE_STATUS/);
});
test('rejects fresh trade being labeled older than three seconds',()=>{
 assert.throws(()=>check({tradeAgeSeconds:3}),
  /INCONSISTENT_RECENT_SNAPSHOT_OLDER_TRADE_STATUS/);
});
test('rejects old quote snapshot labeled fresh',()=>{
 assert.throws(()=>check({snapshotAgeSeconds:7}),
  /INCONSISTENT_RECENT_SNAPSHOT_OLDER_TRADE_STATUS/);
});
test('rejects bad timestamp format and future negative ages',()=>{
 for(const patch of [{tradeAgeSeconds:-3},{tradeAgeSeconds:'5'},
   {snapshotAgeSeconds:NaN},{snapshotAgeSeconds:Infinity}])
  assert.throws(()=>check(patch),/INVALID_TIMESTAMP_AGES/);
});
test('rejects nonsensical chronology',()=>{
 assert.throws(()=>check({tradeAgeSeconds:5,snapshotAgeSeconds:6}),
  /INCONSISTENT_RECENT_SNAPSHOT_OLDER_TRADE_STATUS/);
});
test('stale quote status is rejected, never interpreted as executable',()=>{
 const x=check({status:'QUOTE_SNAPSHOT_STALE_REJECTED',
  reason:'RESPONSE_SNAPSHOT_EXCEEDS_3_SECOND_LIMIT'});
 assert.equal(x.classification,'REJECTED_DIAGNOSTIC_NO_PROMOTION');
 assert.equal(x.marketDataFreshnessCertified,false);
});
test('unknown statuses cannot be promoted',()=>{
 const x=check({status:'TRADE_NOW'});
 assert.equal(x.classification,'UNKNOWN_UNVERIFIED_STATUS_NO_PROMOTION');
});
test('null/array or missing record is rejected',()=>{
 for(const x of [null,[],undefined,23])
  assert.throws(()=>evaluateSanitizedObservation(x),/INVALID_SANITIZED_RECORD/);
});
test('aggregation can count sanitized diagnostics but cannot certify feed',()=>{
 const x=summarizeSanitizedObservations([base(),base(),base()]);
 assert.equal(x.recordsReviewed,3);
 assert.equal(x.countRecentVendorResponseOlderLastTrade,3);
 assert.equal(x.continuousFeedValidated,false);
 assert.equal(x.newTradingEvidence,false);
 assert.equal(x.stillRequiresTimestampedExchangeBookUpdates,true);
});
test('aggregation does not accept empty or unbounded inputs',()=>{
 assert.throws(()=>summarizeSanitizedObservations([]),/REQUIRES_ONE_TO_FIFTY_SANITIZED_SAMPLES/);
 assert.throws(()=>summarizeSanitizedObservations(Array(51).fill(base())),/REQUIRES_ONE_TO_FIFTY_SANITIZED_SAMPLES/);
});
