"""Fictional controls only; no publisher rows or evaluation labels."""
import math
import unittest
import numpy as np
from freshretail_lt_train_hourly_identity_v26 import (
    ABS_TOL, REL_TOL, IdentityAuditError, empty_summary, ingest_block)

class TestTrainOnlyIdentity(unittest.TestCase):
    def test_exact_24_hour_match(self):
        s=ingest_block(empty_summary(),[1.,0.],[1.,0.],[24,24])
        self.assertEqual(s['rows_matching_tolerance'],2)
        self.assertEqual(s['rows_exceeding_tolerance'],0)
    def test_rounding_within_tolerance(self):
        s=ingest_block(empty_summary(),[1.],[1.+ABS_TOL/2],[24])
        self.assertEqual(s['rows_exceeding_tolerance'],0)
    def test_material_mismatch(self):
        s=ingest_block(empty_summary(),[1.],[2.],[24])
        self.assertEqual(s['rows_exceeding_tolerance'],1)
        self.assertEqual(s['rows_abs_difference_over_0_1'],1)
    def test_zero_daily_nonzero_hourly(self):
        s=ingest_block(empty_summary(),[0.],[.5],[24])
        self.assertEqual(s['rows_exceeding_tolerance'],1)
    def test_negative_daily_not_silently_clipped(self):
        s=ingest_block(empty_summary(),[-1.],[-1.],[24],1)
        self.assertEqual(s['rows_negative_daily'],1)
        self.assertEqual(s['hourly_negative_values'],1)
    def test_wrong_length_rejected(self):
        with self.assertRaises(IdentityAuditError): ingest_block(empty_summary(),[1.],[1.],[23])
    def test_null_daily_rejected(self):
        with self.assertRaises((IdentityAuditError,TypeError,ValueError)): ingest_block(empty_summary(),[None],[0.],[24])
    def test_nonfinite_rejected(self):
        for v in (float('nan'),float('inf'),float('-inf')):
            with self.subTest(v=v),self.assertRaises(IdentityAuditError):
                ingest_block(empty_summary(),[v],[0.],[24])
    def test_shape_mismatch_rejected(self):
        with self.assertRaises(IdentityAuditError): ingest_block(empty_summary(),[1.],[1.,2.],[24])
    def test_boolean_count_rejected(self):
        with self.assertRaises(IdentityAuditError): ingest_block(empty_summary(),[1.],[1.],[24],True)
    def test_aggregate_only_no_row_identifiers(self):
        s=ingest_block(empty_summary(),[1.,2.],[1.,3.],[24,24])
        self.assertEqual(s['rows'],2)
        self.assertNotIn('store_id',s)
        self.assertNotIn('product_id',s)
    def test_incremental_batches(self):
        s=empty_summary()
        ingest_block(s,[1.],[1.],[24]); ingest_block(s,[2.],[3.],[24])
        self.assertEqual((s['rows'],s['rows_exceeding_tolerance']),(2,1))

if __name__=='__main__': unittest.main()
