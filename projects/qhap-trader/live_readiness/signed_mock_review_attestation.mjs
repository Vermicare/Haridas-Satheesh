/**
 * QHAP-TRADER — signed MOCK reviewer evidence boundary, offline only.
 *
 * Cryptographically verifies Ed25519 on a strictly synthetic statement
 * against a caller-provided public key and an independently supplied
 * expected SPKI fingerprint. This is a crypto primitive, NOT confirmation
 * that the signer is an authorized independent reviewer. A self-generated
 * key and self-signed claim can pass mathematical verification.
 *
 * No real licenses, broker accounts, raw quotes, tokens, person names,
 * orders, market data, network, file I/O or live-execution capability.
 *
 * The NSE Data Sharing & Usage Policy section 7.4 specifically raises
 * restrictions on providing data for virtual trading/simulation. Whether
 * a proposed research use is permitted needs external documented review.
 * https://www.nseindia.com/static/market-data/nse-data-policy
 */
import {createHash, createPublicKey, verify as cryptoVerify} from 'node:crypto';

const SHA=/^[a-f0-9]{64}$/;
const ID=/^[A-Za-z0-9_-]{3,64}$/;
const PREFIX='QHAP_SYNTHETIC_REVIEW_ATTESTATION_V1\n';
const STATEMENT_KEYS=[
  'domain','reviewerRole','studyId','manifestSha256','observationId',
  'syntheticMetadataSha256','reviewedAtMs','expiresAtMs',
  'reviewDecision','evidenceType','simulationUseRestriction'
];
const ENVELOPE_KEYS=['schemaVersion','fixtureKind','statement','signatureBase64'];
const TRUST_KEYS=[
  'trustedPublicKeyPem','trustedSpkiSha256','expectedManifestSha256',
  'expectedObservationId','observedAtMs'
];
const fixture='HANDCRAFTED_SIGNED_MOCK_REVIEW';
const DOMAIN='QHAP_RESEARCH_FIXTURE_V1';
const ROLE='MOCK_REVIEWER_ONLY';
const LOOKBACK=86400000,MAX_VALIDITY=7*86400000;
const isObj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const exact=(o,fields)=>isObj(o)&&Object.keys(o).length===fields.length&&
  Object.keys(o).every(k=>fields.includes(k));
