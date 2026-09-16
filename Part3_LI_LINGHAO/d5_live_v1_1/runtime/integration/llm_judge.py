"""Auditable, resumable second-model judgement; never rewrites source trials."""
import copy
import csv
import hashlib
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from . import config
from .backends import judge_call
from .d4_harness import read, write, export_results

PROMPT = Path(__file__).with_name('judge_prompt.md')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_key():
    if os.environ.get('OPENROUTER_API_KEY'):
        return
    path = config.ROOT / '.env'
    if path.exists():
        for line in path.read_text().splitlines():
            name, sep, value = line.strip().partition('=')
            if sep and name == 'OPENROUTER_API_KEY':
                os.environ[name] = value.strip().strip('"\'')
                return
    raise ValueError('OPENROUTER_API_KEY missing')


def validate_verdict(text, case_id, trial, criteria):
    # Some providers wrap valid JSON despite response_format. Accept one exact
    # fence wrapper only; never extract a JSON fragment from surrounding prose.
    text = text.strip()
    if text.startswith('```json\n') and text.endswith('\n```'):
        text = text[8:-4]
    elif text.startswith('```\n') and text.endswith('\n```'):
        text = text[4:-4]
    value = json.loads(text)
    if value.get('case_id') != case_id or value.get('trial') != trial:
        raise ValueError('Judge response identity mismatch')
    items = value.get('criteria')
    wanted = {x['review_id'] for x in criteria}
    if not isinstance(items, list) or len(items) != len(wanted) or {x.get('review_id') for x in items} != wanted:
        raise ValueError('Missing, duplicate or unknown judge criteria')
    for item in items:
        if item.get('verdict') not in ('pass', 'fail', 'uncertain'):
            raise ValueError('Invalid judge verdict')
        if not isinstance(item.get('rationale'), str) or not item['rationale'].strip():
            raise ValueError('Missing judge rationale')
        refs = item.get('evidence_refs')
        if not isinstance(refs, list) or not all(isinstance(x, str) and x for x in refs):
            raise ValueError('Invalid evidence references')
        if item['verdict'] == 'pass' and not refs:
            raise ValueError('Pass without cited evidence')
    return value


