import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync,createHash,sign as edSign} from 'node:crypto';
import {
  syntheticStatementSigningBytes as bytes,
  verifySyntheticReviewSignature as audit,
  verifyPairedSyntheticReviews as auditPair
} from './signed_mock_review_attestation.mjs';

const t0=Date.parse('2026-11-12T13:30:00Z');
const fixtureKind='HANDCRAFTED_SIGNED_MOCK_REVIEW';
const manifest='a'.repeat(64),dataHash='b'.repeat(64);
const reviewer=generateKeyPairSync('ed25519');
const other=generateKeyPairSync('ed25519');
const ec=generateKeyPairSync('ec',{namedCurve:'prime256v1'});
const pub=k=>k.publicKey.export({type:'spki',format:'pem'});
const fp=k=>createHash('sha256')
  .update(k.publicKey.export({type:'spki',format:'der'})).digest('hex');
const statement=(patch={})=>({
  domain:'QHAP_RESEARCH_FIXTURE_V1',
  reviewerRole:'MOCK_REVIEWER_ONLY',
  studyId:'QHAP_MOCK_STUDY',
  manifestSha256:manifest,
  observationId:'mock-A',
  syntheticMetadataSha256:dataHash,
  reviewedAtMs:t0,
  expiresAtMs:t0+3600000,
  reviewDecision:'MOCK_PASSED',
  evidenceType:'SYNTHETIC_METADATA_ONLY',
  simulationUseRestriction:'EXTERNAL_LEGAL_REVIEW_REQUIRED',
  ...patch
});
const signed=(s=statement(),key=reviewer)=>({
  schemaVersion:1,fixtureKind,statement:s,
  signatureBase64:edSign(null,bytes(s),key.privateKey).toString('base64')
});
const trust=(patch={},key=reviewer)=>({
  trustedPublicKeyPem:pub(key),
  trustedSpkiSha256:fp(key),
  expectedManifestSha256:manifest,
  expectedObservationId:'mock-A',
  observedAtMs:t0+1000,
  ...patch
});
const reason=(env,ctx,why)=>{
  const r=audit(env,ctx);
  assert.equal(r.canTrade,false);
  assert.ok(r.reasons.includes(why),JSON.stringify(r));
  return r;
};
test('valid synthetic Ed25519 verifies mathematics but cannot certify identity',()=>{
  const r=audit(signed(),trust());
  assert.equal(r.status,'MOCK_SIGNATURE_MATHEMATICALLY_VALID_ONLY',JSON.stringify(r));
  assert.equal(r.signatureMathematicallyValid,true);
  assert.equal(r.externalTrustRootVerified,false);
  assert.equal(r.independentReviewerIdentityVerified,false);
});
test('real or paper order capability is always disabled even with signed pass',()=>{
  const r=audit(signed(),trust());
  assert.equal(r.canTrade,false);
  assert.equal(r.canMakePaperFill,false);
  assert.equal(r.liveTradingAuthorized,false);
  assert.equal(r.realOrderRoutePresent,false);
  assert.equal(r.realOrdersSent,0);
});
test('mathematical signature does not prove legal right to market data',()=>{
  const r=audit(signed(),trust());
  assert.equal(r.legalLicenseRightsVerified,false);
  assert.equal(r.virtualSimulationPermitted,false);
  assert.equal(r.authorizedMarketDataUse,false);
  assert.equal(r.independentlyVerifiedForwardSessions,0);
});
test('a user can self-sign a matching fixture: must never be elevated',()=>{
  const r=audit(signed(statement(),other),trust({},other));
  assert.equal(r.status,'MOCK_SIGNATURE_MATHEMATICALLY_VALID_ONLY');
  assert.equal(r.independentReviewerIdentityVerified,false);
  assert.equal(r.externalTrustRootVerified,false);
});
test('public key pin mismatch blocks, even if signature mathematically valid',()=>{
  const r=reason(signed(),trust({trustedSpkiSha256:fp(other)}),
    'TRUSTED_PUBLIC_KEY_FINGERPRINT_MISMATCH');
  assert.equal(r.signatureMathematicallyValid,true);
  assert.equal(r.status,'HALT_MOCK_SIGNATURE_OR_SCOPE');
});
test('adversary substitutes its own key while external pin stays unchanged',()=>{
  const r=reason(signed(statement(),other),trust({
    trustedPublicKeyPem:pub(other)
  }), 'TRUSTED_PUBLIC_KEY_FINGERPRINT_MISMATCH');
  assert.equal(r.signatureMathematicallyValid,true);
});
test('wrong cryptographic verifying key blocks attempted forgery',()=>{
  const r=reason(signed(statement(),other),trust(),
    'SIGNATURE_MATHEMATICALLY_INVALID');
  assert.equal(r.signatureMathematicallyValid,false);
});
test('signed field tampering fails signature integrity',()=>{
  const e=signed();e.statement.syntheticMetadataSha256='c'.repeat(64);
  reason(e,trust(),'SIGNATURE_MATHEMATICALLY_INVALID');
});
test('signed manifest changed and re-signed with authorized mock key still blocks',()=>{
  const e=signed(statement({manifestSha256:'c'.repeat(64)}));
  const r=reason(e,trust(),'FROZEN_MANIFEST_HASH_MISMATCH');
  assert.equal(r.signatureMathematicallyValid,true);
});
test('signed observation id replayed in wrong context blocks',()=>{
  const e=signed(statement({observationId:'mock-B'}));
  reason(e,trust(),'REVIEWED_OBSERVATION_MISMATCH');
});
test('expired statement is not automatically refreshed by signature',()=>{
  const e=signed();
  reason(e,trust({observedAtMs:t0+3600001}),
    'REVIEW_STATEMENT_EXPIRED');
});
test('future reviewer timestamp is rejected even though signature verifies',()=>{
  const e=signed();
  reason(e,trust({observedAtMs:t0-1}),
    'REVIEW_TIMESTAMP_IN_FUTURE');
});
test('old but unexpired statement is rejected under freshness policy',()=>{
  const e=signed(statement({expiresAtMs:t0+3*86400000}));
  reason(e,trust({observedAtMs:t0+2*86400000}),
    'REVIEW_STATEMENT_TOO_OLD');
});
test('statement with validity over seven days cannot be signed',()=>{
  const s=statement({expiresAtMs:t0+8*86400000});
  assert.throws(()=>bytes(s),/INVALID_SYNTHETIC_STATEMENT/);
});
test('negative, fractional or unsafe time cannot be signed',()=>{
  for(const at of [-1,1.3,Number.MAX_SAFE_INTEGER,NaN,Infinity]) {
    assert.throws(()=>bytes(statement({reviewedAtMs:at})),
      /INVALID_SYNTHETIC_STATEMENT/);
  }
});
test('reviewed time must precede expiry',()=>{
  assert.throws(()=>bytes(statement({expiresAtMs:t0})),
    /INVALID_SYNTHETIC_STATEMENT/);
});
test('reviewer role cannot claim real independent assessor identity',()=>{
  assert.throws(()=>bytes(statement({reviewerRole:'REAL_NSE_REVIEWER'})),
    /INVALID_SYNTHETIC_STATEMENT/);
});
test('signed domain separation prevents alternative evidence protocol',()=>{
  assert.throws(()=>bytes(statement({domain:'BROKER_CERTIFIED_EVIDENCE'})),
    /INVALID_SYNTHETIC_STATEMENT/);
});
test('passing a real market source identity rather than synthetic scope fails',()=>{
  assert.throws(()=>bytes(statement({evidenceType:'REAL_UPSTOX_MARKET_DATA'})),
    /INVALID_SYNTHETIC_STATEMENT/);
});
test('market data simulation restriction must remain unresolved',()=>{
  assert.throws(()=>bytes(statement({simulationUseRestriction:'PERMITTED'})),
    /INVALID_SYNTHETIC_STATEMENT/);
});
test('a denied review can have valid signature but remains hard halt',()=>{
  const e=signed(statement({reviewDecision:'MOCK_DENIED'}));
  const r=reason(e,trust(),'SYNTHETIC_REVIEW_NOT_PASSED');
  assert.equal(r.signatureMathematicallyValid,true);
});
test('unknown review also remains blocked',()=>{
  const e=signed(statement({reviewDecision:'MOCK_UNKNOWN'}));
  reason(e,trust(),'SYNTHETIC_REVIEW_NOT_PASSED');
});
test('unexpected raw prices or account fields cannot be signed',()=>{
  for(const extra of [{last_price:113.25},{access_token:'secret'},
    {userAccount:'123'},{rawMarketData:[1,2]}]) {
    assert.throws(()=>bytes(statement(extra)),
      /INVALID_SYNTHETIC_STATEMENT/);
  }
});
test('signed package with extra private keys or comments is blocked',()=>{
  const e=signed();e.privateKeyPem='SECRET';
  assert.equal(audit(e,trust()).status,'HALT_INVALID_MOCK_ATTESTATION');
});
test('base64 signature with extra bytes or wrong length blocked',()=>{
  const e=signed();e.signatureBase64+='AAA';
  assert.equal(audit(e,trust()).status,'HALT_INVALID_MOCK_ATTESTATION');
  const f=signed();f.signatureBase64=Buffer.alloc(63).toString('base64');
  assert.equal(audit(f,trust()).status,'HALT_INVALID_MOCK_ATTESTATION');
});
test('missing trust pin never becomes auto-trust of embedded sender key',()=>{
  const e=signed();const t=trust();delete t.trustedSpkiSha256;
  assert.equal(audit(e,t).status,'HALT_UNTRUSTED_VERIFIER_CONTEXT');
});
test('trust input cannot include live credentials or broker account',()=>{
  const r=audit(signed(),{...trust(),access_token:'SECRET'});
  assert.equal(r.status,'HALT_UNTRUSTED_VERIFIER_CONTEXT');
});
test('RSA/EC key type cannot verify Ed25519 envelopes',()=>{
  const r=audit(signed(),trust({
    trustedPublicKeyPem:pub(ec),
    trustedSpkiSha256:fp(ec)
  }));
  assert.equal(r.status,'HALT_UNSUPPORTED_KEY_TYPE');
});
test('malformed PEM fails closed without throwing',()=>{
  const r=audit(signed(),trust({trustedPublicKeyPem:'-----BEGIN PUBLIC KEY-----broken'}));
  assert.equal(r.status,'HALT_INVALID_PUBLIC_KEY');
});
test('canonical payload stable when object key insertion order changes',()=>{
  const s=statement();
  const reversed=Object.fromEntries(Object.entries(s).reverse());
  assert.ok(bytes(s).equals(bytes(reversed)));
});
test('without valid observed clock no real-time fallback exists',()=>{
  for(const val of [NaN,-1,Infinity]) {
    const r=audit(signed(),trust({observedAtMs:val}));
    assert.equal(r.status,'HALT_UNTRUSTED_VERIFIER_CONTEXT');
  }
});
const first=()=>signed();
const second=()=>signed(statement({
  observationId:'mock-B',syntheticMetadataSha256:'c'.repeat(64),
  reviewedAtMs:t0+1000,expiresAtMs:t0+3601000
}));
const firstTrust=()=>trust({observedAtMs:t0+2000});
const secondTrust=()=>trust({
  expectedObservationId:'mock-B',observedAtMs:t0+2000
});
test('two clean signed fixtures are still only synthetic provenance',()=>{
  const r=auditPair(first(),second(),firstTrust(),secondTrust());
  assert.equal(r.status,'MOCK_REVIEW_PAIR_INTERNALLY_CONSISTENT_ONLY',JSON.stringify(r));
  assert.equal(r.legalLicenseRightsVerified,false);
  assert.equal(r.independentlyVerifiedForwardSessions,0);
});
test('pair rejects reused signed observation ID',()=>{
  const r=auditPair(first(),first(),firstTrust(),firstTrust());
  assert.ok(r.reasons.includes('REPLAYED_OBSERVATION_ID'));
});
test('pair rejects non-monotonic mock reviewer timestamps',()=>{
  const e=second();
  e.statement.reviewedAtMs=t0-1;
  e=signed(e.statement);
  const r=auditPair(first(),e,firstTrust(),secondTrust());
  assert.ok(r.reasons.includes('NON_MONOTONIC_REVIEW_TIME'));
});
test('pair rejects re-used source metadata fingerprint',()=>{
  const e=signed(statement({
    observationId:'mock-B',reviewedAtMs:t0+1000,
    expiresAtMs:t0+3601000
  }));
  const r=auditPair(first(),e,firstTrust(),secondTrust());
  assert.ok(r.reasons.includes('DUPLICATED_MOCK_SOURCE_DIGEST'));
});
test('pair rejects differing frozen manifest even with valid signatures',()=>{
  const e=signed(statement({
    observationId:'mock-B',syntheticMetadataSha256:'c'.repeat(64),
    manifestSha256:'d'.repeat(64),reviewedAtMs:t0+1000,
    expiresAtMs:t0+3601000
  }));
  const r=auditPair(first(),e,firstTrust(),secondTrust());
  assert.ok(r.reasons.includes('MANIFEST_SCOPE_CHANGED_ACROSS_REVIEWS'));
});
test('pair cannot hide one tampered signature',()=>{
  const e=second();e.signatureBase64=signed(statement({
    observationId:'mock-C'
  })).signatureBase64;
  const r=auditPair(first(),e,firstTrust(),secondTrust());
  assert.ok(r.reasons.includes('UNVERIFIED_OR_FAILED_MOCK_STATEMENT_IN_PAIR'));
});
test('verdict never echoes identity, PEM, key fingerprints, source hash or data',()=>{
  const t=trust(),e=signed(),r=audit(e,t);
  const text=JSON.stringify(r);
  for(const sensitive of [t.trustedPublicKeyPem,t.trustedSpkiSha256,
    e.statement.syntheticMetadataSha256,e.statement.observationId,
    e.signatureBase64]) {
    assert.equal(text.includes(sensitive),false);
  }
});
