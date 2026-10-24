#!/usr/bin/env python3
"""Structural audit of FICTIONAL decision-supersession references.

This cannot establish that a decision happened, who approved it, or whether
any historical document is authentic. It must not be used as an authorization
mechanism or a semantic ground-truth validator.
"""
from collections import Counter


def audit_supersession(fixture):
    """Return sorted stable issue codes for decision-lineage graph anomalies."""
    if not isinstance(fixture, dict):
        return ['malformed_fixture']
    gt = fixture.get('ground_truth')
    if not isinstance(gt, dict):
        return ['malformed_ground_truth']
    current = gt.get('decisions', [])
    historical = gt.get('historical_decisions', [])
    if not isinstance(current, list) or not isinstance(historical, list):
        return ['malformed_decision_collection']
    issues = []
    rows = current + historical
    if any(not isinstance(row, dict) or not isinstance(row.get('id'), str)
           or not row.get('id', '').strip() for row in rows):
        return ['invalid_decision_id']
    ids = [row['id'] for row in rows]
    if any(count > 1 for count in Counter(ids).values()):
        issues.append('duplicate_decision_id')
    # Reject duplicate IDs before constructing a graph: dictionary collapse
    # would conceal a competing record or create misleading cycle results.
    if 'duplicate_decision_id' in issues:
        return issues
    known = set(ids)
    parents = {}
    for row in rows:
        predecessor = row.get('supersedes')
        if predecessor is None or predecessor == '':
            continue
        if not isinstance(predecessor, str) or not predecessor.strip():
            issues.append('invalid_predecessor_ref')
            continue
        if predecessor not in known:
            issues.append('unresolved_predecessor')
            continue
        if predecessor == row['id']:
            issues.append('self_supersession')
        parents[row['id']] = predecessor
    # Every node has at most one predecessor in this declared schema.
    # Detect cycles by traversing only valid edges, not using recursion.
    for start in parents:
        seen = set()
        node = start
        while node in parents:
            if node in seen:
                issues.append('cyclic_supersession')
                break
            seen.add(node)
            node = parents[node]
    # Multiple descendants may be intentional branching. Surface for human
    # review, without asserting that the underlying history is false.
    successors = Counter(parents.values())
    if any(n > 1 for n in successors.values()):
        issues.append('forked_supersession_review')
    return sorted(set(issues))
