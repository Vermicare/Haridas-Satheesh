# CORTEX — PROV-O synthetic lineage integrity v0.2

**2026-10-26 | Architecture / R&D | Fictional ground-truth mapping only | No external review**

## Decision-changing negative controls

The v0.1 mapper accepted malformed author-created fictional ground truth that could compromise the interpretability of its provenance graph:

1. A **current decision reused historical decision ID H0** (with no supersession field). The mapper emitted **two JSON-LD nodes with the same `@id`**, one derived from an archive and another from an utterance. Consumers could silently merge competing provenance.
2. A negative example cited an **unknown utterance**, or an **empty, duplicate, string-typed, or malformed negative-source collection**. The mapper failed to validate the negative evidence that determines which utterances must not become governance facts.

Six additive regression tests were run against the original exact-source Git blob `05a253e64ac26fb0cb8e3fb66c26207a62201f72`: **5 assertion failures and 1 error** (local CPython 3.13.5/Linux). These are synthetic software-validation failures, not observed real organizational failures. No hosted before-fix CI run is claimed.

## Narrow correction

- Reject current decision IDs colliding with historical decision IDs before emitting a graph node.
- Require a list of negative examples, each with a nonempty list of valid, distinct utterance references; reject unknown/duplicate/malformed sources.
- Preserve the frozen baseline, original evaluator, independent fictional fixture, `cortex:supersedes` relation, and all preexisting graph semantics.

**Local reproducibility:** `python -B -m unittest -q test_prov_o_mapping_v01.py` passed **19/19** in each of two separate clean temporary directories (Python 3.13.5, Linux, standard library). Running `python -B prov_o_mapping_v01.py independent_scenario_v03.json` produced identical **2,129-byte** stdout with SHA-256 `e5332353950dadc47ebf66c366bb5e5d929b9d1bb29296003cc4b92f4f89dea5` in both runs. Source/test/input were byte-matched to their Git blob identities:

| Artifact | Git blob SHA |
| --- | --- |
| `prov_o_mapping_v01.py` corrected | `7698114b452384975617cdd7f0e4ba1187f11661` |
| `test_prov_o_mapping_v01.py` expanded | `fb7833a538563bf00d4ae46b64a2303b5fd70e83` |
| `independent_scenario_v03.json` unchanged | `4622df5782c1f67ff1c80a78723d85f753c9f269` |

GitHub Actions **latest-head Ubuntu/Windows verification: TBD** until a matching completed run is inspected. Local execution does not substitute for hosted CI.

## Limits and next experiment

This is **referential integrity of fictional ground truth**, not authenticated meeting provenance, RDF/OWL conformance, model extraction accuracy, independent annotation, or demonstrated human review savings. The mapper can still faithfully represent author-created fictional assertions that are semantically false. No maturity change or release is justified.

**Next evidence gate:** [Issue #12](https://github.com/Vermicare/Haridas-Satheesh/issues/12) — independently annotate an unseen fictional meeting and archive, freeze labels before extraction, then measure correction burden against manual structured notes. Reframe if unsupported governance records or correction time outweigh manual work.
