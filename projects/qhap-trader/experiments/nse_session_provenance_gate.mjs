// Research-only NSE session provenance gate. No market-data or order connectivity.
// A caller must supply independently reviewed, point-in-time evidence; assertions are not certification.
const iso=/^\d{4}-\d{2}-\d{2}$/;
function dateOK(s) {
  if(typeof s!=='string'||!iso.test(s)) return false;
  const [y,m,d]=s.split('-').map(Number);
  if(y<1900||y>9999||m<1||m>12||d<1) return false;
  const v=new Date(Date.UTC(y,m-1,d));
  return v.getUTCFullYear()===y&&v.getUTCMonth()===m-1&&v.getUTCDate()===d;
}
const halt=(reason)=>({accepted:false,decision:'HALT_UNKNOWN',reason,realOrderSubmissionPossible:false});
export function checkSessionProvenance(input) {
  if(!input||!Array.isArray(input.sessions)||!dateOK(input.targetDate)) return halt('INVALID_INPUT');
  if(input.evidenceStatus!=='INDEPENDENTLY_VERIFIED'||input.sourceType!=='NSE_PRIMARY'||typeof input.sourceUrl!=='string'||!/^https:\/\//.test(input.sourceUrl)||!input.reviewedAt||!input.sourceDigest) return halt('UNVERIFIED_EXCHANGE_EVIDENCE');
  if(input.instrumentEvidenceStatus!=='INDEPENDENTLY_VERIFIED'||!input.instrumentId) return halt('UNVERIFIED_INSTRUMENT');
  const sessions=input.sessions;
  if(sessions.length<15||sessions.some(s=>!dateOK(s.date))||new Set(sessions.map(s=>s.date)).size!==sessions.length) return halt('INVALID_SESSION_MANIFEST');
  if(sessions.some((s,i)=>i&&sessions[i-1].date>=s.date)) return halt('UNSORTED_SESSION_MANIFEST');
  const index=sessions.findIndex(s=>s.date===input.targetDate);
  if(index<14) return halt('INSUFFICIENT_IMMEDIATELY_PRECEDING_SESSIONS');
  const target=sessions[index];
  if(target.kind!=='REGULAR'||target.status!=='CONFIRMED') return halt('TARGET_SPECIAL_OR_UNCONFIRMED');
  if(sessions.slice(index-14,index).some(s=>s.kind!=='REGULAR'||s.status!=='CONFIRMED')) return halt('PRIOR_SPECIAL_OR_UNCONFIRMED');
  if(input.dataQualityStatus!=='INDEPENDENTLY_VERIFIED'||input.developmentExclusionStatus!=='INDEPENDENTLY_VERIFIED'||input.regimeStatus!=='INDEPENDENTLY_VERIFIED'||input.costStatus!=='INDEPENDENTLY_VERIFIED'||input.rightsStatus!=='INDEPENDENTLY_VERIFIED') return halt('EXTERNAL_GATES_NOT_VERIFIED');
  // The manifest is required to be independently checked against the complete
  // official exchange calendar; this function cannot independently certify omissions.
  return halt('EXTERNAL_CALENDAR_COMPLETENESS_NOT_INDEPENDENTLY_CERTIFIED');
}
