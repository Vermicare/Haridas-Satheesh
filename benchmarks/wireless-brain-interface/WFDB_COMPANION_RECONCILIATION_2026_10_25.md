# WBI — publisher WFDB companion cross-format reconciliation (2026-10-25)

**Result: 29/29 shared events agree, but the companion file omits one initial rest annotation.** This is a verified **cross-format discrepancy**, not 30/30 cross-format agreement. Maturity remains **Research / Simulation**. No EEG samples were decoded or model trained.

## Source and frozen scope

- Publisher: [PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), DOI 10.13026/C28G6P.
- **Training only:** `S001/S001R04.edf` and its companion `S001/S001R04.edf.event`. EDF SHA-256: `3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d`.
- Both bytes were obtained from the publisher's documented unsigned S3 distribution and verified separately against `SHA256SUMS.txt`. Companion SHA-256 is recorded in the metadata-only CI artifact, not assumed in advance.
- EDF+ annotations: existing project's TAL parser (also previously reproduced independently using MNE-Python 1.13.2). WFDB companion: `wfdb==4.3.1` `rdann`, binary `.edf.event` format, 160 samples/s.
- This comparison does not inspect EEG waveforms. The .event auxiliary note encodes a label and a textual duration (observed `T2 duration: 4.1`). Onsets in the companion are sample-index quantized.

## Executed findings and preserved negative results

| Evidence | Observed result |
|---|---|
| [First cross-format CI #40178026220](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40178026220) | Failed: overly narrow label parser rejected actual `T2 duration: 4.1` auxiliary-note syntax. |
| [Encoding diagnostic CI #40178102249](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40178102249) | Confirmed the actual auxiliary-note representation. |
| [Count mismatch CI #40178231594](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40178231594) | Failed: EDF+ TAL=30 annotations; WFDB companion=29. |
| [Boundary diagnostic CI #40178329171](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40178329171) | Isolated omitted **initial T0 rest event**: EDF+ onset **0.0 s**, duration **4.2 s**. WFDB starts at **sample 672 = 4.2 s**, with `T2`. WFDB counts: T0=14, T1=8, T2=7. |
| [Reconciled CI #40178448547](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40178448547) | **Passed 17/17 synthetic negative/control tests** and verified **29/29 shared event labels, onsets and durations**, after explicitly recording the missing initial T0. Maximum onset difference **0.0 s**, maximum duration difference **0.0 s**. |
| Metadata-only report | SHA-256 `06573ff0040635f3db3776b336f5d1f123fc0dcfda84a1a2669232da7f56782b`; [artifact #12592144458](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40178448547/artifacts/12592144458) (14-day retention). |

**Acceptance is narrowly scoped:** exactly one known initial T0 (0.0 s, 4.2 s) may be absent from this specific companion file. Any other omission, altered label, onset, duration, checksum or count fails closed. The exception was introduced **after** observing the initial negative CI evidence; it is not a predeclared dataset-independent rule. Do not generalize it to other subjects/runs.

## Reproduce

```bash
python -m unittest discover -s benchmarks/wireless-brain-interface -p test_wfdb_event_crosscheck.py -v
python -m pip install "wfdb==4.3.1"
python benchmarks/wireless-brain-interface/wfdb_event_crosscheck.py \
  --edf /secure-local/S001R04.edf \
  --event /secure-local/S001R04.edf.event \
  --sha256-index /secure-local/SHA256SUMS.txt \
  --out /tmp/wbi-wfdb-cross-format-report.json
```

The CI workflow obtains only the predeclared training EDF, companion and checksum index. Raw EDF and binary companion bytes remain runner-local; only a metadata JSON report and dependency list are uploaded. Exact transitive versions are in the short-retention artifact; hash-locked dependencies remain **TBD**.

## Interpretation / decision

This is **not** an independently human-labeled reference, real EEG decoding accuracy, device performance or clinical evidence. PhysioNet documents companion `.event` annotations as corresponding to EDF+ annotations; this run establishes that, for this specific file, **the first rest marker is absent in the companion**, while the remaining 29 agree. The cause of the omission is **TBD**; do not label it a publisher bug without investigation.

**Decision:** keep the full 30-event EDF+ TAL channel as the canonical training annotation source and preserve the 29-event companion as a partial independent cross-format consistency check. Never silently combine these two label sets or compute rest false-action denominators from the truncated companion as though it were complete.

**Next evidence-producing experiment:** freeze a subject-disjoint train/calibration/test EEG preprocessing contract with explicit rest denominator, channel/reference/filter/epoch parameters and leakage controls. Test a train-only signal-processing smoke before held-out evaluation. Separately investigate whether other *training-only* companion files omit initial rest events; do not generalize from S001R04.

**Four-lens review:** hiring manager—reproducible discovery of a real dataset boundary; technical reviewer—explicit missing event, exact 29-event comparison and failure history; innovation leader—real-data integrity risk removed before modeling; founder—no clinical, commercial, novelty, patentability or deployment claim.
