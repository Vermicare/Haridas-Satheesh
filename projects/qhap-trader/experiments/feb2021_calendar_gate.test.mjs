// Research-only conservative calendar gate. Does not certify exchange data.
import test from 'node:test';
import assert from 'node:assert/strict';

export const FEB2021_CANDIDATES = Object.freeze(Array.from({length:28}, (_,i)=>`2021-02-${String(i+1).padStart(2,'0')}`).filter(d=>![0,6].includes(new Date(`${d}T00:00:00Z`).getUTCDay())));
export const FEB2021_INTERRUPTION = '2021-02-24';

export function inspectFebruary2021Manifest({sessions, exceptionDays = []}) {
  if (!Array.isArray(sessions) || !Array.isArray(exceptionDays)) return {state:'HALT_UNKNOWN', reason:'INVALID_MANIFEST'};
  if (sessions.some(d=>typeof d!=='string') || exceptionDays.some(d=>typeof d!=='string')) return {state:'HALT_UNKNOWN',reason:'INVALID_DATE_TYPE'};
  if (new Set(sessions).size!==sessions.length || new Set(exceptionDays).size!==exceptionDays.length) return {state:'HALT_UNKNOWN',reason:'DUPLICATE_DATE'};
  const expected = new Set(FEB2021_CANDIDATES);
  if (sessions.some(d=>!expected.has(d))) return {state:'HALT_UNKNOWN',reason:'UNEXPECTED_SESSION'};
  if (FEB2021_CANDIDATES.some(d=>!sessions.includes(d))) return {state:'HALT_UNKNOWN',reason:'MISSING_EXPECTED_SESSION'};
  if (exceptionDays.some(d=>!expected.has(d))) return {state:'HALT_UNKNOWN',reason:'UNKNOWN_EXCEPTION'};
  if (!exceptionDays.includes(FEB2021_INTERRUPTION)) return {state:'HALT_UNKNOWN',reason:'UNFLAGGED_INTERRUPTION'};
  // Even matching candidate dates cannot authenticate NSE amendments, minute data, rights or reopening phases.
  return {state:'HALT_UNKNOWN',reason:'EXCEPTION_PHASES_AND_SOURCE_PROVENANCE_UNVERIFIED',candidateDays:sessions.length};
}

test('calendar enumerates exactly 20 weekday candidates including Feb 2, 19 and 24',()=>{
  assert.equal(FEB2021_CANDIDATES.length,20);
  for(const d of ['2021-02-02','2021-02-19','2021-02-24']) assert.ok(FEB2021_CANDIDATES.includes(d));
});
test('complete candidate calendar still halts: reopening and provenance unknown',()=>{
  assert.deepEqual(inspectFebruary2021Manifest({sessions:[...FEB2021_CANDIDATES],exceptionDays:['2021-02-24']}),{state:'HALT_UNKNOWN',reason:'EXCEPTION_PHASES_AND_SOURCE_PROVENANCE_UNVERIFIED',candidateDays:20});
});
test('wrongly omitted Feb 2 fails closed',()=>assert.equal(inspectFebruary2021Manifest({sessions:FEB2021_CANDIDATES.filter(d=>d!=='2021-02-02'),exceptionDays:['2021-02-24']}).reason,'MISSING_EXPECTED_SESSION'));
test('Feb 19 settlement holiday cannot be omitted from trading calendar',()=>assert.equal(inspectFebruary2021Manifest({sessions:FEB2021_CANDIDATES.filter(d=>d!=='2021-02-19'),exceptionDays:['2021-02-24']}).reason,'MISSING_EXPECTED_SESSION'));
test('Feb 24 unflagged interruption halts',()=>assert.equal(inspectFebruary2021Manifest({sessions:[...FEB2021_CANDIDATES]}).reason,'UNFLAGGED_INTERRUPTION'));
test('Feb 24 cannot be excluded as a full-day holiday',()=>assert.equal(inspectFebruary2021Manifest({sessions:FEB2021_CANDIDATES.filter(d=>d!=='2021-02-24'),exceptionDays:['2021-02-24']}).reason,'MISSING_EXPECTED_SESSION'));
test('duplicate session halts',()=>assert.equal(inspectFebruary2021Manifest({sessions:[...FEB2021_CANDIDATES,'2021-02-02'],exceptionDays:['2021-02-24']}).reason,'DUPLICATE_DATE'));
test('unexpected extra session halts',()=>assert.equal(inspectFebruary2021Manifest({sessions:[...FEB2021_CANDIDATES,'2021-02-28'],exceptionDays:['2021-02-24']}).reason,'UNEXPECTED_SESSION'));
test('invalid manifest halts',()=>assert.equal(inspectFebruary2021Manifest({sessions:null}).reason,'INVALID_MANIFEST'));
