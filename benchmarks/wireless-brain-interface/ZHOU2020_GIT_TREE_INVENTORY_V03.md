# Zhou2020: pinned full-cohort Git-tree structural inventory (v0.3)

**2026-10-30 | Research / Simulation | no maturity advancement.** This is a **metadata-only** audit of the corrected NEMAR [nm000237 source tree](https://github.com/nemarDatasets/nm000237/tree/a291ed8a2afab3f93b85a540134dceb98092fcaf) pinned at `a291ed8a2afab3f93b85a540134dceb98092fcaf` (dataset description version 1.1.0, Git blob `0c794cf3a1d4a744c8511593c796bc3c6cb99232`). No EEG signals, held-out labels or trial-event rows were accessed.

## Decision-changing finding

The upstream nominal design is **20 subjects × 7 sessions × 6 runs = 840 recordings**. An independent read of **all 20 non-truncated recursive subject Git trees** found **833 `*_channels.tsv` and 833 `*_events.tsv` filenames** across **139 session directories**, not 140. The difference of **−7** is a **net filename count**, not proof that exactly seven original recordings are missing: some sessions have *extra* run files.

**Subject 20 has no `ses-6` directory at this pinned export.** It has three run metadata files in `ses-0`, nine in `ses-4` and eight in `ses-5`, rather than six each. Subjects 1 and 11 each have seven in `ses-2`. Subjects 13, 15 and 17 have below-nominal counts in particular sessions. Full per-subject session counts, source tree identifiers and all ten noncanonical session counts are in the [machine-readable registry](ZHOU2020_GIT_TREE_INVENTORY_V03_REGISTRY.json).

**Important correction to v0.2:** [the earlier 20/20 audit](ZHOU2020_TRAINING_SESSION_CHANNEL_COHORT_V02.md) examined `ses-1/run-0` and called it the *first* session. The upstream dataset is **zero-indexed**: `ses-0` is the first indexed session and `ses-1` is the second. This changes the temporal interpretation, **not** the earlier channel-map PASS counts.

## Independent first/last-session metadata cross-check

Actual pinned upstream `run-0` `channels.tsv` files were separately inspected and compared against the [existing read-only channel gate](zhou2020_bids_channel_gate_v01.py): **20/20 `ses-0` files passed** and **19/19 existing `ses-6` files passed**. Subject 20 has no `ses-6` file. For subjects 1–12, each checked file contains 41 EEG + 2 EOG + 2 MISC (45 channels); subjects 13–20 contain 26 EEG + 2 EOG (28 channels). The exact ordered name/type contract, uniqueness and 500 Hz declared frequency passed. The two cohort-specific Git blob identifiers are `ab35ee26609e008c566beefb5b5e705808a08718` and `cfb30c027daf79bb6865c996b7091247a1864820`. Repeated metadata blob identities do **not** establish signal equality.

**All 833 channel/event metadata filename pairs were subsequently verified at identical subject/session/run indices across all 20 untruncated pinned subject trees (20/20 subject-level PASS; zero orphan metadata filenames).** This is filename-level pairing, **not** event-content validation. Event TSV row counts, raw signal existence and original publisher-file checksums remain **TBD**. An initial independent JavaScript cross-check incorrectly filtered only event filenames (a comma-expression mistake), yielding an impossible 0-channel/833-event mismatch; the filter was corrected and the full 20-subject comparison rerun successfully. The failed check was not reported as a source defect. The separately reported **33,534 versus 33,600** event discrepancy remains unresolved. A missing export session is not proof that the source acquisition never occurred.

## Reproduction package

- [Read-only, fail-closed Python inventory](zhou2020_tree_inventory_v03.py) — uses only GitHub public Git-tree metadata; optionally reads `GITHUB_TOKEN` for API rate limits. Run from this folder: `python zhou2020_tree_inventory_v03.py > inventory.json`. Requires public network access; it does not open EEG files.
- [Ten fictional adversarial tests](test_zhou2020_tree_inventory_v03.py) — `python -m unittest -v test_zhou2020_tree_inventory_v03.py`. **10/10 passed locally on CPython 3.13.5**, including missing session, extra run, orphan event, truncated tree, changed ref, malformed name and renumbered-run controls.
- [Observed pinned-source count registry](ZHOU2020_GIT_TREE_INVENTORY_V03_REGISTRY.json) — provenance and per-session counts from the independent live Git-tree inspection, **not** output from the new Python script.

**Verification boundary:** the live source was audited via the connected GitHub reader and independent JavaScript checks; the newly published Python inventory has **not yet been executed against the live upstream API or in hosted Windows/Ubuntu jobs**. Its ten passing tests use invented Git-tree metadata only. No decoding or drift-aware authorization advantage was measured.

## Research decision and four-lens review

**Stage: Research / Simulation (unchanged).** **Strongest existing WBI evidence:** frozen synthetic evaluator, plus the separate one-subject A01E different-day confidence-only **165/288** baseline. **Largest new gap:** the actual session/run denominator is nonuniform, so an assumed complete 7×6 chronological split is invalid. **Next decisive experiment:** execute the pinned Python inventory against the upstream Git API, reconcile per-run event counts and original-source provenance, and preregister an explicit missingness/session-split rule *before* any new held-out label scoring.

**Kill/reframe:** fail closed if export provenance or label/split alignment is ambiguous; do not impute nonexistent `ses-6` data or discard unfavorable sessions post hoc. Reframe the drift-safety thesis if it cannot outperform simple confidence abstention at matched action coverage. Hiring manager: reproducible bounded progress; technical reviewer: source denominators before model comparisons; innovation leader: no novelty or patentability claim; founder: no user, safety or product validation.

No private/employer data, new EEG performance, external review, release or collaboration commitment.
