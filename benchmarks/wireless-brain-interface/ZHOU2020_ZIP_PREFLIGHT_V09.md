# Zhou2020 v0.9 — bounded original-archive preflight (fictional controls only)

**Date:** 2026-10-30. **Stage:** WBI Research / Simulation, unchanged. **Source:** [Zenodo Zhou2020 v1, record 18988317](https://zenodo.org/records/18988317), published 2026-03-12. **Real original ZIP/NPZ execution:** **TBD — no original bytes acquired or verified**. This is a pre-acquisition software guard, not an EEG benchmark.

## What changed

The [v0.8 source/provenance protocol](ZHOU2020_ORIGINAL_ARCHIVE_PROVENANCE_V08.md) identifies a publisher-repackaged per-subject source. This v0.9 adds an executable **read-only**, Python-standard-library preflight, [zenodo_archive_preflight_v09.py](zenodo_archive_preflight_v09.py), plus [15 fictional adversarial tests](test_zenodo_archive_preflight_v09.py). It never downloads or extracts a ZIP, executes NPZ data, unpickles arrays, or inspects EEG signals or labels. It streams archive MD5 and SHA-256, compares the **publisher's ZIP transfer MD5**, checks archive/member limits, ZIP central-directory metadata, path traversal, duplicate names, symlinks, encryption, compressed/uncompressed size bounds, per-member streamed CRC/size and SHA-256, and emits a machine-readable PASS/FAIL report. MD5 is only a transfer-integrity reference, not a source-authenticity guarantee.

The member path allowlist is a **provisional assumption** based on the publisher's described 'session_1/run_01.npz' structure; unexpected layouts must fail for investigation, not be silently accepted. Nested NPZ contents, array dtypes, event semantics and BIDS correspondence are **not inspected** by this preflight. The sample positive test uses fictional arbitrary bytes with an '.npz' suffix and therefore **does not validate NPZ parsing**.

## Reproduction and evidence

Local environment: CPython 3.13.5, Linux; no third-party packages; no original EEG bytes; fictional ZIPs generated temporarily. Command:

    python -m unittest discover -s benchmarks/wireless-brain-interface -p test_zenodo_archive_preflight_v09.py -v

**Observed locally:** 15/15 tests PASS (fictional positive and 14 negative/invariance cases), source compiled; duplicate-name fixture intentionally emits a Python ZIP warning. Exact source SHA-256: 'b1822a2aa4a564a285fa6bb65ea8c93e3216d4b80c6ff657cdc54101d24661dc'. Test SHA-256: '6b65040416790940949274867e36e16c96062a43076a404b666ac74e22d26da6'. These are local content hashes, not ZIP/NPZ hashes. Hosted cross-platform run: [GitHub Actions #41015688552](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41015688552) **triggered; result TBD until job completion and log inspection**.

For a locally obtained, independently preserved publisher archive (do not upload original signals to public GitHub):

    python benchmarks/wireless-brain-interface/zenodo_archive_preflight_v09.py S01.zip --expected-md5 34867b4b27a8c91fd6fe010cbf4f9caa --json-out s01_private_preflight.json

A PASS only indicates **transfer/ZIP structural consistency within provisional bounds**. The script is not a hardened general-purpose untrusted archive sandbox; it performs resource-bounded streaming, not full nested-format security review. Preserve original bytes privately; record download URL/time, local tool versions and SHA-256; do not publish participant signal data. Reject/record any mismatch, do not repair or modify raw bytes to obtain PASS.

## Evidence gate and decision

**Strongest evidence:** previous pinned 833-file corrected event metadata, frozen synthetic evaluator (unchanged original blob '2becec81a8002cc5ff2f445889b7617baf9937b9'), and now local fictional archive-integrity negative controls. **Largest gap:** zero independently authenticated original EEG ZIP/NPZ bytes, no event-to-recording mapping, no clean held-out decoding or matched-coverage drift benefit. **Next experiment:** acquire **only S01.zip** (~1.1 GB publisher-listed), verify its MD5 and independently computed SHA-256, run v0.9 read-only checks, separately inspect nested NPZ with no pickle under strict limits, then independently map run identifiers/event units against pinned corrected BIDS metadata. Stop/reframe on any integrity or mapping mismatch. Do not advance maturity, claim novelty, patentability, safety, efficacy, clinical performance, external review, release or deployment.

**Four lenses:** hiring manager — auditable, scoped negative controls; technical reviewer — separates transfer integrity from source authenticity and signal semantics; innovation leader — explicit source-identity risk; founder — no validated product or user benefit. No confidential employer data, outreach tracking or private signals.
