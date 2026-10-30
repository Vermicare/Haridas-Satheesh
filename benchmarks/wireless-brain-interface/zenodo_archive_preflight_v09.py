#!/usr/bin/env python3
"""Read-only ZIP transfer and member-integrity preflight; NOT EEG authenticity.

No extraction, numpy, unpickling, or signal inspection. Fails closed. Python >=3.10.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

SUBJECT = re.compile(r'^S(0[1-9]|1[0-9]|20)\.zip$')
MEMBER = re.compile(r'^(?:S\d{2}/)?session_[1-9]\d*/run_\d{2}\.npz$')


def audit(path, expected_md5, max_zip_bytes=2_000_000_000,
          max_member_bytes=256_000_000, max_total_bytes=5_000_000_000):
    path = Path(path)
    out = {'schema': 'wbi-zenodo-zip-preflight-v0.9', 'archive_name': path.name,
           'status': 'FAIL', 'checks': [], 'members': [], 'limitations':
           'ZIP checksum/member integrity only; NOT IEEE equivalence, EEG authenticity, event pairing or held-out validation'}
    def check(condition, name):
        out['checks'].append({'check': name, 'pass': bool(condition)})
        if not condition:
            raise ValueError(name)
    try:
        check(bool(SUBJECT.fullmatch(path.name)), 'expected subject ZIP filename')
        check(bool(re.fullmatch(r'[0-9a-fA-F]{32}', expected_md5)), 'publisher MD5 format')
        check(path.is_file() and not path.is_symlink(), 'regular non-symlink archive')
        size = path.stat().st_size
        check(0 < size <= max_zip_bytes, 'bounded compressed archive size')
        md5, sha256 = hashlib.md5(), hashlib.sha256()  # MD5 is publisher transfer checksum only
        with path.open('rb') as source:
            while chunk := source.read(1024 * 1024):
                md5.update(chunk); sha256.update(chunk)
        out['archive_bytes'] = size
        out['archive_md5'] = md5.hexdigest()
        out['archive_sha256'] = sha256.hexdigest()
        check(md5.hexdigest() == expected_md5.lower(), 'publisher transfer MD5 match')
        with zipfile.ZipFile(path) as archive:
            seen = set(); total = 0; files = 0
            for entry in archive.infolist():
                name = entry.filename
                canonical = name.replace('\\', '/')
                parts = PurePosixPath(canonical).parts
                check(name == canonical and not name.startswith('/') and
                      not re.match(r'^[A-Za-z]:', name) and
                      all(p not in ('.', '..', '') for p in parts),
                      'safe member path: ' + repr(name))
                check(canonical not in seen, 'unique member path: ' + repr(name))
                seen.add(canonical)
                mode = entry.external_attr >> 16
                check(not stat.S_ISLNK(mode), 'no symlink: ' + repr(name))
                check(not (entry.flag_bits & 1), 'not encrypted: ' + repr(name))
                if entry.is_dir():
                    continue
                check(bool(MEMBER.fullmatch(name)), 'allowlisted NPZ member path: ' + repr(name))
                check(entry.file_size <= max_member_bytes,
                      'bounded uncompressed member: ' + repr(name))
                check(entry.compress_size > 0 and
                      entry.file_size <= 500 * entry.compress_size,
                      'bounded compression ratio: ' + repr(name))
                total += entry.file_size
                check(total <= max_total_bytes, 'bounded aggregate uncompressed bytes')
                h = hashlib.sha256(); n = 0
                with archive.open(entry, 'r') as member:
                    while chunk := member.read(1024 * 1024):
                        n += len(chunk)
                        check(n <= max_member_bytes, 'streamed member size bound')
                        h.update(chunk)
                check(n == entry.file_size, 'member size matches central directory')
                out['members'].append({'path': name, 'bytes': n,
                                       'sha256': h.hexdigest()})
                files += 1
            check(files > 0, 'at least one NPZ member')
            out['member_count'] = files
            out['total_uncompressed_bytes'] = total
        out['status'] = 'PASS'
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError, EOFError) as error:
        out['failure'] = str(error)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', help='local S01.zip ... S20.zip; never fetched automatically')
    parser.add_argument('--expected-md5', required=True, help='published checksum, not proof of authenticity')
    parser.add_argument('--json-out', help='optional local report path; never writes source archive')
    args = parser.parse_args()
    result = audit(args.archive, args.expected_md5)
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.json_out:
        Path(args.json_out).write_text(payload, encoding='utf-8')
    print(payload, end='')
    return 0 if result['status'] == 'PASS' else 2

if __name__ == '__main__':
    sys.exit(main())
