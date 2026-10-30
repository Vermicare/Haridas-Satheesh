# CORTEX v0.7 — downstream frozen RDF graph contract (fictional only)

**Date:** 2026-10-30. **Stage:** Research / Architecture (unchanged; below Simulation gate). **External reviewers:** 0. **Real organizational records:** 0. **Deployment:** none. **No new general-purpose ontology or PROV compliance claim.**

## Decision-changing failure boundary

The unchanged [v0.5 exporter](cortex_prov_boundary_v05.py) authenticates two **author-created fictional** input files by exact SHA-256 and emits a reviewed 14-triple Turtle graph. The [v0.6 adapter](cortex_in_memory_boundary_v06.py) protects its optional in-memory use against changed fictional source objects. Neither gate, by itself, checks whether a **downstream serialized RDF graph** has been edited, reinterpreted or enriched after export.

The additive [v0.7 graph auditor](cortex_graph_contract_v07.py) parses a bounded Turtle file with pinned RDFLib 7.5.0, compares the **RDF triple set** against an independently declared exact 14-triple allowlist, and fails closed on missing or extra relations. It accepts harmless triple reordering or duplicate RDF statements while rejecting unsupported additions. It is a fixed-case *downstream-consumer* contract, not a general RDF/PROV reasoner, security proof or semantic annotation.

A fictional negative control adding `ex:checklist-B prov:wasRevisionOf ex:checklist-H12` is rejected even though the unchanged v0.5 exporter output is accepted. This matters because **decision supersession is not necessarily document-content revision**. The same control rejects an invented primary-source claim, an unproved hold invalidation, reversed supersession, removed derivation, namespace spoofing and additional unsupported local edges.

## Standards-to-domain gap matrix

| Question | Established term or boundary | CORTEX v0.7 treatment | Remaining gap |
|---|---|---|---|
| Source/entity derivation | [W3C PROV-O](https://www.w3.org/TR/prov-o/) `prov:Entity`, `prov:wasDerivedFrom` | **Existing standard:** exact fictional source edges preserved | Original historical truth and source authenticity **TBD** |
| Document revision | `prov:wasRevisionOf` concerns revision of content | **Not asserted:** unsupported for this fictional checklist decision | Evidence of actual content revision **TBD** |
| Decision supersession versus clarification | Not automatically identical to PROV revision | **Domain-specific example:** `cortex:supersedes` and `cortex:clarifies`; exact edge direction pinned | Interoperable domain vocabulary and independent semantic judgment **TBD** |
| Identity and approval authority | DID / verifiable credentials are explored by [RecordWeb Community Group](https://www.w3.org/community/recordweb/), not implemented here | **Unverified:** no signer or authorization proof | Identity, authority and credential validity **TBD** |
| Time, freeze, retention, revocation | PROV includes event/temporal relations; this example does not establish them | **Unverified:** `prov:wasInvalidatedBy` forbidden absent evidence | Freeze, retention, revocation and timing **TBD** |
| Source spans and correction lineage | Provenance is not a substitute for evidence adjudication | **Partial fixed-case identifiers only:** b03/b07 and H-11/H-12 | Independent source-span review, disagreements and correction time **TBD** |

RecordWeb is a **W3C-hosted Community Group initiative**, not a W3C Recommendation or evidence of implementation. This experiment does not establish novelty, patentability, institutional adoption, standards conformance, external review or commercial value.

## Reproduction and observed evidence

**Source:** [frozen v0.5 report](CORTEX_PROV_BOUNDARY_V05.md), [v0.6 boundary](CORTEX_IN_MEMORY_BOUNDARY_V06.md), [v0.7 auditor](cortex_graph_contract_v07.py), [15 adversarial tests](test_cortex_graph_contract_v07.py), [machine-readable registry](CORTEX_GRAPH_CONTRACT_V07_REGISTRY.json).

**Local execution:** CPython 3.13.5, Linux 6.18.57 x86_64, RDFLib 7.5.0; **15/15 v0.7 fictional tests PASS**.

**Independent hosted verification:** [GitHub Actions run #41074345425](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41074345425), workflow commit `4be046f0d8786ba386f2532410a0729dbf0e0d7b`, completed **SUCCESS**. Independently inspected **Ubuntu and Windows** job logs: **15/15 v0.7 tests PASS on each**, and the *actual unchanged* v0.5 exporter output passes the independent v0.7 audit with **14 observed triples, zero missing, zero unexpected**. Earlier 201-test fictional suite, 14 v0.5 tests, 10 v0.6 tests and v0.5 SHA-pinned 14-triple parse gate all passed per operating system. Original v0.5 exporter and frozen case/archive were **not modified**.

**30–90 second demonstration** (from `benchmarks/cortex` on the research branch; RDFLib 7.5.0 required):

```sh
python -B cortex_prov_boundary_v05.py export blind_case_20261024.json blind_archive_20261024.json > cortex-prov-v05.ttl
python -B cortex_graph_contract_v07.py audit cortex-prov-v05.ttl
python -B -m unittest -v test_cortex_graph_contract_v07.py
```

The audit returns deterministic JSON with `valid=true` on the original fictional graph and exits nonzero for altered/unsupported graphs. Tests include malicious false-revision, false-primary-source and false-invalidation examples. It never reads actual employer/client meetings, does not publish fictional source dialogue and does not contact external services.

## Stage decision and next experiment

**No maturity advancement.** **Strongest evidence:** repeatable cross-platform source-to-output and downstream RDF-contract tests on one fixed author-created fictional packet. **Largest gap:** no two independent blinded annotations, no measured human correction burden, no unseen-case semantic accuracy, no actual authority or retention model. **Next decisive experiment:** freeze adjudication/matching rules, obtain two voluntary independent annotations of the fictional packet, and time structured-review corrections against manual notes; preserve disagreement and negative findings without publishing identities. **Kill/reframe:** if ungrounded decision edges or review time exceed the manual comparator, abandon claims of automated governance benefit; if established PROV terms suffice, do not invent a generic provenance standard.

**Four lenses:** hiring manager — reproducible failure-mode engineering; technical reviewer — source-byte integrity and output semantic contract are distinct; innovation leader — established standards and overlapping initiatives constrain positioning; founder — no measured user benefit or business viability.

**Outreach/privacy:** no new external reviewer agreement, human result, employer data, patent claim, release or merge is implied by this artifact.
