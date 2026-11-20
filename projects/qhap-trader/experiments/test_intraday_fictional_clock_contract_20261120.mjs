// Offline fictional clock contract tests. No market data, network, brokerage or orders.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const registration = JSON.parse(readFileSync(new URL('./intraday_candidate_registration_20261116.json', import.meta.url), 'utf8'));
const minute = (s) => {
  assert.match(s, /^\\d{2}:\\d{2}$/);
  const [h,m]=s.split(':').map(Number);
  assert.ok(h>=0&&h<24&&m>=0&&m<60);
  return 60*h+m;
};
const stamp = (n) => String(Math.floor(n/60)).padStart(2,'0')+':'+String(n%60).padStart(2,'0');
function decisionGate(decision, lastObservedBarStart, proposedFillBarStart) {
  const d=minute(decision), observed=minute(lastObservedBarStart), fill=minute(proposedFillBarStart);
  // A minute-opening stamped bar is not observable until the following minute.
  if (observed+1>d) return 'HALT_UNKNOWN';
  // A full-minute execution separation follows the decision; no same-bar fill.
  if (fill<d+1) return 'HALT_UNKNOWN';
  if (d===minute(registration.clock.forcedExitDecision)) {
    if (fill>minute(registration.clock.latestPermittedExitFillBarStart)) return 'HALT_UNKNOWN';
    if (fill+1>minute(registration.clock.forcedFlatDeadline)) return 'HALT_UNKNOWN';
  }
  return 'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL';
}
test('fixed registered exit clock is conservative and independent of closing auction',()=>{
  assert.equal(registration.clock.forcedExitDecision,'14:55');
  assert.equal(registration.clock.latestPermittedExitFillBarStart,'14:59');
  assert.equal(registration.clock.forcedFlatDeadline,'15:00');
  assert.equal(registration.clock.unknownExitPolicy,'HALT_UNKNOWN_NO_ASSUMED_FLAT');
  assert.equal(registration.constraints.brokers,'NO_BROKER_ORDER_ROUTE');
  assert.equal(registration.constraints.defaultDecision,'NO_TRADE');
});
test('fictional completed 14:54 observation permits later hypothetical 14:56 through 14:59 only',()=>{
  for(let t=minute('14:56');t<=minute('14:59');t++)
    assert.equal(decisionGate('14:55','14:54',stamp(t)),'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL');
  for(const t of ['14:54','14:55','15:00','15:01'])
    assert.equal(decisionGate('14:55','14:54',t),'HALT_UNKNOWN');
});
test('fictional lookahead, future observation and same-minute execution fail closed',()=>{
  assert.equal(decisionGate('14:55','14:55','14:56'),'HALT_UNKNOWN');
  assert.equal(decisionGate('09:45','09:45','09:46'),'HALT_UNKNOWN');
  assert.equal(decisionGate('09:45','09:44','09:45'),'HALT_UNKNOWN');
  assert.equal(decisionGate('09:45','09:44','09:46'),'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL');
});
test('registration preserves 09:15 opening bar and complete regular source coverage',()=>{
  assert.equal(registration.data.regularStart,'09:15');
  assert.equal(registration.data.regularLastBarStart,'15:29');
  assert.equal(registration.data.expectedBars,375);
  assert.equal(minute('15:29')-minute('09:15')+1,375);
  assert.equal(registration.data.openingMinuteMandatory,true);
  assert.equal(registration.data.historyRequiredCompleteSessions,14);
});
test('eligibility never means a fill, especially for partial/unknown exits',()=>{
  assert.equal(registration.constraints.ambiguousExecution,'HALT_UNKNOWN');
  assert.equal(registration.clock.unknownExitPolicy,'HALT_UNKNOWN_NO_ASSUMED_FLAT');
  assert.equal(registration.validation.unresolvedRightsOrFees,'REJECT');
});
