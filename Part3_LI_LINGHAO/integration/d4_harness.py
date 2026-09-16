"""D4 orchestration and independent grading. Never supplies labels to the agent."""
import csv
import hashlib
import html
import json
import statistics
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from . import config
from .runner import run_case
from .protocol import FIELDS

DATASET = config.ROOT / 'integration/merged_A'
REVIEW_FIELDS = ['review_id', 'case_id', 'trial', 'criterion', 'verdict', 'graded_by', 'comments', 'record_path']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_contract(root=DATASET):
    labels = read(root / 'expected_outcomes_A.json')
    audits = read(root / 'case_audit.json')
    claims = read(root / 'data_A/claims.json')
    ids = [x['case_id'] for x in labels]
    if len(ids) != 45 or len(set(ids)) != 45 or set(ids) != {x['claim_id'] for x in claims} or set(ids) != {x['case_id'] for x in audits}:
        raise ValueError('Frozen claims, labels and audit must contain the same 45 unique IDs')
    expected = {x['case_id']: x for x in audits}
    for label in labels:
        audit = expected[label['case_id']]
        if label['expected_decision'] != audit['decision'] or label.get('trigger') != audit.get('trigger'):
            raise ValueError('Stale review: label/audit mismatch')
        if label['must_record'] != audit['must_record']:
            raise ValueError('Stale judgement criteria')
    return labels, expected


def code_check(record, expected):
    """Grade factual fields and real write/trace consistency; prose is reviewed separately."""
    failures = []
    def check(ok, message):
        if not ok:
            failures.append(message)
    check(record.get('case_id') == expected['case_id'], 'wrong case ID')
    check(record.get('status') == 'completed', 'execution not completed: ' + str(record.get('status')))
    check(record.get('decision') == expected['decision'], 'wrong decision')
    logs = record.get('action_records') or []
    check(record.get('action_count') == 1 and len(logs) == 1, 'expected one actual gated write')
    if len(logs) == 1:
        check(logs[0].get('case_id') == expected['case_id'], 'write has wrong case ID')
        for field in FIELDS:
            check(logs[0].get(field) == record.get(field), 'write/final mismatch: ' + field)
    trace = record.get('trace') or []
    check(bool(trace) and all(x['status'] == 'ok' for x in trace), 'missing or unsuccessful tool trace')
    observed = {x['tool'] for x in trace if x['status'] == 'ok'}
    check({'get_claim', 'issue_decision_letter'} <= observed, 'missing read/write evidence')
    check(bool(record.get('evidence')) and set(record.get('evidence') or []) <= observed, 'unsupported evidence citations')
    if expected['decision'] == 'escalate':
        check(record.get('trigger') == expected['trigger'], 'wrong escalation trigger')
        check(record.get('escalate_to') == 'human claims assessor', 'wrong escalation recipient')
        if expected['trigger'] in ('policy_lapsed', 'outside_policy_dates', 'annual_limit_exceeded'):
            check('lookup_policy' in observed, 'policy evidence missing')
        if expected['trigger'] == 'duplicate_claim':
            check('check_duplicate' in observed, 'duplicate evidence missing')
    else:
        check({'lookup_member', 'lookup_policy', 'check_duplicate', 'get_hospital_status'} <= observed, 'missing core coverage evidence')
        lines = record.get('lines') or []
        check(len(lines) == len(expected['lines']), 'wrong line count')
        # Match occurrences rather than indexing by code: two billed lines may
        # share a code and amount. Consume each occurrence exactly once.
        unmatched = list(lines)
        for line in expected['lines']:
            fields = ('code', 'amount', 'status', 'exclusion', 'preauth')
            match = next((i for i, candidate in enumerate(unmatched)
                          if all(candidate.get(f) == line[f] for f in fields if f in line)), None)
            got = unmatched.pop(match) if match is not None else {}
            for field in fields:
                if field in line:
                    check(got.get(field) == line[field], f"{line['code']}: wrong {field}")
            for tool, arg in [('check_procedure', 'code'), ('check_documents', 'procedure_code')]:
                check(any(x['tool'] == tool and x['args'].get(arg) == line['code'] and x['status'] == 'ok' for x in trace), f"{line['code']}: missing {tool}")
            if 'preauthorisation_records' in line:
                check(any(x['tool'] == 'get_preauthorisation' and x['args'].get('procedure_code') == line['code'] and x['status'] == 'ok' for x in trace), f"{line['code']}: missing preauth lookup")
        if expected['decision'] == 'request_document':
            missing = dict(record.get('missing') or {})
            if isinstance(missing.get('item'), str):
                missing['item'] = missing['item'].replace('_', ' ')
            check(missing == expected['missing'], 'wrong named missing item / line / service date')
        else:
            for field in ('approved_total', 'refused_total'):
                check(record.get(field) == expected[field], 'wrong ' + field)
    return failures


