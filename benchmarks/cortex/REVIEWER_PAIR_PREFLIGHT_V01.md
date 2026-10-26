# CORTEX fictional two-reviewer pair gate v0.1

**Date:** 2026-10-26. **Stage:** Architecture / R&D. **Study:** not started; real reviewers: TBD.

## Hypothesis / failure mode

A pair of individually valid fictional annotations may still be unusable as a blinded comparison if the two submissions reuse one pseudonym, use different methods, refer to different case bytes, omit archived predecessor citations, or claim a zero-second completed review. Existing single-submission validation does not establish pair-level comparability.

## Reproducible artifact

- `reviewer_pair_preflight_v01.py`: Python 3.13 stdlib-only, read-only CLI.
- `test_reviewer_pair_preflight_v01.py`: 14 fictional adversarial tests, including a mismatched packet, duplicate pseudonym, missing citation, wrong method, invalid time, bad source, multiset overlap and privacy-safe error output.
- Frozen case SHA-256: `f6357accbd87e11ffcaf1a2d39a085b0611719de6953cd3e4789ccacbb96344d`.
- Frozen archive SHA-256: `897ba394a392ffd63b5561500e5350573570c835fc699c0fd453148d4e3c8046`.
- Dependencies: stdlib; existing v0.1 intake and v0.4 archive citation gate.
- Test command from `benchmarks/cortex`: `python -B -m unittest -v test_reviewer_pair_preflight_v01.py`.
- Private future use: `python -B reviewer_pair_preflight_v01.py check blind_case_20261024.json blind_archive_20261024.json /outside-repo/private-a.json /outside-repo/private-b.json`.

No private submissions, reviewer codes, raw annotations or contact records are stored in this repository. CLI reports aggregate source-signature counts, not source text. Avoid saving raw completed submissions inside any Git checkout or workflow artifacts. A pseudonym difference does **not** establish independent humans; elapsed seconds are self-reported, not verified. A shared source signature does **not** establish semantic agreement.

## Negative controls and acceptance

Fail closed on altered case/archive hashes, invalid single-reviewer or archive-citation inputs, same pseudonym, non-manual method, zero/invalid duration, unexpected correction duration, and malformed/oversized JSON. For valid *fabricated* pairs, report per-kind counts and exact source-signature multiset intersection only. Do not label those counts accuracy, consensus or adjudication.

**Results:** local isolated tests with stubbed predecessor validators: 14/14 passed on Python (environment details not preserved); full repository-integrated hosted Ubuntu/Windows CI: **TBD until inspected**. Human review, label agreement, extraction accuracy, correction time, independent annotation and deployment: **TBD**.

**Decision:** maintain stage. Next: obtain voluntary independent annotations privately, adjudicate source-span disagreements, freeze gold, then compare general extraction against fairly timed manual notes. Reframe as provenance-only tooling if unsupported facts or correction burden exceed manual notes.
