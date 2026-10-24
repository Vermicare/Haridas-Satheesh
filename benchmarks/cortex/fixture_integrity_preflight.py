#!/usr/bin/env python3
"""Synthetic CORTEX ground-truth preflight, not a semantic evaluator."""
import copy
import json
import unittest
from pathlib import Path

KINDS = ('decisions', 'actions', 'risks', 'dependencies', 'conditional_followups')
FIELDS = {
    'decisions': ('statement', 'status', 'supersedes'),
    'actions': ('owner', 'due', 'action'),
    'risks': ('status', 'statement'),
    'dependencies': ('statement',),
    'conditional_followups': ('condition', 'action'),
}
FIXTURE = Path(__file__).with_name('fixture.json')


def audit_fixture(fixture):
    """Return stable issue codes; source IDs alone do not prove semantic truth."""
    gt = fixture['ground_truth']
    utterances = fixture['meeting']['utterances']
    source_ids = [u['id'] for u in utterances]
    valid = set(source_ids)
    issues = []
    if len(valid) != len(source_ids):
        issues.append('duplicate_utterance_id')
    historical = {x.get('id') for x in gt.get('historical_decisions', [])
                  if isinstance(x, dict) and x.get('id') and x.get('record_ref')}
    current = {x.get('id') for x in gt.get('decisions', [])}
    object_ids = []
    for kind in KINDS:
        signatures = set()
        for obj in gt.get(kind, []):
            object_ids.append(obj.get('id'))
            sources = obj.get('source', [])
            if not sources or len(sources) != len(set(sources)):
                issues.append('invalid_gold_sources')
            if set(sources) - valid:
                issues.append('unresolvable_gold_source')
            signature = tuple(obj.get(k) for k in FIELDS[kind])
            if signature in signatures:
                issues.append('duplicate_gold_signature')
            signatures.add(signature)
            if any(obj.get(k) in (None, '') for k in FIELDS[kind]
                   if k != 'supersedes'):
                issues.append('missing_gold_field')
            if kind == 'decisions' and obj.get('supersedes') and \
                    obj['supersedes'] not in (current | historical):
                issues.append('unresolved_predecessor')
    object_ids.extend(historical)
    if len(object_ids) != len(set(object_ids)):
        issues.append('colliding_object_id')
    for negative in gt.get('negative_examples', []):
        sources = negative.get('source', [])
        if not sources or len(sources) != len(set(sources)):
            issues.append('invalid_negative_sources')
        if set(sources) - valid:
            issues.append('unresolvable_negative_source')
    return sorted(set(issues))


class SyntheticContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = json.loads(FIXTURE.read_text())

    def test_frozen_missing_D0_is_not_hidden(self):
        self.assertIn('unresolved_predecessor', audit_fixture(self.frozen))

    def test_missing_gold_source_is_rejected(self):
        case = copy.deepcopy(self.frozen)
        case['ground_truth']['actions'][0]['source'] = ['missing-utterance']
        self.assertIn('unresolvable_gold_source', audit_fixture(case))

    def test_duplicate_gold_signature_is_rejected(self):
        case = copy.deepcopy(self.frozen)
        duplicate = copy.deepcopy(case['ground_truth']['actions'][0])
        duplicate['id'] = 'A99'
        case['ground_truth']['actions'].append(duplicate)
        self.assertIn('duplicate_gold_signature', audit_fixture(case))

    def test_negative_source_must_exist(self):
        case = copy.deepcopy(self.frozen)
        case['ground_truth']['negative_examples'][0]['source'] = ['ghost']
        self.assertIn('unresolvable_negative_source', audit_fixture(case))

    def test_duplicate_object_id_is_rejected(self):
        case = copy.deepcopy(self.frozen)
        case['ground_truth']['actions'][0]['id'] = 'D1'
        self.assertIn('colliding_object_id', audit_fixture(case))


if __name__ == '__main__':
    unittest.main()
