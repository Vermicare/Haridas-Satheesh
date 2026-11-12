/**
 * QHAP-TRADER — OFFLINE SYNTHETIC metadata-only feed chronology.
 *
 * Accepts only handcrafted mock event METADATA. NEVER ingest live vendor
 * payloads, keys, quote prices, market-depth, orders, account identifiers,
 * access tokens, or licensed market data into this/public-repository module.
 *
 * Docs cross-check (2026-11-12):
 * Upstox V3 streaming has a vendor "currentTs" / quote fields, not an
 * independently attested exchange book-update sequence or event clock:
 * https://upstox.com/developer/api-documentation/v3/get-market-data-feed/
 * Upstox REST V3 "timestamp" is response creation, NOT an order-book event:
 * https://upstox.com/developer/api-documentation/get-full-market-quote-v3/
 * Rights depend on individual relevant NSE/provider agreement:
 * https://www.nseindia.com/static/market-data/nse-data-policy
 *
 * Hash chaining detects corruption within a synthetic fixture; it does
 * not authenticate source, time, independent ownership or licensed use.
 */
import {createHash} from 'node:crypto';

const HASH=/^[a-f0-9]{64}$/;
const ID=/^[a-zA-Z0-9_-]{1,50}$/;
const DATE=/^20\d{2}-\d{2}-\d{2}$/;
const ZERO='0'.repeat(64);
const MAX_WINDOW_MS=60000;
const MAX_OBSERVATION_LAG_MS=5000;
const MAX_VENDOR_RECEIVE_LAG_MS=3000;
const MAX_BOOK_RECEIVE_LAG_MS=2000;
const MAX_BOOK_INTERVAL_MS=10000;
const TOLERABLE_FUTURE_CLOCK_MS=500;
const ROOT_KEYS=['schemaVersion','fixtureKind','observationId','sessionDate',
  'instrumentAlias','captureStartMs','captureEndMs','coverageClaim',
  'expectedFrameCount','clockSemantics','frames','headSha256'];
const FRAME_KEYS=['ordinal','eventId','kind','receivedAtMs',
  'vendorCurrentTsMs','declaredBookObservedAtMs','sampleSha256',
  'prevSha256','sha256'];
const EVENT_KINDS=new Set(['BOOK_OBSERVATION','TRADE_OBSERVATION',
  'HEARTBEAT','DISCONNECT','RECONNECT','AUTH_FAILURE']);
const SOURCE_ONLY=new Set(['BOOK_OBSERVATION','TRADE_OBSERVATION','HEARTBEAT']);
const OUTAGE=new Set(['DISCONNECT','RECONNECT','AUTH_FAILURE']);
const isObj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const exact=(x,keys)=>isObj(x)&&Object.keys(x).length===keys.length&&
  Object.keys(x).every(k=>keys.includes(k));
const nonNeg=n=>Number.isSafeInteger(n)&&n>=0;
const validDate=s=>{
  if(typeof s!=='string'||!DATE.test(s))return false;
  const d=new Date(s+'T00:00:00Z');
  return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===s;
};
const localDate=t=>new Date(t+19800000).toISOString().slice(0,10);
const sha=data=>createHash('sha256').update(data).digest('hex');
const payload=f=>JSON.stringify({
  ordinal:f.ordinal,eventId:f.eventId,kind:f.kind,
  receivedAtMs:f.receivedAtMs,vendorCurrentTsMs:f.vendorCurrentTsMs,
  declaredBookObservedAtMs:f.declaredBookObservedAtMs,
  sampleSha256:f.sampleSha256,prevSha256:f.prevSha256
});
const digest=f=>sha(payload(f));
const report=(status,reasons,counts={})=>Object.freeze({
  status,reasons:[...new Set(reasons)].sort(),
  observationKind:'SYNTHETIC_METADATA_ONLY',
  framesExamined:counts.framesExamined??0,
  declaredBookObservationCount:counts.declaredBookObservationCount??0,
  declaredHeartbeatCount:counts.declaredHeartbeatCount??0,
  declaredOutageCount:counts.declaredOutageCount??0,
  quotedPricesExamined:0,licensedRawFramesExamined:0,
  independentlyAuthenticatedExchangeBookUpdates:0,
  externallyVerifiedDataPermissions:false,
  sourceCryptographicallyAuthenticated:false,
  exchangeEventTimeIndependentlyProven:false,
  sourceCompletenessIndependentlyCertified:false,
  canMakePaperFill:false,canTrade:false,realOrderRoutePresent:false,
  liveTradingAuthorized:false,realOrdersSent:0
});

/**
 * Validates a handcrafted window using a caller-injected observation time.
 * A "clean" result means only that the MOCK dates/digests are consistent.
 */
