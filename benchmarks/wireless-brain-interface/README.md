# Wireless Brain Interface — Benchmark Contract

**Status:** protocol only; results are TBD.  
**Maturity remains:** Research / Simulation.

## Question

Can an uncertainty gate improve the trade-off between incorrect actions and retained correct actions compared with the same signal classifier without the gate?

## Reproducibility contract

Use an established public EEG benchmark and record the dataset/version, source terms, subject/session split, seeds, dependency versions, run date and commit SHA. Dataset files are not committed here.

Freeze the split and metric definitions before reporting results. Start with a simple baseline classifier. Evaluate the identical classifier with and without the uncertainty gate. Any simulated signal shift must be declared before its results are inspected.

## Metrics

| Metric | Result |
|---|---|
| Balanced accuracy | TBD |
| Calibration error | TBD |
| Incorrect-action rate | TBD |
| Coverage / abstention rate | TBD |
| Correct-action retention | TBD |
| Recovery under declared signal shift | TBD |
| End-to-end latency on declared hardware | TBD |
| Peak memory / compute | TBD |

If the selected dataset cannot support a metric, mark it N/A rather than synthesizing evidence.

## Required artifacts

- environment/dependency specification
- dataset provenance and preparation instructions
- fixed-seed baseline
- gated evaluation using the same underlying classifier
- machine-readable results with run conditions
- failure and negative-result notes
- clean-environment reproduction instructions
- limitations

## Advancement gate

Do not advance maturity merely because code exists. A later gate requires a reproducible public-data result showing a meaningful, repeatable trade-off that survives sensitivity checks or independent reproduction.

## Kill / reframe gate

Reframe if the apparent benefit disappears after accounting for suppressed correct actions, adds no material value over a simpler abstention baseline, or is unstable across subjects, sessions or seeds.

Unknown values stay TBD. Public-data results are research evidence, not clinical validation.
