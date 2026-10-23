import copy
import json
import unittest
from pathlib import Path
from governance_demo import evaluate, verify_audit, digest

BASE = json.loads((Path(__file__).parent / "synthetic_scenario.json").read_text(encoding="utf-8"))


def run(events=None, roles=None, origin="FICTIONAL_SYNTHETIC"):
    scenario = copy.deepcopy(BASE)
    if events is not None:
        scenario["events"] = events
    if roles is not None:
        scenario["declared_roles"] = roles
    scenario["origin"] = origin
    return evaluate(scenario)


class GovernanceTests(unittest.TestCase):
    def test_fictional_happy_path_and_negative_controls(self):
        result = run()
        self.assertEqual((result["accepted"], result["rejected"], result["external_actions"]), (4, 2, 0))
        self.assertEqual(result["requests"]["fictional-RAID-01"]["status"], "corrected")
        self.assertTrue(verify_audit(result))

    def test_deterministic_output(self):
        self.assertEqual(digest(run()), digest(run()))

    def test_reject_unlabeled_or_physical_origin(self):
        with self.assertRaises(ValueError):
            run(origin="PHYSICAL")

    def test_missing_actor(self):
        ev = copy.deepcopy(BASE["events"])
        ev[2]["actor"] = "unlisted-person"
        self.assertFalse(run(ev)["audit"][2]["accepted"])

    def test_reject_self_approval_even_if_declared_reviewer(self):
        ev = copy.deepcopy(BASE["events"])
        ev[2]["actor"] = "demo_requester"
        self.assertFalse(run(ev)["audit"][2]["accepted"])

    def test_approval_scope_mismatch(self):
        ev = copy.deepcopy(BASE["events"])
        ev[2]["payload"]["scope"] = "other-program"
        self.assertFalse(run(ev)["audit"][2]["accepted"])

    def test_cross_request_approval(self):
        ev = copy.deepcopy(BASE["events"])
        ev[3]["payload"]["approval_id"] = "some-other-approval"
        self.assertFalse(run(ev)["audit"][3]["accepted"])

    def test_expired_approval(self):
        ev = copy.deepcopy(BASE["events"])
        ev[2]["payload"]["expires_at"] = "2026-01-01T09:02:30Z"
        self.assertFalse(run(ev)["audit"][3]["accepted"])

    def test_expiry_beyond_one_hour(self):
        ev = copy.deepcopy(BASE["events"])
        ev[2]["payload"]["expires_at"] = "2026-01-01T11:00:00Z"
        self.assertFalse(run(ev)["audit"][2]["accepted"])

    def test_replay_execution_rejected(self):
        self.assertFalse(run()["audit"][4]["accepted"])

    def test_duplicate_event_id_rejected(self):
        ev = copy.deepcopy(BASE["events"])
        ev[3]["event_id"] = "e3"
        self.assertFalse(run(ev)["audit"][3]["accepted"])

    def test_nonmonotonic_time_rejected(self):
        ev = copy.deepcopy(BASE["events"])
        ev[3]["at"] = "2026-01-01T09:00:30Z"
        self.assertFalse(run(ev)["audit"][3]["accepted"])

    def test_timezone_required(self):
        ev = copy.deepcopy(BASE["events"])
        ev[2]["at"] = "2026-01-01T09:02:00"
        self.assertFalse(run(ev)["audit"][2]["accepted"])

    def test_missing_receipt_binding(self):
        ev = copy.deepcopy(BASE["events"])
        ev[5]["payload"]["receipt_id"] = "unrelated-receipt"
        self.assertFalse(run(ev)["audit"][5]["accepted"])

    def test_correction_requires_reason(self):
        ev = copy.deepcopy(BASE["events"])
        ev[5]["payload"]["reason"] = "  "
        self.assertFalse(run(ev)["audit"][5]["accepted"])

    def test_audit_tampering_detected(self):
        result = run()
        result["audit"][1]["reason"] = "forged acceptance"
        self.assertFalse(verify_audit(result))

    def test_input_hash_changes_with_mutation(self):
        ev = copy.deepcopy(BASE["events"])
        ev[0]["payload"]["scope"] = "altered"
        self.assertNotEqual(run(ev)["audit"][0]["input_sha256"], run()["audit"][0]["input_sha256"])

    def test_no_real_external_action_even_when_accepted(self):
        self.assertEqual(run()["external_actions"], 0)

    def test_invalid_event_schema(self):
        ev = copy.deepcopy(BASE["events"])
        ev[0]["unexpected"] = "extra"
        self.assertFalse(run(ev)["audit"][0]["accepted"])


if __name__ == "__main__":
    unittest.main()
