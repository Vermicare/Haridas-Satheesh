/**
 * Research-only causal clock guard for proposed NSE intraday candidates.
 * A valid clock is NOT evidence of a market fill, liquidity or data rights.
 * No broker imports, network calls or order routes.
 */
const toMinute = (value) => {
  if (typeof value !== 'string' || !/^[0-9]{2}:[0-9]{2}$/.test(value)) return null;
  const h = Number(value.slice(0,2)), m = Number(value.slice(3,5));
  return h < 24 && m < 60 ? h * 60 + m : null;
};
// Registered 30-minute checkpoints only; no discretionary or hindsight decisions.
const candidateDecisionMinutes = new Set([585,615,645,675,705,735,765,795,825,855,885]);
export function assessIntradayClock({decision, observedBarStart, proposedFillBarStart, kind='ENTRY', confirmedFlat=false}) {
  const d=toMinute(decision), o=toMinute(observedBarStart), f=toMinute(proposedFillBarStart);
  const reject=(reason)=>({status:'HALT_UNKNOWN',reason,confirmedFill:false,realOrderSubmissionPossible:false});
  if ([d,o,f].some(v=>v===null)) return reject('INVALID_CLOCK');
  if (!['ENTRY','EXIT','FORCED_EXIT'].includes(kind)) return reject('INVALID_KIND');
  if (o < 555 || o > 929 || d < 555 || d > 895) return reject('OUTSIDE_RESEARCH_DECISION_SESSION');
  if (o + 1 > d) return reject('UNCOMPLETED_OBSERVATION');
  if (kind !== 'FORCED_EXIT' && !candidateDecisionMinutes.has(d)) return reject('UNREGISTERED_DECISION_TIME');
  if (f < d + 1) return reject('SAME_MINUTE_OR_LOOKAHEAD_FILL');
  if (kind === 'FORCED_EXIT') {
    if (d !== 895) return reject('FORCED_EXIT_DECISION_MUST_BE_1455');
    if (f > 899 || f + 1 > 900) return reject('EXIT_AFTER_FLAT_DEADLINE');
  } else if (kind === 'ENTRY' && f >= 895) return reject('ENTRY_TOO_LATE');
  else if (kind === 'EXIT' && f > 899) return reject('EXIT_AFTER_FLAT_DEADLINE');
  if (confirmedFlat && kind !== 'ENTRY') return reject('INCONSISTENT_FLAT_STATE');
  return {status:'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL',reason:null,
    confirmedFill:false,realOrderSubmissionPossible:false};
}
