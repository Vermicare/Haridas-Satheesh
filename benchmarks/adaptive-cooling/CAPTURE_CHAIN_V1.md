# Adaptive Cooling — original-capture chain preflight v1 (2026-10-26)

**Evidence:** executable, fictional-only software regression checks. **Not:** a physical logging session, authenticated sensor source, verified CSV conversion, instrument calibration, cooling result, energy efficiency, comfort, or safety assessment. Maturity remains **Prototype / Documented R&D**.

## Decision addressed

The existing `dry_run_integrity.py` binds the parsed measurement CSV to its SHA-256, but does **not** bind the original logger/serial bytes, instrument manifest and frozen run plan to that report. A reviewer could receive a plausible CSV while the original logger capture or geometry declaration has changed. This tool checks the declared *byte chain* before the existing origin and numeric preflights; it never authenticates the physical source.

## Required capture bundle

Use a private working directory until the original logger output and instrument identifiers have been checked for sensitive information. Preserve the four unmodified files separately:

- `original_logger` — original serial/logger bytes, before cleaning or conversion.
- `measurement_csv` — derived CSV with the **existing** `raw_data_template.csv` header.
- `instrument_manifest` — the **existing** `instrument_manifest_template.csv`, populated with actual instrument information and uncertainty/check details.
- `run_plan` — frozen, timestamped run plan with sensor geometry, trial conditions and thermal/electrical boundary.

Create `capture_manifest.json` alongside them with this structure (the example values are **deliberately incomplete** and must be replaced with actual declarations; do not treat it as physical evidence):

```json
{
  "schema_version": "cooling-capture-chain-v1",
  "origin": "declared_physical_dry_run",
  "metadata": {
    "run_id": "TBD",
    "capture_start": "TBD",
    "capture_end": "TBD",
    "logger_version": "TBD",
    "firmware_version": "TBD",
    "clock_sync_method": "TBD",
    "sample_interval_s": 30,
    "sensor_geometry": "TBD",
    "energy_boundary": "TBD",
    "heat_rejection_path": "TBD",
    "thermal_storage_preconditioning": "TBD",
    "recharge_energy_accounting": "TBD",
    "conversion_command": "TBD",
    "operator_declaration": "TBD"
  },
  "artifacts": {
    "original_logger": {"path": "original_logger.txt", "sha256": "TBD"},
    "measurement_csv": {"path": "measurement.csv", "sha256": "TBD"},
    "instrument_manifest": {"path": "instrument_manifest.csv", "sha256": "TBD"},
    "run_plan": {"path": "run_plan.json", "sha256": "TBD"}
  }
}
```

For a genuine dry run, `capture_start`/`capture_end` must be timezone-aware ISO-8601 timestamps spanning at least 600 seconds, and the declared sample interval must be finite, positive and ≤60 seconds. This checks **declarations only**; the existing dry-run preflight checks actual CSV timestamps and energy readings. A physical origin label is an unauthenticated declaration, not proof.

From `benchmarks/adaptive-cooling`:

```bash
python -B -m unittest -v test_capture_chain.py
python capture_chain.py --bundle /path/to/private/capture
python capture_chain.py --bundle /path/to/private/capture --expected-manifest-sha256 <64-hex-digest-preserved-before-review>
python fixture_origin_gate.py --raw /path/to/private/capture/measurement.csv --manifest /path/to/private/capture/instrument_manifest.csv --plan /path/to/private/capture/run_plan.json --mode bench
python dry_run_integrity.py --raw /path/to/private/capture/measurement.csv --expected-sha256 <pinned-measurement-csv-sha256>
```

**Note:** the existing origin preflight expects its own run-plan JSON schema. A generic `run_plan.json` is not automatically compatible; use that documented schema, and do not infer that this capture-chain tool validates its contents. A structural chain pass **does not replace** either existing preflight. `--expected-manifest-sha256` is valuable only when the digest was preserved through a separate trusted channel before later review. The manifest is not signed; anyone able to edit all files and hashes can fabricate a consistent bundle.

`REJECTED` / exit 2 indicates an unsafe or inconsistent declaration. `CHAIN_CHECKED_ORIGIN_UNVERIFIED` / exit 0 means that declared local file bytes match their hashes and required metadata fields are present. The tool reports per-file SHA-256, sizes, the manifest SHA-256, and whether an independently supplied manifest pin matched. Every report retains `physical_origin_authenticated=false`, `logger_to_csv_conversion_verified=false`, `instrument_calibration_verified=false`, `performance_claim_permitted=false`.

### Negative controls and limitations

The fictional-only regression suite rejects altered original logger bytes, swapped CSV, altered instrument manifest, missing/empty files, unsafe/symlinked paths, duplicate JSON keys, `NaN`, invalid/missing hashes, short or naive-clock declarations, absent recharge-energy boundary, and a modified manifest after an external digest was pinned. It also confirms a structurally complete **fictional** bundle cannot produce an authenticity or performance claim.

This is **byte integrity**, not physical authenticity or semantic conversion integrity. It does not replay the logger parser, verify sample values or clock synchronization, attest instrument serial numbers, inspect photographs, or measure sensor uncertainty. A fake but internally coherent bundle can pass. SHA-256 and local file reads do not defend against a privileged adversary rewriting both data and unpinned manifest or modifying files after inspection.

### Energy accounting decision before a physical trial

**Primary-source decision:** The [U.S. Department of Energy's thermal-energy-storage overview](https://www.energy.gov/cmei/buildings/thermal-energy-storage) describes thermal storage as charging a hot/cold reservoir for later discharge. Its [July 2023 thermal-storage technology assessment](https://www.energy.gov/sites/default/files/2023-09/9_Technology%20Strategy%20Assessment%20-%20%239%20Thermal%20Energy%20Storage_508.pdf) is background for evaluating storage-system boundaries, **not** a claim that this prototype meets any standard. This changes the experiment: report recharge/preconditioning energy separately and do not use a discharge-only Wh figure to claim overall efficiency.

A PCM/thermal-storage or prechilled-fluid prototype can appear low-power during a ten-minute trial while consuming energy to charge/refrigerate the storage before the trial. The predeclared `energy_boundary`, `thermal_storage_preconditioning`, `recharge_energy_accounting`, and `heat_rejection_path` fields prevent a **silent omission** of those boundaries; the script checks that the fields are declared, **not** that their contents or values are correct. Report both in-run electrical Wh and any recharge/preconditioning energy separately; do not claim system efficiency until the full comparable boundary is measured. Keep fan-only and ambient controls, condensation, humidity, uncertainty and negative results in the subsequent controlled experiment.

## Next physical evidence gate

[Issue #15](https://github.com/Vermicare/Haridas-Satheesh/issues/15): populate real instruments, fix geometry, capture and preserve original ≥10-minute logger bytes, run all three preflights, inspect and record failures, then preregister repeated ambient → fan-only → prototype comparisons. Actual measurements, uncertainty, recharge energy and outcome: **TBD**. No maturity advancement, release or patentability claim.
