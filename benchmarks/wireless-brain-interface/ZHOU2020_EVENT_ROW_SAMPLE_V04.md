# Zhou2020 v0.4 — pinned event-row heterogeneity negative control

**2026-10-30 · Research / Simulation · no maturity advancement.** This is a deliberately narrow, **nonrandom three-file structural audit**, not a full-cohort trial count or a decoding experiment.

## Decision-changing observation

The corrected [NEMAR Zhou2020 v1.1.0 tree](https://github.com/nemarDatasets/nm000237/tree/a291ed8a2afab3f93b85a540134dceb98092fcaf) was pinned to commit `a291ed8a2afab3f93b85a540134dceb98092fcaf`. A live GitHub read of three event TSVs found:

| Pinned public event TSV | Git blob SHA-1 | Event rows |
|---|---|---:|
| `sub-1/ses-0/.../run-0_events.tsv` | `0997cba4376368265a05a10f6958218dee6fb0f5` | **40** |
| `sub-20/ses-0/.../run-0_events.tsv` | `de1390ba9e0a19c678dffe638dbb32e708029be0` | **80** |
| `sub-20/ses-5/.../run-7_events.tsv` | `e184dfdf8454a1fde7da15e369fe459ed3e25de9` | **40** |

**The assumption that every recording contains exactly 40 event rows is falsified by a pinned 80-row file.** The three files contain 160 rows, not the 120 predicted by a uniform 40-row assumption. This does **not** establish how the full 33,534 publisher-reported event rows distribute over 833 recording-metadata pairs; it also does not establish why nominal 33,600 differs. The prior [v0.3 inventory](ZHOU2020_GIT_TREE_INVENTORY_V03.md) still establishes 833 paired metadata filenames, 139 sessions, and an absent `sub-20/ses-6` directory; these are separate questions.

## Executable reproduction and negative controls

- [Read-only pinned sampler](zhou2020_event_row_sample_v04.py) fetches **only three** fixed public TSV blobs, verifies Git blob SHA-1 and counts newline-delimited, structurally valid rows. It never interprets `trial_type` or `value` fields. A mismatch fails closed.
- [Thirteen fictional parser tests](test_zhou2020_event_row_sample_v04.py) cover BOM, LF/CRLF, absent final newline, bad headers, blank lines, malformed field counts, NUL/oversize, bad SHA, wrong row count and altered mock input.
- [Cross-platform workflow](../../.github/workflows/wbi-zhou2020-event-row-sample.yml) is configured for Ubuntu and Windows; [initial run #40951600999](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40951600999) was **queued when this report was authored**. Hosted execution outcome remains **TBD** until job logs and outputs are inspected.
- [Machine-readable registry](ZHOU2020_EVENT_ROW_SAMPLE_V04_REGISTRY.json) records pinned paths, source blob IDs, observed counts, negative controls and limitations.

Run locally from the benchmark directory: `python -m unittest -v test_zhou2020_event_row_sample_v04.py`, then `python zhou2020_event_row_sample_v04.py --output sample.json`. Network access is needed only for the second command.

## Evidence-integrity limitation

During the exploratory manual inspection that motivated this diagnostic, **previews of three public event TSVs exposed their `trial_type` values**. No EEG signals, held-out decoder predictions or model performance were accessed or evaluated, but this work **must not be represented as fully label-blind preregistration**. The executable counts rows without interpreting label values; that narrower statement is verifiable. No label-informed threshold or model choice is permitted from these previews. A future confirmatory comparison needs a frozen protocol and independently controlled held-out boundary, with this disclosure retained.

## Decision and next gate

**Stage unchanged: Research / Simulation.** Strongest new evidence is the pinned 40/80/40 event-row contrast. Largest gap is a full 833-file event-row audit and original NPZ byte provenance, not new EEG accuracy. Next: freeze subject-specific split/missingness rules and the exposure disclosure, verify original-file checksums, then reconcile event counts without label-based tuning. If any pinned file hash differs, fail closed; if a clean evaluation boundary cannot be demonstrated, treat outcomes as exploratory. No clinical, authorization-safety, external-review, novelty or product claim.

**Four lenses:** hiring manager — a falsified simplifying assumption; technical reviewer — three nonrandom blobs, no denominator extrapolation; innovation leader — no novelty claim; founder — no real-world performance evidence. No employer or private data.
