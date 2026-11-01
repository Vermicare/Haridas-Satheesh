"""Read-only, fail-closed inventory of fictional Companion action entry points.

AST names are not evidence of runtime authorization. Classifications are
review hypotheses tied to inspected source, not security certification.
No project code is imported or executed by this scanner.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path

MODULES = (
    'authorization_guard_v02.py', 'authorization_store_v03.py',
    'correction_ledger_v05.py', 'fictional_outbox_v07.py',
    'sandbox_issuer_v10.py', 'revocable_signed_boundary_v11.py',
    'atomic_revocation_delivery_v14.py',
)
ENTRY_NAMES = frozenset({
    'simulate_once', 'execute', '_execute_checked', 'stage', 'dispatch',
    'apply', 'record', 'revoke', 'revoke_digest',
})
# Exact reviewed entry points. A new or missing entry fails the audit.
EXPECTED = {
    'authorization_guard_v02.py::simulate_once': 'FICTIONAL_SIMULATION_ONLY',
    'authorization_store_v03.py::FictionalDurableStore.execute': 'LEGACY_UNGUARDED',
    'correction_ledger_v05.py::FictionalCorrectionLedger.record': 'CORRECTION_FIXTURE_ONLY',
    'fictional_outbox_v07.py::FictionalIdempotentSink.apply': 'LEGACY_UNGUARDED',
    'fictional_outbox_v07.py::FictionalOutbox.stage': 'LEGACY_UNGUARDED',
    'fictional_outbox_v07.py::FictionalOutbox.dispatch': 'LEGACY_UNGUARDED',
    'sandbox_issuer_v10.py::FictionalSignedBoundary.execute': 'SIGNED_NO_REVOCATION',
    'revocable_signed_boundary_v11.py::FictionalRevocableStore.execute': 'EXPLICIT_DENIAL',
    'revocable_signed_boundary_v11.py::FictionalRevocableStore._execute_checked': 'INTERNAL_WRITE_CAPABILITY',
    'revocable_signed_boundary_v11.py::_RevocationBoundStore.execute': 'INTERNAL_ADAPTER',
    'revocable_signed_boundary_v11.py::FictionalRevocableBoundary.execute': 'SIGNED_REVOCABLE_TEST_ONLY',
    'revocable_signed_boundary_v11.py::FictionalRevocableBoundary.revoke': 'UNAUTHENTICATED_TEST_OPERATOR',
    'revocable_signed_boundary_v11.py::FictionalRevocableStore.revoke_digest': 'UNAUTHENTICATED_TEST_OPERATOR',
    'atomic_revocation_delivery_v14.py::AtomicFictionalDelivery.stage': 'PARTIAL_TWO_TRANSACTION_STAGE',
    'atomic_revocation_delivery_v14.py::AtomicFictionalDelivery.dispatch': 'PARTIAL_NO_DISPATCH_EXPIRY',
}

class InventoryError(ValueError):
    pass


def parse_entrypoints(source, filename):
    """Parse syntax without importing source; reject duplicate entry points."""
    try:
        root = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        raise InventoryError(f'invalid Python source: {filename}') from exc
    found = {}
    def record(key, node):
        if key in found:
            raise InventoryError(f'duplicate entry point: {key}')
        found[key] = node.lineno
    for node in root.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in ENTRY_NAMES:
            record(node.name, node)
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name in ENTRY_NAMES:
                    record(f'{node.name}.{method.name}', method)
    return found


def scan(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise InventoryError('source directory missing')
    entries = []
    actual = set()
    sources = []
    for filename in MODULES:
        path = directory / filename
        if path.is_symlink() or not path.is_file():
            raise InventoryError(f'missing or symlink source: {filename}')
        raw = path.read_bytes()
        if len(raw) > 500_000 or b'\0' in raw:
            raise InventoryError(f'oversized or binary source: {filename}')
        normalized = raw.replace(b'\r\n', b'\n')
        if b'\r' in normalized:
            raise InventoryError(f'unexpected CR in source: {filename}')
        try:
            source = normalized.decode('utf-8')
        except UnicodeError as exc:
            raise InventoryError(f'non-UTF-8 source: {filename}') from exc
        sources.append({'path': filename,
                        'sha256_normalized_lf': hashlib.sha256(normalized).hexdigest(),
                        'sha256_checkout_bytes': hashlib.sha256(raw).hexdigest()})
        for qualname, lineno in parse_entrypoints(source, filename).items():
            key = f'{filename}::{qualname}'
            actual.add(key)
            entries.append({'entry': key, 'line': lineno,
                            'review_classification': EXPECTED.get(key, 'UNREVIEWED')})
    if actual != set(EXPECTED):
        raise InventoryError('entrypoint inventory drift: missing=' + repr(sorted(set(EXPECTED)-actual)) +
                             ' unexpected=' + repr(sorted(actual-set(EXPECTED))))
    entries.sort(key=lambda item: item['entry'])
    sources.sort(key=lambda item: item['path'])
    return {'schema': 'companion-fictional-entrypoint-inventory-v1.9',
            'fictional_only': True, 'source_only_no_imports': True,
            'commit': os.environ.get('GITHUB_SHA') or 'TBD',
            'entries': entries, 'source_files': sources,
            'unretired_legacy_routes': sorted(e['entry'] for e in entries if e['review_classification']=='LEGACY_UNGUARDED'),
            'interpretation': 'Static API inventory, not proof of reachability, safety, consent, or isolation.',
            'real_external_actions': 0, 'independent_security_review': 'TBD'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = scan(args.source_dir)
    output = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n'
    if args.output:
        args.output.write_text(output, encoding='utf-8')
    print(output, end='')

if __name__ == '__main__':
    main()