const ms=n=>Number.isSafeInteger(n)&&n>=0&&n<=8640000000000000;
const result=(status,reasons=[],extra={})=>Object.freeze({
  status,reasons:[...new Set(reasons)].sort(),
  canTrade:false,realOrderRoutePresent:false,realOrdersSent:0,
  liveTradingAuthorized:false,canMakePaperFill:false,
  authorizedMarketDataUse:false,independentReviewerIdentityVerified:false,
  legalLicenseRightsVerified:false,virtualSimulationPermitted:false,
  independentTimeWitnessVerified:false,externalTrustRootVerified:false,
  brokerReconciled:false,sourceOrMarketDataAuthenticated:false,
  independentlyVerifiedForwardSessions:0,
  ...extra
});
function validateStatement(s){
  return exact(s,STATEMENT_KEYS)&&s.domain===DOMAIN&&s.reviewerRole===ROLE&&
    ID.test(s.studyId||'')&&SHA.test(s.manifestSha256||'')&&
    ID.test(s.observationId||'')&&SHA.test(s.syntheticMetadataSha256||'')&&
    ms(s.reviewedAtMs)&&ms(s.expiresAtMs)&&
    s.expiresAtMs>s.reviewedAtMs&&
    s.expiresAtMs-s.reviewedAtMs<=MAX_VALIDITY&&
    ['MOCK_PASSED','MOCK_DENIED','MOCK_UNKNOWN'].includes(s.reviewDecision)&&
    s.evidenceType==='SYNTHETIC_METADATA_ONLY'&&
    s.simulationUseRestriction==='EXTERNAL_LEGAL_REVIEW_REQUIRED';
}
function canonical(s){
  return PREFIX+JSON.stringify(Object.fromEntries(STATEMENT_KEYS.map(k=>[k,s[k]])));
}
export function syntheticStatementSigningBytes(statement){
  // Only test fixtures may be prepared for signing. Never ask for real
  // license text or private signing keys in this application.
  if(!validateStatement(statement))throw Error('INVALID_SYNTHETIC_STATEMENT');
  return Buffer.from(canonical(statement),'utf8');
}
export function verifySyntheticReviewSignature(envelope,trust){
  if(!exact(trust,TRUST_KEYS)||!ms(trust.observedAtMs)||
    !SHA.test(trust.trustedSpkiSha256||'')||
    !SHA.test(trust.expectedManifestSha256||'')||
    !ID.test(trust.expectedObservationId||'')||
    typeof trust.trustedPublicKeyPem!=='string'||
    trust.trustedPublicKeyPem.length>1000||
    !trust.trustedPublicKeyPem.startsWith('-----BEGIN PUBLIC KEY-----'))
    return result('HALT_UNTRUSTED_VERIFIER_CONTEXT',['INVALID_OR_MISSING_TRUST_CONTEXT']);
  if(!exact(envelope,ENVELOPE_KEYS)||envelope.schemaVersion!==1||
    envelope.fixtureKind!==fixture||!validateStatement(envelope.statement)||
    typeof envelope.signatureBase64!=='string'||
    !/^[A-Za-z0-9+/]{86}==$/.test(envelope.signatureBase64))
    return result('HALT_INVALID_MOCK_ATTESTATION',['INVALID_OR_SECRET_BEARING_ENVELOPE']);
  const s=envelope.statement;
  const reasons=[];
  if(s.manifestSha256!==trust.expectedManifestSha256)
    reasons.push('FROZEN_MANIFEST_HASH_MISMATCH');
  if(s.observationId!==trust.expectedObservationId)
    reasons.push('REVIEWED_OBSERVATION_MISMATCH');
  if(s.reviewedAtMs>trust.observedAtMs)
    reasons.push('REVIEW_TIMESTAMP_IN_FUTURE');
  if(trust.observedAtMs>s.expiresAtMs)
    reasons.push('REVIEW_STATEMENT_EXPIRED');
  if(trust.observedAtMs-s.reviewedAtMs>LOOKBACK&&
     trust.observedAtMs<=s.expiresAtMs)
    reasons.push('REVIEW_STATEMENT_TOO_OLD');
  let publicKey;
  try {
    publicKey=createPublicKey(trust.trustedPublicKeyPem);
    if(publicKey.asymmetricKeyType!=='ed25519')
      return result('HALT_UNSUPPORTED_KEY_TYPE',['ED25519_PUBLIC_KEY_REQUIRED']);
  } catch {
    return result('HALT_INVALID_PUBLIC_KEY',['UNREADABLE_PUBLIC_KEY']);
  }
  const fingerprint=createHash('sha256')
    .update(publicKey.export({type:'spki',format:'der'})).digest('hex');
  if(fingerprint!==trust.trustedSpkiSha256)
    reasons.push('TRUSTED_PUBLIC_KEY_FINGERPRINT_MISMATCH');
  const sig=Buffer.from(envelope.signatureBase64,'base64');
  if(sig.length!==64)
    return result('HALT_INVALID_MOCK_ATTESTATION',['INVALID_ED25519_SIGNATURE_BYTES']);
  const valid=cryptoVerify(null,syntheticStatementSigningBytes(s),
    publicKey,sig);
  if(!valid)reasons.push('SIGNATURE_MATHEMATICALLY_INVALID');
  if(s.reviewDecision!=='MOCK_PASSED')
    reasons.push('SYNTHETIC_REVIEW_NOT_PASSED');
  if(reasons.length)
    return result('HALT_MOCK_SIGNATURE_OR_SCOPE',reasons,{signatureMathematicallyValid:valid});
  return result('MOCK_SIGNATURE_MATHEMATICALLY_VALID_ONLY',[
    'PUBLIC_KEY_TRUST_ANCHOR_NOT_INDEPENDENTLY_VERIFIED',
    'SIGNED_MOCK_DOES_NOT_GRANT_DATA_RIGHTS_OR_TRADING',
    'NSE_SIMULATION_POLICY_REQUIRES_PROVIDER_DETERMINATION'
  ],{
    signatureMathematicallyValid:true,
    pinnedSpkiFingerprintMatched:true,
    statementScopeMatched:true
  });
}
/**
 * Detects replays/reordered signed fixture reviews. A valid pair STILL does
 * not establish independent signer identity, trading rights or data origin.
 */
export function verifyPairedSyntheticReviews(first,second,trustFirst,trustSecond){
  const a=verifySyntheticReviewSignature(first,trustFirst);
  const b=verifySyntheticReviewSignature(second,trustSecond);
  const reasons=[];
  if(a.status!=='MOCK_SIGNATURE_MATHEMATICALLY_VALID_ONLY'||
     b.status!=='MOCK_SIGNATURE_MATHEMATICALLY_VALID_ONLY')
    reasons.push('UNVERIFIED_OR_FAILED_MOCK_STATEMENT_IN_PAIR');
  const s1=first?.statement,s2=second?.statement;
  if(!validateStatement(s1)||!validateStatement(s2))
    reasons.push('UNTRUSTED_STATEMENT_IN_PAIR');
  else {
    if(s1.observationId===s2.observationId)
      reasons.push('REPLAYED_OBSERVATION_ID');
    if(s1.reviewedAtMs>=s2.reviewedAtMs)
      reasons.push('NON_MONOTONIC_REVIEW_TIME');
    if(s1.manifestSha256!==s2.manifestSha256)
      reasons.push('MANIFEST_SCOPE_CHANGED_ACROSS_REVIEWS');
    if(s1.syntheticMetadataSha256===s2.syntheticMetadataSha256)
      reasons.push('DUPLICATED_MOCK_SOURCE_DIGEST');
  }
  return reasons.length?
    result('HALT_MOCK_REVIEW_PAIR',reasons):
    result('MOCK_REVIEW_PAIR_INTERNALLY_CONSISTENT_ONLY',[
      'SIGNATURES_DO_NOT_PROVE_EXTERNAL_REVIEWER_OR_RIGHTS',
      'NO_AUTHENTICATED_SOURCE_OR_PROSPECTIVE_SESSIONS'
    ]);
}
