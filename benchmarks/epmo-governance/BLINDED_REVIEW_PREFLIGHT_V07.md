# EPMO — blinded reviewer-burden preflight v0.7 (fictional)

**2026-10-26 · Research / Simulation · human observations TBD · external actions 0.**

## Decision question

Can an independent reviewer classify fictional approval/execution/correction decisions correctly, and does a structured review aid reduce errors or time compared with manual notes? **No human reviewer has yet been measured.** This is a pre-registered protocol, not a performance result.

## Frozen policy and test design

- Policy oracle: the existing `governance_demo.evaluate` (declared-role simulation; **no authenticated identities**).
- Sixteen fictional candidate-event cases, including valid approval, execution and correction; wrong reviewer/executor; action/scope mismatch; excessive/expired approval; premature/replayed execution; duplicate event; unknown actor; nonmonotonic timestamp; invalid correction.
- Two identical case sets in counterbalanced order: `manual_notes` and `structured_packet`. The same reviewer must not be told the gold labels; order reversal is **not** a substitute for independent random assignment or a washout period.
- Capture one boolean decision and review seconds per case, with a private response file. Keep answer keys, participant records and outreach history **off public GitHub**. The public source itself permits reconstruction of the labels; this is procedural blinding, **not cryptographic blinding**.
- Predeclared metrics: false approvals / gold-negative cases, true-approval recall / gold-positive cases, median seconds/case, total review seconds, case-level disagreements. No imputation for missing responses; record `TBD` until real human responses exist.
- A single fictional scorer's perfect answers or simulated timings are **tests of arithmetic only**, not independent reviewer evidence.

## Acceptance and failure criteria

1. Packet and gold generated deterministically; exactly 16 unique cases, 3 positive and 13 negative; source scenario/context accepted by the frozen policy.
2. Public packet excludes expected labels/reasons; private gold remains separate.
3. Duplicate/missing/unknown decisions, invalid booleans, nonfinite/negative/implausible times, wrong arm/version and duplicate JSON keys fail closed.
4. Execute adversarial unit tests on Linux and Windows; preserve source hashes, commit and CI run provenance.
5. Only claim a reviewer-burden difference after independently collected, consented, privately held human observations with a declared assignment and analysis plan. No participant-level responses on GitHub.

## Known limitations and decision

This protocol does **not** authenticate actors, prove real approval safety, validate human review, or measure employer outcomes. There is no participant recruitment or binding external commitment. The synthetic event-policy oracle is not independent ground truth for real governance. A public deterministic generator cannot conceal its answer key from a reviewer who reads the code.

**Next:** run the packet generator and scoring contract tests in CI, then recruit an independent technical reviewer through a verified professional route only after checking private outreach history; separately complete the identity/time/outbox sandbox gate in [Issue #14](https://github.com/Vermicare/Haridas-Satheesh/issues/14).

**Four lenses:** hiring—reproducible bounded evaluation; technical—challenge oracle validity and leakage; innovation—assess correction-burden hypothesis; founder—no users, ROI, patentability or market validation.
