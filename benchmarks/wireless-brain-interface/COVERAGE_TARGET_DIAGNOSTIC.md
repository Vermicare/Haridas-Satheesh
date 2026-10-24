# WBI — Calibration-selected coverage-target diagnostic (2026-10-23)

**Stage:** Research / Simulation (unchanged). **Data:** fictional synthetic probabilities and drift scores, not EEG. **Method:** exact frozen `synthetic_evaluator.py` Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9`; original file and `synthetic_risk_coverage.csv` are unchanged.

## Question and protocol

Can a drift-aware gate improve incorrect-action risk over a confidence-only abstention rule at similar held-out coverage? This is a *diagnostic*, not a claim of a fair superiority test.

The extension predeclares calibration coverage targets **0.30, 0.50, 0.70**, searches the original fixed confidence and drift threshold grids using **only calibration predicted probabilities and drift scores** (not calibration labels or test data), then freezes thresholds before the held-out synthetic test. Both policies use the same underlying predictions. Threshold selection chooses the nearest calibration coverage; ties prefer a higher allowed drift, then higher confidence. Test coverage is considered approximately comparable only when the absolute difference is **≤0.05**. A risk delta is suppressed otherwise. This criterion was set in the code before test reporting; it is an engineering tolerance, not a statistical equivalence test.

## Measured held-out synthetic results

| Calibration target | Confidence: test coverage / incorrect-action risk | Gate: test coverage / incorrect-action risk | Test coverage gap | Diagnostic interpretation |
|---|---|---|---:|---|
| 0.30 | 0.3833 / 0.0978 | 0.3125 / 0.0800 | 0.0708 | Not comparable; risk delta withheld |
| 0.50 | 0.5125 / 0.1301 | 0.5833 / 0.1571 | 0.0708 | Not comparable; risk delta withheld |
| 0.70 | 0.7083 / 0.1824 | 0.7375 / 0.2373 | 0.0292 | Within tolerance; gate risk **+0.0549** absolute |

At the one approximately comparable test operating point, the gate performs worse on this fictional fixture. The coarse grids and differing candidate counts prevent a strong inference. No confidence intervals, independent synthetic regimes, public EEG, physical hardware, prospective clinical validation, or calibrated live streaming evaluation were performed.

## Reproduce

From this directory (Python 3.10+ standard library):

```sh
python -m unittest -v test_coverage_target_diagnostic.py
python coverage_target_diagnostic.py --out coverage_target_results.json
sha256sum coverage_target_results.json
```

Expected SHA-256 of the JSON under this exact source and fixture: `24979d49d9ed458f6a7ebea8af5700072d5e81b64f6540653ff4e2b7f1b5ab37`. The JSON contains thresholds, acted/incorrect counts, segment metrics, coverage-comparability flags, frozen source blob, seeds and limitations. The JSON deliberately omits timestamps to permit byte-identical reproduction.

## Failure / learning / decision

The original committed synthetic evaluator has stronger same-runtime execution evidence; this extension does **not** replace it. A calibration target does not guarantee equal test coverage, and the 0.30 and 0.50 comparisons were not close enough to score a risk delta. The 0.70 point was within tolerance but unfavorable to the gate. **No maturity advancement.** Next: preregister independent synthetic drift regimes, uncertainty intervals, calibration budget matching and a prospective public EEG subject/session split; reframe if the gate is repeatedly Pareto-dominated by simpler abstention.

## Review lenses

- **Hiring manager:** executable, candid negative result with no inflated EEG claims.
- **Technical reviewer:** can rerun tests and inspect the threshold selection and mismatch flags; needs independent environment and stronger controls.
- **Innovation leader:** an explicit stop/reframe gate prevents sunk-cost continuation.
- **Founder:** no validated device, product, clinical value, IP claim or user adoption is implied.

**Security/IP/privacy:** fictional fixtures only; no private identifiers, employer information, credentials, real EEG or collaborator data. **Unknowns:** real EEG performance, latency, physical sensors, streaming reliability, utility and novelty = TBD.
