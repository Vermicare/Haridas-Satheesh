# WBI BNCI2014_001 A02T — source metadata acceptance gate v0.4

**Date (UTC):** 2026-10-27. **Maturity:** Research / Simulation, unchanged. **Scope:** public A02T **training-session** metadata only; no EEG decoder, no held-out evaluation labels, no physical device, no clinical validation.

## Research question and defect reproduced

The prior v0.3 A02T inspector returned `six_task_runs_48_cues_each: false` for malformed fictional task structures, but its command-line path still exited successfully and uploaded a metadata artifact. Therefore a green workflow was not by itself an **acceptance decision** for the expected task-run structure.

Version 0.4 adds a separate, fail-closed, standard-library acceptance gate that checks the actual emitted metadata **before** artifact upload. It rejects mismatched pinned source bytes/hash, missing provenance/privacy flags, unexpected recording blocks or order, channel/sample-rate changes, inconsistent summary counts and unverified performance claims. The inspector and frozen WBI synthetic evaluator are unchanged.

## Source and actual execution

- Dataset: BNCI2014_001 / BCI Competition IV 2a, **A02T.mat** training file.
- Source: https://bnci-horizon-2020.eu/database/data-sets/001-2014/A02T.mat (redirect allowlist enforced by the inspector).
- Pinned observed source: **43,068,077 bytes**; SHA-256 `5ddd5cb520b1692c3ba1363f48d98f58f0e46f3699ee50d749947950fc39db27`. This is **not** a publisher-signed checksum or proof of authenticity.
- Original successful hosted source/structure run: [#40533360086](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40533360086), tested commit `51657199afbb9b9b519e9688fde486932e8456a6`, 7/7 synthetic inspector tests.
- **Gate execution:** [GitHub Actions #40571300834](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40571300834), tested commit `63a2c964f7cb40087876f6b8b3eae22560a7a4b7`, GitHub-hosted Ubuntu, CPython 3.13.16, NumPy 2.3.3, SciPy 1.16.2. Job `122425898787` succeeded.
- Independently inspected hosted log: **7/7 original structural tests** and **15/15 new adversarial gate tests** passed; the real A02T fetch matched the pinned bytes/hash and **passed the new gate**. Metadata-only artifact `12764609295` uploaded; ZIP digest reported by Actions `e7cc8641eb00aa7576aa4037a97b68c860017ca74d9b5e4603c465df00203521`.

## Observed structural metadata

| Property | Real A02T observation |
|---|---:|
| Recording blocks | 9 |
| Cue-free baseline blocks | 3 |
| Cued task blocks | 6 |
| Task cues total | 288 |
| Cues per task block | 48 |
| Signal columns | 25 |
| Sampling frequency | 250 Hz |
| First task block (zero-based) | 3 |

The gate independently checks each of the nine block entries, rather than trusting the aggregate Boolean. The 15 negative/positive regression cases use **fictional metadata** only, including a false aggregate, reordered task blocks, changed source hash/size, unexpected channels, incorrect sampling frequency and leakage flags. The actual upstream data was accessed only by the read-only hosted inspector; raw EEG and class labels were **not** uploaded.

## Reproduction

Run the original source inspector in the existing workflow to produce a metadata-only JSON, then execute:

```sh
python -B -m unittest -v test_bnci_a02t_structural_gate_v04
python -B bnci_a02t_structural_gate_v04.py --input /path/to/bnci_A02T_metadata_only.json
```

The second command must exit nonzero if any gate invariant fails. The [workflow](../../.github/workflows/wbi-a02t-metadata-v03.yml) runs the gate before upload and uses read-only repository permissions. The source URL and data license/redistribution terms should be reviewed before any additional acquisition; no source data is redistributed here.

## Decision, failures and limits

**Decision:** accept A02T as one metadata-verified public **training** source, not as a validated EEG decoder. The earlier green-but-nonconforming possibility is now blocked for this workflow; the earlier source inspection evidence remains preserved.

**Largest gap:** 16 other BNCI2014_001 files remain uninspected in this branch after A01T and A02T. The E-session label firewall, independent source authentication, actual held-out decoding, matched-coverage drift-gate benefit, idle false-action safety and external review remain **TBD**.

**Next experiment:** validate the next T-session with the same fail-closed contract, then derive a complete 18-file provenance manifest without accessing held-out E labels; freeze preprocessing and thresholds before any E-session evaluation.

**Advance only when:** reproducible held-out real EEG evaluation supports subject/session-aware matched-coverage benefit with uncertainty. **Reframe if:** drift gating does not beat simple confidence abstention at matched coverage, or data acquisition cannot maintain label isolation.

**Four lenses:** Hiring manager—reproducible fail-closed workflow; technical reviewer—source structure, not EEG outcomes; innovation leader—no maturity upgrade; founder—no medical/safety/product claim.

No outreach, employer data, participant data, release or merge was involved.
