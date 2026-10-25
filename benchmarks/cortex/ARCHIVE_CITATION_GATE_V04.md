# CORTEX — archive-record citation integrity gate v0.4 (2026-10-26)

**Stage:** Architecture / R&D (unchanged). **Evidence class:** author-created fictional review packet and deterministic software tests only. **Actual independent reviewers / semantic extraction accuracy / correction burden / employer data:** TBD or none. No release or deployment.

## Decision-changing negative control

The frozen v0.1 `validate_submission` accepts a fictional decision with `"supersedes": "H-12"` and `"source": ["b07"]` even if the reviewer does not identify **which archived record** documents H-12. It checks that the predecessor ID exists in the archive, not that a submitted citation resolves to the correct archived evidence. This is a *structural provenance gap*, not proof that the decision is semantically false.

The additive v0.4 `archive_citation_gate_v04.py` requires a separate `archive_sources` list for superseding decisions. It resolves every record reference to the archive's `decision_id` and requires **at least one exact match** to `supersedes`. A citation to a different valid record (H-11) does not satisfy an H-12 supersession. Missing, empty, unknown, duplicate, unhashable or malformed references fail closed. This deliberately does **not** alter the original frozen case/archive bytes, old intake, synthetic extractor, baseline, ground truth, or previous CI results.

## Source and provenance model

- Current decision source: `source: ["b07"]` (meeting utterance IDs).
- Historical predecessor: `supersedes: "H-12"` (decision ID).
- Archival evidence: `archive_sources: ["SYN-ARC-12"]` (archived **record** ID, separately checked against H-12).
- This follows the distinction between an entity revision and its supporting provenance in [W3C PROV-O](https://www.w3.org/TR/prov-o/#wasRevisionOf). **It is not a PROV-O conformance or novelty claim.**
- A citation that resolves structurally may still be irrelevant, inaccurate, unauthenticated or fabricated. A human must adjudicate semantic support and reviewer independence.

## Reproduce (public fictional files only)

```bash
cd benchmarks/cortex
python -B -m unittest -v test_archive_citation_gate_v04.py
python -B archive_citation_gate_v04.py demo
python -c "import hashlib;from archive_citation_gate_v04 import demo;assert hashlib.sha256(demo().encode('utf-8')).hexdigest() == '76e54d346299c9a8bb0d2b3485eae6f5b0a834c27128135cf6302d458f44420a'"
# Private completed submissions, if ever collected, must stay OFF GitHub:
python -B archive_citation_gate_v04.py check blind_case_20261024.json blind_archive_20261024.json PRIVATE_SUBMISSION.json
```

**Demo:** missing archival citation → `object[0]:missing_matching_predecessor_archive_source`; correctly cited fictional predecessor → no archive-citation issues. The demo contains **zero actual reviewers**. The v0.4 CLI invokes the existing strict v0.1 byte-hashed intake before its additive check; it returns error codes without printing private source text or reviewer identifiers.

## Experiment registry and failure boundaries

| Field | Recorded value |
|---|---|
| Question | Can a valid predecessor ID hide absent or incorrect archived-record evidence? |
| Inputs | Fictional greenhouse case/archive frozen 2026-10-24; synthetic test-only submission |
| Original behavior | v0.1 accepts an otherwise well-formed submission without `archive_sources` |
| New behavior | v0.4 rejects missing/wrong archival evidence link |
| Local runner | CPython 3.13.5, Linux x86_64, 2026-10-26 |
| Local test status | 17/17 standalone tests passed; 4 integration tests require repository v0.1 and frozen files (local skip) |
| CI result | [GitHub Actions #40241271339](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40241271339): **90/90 tests passed on Ubuntu and Windows** at executable head `e5f95d771a1427772d9cc1dead8b16cfce2a6577`; both job logs inspected; demo hash assertion passed |
| Demo SHA-256 (UTF-8 LF) | `76e54d346299c9a8bb0d2b3485eae6f5b0a834c27128135cf6302d458f44420a` |
| Seeds | None; fixed fictional inputs |
| Source and test blob hashes | Source Git blob `65efbcb816cb45b866573d61bd743a6cddcc94a3`; test Git blob `d008ce2ad1e5ca656012a77ad7b6d1887abbf424` (reread from draft branch) |
| Real reviewers, timings, extraction precision, ROI | TBD |
| Decision | Keep draft; do not advance maturity |

**Next evidence gate:** invite independent, consenting reviewers only after checking outreach history; freeze and privately adjudicate annotations and source spans, then run a genuinely general extractor *after* labels are locked and measure correction time against a fair manual-notes comparator (Issue #12). **Kill/reframe** if unsupported lineage persists or reviewer burden exceeds manual notes.

**Four lenses:** Hiring manager—auditable test of a specific failure; technical reviewer—record-ID versus decision-ID provenance and strict negative controls; innovation leader—bounded falsification; founder—no real workflow benefit or commercial validation yet.
