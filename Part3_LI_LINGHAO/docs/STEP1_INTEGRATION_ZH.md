> 第 1 步历史基线：用户已反馈陈、陆、周审阅接口后认为没有问题。当前三种结果的实现与 v2 证据字段补充见 MINIMAL_FLOW.md；本文保留原始单案例范围和 17 项测试记录。

# 第 1 步：整合基线与团队接口约定

负责人：LI LINGHAO。范围：为 D4、D5(a) 准备统一接口。

## 1. 本步成果与范围

本步在 `Part3_LI_LINGHAO` 中建立可独立运行的整合基线。后续 harness 可以调用一个函数，获得结构化业务字段和运行统计，并检查真实决定日志。每次调用拥有自己的工具数据、版本、backend 游标、护栏状态和输出目录。

这是已经实现、可供团队审阅的整合方案，不代表队友已经审阅或同意。没有向队友发送消息；没有修改队友目录或老师资料中的文件。

第 1 步不等于完成 D4 harness 或 D5(a) 提交：目前只提供一个端到端 scripted 冒烟案例，没有覆盖全部 30–50 个案例，也没有计算案例通过率、评价解释文字、运行 live battery 或实现成本模型。

## 2. 整合选择与贡献归属

| 内容 | 采用的基础 | 本地整合改动 |
|---|---|---|
| ReAct 流程 | 陈的 agent，经陆的整合副本继承 | 统一带统计的 runner：解析、执行、追加真实观察、继续循环 |
| 八个读取工具 | `Part2_LU_XINZE/D2b_integrated_tools.py` | 将模块全局数据改为每次运行独立的 `ClaimTools`；采用可移植数据路径 |
| v1/v2 与业务 prompt | `Part2_LU_XINZE/D2b_integrated_agent.py` | 使用 `build_prompt(version)`；prompt 和工具一起切换版本 |
| 四项代码控制 | `Part2_ZHOU_SIHAN/guardrails.py` | 保留步数、预算、调用去重和自主权设置；修正尝试下一轮导致的多计一轮 |
| 决定写入 | 周的 `gated_action.py` 设计 | 保存结构化业务字段；绑定案例和日志；检查实际证据调用 |
| 面向评测的接口 | LI LINGHAO | 新增 `run_case`、结构化 Final 解析、结果格式、隔离输出和测试 |

整合时的源文件路径与 SHA-256 指纹保存在 `step1_sources.json`。改编后的代码运行时只依赖本地 package 和 Python 标准库，不会导入其他成员目录。默认数据来自本目录现有的、保持原样的 `materials/A2_reference_data/data_A`。

修正了一处原工具注释：非合作医院影响记录内容，不改变决定。该工具的实际行为没有改变。

## 3. 文件分工

| 文件 | 职责 |
|---|---|
| `run_case.py` | 单案例命令行入口，默认离线 |
| `integration/config.py` | BACKEND / MODEL / BASE_URL 和可移植默认设置 |
| `integration/runner.py` | 公共接口与带统计的执行循环 |
| `integration/tools.py` | 每轮独立的八个读取工具及 v1/v2 行为 |
| `integration/prompt.py` | 按版本生成团队 prompt，并加入输出约定 |
| `integration/protocol.py` | 解析字面量 Action、JSON Final，检查基本结构 |
| `integration/guardrails.py` | 每轮独立的护栏状态与读取工具包装 |
| `integration/gated_action.py` | 唯一的决定写入工具 |
| `integration/backends.py` | 固定脚本回放和唯一的 live HTTP 边界 |
| `integration/scripts.py` | 明确编写的 CLM-8925 冒烟脚本 |
| `tests/test_integration.py` | 离线接口与回归测试 |

自动产生的 output 被 Git 忽略。后续 harness 应导出选定的可复现结果表作为提交材料，不应把每个临时冒烟目录都提交。

## 4. 公共接口

在仓库根目录使用：

```python
from Part3_LI_LINGHAO.integration import run_case

result = run_case(
    "CLM-8925",
    backend="scripted",
    prompt_version="v2",
    output_dir="Part3_LI_LINGHAO/output/step1",
    operator_approved=True,
)
```

必填项为 `case_id`。四个主要参数为 `case_id`、`backend`、`prompt_version`、`output_dir`。其他参数只能按名称传入：

