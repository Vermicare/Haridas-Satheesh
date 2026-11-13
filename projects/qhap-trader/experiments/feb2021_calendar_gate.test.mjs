/**
 * QHAP-TRADER — provisional FEB 2021 calendar integrity checks (test only).
 * NSE official original 2021 cash-segment holiday circular lists no Feb dates:
 * https://archives.nseindia.com/content/circulars/CMTR46623.pdf
 * SEBI documents interrupted NSE cash market 24 Feb 2021:
 * https://www.sebi.gov.in/media/press-releases/feb-2021/trading-halt-at-nse-on-february-24-2021_49287.html
 *
 * This is NOT a full/amended exchange calendar or market-data source and
 * cannot resolve actual execution phases, licensed source bytes or fills.
 */
import test from 'node:test';
import assert from 'node:assert/strict';

const DATE_START='2021-02-';
export const PROVISIONAL_FEB2021_WEEKDAYS=Object.freeze(
  Array.from({length:28},(_,i)=>DATE_START+String(i+1).padStart(2,'0'))
    .filter(date=>![0,6].includes(new Date(date+'T00:00:00Z').getUTCDay()))
);
export const INTERRUPTED_SESSION='2021-02-24';
const isArr=a=>Array.isArray(a)&&a.every(v=>typeof v==='string');
function halt(reason,extra={}){
  return Object.freeze({
    status:'HALT_UNKNOWN',
    reason,
    exchangeSessionCalendarIndependentlyCertified:false,
    uninterruptedExecutionPhasesVerified:false,
    sourceDataUseRightsVerified:false,
    canReportCertifiedBacktestProfit:false,
    ...extra
  });
}
export function inspectProvisionalFebruary2021Manifest(input){
  if(input===null||typeof input!=='object'||Array.isArray(input)||
    Object.keys(input).length!==2||
    !Object.hasOwn(input,'sessions')||
    !Object.hasOwn(input,'exceptionDays')||
    !isArr(input.sessions)||!isArr(input.exceptionDays))
    return halt('INVALID_MANIFEST_SHAPE');
  const {sessions,exceptionDays}=input;
  if(new Set(sessions).size!==sessions.length||
     new Set(exceptionDays).size!==exceptionDays.length)
    return halt('DUPLICATE_DATE');
  const candidates=new Set(PROVISIONAL_FEB2021_WEEKDAYS);
  if(sessions.some(d=>!candidates.has(d)))
    return halt('UNEXPECTED_SESSION_DATE');
  if(exceptionDays.some(d=>!candidates.has(d)))
    return halt('UNKNOWN_EXCEPTION_DATE');
  const missing=PROVISIONAL_FEB2021_WEEKDAYS.filter(d=>!sessions.includes(d));
  if(missing.length)
    return halt('MISSING_EXPECTED_WEEKDAY',{missingDays:missing});
  if(!exceptionDays.includes(INTERRUPTED_SESSION))
    return halt('UNFLAGGED_INTERRUPTED_SESSION');
  if(exceptionDays.some(d=>!sessions.includes(d)))
    return halt('EXCEPTION_WITHOUT_SESSION');
  // Even matching a provisional annual list cannot prove exchange session
  // amendments, exceptional reopening phases, vendor coverage or price rights.
  return halt('OUTAGE_PHASES_AND_SOURCE_PROVENANCE_UNVERIFIED',{
    provisionalWeekdayCandidateCount:sessions.length,
    statusIsNotTradingApproval:true
  });
}

const all=()=>[...PROVISIONAL_FEB2021_WEEKDAYS];
const inspect=(sessions,exceptionDays=[INTERRUPTED_SESSION])=>
  inspectProvisionalFebruary2021Manifest({sessions,exceptionDays});

test('Feb 2021 original NSE schedule yields 20 provisional weekday candidates',()=>{
  assert.equal(PROVISIONAL_FEB2021_WEEKDAYS.length,20);
  for(const d of ['2021-02-02','2021-02-19',INTERRUPTED_SESSION])
    assert.ok(PROVISIONAL_FEB2021_WEEKDAYS.includes(d));
});
test('even all candidate days with flagged outage never certify true source',()=>{
  const r=inspect(all());
  assert.equal(r.status,'HALT_UNKNOWN');
  assert.equal(r.reason,'OUTAGE_PHASES_AND_SOURCE_PROVENANCE_UNVERIFIED');
  assert.equal(r.provisionalWeekdayCandidateCount,20);
  assert.equal(r.canReportCertifiedBacktestProfit,false);
  assert.equal(r.exchangeSessionCalendarIndependentlyCertified,false);
});
test('February 2 cannot vanish silently from a candidate calendar',()=>{
  const r=inspect(all().filter(x=>x!=='2021-02-02'));
  assert.equal(r.reason,'MISSING_EXPECTED_WEEKDAY');
  assert.deepEqual(r.missingDays,['2021-02-02']);
});
test('February 19 cannot be incorrectly removed as a cash trading holiday',()=>{
  const r=inspect(all().filter(x=>x!=='2021-02-19'));
  assert.equal(r.reason,'MISSING_EXPECTED_WEEKDAY');
  assert.deepEqual(r.missingDays,['2021-02-19']);
});
test('February 24 interrupted session missing is not a holiday',()=>{
  const r=inspect(all().filter(x=>x!==INTERRUPTED_SESSION));
  assert.equal(r.reason,'MISSING_EXPECTED_WEEKDAY');
  assert.deepEqual(r.missingDays,[INTERRUPTED_SESSION]);
});
test('February 24 included but not flagged is rejected',()=>{
  assert.equal(inspect(all(),[]).reason,'UNFLAGGED_INTERRUPTED_SESSION');
});
test('a fully declared month with fake extra February 28 fails',()=>{
  assert.equal(inspect([...all(),'2021-02-28']).reason,'UNEXPECTED_SESSION_DATE');
});
test('an unexpected exception day or duplicate exception fails closed',()=>{
  assert.equal(inspect(all(),['2021-02-29']).reason,'UNKNOWN_EXCEPTION_DATE');
  assert.equal(inspect(all(),[INTERRUPTED_SESSION,INTERRUPTED_SESSION]).reason,
    'DUPLICATE_DATE');
});
test('duplicate weekday source date fails closed',()=>{
  assert.equal(inspect([...all(),'2021-02-02']).reason,'DUPLICATE_DATE');
});
test('malformed manifests, secret/unrecognized keys and null fail closed',()=>{
  for(const input of [null,[],{},'calendar',
    {sessions:all()},
    {sessions:all(),exceptionDays:[INTERRUPTED_SESSION],accessToken:'secret'},
    {sessions:all(),exceptionDays:23},
    {sessions:[0],exceptionDays:[]}]){
    const r=inspectProvisionalFebruary2021Manifest(input);
    assert.equal(r.reason,'INVALID_MANIFEST_SHAPE');
    assert.equal(r.canReportCertifiedBacktestProfit,false);
  }
});
