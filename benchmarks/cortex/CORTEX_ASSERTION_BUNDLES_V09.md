# CORTEX v0.9 — provenance of competing fictional assertions

**2026-11-01 | Research / Architecture (unchanged) | Software-only, fictional fixed-case control**

## Decision-changing gap

The earlier [v0.5 projection](CORTEX_PROV_BOUNDARY_V05.md) and [v0.7 downstream contract](CORTEX_GRAPH_CONTRACT_V07.md) preserve 14 reviewed RDF triples, but one flattened graph does not identify which fictional asserting party originated a relationship. A downstream consumer might mistake a contested `cortex:supersedes` edge for an agreed institutional fact. The original 14-triple graph, source bytes, evaluator, and historical results are **unchanged**.

[W3C PROV-O](https://www.w3.org/TR/prov-o/) and [PROV-DM](https://www.w3.org/TR/prov-dm/) define `prov:Bundle` as a named set of provenance descriptions that can itself have provenance. [PROV-Links](https://www.w3.org/TR/prov-links/) discusses independently maintained bundles; it is a **Working Group Note**, not a mandatory RDF dataset identity or trust mechanism. **RDF named graphs are this experiment's representation choice, not a requirement of PROV-O.** This is prior-art awareness, not a new ontology, conformance, novelty or patentability claim.

## Executable negative control

[Builder and auditor](cortex_assertion_bundles_v09.py) produce deterministic, fictional-only **N-Quads** with two named assertion graphs. Fictional analyst A says a checklist *supersedes* the historical checklist; fictional analyst B instead says it *clarifies* it. Both cite the same fictional utterance. A separate metadata graph types each assertion graph as a `prov:Bundle` and attributes it to a distinct fictional `prov:Agent`. These are **competing interpretations**, not a proven logical contradiction under RDF's open-world semantics.

[17 adversarial tests](test_cortex_assertion_bundles_v09.py) accept harmless statement reordering and duplicate RDF quads but reject flattened or merged graphs, swapped/missing attribution, invented revision claims, changed source identifiers, extra graphs, invalid UTF-8 and oversized inputs. The auditor checks **exactly 10 fixed-case quads** (2 bundles) against an independently declared allowlist; it is not a general provenance validator. An author can forge both claims and agent labels. **Identity, authority, independent truth, human semantic agreement and measured correction burden remain TBD.**

## Reproduce in 30–90 seconds

On the unmerged CORTEX research branch, from `benchmarks/cortex`, using **Python 3.13** and **RDFLib 7.5.0**:

```sh
python -B -m unittest -v test_cortex_assertion_bundles_v09.py
python -B cortex_assertion_bundles_v09.py demo
```

Expected demo: `valid=true`, `observed_quads=10`, `bundle_count=2`, `independent_truth=TBD`, `authorization=TBD`. It makes no external calls or writes. Optional bounded input: `python -B cortex_assertion_bundles_v09.py audit FILE.nq`; any deviation returns nonzero. Expected deterministic N-Quads SHA-256: `040503af2458cd5c9e3bbbea855409ffabd6895df7da096c67ffb472e9de0cc2`.

**Local execution:** CPython 3.13.5, Linux 6.18.57 x86_64, RDFLib 7.5.0: **17/17 fictional tests passed**; demo verified 10/10 quads and two bundles. **Independent hosted Ubuntu/Windows verification: TBD until final-head workflow logs are inspected.** See [machine-readable registry](CORTEX_ASSERTION_BUNDLES_V09_REGISTRY.json).

## Maturity and decision

**Stage:** Research / Architecture, unchanged. **Strongest evidence:** bounded local provenance-of-assertion negative controls plus earlier cross-platform v0.7 fixed-case graph audit. **Largest gap:** genuine authority/identity, two independent blinded source-span annotations, adjudicated semantic disagreement, and measured manual-versus-correction time **TBD**. **Next experiment:** freeze an unseen fictional packet, obtain voluntary independent first-pass annotations, preserve their distinct asserted origins privately, adjudicate conflicts, and time corrections against manual notes. **Kill/reframe:** if asserting identity cannot be verified, retain a read-only provenance display; if unsupported lineage or correction burden exceeds manual notes, abandon automated-governance benefit claims. No maturity advance, release, merge, product, deployment, human reviewer, employer data, or business-impact claim.

**Four lenses:** hiring manager — reproducible failure-mode demo; technical reviewer — fixed named graphs do not authenticate claims; innovation leader — established PROV bundles constrain positioning; founder — no evidence of real user benefit or enforceable authority.