export function auditSyntheticFeedChronology(window,options={}){
  if(!exact(options,['observedAtMs'])||!nonNeg(options.observedAtMs))
    return report('BLOCKED_INVALID_CLOCK',['INVALID_INJECTED_OBSERVATION_CLOCK']);
  if(!exact(window,ROOT_KEYS)||window.schemaVersion!==1||
    window.fixtureKind!=='HANDCRAFTED_SYNTHETIC_METADATA_ONLY'||
    !ID.test(window.observationId||'')||
    !validDate(window.sessionDate)||window.instrumentAlias!=='MOCK_EQ_1'||
    !nonNeg(window.captureStartMs)||!nonNeg(window.captureEndMs)||
    window.captureStartMs>=window.captureEndMs||
    window.captureEndMs-window.captureStartMs>MAX_WINDOW_MS||
    window.coverageClaim!=='MOCK_COMPLETE_CAPTURE'||
    window.clockSemantics!=='VENDOR_CURRENT_TS_NOT_EXCHANGE_BOOK_EVENT_TIME'||
    !Number.isSafeInteger(window.expectedFrameCount)||
    window.expectedFrameCount<1||window.expectedFrameCount>1000||
    !Array.isArray(window.frames)||!HASH.test(window.headSha256||''))
    return report('BLOCKED_INVALID_ENVELOPE',['INVALID_OR_EXTRA_SYNTHETIC_FIELDS']);
  const issues=[];
  if(window.frames.length!==window.expectedFrameCount)
    issues.push('MISSING_OR_EXTRA_CAPTURE_RECORDS');
  if(localDate(window.captureStartMs)!==window.sessionDate||
     localDate(window.captureEndMs)!==window.sessionDate)
    issues.push('SESSION_DATE_TIMESTAMP_MISMATCH');
  if(window.captureEndMs>options.observedAtMs)
    issues.push('CAPTURE_END_IN_FUTURE');
  if(options.observedAtMs-window.captureEndMs>MAX_OBSERVATION_LAG_MS)
    issues.push('CAPTURE_NOT_RECENT_AT_OBSERVATION');
  let prev=ZERO,lastReceive=-1,lastVendor=-1,lastBook=-1;
  let bookCount=0,heartbeatCount=0,outageCount=0;
  const ids=new Set(),bookDigests=new Set();
  for(let i=0;i<window.frames.length;i++){
    const f=window.frames[i];
    if(!exact(f,FRAME_KEYS)||!nonNeg(f.ordinal)||
      !ID.test(f.eventId||'')||!EVENT_KINDS.has(f.kind)||
      !nonNeg(f.receivedAtMs)||!HASH.test(f.sampleSha256||'')||
      !HASH.test(f.prevSha256||'')||!HASH.test(f.sha256||'')||
      (f.vendorCurrentTsMs!==null&&!nonNeg(f.vendorCurrentTsMs))||
      (f.declaredBookObservedAtMs!==null&&
       !nonNeg(f.declaredBookObservedAtMs))){
      issues.push('INVALID_OR_SECRET_BEARING_FRAME');continue;
    }
    if(f.ordinal!==i+1)issues.push('MISSING_OR_REORDERED_LOCAL_FRAME_SEQUENCE');
    if(ids.has(f.eventId))issues.push('DUPLICATE_CAPTURE_EVENT_ID');
    ids.add(f.eventId);
    if(f.prevSha256!==prev||digest(f)!==f.sha256)
      issues.push('BROKEN_UNKEYED_EVENT_HASH_CHAIN');
    prev=f.sha256;
    if(f.receivedAtMs<window.captureStartMs||
       f.receivedAtMs>window.captureEndMs)
      issues.push('EVENT_OUTSIDE_DECLARED_CAPTURE_WINDOW');
    if(f.receivedAtMs<=lastReceive)
      issues.push('RECEIVE_CLOCK_NOT_STRICTLY_MONOTONIC');
    lastReceive=f.receivedAtMs;
    if(SOURCE_ONLY.has(f.kind)){
      if(!nonNeg(f.vendorCurrentTsMs))
        issues.push('VENDOR_TIMESTAMP_MISSING');
      else{
        if(f.vendorCurrentTsMs>f.receivedAtMs+TOLERABLE_FUTURE_CLOCK_MS)
          issues.push('VENDOR_CLOCK_IN_FUTURE');
        if(f.receivedAtMs-f.vendorCurrentTsMs>MAX_VENDOR_RECEIVE_LAG_MS)
          issues.push('VENDOR_TIMESTAMP_TOO_OLD');
        if(f.vendorCurrentTsMs<lastVendor)
          issues.push('VENDOR_TIMESTAMP_REGRESSED');
        lastVendor=f.vendorCurrentTsMs;
      }
    }else if(f.vendorCurrentTsMs!==null){
      issues.push('OUTAGE_STATE_MUST_NOT_CLAIM_VENDOR_TICK');
    }
    if(f.kind==='BOOK_OBSERVATION'){
      bookCount++;
      if(!nonNeg(f.declaredBookObservedAtMs))
        issues.push('BOOK_METRIC_TIMESTAMP_MISSING');
      else{
        if(f.declaredBookObservedAtMs>f.receivedAtMs+TOLERABLE_FUTURE_CLOCK_MS)
          issues.push('DECLARED_BOOK_CLOCK_IN_FUTURE');
        if(f.receivedAtMs-f.declaredBookObservedAtMs>
           MAX_BOOK_RECEIVE_LAG_MS)
          issues.push('DECLARED_BOOK_METRIC_STALE');
        if(lastBook>=0&&f.declaredBookObservedAtMs<=lastBook)
          issues.push('BOOK_METRIC_TIME_NOT_ADVANCING');
        if(lastBook>=0&&f.declaredBookObservedAtMs-lastBook>
          MAX_BOOK_INTERVAL_MS)
          issues.push('LONG_GAP_BETWEEN_DECLARED_BOOK_METRICS');
        lastBook=f.declaredBookObservedAtMs;
      }
      if(bookDigests.has(f.sampleSha256))
        issues.push('REPEATED_BOOK_SAMPLE_DIGEST_CANNOT_CERTIFY_CHANGE');
      bookDigests.add(f.sampleSha256);
    }else if(f.declaredBookObservedAtMs!==null){
      issues.push('NON_BOOK_EVENT_CLAIMS_BOOK_METRIC_TIME');
    }
    if(f.kind==='HEARTBEAT')heartbeatCount++;
    if(OUTAGE.has(f.kind)){
      outageCount++;
      issues.push('OUTAGE_AUTH_FAILURE_OR_RECONNECT_REQUIRES_RESET');
    }
  }
  if(window.headSha256!==prev)
    issues.push('UNMATCHED_CAPTURE_HASH_HEAD');
  if(bookCount<2)
    issues.push('INSUFFICIENT_DECLARED_BOOK_METRICS');
  if(lastBook<0||window.captureEndMs-lastBook>MAX_BOOK_RECEIVE_LAG_MS)
    issues.push('CAPTURE_END_BOOK_METRIC_NOT_FRESH');
  const counts={framesExamined:window.frames.length,
    declaredBookObservationCount:bookCount,
    declaredHeartbeatCount:heartbeatCount,
    declaredOutageCount:outageCount};
  return issues.length?
    report('HALT_SYNTHETIC_CHRONOLOGY_INTEGRITY',issues,counts):
    report('MOCK_CHRONOLOGY_INTERNALLY_CONSISTENT_ONLY',[
      'MOCK_METADATA_CANNOT_CERTIFY_EXCHANGE_EVENT_FRESHNESS',
      'INDEPENDENT_SOURCE_ENTITLEMENT_AND_CLOCK_ATTESTATION_MISSING'
    ],counts);
}

