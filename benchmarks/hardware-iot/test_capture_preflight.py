"""Synthetic-only contract tests; no physical measurements are represented."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from capture_preflight import FIELDS, MODES, SCHEMA, check


def fixture(root, *, origin="physical", mutate=None):
    """All fixture values are fabricated, including when origin is declared physical."""
    rows = []
    for i in range(121):
        for sensor, value, unit in (("BH1750", "100.0", "lux"), ("SCD40", "650.0", "ppm")):
            rows.append({"boot_id": "fictional-boot", "sensor": sensor, "seq": str(i),
                         "elapsed_ms": str(i * 5000), "value": value, "unit": unit, "ready": "1"})
    manifest = {"schema_version": SCHEMA, "capture_origin": origin,
                "device_id": "FICTIONAL-ESP32", "firmware_sha256": "a" * 64,
                "boot_id": "fictional-boot", "timestamp_source": "device_monotonic_ms",
                "sensor_modes": MODES, "recorded_start_utc": "2026-10-23T00:00:00Z",
                "instruments": {"BH1750": {"model": "BH1750", "address": "0x23", "check_status": "TBD"},
                                "SCD40": {"model": "SCD40", "address": "0x62", "check_status": "TBD"}}}
    if mutate:
        mutate(rows, manifest)
    csv_path = root / "samples.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest["csv_sha256"] = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    return manifest_path, csv_path


class CaptureContract(unittest.TestCase):
    def run_fixture(self, mutate=None, origin="physical"):
        with tempfile.TemporaryDirectory() as directory:
            manifest, csv_path = fixture(Path(directory), origin=origin, mutate=mutate)
            return check(manifest, csv_path)

    def assert_rejected(self, mutate=None, origin="physical", reason=None):
        result = self.run_fixture(mutate, origin)
        self.assertEqual(result["status"], "REJECT_INVALID")
        if reason:
            self.assertIn(reason, " ".join(result["errors"]))

    def test_structural_candidate_is_never_physical_proof(self):
        result = self.run_fixture()
        self.assertEqual(result["status"], "STRUCTURAL_PASS_PROVENANCE_UNVERIFIED")
        self.assertEqual(result["metrics"]["duration_ms"], 600000)
        self.assertIn("do not authenticate", result["limitation"])

    def test_synthetic_origin_rejected(self):
        self.assert_rejected(origin="synthetic", reason="synthetic origin")

    def test_empty_capture(self):
        self.assert_rejected(lambda rows, _: rows.clear(), reason="ten minutes")

    def test_single_sample(self):
        self.assert_rejected(lambda rows, _: rows.__setitem__(slice(None), rows[:1]), reason="100 samples")

    def test_missing_scd40(self):
        self.assert_rejected(lambda rows, _: rows.__setitem__(slice(None), [r for r in rows if r["sensor"] != "SCD40"]), reason="SCD40")

    def test_duplicate_sequence(self):
        self.assert_rejected(lambda rows, _: rows[3].update(seq="0"), reason="nonconsecutive")

    def test_boot_mismatch(self):
        self.assert_rejected(lambda rows, _: rows[2].update(boot_id="other"), reason="boot mismatch")

    def test_monotonic_reversal(self):
        self.assert_rejected(lambda rows, _: rows[4].update(elapsed_ms="0"), reason="reversed")

    def test_large_gap(self):
        def mutate(rows, _):
            for r in rows:
                if int(r["elapsed_ms"]) >= 100000:
                    r["elapsed_ms"] = str(int(r["elapsed_ms"]) + 20000)
        self.assert_rejected(mutate, reason="gap exceeds")

    def test_forged_fast_scd40(self):
        self.assert_rejected(lambda rows, _: rows[3].update(elapsed_ms="1000"), reason="below 4 seconds")

    def test_nonfinite_value(self):
        self.assert_rejected(lambda rows, _: rows[2].update(value="nan"), reason="nonfinite")

    def test_wrong_unit(self):
        self.assert_rejected(lambda rows, _: rows[0].update(unit="ppm"), reason="wrong unit")

    def test_unready_sensor(self):
        self.assert_rejected(lambda rows, _: rows[1].update(ready="0"), reason="not ready")

    def test_wall_clock_only_not_accepted(self):
        self.assert_rejected(lambda rows, m: m.update(timestamp_source="wall_clock"), reason="device_monotonic_ms")

    def test_wrong_sensor_mode(self):
        self.assert_rejected(lambda rows, m: m.update(sensor_modes={"BH1750": "continuous_high_res", "SCD40": "low_power_30s"}), reason="sensor_modes")

    def test_missing_firmware_hash(self):
        self.assert_rejected(lambda rows, m: m.update(firmware_sha256="TBD"), reason="firmware_sha256")

    def test_csv_tampering_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            m, c = fixture(Path(directory))
            c.write_bytes(c.read_bytes() + b"\n")
            self.assertIn("CSV SHA-256 mismatch", check(m, c)["errors"])

    def test_report_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            m, c = fixture(Path(directory))
            a = json.dumps(check(m, c), sort_keys=True)
            b = json.dumps(check(m, c), sort_keys=True)
            self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
