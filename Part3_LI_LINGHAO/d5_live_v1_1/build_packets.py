"""Build member packs from one allocation and exact frozen source bytes."""
import csv
import hashlib
import json
import shutil
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parent
PART=ROOT.parent

def save(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def hashfile(p): return hashlib.sha256(p.read_bytes()).hexdigest()

allocation=[
 ('LI_LINGHAO','deepseek/deepseek-v3.2','DeepSeek','cheap','v2'),
 ('ZHOU_SIHAN','deepseek/deepseek-v3.2','DeepSeek','cheap','v1'),
 ('CHEN_MINGSONG','google/gemini-2.5-flash-lite','Gemini','cheap','v2'),
 ('LU_XINZE','qwen/qwen3-235b-a22b-2507','Qwen','cheap','v2'),
 ('WANG_YI','mistralai/mistral-small-3.2-24b-instruct','Mistral','cheap','v2'),
 ('DAI_MINFEI','anthropic/claude-haiku-4.5','Claude','mid','v2'),
]
snapshot_path = ROOT/'model_catalog_snapshot.json'
if snapshot_path.exists():
 snapshot=json.loads(snapshot_path.read_text())
 models={x['id']:x for x in snapshot['models']}
 checked=snapshot['checked_at_utc']
else:
 with urllib.request.urlopen('https://openrouter.ai/api/v1/models',timeout=30) as r: catalog=json.load(r)['data']
 models={x['id']:x for x in catalog}
 checked=datetime.now(timezone.utc).isoformat()
 snapshot={'checked_at_utc':checked,'source':'https://openrouter.ai/api/v1/models','models':[models[i] for i in sorted({a[1] for a in allocation}|{'openai/gpt-4.1-mini'})]}
 save(snapshot_path,snapshot)
assignments=[]
for name,model,family,tier,version in allocation:
 m=models[model]
 assert {'temperature','stop','max_tokens'} <= set(m['supported_parameters'])
 a=dict(member=name,model=model,family=family,tier=tier,version=version,
        price_in=round(float(m['pricing']['prompt'])*1e6,8),price_out=round(float(m['pricing']['completion'])*1e6,8),
        price_checked_at_utc=checked,price_source=snapshot['source'],member_budget_usd=3.0,
        baseline_commit='9867baa7bc200cc3de269fac460c72450daa7be4',frozen_tag='part3-d4-d5a-v1.0.0',
        cases=45,trials=75,ordinary_trials=30,negative_trials=45,
        judge_model='openai/gpt-4.1-mini',judge_owner='LI_LINGHAO',
        contract_revision='d5-live-1.1',
        role='D2(b) live v1 paired with LI_LINGHAO live v2' if version=='v1' else 'D5(b) live v2')
 assignments.append(a)
save(ROOT/'assignments.json',assignments)
with (ROOT/'MODEL_ASSIGNMENT.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(assignments[0]));w.writeheader();w.writerows(assignments)
runbook='''# Personal live battery - {member}

Package revision: **{contract_revision}**. Extract to a NEW folder. Never reuse v1.0 preflight/release/output.

Assignment: **{model}, {version}**, family {family}, tier {tier}. {role}.
Coordinator: LI_LINGHAO. Run 45 cases / 75 trials. The v1 job is the explicit paired-comparison exception to the v2 model battery; it is not a sixth v2 model.

## Setup (Windows / macOS / Linux)

Unzip this package. Install/use Python 3.10+; no pip dependencies needed. Open a terminal **inside this extracted folder** (the directory containing run_member.py). On Windows, use `python` if `python3` is unavailable. You do not need to copy files into the main repository.

```sh
python3 run_member.py verify
python3 run_member.py offline
```

The offline command needs no key. v2 should have 75 code passes. The v1 diagnostic may have 72/75 due to the documented CLM-8888 incompatibility; this is a result, not permission to alter v1. Output judgement is pending, not passed.

## Small live preflight - 6 separate diagnostic trials

Before starting, inspect assignment.json and confirm your remaining personal OpenRouter credit. The file contains snapshot prices in USD per million tokens. If today's catalog price differs, contact LI_LINGHAO to reissue the pack; do not edit frozen files or silently change model.

```sh
python3 run_member.py preflight
```

The script prompts for your key invisibly if OPENROUTER_API_KEY is absent. It does not save the key. Use your personal key; do not send it to anyone. Preflight runs CLM-8842, CLM-8888, CLM-8910, CLM-8925, CLM-8952, CLM-16404 (mixed lines, missing authorisation, lapsed policy, annual limit, spoofed narrative, repeated lines). Submit the complete preflight folder through your Git branch and Draft PR, including failed records. These 6 trials are additional diagnostics, never part of the final denominator.

**Stop here until LI_LINGHAO returns release.json.** A wrong answer is evidence, not automatically an infrastructure defect. The coordinator reviews API/usage/parse/gate/cap behavior and budget. The estimated spend is extrapolated with a 1.5x margin, not a guarantee. Per-case budget checks happen after a call and can overshoot; unknown provider charges and retries must be checked in your account. Never rerun to select a better score.

## Full battery - only after coordinator release

Put release.json next to the returned preflight.json. Replace `PREFLIGHT_FOLDER` with the actual directory printed by preflight; quote paths containing spaces.

```sh
python3 run_member.py full --preflight "PREFLIGHT_FOLDER/preflight.json" --release "PREFLIGHT_FOLDER/release.json"
```

Use your assigned version automatically; do not type/change model IDs or prices. Keep terminal open until finished. Errors and budget stops remain in all 75 rows. A low score is valid evidence. If interrupted, return partial output and report it; the tool prevents accidental full reruns. No resume is implemented.

## Return evidence

Use the suite path printed at completion:

```sh
python3 run_member.py pack --suite "SUITE_FOLDER"
```

Submit the printed D5_RETURN_{member}.zip through the same Git PR. It contains every original trial and run directory (transcripts and local decision logs), results.json/csv, summary.json, metadata.json, grading/review contracts, assignment and dispatch receipt. Do not copy only summary.csv or delete failures. Supplement with your observations in OBSERVATIONS.md before packing.

Family, tier and prices are in assignment.json; detailed tool order/caps/prices/usage are in each record in results.json. The frozen results.csv intentionally has fewer columns. There is no separate logs/ directory: logs are in run-* subdirectories. Do not claim columns/files that are absent.

## Judgement and comparison

Leave human_review.csv blank. LI_LINGHAO will run **openai/gpt-4.1-mini** as the common second-model judge of the new live outputs (different from all five agent models). Do not reuse historical Haiku scripted judgements or call a judge yourself. Judge spending is separate from agent spending. Code-only pass rate is provisional; final overall pass requires code AND judge pass. Pending/error judgements never count as passes and stay in the denominator.

After receiving the consolidated table, discuss one observed divergence with another v2 model, especially a negative case; quote case/trial IDs and actual logs. For ZHOU_SIHAN, discuss the same-model v1/v2 difference with LI_LINGHAO instead. Do not invent a comparison before other results arrive.

## Fixed experimental controls

New common schema/rubric revision d5-live-1.1; v1/v2 still mean descriptor versions. Same fixture bytes, original grading labels, caps (8 turns; USD 0.05 per trial), local confirmation policy and transport settings (temperature 0, max_tokens 2000). Only the assigned model changes between v2 jobs. v1 versus v2 uses the same DeepSeek model and prices. The answer key is used after execution, never supplied to the agent. Existing teacher cases remain included. No added free-model routes, fallback models, modified cases or ad-hoc per-model prompts.

The team's spend target is <= USD 3 per member for agent work; confirm remaining course credit first. Full-run spending stop uses recorded usage and cannot be a provider hard spending guarantee. The common judge has its own separate budget.
'''
runbook += """

## Git submission (required handoff)

Use the shared repository https://github.com/LinghaoLiOfficial/C-PE6201-Group-6-A2.
Create a personal branch from up-to-date main: `d5/{member}-r1.1`.
Only copy results into `Part3_LI_LINGHAO/d5_live_submissions/{member}/r1.1/`.
First push `preflight/`, `assignment.json`, and `package_manifest.json`, open a Draft
PR targeting main and send its link to LI_LINGHAO. After receiving release.json,
run full and push release.json, D5_RETURN_{member}.zip and OBSERVATIONS.md on the
same branch. Never push directly to main or modify another member's directory.
Never commit keys, .env files, package/output caches or credentials in screenshots.
Keep previous version evidence separate; do not delete or overwrite it.

Example after cloning/updating the shared repo and copying your files:

```sh
git switch -c d5/{member}-r1.1
git add Part3_LI_LINGHAO/d5_live_submissions/{member}/r1.1
git commit -m "Add {member} revision 1.1 preflight evidence"
git push -u origin d5/{member}-r1.1
```

Before the full run, the coordinator checks transport, public schema, real writes,
code diagnostics, spend and remaining credit. A valid model error is evidence, but
a shared contract/transport defect blocks release. Do not self-release or rerun to
select better results. Both v1 and v2 jobs must use this same package revision.
"""
zh='''# 中文快速步骤 - {member}

你的任务：{role}；模型 `{model}`；版本 `{version}`。

1. 解压自己的 ZIP，在含 run_member.py 的文件夹打开终端。Python 3.10+，无需安装第三方库。
2. 运行 `python3 run_member.py verify` 和 `python3 run_member.py offline`。Windows 可用 python 替代 python3。
3. 确认个人额度和 assignment.json 的模型价格。运行 `python3 run_member.py preflight`，按提示输入自己的 key（不显示、不保存）。不要把 key 发给任何人。
4. 将终端打印的整个 preflight 文件夹提交到个人 Git 分支并创建 Draft PR。六个预检案例不计入正式 75 次。
5. 等 LI_LINGHAO 发回 release.json，再按英文 README 的 full 命令运行，两个路径指向你的预检文件和放行文件。
6. 完成后编辑 suite 文件夹内 OBSERVATIONS.md（可自行新建），写真实观察、错误和额度差异，再按 pack 命令打包回传。
7. 不修改案例、模型、prompt、上限；不因答错重跑刷分；中断保留全部部分结果并联系负责人。
8. 你不需人工填写 judgement，也不需调用 judge：由 LI_LINGHAO 集中使用另一个 LLM 评分。原始输出 judgement pending 是正常状态。

详细命令与费用局限见 README_EN.md。每个正式任务 75 次：普通 30，负面 45。v1 是同模型对照，不计入五模型 v2 排名。
'''
packdir=ROOT/'packets';packdir.mkdir(exist_ok=True)
staging=ROOT/'staging';staging.mkdir(exist_ok=True)
frozen=json.loads((PART/'release_manifest.json').read_text())
frozenmap={x['path']:x['sha256'] for x in frozen['files']}
for a in assignments:
 folder=staging/('D5_'+a['member']);folder.mkdir(exist_ok=True)
 runtime=folder/'runtime'
 for src in sorted((ROOT/'runtime/integration').rglob('*')):
  if not src.is_file() or '__pycache__' in src.parts: continue
  rel=src.relative_to(ROOT/'runtime')
  if 'merged_A' in rel.parts or src.name == 'scripted_library.json':
   assert str(rel) in frozenmap and hashfile(src)==frozenmap[str(rel)], str(rel)
  dst=runtime/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 shutil.copyfile(ROOT/'run_member.py',folder/'run_member.py')
 save(folder/'assignment.json',a)
 (folder/'README_EN.md').write_text(runbook.format(**a),encoding='utf-8')
 (folder/'QUICKSTART_ZH.md').write_text(zh.format(**a),encoding='utf-8')
 (folder/'OBSERVATIONS_TEMPLATE.md').write_text('# Observations\n\nRun date:\nActual model ID:\nProvider balance before/after (no key):\nInfrastructure errors:\nCase/trial IDs worth comparing:\nObserved reasoning/tool/gate issue:\nAfter consolidated results: divergence and evidence:\n',encoding='utf-8')
 files=[f for f in folder.rglob('*') if f.is_file() and 'output' not in f.relative_to(folder).parts and '__pycache__' not in f.parts and f.name!='package_manifest.json']
 save(folder/'package_manifest.json',{str(f.relative_to(folder)):hashfile(f) for f in sorted(files)})
 files.append(folder/'package_manifest.json')
 with ZipFile(packdir/(folder.name+'.zip'),'w',ZIP_DEFLATED) as z:
  for f in files:z.write(f,Path(folder.name)/f.relative_to(folder))
print('Created six assigned packets:',packdir)
release_files = [f for f in ROOT.rglob('*') if f.is_file()
                 and not any(x in f.relative_to(ROOT).parts for x in ['staging', 'output', '__pycache__'])
                 and f.name != 'release_manifest.json']
save(ROOT/'release_manifest.json', {str(f.relative_to(ROOT)): hashfile(f) for f in sorted(release_files)})
with ZipFile(PART/'D5_LIVE_HANDOFF_v1.1.zip','w',ZIP_DEFLATED) as z:
 for f in sorted(ROOT.iterdir()):
  if f.is_file() and f.suffix in {'.md','.json','.csv','.py'}:
   z.write(f,Path('D5_LIVE_HANDOFF_v1.1')/f.name)
 for f in sorted(packdir.glob('*.zip')):
  z.write(f,Path('D5_LIVE_HANDOFF_v1.1/packets')/f.name)
 for directory in ['runtime', 'tests', 'validation']:
  for f in sorted((ROOT/directory).rglob('*')):
   if f.is_file() and '__pycache__' not in f.parts and f.suffix != '.pyc':
    z.write(f,Path('D5_LIVE_HANDOFF_v1.1')/f.relative_to(ROOT))
