# WBI — first real MAT run-structure validation (2026-10-27)

**Decision-changing result:** The upstream, previously fingerprinted **A01T.mat training session** contains **nine MAT recording blocks**, not six. Blocks 0–2 (zero-based) have **no trial cues** and are baseline/idle recordings; blocks 3–8 contain **six task runs with 48 cues each (288 total)**. A split preflight that directly interprets MAT block index 0 as task run 1 would misassign run IDs. This corrects the *loader mapping*, not the documented six-task-run design.

## Reproduction and provenance

- Public upstream source: [BNCI2014_001 A01T](https://bnci-horizon-2020.eu/database/data-sets/001-2014/A01T.mat), redirected to the publisher's Graz host. The exact **42,806,453 bytes** match the prior hosted SHA-256 `054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325`; no publisher-signed hash was available.
- [Verified GitHub Actions #40506426387](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40506426387), tested commit `72502ee76ff0985e8ec2f696078bc76e6714998e`, **passed**. GitHub-hosted Ubuntu, CPython 3.13.16, NumPy 2.3.3, SciPy 1.16.2, 7/7 fictional structural regressions passed. The real-source metadata step passed and its JSON was printed in the job log; only a **790-byte compressed metadata-only artifact** (ID `12735471349`) was uploaded. The hosted workflow has no repository write permission.
- Real A01T: **9 blocks**, **3 cue-free**, **6 cued**, **288 cues**, **25 signal columns**, **250 Hz**. Cue-free block sample counts: 29,683 / 20,172 / 41,463. All six cued blocks have 96,735 samples and 48 cues each.
- Implementation: [metadata inspector](bnci_mat_run_metadata_v02.py); [fictional regression tests](test_bnci_mat_run_metadata_v02.py); [read-only workflow](../../.github/workflows/wbi-mat-run-metadata.yml); [machine-readable registry](BNCI_MAT_RUN_METADATA_V02_REGISTRY.json).
- Independent reference implementation: [MOABB BNCI2014_001 loader](https://github.com/NeuroTechX/moabb/blob/develop/moabb/datasets/bnci/bnci_2014.py) invokes `_convert_mi`; [its conversion helper](https://github.com/NeuroTechX/moabb/blob/develop/moabb/datasets/bnci/base.py) skips recording blocks with empty trial arrays. This is consistent with the observed source structure, not an independent replication of our exact source hash.

## Required correction before held-out evaluation

For this MAT route, **task run 1 corresponds to MAT block 3** (zero-based); task runs 1–6 correspond to blocks 3–8. Do not treat baseline blocks as motor-imagery trials. Retain the cue-free recordings for a separately preregistered idle-state analysis if warranted, **not** as an automatically validated false-action benchmark. Validate this mapping independently for each T/E file before producing split identifiers; do not silently assume every file has the same baseline blocks.

**Nonclaims:** No EEG samples, class labels, participant identities or E-session labels were published; no classifier, epoching, held-out accuracy, drift benefit, idle false-action metric or clinical/device-safety result exists. A01T alone does not establish all 18 sessions. MAT route and original GDF ZIP route are distinct. Research / Simulation maturity unchanged.

**Next experiment:** acquire remaining T/E files with per-file hashes, extract metadata only, validate baseline/task mapping and missing-label semantics per file, then freeze a leak-free decoder/threshold protocol before any E-label scoring. Stop/reframe if source-derived run structure contradicts the preregistered split assumptions.
