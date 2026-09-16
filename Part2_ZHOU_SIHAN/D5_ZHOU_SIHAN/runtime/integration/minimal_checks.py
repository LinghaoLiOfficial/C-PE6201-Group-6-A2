"""Independent code checks for three shipped examples, not a full D4 grader.
The answer key is available here only, never to the execution backend.
Prose quality remains an explicit judgement task.
"""
import json
from . import config


def load_key(data_root=None):
    root = data_root or config.DATA_DIR.parent
    rows = json.loads((root / 'expected_outcomes_A.json').read_text(encoding='utf-8'))
    return {row['case_id']: row for row in rows}


def check_minimal(result, expected):
    failures = []
    def check(ok, message):
        if not ok:
            failures.append(message)
    check(result['status'] == 'completed', f"execution status: {result['status']}")
    check(result['decision'] == expected['expected_decision'], 'wrong decision')
    check(result['case_id'] == expected['case_id'], 'wrong case_id')
    check(result['action_count'] == 1 and len(result['action_records']) == 1, 'expected one actual write')
    for record in result['action_records']:
        for field in ('decision', 'trigger', 'missing', 'lines', 'approved_total', 'refused_total', 'reason', 'evidence'):
            check(record.get(field) == result.get(field), 'log mismatch: ' + field)
    if expected.get('trigger'):
        check(result['trigger'] == expected['trigger'], 'wrong escalation trigger')
    cid = expected['case_id']
    successful = [row for row in result['trace'] if row['status'] == 'ok']
    names = {row['tool'] for row in successful}
    check({'get_claim', 'lookup_member', 'lookup_policy', 'check_duplicate', 'issue_decision_letter'} <= names,
          'required evidence calls missing')
    if cid == 'CLM-8842':
        # Independent field-level reading of the shipped label and Appendix A.
        check(result['approved_total'] == 2180, 'approved_total must be 2180')
        check(result['refused_total'] == 300, 'refused_total must be 300')
        lines = result.get('lines') or []
        check(len(lines) == 3, 'all three lines must be recorded')
        got = {row.get('code'): row for row in lines}
        for code, amount, status in [('47120', 1400, 'covered'), ('62480', 780, 'covered'), ('31255', 300, 'not_covered')]:
            check(got.get(code, {}).get('amount') == amount and got.get(code, {}).get('status') == status,
                  'wrong line disposition: ' + code)
        check(got.get('62480', {}).get('preauth') == 'PA-5521', 'missing valid preauth reference')
        check(got.get('31255', {}).get('exclusion') == 'EX-14 cosmetic dermatology', 'missing exclusion rule')
        for tool, arg in [('check_procedure', 'code'), ('check_documents', 'procedure_code')]:
            check({row['args'].get(arg) for row in successful if row['tool'] == tool} == {'47120','62480','31255'},
                  'incomplete per-line evidence: ' + tool)
        check('get_hospital_status' in names and 'get_preauthorisation' in names, 'missing hospital/preauth evidence')
    elif cid == 'CLM-8894':
        # Human-authored normalization of the shipped free-text missing label.
        # Do not infer the normalized answer from the agent's output.
        check(result['missing'] == {'item':'pre-authorisation reference', 'for_line':'29881',
                                   'must_be_valid_on':'2026-09-09'}, 'wrong named missing requirement')
        check({'get_preauthorisation','check_procedure','check_documents','get_hospital_status'} <= names,
              'missing request evidence')
    elif cid != 'CLM-8925':
        raise ValueError('minimal checker only covers the three published example cases')
    return {'code_passed': not failures, 'failures': failures,
            'check_type': 'code', 'judgement_status': 'pending',
            'judgement_requirements': expected.get('must_record', [])}
