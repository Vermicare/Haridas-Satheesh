# CORTEX synthetic governance benchmark v0.1

This package is a **reproducibility harness**, not evidence of general meeting understanding or real-world validation.

## What it tests

The versioned synthetic fixture checks whether a deliberately transparent baseline can preserve:
- explicit approved decisions and supersession;
- committed actions with owner and due date;
- an explicitly stated risk and dependency;
- a conditional escalation;
- negative cases that must not be promoted into decisions/actions.

The fixture and its ground truth are synthetic and public-safe. No employer/client meeting data is used.

## Run locally

Requires Python 3.11+ and no third-party packages.

```bash
cd benchmarks/cortex
python baseline.py fixture.json > result.json
python test_baseline.py
```

Expected v0.1 reference-fixture behavior: the process exits successfully, the five scored extraction groups match the supplied synthetic ground truth, no negative-example source is emitted, and no unsupported `None` field is emitted.

## Evidence boundary

A perfect reference-fixture score **does not** demonstrate generalization. The extractor intentionally keys off the known synthetic fixture structure and utterance identifiers. The current result therefore measures harness determinism and ground-truth comparison only.

Do not describe this benchmark as:
- production accuracy;
- real-world meeting extraction performance;
- an LLM benchmark;
- autonomous governance;
- external validation.

## Next evidence gate

Before any maturity advancement, replace fixture-specific assumptions with content-driven extraction and evaluate on a held-out synthetic/adversarial set that changes names, dates, utterance order, wording and distractors without changing the underlying governance facts.

Predeclare and report:
- per-class precision / recall / F1;
- false promotion rate for proposals and vague suggestions;
- owner/due-date exact-match accuracy;
- supersession/linkage accuracy;
- conditional-follow-up accuracy;
- unsupported-field rate.

Unknown or unmeasured values remain TBD.

## Kill / reframe criterion

If a content-driven baseline cannot preserve high precision on explicit governance facts without excessive false promotion on held-out synthetic cases, keep CORTEX as an architecture/exploration and narrow the extraction scope rather than adding model complexity to protect the concept.
