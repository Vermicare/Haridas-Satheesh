# Retail Prediction & Decision Intelligence

## Retail Demand Intelligence
**Status:** Research / Architecture

A retail intelligence program exploring how to combine:
- historical sales,
- inventory availability,
- price and promotion changes,
- trend signals,
- external events,
- operational constraints,
- uncertainty

to move beyond basic forecasting toward **decision-ready opportunity detection**.

---

## Demand Opportunity Radar v0.1
**Status:** Research / MVP Architecture

Core loop:

1. ingest internal and external signals,
2. create reliable features,
3. generate probabilistic forecasts,
4. correct for censored demand caused by stockouts,
5. estimate commercial opportunity,
6. surface recommended actions,
7. record outcomes for learning.

---

## Feature Factory
**Status:** Research Architecture

Reusable generation, governance and evaluation of predictive features.

---

## Derived Signal Laboratory
**Status:** Research Concept

Environment for inventing and testing derived signals from:
- trends,
- price variation,
- events,
- operational behavior,
- external factors,
- combinations of existing variables.

---

## Probabilistic Forecasting
**Status:** Research

Uses ranges such as **P10 / P50 / P90** instead of pretending a single number captures uncertainty.

---

## Stockout-adjusted Demand
**Status:** Research

Corrects historical demand so periods where an item was unavailable do not falsely appear as weak demand.

---

## Model Tournament
**Status:** Research Architecture

Controlled comparison of competing models rather than prematurely committing to one approach.

---

## Opportunity / Financial Layer
**Status:** Architecture

Translates predictive output into estimated:
- revenue upside,
- avoided loss,
- inventory impact,
- margin effect,
- operational benefit.

---

## Experiment Registry
**Status:** Architecture

Records:
- hypothesis,
- intervention,
- expected result,
- actual result,
- model/version,
- learning.

---

## Human-in-the-loop Retail Execution
**Status:** Architecture Principle

Commercial actions remain reviewable by people rather than allowing consequential automated decisions without governance.
