# Zhou2020: corrected BIDS first-session full-cohort channel audit (v0.2)

**2026-10-29 | Research / Simulation | no stage advancement.** Independently inspected **20/20** public `ses-1/run-0` `channels.tsv` files in [NEMAR nm000237](https://github.com/nemarDatasets/nm000237/commit/a291ed8a2afab3f93b85a540134dceb98092fcaf) at pinned commit `a291ed8a2afab3f93b85a540134dceb98092fcaf`. Dataset description blob `0c794cf3a1d4a744c8511593c796bc3c6cb99232` declares derivative version **1.1.0**.

## Live metadata result

**20/20 PASS.** Subjects 1–12: 41 EEG, 2 EOG, 2 MISC (45 channels). Subjects 13–20: 26 EEG, 2 EOG (28 channels). The independent JavaScript check compared exact channel-name/type/order pairs to the existing [Python gate](zhou2020_bids_channel_gate_v01.py), verified unique names and declared 500 Hz for every channel, and checked the expected per-cohort Git blob SHA-1 identifiers. These are **live metadata checks**, not an execution of the Python gate on a locally downloaded dataset.

| Subject | Rows | EEG/EOG/MISC | Upstream Git blob prefix | Result |
|---:|---:|---:|---|---|
| 1 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 2 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 3 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 4 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 5 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 6 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 7 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 8 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 9 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 10 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 11 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 12 | 45 | 41/2/2 | `ab35ee26609e` | PASS |
| 13 | 28 | 26/2/0 | `cfb30c027daf` | PASS |
| 14 | 28 | 26/2/0 | `cfb30c027daf` | PASS |
| 15 | 28 | 26/2/0 | `cfb30c027daf` | PASS |
| 16 | 28 | 26/2/0 | `cfb30c027daf` | PASS |
| 17 | 28 | 26/2/0 | `cfb30c027daf` | PASS |
| 18 | 28 | 26/2/0 | `cfb30c027daf` | PASS |
| 19 | 28 | 26/2/0 | `cfb30c027daf` | PASS |
| 20 | 28 | 26/2/0 | `cfb30c027daf` | PASS |

All 12 first-cohort files share Git blob `ab35ee26609e008c566beefb5b5e705808a08718`; all 8 second-cohort files share `cfb30c027daf79bb6865c996b7091247a1864820`. Identical **channel metadata** does not imply identical EEG recordings. Git blobs are not independent publisher-signed checksums.

## Reproduce and limits

At the pinned upstream commit, read `dataset_description.json` and `sub-N/ses-1/eeg/sub-N_ses-1_task-imagery_run-0_channels.tsv` for N=1..20. Reject unless dataset Version is 1.1.0 and DatasetType derivative. For subjects 1–12 require the existing gate's ordered 26 common EEG + 15 extra EEG + hEOG/vEOG EOG + M1/M2 MISC; for 13–20 require 26 common EEG + hEOG/vEOG EOG. Check unique names, 500 Hz and cohort Git blobs. Full per-subject paths and observed counts are in the [machine-readable registry](ZHOU2020_TRAINING_SESSION_CHANNEL_COHORT_V02_REGISTRY.json). The previously verified **12/12 fictional Python tests** remain separate evidence; they were not rerun here.

**Not tested:** other sessions/runs, complete event counts, original NPZ provenance, actual Python full-tree execution, raw EEG, held-out labels, decoding accuracy, drift-gate superiority, natural rest false actions, clinical or physical safety. The upstream **33,534 versus 33,600** event and **833 versus 840** recording discrepancies remain unresolved and do not prove specific missing records.

**Strongest existing WBI evidence:** unchanged frozen synthetic evaluator and one-subject A01E 165/288 different-day confidence-only baseline. **Largest gap:** source-complete longitudinal evaluation with independently sealed predictions and matched action coverage. **Next decisive experiment:** locally acquire corrected metadata, run `zhou2020_bids_channel_gate_v01.py`, reconcile every session/run/event denominator, then preregister a label-blind longitudinal protocol. **Stop/reframe:** reject legacy channel maps; do not claim drift/idle safety without paired held-out evidence. Four-lens review: hiring manager — bounded auditable progress; technical reviewer — one-run metadata is insufficient; innovation leader — no novelty claim; founder — no product or user validation. No private/employer data, outreach, release or commitment.
