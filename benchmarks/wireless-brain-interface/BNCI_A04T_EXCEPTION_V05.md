# WBI A04T training-session structural exception — v0.5 (2026-10-28 IST)

**Scope:** reproducible, metadata-only inspection of a public **training** file; not EEG decoding, action authorization, clinical safety, device validation, or independent publisher authentication. **Maturity: Research / Simulation, unchanged.**

## Question and preregistered acceptance rule

The original [BCI Competition IV dataset 2a description](https://www.bbci.de/competition/iv/desc_2a.pdf) documents an **A04T-specific EOG baseline exception**: only the eye-movement condition was recorded. The previously observed A01T/A02T training files each have three cue-free baseline blocks plus six 48-cue task blocks. A validator that hard-codes nine blocks would wrongly reject a legitimate A04T training file.

Before downloading A04T, commit a metadata-only gate accepting **one to three leading cue-free baseline blocks**, followed by **exactly six 48-cue task blocks** (288 total), 25 signal channels and 250 Hz. Reject misplaced cues, malformed structure, privacy/provenance contradictions, performance claims and unapproved network redirects. Do not inspect class-label values or persist raw EEG.

## Source and reproducibility

- Official catalog: https://bnci-horizon-2020.eu/database/data-sets (dataset 001-2014, A04T training; catalog license CC BY-ND 4.0).
- Allowed source: `https://bnci-horizon-2020.eu/database/data-sets/001-2014/A04T.mat`; redirects allowed only to the corresponding approved Graz mirror.
- Inspector: [bnci_a04t_exception_v05.py](bnci_a04t_exception_v05.py), reusing the committed A02T MAT parser without changing that parser or the frozen synthetic evaluator.
- Negative controls: [test_bnci_a04t_exception_v05.py](test_bnci_a04t_exception_v05.py); **13/13 passed locally** on CPython 3.13.5 with a stubbed upstream MAT parser. The hosted test imported the real committed parser.
- Hosted execution: [GitHub Actions #40589338663](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40589338663), **success** on Ubuntu; workflow head `a73bb52d08c24993beb3f6599813dfd9e715b7b1`, Python 3.13 (exact patch: TBD), NumPy 2.3.3, SciPy 1.16.2. The job log was inspected.
- **Hosted regression tests: 13/13 passed.** Source and test Git blob SHA-1 values independently matched the locally tested files: `a799307d33475e79da111c2e201eeb3852729b04` and `ea2cfa1bf0725afd21a9d54c5ab1dc3f21072bee`.
- Uploaded **metadata-only** artifact: `bnci-A04T-training-metadata-only`, ID `12772823419`; workflow log reports ZIP digest SHA-256 `a07346cf6d0f7c252eb75dd167731077c412c1fc7ccda93b568e11ed9821ede7`. Artifact ZIP was **not independently downloaded** for this record. No raw EEG or class-label artifact was uploaded.

## Actual observed A04T structure (not synthetic)

| Property | Observed |
|---|---|
| Public training file | `A04T.mat` |
| Response bytes | **37,150,377** |
| SHA-256 of observed upstream response | `15850d81b95fc88cc8b9589eb9b713d49fa071e28adaf32d675b3eaa30591d6e` |
| Recording blocks | **7** |
| Cue-free EOG/baseline blocks | **1** |
| Task blocks | **6** |
| Total cue positions | **288** |
| Decoding accuracy / false-action risk | **TBD / TBD** |
| Source hash independently repeated | **TBD** |
| Publisher-signed source authenticity | **TBD** |

**Decision-changing finding:** A04T has **seven** blocks, not the nine observed in A01T/A02T. The six task blocks still have 48 cue positions each. The exception-aware gate accepted this actual public source. A universal nine-block requirement would have been incorrect. This is a file-layout result, not an EEG-performance result.

## Failures, limitations and next experiment

The earlier A02T gate intentionally requires three baseline blocks; **do not reuse it unchanged for every subject**. The new A04T rule is based on a published exception and was committed before hosted acquisition. Synthetic negative controls test failure behavior but do not prove full parser correctness. The observed SHA-256 is a reproducibility fingerprint, **not publisher authentication**. Only one hosted A04T acquisition was completed; no independent repeat, raw-data audit, held-out evaluation, or cross-subject decoding was performed.

**Next decisive experiment:** independently reacquire A04T and verify the exact byte fingerprint and block structure; then extend the **training-only** 9-subject manifest, allowing documented subject-specific baseline exceptions without opening evaluation labels. Freeze leakage-safe session/subject splits and matched-coverage evaluation before scoring any EEG. Reframe the proposed drift gate if it fails to outperform confidence-only abstention at comparable useful-action coverage.

**Four lenses:** hiring manager — runnable code, CI and traceable failure tests; technical reviewer — source hash not authenticated and parser reuse still needs independent scrutiny; innovation leader — a genuine dataset-structure exception corrected, but no policy-performance advancement; founder — no clinical, product or IP claim, no external deployment or confidential data.
