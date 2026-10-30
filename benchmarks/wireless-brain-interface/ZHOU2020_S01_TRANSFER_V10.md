# WBI v1.0 — bounded first-original-archive transfer experiment

**Date:** 2026-10-30. **Stage:** Research / Simulation, unchanged. **Experiment status at protocol freeze:** actual S01 download **NOT YET VERIFIED**. This is a one-subject **source-integrity** experiment, not an EEG decoder or clinical test.

## Frozen source and fail-closed acceptance

The official [Zenodo Zhou2020 v1 record](https://zenodo.org/records/18988317) lists the publisher-repackaged `S01.zip` as 1.1 GB with MD5 `34867b4b27a8c91fd6fe010cbf4f9caa`. The [official file response](https://zenodo.org/records/18988317/files/S01.zip?download=1) exposed a **1,143,862,039-byte** content length when inspected 2026-10-30. The MD5 and size are source-declared/observed **transfer constraints**, not a publisher-signed SHA-256 or proof of equivalence to the original IEEE DataPort recording.

The [v1.0 transfer executable](zenodo_s01_transfer_v10.py) uses Python standard library only and has a **1,250,000,000-byte hard download cap**. It downloads only the pinned S01 URL into an ephemeral private directory, checks declared/received byte length and publisher MD5, computes independent SHA-256, and only then invokes the **unchanged** [v0.9 archive preflight](zenodo_archive_preflight_v09.py) to stream-check ZIP/NPZ-member integrity and provisional path limits. It does not extract files, unpickle, parse signal arrays, open event labels, or publish raw data. The source archive is removed when the process exits. Only aggregate status, transfer hashes, member count, total bytes and sorted member SHA-256 values may be uploaded as a public metadata artifact. Failure codes deliberately omit private filesystem paths and redirected URLs.

**Stop:** size/MD5 mismatch, transfer error, unsafe or unexpected ZIP structure, member size/CRC mismatch. Preserve failure; do not modify the raw source or weaken the allowlist to obtain PASS without separate review. Even a PASS is `PASS_TRANSFER_AND_ZIP_STRUCTURE_ONLY`, not EEG authenticity.

## Fictional regression evidence (not the original archive)

Local Linux 6.18.57 x86_64, CPython 3.13.5, 2026-10-30: **10/10 fictional tests passed** with the exact existing v0.9 preflight source. [Test code](test_zenodo_s01_transfer_v10.py) covers fake ZIP success, wrong MD5, incomplete transfer, conflicting Content-Length, size cap, path traversal, non-ZIP, malformed checksum, deterministic report, and redaction of simulated private error details. Source Git blobs are verified against local tested copies: transfer `7fc8efcc522c64c087497aafefb96f65816bb9e4`, tests `7a81e10ed310c2b4b6ec7353b2366b37bf4a4a41`, unchanged v0.9 `9e237b59096a9d3dc22ab1d44104ce61a2455d47`.

Reproduce locally without network (from `benchmarks/wireless-brain-interface`):

```sh
python -B -m unittest -v test_zenodo_s01_transfer_v10.py
```

The [dedicated acquisition workflow](../../.github/workflows/wbi-zenodo-s01-transfer-v10.yml) is limited to this research branch, uses read-only GitHub permissions, and uploads **metadata JSON only**. A hosted result is **TBD until the run and its artifact are independently inspected**.

## Distinct existing EEG evidence that must not be erased

This Zhou2020 S01 archive is **not** the separately documented BNCI2014_001 A01E public-EEG experiment: the [existing A01E different-day confidence-only baseline](WBI_A01E_DIFFERENT_DAY_BASELINE_V12.md) reports **165/288 correct** at its frozen one-subject four-class protocol, but **no drift-aware matched-coverage benefit or idle/rest false-action validation**. The [frozen synthetic evaluator](SYNTHETIC_EVALUATOR.md) remains unchanged at Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9`, and its [execution record](EXECUTION_RECORD.md) shows that on its synthetic fixture the authorization gate did **not** establish superiority over confidence abstention. Neither prior result validates Zhou2020 original signals.

## Decision and next experiment

**Strongest evidence:** separately verified A01E confidence-only public-EEG baseline; corrected Zhou2020 structural metadata and v0.9 fictional integrity controls. **Largest gap:** original S01 ZIP/NPZ byte verification, independently defensible source-to-BIDS event mapping, a frozen multi-subject matched-coverage policy comparison and genuine idle/rest evaluation. **Next:** inspect the first hosted source-transfer report; if and only if it passes, independently reproduce the ZIP SHA-256 and check selected nested NPZ structures with `allow_pickle=False` under strict resource limits, then test event mapping without touching held-out outcomes. **Kill/reframe:** source mismatch or mapping ambiguity stops the Zhou2020 analysis; no superiority/safety/clinical claims without matched-coverage held-out results.

**Four lenses:** hiring manager — real-source evidence gate; technical reviewer — exact transfer conditions and negative controls; innovation leader — source equivalence and standards remain open; founder — no demonstrated users, safety or product advantage. No employer data, private correspondence, patentability claim, merge, release, or stage advancement.