/** Two separate synthetic windows do not certify continuous vendor sampling. */
export function auditPairedSyntheticFeedWindows(first,second,options={}){
  const a=auditSyntheticFeedChronology(first,options);
  const b=auditSyntheticFeedChronology(second,options);
  const reasons=[];
  const ok='MOCK_CHRONOLOGY_INTERNALLY_CONSISTENT_ONLY';
  if(a.status!==ok||b.status!==ok)
    reasons.push('ONE_OR_BOTH_CAPTURE_WINDOWS_FAILED');
  if(!isObj(first)||!isObj(second))
    reasons.push('INVALID_CAPTURE_PAIR');
  else{
    if(first.observationId===second.observationId)
      reasons.push('DUPLICATED_OBSERVATION_ID');
    if(first.sessionDate!==second.sessionDate)
      reasons.push('SESSION_ROLLOVER_REQUIRES_NEW_ATTESTATION');
    if(first.instrumentAlias!==second.instrumentAlias)
      reasons.push('INSTRUMENT_CAPTURE_SCOPE_CHANGED');
    if(!nonNeg(first.captureEndMs)||!nonNeg(second.captureStartMs)||
      second.captureStartMs<=first.captureEndMs)
      reasons.push('OVERLAPPING_OR_REVERSED_CAPTURE_WINDOWS');
    else if(second.captureStartMs-first.captureEndMs>MAX_BOOK_INTERVAL_MS)
      reasons.push('UNOBSERVED_INTER_WINDOW_GAP');
  }
  return report(reasons.length?'HALT_SYNTHETIC_PAIR_INTEGRITY':
    'MOCK_PAIR_INTERNALLY_CONSISTENT_ONLY',
    reasons.length?reasons:[
      'INDEPENDENT_SOURCE_ENTITLEMENT_AND_CLOCK_ATTESTATION_MISSING'
    ],{
      framesExamined:a.framesExamined+b.framesExamined,
      declaredBookObservationCount:
        a.declaredBookObservationCount+b.declaredBookObservationCount,
      declaredHeartbeatCount:
        a.declaredHeartbeatCount+b.declaredHeartbeatCount,
      declaredOutageCount:a.declaredOutageCount+b.declaredOutageCount
    });
}
