# WBI — independent EDF+ annotation reader agreement (2026-10-25)

**Evidence gate: PASSED for one predeclared training EDF; maturity remains Research / Simulation.** This is agreement between two **software readers of the same annotation channel**, not independent human labels, EEG decoding, clinical validation, or device performance.

## Source and freeze

- PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0, **S001/S001R04.edf**, training partition only; R04 means imagined left/right fist for T1/T2.
- Publisher SHA256SUMS.txt and predeclared file SHA-256: `3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d`.
- Original training EDF and publisher checksum index were acquired through the publisher's documented unsigned S3 route. **No raw EEG was uploaded as an artifact or committed.**
- Reference readers: the existing project's `edf_annotation_contract.py` and independent **MNE-Python 1.13.2** `mne.io.read_raw_edf(..., preload=False)`. This is not a comparison to the publisher's companion `.edf.event` file.
- Predeclared absolute agreement tolerance: **0.0001 s** on every event onset and duration. Exact label and event count agreement required. Both readers process the same verified bytes.

## Executed evidence

- [Successful independent-reader CI #40166652769](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40166652769), Ubuntu / Python 3.13 / MNE 1.13.2, 2026-10-25 05:45 UTC.
- **12/12 fictional comparator contract tests passed** (mismatched label, count, onset, duration; duplicate; nonfinite; malformed fields; zero duration).
- The checksum-pinned **real training EDF** passed independent reader agreement for **all 30 events**: **T0=15, T1=8, T2=7**. Maximum observed onset difference **0.0 s** and maximum observed duration difference **0.0 s**.
- Metadata-only report SHA-256: `46cf5a93af885c0170ed9ec1ddbe001805d70d292c07e5963fbae835e37966b9`.
- [CI artifact #12588468001](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40166652769/artifacts/12588468001) contains the metadata-only JSON and `pip freeze` dependency list (14-day retention), **not** the EDF.
- At the same head, frozen synthetic reproduction, synthetic coverage and the original real TAL preflight workflows all passed; earlier stronger frozen synthetic records remain untouched.

## Reproduction

```bash
python -m unittest discover -s benchmarks/wireless-brain-interface -p test_independent_edf_annotation_review.py -v
python -m pip install "mne==1.13.2"
python benchmarks/wireless-brain-interface/independent_edf_annotation_review.py \
  --edf /secure-local/S001R04.edf \
  --sha256-index /secure-local/SHA256SUMS.txt \
  --out /tmp/wbi-independent-annotation-review.json
```

The runner workflow acquires exactly one publisher-pinned training EDF plus its checksum index; the CLI above is **offline** and requires those exact files. Reported Python and transitive dependency versions are preserved in the CI artifact. Full dependency hash locking is **TBD**.

## Interpretation and next decision

Agreement between two EDF+ software parsers removes one concrete *parsing reproducibility* uncertainty. It does **not** establish that the original annotation labels are ground truth, that EEG signal processing is correct, that a model generalizes, or that an authorization gate improves outcomes. The companion PhysioNet `.edf.event` format remains an independent cross-format reference to inspect. **No held-out subject accessed, no decoder trained, no clinical claim.**

**Next experiment:** independently parse the publisher's companion `S001R04.edf.event` annotation file and reconcile every label/onset with both EDF+ readers; explicitly document whether durations are represented or must remain unverified by that file. Then freeze a subject-disjoint preprocessing/benchmark plan and compare ungated, confidence-abstention and gated policies at matched coverage. If the cross-format labels or times disagree, halt preprocessing and repair the contract.

Primary technical sources: [PhysioNet EEGMMIDB](https://physionet.org/content/eegmmidb/1.0.0/), [EDF+ specification](https://www.edfplus.info/specs/edfplus.html), [MNE read_raw_edf documentation](https://mne.tools/stable/generated/mne.io.read_raw_edf.html), [WFDB annotation format](https://physionet.org/physiotools/wag/annot-5.htm).

**Four-lens review:** hiring manager—source-pinned and CI-backed evidence; technical reviewer—independent implementation and exact per-event agreement; innovation leader—one uncertainty removed, stage unchanged; founder—no performance, product, patentability, clinical or deployment claim.
