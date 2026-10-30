# CORTEX v0.6 — frozen in-memory semantic-mutation boundary

**Date:** 2026-10-30. **Stage:** Architecture / R&D (unchanged). **Scope:** fixed author-created fictional greenhouse governance packet. **Human reviewers:** 0. **Actual organizational records:** 0. **External actions:** 0.

## Evidence question and observed failure mode

The [unchanged v0.5 fixed-case projector](cortex_prov_boundary_v05.py) deliberately checks the presence of fictional source identifiers `b03`, `b07`, `H-11` and `H-12` before emitting a reviewed 14-triple Turtle graph. Its **command-line entrypoint already checks the exact source-file SHA-256 hashes**. Its exposed **in-memory** `render_turtle(case, archive)` helper, however, does not recheck the text or status behind those identifiers.

Adversarial fictional mutations that retain identifiers — changing the public hold from active to revoked, negating checklist supersession, replacing archive text/status, or adding an unreviewed utterance — leave the v0.5 in-memory output **identical**. This is an expected limitation of a static fixed-case projector, but an integration hazard if downstream callers treat the helper as a general semantic mapper. **It is not a bypass of the original hash-pinned v0.5 command-line interface**, and no real governance error was observed.

## Additive safeguard and independent test

The optional [v0.6 checked adapter](cortex_in_memory_boundary_v06.py) first uses v0.5's existing SHA-pinned raw-file reader, then compares canonical UTF-8 JSON representations of the supplied in-memory case/archive against the independently parsed pinned files. It rejects changed text, changed statuses, extra objects, and a Python equality trap (`True == 1`) that plain dictionary comparison could miss. Nonfinite JSON and unreadable paths fail closed with generic errors that do not echo paths. The adapter then delegates unchanged input to the original projector; it does not change v0.5 or generalize it.

[Ten fictional-only regression/integration tests](test_cortex_in_memory_boundary_v06.py) include an **actual read of the repository's two SHA-pinned fictional JSON files**, a successful unchanged projection, and an adversarial source-text mutation that the original helper accepts but the checked adapter rejects.

**Final-code-head hosted verification:** [GitHub Actions #40993096972](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40993096972), commit `afc1dca8f1b232b586f470408bbe6c2f71bc5fda`. Independently inspected **Ubuntu and Windows** job logs: **10/10 v0.6 tests passed on each OS**, including actual pinned-file roundtrip and semantic-mutation rejection. The unchanged v0.5 **14/14** tests and **14-triple** RDFLib parse/fingerprint gate also passed in the same jobs. This is software-only verification, not source authenticity, external review or semantic correctness.

## Reproduce

From `benchmarks/cortex` in branch `research/cortex-fixture-integrity-v04-20261023`:

```sh
python -B -m unittest -v test_cortex_in_memory_boundary_v06.py
python -B -m unittest -v test_cortex_prov_boundary_v05.py
```

The first test module requires only Python standard library and the original v0.5 source plus the two frozen fictional JSON files. The existing workflow separately pins RDFLib 7.5.0 for independent Turtle parsing. Source Git blob `526f8bbb1827ebcbdb27c874cb6393b5ffbe638e`; test blob `879bb1be6e890027140ce2b79d91720ddd7fa193`; workflow blob `c6ec0b9e568d8cac149cbe57c9e7a90400df6a54`. [Registry](CORTEX_IN_MEMORY_BOUNDARY_V06_REGISTRY.json) records scope, run and unknowns.

## Decision and next experiment

**No maturity advance.** The guard is a narrow consistency gate, not a general extractor, RDF/PROV compliance certificate, evidence of archival truth, or proof that a meeting actually authorized a decision. **Strongest evidence:** independently executed cross-platform negative controls on a pinned fictional packet. **Largest gap:** independent semantic annotations and measured correction burden. **Next decisive experiment:** obtain two voluntary, genuinely independent blinded fictional-packet annotations, freeze source-span labels before comparing against manual structured notes, and measure disagreement/correction time. **Reframe:** do not promote a fixed-case projection to a general mapping API; withdraw any decision-lineage accuracy claim if unseen-case or human review fails.

**Four lenses:** hiring manager — a concrete integration guard with reproducible tests; technical reviewer — distinction between raw-file CLI integrity and unsafe in-memory reuse; innovation leader — established W3C PROV-O mapping preserved without novelty claims; founder — no users, deployments, or quantified business impact.
