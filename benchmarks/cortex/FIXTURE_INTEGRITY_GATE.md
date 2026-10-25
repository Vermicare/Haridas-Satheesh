# CORTEX — fixture source-reference integrity preflight

**2026-10-23 · Synthetic-only regression evidence · Public maturity unchanged: Architecture / R&D**

This additional preflight tests the *ground-truth fixture*, not model extraction or semantic accuracy. The existing committed evaluator and fixture are unchanged.

## Reproduce

From the repository root:

```bash
python -m unittest -v benchmarks/cortex/fixture_integrity_preflight.py
```

Five standard-library regression tests cover an unresolved historical predecessor, a nonexistent gold source utterance, duplicate gold signatures, nonexistent negative-example sources and colliding object IDs.

The frozen synthetic fixture contains a decision `D2` whose `supersedes` field references `D0`, but the fixture has no D0 decision or historical record. The preflight deliberately **detects**, rather than silently repairs, that unresolved lineage.

The original deterministic baseline can score 1.0 decision F1 and 1.0 lineage on the frozen fixture using exact-match ground truth. Those scores do **not** establish independently verified lineage or real governance effectiveness.

## Why this matters

In a separate local v0.3 evaluation-contract candidate, a deliberately malformed independent fictional fixture could pass the readiness check with an empty prediction when a gold source referred to a nonexistent utterance, or when gold signatures were duplicated. The published preflight adds fixture-side regression coverage for those cases. The local v0.3 candidate is **not** committed here, and this file is not a claim that GitHub CI has reproduced the full local package.

## Evidence boundary

- All utterances and decisions are fictional; no employer or customer data.
- Source-ID existence is necessary, not sufficient, for semantic correctness.
- No human adjudication, review burden, real workflow accuracy, deployment, or external validation measured.
- Original frozen fixture is immutable; any correction to D0 needs a separately versioned fixture and explicit source/adjudication rationale.
- Cross-platform CI and independent review remain **TBD**.

**Next experiment:** independently adjudicate D0 using a versioned fictional historical record, then score an unseen fictional scenario with blinded human source-span review and measured correction minutes.

**Reframe rule:** simplify structured memory if unsupported attributions or reviewer workload erase the benefit over manually maintained governance records.
