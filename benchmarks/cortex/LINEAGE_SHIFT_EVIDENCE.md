# CORTEX — fictional archive-reference and transfer stress gate

**2026-10-24 | Synthetic-only | Stage remains Architecture / R&D**

## Decision-changing result

The committed v0.1 baseline has exact-signature F1 **1.0 in each of five categories** on the original fixture, despite its unresolved predecessor `D0`. On a separately authored, fictional meeting with new utterance IDs and a new context, the same frozen-only baseline emits **zero governance objects**: exact-signature F1 **0.0 in each of five categories**. This is an *expected limitation of a deliberately hard-coded demonstration baseline*, not a performance estimate for a general CORTEX extractor or a statistically valid distribution-shift study.

The earlier additive fixture preflight accepts a historical `record_ref` as soon as it is nonempty. A negative control removes the purported archive record while retaining the string reference: the earlier preflight returns no errors. The new `audit_archive` checks that each declared historical record reference resolves to an actual *fixture-internal* archive object with matching decision ID and nonempty text. It rejects missing records, duplicate references, wrong IDs and empty text. **An internally consistent fictional archive is not authenticated history.**

## Reproduce

Run from `benchmarks/cortex` with CPython 3.13 (stdlib only):

```bash
python -B -m unittest -v fixture_integrity_preflight.py test_lineage_shift.py
python -B run_lineage_shift.py
sha256sum synthetic_lineage_shift_results.json
```

The original `fixture.json`, `baseline.py` and `evaluator.py` are unchanged. `independent_scenario_v03.json` is **author-created fictional data** derived from a local October 23 test fixture, with a newly declared *fictional* archive record. It was not blinded or human-adjudicated. The generated report is deterministic JSON (LF, UTF-8, sorted keys) with the expected SHA-256 `2c3d060df1932318cc64dba980946ebaad3c47fd56a7509b488f9f53e2dc6180`.

## Limits, advancement and stop rule

- Structural source-ID and archive-reference checks are not semantic, legal, provenance-authenticity or employer-data validation.
- The exact-match legacy evaluator may award high F1 even when lineage is unresolved. Present fixture readiness alongside score; do not silently rewrite historical evidence.
- No real workflow, external review, measured reviewer time, business impact, model generalization, production authorization or deployment evidence exists.
- Next: have independent reviewers annotate a **new unseen fictional meeting** and genuine fictional archive documents, freeze labels before extractor execution, record disagreements, traceability and correction minutes. Compare a general extractor to a manual structured-note baseline. Do not advance without reproducible unseen-case quality and acceptable review burden.
- Reframe if structured-memory false positives or correction time outweigh the value of traceable decisions.

**No release, stage change, public real-world performance claim, or employer information.**

## Addendum — supersession graph negative controls (2026-10-24)

Source inspection of the earlier `audit_fixture` shows that a declared predecessor is accepted when its identifier belongs to the current-or-historical ID set. This membership check does **not** detect a decision superseding itself or multi-node cycles. Such graphs make the ordering of historical decisions internally contradictory even when every referenced ID resolves.

Added [`supersession_graph.py`](supersession_graph.py) with [15 fictional-only adversarial tests](test_supersession_graph.py). Two tests reproduce the earlier membership-only preflight accepting a self-loop and a two-node cycle before asserting rejection by the new gate. The new additive structural preflight reports self-loops, multi-node cycles, missing predecessors, duplicate IDs, malformed collections and branching successors. A branch is marked `forked_supersession_review`, **not** automatically declared false: concurrent policy forks can be legitimate and require reviewer adjudication. The original frozen evaluator, fixture, lineage-shift outputs and scores are untouched.

**Local reproduction:** CPython 3.13.5/Linux standard library; two independent invocations of `python -B -m unittest -v test_supersession_graph.py` passed **15/15** with byte-identical **elapsed-time-normalized** test logs (SHA-256 `1f6d6fb7967142133f8761abb60c122a68a747e3337399a2b3e628cca4639ed8`); raw unittest durations may differ. Git blob IDs: source `a7477749e0be070dbbfa985f01dcc1bb0e54a3ce`; tests `bac2161a4daaa604cb0aba09ddab67a41b53a7ea`. [GitHub CI #40067378077](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40067378077) completed successfully: **32/32 tests on Ubuntu and Windows**, including both reproduced prior false accepts; the frozen synthetic output SHA-256 assertion also passed.

**Evidence boundary:** This is a structural consistency check on author-created fictional decision graphs. It does not prove archive authenticity, temporal truth, real extraction accuracy, legal validity, authorization, or usefulness. The stage remains **Architecture / R&D**. Next gate: independently annotated unseen fictional decisions and real reviewer-time measurements, including adjudication of deliberate forks.


## Addendum — linear-time fictional lineage traversal (2026-10-24)

**Evidence gap addressed:** the previous graph-cycle walk restarted from every predecessor and could traverse the same long acyclic chain repeatedly (quadratic worst-case). This is a scalability defect in the *structural validator*, not a claim about CORTEX extraction quality. The additive replacement uses a nonrecursive three-state walk (unseen / current path / completed) and retains the same sorted issue codes, including the human-review-only fork flag. It does not alter the frozen extractor, fixture, original scores or archive checks.

**Local negative-control comparison:** CPython 3.13.5 on Linux 6.18.55 x86_64, stdlib only; fixed RNG seed 2401024, 360 generated fictional graphs. Independent graph-walk outputs agreed in all 360 cases. A single-process synthetic acyclic-chain comparison was executed twice, with graph lengths 1,000 / 5,000 / 12,000. In the second run the prior graph walk took **0.039438 / 1.029424 / 6.795228 seconds**, and the linear candidate took **0.000302 / 0.001391 / 0.003332 seconds**. These are **local, non-gating timings of graph traversal only**, not whole-evaluator benchmarks, guaranteed speedups, real-world throughput or cross-platform performance results. Run conditions and code are in [the standalone benchmark](benchmark_supersession_scaling.py); unknown hardware details are TBD. The separate local comparator script SHA-256 was `2829625afa89538a90368dd19b9cd688dc82f4bbfecd96c66f497dfb2184d6fe`.

**Repository tests:** [two additional adversarial tests](test_supersession_graph.py) require a 12,000-node fictional chain and compare cycle presence against a simple independent oracle on 80 seeded small graphs. No wall-clock threshold is imposed in CI. Source Git blob SHA `6d82f0b5b588ca65aec48abbeeee686407c9ddda`; test blob `458f205d89b9d6df7882693605e874e611e75ae7`; benchmark blob `d6f2c1dcc48b171194638c79a2e1f48b45504982`. Cross-platform CI: [GitHub Actions #40086872697](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40086872697) passed **34/34 tests on both Windows and Ubuntu**, and the seeded 360-graph benchmark/integrated 12,000-node chain check passed on both platforms. Per-run wall-clock ratios varied and are not acceptance thresholds.

**Stage:** remains Architecture / R&D. **Largest gap:** blinded unseen-case annotations, independent source-span and lineage adjudication, and measured human correction burden versus manual notes. **Next experiment:** Issue #12, not further synthetic timing optimization. Reframe if reviewer burden/false governance records outweigh the benefit of traceable decisions.
