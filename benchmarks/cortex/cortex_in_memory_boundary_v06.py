"""Fail-closed optional in-memory adapter for frozen, fictional CORTEX v0.5.

Does not change the historical v0.5 exporter or claim general semantic accuracy.
"""
from __future__ import annotations

import json

import cortex_prov_boundary_v05 as frozen


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def render_checked(case: dict, archive: dict, case_path: str, archive_path: str) -> str:
    """Render only if both in-memory objects equal exact SHA-pinned file contents.

    Reject mutated objects even if source IDs remain intact. The source-file
    hashes are verified by the original v0.5 reader. This is a local software
    consistency gate, not proof of source truth or human semantic agreement.
    """
    try:
        original_case = frozen._read_pinned(case_path, frozen.CASE_SHA256)
        original_archive = frozen._read_pinned(archive_path, frozen.ARCHIVE_SHA256)
        if _canonical(case) != _canonical(original_case) or _canonical(archive) != _canonical(original_archive):
            raise ValueError("in_memory_source_mismatch")
        return frozen.render_turtle(original_case, original_archive)
    except (OSError, UnicodeError, TypeError, AttributeError, KeyError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc) == "in_memory_source_mismatch":
            raise ValueError("in_memory_source_mismatch") from None
        raise ValueError("invalid_or_unreadable_frozen_input") from None
