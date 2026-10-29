# Zhou2020: pinned full-cohort Git-tree structural inventory (v0.3)

**2026-10-30 | Research / Simulation | no maturity advancement.** This is a **metadata-only** audit of the corrected NEMAR [nm000237 source tree](https://github.com/nemarDatasets/nm000237/tree/a291ed8a2afab3f93b85a540134dceb98092fcaf) pinned at `a291ed8a2afab3f93b85a540134dceb98092fcaf` (dataset description version 1.1.0, Git blob `0c794cf3a1d4a744c8511593c796bc3c6cb99232`). No EEG signals, held-out labels or trial-event rows were accessed.

## Decision-changing finding

The upstream nominal design is **20 subjects × 7 sessions × 6 runs = 840 recordings**. An independent read of **all 20 non-truncated recursive subject Git trees** found **833 `*_channels.tsv` and 833 `*_events.tsv` filenames** across **139 session directories**, not 140. The difference of **−7** is a **net filename count**, not proof that exactly seven original recordings are missing: some sessions have *extra* run files.

**Subject 20 has no `ses-6` directory at this pinned export.** It has three run metadata files in `ses-0`, nine in `ses-4` and eight in `ses-5`, rather than six each. Subjects 1 and 11 each have seven in `ses-2`. Subjects 13, 15 and 17 have below-nominal counts in particular sessions. Full per-subject session counts, source tree identifiers and all ten noncanonical session counts are in the [machine-readable registry](ZHOU2020_GIT_TREE_INVENTORY_V03_REGISTRY.json).

**Important correction to v0.2:** [the earlier 20/20 audit](ZHOU2020_TRAINING_SESSION_CHANNEL_COHORT_V02.md) examined `ses-1/run-0` and called it the *first* session. The upstream dataset is **zero-indexed**: `ses-0` is the first indexed session and `ses-1` is the second. This changes the temporal interpretation, **not** the earlier channel-map PASS counts.

## Independent first/last-session metadata cross-check

Actual pinned upstream `run-0` `channels.tsv` files were separately inspected and compared against the [existing read-only channel gate](zhou2020_bids_channel_gate_v01.py): **20/20 `ses-0` files passed** and **19/19 existing `ses-6` files passed**. Subject 20 has no `ses-6` file. For subjects 1–12, each checked file contains 41 EEG + 2 EOG + 2 MISC (45 channels); subjects 13–20 contain 26 EEG + 2 EOG (28 channels). The exact ordered name/type contract, uniqueness and 500 Hz declared frequency passed. The two cohort-specific Git blob identifiers are `ab35ee26609e008c566beefb5b5e705808a08718` and `cfb30c027daf79bb6865c996b7091247a1864820`. Repeated metadata blob identities do **not** establish signal equality.

**All 833 channel/event metadata filename pairs were subsequently verified at identical subject/session/run indices across all 20 untruncated pinned subject trees (20/20 subject-level PASS; zero orphan metadata filenames).** This is filename-level pairing, **not** event-content validation. Event TSV row counts, raw signal existence and original publisher-file checksums remain **TBD**. An initial independent JavaScript cross-check incorrectly filtered only event filenames (a comma-expression mistake), yielding an impossible 0-channel/833-event mismatch; the filter was corrected and the full 20-subject comparison rerun successfully. The failed check was not reported as a source defect. The separately reported **33,534 versus 33,600** event discrepancy remains unresolved. A missing export session is not proof that the source acquisition never occurred.

## Upstream source-manifest reconciliation

A separate read of the pinned upstream [`sourcedata/sourcedata_provenance.json`](https://github.com/nemarDatasets/nm000237/blob/a291ed8a2afab3f93b85a540134dceb98092fcaf/sourcedata/sourcedata_provenance.json) (Git blob `c80403a970eb2c064e74daf50dbb08115e8299ff`) lists **853 entries: 833 original NPZ run files and 20 subject ZIP files**. All 833 NPZ entries have 64-character SHA-256 strings, **but the NPZ bytes were not independently downloaded or hashed**. Their per-subject/per-session run-count matrix matches **all 140 positions** of the corrected BIDS metadata inventory, including subject 20's absent seventh session and the extra-run sessions. Source `session_1..7` corresponds by index to BIDS `ses-0..6`; source `run_01..N` entries are consecutive within each represented session, matching the observed BIDS `run-0..(N-1)` numbering by count.

**Interpretation:** The 833-versus-840 nominal difference is **already present in the upstream source inventory**, not merely a missing-file count introduced by the corrected BIDS export. This is a structural/count reconciliation, **not** an independent byte-level source-to-BIDS mapping, proof that original signals are complete, or an explanation for the separate event-row discrepancy. The provenance manifest is public but not publisher-cryptographically signed.

## Reproduction package

- [Read-only, fail-closed Python inventory](zhou2020_tree_inventory_v03.py) — uses only GitHub public Git-tree metadata; optionally reads `GITHUB_TOKEN` for API rate limits. Run from this folder: `python zhou2020_tree_inventory_v03.py > inventory.json`. Requires public network access; it does not open EEG files.
- [Ten fictional adversarial tests](test_zhou2020_tree_inventory_v03.py) — `python -m unittest -v test_zhou2020_tree_inventory_v03.py`. **10/10 passed locally on CPython 3.13.5**, including missing session, extra run, orphan event, truncated tree, changed ref, malformed name and renumbered-run controls.
- [Observed pinned-source count registry](ZHOU2020_GIT_TREE_INVENTORY_V03_REGISTRY.json) — provenance and per-session counts from the independent live Git-tree inspection, **not** output from the new Python script.

**Verification boundary:** the live source was audited via the connected GitHub reader and independent JavaScript checks; the published Python inventory has now been executed against the pinned public upstream Git API in hosted Ubuntu and Windows jobs (see dated addendum). Its ten regression tests on each OS still use invented Git-tree metadata only. No decoding or drift-aware authorization advantage was measured.

## Research decision and four-lens review

**Stage: Research / Simulation (unchanged).** **Strongest existing WBI evidence:** frozen synthetic evaluator, plus the separate one-subject A01E different-day confidence-only **165/288** baseline. **Largest new gap:** the actual session/run denominator is nonuniform, so an assumed complete 7×6 chronological split is invalid. **Next decisive experiment:** independently verify sampled original NPZ checksums and reconcile per-run event counts, and preregister an explicit missingness/session-split rule *before* any new held-out label scoring.

**Kill/reframe:** fail closed if export provenance or label/split alignment is ambiguous; do not impute nonexistent `ses-6` data or discard unfavorable sessions post hoc. Reframe the drift-safety thesis if it cannot outperform simple confidence abstention at matched action coverage. Hiring manager: reproducible bounded progress; technical reviewer: source denominators before model comparisons; innovation leader: no novelty or patentability claim; founder: no user, safety or product validation.

No private/employer data, new EEG performance, external review, release or collaboration commitment.

## 2026-10-30 addendum — independent hosted Python execution

[GitHub Actions run #40942169065](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40942169065), at [research commit `f660b8a`](https://github.com/Vermicare/Haridas-Satheesh/commit/f660b8a3f2db6fd9e55d20ef9df054dba44ea0fc), completed **successfully on Ubuntu and Windows**. Both job logs were independently inspected. The unchanged `zhou2020_tree_inventory_v03.py` executed against the pinned upstream GitHub Git-tree API; both runs passed **10/10 fictional regression tests** and independently reported **20 subjects, 139 session directories, 833 paired channel/event metadata runs, absent `sub-20/ses-6`**. Both preserved a derived metadata-only JSON artifact: [Ubuntu artifact](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40942169065/artifacts/12926339862) and [Windows artifact](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40942169065/artifacts/12927936844), each expiring **2026-11-12 UTC**. This is execution of the original pinned Python inventory, not only a separate JavaScript tree count.

The same jobs also reran the frozen original synthetic evaluator, and the log-reported CSV SHA-256 matched its original execution record (`65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`). The original evaluator and synthetic outputs were not modified.

**Evidence boundary:** GitHub job logs and artifact metadata were inspected; the two artifact ZIP contents have **not** been independently compared byte-for-byte. No original NPZ bytes/checksums, EEG signals, event rows, held-out labels or longitudinal decoding performance were verified. The dataset is not assumed complete. Stage remains **Research / Simulation**. Next: preregister checksum sample and missingness/split protocol, then verify original-file hashes and event-row provenance without leakage.
