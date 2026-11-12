import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {
 auditSyntheticFeedChronology as audit,
 auditPairedSyntheticFeedWindows as pair
} from './synthetic_feed_chronology.mjs';

const base=Date.parse('2026-11-16T04:00:00Z');
const ZERO='0'.repeat(64);
const sha=x=>createHash('sha256').update(x).digest('hex');
const digest=f=>sha(JSON.stringify({
 ordinal:f.ordinal,eventId:f.eventId,kind:f.kind,
 receivedAtMs:f.receivedAtMs,vendorCurrentTsMs:f.vendorCurrentTsMs,
 declaredBookObservedAtMs:f.declaredBookObservedAtMs,
 sampleSha256:f.sampleSha256,prevSha256:f.prevSha256
}));
function reseal(w){
 let prev=ZERO;
 for(const f of w.frames){
   f.prevSha256=prev;f.sha256=digest(f);prev=f.sha256;
 }
 w.headSha256=prev;w.expectedFrameCount=w.frames.length;
 return w;
}
function windowOf(kinds=['BOOK_OBSERVATION','BOOK_OBSERVATION'],offset=0){
 const start=base+offset;
 const w={
   schemaVersion:1,fixtureKind:'HANDCRAFTED_SYNTHETIC_METADATA_ONLY',
   observationId:'mock-'+offset,sessionDate:'2026-11-16',
   instrumentAlias:'MOCK_EQ_1',captureStartMs:start,
   captureEndMs:start+(kinds.length+0.5)*1000,
   coverageClaim:'MOCK_COMPLETE_CAPTURE',expectedFrameCount:kinds.length,
   clockSemantics:'VENDOR_CURRENT_TS_NOT_EXCHANGE_BOOK_EVENT_TIME',
   frames:[],headSha256:ZERO
 };
 kinds.forEach((kind,i)=>{
   const received=start+(i+1)*1000;
   const hasTick=!['DISCONNECT','RECONNECT','AUTH_FAILURE'].includes(kind);
   w.frames.push({
     ordinal:i+1,eventId:'e'+(i+1),kind,receivedAtMs:received,
     vendorCurrentTsMs:hasTick?received-50:null,
     declaredBookObservedAtMs:kind==='BOOK_OBSERVATION'?received-100:null,
     sampleSha256:sha('f'+i+kind+offset),
     prevSha256:ZERO,sha256:ZERO
   });
 });
 return reseal(w);
}
const clock=w=>({observedAtMs:w.captureEndMs+100});
const run=w=>audit(w,clock(w));
const reason=(w,code)=>{
 const r=run(w);
 assert.equal(r.status,'HALT_SYNTHETIC_CHRONOLOGY_INTEGRITY',JSON.stringify(r));
 assert.ok(r.reasons.includes(code),JSON.stringify(r));
 assert.equal(r.canTrade,false);
};
test('consistent two-book mock is only mock ordering, never verified feed',()=>{
 const r=run(windowOf());
 assert.equal(r.status,'MOCK_CHRONOLOGY_INTERNALLY_CONSISTENT_ONLY',JSON.stringify(r));
 assert.equal(r.declaredBookObservationCount,2);
 assert.equal(r.independentlyAuthenticatedExchangeBookUpdates,0);
 assert.equal(r.canMakePaperFill,false);
});
test('mock clean result never authorizes market data use or real orders',()=>{
 const r=run(windowOf());
 assert.equal(r.externallyVerifiedDataPermissions,false);
 assert.equal(r.sourceCryptographicallyAuthenticated,false);
 assert.equal(r.sourceCompletenessIndependentlyCertified,false);
 assert.equal(r.realOrderRoutePresent,false);
 assert.equal(r.realOrdersSent,0);
});
test('three mock book events and heartbeat preserve self-declared only status',()=>{
 const r=run(windowOf(['BOOK_OBSERVATION','HEARTBEAT',
   'BOOK_OBSERVATION','BOOK_OBSERVATION']));
 assert.equal(r.status,'MOCK_CHRONOLOGY_INTERNALLY_CONSISTENT_ONLY');
 assert.equal(r.declaredHeartbeatCount,1);
});
test('single book snapshot cannot establish stream freshness',()=>{
 const w=windowOf(['BOOK_OBSERVATION']);
 reason(w,'INSUFFICIENT_DECLARED_BOOK_METRICS');
});
test('only vendor heartbeats cannot substitute for book updates',()=>{
 const w=windowOf(['HEARTBEAT','HEARTBEAT']);
 reason(w,'INSUFFICIENT_DECLARED_BOOK_METRICS');
 reason(w,'CAPTURE_END_BOOK_METRIC_NOT_FRESH');
});
test('fresh heartbeat cannot refresh aged book metric',()=>{
 const w=windowOf(['BOOK_OBSERVATION','BOOK_OBSERVATION',
  'HEARTBEAT','HEARTBEAT','HEARTBEAT']);
 reason(w,'CAPTURE_END_BOOK_METRIC_NOT_FRESH');
});
test('vendor currentTs older than local receive by three seconds is rejected',()=>{
 const w=windowOf();w.frames[1].vendorCurrentTsMs-=3100;
 reason(reseal(w),'VENDOR_TIMESTAMP_TOO_OLD');
});
test('vendor timestamp in future beyond skew allowance is blocked',()=>{
 const w=windowOf();w.frames[0].vendorCurrentTsMs+=700;
 reason(reseal(w),'VENDOR_CLOCK_IN_FUTURE');
});
test('vendor message clock regression detected without fabricating exchange seq',()=>{
 const w=windowOf();w.frames[1].vendorCurrentTsMs=w.frames[0].vendorCurrentTsMs-1;
 reason(reseal(w),'VENDOR_TIMESTAMP_REGRESSED');
});
test('stale reported book-update time blocks',()=>{
 const w=windowOf();w.frames[1].declaredBookObservedAtMs-=3000;
 reason(reseal(w),'DECLARED_BOOK_METRIC_STALE');
});
test('declared book-event time in future beyond skew allowance blocks',()=>{
 const w=windowOf();w.frames[1].declaredBookObservedAtMs+=1000;
 reason(reseal(w),'DECLARED_BOOK_CLOCK_IN_FUTURE');
});
test('unchanged book event timestamp blocks fresh-book claim',()=>{
 const w=windowOf();w.frames[1].declaredBookObservedAtMs=
   w.frames[0].declaredBookObservedAtMs;
 reason(reseal(w),'BOOK_METRIC_TIME_NOT_ADVANCING');
});
test('long interval between book events triggers missing continuity',()=>{
 const w=windowOf();
 w.captureEndMs+=12000;
 w.frames[1].receivedAtMs+=12000;
 w.frames[1].vendorCurrentTsMs+=12000;
 w.frames[1].declaredBookObservedAtMs+=12000;
 reason(reseal(w),'LONG_GAP_BETWEEN_DECLARED_BOOK_METRICS');
});
test('repeated book sample digest cannot prove a new book observation',()=>{
 const w=windowOf();w.frames[1].sampleSha256=w.frames[0].sampleSha256;
 reason(reseal(w),'REPEATED_BOOK_SAMPLE_DIGEST_CANNOT_CERTIFY_CHANGE');
});
test('non-monotonic received time blocks event ordering',()=>{
 const w=windowOf();w.frames[1].receivedAtMs=w.frames[0].receivedAtMs;
 reason(reseal(w),'RECEIVE_CLOCK_NOT_STRICTLY_MONOTONIC');
});
test('duplicate event identifier blocks double-count',()=>{
 const w=windowOf();w.frames[1].eventId=w.frames[0].eventId;
 reason(reseal(w),'DUPLICATE_CAPTURE_EVENT_ID');
});
test('missing or reordered local ordinal blocks even if hash is recomputed',()=>{
 const w=windowOf();w.frames[1].ordinal=3;
 reason(reseal(w),'MISSING_OR_REORDERED_LOCAL_FRAME_SEQUENCE');
});
test('missing frame despite declared count blocks',()=>{
 const w=windowOf();w.frames.pop();
 // retain original expectedFrameCount and head hash
 reason(w,'MISSING_OR_EXTRA_CAPTURE_RECORDS');
});
test('event payload modification without chain rebuild is detected',()=>{
 const w=windowOf();w.frames[1].receivedAtMs+=1;
 reason(w,'BROKEN_UNKEYED_EVENT_HASH_CHAIN');
});
test('forged chain head rejected even if frame sequence is otherwise correct',()=>{
 const w=windowOf();w.headSha256='e'.repeat(64);
 reason(w,'UNMATCHED_CAPTURE_HASH_HEAD');
});
test('disconnect is a hard halt and may not presume automatic continuation',()=>{
 const w=windowOf(['BOOK_OBSERVATION','BOOK_OBSERVATION','DISCONNECT']);
 reason(w,'OUTAGE_AUTH_FAILURE_OR_RECONNECT_REQUIRES_RESET');
});
test('reconnect requires new audit rather than automatically healing gap',()=>{
 const w=windowOf(['BOOK_OBSERVATION','RECONNECT','BOOK_OBSERVATION']);
 reason(w,'OUTAGE_AUTH_FAILURE_OR_RECONNECT_REQUIRES_RESET');
});
test('auth failure latches halt despite later vendor-shaped book metric',()=>{
 const w=windowOf(['BOOK_OBSERVATION','AUTH_FAILURE','BOOK_OBSERVATION']);
 reason(w,'OUTAGE_AUTH_FAILURE_OR_RECONNECT_REQUIRES_RESET');
});
test('order, trade, raw quote fields or credentials rejected by exact schema',()=>{
 for(const patch of [{accessToken:'secret'},{bid_price:12},
   {order_id:'an-order'},{rawFrame:'secret'}, {ltp:101}]){
   const w=windowOf();Object.assign(w.frames[1],patch);
   const r=run(w);
   assert.equal(r.status,'HALT_SYNTHETIC_CHRONOLOGY_INTEGRITY');
   assert.ok(r.reasons.includes('INVALID_OR_SECRET_BEARING_FRAME'));
 }
});
test('top-level secrets or raw market data cannot enter source metadata',()=>{
 const w=windowOf();w.clientId='private';
 const r=run(w);
 assert.equal(r.status,'BLOCKED_INVALID_ENVELOPE');
});
test('nonmock provider claim is invalid, not independently verified broker',()=>{
 const w=windowOf();w.fixtureKind='UPSTOX_LIVE';
 assert.equal(run(w).status,'BLOCKED_INVALID_ENVELOPE');
});
test('unverified real instrument identifier cannot replace mock alias',()=>{
 const w=windowOf();w.instrumentAlias='NSE_EQ|INE1234567890';
 assert.equal(run(w).status,'BLOCKED_INVALID_ENVELOPE');
});
test('empty capture cannot be trusted',()=>{
 const w=windowOf();w.frames=[];w.expectedFrameCount=0;
 assert.equal(run(w).status,'BLOCKED_INVALID_ENVELOPE');
});
test('excess declared frame count fails before ingesting huge payloads',()=>{
 const w=windowOf();w.expectedFrameCount=1001;
 assert.equal(run(w).status,'BLOCKED_INVALID_ENVELOPE');
});
test('capture timestamp ahead of injected clock blocks',()=>{
 const w=windowOf();
 const r=audit(w,{observedAtMs:w.captureEndMs-10});
 assert.ok(r.reasons.includes('CAPTURE_END_IN_FUTURE'));
});
test('capture completed too long before observation is not current',()=>{
 const w=windowOf();
 const r=audit(w,{observedAtMs:w.captureEndMs+10000});
 assert.ok(r.reasons.includes('CAPTURE_NOT_RECENT_AT_OBSERVATION'));
});
test('invalid missing clock never auto-falls back to Date.now',()=>{
 const w=windowOf();
 for(const o of [{},{observedAtMs:NaN},{observedAtMs:-1},
   {observedAtMs:Infinity}])
   assert.equal(audit(w,o).status,'BLOCKED_INVALID_CLOCK');
});
test('bad mock date and weekend rollover metadata rejected',()=>{
 const w=windowOf();w.sessionDate='2026-02-29';
 assert.equal(run(w).status,'BLOCKED_INVALID_ENVELOPE');
});
test('session date mismatch with actual capture local clock blocked',()=>{
 const w=windowOf();w.sessionDate='2026-11-17';
 reason(w,'SESSION_DATE_TIMESTAMP_MISMATCH');
});
test('longer than bounded 60s mock observation window rejected',()=>{
 const w=windowOf();w.captureEndMs=w.captureStartMs+61000;
 assert.equal(run(w).status,'BLOCKED_INVALID_ENVELOPE');
});
test('book metric with missing vendor timestamp blocked',()=>{
 const w=windowOf();w.frames[1].vendorCurrentTsMs=null;
 reason(reseal(w),'VENDOR_TIMESTAMP_MISSING');
});
test('book metric with missing claimed book time blocked',()=>{
 const w=windowOf();w.frames[1].declaredBookObservedAtMs=null;
 reason(reseal(w),'BOOK_METRIC_TIMESTAMP_MISSING');
});
test('heartbeat carrying fake book-update time is blocked',()=>{
 const w=windowOf(['BOOK_OBSERVATION','HEARTBEAT','BOOK_OBSERVATION']);
 w.frames[1].declaredBookObservedAtMs=w.frames[1].receivedAtMs;
 reason(reseal(w),'NON_BOOK_EVENT_CLAIMS_BOOK_METRIC_TIME');
});
test('disconnect carrying fake vendor quote timestamp is blocked',()=>{
 const w=windowOf(['BOOK_OBSERVATION','BOOK_OBSERVATION','DISCONNECT']);
 w.frames[2].vendorCurrentTsMs=w.frames[2].receivedAtMs;
 reason(reseal(w),'OUTAGE_STATE_MUST_NOT_CLAIM_VENDOR_TICK');
});
test('event outside declared capture bounds is blocked',()=>{
 const w=windowOf();w.frames[0].receivedAtMs=w.captureStartMs-1;
 reason(reseal(w),'EVENT_OUTSIDE_DECLARED_CAPTURE_WINDOW');
});
test('two nonoverlapping mock windows are still not authenticated',()=>{
 const a=windowOf(),b=windowOf(undefined,4000);
 const r=pair(a,b,{observedAtMs:b.captureEndMs+100});
 assert.equal(r.status,'MOCK_PAIR_INTERNALLY_CONSISTENT_ONLY',JSON.stringify(r));
 assert.equal(r.independentlyAuthenticatedExchangeBookUpdates,0);
 assert.equal(r.canTrade,false);
});
test('overlapping capture windows trigger hard halt',()=>{
 const a=windowOf(),b=windowOf(undefined,1000);
 const r=pair(a,b,{observedAtMs:b.captureEndMs+100});
 assert.ok(r.reasons.includes('OVERLAPPING_OR_REVERSED_CAPTURE_WINDOWS'));
});
test('reversed capture windows trigger halt',()=>{
 const a=windowOf(undefined,4000),b=windowOf();
 const r=pair(a,b,{observedAtMs:a.captureEndMs+100});
 assert.ok(r.reasons.includes('OVERLAPPING_OR_REVERSED_CAPTURE_WINDOWS'));
});
test('duplicate observation IDs between windows trigger halt',()=>{
 const a=windowOf(),b=windowOf(undefined,4000);b.observationId=a.observationId;
 const r=pair(a,b,{observedAtMs:b.captureEndMs+100});
 assert.ok(r.reasons.includes('DUPLICATED_OBSERVATION_ID'));
});
test('observing another instrument under one session requires reset',()=>{
 const a=windowOf(),b=windowOf(undefined,4000);b.instrumentAlias='MOCK_EQ_2';
 const r=pair(a,b,{observedAtMs:b.captureEndMs+100});
 assert.ok(r.reasons.includes('INSTRUMENT_CAPTURE_SCOPE_CHANGED'));
});
test('more than 10 seconds unknown between capture windows fails closed',()=>{
 const a=windowOf(),b=windowOf(undefined,15000);
 const r=pair(a,b,{observedAtMs:b.captureEndMs+100});
 assert.ok(r.reasons.includes('UNOBSERVED_INTER_WINDOW_GAP'));
});
test('bad capture in pair cannot be bypassed by clean peer',()=>{
 const a=windowOf(),b=windowOf(undefined,4000);
 a.frames[0].sha256='f'.repeat(64);
 const r=pair(a,b,{observedAtMs:b.captureEndMs+100});
 assert.ok(r.reasons.includes('ONE_OR_BOTH_CAPTURE_WINDOWS_FAILED'));
});
test('unknown event type cannot claim vendor event health',()=>{
 const w=windowOf();w.frames[0].kind='ORDER_SUBMISSION';
 assert.ok(run(w).reasons.includes('INVALID_OR_SECRET_BEARING_FRAME'));
});
test('sha and times from a self-claimed fixture never authenticate source',()=>{
 const r=run(windowOf());const json=JSON.stringify(r);
 for(const k of ['MOCK_EQ_1','observationId','sampleSha256','headSha256'])
   assert.equal(json.includes(k),false);
 assert.equal(r.exchangeEventTimeIndependentlyProven,false);
 assert.equal(r.licensedRawFramesExamined,0);
});


test('timestamp outside JavaScript Date range fails rather than throwing',()=>{
 const w=windowOf();w.captureEndMs=Number.MAX_SAFE_INTEGER;
 const result=run(w);
 assert.equal(result.status,'BLOCKED_INVALID_ENVELOPE');
 const v=windowOf();v.frames[0].receivedAtMs=Number.MAX_SAFE_INTEGER;
 const auditResult=run(v);
 assert.equal(auditResult.status,'HALT_SYNTHETIC_CHRONOLOGY_INTEGRITY');
 assert.ok(auditResult.reasons.includes('INVALID_OR_SECRET_BEARING_FRAME'));
});
test('upstream-like quote blob pretending to be a snapshot cannot enter fixture',()=>{
 const w=windowOf();
 w.frames[0].feeds={currentTs:w.frames[0].receivedAtMs,
   ltpc:{ltp:100}};
 assert.ok(run(w).reasons.includes('INVALID_OR_SECRET_BEARING_FRAME'));
});
