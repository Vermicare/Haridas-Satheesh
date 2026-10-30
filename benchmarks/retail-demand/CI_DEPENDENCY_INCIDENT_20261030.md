# Retail unified synthetic CI — missing NumPy dependency, 2026-10-30

**Status:** repaired and independently re-executed on hosted Ubuntu and Windows; **maturity:** Research / Architecture (unchanged). No forecasting metric, publisher data, frozen prediction, evaluator or research outcome changed.

## Reproducible failure

The existing `.github/workflows/retail-observable-baseline.yml` runs `python -m unittest discover -v` over the *entire* `benchmarks/retail-demand/observable_baseline` directory. After addition of the TRAIN-only v2.6 test module, this generic workflow began discovering `test_freshretail_lt_train_hourly_identity_v26.py`, which imports NumPy. Unlike the dedicated v2.6 workflow, the generic workflow did **not** install NumPy.

[Original failing unified CI #41022315777](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41022315777), commit `19f09784749a02e4c8bee3c031d744144ae896cc`: Ubuntu failed on test discovery with `ModuleNotFoundError: No module named 'numpy'` (225 tests ran, one import error); the Windows matrix job was cancelled under fail-fast. This was an **environment/dependency regression**, not a failing numeric identity assertion or contradictory publisher dataset result. Earlier similar notifications are not proof of any other root cause.

## Minimal correction

Research-branch commit [`762ad401afcce4201b172866d15c0424fefe6c49`](https://github.com/Vermicare/Haridas-Satheesh/commit/762ad401afcce4201b172866d15c0424fefe6c49) adds a pinned `python -m pip install --disable-pip-version-check numpy==2.2.6` step before the unified discovery. The pin exactly matches the dedicated v2.6 fictional-control workflow; no test is skipped and no scoring code is changed.

## Final-code-head independent verification

[GitHub Actions #41035327259](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41035327259), **completed SUCCESS** on the correction commit:

| Host | Unified tests | Demo | Result |
| --- | ---: | --- | --- |
| Ubuntu, Python 3.13 | 236/236 | PASS | SUCCESS |
| Windows, Python 3.13 | 236/236 | PASS | SUCCESS |

Both hosted job logs were independently inspected. They show the NumPy installation, 236 completed tests with no failures, and a successful fictional-only demo. The workflow file was reread from the research branch and contains the pinned dependency step.

**Scope/unknowns:** This validates the unified fictional test suite on two hosted operating systems, not any real demand, forecasting superiority, latent-demand identifiability, business benefit, external review, or deployment. Future test modules must declare dependencies or be explicitly separated into bounded workflow environments; cross-workflow test discovery must not silently expand the required dependency set. No release, merge or maturity advance.
