# WBI — Rest-aware action-denominator contract v0.1 (2026-10-25)

**Evidence class:** executable **fictional event-score** contract, NOT real EEG decoding, rest-state false-action validation, continuous-time safety, clinical testing or device validation. Public maturity remains **Research / Simulation**. This is an additive preflight; the [frozen synthetic evaluator](SYNTHETIC_EVALUATOR.md), its [independent cross-platform reproduction](FROZEN_CROSS_PLATFORM_REPRO_2026_10_24.md), and [subject split](PHYSIONET_SUBJECT_SPLIT_PREFLIGHT_2026_10_24.md) are unchanged.

## Decision-changing protocol correction

The existing PhysioNet split preflight maps **T0 = rest-exclude**, appropriately for **left-vs-right imagery classifier training**. It must **not** be interpreted as permission to exclude T0 from the **action safety evaluation**. Any left/right action emitted on T0 is a false action. Otherwise a seemingly safe two-class decoder could score well by silently discarding the idle denominator.

The checksum-verified training EDF **S001R04** previously yielded **15 T0, 8 T1, 7 T2** annotations. The publisher's WFDB companion omits one initial T0, yielding **14 T0**. The [cross-format discrepancy record](WFDB_COMPANION_RECONCILIATION_2026_10_25.md) establishes why annotation-source completeness matters. This new contract uses only **fictional** event scores; it does not read those real EEG waveforms or annotations.

## Contract and negative controls

- [Executable evaluator](rest_aware_evaluation_contract.py), [16 adversarial tests](test_rest_aware_evaluation_contract.py) and [Linux/Windows CI workflow](../../.github/workflows/wbi-synthetic-coverage.yml); standard-library Python 3.13, imports the existing frozen subject partition generator.
- Three policies consume **the same fictional scores**: ungated action, confidence abstention and confidence-plus-drift gate. Rest is not a third decoded class; **every act on T0 counts as incorrect**.
- Predeclared grids: confidence 0.50/0.60/0.70/0.80/0.90; drift 0.30/0.50/0.70/1.00; minimum imagery-event coverage 0.50. The **same** objective (minimize rest event false-action rate, then incorrect-action risk, then maximize imagery coverage) selects each policy on **calibration subjects only**; thresholds are frozen for disjoint test subjects.
- Reports **imagery coverage** and **rest false actions per rest event** separately, plus incorrect-action risk and retained correct imagery. No matched-coverage superiority claim: thresholds can yield different test coverage. Later analysis must match imagery coverage and report the full risk/coverage trade-off and subject-level uncertainty.
- Rejects cross-partition subjects, missing all T0 or imagery events, duplicate IDs, unknown labels, nonfinite/out-of-range scores and invalid thresholds. Zero actions yield JSON null risk rather than NaN.
- **Known negative finding:** dropping only *some* T0 events still passes the minimum-denominator check. It is **not** a source-completeness validator. Actual evaluation must first reconcile full EDF+ TAL annotations, file checksums, event timing, duration and per-record counts; never substitute the 29-event companion silently.

## Reproduce

From `benchmarks/wireless-brain-interface`:

```sh
python -m unittest -v test_rest_aware_evaluation_contract.py
python rest_aware_evaluation_contract.py > rest_aware_contract_demo.json
sha256sum rest_aware_contract_demo.json
```

**Local preparation (2026-10-25):** CPython 3.13.5/Linux, **16/16** tests passed using a **minimal local stand-in** that implements the same frozen subject-order algorithm. Local demo SHA-256 `45e77bd0d95ae939614bf7569a251132f9bf7dd42ea37a1d17767bcc07e45de2`. This is not yet independent CI verification against the actual repository module; the workflow is configured to test that separately on Linux and Windows. Actual CI result: **TBD until verified**. Do not conflate the hand-authored fictional fixture's favorable gate output with evidence of performance.

## Next evidence gate and stop rule

Before scoring held-out EEG: (1) verify complete canonical T0/T1/T2 annotations and explicit rest windows; (2) freeze channel/reference/filter/epoch/artefact decisions and train-only fit; (3) train a simple decoder using training subjects only; (4) calibrate confidence and any drift score on calibration subjects only; (5) compare all policies at **matched imagery coverage**, with rest false activations per **minute of actual idle exposure**, useful-action retention and subject-level uncertainty; (6) preserve versions, checksums, exclusions, failures and negative results. One-session PhysioNet EEG cannot establish longitudinal drift.

**Kill/reframe:** if the extra drift gate does not beat simple abstention at comparable coverage, or suppresses useful actions excessively, narrow the contribution. **No release, deployment, external review, clinical or patentability claim.**

**Four lenses:** Hiring—inspectable negative controls; technical—denominator/completeness and calibration separation; innovation—explicit stop gate; founder—no measured utility, customer adoption or defensible moat established. No employer, personal, or outreach data.
