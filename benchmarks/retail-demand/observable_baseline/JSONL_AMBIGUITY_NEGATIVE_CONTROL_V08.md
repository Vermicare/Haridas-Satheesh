# Retail v0.8 — ambiguous JSONL evidence negative control (2026-10-25)

**Stage:** Research / Architecture, unchanged. **Data:** fictional fixtures only. **Real publisher Parquet downloaded:** no. **Real forecast results:** TBD.

## Hypothesis / observed defect
Both in-memory and SQLite JSONL evaluators previously called Python `json.loads` with default settings. Default JSON decoding retains the **last** value of a duplicate object key, silently discarding conflicting earlier values, and accepts the non-standard `NaN` constant. A valid-looking report can therefore be attributed to a source whose original evidence contains conflicting fields or invalid JSON constants.

## Before-fix evidence
At commit `8837e3bff027857a23f806a8e3297f04fb529913`, four fictional regression methods ran on the existing evaluator:
- A canonical 84-day fixture was accepted by both engines (positive control).
- Conflicting duplicate `store_id` was silently accepted by both engines.
- Conflicting duplicate `hours_stock_status` was silently accepted by both engines.
- An unused `NaN` metadata field was silently accepted by both engines.

**GitHub Actions [#40203087915](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40203087915):** Ubuntu/Python 3.13 ran 63 tests, with six expected failing subtests (three defect cases × two engines). Windows test step also failed before cancellation; no complete Windows failure count is claimed.

## Correction
At commits `6dca021b2cbe64c1099f759611606f6115d69fe7` and `53e7830bc221287044161334d1da990bf85ed058`, both engines were changed to share `retail_gate.parse_json_evidence`:
- `object_pairs_hook` rejects duplicate keys at any object nesting level;
- `parse_constant` rejects `NaN`, `Infinity`, and `-Infinity`;
- malformed JSON retains the existing `EvidenceError` interface and line context;
- the forecasting, cohort-selection and metric logic remain unchanged.

**After-fix GitHub CI:** TBD until final-head run finishes and both OS results are inspected.

## Reproduce
From `benchmarks/retail-demand/observable_baseline` on the linked branch:

```bash
python -m unittest discover -v
python demo_60s.py
```

Versions/conditions: GitHub CI uses Python 3.13 on `ubuntu-latest` and `windows-latest`; exact runner image revisions and wall time: TBD. Source and test code are versioned in the draft PR branch. No publisher dataset, employer records, live inventory or private contact data are included.

## Decision and limits
This is a **JSONL ingestion-integrity** improvement, not proof of publisher-origin authenticity, dataset semantics, latent-demand recovery, forecast uplift or business value. JSON input hashing still proves byte consistency, not that a caller sourced those bytes from the publisher. A malicious but internally consistent JSONL document can still pass structural validation.

**Next experiment:** obtain the exact publisher-pinned FreshRetailNet train Parquet, independently verify its SHA-256, run the real `pyarrow` exporter and both frozen chronological evaluators, record eligible held-out counts, and preserve negative results. Reframe if actual schema or censoring semantics differ or if the stockout-aware heuristic fails against seasonal naive on comparable observed in-stock days.

**Primary sources:** [Publisher dataset card](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K), [publisher baseline](https://github.com/Dingdong-Inc/frn-50k-baseline), [FreshRetailNet paper](https://arxiv.org/abs/2505.16319). These sources describe the benchmark; they are not independent execution evidence for this repository.
