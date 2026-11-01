"""Fictional-only adversarial tests. No publisher file or EVAL label accessed."""
import datetime as dt
import unittest
import freshretail_lt_train_cohort_v19 as gate


def fictional(store, product, day, flags=None, count=0):
    return {"store_id": store, "product_id": product, "dt": day.isoformat(),
            "hours_stock_status": [0] * 24 if flags is None else flags,
            "stock_hour6_22_cnt": count}


def series(store, product, n=90):
    return [fictional(store, product, gate.START + dt.timedelta(days=i))
            for i in range(n)]


class TrainingCohortV19Tests(unittest.TestCase):
    def test_complete_train_only_two_series_freezes_without_eval(self):
        rows = series(1, 2) + series(3, 4)
        r = gate.audit_training_rows(rows, cohort_size=2)
        self.assertEqual(r["status"], "TRAIN_COHORT_FROZEN_NO_EVAL_ACCESS")
        self.assertEqual(r["eligible_complete_valid_series"], 2)
        self.assertEqual(r["selected_series"], 2)
        self.assertEqual(len(r["selected_cohort_sha256"]), 64)
        self.assertFalse(r["evaluation_file_opened"])
        self.assertFalse(r["evaluation_labels_read"])
        self.assertEqual(r["forecast_scores"], "TBD")

    def test_permutation_invariant_cohort_digest(self):
        rows = series(1, 2) + series(3, 4) + series(5, 6)
        a = gate.audit_training_rows(rows, cohort_size=2)
        b = gate.audit_training_rows(list(reversed(rows)), cohort_size=2)
        self.assertEqual(a["selected_cohort_sha256"], b["selected_cohort_sha256"])

    def test_missing_training_day_never_replaced_by_future(self):
        rows = series(1, 2, 89) + series(3, 4)
        r = gate.audit_training_rows(rows, cohort_size=2)
        self.assertEqual(r["status"], "STOP_INSUFFICIENT_ELIGIBLE_TRAIN_SERIES")
        self.assertEqual(r["selected_cohort_sha256"], "TBD")
        self.assertEqual(r["selected_series"], 0)

    def test_duplicate_training_day_disqualifies_series(self):
        rows = series(1, 2) + series(3, 4)
        rows.append(rows[0].copy())
        r = gate.audit_training_rows(rows, cohort_size=2)
        self.assertEqual(r["duplicate_training_rows"], 1)
        self.assertEqual(r["eligible_complete_valid_series"], 1)
        self.assertEqual(r["status"], "STOP_INSUFFICIENT_ELIGIBLE_TRAIN_SERIES")

    def test_inconsistent_hourly_status_disqualifies_series(self):
        rows = series(1, 2) + series(3, 4)
        rows[0] = fictional(1, 2, gate.START, [1] * 24, 0)
        r = gate.audit_training_rows(rows, cohort_size=2)
        self.assertEqual(r["invalid_stock_status_rows"], 1)
        self.assertEqual(r["eligible_complete_valid_series"], 1)

    def test_future_training_date_fails_closed(self):
        rows = series(1, 2)
        rows.append(fictional(1, 2, gate.ORIGIN))
        with self.assertRaises(gate.CohortGateError):
            gate.audit_training_rows(rows, cohort_size=1)

    def test_invalid_identifiers_and_date_rejected(self):
        for changed in ({"store_id": True}, {"product_id": -1}, {"dt": "2025-07-14T00:00:00"},
                        {"dt": None}):
            with self.subTest(changed=changed):
                row = fictional(1, 2, gate.START)
                row.update(changed)
                with self.assertRaises(gate.CohortGateError):
                    gate.audit_training_rows([row], cohort_size=1)

    def test_bad_status_shapes_fail(self):
        for flags, count in (([0] * 23, 0), ([0] * 23 + [2], 0),
                             ([0] * 24, True), ([0] * 24, 17)):
            with self.subTest(flags=flags, count=count):
                rows = series(1, 2)
                rows[0] = fictional(1, 2, gate.START, flags, count)
                r = gate.audit_training_rows(rows, cohort_size=1)
                self.assertEqual(r["status"], "STOP_INSUFFICIENT_ELIGIBLE_TRAIN_SERIES")

    def test_earlier_rows_ignored_but_never_used_for_selection(self):
        rows = series(1, 2)
        rows.append(fictional(99, 99, gate.START - dt.timedelta(days=1)))
        r = gate.audit_training_rows(rows, cohort_size=1)
        self.assertEqual(r["distinct_training_series"], 1)
        self.assertEqual(r["earlier_training_rows_ignored"], 1)
        self.assertEqual(r["selected_series"], 1)

    def test_no_eval_path_or_eval_reader_exists_in_cli(self):
        self.assertEqual(set(gate.FIELDS),
                         {"store_id", "product_id", "dt", "hours_stock_status",
                          "stock_hour6_22_cnt"})
        self.assertEqual(gate.COHORT, 512)
        self.assertEqual(gate.DAYS, 90)


if __name__ == "__main__":
    unittest.main()
