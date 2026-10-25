# WBI — EDF+ task-annotation preflight (2026-10-25)

**Maturity: Research / Simulation (unchanged).** This is a bounded **single training-subject** annotation-integrity experiment, not a decoder benchmark, drift study, clinical result, or device validation. A passing source-pinned GitHub Actions run now establishes **real training-file annotation extraction only**; independent annotation-reader agreement, EEG decoding and performance remain **TBD**.

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
- **Earlier annotation CI:** bounded HTTPS acquisitions timed out; synthetic tests passed but real task-annotation counts were **TBD**. These operational failures are preserved and are not EEG performance results.
- **Recovery and real-data result:** [CI #40163082196](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40163082196) **PASSED** on Ubuntu / CPython 3.13.16 at 2026-10-25 04:46 UTC. The [publisher-documented unsigned S3 route](https://physionet.org/content/eegmmidb/1.0.0/) completed in the first transport attempt; the HTTPS fallback was not used. The same source-pinned training EDF `S001R04.edf` matched publisher SHA-256 index and previously pinned digest `3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d`. **10/10 fictional structural tests and 10/10 fictional TAL contract tests passed**, followed by real TAL extraction of **T0=15, T1=8, T2=7 (30 task annotations)**. No EEG samples were decoded, and no held-out subject was accessed. The metadata-only JSON SHA-256 is `c9130f2b186471c76a629b1d8f20750f8585b808675fd4ebda82d9afc9d45936`; [artifact #12587096905](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40163082196/artifacts/12587096905) retains only metadata (14-day retention), not raw EDF. The [machine-readable registry](REAL_EDF_ANNOTATION_S3_REGISTRY_2026_10_25.json) records provenance, exact CI commit, limitations and next gate.

## Gate / limitations

Real TAL parsing has now passed the pinned single-file gate. **Next, independently compare all task events against the publisher's companion `.event` file or another EDF+ reader** (counts, event onsets, durations and run-specific labels) **before** freezing preprocessing. No independent comparison has yet been executed. Then perform subject-disjoint train/calibration baseline experiments without accessing held-out labels.

If annotation timing or label mapping cannot be independently reconciled, stop decoder work and repair the data contract; do not silently relabel. The existing [frozen synthetic evaluator](SYNTHETIC_EVALUATOR.md), its [cross-platform reproduction](FROZEN_CROSS_PLATFORM_REPRO_2026_10_24.md), and prior stronger results remain unchanged.

**Four-lens check:** hiring manager—traceable evidence gate; technical reviewer—byte-layout correction and adversarial controls; innovation leader—failure preserved, no false stage upgrade; founder—no performance, users, product, clinical or patentability claims.
