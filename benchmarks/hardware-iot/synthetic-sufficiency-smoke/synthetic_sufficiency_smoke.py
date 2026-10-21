"""Synthetic-only, dependency-free post-integrity telemetry sufficiency smoke gate.

This script never opens a serial port and cannot authenticate sensor origin.
It deliberately accepts only synthetic fixture events, never physical claims.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime


ALLOWED = {"SCD40_CO2", "BH1750_LUX"}


def _seconds(utc: str) -> float:
    if not isinstance(utc, str) or not utc.endswith("Z"):
        raise ValueError("UTC must end in Z")
    return datetime.fromisoformat(utc[:-1] + "+00:00").timestamp()


def assess(rows, *, expected=("SCD40_CO2",), minimum=100,
           minimum_per_sensor=100, minimum_span_s=600.0,
           maximum_gap_s=10.0, maximum_clock_difference_s=2.0):
    """Check synthetic record density and timing; NEVER assert physical evidence."""
    base = {"schema": "synthetic-sufficiency-smoke-v1",
            "hardware_verified": False, "bench_eligible": False,
            "sensor_calibration_verified": False, "physical_measurements": 0}

    def result(status, reason, **fields):
        return {**base, "status": status, "reason": reason, **fields}

    if (type(minimum) is not int or minimum < 1 or
            type(minimum_per_sensor) is not int or minimum_per_sensor < 1 or
            minimum_span_s <= 0 or maximum_gap_s <= 0 or
            maximum_clock_difference_s < 0 or not expected or
            len(set(expected)) != len(expected) or not set(expected) <= ALLOWED):
        raise ValueError("invalid predeclared criteria")
    if not isinstance(rows, list):
        return result("REJECT", "invalid_rows")
    if not rows:
        return result("INSUFFICIENT", "zero_observations", count=0)

    monotonic, wall, counts = [], [], Counter()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {
                "seq", "host_monotonic_ns", "host_wall_utc", "sensor", "source_kind"}:
            return result("REJECT", "invalid_event_schema", index=index)
        if (type(row["seq"]) is not int or row["seq"] != index or
                type(row["host_monotonic_ns"]) is not int or
                row["host_monotonic_ns"] < 0 or row["sensor"] not in ALLOWED or
                row["source_kind"] != "synthetic"):
            return result("REJECT", "untrusted_or_invalid_event", index=index)
        try:
            wall.append(_seconds(row["host_wall_utc"]))
        except (ValueError, TypeError, OverflowError):
            return result("REJECT", "invalid_wall_clock", index=index)
        monotonic.append(row["host_monotonic_ns"] / 1e9)
        counts[row["sensor"]] += 1
        if index and monotonic[-1] < monotonic[-2]:
            return result("REJECT", "monotonic_clock_regression", index=index)

    if len(rows) < minimum:
        return result("INSUFFICIENT", "too_few_samples", count=len(rows))
    if any(counts[sensor] < minimum_per_sensor for sensor in expected):
        return result("INSUFFICIENT", "insufficient_expected_sensor_coverage",
                      counts={s: counts[s] for s in expected})
    span = monotonic[-1] - monotonic[0]
    if span < minimum_span_s:
        return result("INSUFFICIENT", "monotonic_span_short", span_s=round(span, 6))
    if abs((wall[-1] - wall[0]) - span) > maximum_clock_difference_s:
        return result("REVIEW_REQUIRED", "wall_monotonic_disagreement")
    if any(b - a > maximum_gap_s for a, b in zip(monotonic, monotonic[1:])):
        return result("REVIEW_REQUIRED", "capture_gap")
    return result("SYNTHETIC_SUFFICIENCY_PASS", "declared_criteria_met",
                  count=len(rows), span_s=round(span, 6),
                  counts={s: counts[s] for s in expected})


def _fixture(n=121, *, monotonic_step_s=5.0, wall_step_s=5.0):
    from datetime import timedelta, timezone
    start = datetime(2026, 10, 22, 0, 0, tzinfo=timezone.utc)
    return [{"seq": i, "host_monotonic_ns": int(i * monotonic_step_s * 1e9),
             "host_wall_utc": (start + timedelta(seconds=i * wall_step_s))
             .isoformat().replace("+00:00", "Z"),
             "sensor": "SCD40_CO2", "source_kind": "synthetic"} for i in range(n)]


if __name__ == "__main__":
    cases = {"empty": _fixture(0), "single": _fixture(1),
             "fake_wall_duration": _fixture(monotonic_step_s=0.000001),
             "fictional_consistent_duration": _fixture()}
    print(json.dumps({"fixture_kind": "FICTIONAL SYNTHETIC ONLY",
                      "cases": {name: assess(rows) for name, rows in cases.items()}},
                     indent=2, sort_keys=True))
