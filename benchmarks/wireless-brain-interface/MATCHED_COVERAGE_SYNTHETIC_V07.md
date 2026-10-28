# WBI v0.7 — synthetic matched-coverage drift falsification (preregistered 2026-10-28)

**Stage remains Research / Simulation.** This is a new, separate experiment on the *unmerged* WBI draft branch. It does not modify the frozen `synthetic_evaluator.py`, `synthetic_risk_coverage.csv`, `SYNTHETIC_EVALUATOR.md` or `EXECUTION_RECORD.md`. **No public EEG decoding or clinical validation is claimed.**

## Question and baseline

At exactly matched action coverage, does adding the fictional drift feature reduce incorrect actions relative to confidence-only abstention? The original frozen synthetic record has **not** established superiority, because its compared operating points have different coverage. The new test is a **falsification probe**, not a retroactive reinterpretation of that record.

## Frozen design before result generation

- Use the unchanged `synthetic_evaluator.fixture`, `pred_conf`, and `Row` definitions. Each replicate draws a separate deterministic calibration fixture and a separate held-out test fixture of 240 fictional rows; 40% of the rows are *not* to be assumed drifted (the fixture defines its own drift segments).
- Exactly **120/240 (50%)** actions for *each* policy, ranked with stable input-index tie breaking. No threshold or coverage is selected using test labels.
- Baseline ranking score: decoder confidence. Candidate ranking score: confidence minus `lambda × drift`, with `lambda` selected on calibration only from the **predeclared** grid `[0.0, 0.1, 0.25, 0.5, 1.0]` to minimize calibration incorrect-action count at 120 actions. On ties, choose the smallest lambda. Lambda 0 is explicitly eligible, so the drift method can decline the extra feature.
- Evaluate fixed calibration-derived lambda on held-out test at 120 actions. Report raw incorrect counts, exact-coverage risk and paired incorrect-count delta (candidate minus baseline). **Negative delta favors the candidate; zero/positive does not.**
- Stress test: deterministically permute **test drift values only** while preserving confidence, labels and marginal drift values. Do **not** recalibrate lambda. This is a synthetic distribution-shift negative control, not a real EEG perturbation.
- Replicates: 12 deterministic calibration/test seed pairs derived from the original seeds with increments of 1009. The original seeds are included as replicate 0. Report all replicate results, wins/ties/losses, and arithmetic aggregate, without post-hoc subset selection or claims of statistical significance.
- Contract tests must prove equal coverage, deterministic ranking, unchanged decisions when test labels mutate, zero-weight baseline equivalence, and no access to test labels in calibration.
- Output JSON is **synthetic aggregate only**, with runtime, code/source provenance and SHA-256 of the unchanged original evaluator source. Unknown hardware, public EEG, external-review and clinical metrics remain `TBD`.

## Decision rule

Do **not** advance maturity on any synthetic outcome. If the candidate loses or ties across most held-out replicates, **reframe** the synthetic drift feature as unproven rather than implying safety. Even if it wins, require a separately preregistered, subject/session-held-out public EEG benchmark at matched coverage before any real-data claim. No patents, users, pilots, safety or product claims.

## Four-lens review

Hiring manager: reproducible negative-result discipline. Technical reviewer: calibration/test isolation, exact-coverage paired comparison, drift permutation. Innovation leader: a falsifiable claim rather than architecture promotion. Founder: practical safety, user value and independent review **TBD**.
