# CORTEX — malformed reviewer-packet fail-closed regression v0.2 (2026-10-25)

**Stage: Architecture / R&D — unchanged.** This is a fictional-input validation correctness experiment, **not** extraction accuracy, reviewer independence, authenticated history, measured correction burden, or external review.

## Question and hypothesis

Can the existing blinded-review intake reject malformed case/archive JSON as structured errors without uncaught Python exceptions? The existing `validate_packet` flagged malformed structures, but `validate_submission` separately traversed the same untrusted objects using chained `.get()` and set comprehensions without checking container and identifier types.

## Before-fix negative evidence

Eight additional fictional-only adversarial tests were committed **before** the source correction. [GitHub Actions #40155101712](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40155101712), commit `cfc37ace477b4409e0a9c7939285f00580697d39`, ran **60 tests per OS**. **Seven tests errored** on Ubuntu and Windows; the non-list archive-dictionary case returned the expected error without crashing. Observed failures: `AttributeError` for null meeting/nonobject case/nonobject archive and `TypeError` for null record/utterance lists and unhashable fictional IDs. This is an intake reliability defect, **not** a demonstrated exploit, external vulnerability, or real user failure.

## Minimal correction

The corrected `validate_submission` checks case/archive container types, uses empty collections when nested structures are malformed, and admits only string IDs into source and archive lookup sets. It retains `validate_packet` error codes and adds `submission:invalid_packet` when top-level case/archive types are wrong. It does **not** relax hash pins or accept missing provenance. Original frozen CORTEX fixture, evaluator, shifted scenario, blind case/archive, and source SHA-256 pins remain unchanged.

- Source: [blind_review_preflight.py](blind_review_preflight.py), Git blob `a051f57af02802863bd9c536d5372efcefd178a1`.
- Tests: [test_blind_review_preflight.py](test_blind_review_preflight.py), Git blob `39785f659cc64f760af4d977e36918b9c477159f`.
- Corrected commit: `725d40831c96e38a5cb56acdd0e29a95f557fbec`.
- [Corrected GitHub Actions #40155139147](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40155139147): **60/60 tests passed on Ubuntu and Windows**, including eight new fictional negative controls. The frozen blind-case/archive raw-byte checks and synthetic lineage output hash checks also passed.
- Run conditions: GitHub-hosted Ubuntu/Windows, `actions/setup-python@v5` requested Python 3.13, stdlib-only tests. Exact Python patch versions and runner images: **TBD**. Random seed: **not applicable** to these fixed adversarial controls. Physical input, dataset measurements, human review and correction times: **TBD**.

## Reproduce

From `benchmarks/cortex`:

```sh
python -B -m unittest -v test_blind_review_preflight.py
python -B blind_review_preflight.py manifest blind_case_20261024.json blind_archive_20261024.json
```

For full cross-platform regression, run the `cortex-fixture-integrity.yml` workflow. Both source and test blob SHAs and the workflow head commit should be recorded. No raw private submissions or collaborator information are part of this package.

## Decision and boundaries

**Decision:** retain the guard and eight regression tests; **no maturity upgrade**. This closes a deterministic malformed-input exception path, not the larger generalization/reviewer-evidence gap. A malformed packet must return a nonzero status and specific error codes rather than be counted as a successful review. Remaining gap: independently annotated unseen fictional governance case and fair, genuinely timed manual-note versus extractor-correction comparison. Kill/reframe if unsupported decisions or correction burden exceed manual notes, or if a general extractor cannot maintain source lineage.

**Four lenses:** hiring manager—auditable defect/fix evidence; technical reviewer—reproducible before/after cross-platform regression; innovation leader—negative result retained without stage inflation; founder—no deployment, customer, commercial or IP claim.
