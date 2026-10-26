# CORTEX — illustrative PROV-O mapping v0.1 (fictional only)

**2026-10-26 | Architecture / R&D | Not a real-world benchmark | Human review: TBD**

## Decision and primary source

The W3C [PROV-O Recommendation (2013-04-30)](https://www.w3.org/TR/prov-o/) already specifies interoperable provenance entities and derivation relations. This is an **interoperability mapping exercise**, not a new ontology, patentability claim, proof of authenticity, or an OWL conformance certification.

The independent **author-created fictional** `independent_scenario_v03.json` supplies meeting utterances, ground-truth governance records, a historical decision H0, and an archive record SYN-ARCHIVE-001. `prov_o_mapping_v01.py` converts these into a deterministic JSON-LD-shaped graph with:
- `prov:Entity` nodes for utterances, archive records and structured governance records;
- `prov:wasDerivedFrom` edges from a *structured representation* to its cited fictional utterance or archive record;
- **`cortex:supersedes`**, a domain-specific decision relationship from D3 to H0, *not* `prov:wasRevisionOf`.

**Important semantic boundary:** `prov:wasRevisionOf` implies a revised entity containing substantial content from the original. A new governance decision that reverses an old one need not be a revision. Likewise `prov:hadPrimarySource` requires a domain-specific judgment about firsthand source status; this mapping does **not** assert it merely because a string resembles a transcript or archive. The `cortex:supersedes` term is an illustrative local extension, not a W3C term or proposed new generic provenance standard.

## Reproduce

From `benchmarks/cortex`, Python 3.13 standard library only:

```bash
python -B -m unittest -v test_prov_o_mapping_v01.py
python -B prov_o_mapping_v01.py independent_scenario_v03.json
```

Thirteen negative/positive controls cover deterministic output, resolved fictional historical citation, correct singular node IDs, source membership, duplicate/unknown/malicious IDs, self/unknown supersession, negative-case promotion and synthetic-only input. Existing original fixture, baseline, evaluator, other CI test cases and scores remain untouched.

The graph is a **demonstration of representation**, not an independently parsed RDF/OWL validation, real semantic extraction, a trustworthy historical archive, proof of permission, reviewer study, or performance result. It maps *author-created ground truth*, not extracted model predictions. An internally consistent fictional graph can still be false. All real-world accuracy, reviewer correction time, cross-system interoperability and business value remain **TBD**.

## Next evidence gate

Issue #12: independent blinded source-span/lineage annotations on a genuinely unseen fictional case, frozen gold labels, general extractor, and actual measured correction burden against manual structured notes. Do not use this illustrative graph to inflate extractor precision. Reframe CORTEX if unsupported governance records or correction burden exceed the manual baseline. No stage advancement, release, merge, outreach, employer data or deployment follows from this mapping.
