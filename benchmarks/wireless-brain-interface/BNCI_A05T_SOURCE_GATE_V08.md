# WBI A05T public training-source structure gate v0.8 — 2026-10-29 IST

**Evidence:** independently reproduced public training-file byte identity and structural metadata only. **Not:** EEG decoding, label inspection, clinical or product validation. **Stage:** Research / Simulation unchanged.

## Frozen question and method

Can an additional BNCI2014_001 subject's A05T **training** file be downloaded through allowlisted HTTPS in separate Ubuntu and Windows environments, with no evaluation-file access and no EEG or label exports?

The [executable source](bnci_a05t_source_gate_v08.py) checks the exact A05T filename, a bounded official-host/mirror download, byte digest, 9 blocks, 3 cue-free baselines, 6 task blocks with 48 cue positions each, 25 channels, 250 Hz, and negative label/performance flags. The existing MAT structural parser is reused; parser correctness is not independently established. The official [dataset index](https://bnci-horizon-2020.eu/database/data-sets) lists 001-2014 and its CC BY-ND 4.0 terms. Do not redistribute original MAT files.

## Verified hosted execution

[GitHub Actions run #40747031127](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40747031127) succeeded at code-bearing head 6257f6897e7826c6e82013f96027952a4c271f11. **Ubuntu and Windows each passed 16/16 fictional adversarial tests** and independently downloaded A05T training bytes. Both completed job logs were inspected.

- Exact byte count: **42,452,392**.
- Observed SHA-256 on both systems: **77387d3b669f4ed9a7c1dac4dcba4c2c40c8910bae20fb961bb7cf5a94912950**.
- Structure on both systems: **9 blocks; 3 cue-free baseline; 6 cued task; 288 cue positions; 25 channels; 250 Hz**.
- Pinned NumPy **2.3.3**, SciPy **1.16.2**. Python **3.13.17 Ubuntu**, **3.13.16 Windows**.
- A05E / evaluation labels accessed: **no**. EEG/class labels persisted or uploaded: **no**. Decode accuracy, incorrect-action risk: **TBD**.

Both artifact ZIPs were downloaded, SHA-256 checked against GitHub metadata and inspected. Each contained only one metadata JSON. All substantive fields matched; JSON bytes differed in runtime provenance.

- Ubuntu artifact 12840909612: ZIP SHA-256 899d7d476b455a4d32f5181aae96d011d0d72a83d79ab79e5311aa8cc2f88c27; JSON SHA-256 32ea4c113f80da65c596d1f82c3be4e169f5ac7d675f7cb4e67ebd7f880c1e7d.
- Windows artifact 12842760619: ZIP SHA-256 462d475b59c13717f10ed1a48cb65e17b35c5859a5cec805654a2b8c35c545fa; JSON SHA-256 ea87df929d1cf35fce05e2493c2c52fbb3ddf5c595453eba585c2c74288e3dfc.

## Reproduce and decision

From benchmarks/wireless-brain-interface after installing the pinned dependencies, run the unit tests with python -B -m unittest -v test_bnci_a05t_source_gate_v08, then execute python -B bnci_a05t_source_gate_v08.py --output /private/new_a05t_metadata.json. Output paths cannot already exist. The [workflow](../../.github/workflows/wbi-a05t-source-gate-v08.yml) repeats both steps on Ubuntu and Windows.

The earlier A04T short-baseline exception and v0.7 **negative synthetic drift-permutation result** remain unchanged. The original [frozen synthetic evaluator](SYNTHETIC_EVALUATOR.md) and [execution record](EXECUTION_RECORD.md) were not modified. This is an observed source-byte identity, **not** a publisher signature or an independent MAT parser. It cannot establish decoding, drift-gate benefit, clinical safety or patentability.

**Next decisive gate:** complete the remaining **14** public file-identity/structure checks without inspecting evaluation labels, then freeze leakage-safe held-out subject/session EEG decoding and compare confidence abstention with the drift gate at identical action coverage. Reframe the drift-gate contribution if simpler abstention wins. No maturity advancement, merge, release or outreach.
