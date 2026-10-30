"""Fictional archive negative controls only. No EEG bytes are used."""
import hashlib
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile
from zenodo_archive_preflight_v09 import audit


class ArchivePreflight(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'S01.zip'

    def fixture(self, members=None):
        if members is None:
            members = [('session_1/run_01.npz', b'FICTIONAL DATA ' * 10)]
        with zipfile.ZipFile(self.path, 'w') as z:
            for name, payload in members:
                z.writestr(name, payload)
        return hashlib.md5(self.path.read_bytes()).hexdigest()

    def test_fictional_good(self):
        md5 = self.fixture()
        r = audit(self.path, md5)
        self.assertEqual(r['status'], 'PASS')
        self.assertEqual(r['member_count'], 1)
        self.assertEqual(r['members'][0]['sha256'], hashlib.sha256(b'FICTIONAL DATA ' * 10).hexdigest())

    def test_wrong_publisher_md5(self):
        self.fixture()
        self.assertEqual(audit(self.path, '0' * 32)['status'], 'FAIL')

    def test_duplicate_member(self):
        md5 = self.fixture([('session_1/run_01.npz', b'a'), ('session_1/run_01.npz', b'b')])
        self.assertEqual(audit(self.path, md5)['status'], 'FAIL')

    def test_traversal(self):
        md5 = self.fixture([('../session_1/run_01.npz', b'a')])
        self.assertEqual(audit(self.path, md5)['status'], 'FAIL')

    def test_backslash(self):
        md5 = self.fixture([('session_1\\run_01.npz', b'a')])
        self.assertEqual(audit(self.path, md5)['status'], 'FAIL')

    def test_absolute(self):
        md5 = self.fixture([('/session_1/run_01.npz', b'a')])
        self.assertEqual(audit(self.path, md5)['status'], 'FAIL')

    def test_unexpected_file(self):
        md5 = self.fixture([('session_1/run_01.pkl', b'a')])
        self.assertEqual(audit(self.path, md5)['status'], 'FAIL')

    def test_member_size_limit(self):
        md5 = self.fixture()
        self.assertEqual(audit(self.path, md5, max_member_bytes=10)['status'], 'FAIL')

    def test_archive_size_limit(self):
        md5 = self.fixture()
        self.assertEqual(audit(self.path, md5, max_zip_bytes=10)['status'], 'FAIL')

    def test_bad_zip(self):
        self.path.write_bytes(b'not a zip')
        md5 = hashlib.md5(self.path.read_bytes()).hexdigest()
        self.assertEqual(audit(self.path, md5)['status'], 'FAIL')

    def test_empty_zip(self):
        md5 = self.fixture([])
        self.assertEqual(audit(self.path, md5)['status'], 'FAIL')

    def test_symlink_member(self):
        with zipfile.ZipFile(self.path, 'w') as z:
            info = zipfile.ZipInfo('session_1/run_01.npz')
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(info, 'target')
        md5 = hashlib.md5(self.path.read_bytes()).hexdigest()
        self.assertEqual(audit(self.path, md5)['status'], 'FAIL')

    def test_zip_bomb_ratio(self):
        with zipfile.ZipFile(self.path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('session_1/run_01.npz', b'0' * 1_000_000)
        md5 = hashlib.md5(self.path.read_bytes()).hexdigest()
        self.assertEqual(audit(self.path, md5)['status'], 'FAIL')

    def test_subject_name(self):
        md5 = self.fixture()
        wrong = self.path.with_name('wrong.zip')
        self.path.rename(wrong)
        self.assertEqual(audit(wrong, md5)['status'], 'FAIL')

    def test_source_unchanged(self):
        md5 = self.fixture()
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        audit(self.path, md5)
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), before)


if __name__ == '__main__':
    unittest.main()
