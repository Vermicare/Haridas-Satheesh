# WBI frozen synthetic evaluator — reproducibility gate

**Evidence scope:** deterministic fictional data only. No real EEG, device, clinical, or safety-performance validation.

The branch contains `verify_frozen_wbi.py` and `test_ci_reproduction.py`. The verifier executes the **unchanged** frozen evaluator twice in separate temporary directories, rejects source and reference-CSV tampering, and checks byte-identical outputs, published thresholds, reported metrics, and the synthetic-only warning.

- Frozen evaluator Git blob: `2becec81a8002cc5ff2f445889b7617baf9937b9`
- Published risk–coverage CSV SHA-256: `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`
- Prior verified evidence: [EXECUTION_RECORD.md](EXECUTION_RECORD.md) documents two same-runtime executions on CPython 3.13.5.
- **Cross-environment CI: TBD.** The proposed workflow could not be committed because the GitHub connector rejected workflow-file creation. Do not imply that this branch has run on Windows or macOS.

## Local commands

From the repository root:

```sh
python benchmarks/wireless-brain-interface/verify_frozen_wbi.py
python -m unittest discover -s benchmarks/wireless-brain-interface -p 'test_ci_reproduction.py' -v
```

The verifier requires Python 3.11+ (proposed matrix: Ubuntu/Python 3.11 and 3.13, Windows/Python 3.13, macOS/Python 3.13). It has no third-party runtime dependencies. `.gitattributes` preserves the source's LF and reference CSV's CRLF bytes across checkout policies.

## Promotion criteria

1. Activate a **reviewed** pull-request/manual GitHub Actions workflow only after workflow-write capability is explicitly available. Do not bypass connector safety controls or introduce hourly CI schedules.
2. Inspect each of four real runner logs and output digests; record runner OS/Python versions, commit SHA, checksums, and failures. If any job fails, investigate rather than removing that runner.
3. Only after all jobs pass, record cross-environment reproducibility for those **specific** runner configurations; preserve the stronger existing same-runtime execution evidence.
4. Keep WBI at **Research / Simulation**. This gate does not prove drift-gate superiority, matched-coverage performance, or real EEG decoding.

## Known negative evidence and boundaries

The published synthetic test reports incorrect-action risk **0.1571** for the authorization gate versus **0.1301** for confidence abstention, at unequal coverage (0.5833 vs 0.5125). No superiority claim follows. The original evaluator's action-vector-length validation issue is separate from this reproducibility gate.

No personal, employer, clinical, or private datasets are included.
