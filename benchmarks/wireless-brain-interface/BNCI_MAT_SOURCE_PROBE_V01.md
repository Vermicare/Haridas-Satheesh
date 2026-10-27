# WBI — publisher-source byte acquisition gate (2026-10-27)

**Decision-changing source distinction:** The [BNCI Horizon 2020 catalog](https://bnci-horizon-2020.eu/database/data-sets) lists 18 individual **MAT** files for `001-2014` under **CC BY-ND 4.0**. The [original BCI Competition IV site](https://www.bbci.de/competition/iv/) distributes a **GDF ZIP** under its own download conditions. The existing `bnci2a_source_archive_preflight.py` applies **only to the GDF ZIP**. It must not be applied to MAT files.

## Bounded source experiment

- **Source:** `https://bnci-horizon-2020.eu/database/data-sets/001-2014/A01T.mat` (catalog redirects to `https://lampx.tugraz.at/~bci/database/001-2014/A01T.mat`; route observed 2026-10-27).
- **Method:** one read-only full-byte SHA-256 stream of **A01T training-session MAT only**, bounded to 100 MiB, exact HTTPS host/path allowlist, no raw file or EEG saved, no evaluation labels fetched.
- **Output:** metadata-only JSON (source route, SHA-256, bytes, signature, time, runtime). A matching hash identifies fetched bytes, **not** publisher authenticity or signal validity.
- **Preflight:** 10/10 synthetic standard-library tests passed locally (CPython 3.13.5, Linux 6.18.55, GCC 14.2.0). Tests include untrusted redirects, HTML in place of MAT, incomplete/oversized transfers and tiny reads.
- **Local upstream attempt:** failed before download due to DNS resolution of `lampx.tugraz.at`. **Hosted Actions source acquisition VERIFIED:** [Actions #40490939415](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40490939415) passed at executable commit `2f15f8a3d5dfd9f8d323aa920ec82e2e639f0571`. The source-contract job passed **10/10 tests** on Ubuntu/Python 3.13.16. Two separately executed hosted read-only source streams (original job and rerun, same commit) each read **42,806,453 bytes**, detected `MATLAB_5`, and returned the identical SHA-256 `054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325`. Both logs were inspected; only 686-byte metadata artifacts were uploaded (IDs `12728717253` and `12728442549`). This is two successful fetches of the same provider file, not independent publisher authentication.
- **Unknown:** MAT internal data/event structure, the other 17 session files, actual event/trial counts, E-session label handling, classifier and risk–coverage metrics: **TBD**. [Machine-readable registry](BNCI_MAT_SOURCE_PROBE_V01_REGISTRY.json) preserves exact run, source/test Git blobs and limitations.

## Scientific boundary and next gate

This is source acquisition integrity, **not** real EEG classification or safety validation. The two formats must be separately loaded and independently attributed. Keep E labels isolated, verify genuine session/run metadata, freeze decoder/calibration/thresholds before held-out scoring, and compare gate versus abstention at matched coverage. Do not redistribute EEG or transformed excerpts without checking publisher terms. Stage remains **Research / Simulation**; no clinical, deployment or patentability claims.
