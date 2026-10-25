#!/usr/bin/env python3
"""Additive synthetic archive-reference audit; not provenance authentication."""
from collections import Counter


def audit_archive(fixture):
    """Return stable structural error codes; an internally linked record may be fictional."""
    gt = fixture.get('ground_truth', {})
    history = gt.get('historical_decisions', [])
    records = fixture.get('history', {}).get('records', [])
    issues = []
    if not isinstance(history, list) or not isinstance(records, list):
        return ['malformed_archive_collection']
    refs = [r.get('record_ref') for r in records if isinstance(r, dict)]
    if len(refs) != len(records) or any(not x for x in refs):
        issues.append('invalid_archive_record')
    if any(count > 1 for count in Counter(refs).values()):
        issues.append('duplicate_archive_ref')
    by_ref = {r.get('record_ref'): r for r in records if isinstance(r, dict)}
    hist_ids = []
    for h in history:
        if not isinstance(h, dict) or not h.get('id') or not h.get('record_ref'):
            issues.append('invalid_historical_declaration')
            continue
        hist_ids.append(h['id'])
        record = by_ref.get(h['record_ref'])
        if record is None:
            issues.append('unresolved_archive_ref')
        else:
            if record.get('decision_id') != h['id']:
                issues.append('archive_decision_id_mismatch')
            if not isinstance(record.get('text'), str) or not record['text'].strip():
                issues.append('archive_record_missing_text')
    if any(count > 1 for count in Counter(hist_ids).values()):
        issues.append('duplicate_historical_id')
    # Deliberately no authenticity or semantic truth claim: a fictional record
    # can satisfy all structural checks.
    return sorted(set(issues))
