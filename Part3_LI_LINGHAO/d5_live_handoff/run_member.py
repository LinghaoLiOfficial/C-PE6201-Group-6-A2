#!/usr/bin/env python3
"""Portable D5 dispatch wrapper. Frozen runner/harness stay unchanged."""
import argparse
import getpass
import hashlib
import json
import math
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'runtime'))
from integration import config
from integration.d4_harness import load_contract, run_battery, read, write, sha, code_check
from integration.runner import run_case


def verify():
    manifest = read(ROOT / 'package_manifest.json')
    for name, digest in manifest.items():
        if sha(ROOT / name) != digest:
            raise ValueError('Package changed: ' + name)
    return sha(ROOT / 'package_manifest.json')


def authenticate():
    if not os.environ.get('OPENROUTER_API_KEY'):
        os.environ['OPENROUTER_API_KEY'] = getpass.getpass('Personal OpenRouter key (hidden; not saved): ')
    if not os.environ['OPENROUTER_API_KEY']:
        raise ValueError('No API key supplied')


def run(a, cid, output, backend='live'):
    return run_case(cid, backend=backend, prompt_version=a['version'],
                    data_dir=config.ROOT / 'integration/merged_A/data_A', output_dir=output,
                    model=a['model'], price_in_per_m=a['price_in'],
                    price_out_per_m=a['price_out'], operator_approved=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['verify', 'offline', 'preflight', 'release', 'full', 'pack'])
    p.add_argument('--preflight', type=Path)
    p.add_argument('--release', type=Path)
    p.add_argument('--suite', type=Path)
    p.add_argument('--note', default='')
    args = p.parse_args()
    digest = verify()
    a = read(ROOT / 'assignment.json')
    for k in ['price_in', 'price_out', 'member_budget_usd']:
        if not isinstance(a[k], (int, float)) or not math.isfinite(a[k]) or a[k] < 0:
            raise ValueError('Invalid price/budget')
    if args.action == 'verify':
        print('Verified package', a['member'], a['model'], a['version'], digest)
        return
    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    if args.action == 'offline':
        s = run_battery(output / 'offline', version=a['version'])
        print(json.dumps(s, indent=2))
        return
    if args.action == 'preflight':
        authenticate()
        folder = Path(tempfile.mkdtemp(prefix='preflight-', dir=output))
        labels, expected = load_contract()
        selected = [next(x['case_id'] for x in labels if x['expected_decision'] == d)
                    for d in ['approve_in_principle', 'request_document', 'escalate']]
        records = [run(a, cid, folder) for cid in selected]
        spent = sum(r['cost_usd'] for r in records)
        ordinary_cost = records[0]['cost_usd']
        negative_cost = max(r['cost_usd'] for r in records[1:])
        estimate = spent + 1.5 * (30 * ordinary_cost + 45 * negative_cost)
        report = dict(assignment=a, package_sha256=digest,
                      created_at=datetime.now(timezone.utc).isoformat(),
                      records=records, code_failures=[code_check(r, expected[r['case_id']]) for r in records],
                      observed_cost_usd=spent, projected_agent_total_usd=estimate,
                      estimate_note='1.5x observed strata cost plus preflight; not a guarantee; judge extra',
                      transport_ok=all(r['responses'] and r['stopped_by'] != 'backend_error' for r in records))
        write(folder / 'preflight.json', report)
        print('Send this entire preflight folder to LI_LINGHAO:', folder)
        print('Projected agent spend including preflight: USD', round(estimate, 4))
        return
    if args.action == 'release':
        if not args.preflight or not args.note.strip():
            raise ValueError('Coordinator requires --preflight FILE --note REVIEW_NOTES')
        pre = read(args.preflight)
        if pre['package_sha256'] != digest or pre['assignment'] != a:
            raise ValueError('Preflight belongs to another package')
        if not pre['transport_ok'] or pre['projected_agent_total_usd'] > a['member_budget_usd']:
            raise ValueError('Transport or projected budget failed; investigate before release')
        release = dict(package_sha256=digest, preflight_sha256=sha(args.preflight),
                       preflight_cost_usd=pre['observed_cost_usd'],
                       reviewed_by='LI_LINGHAO', note=args.note,
                       created_at=datetime.now(timezone.utc).isoformat())
        write(args.preflight.parent / 'release.json', release)
        print(args.preflight.parent / 'release.json')
        return
    if args.action == 'full':
        if not args.release or not args.preflight:
            raise ValueError('Full run requires --release FILE and --preflight FILE')
        rel = read(args.release)
        if rel['package_sha256'] != digest or rel['preflight_sha256'] != sha(args.preflight):
            raise ValueError('Release does not match this package/preflight')
        if list(output.glob('full-started.json')):
            raise ValueError('Full run already started. Keep original evidence; contact coordinator, do not overwrite/retry.')
        authenticate()
        write(output / 'full-started.json', dict(release=rel, assignment=a))
        spent = rel['preflight_cost_usd']
        transport_failed = False
        def execute(cid, **kwargs):
            nonlocal spent, transport_failed
            # Preserve every trial in the denominator after a spending stop.
            # Existing per-trial ceiling is checked after a call, not a provider hard cap.
            if spent >= a['member_budget_usd']:
                raise RuntimeError('member_budget_exhausted; trial not executed')
            if transport_failed:
                raise RuntimeError('prior_backend_error; stopped further paid calls, trial not executed')
            r = run_case(cid, **kwargs)
            spent += r['cost_usd']
            transport_failed = r.get('stopped_by') == 'backend_error'
            print(cid, r['status'], 'observed spend', round(spent, 5), flush=True)
            return r
        summary = run_battery(output / 'full', backend='live', version=a['version'],
                              model=a['model'], price_in=a['price_in'], price_out=a['price_out'], executor=execute)
        suite = Path(summary['suite'])
        write(suite / 'assignment.json', a)
        write(suite / 'release.json', rel)
        write(suite / 'preflight.json', read(args.preflight))
        write(suite / 'dispatch_receipt.json', dict(package_sha256=digest, observed_agent_spend_usd=spent,
              note='Judgement remains pending until coordinator runs independent judge; unknown provider charges are not zero.'))
        print('Return complete suite:', suite)
        return
    if args.action == 'pack':
        if not args.suite:
            raise ValueError('--suite DIR required')
        suite = args.suite.resolve()
        if output.resolve() not in suite.parents:
            raise ValueError('Only a suite inside package/output may be packed')
        rows = read(suite / 'results.json')
        labels, _ = load_contract()
        wanted = {(l['case_id'], t) for l in labels for t in range(1, (1 if l['expected_decision']=='approve_in_principle' else 3)+1)}
        if len(rows) != 75 or {(r['case_id'],r['trial']) for r in rows} != wanted:
            raise ValueError('Not a complete 75-row battery; return partial folder separately and report interruption')
        files = [f for f in suite.rglob('*') if f.is_file()]
        for f in files:
            if f.is_symlink() or f.name == '.env' or b'sk-or-v1-' in f.read_bytes():
                raise ValueError('Potential secret/unsafe file: ' + f.name)
        target = output / ('D5_RETURN_' + a['member'] + '.zip')
        with ZipFile(target, 'w', ZIP_DEFLATED) as z:
            for f in files: z.write(f, Path('suite') / f.relative_to(suite))
            z.write(ROOT / 'assignment.json', 'assignment.json')
            z.write(ROOT / 'package_manifest.json', 'package_manifest.json')
        print(target)

if __name__ == '__main__':
    main()
