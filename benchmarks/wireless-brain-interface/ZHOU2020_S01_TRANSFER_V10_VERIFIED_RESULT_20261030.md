# Zhou2020 S01 v1.0 — independently inspected transfer-result checkpoint

**Date:** 2026-10-30. **Stage:** Research / Simulation (unchanged). **Result:** **PASS_TRANSFER_AND_ZIP_STRUCTURE_ONLY**, **not** EEG authenticity, IEEE DataPort equivalence, original NPZ validation, source-to-BIDS mapping, decoder validation, or clinical evidence.

## Exact provenance and execution

- Publisher-repackaged source: [Zenodo Zhou2020 record 18988317](https://zenodo.org/records/18988317), file `S01.zip`, record DOI `10.5281/zenodo.18988317`, source version v1.
- Frozen [protocol and safeguards](ZHOU2020_S01_TRANSFER_V10.md), [bounded downloader](zenodo_s01_transfer_v10.py), [existing v0.9 ZIP preflight](zenodo_archive_preflight_v09.py) and [ten fictional regression tests](test_zenodo_s01_transfer_v10.py).
- Hosted [GitHub Actions run #41057530771](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41057530771), job `124068719242`, commit `1bce7fa15b7cef7c1f042f60a5d1d9532fffd8e4`, Ubuntu hosted runner, Python 3.13 as pinned by workflow; exact Python patch and runner image version **TBD**.
- All **10/10 network-free fictional regression tests passed**. The real download/preflight step completed successfully; this was **one hosted original-source acquisition**, not an independent second download.
- The ephemeral 1.14 GB archive was **not uploaded**. The [metadata-only hosted artifact #12977563337](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41057530771/artifacts/12977563337) expires **2026-11-06** according to GitHub; it contains only `s01-metadata-only.json`.

## Verified observations

| Check | Observed |
|---|---|
| Declared and received compressed bytes | **1,143,862,039 / 1,143,862,039** |
| Publisher-listed MD5 and independently streamed MD5 | `34867b4b27a8c91fd6fe010cbf4f9caa` — match |
| Independently computed ZIP SHA-256 (hosted transfer) | `897c8316ac8130635821cab42d39b946dcedf54a582f3252bf028e190f294dbf` |
| ZIP preflight | **PASS**, **4,141** reported checks |
| ZIP NPZ members | **43** |
| Aggregate declared uncompressed member bytes | **3,865,018,046** |
| Hosted artifact ZIP SHA-256 | `f174c606fd221012d08906bd375307e4d7f5eb8ac19ae0608f99a898e5cb3bd2` |
| Metadata JSON SHA-256 | `4dd22f27bd72f21200976372fb238517b1affdd224d27b884afec4f69f61631b` |
| Original IEEE DataPort equivalence | **TBD** |
| Original NPZ semantic/authenticity validation | **TBD** |
| Source-to-BIDS event mapping | **TBD** |
| Held-out EEG decoding, matched-coverage drift-gate superiority, rest false actions | **NOT PERFORMED** |

## Independent post-run artifact inspection

The **original** 2,401-byte hosted ZIP artifact was downloaded separately from GitHub Actions and independently hashed: SHA-256 matches the provider-reported artifact digest. Its ZIP CRC/integrity check passed, and its single **4,185-byte** JSON member was parsed without relying on the workflow's console summary. Sixteen structural/semantic assertions passed, including exact byte counts, MD5 match, status, **43 sorted and unique SHA-256-format member digests**, zero signal upload/array opening, and explicit unknowns. This independently checks the **hosted metadata artifact**, **not** the original 1.14 GB raw archive or all 43 NPZ bytes a second time. The archive checksum is a reported result of the one hosted acquisition.

No NPZ arrays were decoded or unpickled. No signal bytes, original filenames or private data were published. MD5 is used solely to match the publisher's transfer reference, not as a cryptographic authenticity or signing guarantee. Member hashes are content fingerprints, not proof of IEEE origin or event alignment.

## Decision and next falsifiable gate

**No stage advancement, merge, release, clinical/safety claim or superiority claim.** This closes the *first publisher-repackaged S01 transfer-and-ZIP-integrity gate only*. Existing [synthetic evaluator](SYNTHETIC_EVALUATOR.md) and its [negative execution record](EXECUTION_RECORD.md) remain unchanged. Separately verified A01E **165/288** different-day confidence-only decoding is distinct from this Zhou2020 source experiment.

**Next:** independently reacquire S01 in a separate environment and compare its SHA-256 with `897c8316...`; if equal, inspect only bounded selected NPZ structural metadata with `allow_pickle=False`, then preregister a source-to-corrected-BIDS event mapping and held-out EEG outcome rules. **Stop/reframe** on checksum discrepancy, ambiguous event mapping, unsafe NPZ structure, or label leakage. Until independently verified, all mapping and real-data drift-effect claims remain **TBD**.

**Four lenses:** hiring manager — actual public-source acquisition, not a simulated-only milestone; technical reviewer — one-host transfer plus independently audited metadata, not independent re-download; innovation leader — source equivalence remains unresolved; founder — no measured real-world efficacy, users or deployment.
