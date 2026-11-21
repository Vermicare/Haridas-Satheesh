// Fictional-only contract checks. No private bars, prices, tokens or broker routes.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const registration = JSON.parse(readFileSync(new URL('./intraday_candidate_registration_20261116.json', import.meta.url)));
const gate = registration.validation.developmentExclusionGate;
const dayPattern = /^\d{4}-\d{2}-\d{2}$/;
// Strict Gregorian validation: Date.parse may normalize impossible days.
const validCalendarDate = value => {
  if (typeof value !== 'string' || !dayPattern.test(value)) return false;
  const [year,month,day] = value.split('-').map(Number);
  if (year < 1900 || year > 9999 || month < 1 || month > 12 || day < 1) return false;
  const d = new Date(Date.UTC(year,month-1,day));
  return d.getUTCFullYear() === year && d.getUTCMonth() === month-1 && d.getUTCDate() === day;
};
const isWeekday = date => {
  const day = new Date(date + 'T00:00:00Z').getUTCDay();
  return day >= 1 && day <= 5;
};
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
    if (!row || typeof row.symbol !== 'string' || !row.symbol || !validCalendarDate(row.date)) return fail('INVALID_DEVELOPMENT_ROW');
    const k = key(row);
    if (known.has(k)) return fail('DUPLICATE_DEVELOPMENT_ROW');
    known.add(k);
  }
  const selected = new Set();
  const days = new Set();
  const regimes = new Set();
  for (const row of proposed) {
    if (!row || typeof row.symbol !== 'string' || !row.symbol || !validCalendarDate(row.date) || typeof row.regime !== 'string' || !row.regime) return fail('INVALID_HOLDOUT_ROW');
    const k = key(row);
    if (!isWeekday(row.date)) return fail('NON_TRADING_WEEKEND');
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
const fictionalWeekdays = Array.from({length:100}, (_,i) => new Date(Date.UTC(2021,0,1+i)).toISOString().slice(0,10)).filter(isWeekday).slice(0,60);
const fictionalHoldout = fictionalWeekdays.map((date,i)=>({
  symbol:'FICTIONAL', date,
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

test('impossible Gregorian dates fail closed without rejecting leap days', () => {
  assert.equal(checkEligibility({...eligibleInputs,registry:[{symbol:'FICTIONAL',date:'2025-02-30'}],testOnlyGateStatus:'FROZEN_VERIFIED'}).reason,'INVALID_DEVELOPMENT_ROW');
  assert.equal(checkEligibility({...eligibleInputs,proposed:fictionalHoldout.map((row,i)=>i===0?{...row,date:'2025-02-30'}:row),testOnlyGateStatus:'FROZEN_VERIFIED'}).reason,'INVALID_HOLDOUT_ROW');
  assert.equal(checkEligibility({...eligibleInputs,proposed:fictionalHoldout.map((row,i)=>i===0?{...row,date:'2024-02-29'}:row),testOnlyGateStatus:'FROZEN_VERIFIED'}).eligible,true);
});

// Weekend rejection is necessary, not sufficient: holidays and exceptional sessions
// still require independently authenticated exchange calendars before real eligibility.
test('fictional frozen-registry scenario rejects a Saturday despite 60 dates and three regime labels', () => {
  const proposed = fictionalHoldout.map((row,i) => i === 0 ? {...row,date:'2021-01-02'} : row);
  assert.equal(checkEligibility({...eligibleInputs,proposed,testOnlyGateStatus:'FROZEN_VERIFIED'}).reason,'NON_TRADING_WEEKEND');
});
