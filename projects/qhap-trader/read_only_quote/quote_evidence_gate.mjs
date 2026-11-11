/**
 * QHAP-TRADER: evidence-only categorization of LOCAL, SANITIZED diagnostic statuses.
 * No networking, market prices, credentials, storage, orders or trade simulations.
 * An Upstox V3 REST response-generation timestamp is NOT proof that the
 * bid/ask book changed or a quote is currently executable.
 */
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const allowed=new Set([
 'tradesSent','ordersPossible','paperTradesCreated','safeToUseForPaperExecution',
 'completeSessionCertified','marketDataStored','pricesPrinted',
 'quoteLicensingCertified','exchangeOpenCertified','dataProvenance',
 'tradeAgeSeconds','snapshotAgeSeconds','status','reason','explanation',
 'localClockReliableNotProven'
]);
const safeType=x=>typeof x==='number'&&Number.isSafeInteger(x)&&x>=0&&x<=86400;
function guard(record){
 if(!record||typeof record!=='object'||Array.isArray(record))
  throw Error('INVALID_SANITIZED_RECORD');
 for(const field of Object.keys(record))
  if(!allowed.has(field))throw Error('UNEXPECTED_PRIVATE_OR_RAW_FIELD');
 const zero=['tradesSent','paperTradesCreated'];
 const falseFields=['ordersPossible','safeToUseForPaperExecution',
  'completeSessionCertified','marketDataStored','pricesPrinted',
  'quoteLicensingCertified','exchangeOpenCertified'];
 if(zero.some(k=>record[k]!==0)||falseFields.some(k=>record[k]!==false)||
    record.dataProvenance!=='ONE_VENDOR_V3_REST_SNAPSHOT_USER_LOCAL_ONLY')
  throw Error('UNSAFE_OR_UNVERIFIED_DIAGNOSTIC_FLAGS');
 if(typeof record.status!=='string'||record.status.length>90||
   (record.reason!==undefined&&(typeof record.reason!=='string'||record.reason.length>120)))
  throw Error('INVALID_STATUS');
 if(record.tradeAgeSeconds!==undefined&&!safeType(record.tradeAgeSeconds)||
    record.snapshotAgeSeconds!==undefined&&!safeType(record.snapshotAgeSeconds))
  throw Error('INVALID_TIMESTAMP_AGES');
}
const common=Object.freeze({
 source:'USER_REPORTED_LOCAL_ONE_SHOT_UPSTOX_V3_REST',
 authenticatedHttp200DirectlyVerifiedByThisModule:false,
 marketDataFreshnessCertified:false,continuousFeedValidated:false,
 executablePriceCertified:false,paperSessionCertified:false,
 noTradeComparatorPreserved:true,liveOrderAuthorization:false,
 ordersSent:0,simulatedOrdersCreated:0,
});
export function evaluateSanitizedObservation(record){
 guard(record);
 if(record.status==='RECENT_SNAPSHOT_OLDER_LAST_TRADE_OBSERVATION_ONLY'){
  if(!safeType(record.snapshotAgeSeconds)||!safeType(record.tradeAgeSeconds)||
    record.snapshotAgeSeconds>3||record.tradeAgeSeconds<=3||
    record.tradeAgeSeconds<record.snapshotAgeSeconds||
    record.reason!=='LAST_TRADE_OLDER_THAN_3_SECONDS')
    throw Error('INCONSISTENT_RECENT_SNAPSHOT_OLDER_TRADE_STATUS');
  return {...common,classification:'RECENT_VENDOR_RESPONSE_OLD_TRADE_OBSERVATION_ONLY',
    responseAgeSecondsReported:record.snapshotAgeSeconds,
    lastTradeAgeSecondsReported:record.tradeAgeSeconds,
    usableFor:'DATA_QUALITY_RESEARCH_ONLY_NOT_PAPER_FILL',
    recommendedNextGate:'AUTHORIZED_MULTI_SAMPLE_FEED_HEALTH_AND_BOOK_UPDATE_PROVENANCE'};
 }
 if(record.status==='STRICT_SINGLE_QUOTE_FRESHNESS_PASSED_NOT_A_SESSION'){
  // This older diagnostic emits no price, clock or age metrics on a strict pass.
  if(record.tradeAgeSeconds!==undefined||record.snapshotAgeSeconds!==undefined)
    throw Error('UNEXPECTED_STRICT_PASS_AGE_METRICS');
  return {...common,classification:'SINGLE_REST_CHECK_PASSED_NO_SESSION_CERTIFICATION',
    usableFor:'READ_ONLY_CONNECTIVITY_EVIDENCE_ONLY',
    recommendedNextGate:'AUTHORIZED_MULTI_SAMPLE_FEED_HEALTH_AND_BOOK_UPDATE_PROVENANCE'};
 }
 const rejected=new Set(['QUOTE_REJECTED','QUOTE_SNAPSHOT_STALE_REJECTED',
  'FUTURE_TIMESTAMP_CLOCK_OR_VENDOR_REJECTED','TRADE_AFTER_VENDOR_SNAPSHOT_REJECTED',
  'QUOTE_FRESHNESS_CONTRADICTION_REJECTED']);
 if(!rejected.has(record.status))return {...common,
   classification:'UNKNOWN_UNVERIFIED_STATUS_NO_PROMOTION',
   usableFor:'NONE'};
 return {...common,classification:'REJECTED_DIAGNOSTIC_NO_PROMOTION',usableFor:'NONE'};
}
/** Advisory aggregation, NEVER a stream/sampling certification. */
export function summarizeSanitizedObservations(records){
 if(!Array.isArray(records)||records.length<1||records.length>50)
  throw Error('REQUIRES_ONE_TO_FIFTY_SANITIZED_SAMPLES');
 const results=records.map(evaluateSanitizedObservation);
 return {...common,
  recordsReviewed:results.length,
  countRecentVendorResponseOlderLastTrade:results.filter(x=>
   x.classification==='RECENT_VENDOR_RESPONSE_OLD_TRADE_OBSERVATION_ONLY').length,
  countStrictSingleCheckPassed:results.filter(x=>
   x.classification==='SINGLE_REST_CHECK_PASSED_NO_SESSION_CERTIFICATION').length,
  countRejectedOrUnknown:results.filter(x=>
   !['RECENT_VENDOR_RESPONSE_OLD_TRADE_OBSERVATION_ONLY',
     'SINGLE_REST_CHECK_PASSED_NO_SESSION_CERTIFICATION'].includes(x.classification)).length,
  output:'AGGREGATE_LOCAL_DIAGNOSTIC_EVIDENCE_ONLY',
  stillRequiresTimestampedExchangeBookUpdates:true,
  newTradingEvidence:false
 };
}
if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
 if(process.argv.length!==3||process.argv[2]!=='--demo'){
  console.error('Usage: node quote_evidence_gate.mjs --demo (synthetic only)');
  process.exitCode=1;
 }else{
  const synthetic={tradesSent:0,ordersPossible:false,paperTradesCreated:0,
   safeToUseForPaperExecution:false,completeSessionCertified:false,
   marketDataStored:false,pricesPrinted:false,quoteLicensingCertified:false,
   exchangeOpenCertified:false,
   dataProvenance:'ONE_VENDOR_V3_REST_SNAPSHOT_USER_LOCAL_ONLY',
   tradeAgeSeconds:5,snapshotAgeSeconds:0,
   status:'RECENT_SNAPSHOT_OLDER_LAST_TRADE_OBSERVATION_ONLY',
   reason:'LAST_TRADE_OLDER_THAN_3_SECONDS'};
  console.log(JSON.stringify({syntheticOnly:true,...evaluateSanitizedObservation(synthetic)}));
 }
}
