# Frozen WBI synthetic evaluator — independent cross-platform reproduction (2026-10-24)

**Evidence scope:** deterministic fictional calibration/test data only. This does **not** validate EEG decoding, human intent, clinical safety, hardware or deployment. Maturity stays **Research / Simulation**.

## Question and fixed provenance

Can the exact evaluator already committed to `main` be executed unchanged in independent Linux and Windows CI environments, producing the same frozen thresholds, synthetic held-out metrics and byte-identical risk–coverage CSV?

- Original evaluator: [`synthetic_evaluator.py`](synthetic_evaluator.py), Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9`.
- Existing stronger baseline: [`EXECUTION_RECORD.md`](EXECUTION_RECORD.md), 2026-09-28, two same-runtime runs.
- Frozen output SHA-256 from that record: `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`.
- Verification implementation: [`verify_frozen_execution.py`](verify_frozen_execution.py); no modifications to original evaluator, its thresholds, fixture, CSV or earlier execution record.
- Runner: [least-privilege Linux/Windows CI](../../.github/workflows/wbi-frozen-synthetic-repro.yml); CPython 3.13.16, Python standard library only.
- New verifier checks the Git blob, executes two isolated-directory runs per OS, checks the pinned CSV digest, frozen thresholds and held-out summary, and requires identical normalized stdout.

## Verified CI evidence

[GitHub Actions run #40059209875](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40059209875) **passed both Linux and Windows jobs** on 2026-10-24.

| Independent environment | Frozen source Git blob | CSV SHA-256 | Normalized stdout SHA-256 | Isolated reruns | Result |
|---|---|---|---|---:|---|
| Ubuntu / CPython 3.13.16 | `2becec81a8002cc5ff2f445889b7617baf9937b9` | `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a` | `39014b30200d6ddd20b7791ba3e70c48f17770a65a833d365af30b04b7a55c91` | 2 | PASS |
| Windows / CPython 3.13.16 | `2becec81a8002cc5ff2f445889b7617baf9937b9` | `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a` | `39014b30200d6ddd20b7791ba3e70c48f17770a65a833d365af30b04b7a55c91` | 2 | PASS |

The independent local Linux reproduction (CPython 3.13.5) also matched the same CSV and stdout digests. A source-tampering negative control was rejected before execution.

## Failures retained and correction

- [CI #40059082032](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40059082032): Windows checkout translated LF source to CRLF, changing the working-tree Git-blob calculation. **Correction:** normalize only checkout line endings, then execute the canonical pinned source bytes.
- [CI #40059163883](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40059163883): Windows subprocess output used a legacy console encoding, causing a UTF-8 decode failure on the synthetic disclaimer's em dash. **Correction:** explicitly set subprocess `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1`.
- Neither correction changes the original evaluator or suppresses metric mismatches. The final verifier fails closed on source, output or threshold differences.

## Decision and next evidence gate

**Cross-platform reproducibility of the frozen synthetic contract is now demonstrated on this draft PR branch**, not merged to `main`. This closes the *environment reproduction* gap in [`SYNTHETIC_EVALUATOR.md`](SYNTHETIC_EVALUATOR.md), but does **not** close the real EEG or comparative-benefit gap.

The earlier [synthetic stress experiment](SYNTHETIC_REGIME_STRESS.md) remains negative/mixed (gate worse in 21 of 42 coverage-comparable fictional operating points, better in 6, tied in 15). **Do not advance maturity.** Next: independent technical review of coverage matching, then preregistered subject/session-separated public EEG comparisons against ungated and confidence-abstention baselines at matched coverage.

**Kill/reframe:** if the drift gate remains dominated by simple confidence abstention under fair public-data comparisons, demote it to an optional diagnostic rather than claim a useful authorization improvement.

Unknown real EEG accuracy, safety, latency, hardware performance, external review and clinical benefit: **TBD**.
