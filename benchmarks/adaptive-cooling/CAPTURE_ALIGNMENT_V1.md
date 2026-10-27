# Adaptive Cooling — capture declaration alignment v1 (2026-10-27)

**Scope:** fictional-only software evidence integrity. **Not:** physical measurement, logger-to-CSV semantic replay, sensor authentication, calibration, thermal/energy efficacy, comfort or safety validation. **Stage remains Prototype / Documented R&D.**

## Decision-changing gap

The earlier [capture byte-chain preflight](CAPTURE_CHAIN_V1.md) checks hashes and required declarations; [dry-run integrity](DRY_RUN_INTEGRITY.md) checks timestamp, power and energy consistency within the CSV. Neither checks that a fully rehashed CSV's **run ID, condition or observed time boundaries agree with the declared run manifest and frozen plan**. Consequently, an internally coherent but mislabelled file set could pass both isolated gates. This preflight adds that cross-document check, not a physical-origin guarantee.

## Reproduce

Run from `benchmarks/adaptive-cooling`:

```bash
python -B -m unittest -v test_fixture_origin_gate.py test_dry_run_integrity.py test_capture_chain.py test_capture_alignment.py
python capture_alignment.py --bundle /path/to/private/capture --expected-manifest-sha256 <independently-preserved-64-hex-pin>
```

The existing `capture_manifest.json` and four artifact roles are required. The frozen `run_plan.json` must additionally contain `run_id` and `condition` (one of the CSV's `ambient`, `fan_only`, `prototype` conditions). The new preflight runs the original byte-chain and numeric CSV gates first, then requires matching run IDs across CSV/manifest/plan, matching CSV/plan condition, and a declared capture interval enclosing actual first/last samples with no more than one declared sample interval of boundary slack. The declared capture still must span ≥600 seconds; the numeric CSV gate separately checks actual duration and gaps. A declared sampling interval does not prove logger timing or sensor identity.

A return status of `DECLARATIONS_ALIGNED_ORIGIN_UNVERIFIED` means only that **these local file bytes and declarations** are mutually consistent under the checks; it never establishes physical origin. `REJECTED` (exit code 2) records contradictions and must not be silently bypassed. Rehashing all files and adjusting all declarations can produce a consistent fictional bundle; this preflight cannot prevent fabrication. An independently preserved manifest pin is recommended, but is not a signature or trusted hardware attestation. Raw captures may contain private data and should remain outside public Git until reviewed.

## Frozen fictional-only negative controls

The 13 tests cover: valid fictional alignment; partial and complete CSV run-ID swaps with hashes recomputed; plan run-ID and condition swaps; missing plan condition; declared start/end offsets; a one-interval boundary tolerance control; energy-counter disagreement; unpinned CSV tampering; an incorrect external manifest pin; and duplicate plan JSON keys. Tests do **not** use physical instruments. Results/CI links must be recorded only after actual execution.

## Limits and next evidence gate

The tool does **not** replay a vendor logger parser, prove that serial bytes generated CSV readings, authenticate timestamps, validate instrument accuracy, or verify real thermal and electrical boundaries. An attacker who controls all files and manifest can create a coherent fake. Meter latency and quantization can also trigger the existing interval energy diagnostic; investigate, do not post-hoc tune tolerances.

Under [Issue #15](https://github.com/Vermicare/Haridas-Satheesh/issues/15), obtain actual instrument identities and uncertainties, fix geometry, preserve an original ≥10-minute logger capture privately, document the exact conversion command and version, then run all four gates. Only afterward preregister repeated ambient → fan-only → prototype comparisons with full energy accounting (including preconditioning/recharge) and condensation observations. **All physical results TBD.**
