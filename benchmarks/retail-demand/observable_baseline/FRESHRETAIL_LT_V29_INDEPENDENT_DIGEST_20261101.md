# Retail v2.9 — independent full-target digest reproduction (2026-11-01)

**Evidence status: VERIFIED reproducibility on two independent hosted Linux runners. Stage: Research / Architecture, unchanged.** This verifies deterministic historical-only prediction bytes and full-target coverage; it is **not** a forecast-accuracy result, official leaderboard score, blinded validation, or latent-demand evidence.

## Frozen sources and implementation

- Workflow: [retail-lt-independent-digest-v29.yml](../../../.github/workflows/retail-lt-independent-digest-v29.yml), created at commit `8f2b4cd118a3daacc30f53e77e5be763412dab3a`.
- Existing unmodified generator: [freshretail_lt_full_target_last_observed_v28.py](freshretail_lt_full_target_last_observed_v28.py); independent exact-key coverage gate: [freshretail_lt_full_target_gate_v27.py](freshretail_lt_full_target_gate_v27.py).
- Publisher: `Dingdong-Inc/FreshRetailNet-LT` revision `01c3bb306415e09d3ccd2fe762f33eb3aeb2affd`. TRAIN SHA-256 `e744c537ed16a8254c50f8456de7c5614866d4d8b6787e3cc3b67be02ea2f1e3`; EVAL SHA-256 `370ca7f995d2a059744e1659eb681e60db694bec2f80a84252426afdd2b6d626`. Both runners independently downloaded and checked source bytes before execution.
- Python 3.13, pinned PyArrow 20.0.0, GitHub Actions read-only repository permission, ephemeral private raw files. EVAL target keys and dates only; no EVAL labels/features are passed to the predictor.

## Independent execution evidence

[Successful workflow run #41312615047](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41312615047), head `8f2b4cd118a3daacc30f53e77e5be763412dab3a`.

| Host | Job | Outcome | Exact private CSV SHA-256 | Coverage |
|---|---|---|---|---|
| Ubuntu 24.04 | [job 124865977235](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41312615047/job/124865977235) | PASS | `54b5bdd957b6e3c367489b2236109df95a27e95b141d088cc23c8155be6792d1` | 70,000 / 70,000 |
| Ubuntu 22.04 | [job 124865977383](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41312615047/job/124865977383) | PASS | `54b5bdd957b6e3c367489b2236109df95a27e95b141d088cc23c8155be6792d1` | 70,000 / 70,000 |

Both original job logs were independently fetched and inspected: the publisher SHA-256 source checks succeeded; each generator reported `rows=70000`, `fallback=0`, `evaluation_labels_read=false`; each independent v2.7 gate returned `PASS_FULL_TARGET_ONLY` with `official_leaderboard_comparable=false`; each separate file-byte SHA-256 assertion reproduced the **previously published v2.8** digest exactly. The workflow additionally asserted 10,000 targets per day for seven days, no fallback and no EVAL features or labels used by the generator.

The hosted jobs uploaded **aggregate-only**, not raw publisher files or prediction rows: [Ubuntu 24.04 artifact #13085962476](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41312615047/artifacts/13085962476) and [Ubuntu 22.04 artifact #13085806646](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41312615047/artifacts/13085806646). Both reported 1,396-byte ZIP artifacts; **their ZIP bytes were not separately downloaded or hash-audited during this run**. Artifact retention is 14 days, subject to GitHub expiry.

## Decision, largest gap and next experiment

**Strongest new evidence:** identical canonical prediction bytes from two separately provisioned hosts and a prior run, using pinned sources and unmodified historical-only code. This closes the *second-host full-target reproducibility* gap. It does not provide an independent forecasting algorithm, independent source-origin attestation, Windows full-data reproduction, or model accuracy evidence.

**Largest gap:** exact publisher `psd >= 0` and `stock_hour6_22_cnt == 0` eligibility mask, publisher-consistent exploratory scoring, strong historical-only comparator and genuinely unseen confirmatory evaluation. EVAL labels are public; any future scoring on them must be explicitly exploratory, not blinded.

**Next experiment:** freeze the publisher metric and mask implementation before inspecting scoring outcomes; execute the full 70,000-target exploratory score on the pinned EVAL with a strong comparator, report the eligible count, all exclusions, per-day error and uncertainty. Keep negative results and historical v2.1 within-subset evidence.

**Kill/reframe:** halt leaderboard/commercial/latent-demand claims on label leakage, altered source/digest, mask mismatch, incomplete targets, or lack of advantage over transparent comparators. If latent demand cannot be identified, frame the work as observed-sales forecasting and partial-identification research. No maturity advance, merge, release, customer, revenue or deployment claim.

**Four lenses:** hiring manager—repeatable public-data engineering; technical reviewer—two-host digest and coverage evidence but scoring TBD; innovation leader—falsifiable comparator pending; founder—no demonstrated economic value.
