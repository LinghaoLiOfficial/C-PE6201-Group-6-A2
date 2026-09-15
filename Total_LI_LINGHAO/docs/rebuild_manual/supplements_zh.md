# 操作补充：从空目录到每个产物

## 两种使用方式，不混淆实验来源

学习重建：先只复制教师原始T类文件；按步骤1–40逐块新增代码。代码附录C提供最终每个Python文件的完整内容，显示行号不是代码的一部分。先创建文件顶部import和公共定义，再按步骤插入函数；类方法缩进四空格。一个阶段尚未写齐依赖时只做py_compile，步骤20才做端到端。附录D给出全部EXTRA赋值和标签，不需要猜测省略号。老师原生成器其余部分保留，不能用全新生成器冒充未改原件。

精确复现：把当前提交包解压到新目录；按README跑离线链路。这可以验证历史实验的实现，但不等于新团队从零开发或每人重新完成live。不要把历史results复制到空团队后宣称刚运行过。源码附录对应47e1212后的同一评测实现；本手册只改文档，不改变冻结fingerprint。

## 环境和建文件顺序

运行时需要Python3.10及以上，macOS/Linux（ledger使用fcntl）。先创建claim_agent、tests、scripts、docs、results目录。原teacher reference data复制成A2_reference_data，保留checker、generator、原15标签和data_A；无需改ProblemB文件。按附录C建立__init__.py、tools.py、agent.py、backends.py、harness.py和run_eval.py；其余scripts/tests在对应步骤新增。离线运行不安装模型SDK、不需要API key。

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python3 -m py_compile claim_agent/*.py run_eval.py
python3 A2_reference_data/make_fixtures_A.py
python3 A2_reference_data/check_my_data.py
python3 run_eval.py
python3 scripts/reproduce.py
```

报告构建额外安装requirements-authoring.txt中的reportlab和matplotlib。旧中文手册builder需要macOS Songti字体；其它操作系统换成合法安装的中文TrueType字体路径。这是文档构建环境差异，不是保险规则差异。

## 新建价格和账户快照：不能依赖历史结果文件

步骤26之前，results/model_catalog.json与account_budget.json尚不存在。完成backends.py后，从项目根目录执行以下脚本。它只查询目录/账户元数据，不发送模型推理；不打印key。credential()读取仓库外私密配置。保存的是runner需要的pricing结构和允许公开的数值，绝不能保存Authorization header或原key响应的其它标识字段。先通过provider界面设置不超过本次授权的硬limit；若无余额，停止live并记录未完成。

```python
import json, urllib.request
from pathlib import Path
from claim_agent.backends import BASE_URL, credential
from scripts.run_live import MODELS
out = Path('results')
out.mkdir(exist_ok=True)
def get_json(endpoint):
    request = urllib.request.Request(
        BASE_URL + endpoint,
        headers={'Authorization': 'Bearer ' + credential()})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)['data']
models = {row['id']: row for row in get_json('/models')}
missing = set(MODELS) - set(models)
if missing:
    raise RuntimeError('Revise the model plan before freezing: ' + str(missing))
(out / 'model_catalog.json').write_text(json.dumps(
    [{'id': m, 'pricing': models[m]['pricing']} for m in MODELS], indent=2))
account = get_json('/key')
allowed = ['limit', 'limit_remaining', 'usage', 'is_free_tier']
clean = {k: account.get(k) for k in allowed}
if clean['limit_remaining'] is None or clean['limit_remaining'] <= 0:
    raise RuntimeError('A positive bounded balance is required')
(out / 'account_budget.json').write_text(json.dumps(clean, indent=2))
```

以上是本手册新增的重建操作片段，不是声称旧仓库已经存在capture_catalog.py。若保存成scripts/capture_catalog.py，它属于新产出N；记录抓取时间。对本来已有历史account_budget的目录，不覆盖起始基线；新实验必须使用新工作副本。

## 如果要按课程要求让每位成员独立运行

当前run_live.py只提供--pilot和--workers；不存在--model参数。不可照写一个不存在的命令。以下是对新团队工作副本的明确扩展方案，未在本次正式384结果中执行。

1. 在main的argparse段新增--model（choices=MODELS）、--variant（choices=['v1','v2']，default='v2'）、--owner（required）、--output-dir（required）。
2. 将configs赋值移到manifest构造之前并替换为configs=[(args.model,args.variant)]；要求args.model必选。outdir改ROOT/args.output_dir；manifest保留完整5个MODELS目录、prices、fingerprint、temperature，并新增owner、executed_configuration、shared_key=False与本组配置数1。任务循环只用这一条configs。
3. 每位成员在自己的相同commit工作副本、同一40案上运行，用自己的仓库外key与最新account_budget；不修改backend RULES或variant含义。六组分配5个v2加Gemini v1。
4. 各人提交该组64条原始json、manifest、model_catalog和非秘密budget/reconciliation；原owner名是执行事实，不由整合者猜填。收集后检验六组hash一致、temperature相同、pricing时间可比、每组64且无重复key。
5. 整合到新的results/live目录时保留六个owner manifest在单独目录；生成一个汇总manifest包含5个MODELS、六组清单和shared_key=False。保持原trial命名规则以供build_analysis/judge读取。各key的对账分别保留，不用集中reconcile_spend伪装六key总账。
6. 这是实验运行器扩展；在正式运行前进行免费mock/manifest校验。若模型目录变化或prompt变更，整组重新冻结；不能将旧共享key384试验改名成个人试验。

这一方案的功能描述不代表已实现的新CLI；如果只需要精确重建当前交付，保持附录C的runner原样，明确共享方式偏离个人执行要求即可。

## 直接复用Class5 notebook的补齐方法

教师T1 p.14要求“reuse that notebook rather than starting again”。当前仓库已复用公式到build_analysis.py，但没有analysis/Cost_to_Serve_A2.ipynb实物。因此从零完成课程时应执行下面步骤，而不是把公式引用等同文件复用。

1. 复制T5原件为analysis/Cost_to_Serve_A2.ipynb；原件不动。保留Sections1–8教学内容，并在Section7后新增markdown cell，标题“A2 Problem A: measured fixture battery”。
2. 写markdown解释volume=8000、failure=38/60*12=7.60、fixed=80是运营假设，模型数据来自当前results/cost_model.json；不把课堂support-triage或invoice示例数字当本作业结果。
3. 新增以下code cell；在新项目根目录启动Jupyter或按路径设置project_root；输出会包含所有模型的实际三层成本。给它运行结果，不只空白代码。

```python
import json
from pathlib import Path
project_root = Path.cwd()
if not (project_root / 'results/cost_model.json').exists():
    project_root = project_root.parent
model = json.loads((project_root / 'results/cost_model.json').read_text())
for row in model['models']:
    variable = row['variable_usd']
    fallback = (1 - row['pass_rate']) * (38 / 60 * 12)
    monthly = 8000 * (variable + fallback) + 80
    assert abs(monthly - row['monthly_usd']) < 1e-6
    print(row['model'], row['variant'], variable, fallback, monthly)
print('Break-even:', model['cheap_break_even_success'])
```

4. 新增分析markdown cell，解释最优模型、cheap break-even、±10pp敏感性和固定成本假设；附record来源/hash。保存notebook与执行输出，在package_submission.py的DIRECTORIES中加入analysis，否则该新增文件不会自动入包。本次手册只描述这一补齐操作，没有悄悄改写已冻结实验。

## 正式文档分别写什么

PREBUILD：五条承诺和早期架构判断；DESIGN：工具三问、四动作、依赖、gate与未建架构；TOOL_CONTRACTS：六工具的六字段；DATA_DESIGN：每例目的、标签依据、来源；EXPERIMENT_PROTOCOL：固定配置、trial和judge计划；GUARDRAIL_CHECKLIST：每项错误行为及实测；FAILURE_EXPERIMENTS：两消融与恢复；RESULTS：生成数表和口径；REPORT：六节论证≤2000词；IMPROVEMENTS中英：来源→缺陷→修改→验证；CONTRIBUTIONS：真实归属；SELF_APPRAISAL：真人集体确认；SUBMISSION_STATUS：可核实状态；DEMO：五分钟六人演示操作。

手册40步的“应写分析”给出每次新增文段；附录E给当前完整REPORT，附录F给关键配套文档当前内容。读者按同一结构写自己的实测文段，不需要自行猜报告提纲。

## 停止条件与常见排错

若ModuleNotFoundError，先确认在项目根目录、__init__.py已建立；不要用个人绝对路径修补。若checker报shipped改变，恢复T8原件，仅把EXTRA赋值迁回。若missing label，补独立key而非跳过。若64trial少了某案，检查negative字段和manifest，不降低分母。若默认core gate拒绝，这是预期；不要改成默认True来过测试。若stepcap截断，先查是否重复/非法依赖，不能只无限加cap。若source hash不同，归档旧实验并重新冻结，不能只改manifest。若judge未完成，assessed尚未完整；若余额不足，不造数字。若本地测试全过但没有视频/自评/公开仓库/回执，仍未完成课程提交。

## 报告真正的编辑入口

当前scripts/build_report.py把正文存在main的sections列表内，并同时生成docs/REPORT.md与PDF。要改报告某段，请改对应sections字符串或f-string；只编辑REPORT.md会在重建时丢失。步骤33–37按这个实际方向操作。中文手册源文件与report builder是两条独立生成链。

## 成本脚本还需要旧工具prefix输入

build_analysis.py会读取docs/LEGACY_TOOL_PREFIX.txt。从零重建时先建立这个N类证据文件：它是陈明松原agent实际插入prompt的TOOL_SPEC摘录，不能取整份带注释的tools.py计算。内容如下；保存时按当前原文件保持末尾没有额外空行，字符/4估算才能精确复现170。不能将它登记为教师原件。

```text
get_claim(claim_id: str) -> claim header: member_id, hospital_id, date_of_service, narrative, documents, lines
lookup_member(member_id: str) -> member_id, policy_id
lookup_policy(policy_id: str) -> status, start_date, end_date, annual_limit, used_to_date, exclusions
get_hospital_status(hospital_id: str) -> hospital_id, panel (true=in-network)
check_procedure(code: str) -> code, description, requires_preauth
get_preauthorisation(member_id: str, procedure_code: str) -> preauth_id, valid_from, valid_to
check_documents(procedure_code: str) -> required_documents (list)
check_duplicate(claim_id: str) -> duplicate of an earlier decided claim, or "no duplicate found"
```

此外建立requirements-authoring.txt：reportlab>=4.0与matplotlib>=3.8各一行。建立.gitignore：__pycache__/、*.pyc、.env*、.venv/、tmp/、*.zip各一行。这些是新增配置，不能放入key。正式新团队还应把analysis notebook纳入打包目录，见前节。

## 本手册已验证的重建范围

本次在全新临时目录中复制留存的教师reference-data基线，只替换EXTRA赋值，再加入附录对应的集成代码和独立标签；未复制任何历史results。依次运行generator、teacher checker和scripts/reproduce.py全部成功，重新得到64/64、分组input估算395961；33项tests、两版guardrail和D7随reproduce一起运行成功。证据在results/rebuild_manual_reproduction.json。没有为写手册重新运行付费模型，也没有代替真人录像、自评或上传。
