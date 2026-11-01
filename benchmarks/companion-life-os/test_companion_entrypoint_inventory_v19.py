"""Fictional-only AST inventory controls; no real connectors or code execution."""
import tempfile
import unittest
from pathlib import Path

from companion_entrypoint_inventory_v19 import (
    EXPECTED, MODULES, InventoryError, parse_entrypoints, scan,
)


class EntryPointInventoryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for module in MODULES:
            entries = [key.split('::', 1)[1] for key in EXPECTED if key.startswith(module + '::')]
            top = sorted(name for name in entries if '.' not in name)
            classes = {}
            for name in entries:
                if '.' in name:
                    cls, method = name.split('.', 1)
                    classes.setdefault(cls, []).append(method)
            lines = ['def ' + name + '():\n    return None\n' for name in top]
            for cls, methods in sorted(classes.items()):
                lines.append('class ' + cls + ':\n')
                lines.extend('    def ' + method + '(self):\n        return None\n' for method in sorted(methods))
            (self.root / module).write_text('\n'.join(lines), encoding='utf-8')

    def test_exact_fixture_passes_and_flags_legacy_routes(self):
        result = scan(self.root)
        self.assertEqual(len(result['entries']), len(EXPECTED))
        self.assertEqual(len(result['unretired_legacy_routes']), 4)
        self.assertEqual(result['real_external_actions'], 0)

    def test_new_unreviewed_dispatch_rejected(self):
        p = self.root / MODULES[0]
        p.write_text(p.read_text() + '\nclass UnknownAdapter:\n    def dispatch(self): pass\n')
        with self.assertRaisesRegex(InventoryError, 'unexpected'):
            scan(self.root)

    def test_missing_known_entry_rejected(self):
        p = self.root / MODULES[0]
        p.write_text('pass\n')
        with self.assertRaisesRegex(InventoryError, 'missing='):
            scan(self.root)

    def test_duplicate_method_rejected(self):
        with self.assertRaisesRegex(InventoryError, 'duplicate'):
            parse_entrypoints('class X:\n def execute(self): pass\n def execute(self): pass\n', 'x.py')

    def test_async_entrypoint_detected(self):
        self.assertEqual(parse_entrypoints('async def dispatch(): pass\n', 'x.py'), {'dispatch': 1})

    def test_syntax_error_fails_closed(self):
        with self.assertRaisesRegex(InventoryError, 'invalid Python'):
            parse_entrypoints('def broken(', 'x.py')

    def test_symlink_source_rejected(self):
        p = self.root / MODULES[0]
        target = self.root / 'target.py'
        target.write_text(p.read_text())
        p.unlink()
        try:
            p.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable on this runner')
        with self.assertRaisesRegex(InventoryError, 'symlink'):
            scan(self.root)

    def test_lf_and_crlf_normalized_hash_equal(self):
        a = scan(self.root)
        p = self.root / MODULES[0]
        p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
        b = scan(self.root)
        self.assertEqual(a['source_files'][0]['sha256_normalized_lf'],
                         b['source_files'][0]['sha256_normalized_lf'])

    def test_source_is_not_modified(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        scan(self.root)
        after = {p.name: p.read_bytes() for p in self.root.iterdir()}
        self.assertEqual(before, after)

    def test_missing_directory_fails_closed(self):
        with self.assertRaisesRegex(InventoryError, 'directory missing'):
            scan(self.root / 'missing')


if __name__ == '__main__':
    unittest.main()
