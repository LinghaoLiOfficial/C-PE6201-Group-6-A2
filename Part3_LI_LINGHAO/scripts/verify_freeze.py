#!/usr/bin/env python3
"""Verify release files without network, API keys, or modifying the workspace."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'release_manifest.json').read_text())
    failures = []
    for item in manifest['files']:
        p = ROOT / item['path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
            failures.append(item['path'])
    if failures:
        print('FREEZE MISMATCH: ' + ', '.join(failures))
        return 1
    print(f"{manifest['release']}: {len(manifest['files'])} frozen files verified")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
