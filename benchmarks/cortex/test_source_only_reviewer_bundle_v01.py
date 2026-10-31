"""Fictional source-only packaging tests; no reviewer or human timing data."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import source_only_reviewer_bundle_v01 as bundle

CASE_OBJ = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
            "meeting": {"utterances": [{"id": "u01", "text": "Fictional discussion."}]}}
ARCHIVE_OBJ = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
               "records": [{"record_ref": "A01", "decision_id": "H01", "text": "Fictional history."}]}
C = (json.dumps(CASE_OBJ, sort_keys=True) + "\n").encode()
A = (json.dumps(ARCHIVE_OBJ, sort_keys=True) + "\n").encode()


class SourceOnlyBundleTests(unittest.TestCase):
    def packet(self, c=C, a=A):
        with patch.dict(bundle.PINS, {bundle.CASE: bundle.sha256(C),
                                      bundle.ARCHIVE: bundle.sha256(A)}):
            return bundle.build_packet(c, a)

    def test_exact_three_source_only_members(self):
        zipped, m = self.packet()
        with ZipFile(io.BytesIO(zipped)) as z:
            self.assertEqual(z.namelist(), [bundle.CASE, bundle.ARCHIVE,
                                            "REVIEWER_INSTRUCTIONS.txt"])
            self.assertEqual(z.read(bundle.CASE), C)
            self.assertEqual(z.read(bundle.ARCHIVE), A)
            self.assertNotIn(b"ground_truth", z.read("REVIEWER_INSTRUCTIONS.txt"))
        self.assertEqual(m["bundle_sha256"], bundle.sha256(zipped))
        self.assertEqual(m["reviewers"], "TBD")

    def test_deterministic_zip_bytes(self):
        self.assertEqual(self.packet()[0], self.packet()[0])

    def test_modified_source_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.packet(C + b" ")

    def test_crlf_normalization_not_silently_accepted(self):
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.packet(C.replace(b"\n", b"\r\n"))

    def test_extra_interpretation_in_source_fails_hash(self):
        c = copy.deepcopy(CASE_OBJ)
        c["expected_labels"] = ["fictional answer"]
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.packet(json.dumps(c).encode())

    def test_duplicate_json_members_rejected(self):
        with patch.dict(bundle.PINS, {bundle.CASE: bundle.sha256(b'{"synthetic":true,"synthetic":true}'),
                                      bundle.ARCHIVE: bundle.sha256(A)}):
            with self.assertRaises(ValueError):
                bundle.build_packet(b'{"synthetic":true,"synthetic":true}', A)

    def test_output_in_public_repo_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "outside the public repository"):
                bundle.write_packet(root / "private.zip", root, C, A)
            self.assertFalse((root / "private.zip").exists())

    def test_existing_private_file_not_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "already.zip"
            out.write_bytes(b"DO-NOT-OVERWRITE")
            with patch.dict(bundle.PINS, {bundle.CASE: bundle.sha256(C),
                                          bundle.ARCHIVE: bundle.sha256(A)}):
                with self.assertRaises(FileExistsError):
                    bundle.write_packet(out, root / "public", C, A)
            self.assertEqual(out.read_bytes(), b"DO-NOT-OVERWRITE")

    def test_manifest_no_private_or_case_text(self):
        zipped, manifest = self.packet()
        rendered = json.dumps(manifest)
        self.assertNotIn("Fictional discussion", rendered)
        self.assertNotIn("u01", rendered)
        self.assertNotIn("reviewer_code", rendered)


if __name__ == "__main__":
    unittest.main()
