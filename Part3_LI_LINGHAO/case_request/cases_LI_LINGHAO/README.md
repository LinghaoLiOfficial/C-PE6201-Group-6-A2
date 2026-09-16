# LI LINGHAO case handoff

This folder contains LI LINGHAO's five original Problem A cases:

- `fixtures_LI_LINGHAO.json`: five `EXTRA_CLAIMS`; no supporting rows are needed.
- `labels_LI_LINGHAO.json`: five independently derived answer labels.
- `design_LI_LINGHAO.md`: calculations, targeted wrong behaviours and grading checks.
- `design_LI_LINGHAO_ZH.md`: Chinese translation for personal review and team handoff.

These files are not merged into the teacher fixture directory or the team answer
key. The coordinator should review them, run the validation test, then insert the
approved rows into the generator and one shared answer key.

Validation and scripted execution from the repository root:

```bash
python3 Part3_LI_LINGHAO/case_request/validate_cases.py
PYTHONPATH=Part3_LI_LINGHAO python3 Part3_LI_LINGHAO/run_li_cases.py
```

The run reports seven trials: one ordinary trial for each of the four ordinary
cases and three independent trials for the negative escalation case. The code
checker confirms decisions, line dispositions, totals, evidence calls and the
single escalation trigger. Prose-quality judgement remains a human review task.
