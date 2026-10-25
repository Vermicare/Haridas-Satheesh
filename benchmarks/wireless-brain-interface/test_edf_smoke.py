"""Fictional EDF headers only; never mislabel tests as real EEG evidence."""
import hashlib
import unittest
from edf_smoke import SmokeError, checksum_from_index, inspect_edf, verify


def fictional_edf(rate=160, annotations=True, truncate=0):
    n = 65
    def field(x, width):
        return str(x).encode('ascii').ljust(width, b' ')
    header = bytearray(b' ' * 256)
    header[0:8] = field(0, 8)
    header[184:192] = field(256 * (n + 1), 8)
    header[236:244] = field(1, 8)
    header[244:252] = field(1, 8)
    header[252:256] = field(n, 4)
    labels = [f'EEG {i:02d}' for i in range(64)] + ['EDF Annotations' if annotations else 'EEG 64']
    header += b''.join(field(x, 16) for x in labels)
    for width in (80, 8, 8, 8, 8, 8, 80):
        header += b''.join(field('', width) for _ in range(n))
    samples = [rate] * 64 + [64]
    header += b''.join(field(x, 8) for x in samples)
    header += b''.join(field('', 32) for _ in range(n))
    assert len(header) == 256 * (n + 1)
    data = bytes(header) + b'\0' * (sum(samples) * 2)
    return data[:len(data) - truncate] if truncate else data


class EDFSmokeTests(unittest.TestCase):
    def setUp(self):
        self.data = fictional_edf()
        self.digest = hashlib.sha256(self.data).hexdigest()
        self.index = f'{self.digest}  S001/S001R04.edf\n'

    def test_structural_valid(self):
        self.assertEqual(inspect_edf(self.data)['eeg_sampling_hz'], 160)
        self.assertEqual(inspect_edf(self.data)['eeg_channels'], 64)

    def test_checksum_bound_to_bytes(self):
        result = verify(self.data, self.index)
        self.assertEqual(result['subject_split'], 'train')
        self.assertFalse(result['decoder_trained'])

    def test_wrong_checksum_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'SHA256'):
            verify(self.data, '0' * 64 + '  S001/S001R04.edf\n')

    def test_duplicate_checksum_entry_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'exactly one'):
            checksum_from_index(self.index + self.index)

    def test_missing_checksum_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'exactly one'):
            checksum_from_index(self.digest + '  S001/S001R06.edf\n')

    def test_truncated_edf_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'length mismatch'):
            inspect_edf(fictional_edf(truncate=2))

    def test_sampling_rate_mismatch_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'sampling rate'):
            inspect_edf(fictional_edf(rate=128))

    def test_annotation_missing_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'annotations channel'):
            inspect_edf(fictional_edf(annotations=False))

    def test_header_count_corruption_rejected(self):
        data = bytearray(self.data)
        data[184:192] = b'9999    '
        with self.assertRaisesRegex(SmokeError, 'header byte count'):
            inspect_edf(bytes(data))

    def test_duplicate_channel_label_rejected(self):
        data = bytearray(self.data)
        data[256 + 16:256 + 32] = data[256:272]
        with self.assertRaisesRegex(SmokeError, 'duplicate'):
            inspect_edf(bytes(data))

if __name__ == '__main__':
    unittest.main()