def summarize(rows):
    result = {'trials': len(rows), 'cases': len({x['case_id'] for x in rows}),
              'code_passed': sum(x['code_passed'] for x in rows),
              'execution_errors': sum(x['record'].get('status') != 'completed' for x in rows),
              'judgement_passed': sum(x['judgement'] == 'pass' for x in rows),
              'judgement_failed': sum(x['judgement'] == 'fail' for x in rows),
              'judgement_pending': sum(x['judgement'] == 'pending' for x in rows),
              'overall_passed': sum(x['code_passed'] and x['judgement'] == 'pass' for x in rows)}
    for name, negative in [('ordinary', False), ('negative', True)]:
        subset = [x for x in rows if x['negative'] == negative]
        result[name] = {'trials': len(subset), 'code_passed': sum(x['code_passed'] for x in subset),
                        'overall_passed': sum(x['code_passed'] and x['judgement'] == 'pass' for x in subset)}
    for field in ('turns', 'tokens_in', 'tokens_out', 'cost_usd'):
        values = [x['record'][field] for x in rows if x['record'].get(field) is not None]
        result[field] = {'measured_trials': len(values), 'total': sum(values),
                         'median': statistics.median(values) if values else None,
                         'max': max(values) if values else None}
    result['step_cap_hits'] = sum(x['record'].get('stopped_by') == 'step_cap' for x in rows)
    return result


