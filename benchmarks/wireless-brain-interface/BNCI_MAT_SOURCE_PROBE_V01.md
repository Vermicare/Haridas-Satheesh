# WBI — publisher-source byte acquisition gate (2026-10-27)

**Decision-changing source distinction:** The [BNCI Horizon 2020 catalog](https://bnci-horizon-2020.eu/database/data-sets) lists 18 individual **MAT** files for `001-2014` under **CC BY-ND 4.0**. The [original BCI Competition IV site](https://www.bbci.de/competition/iv/) distributes a **GDF ZIP** under its own download conditions. The existing `bnci2a_source_archive_preflight.py` applies **only to the GDF ZIP**. It must not be applied to MAT files.

## Bounded source experiment

- **Source:** `https://bnci-horizon-2020.eu/database/data-sets/001-2014/A01T.mat` (catalog redirects to `https://lampx.tugraz.at/~bci/database/001-2014/A01T.mat`; route observed 2026-10-27).
- **Method:** one read-only full-byte SHA-256 stream of **A01T training-session MAT only**, bounded to 100 MiB, exact HTTPS host/path allowlist, no raw file or EEG saved, no evaluation labels fetched.
- **Output:** metadata-only JSON (source route, SHA-256, bytes, signature, time, runtime). A matching hash identifies fetched bytes, **not** publisher authenticity or signal validity.
- **Preflight:** 10/10 synthetic standard-library tests passed locally (CPython 3.13.5, Linux 6.18.55, GCC 14.2.0). Tests include untrusted redirects, HTML in place of MAT, incomplete/oversized transfers and tiny reads.
- **Local upstream attempt:** failed before download due to DNS resolution of `lampx.tugraz.at`. **Hosted Actions upstream result: TBD** pending exact final-head job logs.
- **Unknown:** upstream SHA-256/bytes, MAT content, actual event/trial counts, E-session label handling, classifier and risk–coverage metrics: **TBD**.

## Scientific boundary and next gate

This is source acquisition integrity, **not** real EEG classification or safety validation. The two formats must be separately loaded and independently attributed. Keep E labels isolated, verify genuine session/run metadata, freeze decoder/calibration/thresholds before held-out scoring, and compare gate versus abstention at matched coverage. Do not redistribute EEG or transformed excerpts without checking publisher terms. Stage remains **Research / Simulation**; no clinical, deployment or patentability claims.
