# Zhou2020 v0.5 — full pinned corrected event-TSV structural census

**2026-10-30 UTC · Wireless Brain Interface · Research / Simulation (unchanged).** This is a **metadata/event-row integrity result**, not EEG decoding, clinical validation, human authorization safety, signal provenance, or a fully label-blind experiment.

## Decision-changing result

The corrected public [NEMAR Zhou2020 dataset at pinned ref a291ed8](https://github.com/nemarDatasets/nm000237/tree/a291ed8a2afab3f93b85a540134dceb98092fcaf) contains **833 paired channel/event metadata filenames across 20 subjects and 139 session directories** (previously established in v0.3). A new bounded read-only census fetched **all 833 event TSV files**, verified each raw file against its exact Git-tree blob SHA-1, and counted structurally valid tab-separated rows **without interpreting trial_type or value fields**.

**Observed total: 33,534 structural event rows.** This **numerically matches** the publisher's previously reported **33,534** trials, but row-count equality alone does not prove event semantics or original EEG-recording integrity.

| Event rows per recording TSV | Number of files |
|---:|---:|
| 18 | 1 |
| 37 | 4 |
| 38 | 2 |
| 39 | 4 |
| 40 | **815** |
| 56 | 1 |
| 80 | 6 |
| **Total** | **833** |

**18 of 833 files** are not 40-row files. The nominal **840 × 40 = 33,600** count decomposes as **833 × 40 = 33,320** plus **+214** from observed per-file heterogeneity, giving **33,534** (**−66** relative to nominal). This is an accounting reconciliation, **not** proof that seven specific original recordings were lost or that every TSV row represents an independently verified original trial. The absent subject-20 seventh session and irregular run sets remain documented separately in v0.3.

## Reproducible implementation

- [Read-only full-census CLI](zhou2020_event_census_v05.py) reuses the unchanged [v0.3 Git-tree structural audit](zhou2020_tree_inventory_v03.py) and [v0.4 bounded TSV parser](zhou2020_event_row_sample_v04.py). It enumerates all 833 event blob paths from the pinned Git tree, checks each file's Git blob SHA-1 and row structure, and emits aggregate summaries plus file paths, source hashes, byte sizes and row counts only. It does **not** include trial-type values, EEG signals, model predictions or contact information.
- [Eleven fictional fail-closed controls](test_zhou2020_event_census_v05.py) cover altered source blobs, malformed rows, missing/duplicate census entries, invalid worker limits, broken inventory prerequisites, malformed Git blob IDs, oversize sources and canonical serialization.
- [Hosted workflow](../../.github/workflows/wbi-zhou2020-event-census.yml) runs the fictional tests and full pinned public-source census on both Ubuntu and Windows. The 833-file census is not simulated.
- Reproduce on a networked Python 3.13 environment from this directory: `python -B -m unittest -v test_zhou2020_event_census_v05.py`, then `python -B zhou2020_event_census_v05.py --output census.json --workers 6`. Source access is public; no GitHub write or private credentials required.

## Independently inspected hosted evidence

**Final code-bearing [GitHub Actions run #40981177763](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40981177763), head 67acc3d7f574ef2bf23a385b1cb1e6a196a78321: completed successfully.** Ubuntu CPython **3.13.17** and Windows CPython **3.13.16** each passed **11/11 fictional tests**, then fetched/verified all 833 pinned public event files and reported **33,534** rows. Both full-census job logs were inspected.

The two original hosted ZIP artifacts were independently downloaded, checked for ZIP integrity, rehashed and parsed:

| Artifact | GitHub ID | ZIP SHA-256 |
|---|---:|---|
| [Ubuntu](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40981177763/artifacts/12944434131) | 12944434131 | `5b161c78785033daca3bbb65ae125554202ef0e14801bddd562df5fc9b61a609` |
| [Windows](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40981177763/artifacts/12943864747) | 12943864747 | `5e333e2d1f18cada237f86ac82d7d4ff441bfd5f1ce2697998c73ce59b511ef6` |

Each ZIP contains a single **216,160-byte JSON file**. The extracted JSON files are **byte-identical** (SHA-256 `b891a3edfd8b1c535bc50032f7d46717de4f45d0eddbfd500f06430e757ec6b1`). An independent standard-library verifier confirmed 833 unique paths, 20 subjects, 139 sessions, source hash syntax, exact row histogram, and agreement between all per-file, per-subject and per-session totals. ZIP hashes differ because ZIP metadata differs. Artifacts expire **2026-11-13 UTC**.

The earlier Ubuntu-only successful [run #40980966213](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40980966213) is retained as additional provenance; the final cross-platform run is the primary evidence.

## Research decision and limitations

**No maturity advancement.** The result closes the *structural corrected-event-file row-count* question and invalidates a universal 40-row assumption, but does **not** verify the original NPZ/EEG bytes, sensor signal integrity, class/event semantics, independent participant labels, subject-specific longitudinal protocol, clinical safety or any model improvement.

**Label-exposure disclosure:** earlier exploratory human inspection of three public event-file previews exposed trial-type values. The v0.5 executable itself never interprets those fields, but this study must **not** be described as fully label-blind preregistration. No decoder thresholds or accuracy results were derived from this census.

**Next decisive experiment:** independently verify a preregistered subset of original NPZ/EEG recording hashes against source provenance, reconcile the event-to-original-recording mapping and session-specific missingness, then freeze an untouched subject-specific longitudinal decoder/abstention comparison before any new held-out-label inspection. **Stop/reframe** any cross-session safety claim if clean held-out boundaries, source integrity or matched-coverage risk improvement cannot be demonstrated.

**Four lenses:** hiring manager — inspectable end-to-end source-integrity reconciliation; technical reviewer — bounded 833-file checksum/row audit and independently identical hosted artifacts, but not original signal authentication; innovation leader — no novelty or patentability claim; founder — no users, deployments, clinical or business outcomes. No release, merge, confidential data or external commitment.
