# WBI — first real PhysioNet EDF structural smoke (2026-10-25)

**Stage remains Research / Simulation.** This is one *training-subject* EDF acquisition and structural/checksum preflight, **not** a decoded EEG experiment, subject-generalization test, drift evaluation, clinical validation or product claim.

## Why this matters

The existing subject-disjoint [preregistered split](PHYSIONET_SUBJECT_SPLIT_PREFLIGHT_2026_10_24.md) had never read original EDF bytes. This experiment tests the data-access and source-integrity boundary before any model training or held-out test access. The frozen [synthetic evaluator](SYNTHETIC_EVALUATOR.md), its [same-runtime execution record](EXECUTION_RECORD.md), and its [independent cross-platform reproduction](FROZEN_CROSS_PLATFORM_REPRO_2026_10_24.md) are unchanged.

## Predeclared source and checks

- **Source:** [PhysioNet EEG Motor Movement/Imagery v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), DOI 10.13026/C28G6P, ODC-By-1.0.
- **One selected file:** `S001/S001R04.edf`, from the frozen **train** partition; imagined unilateral left/right fist task. No calibration or held-out test subjects accessed.
- **Checksum index:** `https://physionet.org/files/eegmmidb/1.0.0/SHA256SUMS.txt`; require one exact entry and exact local byte match.
- **Structural checks:** EDF version, 65 signals (64 EEG + one annotation), unique channel labels, 160 Hz for this nonexception subject, positive record count/duration, exact header length and payload byte count.
- **Safety:** bounded 8 MiB EDF and 512 KiB index downloads; no raw EEG committed or uploaded. Output is a machine-readable metadata-only report. This does not decode events or establish signal quality. Publisher-index consistency over HTTPS is **not independent cryptographic attestation** of origin.

## Reproduce

From `benchmarks/wireless-brain-interface/`:

```sh
python -m unittest -v test_edf_smoke.py
python edf_smoke.py --fetch --out edf-smoke.json
```

The second command needs network access to the public dataset. The JSON report explicitly records that decoder training, event decoding and test-subject access were not performed.

## Evidence and failure log

- Local CPython 3.13.5 / Linux: **10/10 fictional adversarial contract tests passed** (bad SHA, duplicate/missing index entry, truncated bytes, 128 Hz substitution, missing annotations, corrupt header, duplicate channel).
- [First CI run #40121746984](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40121746984): 10/10 tests passed on CPython 3.13.16 / Ubuntu. **One real S001R04 EDF acquisition and checksum/structure validation completed** at 18:44:36 UTC on 2026-10-24; the log reports SHA-256 `3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d`, **125 data records, 64 EEG channels at 160 Hz**. The redundant second network acquisition exceeded the eight-minute job budget; CI was cancelled and **no report artifact was uploaded**. This is a **partial success with an operational timeout**, not a passing workflow.
- **Recovery:** use one bounded network acquisition per job and verify against both the publisher checksum index and the first observed fixed SHA-256. A new CI attempt is required; until it passes, complete CI status is **TBD**.
- **Negative result:** independent repeated download is not yet demonstrated; network latency was significant. Do not claim two successful acquisitions.

## Next evidence gate

Obtain a passing metadata-only CI report; inspect annotation events using a pinned reader and independently verify run-specific T0/T1/T2 mapping, with event counts and exclusions. The frozen split places sampling-rate exceptions **S088 and S100 in train** and **S092 in held-out test**; inspect the two train exceptions first and leave S092 untouched until the pipeline is frozen. Then run a frozen train/calibration-only preprocessing and decoder baseline before touching held-out subjects. Reframe any drift-gate benefit claim if confidence-only abstention remains superior at matched coverage. Unknown decoding accuracy, uncertainty, cross-subject generalization, longitudinal drift and safety remain **TBD**.

**Four lenses:** hiring manager—traceable first real-byte acquisition; technical reviewer—checksum and header checks are necessary but not event/label validation; innovation leader—negative timeout preserved; founder—no performance, users, deployment, novelty or patentability claim. No employer, personal, collaborator or private data are published.