| 参数 | 默认值／含义 |
|---|---|
| `data_dir` | 老师的 `data_A`；可以换成包含同样 JSON 表的目录 |
| `model`、`base_url` | 配置中的模型与兼容 API 地址 |
| `autonomy` | 默认 `confirm`；另支持 `suggest`、`act` |
| `operator_approved` | 默认 `False`；由调用方明确设置，模型不能控制 |
| `step_cap` | 最多 8 个响应轮次 |
| `budget_usd` | USD 0.05 的估计成本停止阈值 |
| `price_in_per_m`、`price_out_per_m` | live 必须明确提供价格；scripted 使用示例值 0.10 / 0.40 |
| `scripted_steps` | 可选的固定响应字符串列表，用于后续脚本或测试 |

不支持的版本、未知案例 ID、缺少脚本和不合法设置会明确报错。live 必须提供价格；开始运行后若没有 key 或调用失败，则返回执行错误。导入代码或使用 scripted 时不会发送 live 请求。

## 5. 统一响应与写入格式

模型仍通过一个或多个单行 `Action: tool_name(keyword=value)` 调用工具，参数必须是 Python 字面量。使用 AST 解析替代原正则解析，支持列表、字典和转义字符串，同时不使用 `eval`。函数表达式和关键字解包会被拒绝。

`issue_decision_letter` 必须单独占一个工具调用轮次，其参数为：

```text
claim_id, decision, reason, evidence,
trigger=None, missing=None, lines=None,
approved_total=None, refused_total=None, escalate_to=None
```

`evidence` 是工具名称列表；`missing` 是含 `item`、`for_line`，以及必要时 `must_be_valid_on` 的对象；`lines` 是逐行处理对象的列表。升级人工必须提供 `trigger` 和 `escalate_to`；补件必须提供具体 `missing` 对象。

收到写入观察之后，`Final:` 必须返回一个 JSON 对象，其业务字段与写入内容相同。旧版自由文本 Final 会被明确拒绝，不会靠猜测转换。这项格式扩展对 v1、v2 一致应用，使两者的预期差异仍是 preauthorisation 接口。

继续执行下一轮时，只追加已解析的 Action 行和真实工具观察；模型自行生成的观察不能充当工具证据。多个读取调用可以处于同一响应轮次，但在程序中按顺序执行；本次整合不声称实现了并发执行或得到了新的 D2(c) 性能测量。

## 6. 返回结果格式：schema_version=1

| 类别 | 字段与含义 |
|---|---|
| 标识 | `schema_version`、`case_id`、`run_id`、`run_date`、`backend`、`model`、`prompt_version` |
| 业务结果 | `decision`、`reason`、`evidence`、`trigger`、`missing`、`lines`、`approved_total`、`refused_total`、`escalate_to` |
| 执行状态 | `status`、`stopped_by`、`error`、`execution_issues` |
| 运行统计 | `turns`、`tokens_in`、`tokens_out`、`cost_usd`、`token_source`、`cost_basis`、`prices_per_m`、`limits` |
| 门禁 | `autonomy`、`operator_approved`、`action_count`、`action_records` |
| 证据 | `trace`、`responses`、`decision_log`、`output_dir` |

`trace` 保存每次工具调用尝试的参数、观察、轮次和状态（`ok`、`blocked`、`error`）。`responses` 保存 backend 响应和逐轮 usage，供检查。`action_records` 从真实 JSONL 文件读取，不根据模型最后声称的内容重建。

顶层业务字段表示解析后的 Final。因此，仅仅 `decision` 非空不代表成功执行。后续 grader 必须同时检查执行状态与实际日志。

| 状态 | 含义 |
|---|---|
| `completed` | Final 合法，真实写入一次，业务字段一致，无工具错误或拦截 |
| `not_recorded` | Final 合法，但没有实际记录，例如未确认 |
| `record_mismatch` | Final 与实际写入字段不同 |
| `completed_with_tool_issues` | 存在一致的记录，但执行中出现工具错误或拦截 |
| `stopped` | 步数或预算阈值终止循环 |
| `error` | 解析／backend 错误、脚本耗尽或写入与其他调用混在同一轮 |

`completed` 是执行结果，不是 D4 正确性评分。错误业务推理也可能产生格式正确的记录，后续 grader 仍需与独立答案比较。

## 7. 状态隔离、门禁和统计口径

每次调用创建 `output_dir/run-<唯一后缀>/`，包含 `result.json`、`decisions.jsonl`、`transcript.txt`，不会清空旧日志。重复运行同一案例从原始 fixture 数据开始，不会继承前一次运行的决定。老师的 `decided_claims.json` 仍用于业务重复理赔检查，与本轮写入日志不是一回事。

