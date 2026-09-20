# Dispatch validation

Validation performed locally during package preparation. No paid agent or judge
requests were made and no key was read for this work.

- All 127 baseline manifest entries still match the frozen release.
- Original regression suite: 35 tests passed.
- Extracted v2 package offline battery: 75 trials, 75 code passes, 75 pending
  judgements. This is scripted validation, not measured live performance.
- Extracted v1 package offline battery: 75 trials, 72 code passes, 72 pending
  judgements; three failures remain visible in the denominator.
- All six distributed ZIPs extract and pass their package hash checks.
- Mocked transport test exercises preflight, release, full battery and return ZIP.
  It verifies pending judgement is not a pass and rejects an accidental full rerun
  and modified assignment. Test outputs are temporary and are not distributed as
  evidence.
- Public model catalog snapshot records selected IDs, prices and supported
  parameters. Authenticated model compatibility, live accuracy and actual spend
  remain unmeasured until members run their preflights.

Reproduce wrapper validation without a key:

```sh
python3 Part3_LI_LINGHAO/d5_live_handoff/test_dispatch.py
python3 Part3_LI_LINGHAO/scripts/verify_freeze.py
python3 -m unittest discover -s Part3_LI_LINGHAO/tests -q
```

Rebuild uses the stored catalog snapshot for stable allocation/prices:

```sh
python3 Part3_LI_LINGHAO/d5_live_handoff/build_packets.py
```

The builder expects this source directory within the repository. Members run the
self-contained `run_member.py` inside their individual ZIP instead.
