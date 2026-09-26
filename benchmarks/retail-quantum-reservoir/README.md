# Quantum Reservoir Challenge — Retail Demand Intelligence

**Status:** Experimental research track — simulated quantum method, **not** evidence of quantum advantage  
**Parent benchmark:** [Retail Demand Intelligence](../retail-demand/README.md)  
**Results:** **TBD**

## Question

Can a small quantum-reservoir representation extract useful temporal structure from retail-demand sequences under the **same information, folds and evaluation rules** as a classical reservoir?

This experiment is deliberately allowed to fail. Its purpose is to test whether a quantum dynamical feature map contributes measurable value after controlling for leakage, classical capacity and model-selection effort.

## Why this is worth testing

- Otieno et al., *EPJ Quantum Technology* (2026), used quantum reservoirs of up to six interacting qubits for financial time-series forecasting: https://doi.org/10.1140/epjqt/s40507-026-00563-2
- Das et al., *Physical Review Research* (2026), benchmarked nonlinear memory and chaotic time-series prediction in Jaynes-Cummings quantum reservoirs: https://doi.org/10.1103/ffd3-ytbt
- Experimental correlated-spin QRC was reported in *Physical Review Letters* (2026): https://doi.org/10.1103/r8ww-qw7j
- A 2026 digital-QRC study on ATM cash-demand forecasting reported that QRC did **not** outperform Prophet on MAE/NMSE: https://arxiv.org/abs/2606.04686

These works motivate an experiment; they do not establish that QRC improves retail demand forecasting.

## Experiment boundary

The parent FreshRetailNet-50K benchmark remains the source of truth for dataset provenance, chronological splitting and retail metrics.

~~~text
                    SAME RETAIL SEQUENCE
                           |
             +-------------+-------------+
             |                           |
             v                           v
     CLASSICAL RESERVOIR          QUANTUM RESERVOIR
       Echo State Network        small simulated qubit system
             |                           |
             v                           v
        ridge readout                ridge readout
             |                           |
             +-------------+-------------+
                           |
                    SAME TEST FOLDS
                           |
              WAPE / MAE / runtime
~~~

The readout family is intentionally shared. The reservoir is the primary changed component.

## v0.1 implementation

### Classical control

Use an Echo State Network with a fixed random seed and ridge-regression readout. Record reservoir dimension, spectral radius, leak rate, input scaling, ridge coefficient, random seed and train/inference time.

### Quantum arm

Start with a **classically simulated** small quantum reservoir. Do not imply access to or execution on quantum hardware.

Record simulator/library and version, qubit count, input encoding, circuit/Hamiltonian definition, connectivity, evolution depth/time, measured observables, temporal multiplexing if used, shots if sampled, random seeds, ridge coefficient and simulation/inference time.

## Fair-comparison rules

1. Identical train/test observations and forecast horizons.
2. Identical chronological folds.
3. No future stock status, target or derived future information.
4. Same output/readout family unless an ablation explicitly tests otherwise.
5. Hyperparameter search budgets must be recorded and bounded.
6. Report compute/runtime; do not compare accuracy while hiding a radically different search cost.
7. Report classical reservoir size and include at least one capacity- or parameter-budget-aware comparison.
8. No claim of quantum advantage from simulator performance alone.
9. Run multiple fixed seeds where stochasticity exists; retain dispersion, not only the best run.
10. Negative results remain in the repository.

## Predeclared results

| Metric | Seasonal naive | Classical reservoir | Quantum reservoir |
|---|---:|---:|---:|
| WAPE | TBD | TBD | TBD |
| MAE | TBD | TBD | TBD |
| Train/simulation time | TBD | TBD | TBD |
| Inference time | TBD | TBD | TBD |
| Peak memory | TBD | TBD | TBD |
| Seeds / repeats | TBD | TBD | TBD |

## Required ablations

- quantum reservoir vs classical ESN,
- quantum reservoir vs seasonal naive,
- full quantum-derived feature vector vs reduced feature vector,
- at least two qubit/reservoir capacities,
- noiseless simulation vs a declared noise model only after the noiseless pipeline is reproducible.

A gain that disappears under reasonable seed, capacity or search-budget controls is not treated as evidence.

## Advancement gate

This track stays **Experimental / Simulation** until the parent Retail v0.1 benchmark is reproducible, both reservoirs run through the same evaluator, configurations and outputs are machine-readable, repeated runs exist, and the comparison survives leakage/fairness tests.

Even then, a simulated improvement supports only: **under this declared simulation and benchmark configuration, the QRC representation changed forecasting performance relative to the declared classical controls.** It does not establish hardware speedup, commercial advantage or general quantum advantage.

## Kill / reframe gate

Stop or reframe if QRC cannot beat simple controls after fair tuning; apparent gains require materially larger search/compute budgets; results are unstable across seeds/folds; simulation cost overwhelms predictive value; a classical reservoir captures the effect more simply; or this track distracts from validating the parent stockout-aware thesis.

A clean negative result is useful evidence.

## Milestone path

~~~text
v0.1  deterministic simulator + ESN comparator
  |
v0.2  repeated folds/seeds + fairness ablations
  |
v0.3  noise-aware simulation
  |
v0.4  optional real quantum-hardware replication
~~~

No later milestone is implied by creation of this specification.

## Next executable artifact

Build a tiny deterministic smoke benchmark first:

~~~text
sequence -> classical reservoir -> ridge readout -> metrics.json
sequence -> quantum simulator   -> ridge readout -> metrics.json
~~~

Only after that smoke test passes should the track consume the pinned FreshRetailNet subset.
