# 45-case integration and review

The reproducible merge is implemented by `scripts/merge_and_review_cases.py`.
It starts from the 15 shipped Problem A rows, appends the five new rows from each
of the six member folders, merges all supporting rows and labels, checks every
foreign-key reference and rejects duplicate IDs. Teacher rows are never edited.

Run from the repository root:

```bash
python3 Part3_LI_LINGHAO/scripts/merge_and_review_cases.py
```

The snapshot is written to `Part3_LI_LINGHAO/integration/merged_A/`. The report
records source folders, counts, duplicate-ID errors, link errors and the final
ordinary/negative split. Original label rows remain unchanged. Compact string `missing` labels have
explicit mappings in `missing_normalization.json` and structured expectations in
`case_audit.json` for the shared harness. This is a data-schema normalization, not a change to the expected
outcome. The expected distribution is 45 claims, 45 labels, 30 ordinary cases and
15 negative cases.

This stage does not claim model accuracy or prose-quality judgement. Those belong
to the subsequent scripted and live evaluation stages.