def export_results(suite, rows, metadata):
    summary = dict(summarize(rows), **metadata, suite=str(suite.resolve()))
    write(suite / 'results.json', rows)
    write(suite / 'summary.json', summary)
    with (suite / 'results.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.writer(handle)
        writer.writerow(['case_id', 'trial', 'negative', 'status', 'decision', 'code_passed', 'judgement', 'overall_passed', 'turns', 'tokens_in', 'tokens_out', 'cost_usd', 'failures'])
        for r in rows:
            a = r['record']
            writer.writerow([r['case_id'], r['trial'], r['negative'], a.get('status'), a.get('decision'), r['code_passed'], r['judgement'], r['code_passed'] and r['judgement'] == 'pass', a.get('turns'), a.get('tokens_in'), a.get('tokens_out'), a.get('cost_usd'), '; '.join(r['failures'])])
    return summary


def run_battery(output_dir, *, backend='scripted', version='v2', model=config.MODEL,
                price_in=None, price_out=None, executor=run_case):
    if backend == 'live' and (price_in is None or price_out is None):
        raise ValueError('Live runs require explicit per-million-token prices')
    labels, expected = load_contract()
    parent = Path(output_dir)
    parent.mkdir(parents=True, exist_ok=True)
    suite = Path(tempfile.mkdtemp(prefix='suite-', dir=parent)).resolve()
    metadata = {'backend': backend, 'prompt_version': version, 'model': model if backend == 'live' else 'scripted',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'operator_confirmation': 'simulated for local decision-log writes',
                'cost_basis': 'synthetic; API cost zero' if backend == 'scripted' else 'API usage times configured prices',
                'judgement_policy': 'every completed trial, every must_record criterion; no propagation between repeats',
                'implementation_sha256': {p.name: sha(p) for p in sorted(Path(__file__).parent.glob('*.py'))},
                'scripted_library_sha256': sha(Path(__file__).with_name('scripted_library.json')),
                'dataset_sha256': {str(p.relative_to(DATASET)): sha(p) for p in sorted(DATASET.rglob('*.json'))}}
    write(suite / 'metadata.json', metadata)
    write(suite / 'grading_contract.json', {'labels': labels, 'audit': expected})
    rows, reviews, pages = [], [], []
    for label in labels:
        cid = label['case_id']
        negative = label['expected_decision'] != 'approve_in_principle'
        for trial in range(1, (3 if negative else 1) + 1):
            try:
                record = executor(cid, data_dir=DATASET / 'data_A', output_dir=suite,
                                  backend=backend, prompt_version=version, model=model,
                                  price_in_per_m=price_in, price_out_per_m=price_out,
                                  operator_approved=True)
            except Exception as exc:
                record = {'case_id': cid, 'status': 'execution_error', 'error': f'{type(exc).__name__}: {exc}'}
            failures = code_check(record, expected[cid])
            row = {'case_id': cid, 'trial': trial, 'negative': negative, 'code_passed': not failures,
                   'failures': failures, 'record': record,
                   'judgement': 'pending' if record['status'] == 'completed' else 'not_reviewable'}
            rows.append(row)
            record_path = f'{cid}-trial-{trial}.json'
            write(suite / record_path, record)
            if row['judgement'] == 'pending':
                pages.append(f'<h2>{cid} / trial {trial}</h2><pre>{html.escape(json.dumps(record, indent=2, ensure_ascii=False))}</pre>')
                for index, criterion in enumerate(label['must_record'], 1):
                    reviews.append({'review_id': f'{cid}/{trial}/{index}', 'case_id': cid, 'trial': trial,
                                    'criterion': criterion, 'verdict': '', 'graded_by': '', 'comments': '', 'record_path': record_path})
    with (suite / 'human_review.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        writer.writerows(reviews)
    write(suite / 'review_template.json', reviews)
    (suite / 'review_records.html').write_text('<!doctype html><meta charset="utf-8"><title>D4 review records</title><style>body{max-width:1000px;margin:30px auto;font-family:system-ui}pre{white-space:pre-wrap;background:#f4f4f4;padding:15px}</style><h1>Actual run records / 真实运行记录</h1><p>填写同目录 human_review.csv；每条要求 pass / fail，填写姓名；不确定保留空白。代码通过不等于理由通过。</p>' + ''.join(pages), encoding='utf-8')
    return export_results(suite, rows, metadata)


def import_reviews(suite, review_file):
    suite = Path(suite).resolve()
    template = read(suite / 'review_template.json')
    known = {x['review_id']: x for x in template}
    with Path(review_file).open(encoding='utf-8-sig', newline='') as handle:
        entries = list(csv.DictReader(handle))
    if len(entries) != len(known) or {x['review_id'] for x in entries} != set(known):
        raise ValueError('Review IDs missing, duplicated or from another suite')
    grouped = {}
    for x in entries:
        original = known[x['review_id']]
        for key in ('case_id', 'trial', 'criterion', 'record_path'):
            if str(x[key]) != str(original[key]):
                raise ValueError('Do not edit identity, criterion or record columns: ' + x['review_id'])
        verdict = x['verdict'].strip().lower()
        if verdict not in ('', 'pass', 'fail'):
            raise ValueError('verdict must be blank, pass or fail')
        if verdict and not x['graded_by'].strip():
            raise ValueError('Every verdict requires graded_by')
        if verdict == 'fail' and not x['comments'].strip():
            raise ValueError('Explain failed criteria in comments')
        grouped.setdefault((x['case_id'], int(x['trial'])), []).append(verdict)
    rows = read(suite / 'results.json')
    for row in rows:
        verdicts = grouped.get((row['case_id'], row['trial']))
        if verdicts is not None:
            row['judgement'] = 'fail' if 'fail' in verdicts else 'pass' if all(x == 'pass' for x in verdicts) else 'pending'
    write(suite / 'human_reviews_imported.json', entries)
    return export_results(suite, rows, read(suite / 'metadata.json'))
