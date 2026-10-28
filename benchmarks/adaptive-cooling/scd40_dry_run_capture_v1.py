#!/usr/bin/env python3
"""Capture real SCD4x readings on Raspberry Pi; never generate synthetic readings.

A logger integration dry run, NOT a cooling benchmark or sensor-authentication tool.
No automatic upload or control of cooling hardware. Standard library plus an
optional hardware driver imported only by main().
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time

VERSION = 'scd40-physical-dry-run-logger-v1'


def valid_sample(temp, rh, co2):
    if not all(type(v) in (float, int) and math.isfinite(v) for v in (temp, rh, co2)):
        raise ValueError('nonfinite or nonnumeric sensor reading')
    if not -10 <= temp <= 60 or not 0 <= rh <= 100 or not 0 <= co2 <= 40000:
        raise ValueError('out-of-range SCD4x reading')
    return {'scd4x_temperature_c': float(temp),
            'scd4x_relative_humidity_pct': float(rh),
            'scd4x_co2_ppm': float(co2)}


def capture(sensor, destination, *, run_id, placement, duration_s=600.0,
            poll_s=1.0, monotonic=time.monotonic, sleep=time.sleep,
            utc_now=lambda: datetime.now(timezone.utc)):
    """Capture a single physical-device stream. Injected sensor is for TESTS ONLY.

    Output uses exclusive file creation, newline JSON, fsync, and a terminal
    completion record. A partial file has no valid terminal record. The SCD4x
    reports internal temperature, not independently calibrated zone temperature.
    """
    if not run_id.strip() or not placement.strip():
        raise ValueError('run_id and placement are mandatory')
    if not (math.isfinite(duration_s) and duration_s > 0 and
            math.isfinite(poll_s) and 0 < poll_s <= 5):
        raise ValueError('invalid duration or polling interval')
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    started = monotonic()
    samples = 0
    last_sample_time = None
    first_sample_time = None
    max_sample_gap_s = 0.0
    active = False
    # Exclusive create avoids overwriting evidence. Failures remain inspectable.
    with dest.open('x', encoding='utf-8', newline='\n') as handle:
        def emit(record):
            handle.write(json.dumps(record, sort_keys=True, allow_nan=False) + '\n')
            handle.flush()
            os.fsync(handle.fileno())
        emit({'event': 'begin', 'schema_version': VERSION, 'run_id': run_id,
              'placement': placement, 'declared_origin': 'physical_device_logger',
              'physical_origin_authenticated': False,
              'calibration_verified': False, 'cooling_performance_claim_permitted': False,
              'sensor_role': 'single SCD4x device; not independent ambient/target pair',
              'utc': utc_now().isoformat(), 'requested_duration_s': duration_s,
              'poll_s': poll_s})
        try:
            sensor.start_periodic_measurement()
            active = True
            while monotonic() - started < duration_s:
                if sensor.data_ready:
                    temp, rh, co2 = sensor.temperature, sensor.relative_humidity, sensor.CO2
                    values = valid_sample(temp, rh, co2)
                    now_mono = monotonic()
                    if first_sample_time is None:
                        first_sample_time = now_mono
                    if last_sample_time is not None and now_mono <= last_sample_time:
                        raise ValueError('non-increasing sample monotonic timestamp')
                    if last_sample_time is not None:
                        max_sample_gap_s = max(max_sample_gap_s, now_mono - last_sample_time)
                    last_sample_time = now_mono
                    emit({'event': 'sample', 'index': samples, 'utc': utc_now().isoformat(),
                          'elapsed_monotonic_s': now_mono - started, **values})
                    samples += 1
                sleep(poll_s)
        except BaseException as exc:
            emit({'event': 'capture_failed', 'utc': utc_now().isoformat(),
                  'exception_type': type(exc).__name__, 'samples_before_failure': samples})
            raise
        finally:
            if active:
                try:
                    sensor.stop_periodic_measurement()
                except Exception as exc:
                    emit({'event': 'stop_failed', 'exception_type': type(exc).__name__})
                    raise
        elapsed = monotonic() - started
        quality_pass = (elapsed >= 600 and samples >= 2 and max_sample_gap_s <= 60
                        and first_sample_time - started <= 60
                        and monotonic() - last_sample_time <= 60)
        emit({'event': 'complete', 'utc': utc_now().isoformat(),
              'elapsed_monotonic_s': elapsed, 'samples': samples,
              'max_sample_gap_s': max_sample_gap_s if samples >= 2 else None,
              'minimum_600_s_observed': elapsed >= 600,
              'capture_quality_gate_passed': quality_pass,
              'physical_origin_authenticated': False,
              'cooling_performance_claim_permitted': False})
    raw = dest.read_bytes()
    return {'path': str(dest), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(), 'samples': samples,
            'elapsed_monotonic_s': elapsed,
            'capture_quality_gate_passed': quality_pass,
            'physical_origin_authenticated': False,
            'cooling_performance_claim_permitted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='Private local JSONL path, never uploaded automatically')
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--placement', required=True,
                        help='Describe actual sensor position and geometry; no personal information')
    args = parser.parse_args()
    import board  # hardware-only dependency; never mocked in the live CLI
    import adafruit_scd4x
    sensor = adafruit_scd4x.SCD4X(board.I2C())
    result = capture(sensor, args.output, run_id=args.run_id, placement=args.placement)
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
