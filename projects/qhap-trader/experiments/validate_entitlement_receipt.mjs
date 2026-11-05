import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

// Research-only structural preflight. NEVER grants a data license or authorizes replay.
export function assessReceipt(receipt) {
  const failures = [];
  if (!receipt || typeof receipt !== 'object' || Array.isArray(receipt)) return { status: 'BLOCKED', failures: ['INVALID_RECEIPT'], replay_authorized: false };
  const required = ['provider', 'instrument_isin', 'product_and_granularity', 'bar_timestamp_timezone_and_construction', 'license_reference_local_only', 'session_calendar_reference', 'corporate_action_reference', 'local_source_sha256'];
  for (const key of required) if (typeof receipt[key] !== 'string' || !receipt[key].trim() || receipt[key].trim().toUpperCase() === 'UNKNOWN') failures.push(`MISSING_${key.toUpperCase()}`);
  if (typeof receipt.local_source_sha256 !== 'string' || !/^[a-f0-9]{64}$/i.test(receipt.local_source_sha256)) failures.push('INVALID_SHA256');
  for (const key of ['research_non_display_permitted', 'retention_permitted']) if (receipt[key] !== true) failures.push(`UNVERIFIED_${key.toUpperCase()}`);
  if (receipt.public_redistribution_permitted !== true && receipt.public_redistribution_permitted !== false) failures.push('UNKNOWN_REDISTRIBUTION_RIGHTS');
  if (!Number.isSafeInteger(receipt.observed_session_count) || receipt.observed_session_count < 60) failures.push('INSUFFICIENT_PROSPECTIVE_SESSIONS');
  // A self-reported receipt is not independent evidence, even when all fields look complete.
  failures.push('INDEPENDENT_ENTITLEMENT_AND_DATA_AUDIT_REQUIRED');
  return { status: 'BLOCKED', failures: [...new Set(failures)], replay_authorized: false };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  if (process.argv.includes('--self-test')) {
    let n = 0;
    const check = (name, receipt, expected) => { const result = assessReceipt(receipt); assert.equal(result.replay_authorized, false, name); assert.equal(result.status, 'BLOCKED', name); if (expected) assert.ok(result.failures.includes(expected), name); n++; };
    check('null', null, 'INVALID_RECEIPT');
    check('empty', {}, 'INVALID_SHA256');
    check('array', [], 'INVALID_RECEIPT');
    check('fake approval', { replay_authorized: true }, 'INDEPENDENT_ENTITLEMENT_AND_DATA_AUDIT_REQUIRED');
    check('unknown rights', { research_non_display_permitted: 'UNKNOWN', retention_permitted: 'UNKNOWN' }, 'UNVERIFIED_RESEARCH_NON_DISPLAY_PERMITTED');
    check('zero days', { observed_session_count: 0 }, 'INSUFFICIENT_PROSPECTIVE_SESSIONS');
    check('negative days', { observed_session_count: -1 }, 'INSUFFICIENT_PROSPECTIVE_SESSIONS');
    check('invalid hash', { local_source_sha256: 'abc' }, 'INVALID_SHA256');
    const complete = Object.fromEntries(['provider', 'instrument_isin', 'product_and_granularity', 'bar_timestamp_timezone_and_construction', 'license_reference_local_only', 'session_calendar_reference', 'corporate_action_reference'].map(k => [k, 'synthetic-not-evidence']));
    Object.assign(complete, { local_source_sha256: 'a'.repeat(64), research_non_display_permitted: true, retention_permitted: true, public_redistribution_permitted: false, observed_session_count: 60, replay_authorized: true });
    check('all self-asserted', complete, 'INDEPENDENT_ENTITLEMENT_AND_DATA_AUDIT_REQUIRED');
    console.log(JSON.stringify({ synthetic_tests_passed: n, synthetic_tests_total: n, replay_authorization_possible: false }));
  } else {
    if (process.argv.length !== 3) { console.error('Usage: node validate_entitlement_receipt.mjs receipt.json | --self-test'); process.exit(2); }
    const result = assessReceipt(JSON.parse(readFileSync(process.argv[2], 'utf8')));
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.replay_authorized ? 0 : 1);
  }
}