def run_judge(suite, *, model='anthropic/claude-haiku-4.5', price_in=1.0,
              price_out=5.0, budget=2.0, max_calls=75, caller=judge_call):
    suite = Path(suite).resolve()
    if any(not math.isfinite(x) or x < 0 for x in (price_in, price_out, budget)):
        raise ValueError('Prices and budget must be finite and nonnegative')
    if type(max_calls) is not int or max_calls < 0:
        raise ValueError('max_calls must be a nonnegative integer')
    metadata = read(suite / 'metadata.json')
    source = read(suite / 'results.json')
    for agent_model in [metadata.get('model')] + [r['record'].get('model') for r in source]:
        if agent_model and model.split(':')[0] == agent_model.split(':')[0]:
            raise ValueError('Judge must be a different model from the evaluated agent')
    template = read(suite / 'review_template.json')
    prompt = PROMPT.read_text(encoding='utf-8')
    contract = {'judge_model': model, 'prompt': prompt, 'source_sha256': fingerprint(source),
                'criteria_sha256': fingerprint(template), 'price_in_per_m': price_in,
                'price_out_per_m': price_out, 'base_url': config.BASE_URL, 'max_output_tokens': 2400}
    folder = suite / ('llm_judge_' + fingerprint(contract)[:12])
    folder.mkdir(exist_ok=True)
    write(folder / 'judge_config.json', contract)
    (folder / 'judge_prompt.md').write_text(prompt, encoding='utf-8')
    grouped = {}
    for item in template:
        grouped.setdefault((item['case_id'], int(item['trial'])), []).append(item)
    entries, spent, new_calls = [], 0.0, 0
    # Count every recorded call, including invalid responses, before resuming.
    for path in folder.glob('call-*.json'):
        spent += read(path).get('cost_usd', 0)
    for row in source:
        cid, trial = row['case_id'], row['trial']
        criteria = grouped.get((cid, trial))
        if not criteria:
            continue
        path = folder / f'call-{cid}-{trial}.json'
        if path.exists():
            cached = read(path)
            if cached.get('error_type') == 'JSONDecodeError' and 'response' in cached:
                try:
                    cached['verdict'] = validate_verdict(cached['response']['choices'][0]['message']['content'], cid, trial, criteria)
                    cached['status'] = 'completed'
                    cached['reparsed_locally'] = True
                    write(path, cached)
                except (ValueError, KeyError):
                    pass
            entries.append(cached)
            continue
        if new_calls >= max_calls:
            break
        record = row['record']
        # Keep only actual decision/trace evidence; no audit-derived answer fields.
        payload = {'case_id': cid, 'trial': trial,
                   'criteria': [{'review_id': x['review_id'], 'criterion': x['criterion']} for x in criteria],
                   'record': {k: record.get(k) for k in ('decision','reason','lines','trigger','missing',
                              'approved_total','refused_total','escalate_to','evidence','action_records','trace')}}
        messages = [{'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}]
        # UTF-8 bytes are a conservative upper estimate for token budget planning.
        reservation = len(json.dumps(messages, ensure_ascii=False).encode()) * price_in / 1e6 + 2400 * price_out / 1e6 + 0.01
        if spent + reservation > budget:
            break
        entry = {'case_id': cid, 'trial': trial, 'request': messages, 'judge_model': model,
                 'timestamp': datetime.now(timezone.utc).isoformat(), 'status': 'error',
                 'cost_usd': 0, 'budget_reservation_usd': reservation}
        began = time.monotonic()
        try:
            response = caller(messages, model, config.BASE_URL, max_tokens=2400)
            entry['response'] = response
            usage = response.get('usage', {})
            if any(type(usage.get(k)) is not int or usage[k] < 0 for k in ('prompt_tokens', 'completion_tokens')):
                raise ValueError('Missing provider token usage')
            entry['usage'] = usage
            entry['cost_usd'] = (usage['prompt_tokens'] * price_in + usage['completion_tokens'] * price_out) / 1e6
            actual = response.get('model', '')
            if actual and actual.split(':')[0] != model.split(':')[0]:
                raise ValueError('Provider returned unexpected judge model')
            entry['verdict'] = validate_verdict(response['choices'][0]['message']['content'], cid, trial, criteria)
            entry['status'] = 'completed'
        except Exception as exc:
            # Error bodies may contain provider/request details; store type only.
            entry['error_type'] = type(exc).__name__
            if 'usage' not in entry:
                entry['cost_usd'] = reservation
                entry['cost_uncertain'] = True
        entry['elapsed_seconds'] = round(time.monotonic() - began, 3)
        write(path, entry)
        entries.append(entry)
        spent += entry['cost_usd']
        new_calls += 1
        print(f"{cid} trial {trial}: judge {entry['status']}; spent/reserved ${spent:.4f}", flush=True)
        # Avoid repeated credential/provider failures; safe resume uses the same folder.
        if entry.get('error_type') in ('HTTPError', 'URLError', 'TimeoutError'):
            break
    judged = copy.deepcopy(source)
    by_id = {(x['case_id'], x['trial']): x for x in entries}
    review_rows = []
    for row in judged:
        key = (row['case_id'], row['trial'])
        if key not in grouped:
            continue
        row['judgement'] = 'pending'
        call = by_id.get(key)
        if not call or call['status'] != 'completed':
            continue
        decisions = call['verdict']['criteria']
        values = [x['verdict'] for x in decisions]
        row['judgement'] = 'fail' if 'fail' in values else 'pending' if 'uncertain' in values else 'pass'
        row['judged_by'] = 'model:' + model
        for item in decisions:
            original = next(x for x in grouped[key] if x['review_id'] == item['review_id'])
            review_rows.append(dict(original, verdict=item['verdict'], graded_by='model:' + model,
                                    comments=item['rationale'], record_path='../' + original['record_path'],
                                    evidence_refs='; '.join(item['evidence_refs'])))
    with (folder / 'model_reviews.csv').open('w', newline='', encoding='utf-8-sig') as f:
        fields = ['review_id','case_id','trial','criterion','verdict','graded_by','comments','record_path','evidence_refs']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(review_rows)
    completed = sum(x['status'] == 'completed' for x in entries)
    judge_meta = dict(metadata, judgement_policy='second-model judge, every trial and criterion',
                      judge_model=model, judge_calls_completed=completed,
                      judge_calls_error=sum(x['status'] != 'completed' for x in entries),
                      judge_calls_pending=len(grouped) - len(entries),
                      judge_cost_usd=spent, judge_cost_includes_reservations=any(x.get('cost_uncertain') for x in entries),
                      judge_budget_usd=budget, source_suite=str(suite))
    judge_meta['judge_tokens_in'] = sum(x.get('usage', {}).get('prompt_tokens', 0) for x in entries)
    judge_meta['judge_tokens_out'] = sum(x.get('usage', {}).get('completion_tokens', 0) for x in entries)
    judge_meta['judge_criteria'] = {v: sum(x['verdict'] == v for x in review_rows) for v in ('pass', 'fail', 'uncertain')}
    summary = export_results(folder, judged, judge_meta)
    report = ['# Second-model judgement report', '',
              f"Judge: `{model}`. Source backend: `{metadata.get('backend')}`.", '',
              f"Code checks: {summary['code_passed']}/{summary['trials']}. "
              f"Judgement passed: {summary['judgement_passed']}/{summary['trials']}. "
              f"Overall passed: {summary['overall_passed']}/{summary['trials']}.", '',
              f"Judge API cost (or reserved upper estimate for unknown calls): USD {spent:.6f}.",
              'Judgements evaluate recorded outputs; combined acceptance requires code AND judgement pass, with the full trial denominator.', '',
              '## Failed Or Uncertain Criteria', '']
    findings = [x for x in review_rows if x['verdict'] != 'pass']
    for x in findings:
        report += [f"### {x['review_id']} ({x['verdict']})", '',
                   x['criterion'], '', x['comments'], '',
                   'Evidence references: ' + x['evidence_refs'], '']
    if not findings:
        report.append('No failed or uncertain criteria among completed judge responses.')
    if summary['judge_calls_error'] or summary['judge_calls_pending']:
        report += ['', 'Some calls are pending or errored; this is not a complete judgement run.']
    (folder / 'REPORT.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    return summary
