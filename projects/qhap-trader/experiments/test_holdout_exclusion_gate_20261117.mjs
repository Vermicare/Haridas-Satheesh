// Fictional-only contract checks. No private bars, prices, tokens or broker routes.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const registration = JSON.parse(readFileSync(new URL('./intraday_candidate_registration_20261116.json', import.meta.url)));
const gate = registration.validation.developmentExclusionGate;
const dayPattern = /^\d{4}-\d{2}-\d{2}$/;
const key = (row) => `${row.symbol}|${row.date}`;
const fail = (reason) => ({ decision: 'HALT_UNKNOWN', eligible: false, reason });

// This function is deliberately fail-closed: a private registry cannot be
// self-certified by a synthetic test or a GitHub Actions run.
function checkEligibility({ registry, proposed, registryIndependentlyComplete = false, provenanceReviewed = false, testOnlyGateStatus = gate.status }) {
  if (testOnlyGateStatus !== 'UNRESOLVED_FAIL_CLOSED' && testOnlyGateStatus !== 'FROZEN_VERIFIED') return fail('UNKNOWN_GATE_STATUS');
  if (!registryIndependentlyComplete || !provenanceReviewed || testOnlyGateStatus !== 'FROZEN_VERIFIED') return fail('REGISTRY_NOT_INDEPENDENTLY_FROZEN');
  if (!Array.isArray(registry) || !registry.length || !Array.isArray(proposed) || !proposed.length) return fail('MISSING_REGISTRY_OR_HOLDOUT');
  const known = new Set();
  for (const row of registry) {
    if (!row || typeof row.symbol !== 'string' || !row.symbol || !dayPattern.test(row.date ?? '') || !Number.isFinite(Date.parse(row.date + 'T00:00:00Z'))) return fail('INVALID_DEVELOPMENT_ROW');
    const k = key(row);
    if (known.has(k)) return fail('DUPLICATE_DEVELOPMENT_ROW');
    known.add(k);
  }
  const selected = new Set();
  const days = new Set();
  const regimes = new Set();
  for (const row of proposed) {
    if (!row || typeof row.symbol !== 'string' || !row.symbol || !dayPattern.test(row.date ?? '') || !Number.isFinite(Date.parse(row.date + 'T00:00:00Z')) || typeof row.regime !== 'string' || !row.regime) return fail('INVALID_HOLDOUT_ROW');
    const k = key(row);
    if (selected.has(k)) return fail('DUPLICATE_HOLDOUT_ROW');
    if (known.has(k)) return fail('DEVELOPMENT_HOLDOUT_OVERLAP');
    selected.add(k);
    days.add(row.date);
    regimes.add(row.regime);
  }
  if (days.size < registration.validation.minUntouchedUniqueTradingDays) return fail('INSUFFICIENT_DISTINCT_DAYS');
  if (regimes.size < registration.validation.minVerifiedRegimes) return fail('INSUFFICIENT_REGIMES');
  return { decision: 'ELIGIBLE_FOR_SEPARATE_DATA_RIGHTS_AND_INTEGRITY_REVIEW', eligible: true };
}

const fictionalRegistry = [{symbol:'FICTIONAL',date:'2020-01-01'}];
const fictionalHoldout = Array.from({length:60}, (_,i)=>({
  symbol:'FICTIONAL', date:new Date(Date.UTC(2021,0,1+i)).toISOString().slice(0,10),
  regime:['A','B','C'][i%3]
}));
const eligibleInputs = {registry:fictionalRegistry,proposed:fictionalHoldout,registryIndependentlyComplete:true,provenanceReviewed:true};

test('current proposal cannot self-certify eligibility even with fabricated complete-looking data', () => {
  assert.equal(checkEligibility(eligibleInputs).reason,'REGISTRY_NOT_INDEPENDENTLY_FROZEN');
});
test('missing registry fails closed', () => {
  assert.equal(checkEligibility({...eligibleInputs,registry:[]}).eligible,false);
});
test('unreviewed provenance fails closed', () => {
  assert.equal(checkEligibility({...eligibleInputs,provenanceReviewed:false}).eligible,false);
});
test('unresolved proposal cannot pass an overlap by pretending review is complete', () => {
  const proposed=[...fictionalHoldout,{symbol:'FICTIONAL',date:'2020-01-01',regime:'A'}];
  assert.equal(checkEligibility({...eligibleInputs,proposed,testOnlyGateStatus:'FROZEN_VERIFIED'}).reason,'DEVELOPMENT_HOLDOUT_OVERLAP');
});
test('guard has no broker route and default remains NO_TRADE', () => {
  assert.equal(registration.constraints.brokers,'NO_BROKER_ORDER_ROUTE');
  assert.equal(registration.constraints.defaultDecision,'NO_TRADE');
  assert.equal(registration.capital.virtualInr,10000);
});

test('fictional frozen-registry scenario rejects duplicate holdout symbol-days', () => {
  assert.equal(checkEligibility({...eligibleInputs,proposed:[...fictionalHoldout,fictionalHoldout[0]],testOnlyGateStatus:'FROZEN_VERIFIED'}).reason,'DUPLICATE_HOLDOUT_ROW');
});
test('fictional frozen-registry scenario rejects fewer than 60 distinct days', () => {
  assert.equal(checkEligibility({...eligibleInputs,proposed:fictionalHoldout.slice(0,59),testOnlyGateStatus:'FROZEN_VERIFIED'}).reason,'INSUFFICIENT_DISTINCT_DAYS');
});
test('fictional frozen-registry scenario rejects fewer than three regimes', () => {
  assert.equal(checkEligibility({...eligibleInputs,proposed:fictionalHoldout.map(x=>({...x,regime:'A'})),testOnlyGateStatus:'FROZEN_VERIFIED'}).reason,'INSUFFICIENT_REGIMES');
});
test('fictional frozen-registry scenario can reach eligibility branch, never actual authorization', () => {
  assert.equal(checkEligibility({...eligibleInputs,testOnlyGateStatus:'FROZEN_VERIFIED'}).decision,'ELIGIBLE_FOR_SEPARATE_DATA_RIGHTS_AND_INTEGRITY_REVIEW');
});
