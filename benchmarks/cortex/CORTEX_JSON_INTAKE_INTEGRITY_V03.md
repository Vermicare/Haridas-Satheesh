# CORTEX — JSON intake ambiguity and CLI fail-closed regression v0.3

**Date:** 2026-10-25. **Maturity:** Architecture / R&D (unchanged). **Scope:** author-created fictional review packet and invented test-only submissions. **Human reviewer results:** TBD.

## Question and negative control

Does the blinded CORTEX review intake preserve unambiguous evidence when reading JSON from disk and reject malformed packet structure without an uncaught exception?

Nine additive adversarial tests were committed before changing the validator. [Before-fix GitHub Actions #40199073982](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40199073982) ran 69 tests per OS and reproduced **4 failed assertions plus 5 uncaught errors on Ubuntu and Windows**. The original parser silently accepted duplicate JSON members where the last value won, accepted `NaN` and `1e400` in unexamined fields, and the `manifest` command crashed on null/nonobject meeting or archive structures and malformed JSON.

These are **fictional evidence-intake integrity defects**, not a proven security exploit or an external reviewer incident. A passing fixture-specific score is not evidence of semantic accuracy.

## Narrow correction

The stdlib JSON reader now rejects duplicate object members, non-JSON numeric constants, and floats outside finite binary64 range. The command-line entry point reports `input:invalid_json_or_read` and nonzero exit status for invalid files, without echoing private submission contents or paths. Manifest counts are computed only from valid list containers. Existing `validate_packet` issue codes, frozen fixtures, synthetic extractor/evaluator, blinded case/archive SHA-256 pins, and lineage-shift output hash remain unchanged.

**Standards decision:** [IETF RFC 8259 §4](https://www.rfc-editor.org/rfc/rfc8259#section-4) says JSON member names **SHOULD** be unique and warns of inconsistent duplicate-member behavior. §6 disallows literal `NaN`/`Infinity`; it permits syntactic `1e400` but warns of numeric interoperability limits. This intake intentionally adopts a **stricter finite-number profile** for reproducibility; it is not a claim that RFC 8259 universally forbids `1e400`.

## Reproduction and evidence

- Corrected source: [blind_review_preflight.py](blind_review_preflight.py), Git blob `e069d485bbcf9e1df63325f978352b8796f55fe9`.
- Tests: [test_blind_review_preflight.py](test_blind_review_preflight.py), Git blob `e183cc1817682f35cc0af869bebb48b6ac5d1a39`; **9 new controls**.
- Before-fix commit `3e8c52036beee17cbc408c545bf8271d4ad6612a`: 69 executed, **4 failures + 5 errors per OS**.
- Corrected commit `7e3686b86d612628469890eaf74b39666ead621f`: [GitHub Actions #40199139641](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40199139641) **69/69 passed on Ubuntu and 69/69 on Windows**. Both jobs also passed existing raw-byte packet SHA-256 assertions and frozen lineage-shift output SHA-256 assertion.
- Runner: GitHub-hosted `ubuntu-latest` and `windows-latest`; `actions/setup-python@v5` requested Python 3.13; stdlib-only tests. Exact patch versions and runner image revisions: **TBD**. Seeds: N/A for the nine fixed test fixtures. Real meetings, reviewers, hardware, semantic accuracy and correction-time measurements: **TBD**.

Reproduce from `benchmarks/cortex`:

```bash
python -B -m unittest -v fixture_integrity_preflight.py test_lineage_shift.py test_supersession_graph.py test_blind_review_preflight.py
python -B blind_review_preflight.py manifest blind_case_20261024.json blind_archive_20261024.json
```

**Decision:** keep the fail-closed correction and tests; **no stage change, release, deployment, or claim of reviewer validation**. The largest remaining gap is independent blinded annotation of the frozen fictional case, source-span/lineage adjudication, and actual correction time compared fairly with manual structured notes (Issue #12). Reframe CORTEX as provenance/lineage tooling if unsupported governance records or reviewer burden exceed manual notes.

**Four lenses:** hiring manager—verifiable defect/fix with bounded claims; technical reviewer—before/after cross-platform CI and source pins; innovation leader—negative evidence preserved; founder—no customer, product, commercial or patentability claim. Private reviewer records and outreach tracking stay off GitHub.
