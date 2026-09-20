"""Create member-specific feedback, without changing experiment evidence."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
audit = json.loads((ROOT/'audit_results.json').read_text())
content = {
'CHEN_MINGSONG': (
'''# CHEN_MINGSONG — investigate the low score before a rerun

Your full submission is preserved and internally consistent: 75 trials, 3 code
passes, 5 reviewable records and 70 execution failures. A 3/75 score warrants a
focused diagnosis, but does not by itself prove a broken harness. Regrading the
saved records reproduces the score; runtime, data and assignment hashes match.

The current coordinator request is to investigate and report whether a new run is
justified. Do not start another paid full run from this feedback alone.

1. Pull the latest repository safely, preserving local work. Keep the entire
   original suite, preflight, release and return ZIP. Do not reset the full-started
   marker, replace failed records, or edit the original summary.
2. Check your local original package with `python run_member.py verify`. Record
   Python/OS versions, launch command, working directory, model ID and whether
   any prompts, scripts or transport settings were changed outside the package.
   Submit the verification output without credentials.
3. Diagnose using saved responses first; no API calls are required. Follow the
   response -> parser/tool call -> observation -> gated write -> Final chain.
   Separate genuine model protocol errors from interface/environment defects.
   The shared contract explicitly requires strict JSON in Final, separate Action
   and Final turns, a non-empty reason, and dispositions for non-escalation lines.
   Python None is allowed in literal Action arguments, not in Final JSON.
4. Inspect CLM-8842 trial 1: the decision write was recorded but the later Final
   contained invalid JSON. Also inspect one Action/Final mixing error, one
   not_recorded trial and one empty-reason error. Cite exact case/trial and turn
   IDs plus original response excerpts; redact credentials. Do not write proposed
   ideal answers or patch saved responses. The audit extract lists error counts.
5. Submit DIAGNOSTIC_RESPONSE.md using the included template. State whether the
   observed response actually violates the published contract. If you suspect a
   harness bug, provide a minimal offline reproduction from an existing response,
   the expected parser behaviour and the exact failing code location.
6. Send LI_LINGHAO the commit/PR link. The coordinator will decide the next run:
   a verified common defect requires a shared versioned fix, regression checks,
   a new diagnostic preflight/release and a separately named complete battery.
   Assess which other model jobs are affected before comparing versions.
   If no defect is found, retain 3/75 as valid measured evidence. A coordinator may
   prescribe a separate replication study, but it must report both runs and must
   not select the higher score or overwrite the original.

Do not switch to an easier model, add Gemini-only prompts, relax guards, tune to
specific case answers or retry repeatedly until a desired score is reached.
The five reviewable original trials still need the common independent judge;
3/75 is currently code acceptance, not final combined acceptance.
''',
'''# CHEN_MINGSONG：低分专项诊断反馈

现有完整 75 次运行代码仅通过 3 次，值得专项排查。但原始记录复算一致、代码/数据/
配置哈希匹配，不能仅因低分断言 harness 有问题。本次要求是先诊断并提交结论，
不是立即授权重新付费跑完整 battery。

1. 安全拉取最新仓库，保留原 suite、预检、release、ZIP，不删启动标记、不改成绩。
2. 在原运行包执行 verify，记录 Python/系统版本、启动命令、工作目录、模型及包外改动。
3. 优先分析已保存响应，不需调用 API。区分模型违规与接口缺陷：Final 必须严格 JSON；
   Action 和 Final 必须分轮；reason 不可空；非升级人工决定需逐行处置。
   Action 字面量允许 None，不代表 Final JSON 也允许。
4. 分析 CLM-8842 trial 1 的“写入成功但 Final JSON 错误”，另选 Action/Final 同轮、
   not_recorded、空 reason 各一条。引用原始 case/trial/turn 与响应片段，不编造理想答案。
5. 填写 DIAGNOSTIC_RESPONSE.md；若怀疑公共代码有错，提供现有响应的最小离线复现、
   预期行为及代码位置，提交个人分支/PR 后通知 LI_LINGHAO。
6. 确认公共缺陷后才统一修复、发布新版本、预检放行并另存完整重跑结果，同时评估其他
   模型是否受影响。若只是模型违规，原 3/75 是有效测量；若另作重复实验，需预先规定
   实验方案并同时报告两次结果，不可择高分替换。

不要自行换模型、增加 Gemini 专属提示、降低规则或反复刷分。原始 5 条可审阅记录仍由
协调人统一 judge。详细诊断步骤以英文文件为准。
'''),
'LU_XINZE': (
'''# LU_XINZE — complete the missing formal battery

The audited repository contains six revision 1.1 preflight records, no formal
return ZIP and no matching release. All six returned model responses and failed
because the model generated a prohibited Observation block. Transport is working;
0/6 is diagnostic evidence, not proof of an API outage. The recorded estimate is
USD 0.0057162; projected agent total USD 0.12504804375 is not a billing guarantee.

First confirm whether a full run already exists locally. If yes, upload that
original suite/return ZIP, release and observations; do not rerun. If no, report
your current credit and environment/price changes, obtain the matching release
from LI_LINGHAO, then run the first full 75-trial battery using your original
assigned Qwen v2 revision 1.1 package and its README commands.

Do not change prompts or guards to remove Observation failures. Retain all 75
rows, including failures and budget/backend stops. Keep the terminal open. If
interrupted, preserve partial evidence and contact the coordinator; do not reset
the start marker. Pack the complete suite with the documented pack command and
submit the return ZIP, release.json and OBSERVATIONS.md. The coordinator runs the
independent judge. No new code or runtime is supplied in this feedback package.
''',
'''# LU_XINZE：补齐正式运行

仓库只有 6 次新版预检，没有完整返回 ZIP 或匹配 release。六条均收到模型响应，因
模型自行输出 Observation 失败；这不是 API 不通，不能为提高分数自行改 prompt。
已记录估算费用 US$0.0057162，预计总额 US$0.12504804375，仅供预算参考。

先确认是否已在本地完成正式运行：有则提交原始结果，不要重复跑；没有则报告当前额度
及环境/价格变化，由 LI_LINGHAO 提供匹配 release，再按原 Qwen v2 revision 1.1 包
README 首次跑完整 75 次。保留失败和中断证据，不删启动标记。完成后提交返回 ZIP、
release.json 和 OBSERVATIONS.md，judge 由协调人完成。
'''),
'WANG_YI': (
'''# WANG_YI — complete the missing formal battery

The audited repository contains six revision 1.1 preflight records, no formal
return ZIP and no matching release. Code acceptance is 1/6 and transport_ok is
true. The other records show Action/Final mixing, missing gated recording and a
syntax error. The recorded estimate is USD 0.007353875; projected agent total
USD 0.1685860625 is not a billing guarantee. Old Part8 preflight evidence does not
substitute for the revision 1.1 formal battery.

First confirm whether a full run already exists locally. If yes, submit that
original evidence rather than rerunning. If not, report remaining credit and any
environment/price changes, obtain the matching release from LI_LINGHAO, and run
the first complete 75-trial battery with the assigned Mistral v2 revision 1.1
package. Follow its original README; do not change model, prompt or guardrails.

Keep all failures in the 75-row denominator. Preserve partial output if interrupted
and contact the coordinator instead of resetting the full-start marker. Submit
the packed return ZIP, release.json and OBSERVATIONS.md. The independent judge
will be run centrally. No new runtime is supplied here.
''',
'''# WANG_YI：补齐正式运行

仓库只有 6 次新版预检，代码通过 1/6，transport_ok=true；其他记录为 Action/Final
混合、未完成受控写入和语法错误。缺少正式返回 ZIP 与匹配 release。Part8 下旧预检
不能替代新版正式 battery。预检估算 US$0.007353875，预计总额 US$0.1685860625。

先确认是否已有本地正式结果：有则提交原始证据，不重跑；没有则报告余额及环境/价格
变化，拿到 LI_LINGHAO 的匹配 release 后，按原 Mistral v2 revision 1.1 包 README
首次完整运行 75 次。不要改模型、prompt 或保护机制。保留全部失败和中断证据，提交
返回 ZIP、release.json、OBSERVATIONS.md；judge 由协调人统一运行。
'''),
'DAI_MINFEI': (
'''# DAI_MINFEI — investigate the interrupted preflight

Only two complete result records are present: CLM-8842 failed with mixed Action
and Final; CLM-8888 ended not_recorded. A third run contains an empty decision
log without result.json or transcript. No preflight.json or full battery exists
in the audited repository. The known recorded cost is USD 0.035591; costs of any
unrecorded calls are unknown, not zero.

First check whether additional original output exists locally and upload it if
available. Otherwise, preserve the entire interrupted attempt and provide the
last terminal output, exit code if available, whether the process/terminal was
closed, Python/OS versions, exact command, time of interruption and remaining
credit. Redact keys and credentials. Do not reconstruct missing records.

Use the original Claude Haiku 4.5 v2 revision 1.1 package. Run verify and the
offline check, and report any failure. Investigate the interruption separately
from the two genuine model protocol failures. Do not modify prompts or scoring
to make those failures disappear.

After the coordinator reviews the interruption and budget, obtain approval for a
fresh six-case diagnostic attempt in a separate output folder. Keep and label
both attempts; report their costs separately. A complete preflight and matching
release are required before the first formal 75-trial run. Follow the personal
README for full/pack commands. Submit the complete return ZIP, release and
observations afterward; the independent judge is coordinated centrally.
''',
'''# DAI_MINFEI：排查预检中断

仓库只有两条完整记录：CLM-8842 为 Action/Final 同轮错误，CLM-8888 为 not_recorded；
第三个 run 仅有空决策日志，没有 result/transcript。没有 preflight.json 或正式 battery。
已知成本 US$0.035591，未记录调用费用未知，不能计为零。

先检查是否有未上传的原始结果，有则补交。否则保留整个中断目录，反馈最后终端输出、
退出码（如有）、是否关闭进程/终端、Python/系统版本、命令、中断时间及余额，去除密钥。
使用原 Claude Haiku 4.5 v2 revision 1.1 包执行 verify/offline，反馈错误。

区分运行中断原因与两条模型协议错误，不通过修改 prompt 或评分掩盖问题。协调人审阅
中断和预算后，再批准在独立输出目录做新的 6 案例诊断预检；保留两次证据，费用分开。
完整预检及匹配 release 后才能首次正式跑 75 次。后续提交返回 ZIP、release 和观察
说明，由协调人集中 judge。不可伪造缺失轨迹。
''')}
common = '''# Return instructions

Audit snapshot: {commit}; this feedback is based on repository evidence, not a
claim about files that exist only on your computer. Safely pull the latest main
before working; preserve uncommitted changes. Use your personal Git branch and PR.

Save your response as RESPONSE.md (CHEN: DIAGNOSTIC_RESPONSE.md) under
Part3_LI_LINGHAO/d5_live_submissions/{member}/r1.1/feedback/.
Use a separate labelled directory for any newly authorised experiment; never
overwrite the first attempt. DAI's existing Part4 evidence may remain in place;
include its path in your response. Do not commit keys, .env or credentials.

Response checklist:
- What is already complete locally, and where is its original evidence?
- Commands/environment and any changes from the assigned package.
- Verified findings with case/trial/turn IDs and original evidence paths.
- Infrastructure issue versus model error; what remains uncertain?
- Known costs and remaining credit; unknown charges explicitly labelled.
- Requested next action and link to the uploaded evidence/commit/PR.

These are feedback documents, not a release.json or a replacement execution pack.
No member should fill in human judgements or run a separate judge.
'''
template = '''# Diagnostic response — CHEN_MINGSONG

Date / original suite path / original commit:
Python and OS / command / working directory:
Package verification output (no keys):
Any external configuration or source changes:

| Case / trial / turn | Raw response excerpt | Published rule | Observed failure | Model error or suspected harness defect? |
|---|---|---|---|---|
| CLM-8842 / 1 / ... | | | | |
| Action + Final example | | | | |
| not_recorded example | | | | |
| empty reason example | | | | |

Offline reproduction and expected behaviour (if a defect is suspected):
Code location and scope of impact:
What remains uncertain:
Known spend / remaining credit:
Recommendation: retain original / shared fix proposal / separate replication proposal:
Evidence commit or PR:
'''
out = ROOT/'feedback_packets';out.mkdir(exist_ok=True)
hashes = {}
for member,(en,zh) in content.items():
    folder = out/('D5_FEEDBACK_'+member);folder.mkdir(exist_ok=True)
    (folder/'FEEDBACK_EN.md').write_text(en)
    (folder/'FEEDBACK_ZH.md').write_text(zh)
    (folder/'RETURN_INSTRUCTIONS.md').write_text(common.format(commit=audit['commit'],member=member))
    (folder/'AUDIT_EXTRACT.json').write_text(json.dumps({'commit':audit['commit'],'member':member,'audit':audit['members'][member]},ensure_ascii=False,indent=2)+'\n')
    if member=='CHEN_MINGSONG': (folder/'DIAGNOSTIC_RESPONSE_TEMPLATE.md').write_text(template)
    target=out/(folder.name+'.zip')
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for f in sorted(folder.iterdir()):z.write(f,folder.name+'/'+f.name)
    hashes[target.name]=hashlib.sha256(target.read_bytes()).hexdigest()
(out/'SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('Created four member-specific bilingual feedback ZIPs.')
