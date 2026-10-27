"""Fictional cross-request receipt identity controls; no real external actions."""
import copy
import json
import unittest
from pathlib import Path

from governance_demo import evaluate

BASE = json.loads((Path(__file__).parent / "synthetic_scenario.json").read_text(encoding="utf-8"))


def second_request(receipt_id):
    scenario = copy.deepcopy(BASE)
    scenario["events"].extend([
        {"event_id": "e7", "request_id": "fictional-RAID-02", "type": "submit",
         "actor": "demo_requester", "at": "2026-01-01T09:06:00Z",
         "payload": {"action": "publish_status", "scope": "fictional-program"}},
        {"event_id": "e8", "request_id": "fictional-RAID-02", "type": "approve",
         "actor": "demo_reviewer", "at": "2026-01-01T09:07:00Z",
         "payload": {"action": "publish_status", "scope": "fictional-program",
                     "expires_at": "2026-01-01T09:37:00Z"}},
        {"event_id": "e9", "request_id": "fictional-RAID-02", "type": "execute",
         "actor": "demo_executor", "at": "2026-01-01T09:08:00Z",
         "payload": {"approval_id": "e8", "action": "publish_status",
                     "scope": "fictional-program", "receipt_id": receipt_id}},
    ])
    return evaluate(scenario)


class ReceiptIdentityTests(unittest.TestCase):
    def test_unique_second_receipt_is_accepted(self):
        result = second_request("fictional-r2")
        self.assertTrue(result["audit"][-1]["accepted"])
        self.assertEqual(result["requests"]["fictional-RAID-02"]["receipt_id"], "fictional-r2")
        self.assertEqual(result["external_actions"], 0)

    def test_reuse_of_corrected_request_receipt_is_rejected(self):
        result = second_request("r1")
        self.assertFalse(result["audit"][-1]["accepted"],
                         "Cross-request duplicate receipt IDs must not be accepted")
        self.assertIn("duplicate receipt", result["audit"][-1]["reason"])
        self.assertEqual(result["requests"]["fictional-RAID-02"]["status"], "approved")
        self.assertEqual(result["external_actions"], 0)


if __name__ == "__main__":
    unittest.main()
