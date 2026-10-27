# Wireless Brain Interface — Benchmark Contract

**Status:** [frozen synthetic evaluator](SYNTHETIC_EVALUATOR.md) has a [preserved two-run same-runtime execution record](EXECUTION_RECORD.md), including byte-identical risk–coverage CSV SHA-256 `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`. Its **synthetic** results do not show gate superiority over simple abstention. Real public-EEG results remain **TBD**. [Draft PR #16](https://github.com/Vermicare/Haridas-Satheesh/pull/16) contains additional independently hosted cross-OS reproduction and a metadata-only prospective EEG split protocol; it is unmerged and does not establish EEG decoding.  
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
