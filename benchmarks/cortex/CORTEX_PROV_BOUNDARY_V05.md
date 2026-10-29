# CORTEX v0.5 — frozen fictional PROV-O boundary projection

**Date:** 2026-10-29. **Maturity:** Architecture / R&D (unchanged). **Human reviewers:** 0. **Actual governance records:** 0. **External actions:** 0. **Purpose:** an executable, deliberately narrow standards-mapping experiment, **not** a general extractor, RDF reasoner, PROV compliance certification, proof of archival authenticity, independent semantic annotation, or product.

## Decision-changing design question

The existing blinded fictional case distinguishes an active public-demonstration hold (archive H-11, clarified by utterance b03) from a calibration-checklist replacement (archive H-12 superseded by a new checklist decision in b07). A naive provenance mapping can accidentally encode both as revisions or infer that the public hold was revoked. That would corrupt decision lineage.

The [W3C PROV-O Recommendation (2013-04-30)](https://www.w3.org/TR/prov-o/) already supplies reusable entity and derivation relationships. In particular, `prov:wasRevisionOf` is a *content-revision* relation, not a generic governance supersession or reversal. `prov:hadPrimarySource` asserts first-hand provenance that an arbitrary historical archive cannot establish. [W3C PROV Constraints](https://www.w3.org/TR/prov-constraints/) adds consistency rules; this experiment **does not** implement those full constraints.

**Decision:** reuse `prov:Entity` and `prov:wasDerivedFrom` for the pinned fictional source lineage, but retain distinct, example-only `cortex:supersedes` and `cortex:clarifies` domain predicates. Do **not** infer `prov:wasRevisionOf`, `prov:hadPrimarySource`, `prov:wasInvalidatedBy`, or a hold revocation. These local predicates are illustrative, not an established interoperable ontology or a novelty claim.

## Executable artifact

- [Projection CLI](cortex_prov_boundary_v05.py) emits **14 deterministic Turtle triples** with no fictional dialogue text or private identifiers. Only the exact frozen [case](blind_case_20261024.json) and [archive](blind_archive_20261024.json) raw-byte SHA-256 hashes are accepted by the CLI.
- [Adversarial tests](test_cortex_prov_boundary_v05.py) exercise false revisions, false hold supersession, unresolved predecessor/source, duplicate utterances, wrong fixture identity, changed bytes, oversized input and private-path non-disclosure.
- [Machine-readable registry](CORTEX_PROV_BOUNDARY_V05_REGISTRY.json) records versions, source digests, test conditions and unknowns.

From `benchmarks/cortex`:

```sh
python -B -m unittest -v test_cortex_prov_boundary_v05.py
python -B cortex_prov_boundary_v05.py export blind_case_20261024.json blind_archive_20261024.json > /tmp/cortex-fictional-prov-v05.ttl
```

The output has a fictional example namespace and no contact information, employer data, live meeting data or participant submissions. The Python CLI uses only the standard library; an independent optional Turtle parse was performed with RDFLib 7.5.0.

## Executed evidence, including failure

- Local CPython **3.13.5**, Linux **6.18.55 x86_64**, standard library tests: **14/14 passed** after fixing a test that initially counted the three Turtle prefix declarations as triples (**initial 13/14**, corrected and rerun). This was a *test assertion* defect, not a model finding.
- Frozen case SHA-256: `f6357accbd87e11ffcaf1a2d39a085b0611719de6953cd3e4789ccacbb96344d`; archive SHA-256: `897ba394a392ffd63b5561500e5350573570c835fc699c0fd453148d4e3c8046`. Both raw-byte digests independently matched the checked-out fictional fixtures.
- Independently parsed generated Turtle using RDFLib **7.5.0**: **14 RDF triples**; output SHA-256 `7cca1eea84e9ff8b916ee2a6ca8b73a0c3aeb047dafdcf521cc47d9d9ffbd9b0`.
- Source SHA-256 `9fadeca6469a6fb73cd7fbd7915d2cf6ed6b11a5bd6775f467c17e297169c507`; test SHA-256 `0934f0117dd1058f3f5ede943021406746a51f1610aa7d10b94a039945f55114`.
- Hosted Windows/Ubuntu execution for **v0.5**: **TBD**. General RDF/OWL semantic validation: **TBD**. Human correction burden, blinded annotation agreement, extractor accuracy and archival authenticity: **TBD**.

## Scope and falsification

This is a *hand-reviewed fixed-case projection*. Hashes protect against unnoticed input changes; they do not prove source truth. The in-memory rendering function is exposed for fictional unit tests, while the public CLI enforces exact fixture hashes. No claim of semantic generalization is made.

**Next experiment:** two genuinely independent, voluntary blinded annotations with frozen labels and real measured review/correction time against manual notes, followed by an unseen-case mapping. Before a generalized exporter, compare with W3C PROV-O semantics and test that ambiguous historical relationships are refused rather than guessed. **Reframe** to provenance-assisted human review if unsupported decision edges or review burden exceed manual notes.

**Four lenses:** hiring manager — inspectable runnable architecture boundary; technical reviewer — explicit negative controls and limited PROV mapping; innovation leader — established prior art, no novelty/patentability claim; founder — no users, deployment or business benefit measured. No maturity advancement, release, merge or external commitment.
