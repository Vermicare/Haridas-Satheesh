// Offline fictional clock contract tests. No market data, network, brokerage or orders.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const registration = JSON.parse(readFileSync(new URL('./intraday_candidate_registration_20261116.json', import.meta.url), 'utf8'));
const minute = (s) => {
  assert.match(s, /^[0-9]{2}:[0-9]{2}$/);
  const [h,m]=s.split(':').map(Number);
  assert.ok(h>=0&&h<24&&m>=0&&m<60);
  return 60*h+m;
};
import { assessIntradayClock } from './intraday_execution_clock.mjs';
const decisionGate=(decision,observedBarStart,proposedFillBarStart,kind='ENTRY') =>
  assessIntradayClock({decision,observedBarStart,proposedFillBarStart,kind}).status;
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
    assert.equal(decisionGate('14:55','14:54',String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0'),'FORCED_EXIT'),'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL');
  for(const t of ['14:54','14:55','15:00','15:01'])
    assert.equal(decisionGate('14:55','14:54',t,'FORCED_EXIT'),'HALT_UNKNOWN');
});
test('fictional lookahead, future observation and same-minute execution fail closed',()=>{
  assert.equal(decisionGate('14:55','14:55','14:56','FORCED_EXIT'),'HALT_UNKNOWN');
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

test('shared clock rejects invalid times, late entries, and unknown forced-exit timing',()=>{
  assert.equal(decisionGate('09:45','09:44','14:55'),'HALT_UNKNOWN');
  assert.equal(decisionGate('14:54','14:53','14:56','FORCED_EXIT'),'HALT_UNKNOWN');
  assert.equal(decisionGate('14:55','14:54','15:00','FORCED_EXIT'),'HALT_UNKNOWN');
  assert.equal(decisionGate('xx:55','14:54','14:56'),'HALT_UNKNOWN');
  assert.equal(assessIntradayClock({decision:'14:55',observedBarStart:'14:54',proposedFillBarStart:'14:56',kind:'FORCED_EXIT'}).confirmedFill,false);
});

test('off-schedule fictional decisions cannot manufacture candidate eligibility',()=>{
  for(const decision of ['09:25','09:44','10:00','14:54']) {
    const m=Number(decision.slice(0,2))*60+Number(decision.slice(3));
    const stamp=n=>String(Math.floor(n/60)).padStart(2,'0')+':'+String(n%60).padStart(2,'0');
    assert.equal(decisionGate(decision,stamp(m-1),stamp(m+1),'ENTRY'),'HALT_UNKNOWN');
    assert.equal(decisionGate(decision,stamp(m-1),stamp(m+1),'EXIT'),'HALT_UNKNOWN');
  }
  assert.equal(decisionGate('09:45','09:44','09:46','ENTRY'),'ELIGIBLE_TO_SIMULATE_NOT_A_CONFIRMED_FILL');
});
