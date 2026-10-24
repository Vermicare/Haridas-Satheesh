# WBI — EDF+ task-annotation preflight (2026-10-25)

**Maturity: Research / Simulation (unchanged).** This is a bounded **single training-subject** annotation-integrity experiment, not a decoder benchmark, drift study, clinical result, or device validation. Real event counts and per-file label distributions remain **TBD until a passing source-pinned CI report**.

## Decision-changing protocol finding

The EDF+ specification stores TAL annotation characters **as consecutive bytes in the annotation signal's two-byte sample storage**. It does **not** place a zero high byte between every character. A preliminary local parser mistakenly assumed interleaved high-byte zeros; that draft was corrected **before treating any public-EDF output as evidence**. The corrected synthetic adversarial fixtures explicitly use consecutive bytes.

Primary sources:
- [EDF+ specification §2.2](https://www.edfplus.info/specs/edfplus.html): TAL onset, optional duration, 0x14 text separator, 0x15 duration separator, 0x00 terminator, per-record timekeeping and byte layout.
- [PhysioNet EEGMMIDB v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/): T0 rest; T1/T2 map to left/right fist **only in unilateral imagery runs** R04/R08/R12; the bilateral imagery runs have different meanings.

## Frozen input and acceptance contract

- Input: **S001/S001R04.edf**, **train** partition only; original EEGMMIDB v1.0.0 file. Held-out subjects remain untouched.
- Require the publisher SHA256SUMS.txt entry and the already observed pinned digest `3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d`.
- First run the existing `edf_smoke.py` structural/checksum verifier on **the same downloaded bytes**, then read **only** the EDF+ annotation channel. Do not interpret EEG waveform samples.
- Decode TAL onsets, durations, T0/T1/T2 text and timekeeping entries. Reject malformed separators, missing durations on task events, non-ASCII/unknown task codes, impossible event timing, and empty task-event sets. Emit counts and onset/duration metadata **only**.
- Run-specific mapping is **R04 unilateral imagery: T1 imagined left fist; T2 imagined right fist; T0 rest**. No claim that this mapping applies to all runs.
- No source EEG bytes, identifiable recordings, raw sensor streams or outreach data are committed or uploaded.
- Network fetch: one source file per attempt, at most two bounded attempts; timeouts are **operational failures**, not negative scientific results. No successful second acquisition is implied.

## Reproduce

```sh
python -m unittest discover -s benchmarks/wireless-brain-interface -p test_edf_smoke.py -v
python -m unittest discover -s benchmarks/wireless-brain-interface -p test_edf_annotation_contract.py -v
python benchmarks/wireless-brain-interface/edf_annotation_contract.py --fetch --out /tmp/wbi-edf-annotations.json
```

The last command requires public dataset access; local offline input requires both `--edf` and `--sha256-index`. The output is metadata-only and marks decoder accuracy, longitudinal drift and performance **TBD**.

## Evidence ledger

- Prior independent **real-byte structural** verification: [successful CI #40122474197](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40122474197), one training EDF, no events decoded.
- Later [PR-head structural CI #40122933217](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40122933217) **failed** due to `TimeoutError` while reading the remote EDF; its offline 10/10 header tests passed. This failure was not an EEG parsing or model result.
- **Local development:** 10/10 *fictional* TAL contract tests passed on Linux/Python; these do not establish actual event counts or correct parsing of the public EDF.
- **New source-pinned live annotation CI:** **TBD** pending completed final-head run. Do not infer success from an earlier revision or from green synthetic jobs.

## Gate / limitations

If real TAL parsing succeeds, preserve exact report hash, event counts, CI run ID, Python version and any exclusions. Next, cross-check the annotations against an independent EDF reader or the companion PhysioNet `.event` file **before** freezing preprocessing. Then perform subject-disjoint train/calibration baseline experiments without accessing held-out labels.

If annotation timing or label mapping cannot be independently reconciled, stop decoder work and repair the data contract; do not silently relabel. The existing [frozen synthetic evaluator](SYNTHETIC_EVALUATOR.md), its [cross-platform reproduction](FROZEN_CROSS_PLATFORM_REPRO_2026_10_24.md), and prior stronger results remain unchanged.

**Four-lens check:** hiring manager—traceable evidence gate; technical reviewer—byte-layout correction and adversarial controls; innovation leader—failure preserved, no false stage upgrade; founder—no performance, users, product, clinical or patentability claims.