写入门禁检查自主权设置、人工确认、预算、绑定案例 ID，以及本轮是否已经存在决定；还会检查引用的工具名称是否对应成功观察。它不证明证据语义充分，也不等于完成 hostile-text checklist。重复读取保留周的“相同调用去重”行为；重复决定即使更改理由，也会被拦截。

turns 统计 backend 实际返回的响应，包括最终回答。尝试第九次响应不会把八轮计成九轮。预算在取得 usage 之后、执行本轮工具之前检查，因此一次 API 请求本身可能使费用超限。这是停止阈值，不是保证不超支的预付限额。

scripted 每个响应使用 800 输入、60 输出的合成 token 数。`cost_usd` 按这些数和配置价格计算，仅用于测试；`api_cost_usd` 为零。live 使用 API 返回 usage 和调用方提供的价格，是估计值，不是供应商账单（`api_cost_usd` 为 null）。缓存、推理 token 定价等计费细节留待 D6 对接。

重复运行时，时间戳和唯一目录会变化。可复现性应比较决定、trace、计数和执行状态，不要求整个结果文件字节一致。

## 8. 运行与验证

需要 Python 3.10 或更高版本，只使用标准库。在仓库根目录执行：

```bash
python3 Part3_LI_LINGHAO/run_case.py --approve
python3 Part3_LI_LINGHAO/run_case.py --version v1 --approve
python3 -m unittest discover -s Part3_LI_LINGHAO/tests -v
```

冒烟运行应显示 `completed`、`escalate`、`annual_limit_exceeded`、5 turns、1 条实际记录。不加 `--approve` 时，会按设计得到 `not_recorded`、0 条记录和退出码 1。退出码 0 表示执行干净完成，不表示准确率评分通过。

已执行验证：17 个测试全部通过。覆盖确认后运行与日志回读、未确认、suggest/act、重复运行隔离、v1/v2 实例隔离、准确步数统计、预算在工具执行前停止、重复写入、Final 与日志不一致、补件／批准结构化字段传输、拒绝非字面量表达式、写入独占一轮、错误案例写入、缺失脚本／live 价格，以及模拟 live usage 计费。

没有调用真实 API。live adapter 测试使用模拟 HTTP 响应。补件／批准测试只验证数据结构往返，不验证完整业务推理。提供的端到端脚本仅覆盖 CLM-8925。这些测试不是 D3 checklist、D4 评测集或 live 模型证据。

## 9. 团队对接与审阅清单

| 成员 | 具体需要审阅／提供什么 |
|---|---|
| CHEN MINGSONG | 审阅保留的八工具接口与 ReAct 流程，核对轮次定义和批量调用假设 |
| LU XINZE | 审阅 `ClaimTools`、`build_prompt`，核对 v1/v2 行为和两个版本统一的结构化 Final 扩展 |
| ZHOU SIHAN | 审阅门禁字段、调用方确认、每轮独立日志及去重；后续把 D3/D7 测试移到同一路径 |
| LI LINGHAO | 维护接口约定、测试和后续 harness；收集案例，实现评分，避免答案泄漏给 agent |
| DAI MINFEI | 使用模型／版本／usage／成本来源字段，提供模型价格及后续计费修正 |
| WANG YI | 按本文件范围和证据撰写报告，将其描述为接口验证，不称为实测准确率 |

这些是待团队审阅的具体项目，不代表已取得团队同意。现在可以直接审阅本地可运行实现，并提出接口修改。

## 10. 后续工作与继承的限制

1. 收集并验证最终案例集，保留老师的标签和数据，扩展 generator 与答案文件。
2. 编写 D4 harness：运行次数安排、精确结果检查、判断评分和汇总。
3. 扩展脚本到每个提交案例；runner 不会静默用别的案例脚本替代。
4. 在最终整合路径完成 D3 checklist 和 D7 实验。
5. 在 live battery 和 v1/v2 对比前冻结案例、prompt、grader 和设置。
6. 增加新类型 fixture 前检查继承的工具假设：preauthorisation 按一个会员／操作代码组合保存一条记录，尚不处理同组合多条授权；v2 把所有有效期外的授权标为 `expired_before_service`，包括授权开始日晚于服务日。这些行为被保留，本步测试没有证明这些边界正确。
7. 当前结构检查只约束必要形状，不验证完整逐行金额核对或全部业务正确性。后续需由 grader 检查，并单独约定必要的工具改进。

整合执行路径不会读取任何答案文件。scripted 成功证明预先编写的步骤可以复现执行，不证明 live 模型能自行选出这些步骤。
