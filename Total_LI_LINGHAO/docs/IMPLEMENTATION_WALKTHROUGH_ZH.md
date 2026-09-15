# 从作业要求到代码、实验与报告
## PE6201 A2 · Group-6 · Problem A 完整中文实施说明

这不是另一份摘要，而是一份可以沿着仓库逐步学习的实施手册：看到一条要求后，怎样判断它要求什么证据，怎样找到代码入口，怎样修改与验证，最后怎样写成报告中的论证。

适用版本：最终实现分支 codex/problem-a-integration；基础交付提交 475b193。文中代码定位以本次生成时的文件和函数为准，后续行号可能变化，函数名与文件名是主要检索依据。正式实验源代码与数据指纹位于 results/live/manifest.json。

阅读对象：需要理解全组代码、参加演示或解释设计取舍的六位成员。无需先掌握框架；先理解“提出动作、读取事实、校验、落盘、评分”这条链。

核心阅读法：每章按“要求 → 原有不足 → 修改位置与步骤 → 测试证据 → 报告段落”展开。标为“当前实现”的内容已经完成；“示范段落”是可参考的英文表达，使用时仍须核对最终表格；“局限”说明不能从现有证据推断什么。

正式英文报告仍是 output/pdf/PE6201_A2_Group-6_Report.pdf，正文 1,552 词。本中文手册是学习与交接附件，不替代正式报告，不计入该报告的正文，也不声称真人演示、自评签署或课程上传已经完成。

本手册不包含密钥。任何运行示例都只引用配置位置，不要求在聊天、截图或提交文件中展示凭据。

---PAGE---
# 01｜先把评分要求变成可验收产物

## 为什么先做这一步

“把 agent 做出来”不是完整目标。题目把分数分配给概念理解、技术执行、论证及表达。如果只改 agent.py，D0 的论证、D4 的答案键、D6 的成本和 D7 的因果证据仍然缺失。第一步应逐项写出“教师检查什么、我们交什么、怎样重现”。

## 要求与实施对应

D0：说明为什么采用 agent、如何获得客观反馈、什么算成功。产物是 docs/PREBUILD.md、保留的 D0 原稿和报告第 1 节；先写成功标准，再写集成实现。

D1：单个手写 ReAct 循环。入口是 claim_agent/agent.py 的 run_case；真实模型只能通过工具取证，不能读取答案键，不能由框架替我们运行循环。

D2：选工具、写六字段契约、防呆、测 v1/v2、测串行与多工具同轮。产物是 tools.py、TOOL_CONTRACTS.md、DESIGN.md 和对照结果。

D3：代码层上限、去重和确认门，加独立 guardrail checklist。产物是运行时控制、tests/test_guardrails.py 和可重现结果，不能只在 prompt 写“请小心”。

D4/D5：独立标签、隔离、多 trial、代码和判断评分、离线和真实模型。产物是 40 案、64 trials/配置、六组最终 live 结果和独立 judge 记录。

D6/D7：三层成本、敏感性、盈亏平衡，以及从正常系统删除组件得到的两项失败。产物是成本计算脚本、原始轨迹与 before/after 表。

## 怎样写进报告

不要写“我们实现了很多功能”。应写“我们用哪项证据支持哪项主张”。例如：The harness evaluates outcomes and gate behaviour across independently labelled cases. 这句话需要答案键、grader、逐 trial 结果同时存在，缺一项就不能只靠文字成立。

---PAGE---
# 02｜先审查成员成果，再做集成决策

## 当前原始来源

陈明松提供 drawer 工具、循环、工具评分和单例并行实验；陆鑫泽提供工具契约、保单/授权接口和 smoke tests；周思涵提供防护状态、gate、checklist 与失败演示；王毅提供 D0 和案例草稿。李凌昊组织集成；未发现戴敏菲目录中足以证明已完成成本实现的内容，因此不能替他补写历史贡献。

## 四种处理方式

第一，直接保留正确的领域判断，例如部分拒付仍为 ACT。第二，适配有价值但协议不一致的代码，例如字符串工具结果改成结构化 JSON。第三，修复已知缺陷，例如授权索引覆盖多候选、默认批准和共享 ledger。第四，补齐缺失交付，例如强评分器、完整 live battery 和成本敏感性。

原目录不覆盖。最终集成代码放在 Total_LI_LINGHAO；源文件差异与测试说明写入 IMPROVEMENTS.md。这样原始贡献、集成修复和最终实验能分别追溯，不把 AI 重构归成成员当时已经完成。

## 一项改进怎样记录

推荐固定七项：来源文件/函数；原行为；为何不满足要求；修复步骤；验证案例或测试；实测结果；仍有的限制。把“审查发现”和“已复现”分开。看见代码可能漏检，不等于已经运行并观察到漏检。

例如 I03：原授权表按 member/code 建单值索引，可能覆盖候选；当前 _preauth 保留候选列表和日期状态；验证 CLM-8894、CLM-9310、CLM-9311；局限是没有连接真实授权服务。这个描述比“优化了授权逻辑”更可检查。

## 报告与附件的分工

正式报告只写影响结论最大的变化；完整修复清单放在中英文 IMPROVEMENTS。贡献记录应说明“源自谁的设计、由集成补了什么”，不能凭目录名称推断某人已经完成个人 live 操作或录像。

---PAGE---
# 03｜D0：从“为什么要 agent”写出诚实论证

## 题目要求

说明七级架构阶梯、workflow test、客观 ground truth、第一次写入，以及五条预先成功标准。不是证明 LLM 比一切规则程序都强，而是说明题目要求的架构做了什么、付出什么。

## 原稿哪里需要改

原 D0 把固定 workflow 描述得过弱，例如暗示工作流不能有条件分支或变化长度。实际上普通代码可以循环处理任意数量的 line，也可以对失效保单早退。把“不采用”写成“不可能”会损害概念理解分。

## 当前修改与证据

docs/PREBUILD.md 先承认固定规则工作流可行，再把实验定位为：由模型依据观察选择下一步工具；因此会产生轨迹方差、重复上下文和攻击面，需要代码控制。原 D0 提交 a947eeb 早于原 agent 提交 46eaf27；集成标准也先于集成 engine 提交，保留真实历史，不补造时间。

五条标准应能转成验收：结论有真实证据；缺失项/触发原因准确；至多一次受控写入；无法完成时明确停止；统计 token、轮次和 fallback。每条分别对应 grader、gate 和 instrumentation。

## 报告段落示范

A deterministic branching workflow could implement these finite rules. The assignment selects a single ReAct agent, whose value here is adaptive evidence gathering. We therefore evaluate the additional variance, repeated context and governance cost rather than claiming workflows are impossible.

这段依次完成三件事：承认备选架构能力；说明当前选择来源；提出后面实验要回答的问题。接着补充保单、文档和授权记录能在本地查询中立即纠正模型，最后点明 issue_decision_letter 是治理边界。

## 不能这样写

“因为 line 数量变化，所以必然只能使用 agent”不成立。“离线全部正确，因此适合生产”也不成立。D0 的结论必须与后面的真实模型差异、失败成本和局限保持一致。

---PAGE---
# 04｜D1：把一轮运行拆成可审计步骤

## 当前代码路径

run_eval.py 调用 claim_agent.agent.run_case。每次运行新建 ToolSession；backend.next 收到案号和已有观察，返回 calls；主循环验证调用形状、预算和依赖；工具读取 JSON；结果附上 observation ID；下一轮继续。成功的写入会设置 session.record，循环随后结束。

## 为什么分成这些模块

agent.py 负责“能否执行这一轮”，tools.py 负责“事实和写入是否合法”，backends.py 负责“如何和模型服务通信”，harness.py 负责“结果与独立标签是否一致”。如果把答案键和工具混在一起，就容易让系统先知道答案，再伪造查询过程。

## 具体修改步骤

1. 将各成员不一致的 Action/字符串输出统一为 calls 列表；每个元素只有 tool 和 arguments 两部分。
2. 同一 engine 同时接 ScriptedBackend 和 LiveBackend；两者共用工具、gate 与 grader。
3. 将所有 provider 细节集中到 provider_request 和 LiveBackend，切模型只改 model 字符串。
4. 把案号明确放入 live 消息。只保存到 Python 对象属性里而不传给模型，模型首轮仍不知道要查谁。
5. 每轮保存 raw 响应、calls、usage、观察或 error，不依赖最终文本倒推执行经过。

## scripted 到底模拟什么

它只根据观察产生确定性动作，不读取答案键；真实工具仍读取 fixture 数据。所以离线成功验证的是集成线路、规则和防护。它不是一个真实 LLM，不能用其通过率判断 prompt 写得好不好。

## 验证与报告

运行 python3 run_eval.py，期望 64 trials 全部有可判定记录；查看单例 --demo 能追溯每轮。报告可写：The scripted backend reproduces the same tool and guardrail pipeline without a key. It validates integration, not language-model competence. 后一句必须保留，避免把测试替身当成模型测量。

---PAGE---
# 05｜D2(a)：怎样把八个 drawer 合并为六个工具

## 要求不是“工具越少越好”

每个工具要回答：没有它哪个案例失败；是否与邻近工具混淆；即使从不调用，它的定义会怎样增加上下文成本。合并也不能把全部决策藏进一个“直接给答案”的工具。

## 当前六工具及修改理由

get_claim：返回案号、会员、日期、line、文档、narrative 和重复元数据。重复判断与当前案头信息相关，放在同一入口，避免额外一次 history 工具调用。

lookup_policy：接 claim_id，在内部解析 member 和 policy。删去独立 lookup_member 的模型步骤，防止模型选择其他会员的有利保单。

check_coverage：接 claim_id/code，同时返回排除规则和必需/缺失文档。文档要求本来按 procedure 定义，和 coverage 一起返回更容易形成完整 line 判断。

get_preauthorisation：保留单独工具，因为是否需要它由 coverage 结果决定。若提前查所有授权，就浪费轮次并削弱动态依赖的证据。

get_hospital_status：虽不单独决定升级，但答案键要求正确记录 panel 状态，因此仍有独立职责。

issue_decision_letter：唯一写入工具。名字代表业务动作，代码仅写本地结构化记录，不生成客户信件。

## 改完以后测什么

不能只数工具个数。scripts/build_analysis.py 比较实际旧 TOOL_SPEC 与最终契约的字符/4 估算，170 增至 514 token。工具少了，说明更完整反而变长；报告应诚实写这个代价，再解释节省主要来自哪些轮次。

## 报告句式

We removed a separate member lookup by resolving the policy inside a claim-scoped tool. This reduced an avoidable model step while preventing cross-member substitution. Complete descriptors increased prefix size, so fewer tools did not by itself imply a cheaper prompt.

---PAGE---
# 06｜D2(b)：把“请小心”改成接口防呆

## 六字段契约怎样写

对每个工具依次写 NAME+SIGNATURE、WHAT、INPUT、RETURNS、FAILS WHEN、IRREVERSIBLE。当前 tool_descriptors 函数提供给模型的精简说明，docs/TOOL_CONTRACTS.md 提供完整交接说明。两者必须与实际参数名和错误行为一致。

以 check_coverage 为例：输入是 claim_id 和 code；回答该 procedure 是否排除、需何种文档及授权；返回结构化字段；code 不在当前 claim、缺少保单前置观察或参数多余时抛出 ToolError；没有不可逆动作。

## 两个真正的 poka-yoke

第一，工具不接受模型自由传入 service date、claim total 或另一个 policy。由 claim_id 找到记录再计算，使“省略日期”“降低金额”“换个保单”在接口上无法发生。

第二，只有 code 确实在当前 claim 中，且已有该 code 的 coverage 观察证明需要授权时，get_preauthorisation 才可执行。仅在 prompt 写“不要乱查”不是这种约束。

## 修改时的同步步骤

先改函数签名与验证；再改 descriptor；再改 backend 的调用 envelope 示例；再改 scripted planner；最后加正确和错误输入测试。只改其中一处，模型看到的“说明书”与实际工具就会矛盾。

## 测试在哪里

tests/test_tools.py 检查依赖、跨案访问、缺失证据、错误金额和确认副本。tests/test_guardrails.py 检查未知工具、多余 admin 参数、负数、NaN、布尔金额等。money 使用 Decimal，防止把 bool 当作整数或用非有限值绕过比较。

## 报告句式

Claim-scoped inputs make cross-member substitution impossible at the tool boundary. Procedure membership and prior coverage evidence reject unrelated authorisation queries before execution. 不要写“消除所有推理错误”，因为模型仍可能选错动作或写不充分的解释。

---PAGE---
# 07｜完整示例一：过期授权要求怎样变成代码

## 从要求推导返回字段

CLM-8894 不仅要求 request_document，还要求记录 PA-5640 被找到、有效期在 2026-05-31 结束，以及为什么不适用于 2026-09-09 的服务。只返回 None，会丢掉“没有记录”和“有记录但过期”的区别。

## 修改位置与步骤

在 claim_agent/tools.py 的 _preauth：先读 claim 的日期；遍历与会员和 procedure 同时匹配的所有授权；分别解析 valid_from/valid_to；计算 valid、expired_before_service 或 not_yet_valid；把原记录加上状态放入 candidates；从 candidates 中选择有效记录作为 valid。没有匹配与有候选但无有效候选分别标明。

实际核心逻辑如下，完整代码见后面的源码定位附录：

```python
status = ('not_yet_valid' if service < start else
          'expired_before_service' if service > end else 'valid')
candidates.append(dict(deepcopy(row), status=status))
valid = next((r for r in candidates if r['status'] == 'valid'), None)
```

## 还要改哪里

ScriptedBackend 在需要授权却 valid 为空时，将 line 标为 unresolved，missing 写明 code、preauthorisation 和服务日期；reason 引用候选证据。_issue 必须自己重新核验有效性，不能因为 planner 写了 preauth ID 就相信其有效。

## 怎样验证

CLM-8894 证明过期；CLM-9310/9311 证明多个候选和有效期边界。测试要核对编号、日期、状态和最终缺失项，而不只看 decision。D7 删除有效性投影会诱导错误批准提议，独立写入校验仍拦住它。

## 怎样写报告

An existing authorisation is not necessarily applicable. We retain candidate IDs and validity dates, distinguish expired from not-yet-valid records, and require coverage on the service date. CLM-8894 therefore requests current authorisation rather than approving from mere existence.

---PAGE---
# 08｜完整示例二：重复案件与金额边界

## 为什么只比较一两个字段不够

同一会员同一天可以有不同医院或不同项目。教师数据专门设置 near-miss，只有会员、医院、日期和完整 line 集合都一致，才能认定是已决定案件的重复提交。claim_id 不同不代表不是重复。

## 代码怎样改

tools.py 的 _signature 把每行变成 code 与规范化金额，再用 Counter 保存同一行出现次数，排序后形成可比较签名。Counter 很重要：集合会把重复项目折叠；只对原 list 比较则会把项目换序误认为新案件。

当前 get_claim 工具读取决定历史并返回 prior claim ID 和匹配字段，供报告与 reason 引用。数据生成器中新加 CLM-9106 与已决定记录换序匹配，独立答案要求 duplicate_claim；另保留只差日期、金额或 line 的非重复对照。

## 额度规则怎样落实

_policy_result 先汇总整个 claim 的金额，再计算 annual_limit - used_to_date，判断 total > remaining。不能写成 >=，因为恰好等于剩余额度不应自动升级。也不能先扣除排除项目金额，再与额度比较；题目示例按 claim total 判断。

## 标签不能从程序输出抄

构造 remaining=600 的情形，分别写 600 和 600.01。先依据路由表写正确标签，再运行。教师 CLM-8971 的说明提到边界，但实际金额未到相等边界，因此保留原记录，新增真正边界，不改教师数据。

## 报告写法

We compare a monetary line multiset together with member, hospital and service date. Reordered duplicates escalate, while near-matches remain decidable. An added exact-limit case and a one-cent-over case test the strict greater-than boundary.

---PAGE---
# 09｜D2(c)：真正减少模型轮次，而非伪并行

## 先画依赖再写代码

当前链条是 get_claim → lookup_policy → check_coverage → 条件性 get_preauthorisation → write。get_hospital_status 可与 coverage 同轮；多个不同 code 的 coverage 也可同轮。需要前一步输出的调用不能因为“参数猜得出来”就提前执行。

## 原脚手架问题如何修

示例把 policy lookup 与使用硬编码 policy ID 的 coverage 放在同一轮。我们改成以 claim_id 为范围，并在 run_case 开始执行 batch 前检查本轮之前的 observations。判断依据是旧观察快照，不是刚在这个 batch 里产生的结果。

CLM-8842 的当前路径为：第 1 轮读 claim；第 2 轮读 policy；第 3 轮三个 coverage 加 hospital；第 4 轮查唯一需要的授权；第 5 轮写入。真实模型可以采用其他合法分组，不要求完全复制脚本路径。

## 串行实验怎么做才公平

--sequential 强制 backend 每次响应只有一个工具调用。同一批调用在本地依次执行，并不构成串行模型对照，因为模型响应次数未变化。比较必须统计模型轮次、累计输入输出、成本及业务正确率。

当前本地 fixture 读取按确定顺序执行。这里“并行”指模型同轮发出独立调用，并不声称用了线程加快磁盘查询。这个措辞应在报告中说明，避免夸大实现。

## 实测怎样写

最终离线两组均 64/64；串行 median/max 为 5/9，多工具同轮为 4/5；输入估算 506,789 降至 395,961，减少约 21.9%。这是按实际轨迹估算，并非 API 实际账单。

Model-turn grouping preserved scripted correctness while reducing repeated input context by 21.9%. Local reads execute deterministically; the saving comes from fewer provider turns, not faster disk I/O.

---PAGE---
# 10｜D3(a)：把确认门放在真正写入之前

## 正确位置

不是启动 agent 前问一次“允许吗”，然后任由它写任何结果。确认必须针对即将落盘的具体 proposal，位于 _issue 的业务校验之后、ledger append 之前。审批内容变了，应重新审批。

## 当前验证顺序

检查 proposal 的字段和 case_id；检查 evidence 是否引用真实 observation；确认每个必要工具证据存在；重算正确的 line、missing、trigger 和金额；检查重复写入；处理 suggest/confirm/act；最后复制合法 proposal，附 gate、时间、hash 和运行指标，再写文件。

## 默认自动批准怎样修

run_case 的 approval 默认为 None；confirm 没有回调或回调不明确返回 True 时抛出 gate_confirmation_required。run_eval.py 为测试显式传入模拟确认回调。它用来验证完整正常路径，不代表真人批准，更不能写成“所有 live 决策均经六名成员审核”。

## 防止确认回调偷改内容

将 proposal 的 deepcopy 传给审批函数。测试在回调中改变金额，验证实际写入内容仍是校验后的原对象。记录 decision_hash 可以对照具体批准内容，但它本身不是电子签名或真实身份认证。

## ledger 与隔离

每个 trial 用独立临时目录；持久 ledger 在 fcntl 锁内读旧记录、拒绝同案重复、再追加。锁解决同一文件的并发竞态，单会话 self.record 解决同一次运行的重复写入；二者不是同一个问题。

## 报告句式

The confirm gate applies to the validated decision payload immediately before the local write. Evaluation uses a separately declared simulated operator; the core defaults to no approval. 这两句把安全默认与测试便利同时解释清楚。

---PAGE---
# 11｜D3(a)：步数、token、美元与动作去重

## 四个限制解决不同失败

Step cap 防止无限循环；token ceiling 防止长上下文；美元 threshold 控制不同模型价格；dedup 尽早发现重复调用。只有一个 step cap，仍可能在达到上限前烧掉大量高价 token；只有预算也不能准确识别低成本死循环。

## 当前代码怎样实现

run_case 每轮先检查已累计 token/cost；取得模型响应后立即记账，再检查是否超过阈值；若超出则不执行本轮工具。这样已发生的模型费用不会因为行动被阻止而“消失”。每个动作按排序 JSON 编码形成 key，已出现的相同动作触发 duplicate_action。

注意当前策略是重复相同动作即终止，它保守地把某些可能可恢复的重复也计成业务失败。不能在报告里把“拦住了”直接算作“完成了”。现场 trace 可以解释为什么便宜模型 token 不贵、fallback 却高。

## 上限来源

离线完整串行最长合法路径为 9 轮，同轮多工具最长 5 轮，故统一 cap=10 有证据基础。token_limit=60,000。核心默认预算 0.10 美元；live runner 配置停止阈值 0.14、每个并发任务预留 0.18。已经发出的请求不能撤回，不能声称阈值是逐分绝不超出的硬切断。

真正全局硬约束还来自本 key 的 10 美元 lifetime 限额、不可追加；它比本次每用户每月 10 美元更严格，但不是已实现生产级月度多用户计费服务。

## 测试与写法

test_loop.py 验证响应已计费但行动被预算阻止、malformed block 明确失败、ledger 含实际运行计数。报告要写清 stopping threshold 与 in-flight reserve 的区别，而不是只写“实现预算限制”。

---PAGE---
# 12｜D3(b)：攻击测试必须真正在测攻击

## 为什么旧测试可能是假阳性

如果任何请求都因没有操作员确认而被阻止，那么恶意 narrative 的测试通过不能说明系统识别了攻击。正确对照是：正常确认已经存在，攻击仍不能使不合法 proposal 通过；同时正常文本在相同条件下可以完成。

## 当前攻击面与测试

narrative 来自外部会员，可能直接要求忽略规则、伪造 check_coverage 返回、伪造 system/developer 角色。detect_instruction 标识已知形式；真正写入时 _issue 仍独立检查，不能仅信模型一句“已安全处理”。CLM-8952 还必须取得真实 coverage 证据，不能只跳过全部检查后泛泛升级。

## 开发中实际发生的两项问题

带 priority 属性的 system 标签最初漏检，使 CLM-9101 错误 ACT；匹配 ignore 的正则跨越句子，又误把 CLM-9309 的正常医嘱识别为攻击。初次集成 64 trials 仅通过 60，修正角色标签和语句范围后全部通过。完整 before 轨迹保存在 development_before_injection_fix.json。

## 修改步骤

先保存失败输入和轨迹；针对明确攻击语法修改检测；同时加入正常近似文本，防止扩大误报；在模拟批准开启条件下重跑；最后全量回归。不能把新增规则写成“防御所有 prompt injection”。

## 报告与 checklist 分开

评测案例问“是否正确完成业务”；guardrail checklist 问“能否被诱导违规、越权或耗尽资源”。当前独立 checklist 为 16 项，v1/v2 都通过；再加其他工具和循环测试共 33 项。OWASP 分类是组织威胁的框架，不是通过测试便取得的安全认证。

示范句：Hostile cases were tested with simulated approval enabled, so refusal could not be explained merely by an absent operator gate. Benign controls exposed and corrected overblocking.

---PAGE---
# 13｜D4：怎样新增案例而不污染答案

## 三种文件不要混淆

make_fixtures_A.py 是可重复的数据来源；data_A/*.json 是生成后的记录；expected_outcomes_A.json 与 expected_details_A.json 是独立答案。前者保留教师原标签形状，后者增加机器能严格核验的行、金额和缺失项。

## 一条新案例的完整操作

1. 先选要测的业务规则，例如“授权尚未生效”，写清要防的错误是只看存在。
2. 检查会员、保单、医院和 procedure 的外键是否都能解析；如果需要新的支持记录，将其加入对应 EXTRA_*。
3. 确保没有更早的触发条件遮蔽目标，例如要测授权日期，就不能先让保单失效。
4. 依据 Appendix A 写标签，注明 must_record 与 case family；不能先跑模型再把结果抄成答案。
5. 运行 generator 和 check_my_data；检查原始 15 案和原标签未变化。
6. 跑单例再全量，若 disagree，依据业务规则判断是 agent 还是标签错，不依照模型多数投票定真值。

## 当前集合

40 案：28 个 ACT、3 个 ASK、9 个 ESCALATE。负例定义为非 ACT，共 12 个；普通各 1 trial，负例各 3 trials，因此每配置 28 + 12×3 = 64。重复 trial 检验同案稳定性，不代表 64 个独立业务样本。

## 为什么需要独立详细标签

例如只写 approve_in_principle 会放过漏写排除项的错误。详细标签必须检查每行 code/amount/status、批准/拒付合计、授权编号和指定文档。重复 procedure 仍按原行保留，不因为按 unique code 查询而丢掉真实重复 line。

## 报告句式

Labels were derived from the routing table before evaluation, with original records preserved. The set contains targeted boundary and near-match controls rather than many clones of easy approvals.

---PAGE---
# 14｜D4：从弱 outcome 检查升级为强 grader

## 修改位置

claim_agent/harness.py 的 grade 只在结果返回后运行。它读取 expected_details_A.json；agent 与 tools 不得导入这个答案键。这样即使某个工具规则写错，grader 仍可能依据独立标签指出错误。

## 当前检查顺序

没有 gated record 就失败；比较 case_id、decision；升级比较 trigger 和 human claims assessor；普通结果比较 approved_total/refused_total；逐行比较 code、amount、status 与 exclusion/preauth；规范化 missing 的字段差异；检查一次成功写入、gate、evidence IDs 和案例指定工具约束；必要时核对 hospital panel。

## 为什么要做字段规范化

独立标签用 pending、preauth_id、item；运行记录用 unresolved、preauth、document。grader 可以把同一语义映射到统一格式，但不能模糊成“只要字符串包含授权就通过”。映射应针对固定字段，金额与代码仍须一致。

## 为什么要检查正确原因

escalate + annual_limit_exceeded 与 escalate + duplicate_claim 虽然 outcome 相同，业务证据完全不同。只检查 decision 会奖励碰巧猜中。缺文档也必须指出哪一行、哪一种文档和适用日期。

## 输出与退出码

每次 r 保存 grade.pass、errors、check，再汇总分母。run_eval.py 只要有一个 trial 失败就返回非零，使脚本或 CI 能发现失败，而不是终端显示完表格后仍成功退出。

## 写进报告

We grade the decision and its decisive fields, not the path alone or a substring that usually accompanies a correct answer. A correct outcome with the wrong trigger fails. 同时说明工具轨迹约束只用于核验必要证据与 gate，不把任意一种固定检索路径强加为唯一正确答案。

---PAGE---
# 15｜D4：怎样使用独立 judgement 而不自评自满

## 哪些东西代码检查不了

reason 可能语法正确却没解释原因；可能列出很多观察但没有建立日期与结论的关系。对这些自由文本质量问题，使用人或独立模型判断。不要把是否写出了某个英文单词当成解释充分的证明。

## 当前实验做法

预选六案：8842、8894、8925、8952、9309、9310；按 trial 规则每配置 12 项。Haiku 评其他模型，Gemini 评 Haiku。五个 v2 加一个 v1 共 72 个 live 指定项，另加 12 个 scripted，共 84 份状态记录。

代码已经失败的项不让 judge 翻案，记录 code_failed_not_judged。代码通过的项才发给 judge；最终实际独立评分 52 次，其中通过 49。所有 84 项都有明确状态，没有待判项被算作成功。

## 评分器自身出错时怎么改

首版把“未执行逐行 coverage 定价”误解为“原始 claim 没有各行金额”。原始账单有金额与 agent 没有执行 coverage 并不矛盾。我们保留旧 verdict，澄清术语后对整个预选子集重评，不能只重评不喜欢的失败。

后来发现 reason 也应明确写“因超限而未逐行定价”，遂改善最终 engine 并把全部 384 次重新运行。这个顺序必须说清：校准 judge 不是修改 agent；修改 agent 后也不能沿用旧版本 battery。

## 最终通过率口径

非预选项以代码评分为准；预选项要求代码与 judge 都通过。Llama 代码 51/64，加入解释判断后 48/64。Haiku 两者都为 64/64。成本使用后者 assessed rate；表格同时保留 code rate。

## 报告写法

Judgement complements deterministic checks on a preselected subset. We retain the judge prompt, evaluated input and raw verdict, and use a different model from the one being graded. Pending or code-failed items cannot be counted as judged passes.

---PAGE---
# 16｜D5：把 live 调用变成可比较实验

## 代码位置与输入

backends.py 的 provider_request 是唯一处理 HTTPS provider 的函数；LiveBackend.next 组装 system prompt、案号、已有 observations 和运行时错误反馈。使用固定 temperature=0、max_tokens=2200 及 JSON 输出要求。温度为零仍不保证跨时间、provider 路由或服务实现完全确定。

## 必须保存什么

原始响应 raw，包括 choices 与 usage；解析后的 calls；每轮实际输入/输出 token 和 cost；模型 ID、variant、trial、源码数据 hash、模拟操作员声明。JSON 解析失败也要保留原始响应，不能只抛异常后丢掉失败证据。

## 当前重试策略

最多两次工具形状或依赖修正机会；错误反馈指明契约，不替模型生成正确业务答案。重复已出现的相同动作仍被去重终止。网络异常不无限自动重试，避免失控费用与只保留最终成功的偏差。

## 五模型与 v1 对照

最终五家族为 Gemini Flash Lite、GPT-4o-mini、Llama 3.3 70B、Qwen3 30B、Claude Haiku 4.5；价格来自保留的 OpenRouter catalog。每个 v2 64 次，另用同一 Gemini 跑 v1 64 次，总计 384。

正式模型选择跨便宜与较高价格层。最便宜的 token 并不一定带来最便宜的任务，因为它可能造成更多人工 fallback。各模型都用同一数据、规则、试次和最终版本，只更换模型配置。

## 单 key 的真实边界

用户要求集中使用共享 key，因此所有执行按实际方式披露，不能写成六人各自用个人 key 完成。密钥位于仓库外，原始响应和压缩包不得含 credential。余额与扣费核对只保留非敏感数值。

---PAGE---
# 17｜D5：冻结、完整重跑与预算对账

## 为什么要冻结

若模型 A 跑完后改了 prompt，模型 B 使用新版本，差异就混入实现变化。scripts/run_live.py 对代码、fixture 和答案文件计算 SHA-256，保存在 manifest 和每个 trial；检测已有 manifest 与当前 fingerprint 不同就停止续跑。

## 当前两轮完整实验

第一轮 384 次保留在 results/live_initial；它揭示早退说明、触发枚举与错误反馈不足。最终改进后，不只挑失败案件重试，而是再次运行全部六配置，放在 results/live。pilot_initial 与 pilot 只属于开发试跑，不混入正式分母。

最终代码检查：Gemini 43/64、GPT 26/64、Llama 51/64、Qwen 40/64、Haiku 64/64；Gemini v1 为 40/64。加入指定解释评分后 Llama 为 48/64，其余最终合计不变。说明改进对模型影响不同，不保证所有模型都提高。

## 预算如何核对

runner 对每个在途任务预留费用，累计已保存结果。最终 reconcile_spend.py 只读 provider key 用量，比较任务开始和结束累计 usage。全部两轮、pilot 和 judge 的账户增量为 US$2.411415156，剩余 US$7.567671255；与返回 usage 汇总的差仅为浮点舍入级别。

若传输失败发生在 provider 已处理后，用量可能没有返回，应承认单请求计数不完整，并看账户总额。不能把未知自动当零成本。当前表格对缺用量运行有标记。

## 报告写法

All final configurations share a frozen source/data fingerprint. We reran the entire battery after the final interface revision and retained the earlier battery separately. Failed trials remain in the denominator. 这比“我们反复调到高通过率”更能说明实验有效性。

---PAGE---
# 18｜D6：从原始 usage 写出三层成本

## 先选对公式

本题采用失败交人工的世界，不是无限重试直到成功。因此不是 variable/P，而是每任务成本 C = variable + (1-P)×failure_cost。每月成本 = 8000×C + fixed_monthly。脚本位置为 scripts/build_analysis.py，原则沿用 Class 5 notebook。

## 数据来源与单位

input/output token 来自 live API usage；catalog 的 prompt/completion 是每 token 美元，直接相乘，不再错误除一次百万。若使用每百万价格表才应除 1,000,000。baseline 使用未缓存 list price，provider 实际 charge 另存，不把自动缓存优惠偷偷放进 headline。

failure_cost = 38 美元/小时 × 12 分钟 ÷ 60 = 7.60 美元。P 使用 assessed pass rate。正确升级本身算业务成功，不应当作模型失败；常规人工办理和 operator 确认劳动是该简化公式之外的生产成本。

fixed=80 美元/月是明确假设：存储 5、基础设施 10、监控 10、评测刷新 5、维护 50。它不是实测云账单，不能与本次 API 扣费混淆。

## 用最终 Haiku 演算

64 次总 input=488,280，output=43,973；价格为每百万 input 1 美元、output 5 美元。变量合计 0.708145 美元，除 64 得约 0.01106477 美元/任务。样本 P=1，公式中的样本 fallback 为零，每月 8000×0.01106477+80≈168.52 美元。

这个 168.52 只是按当前样本代入的点估计，不是生产承诺。若成功率降到 90%，单任务增加 0.76 美元人工 fallback，月成本即增 6080 美元。必须把这类敏感性放在点估计旁边。

## 报告句式

Fallback dominates token price. The measured zero-error sample does not establish zero future fallback, and the fixed monthly allowance is an explicit operating assumption rather than incurred spending.

---PAGE---
# 19｜D6：四个杠杆、敏感性与盈亏平衡

## 四个杠杆怎样分别证明

工具定义大小 B：比较实际旧 TOOL_SPEC 与最终契约，估算 170→514，变大也要报告；不能用删了两个工具就推出 prompt 变小。轮数 T：全集串行与分组轨迹；输入估算下降 21.9%。观察大小 D：只取 preauthorisation 返回，v1 平均 137.6、v2 平均 82.4 个估算 token。成功率 P：Gemini v1 assessed 40/64、v2 43/64，影响 fallback。

B 是每轮重复的固定前缀；D 是后来不断重传的观察；T 决定重复次数。这里逐轨迹记账比把一套固定 B/D 套在所有案件上更直接。char/4 是近似，不是 provider tokenizer 实测，报告中必须标注。

## 敏感性怎样算

对每个模型取 P-0.10、P、P+0.10，裁剪到 [0,1]，分别计算 variable+(1-P)×7.6。可再用不同失败人工成本核对推荐是否稳健。不能把 10% 相对变化写成 10 个百分点：80% 的 ±10pp 是 70%/90%，不是 72%/88%。

## 盈亏平衡怎样算

设便宜模型 token 成本 C，贵模型含其失败的总成本 E，一次失败成本 F。解 C+(1-p)F=E，可得 p*=1-(E-C)/F。最终最便宜 token 的 Qwen 需要约 99.86% 才与本样本 Haiku 比肩，但实测 assessed 为 62.50%。便宜 token 的优势不足以抵消失败。

## 不确定性怎样写

64/64 的有限样本 Wilson 区间仍有低于 100% 的下界，而且负例三次重复并非独立不同案件。区间只作说明，不能直接宣传生产置信保证。若 case mix 改变，当前按 trial 加权的 P 也会变。

示范句：The cheap model does not clear its break-even success rate under the default handling cost. This conclusion is conditional on the fixture mix and failure-cost assumption, not a universal ranking of models.

---PAGE---
# 20｜D7：怎样做能说明因果的失败复现

## 必须保持什么不变

同一个 engine、同一故障输入、同一数据和其他 guard，只删除一个目标组件，再恢复。另写一个很差的 agent 与正常 agent 比较，无法判断究竟是哪项差异造成效果，不能替代本题消融。

## 实验一：删去动作去重

tests/test_d7.py 的 RepeatingBackend 每次都请求 get_claim。正常版第二次发现重复并停止；disable_dedup=True 后允许一直到 10 轮 cap。恢复去重再次第二轮停止。scripts/reproduce.py 保存三组完整轨迹和 grade。

应报告 normal/ablated/restored 的 turns、input、output、估算 cost、stop 和任务是否通过。这个故障 backend 永远重复，所以正常与恢复也没有完成业务；去重恢复的是迅速止损，不是完成任务。把它写成“恢复成功率 100%”是不真实的。

## 实验二：删去授权有效性投影

正常 _preauth 只把真实有效候选放到 valid；ablate_preauth=True 用第一个候选，即使已经过期。相同 scripted planner 因而提出批准 CLM-8894，但 _issue 仍用完整规则重新判断，把错误提议挡住；恢复后正确请求授权。

## 为什么修复层不同

循环问题属于 engine 的执行记忆和资源控制；prompt 请求“别重复”不能代替集合去重。授权问题属于工具返回语义；模型不能从虚假的 valid 投影可靠推断真实有效性。writer 是第二道代码防线，保留它使实验显示防御纵深。

## 报告句式

Removing validity projection induced an unsafe approval proposal, which the unchanged writer rejected. Restoration recovered the correct request. This is a contained interface failure, not an unsafe write. 这段明确发生了什么和没有发生什么，不能夸大事故。

---PAGE---
# 21｜如何把技术结果写成六节英文报告

## 第一节 Why an agent

按“备选架构能力→本题选择→ground truth→首次写入→实测可靠性”组织，不按开发流水账。当前选 Gemini P=43/64、median T=5，s=P^(1/T)≈0.9235；固定 s 时两轮约 85.3%、八轮约 52.9%。P 已经是整次成功率，不能误用 P^T。

## 第二节 The tool layer

选一两个有代表性的工具合并、防呆和依赖变化，配前后数字。解释为什么不新增工具、为何多工具同轮合法、观察缩小是否真带来 pass rate 改善。不要逐函数复述全部代码；细节留给本手册和契约附件。

## 第三节 What the evidence showed

先说明 40 案/64 trials 和评分方法，再写模型间最有价值的差异。强调负例、失败类型和 judge 对部分解释的否定。所有模型完整表放表格，正文不必给每个模型一段广告式点评。

## 第四节 What it costs

先讲三层和数据源，再给最佳样本选项、月成本与敏感性；随后说明哪个杠杆主导、便宜模型是否过盈亏平衡。把固定成本假设、确认劳动和生产 case mix 局限写明，避免让低 token 账单冒充总业务成本。

## 第五节 The two failures

每项按“同输入删除什么→观察到什么→哪层修复→恢复结果→其余控制作用”压缩。必须使用最终 d7_failures.json 数值，不照抄教师 8 轮、1.6 倍的示例。

## 第六节 What we would not deploy

写出当前证据未覆盖的风险，以及一个未构建架构的取舍。第二 runtime reviewer 可能改善解释，但增加调用、相关错误和攻击面，因此只把独立 judge 用作评测仪器，不增加第二个写入者。

## 文段自检

每一句带数值的主张能否找到结果文件？每一句“导致”是否有受控对照？每一句“安全”是否限定为测试范围？正式正文保持不超过 2,000 英文词，当前 1,552；中文详解不塞回正文凑篇幅。

---PAGE---
# 22｜从一条新增要求完成一次安全修改

## 示例：老师要求“授权有效期第一天也要通过”

第一步定位规则。有效期是 inclusive，即 valid_from ≤ service ≤ valid_to。先读 Appendix A 与现有标签，确认不是自行发明新政策。

第二步设计案例。在 make_fixtures_A.py 的 EXTRA_CLAIMS 增加案，服务日等于有效授权起始日；确保保单 active、额度足够、文档完整，没有重复或注入等前置触发。必要时增加新的 supporting rows，不改教师原行。

第三步先写答案。expected_outcomes_A.json 写 approve_in_principle 与必须引用的授权；expected_details_A.json 写 covered、preauth_id、总额。记录 case_provenance，说明测试目标。

第四步看当前代码。_preauth 已用 service < start 和 service > end 排除，其余为 valid，起止日均合法，因此可能只需要加测试而不改实现。不要为了显得做了工作而把正确逻辑重写。

第五步运行 generator、checker、单例、全量。若失败，检查是标签误设、缺其他数据，还是真实边界 bug；保存失败再修，不能把 expected 改成模型结果。

第六步更新实验。若正式冻结后代码、数据或标签变化，fingerprint 变化；旧 live 结果必须另存，按新版本重跑受影响的正式实验，不能把新 41 案与旧 40 案的分母混合。

第七步写说明。要求、原因、位置、验证、结果、局限写入 IMPROVEMENTS。报告只需一句：An added inclusive-start-date case verifies that authorisation is valid on its first covered day. 只有确实运行并通过后才能用 verifies。

## 本章的目的

不是把上述新增案自动加入当前冻结集，而是教会成员今后面对新要求时先判断“要改代码还是只需补测试”。当前正式集合仍为 40 案，不因本手册示例改变。

---PAGE---
# 23｜复现与交付：按什么顺序运行

## 免费离线验证

在 Total_LI_LINGHAO 目录运行以下命令。它们写入结果文件，因此正式发布前应确认使用的是预期代码版本；不会调用 live provider。

```bash
python3 A2_reference_data/check_my_data.py
python3 run_eval.py
python3 scripts/reproduce.py
python3 scripts/replay_judgements.py
python3 scripts/verify_package.py
python3 scripts/build_analysis.py
```

checker 验证外键与原数据；run_eval 默认离线；reproduce 重建串行/v1/D7 并跑 33 测试及双版本 checklist；replay_judgements 重放归档 verdict，不是重新独立评分；verify 检查 384 trials、指纹和 token；analysis 重算表格成本。

## 报告与打包

PDF 构建需可选 reportlab/matplotlib；评测 engine 本身只依赖标准库。英文正式报告由 build_report.py 生成；本中文手册由 build_walkthrough_zh.py 生成。生成后必须渲染检查，不能只检查文本能否抽取。

```bash
python3 scripts/build_report.py
python3 scripts/build_walkthrough_zh.py
python3 scripts/package_submission.py
```

压缩包排除凭据、缓存和无关旧代码，保留原始实验、答案键、脚本与说明。在临时目录解压后重跑，比在开发目录“再成功一次”更能发现隐含路径依赖。

## 需要真实人完成的部分

六人真实录制并说话；核对贡献和集体自评，必要时填官方模板；确认公开仓库发布；上传 NTULearn 并填写真实视频链接。当前文档不会伪造这些状态。密钥集中操作的课程要求差异也必须如实说明。

## 变更说明写作模板

“要求 X 需要证据 Y。原实现 Z 在情形 C 下不足，因此在函数 F 修改为 G。测试 T 的 before/after 为 A/B。局限 L 仍未覆盖。”按此句式可以解释大部分代码修改，无需堆砌“优化、增强、完善”等空泛词。

---PAGE---
# 24｜答辩时最容易被问到的十个问题

## 1. 为什么不直接用规则工作流？

规则工作流可行。作业要求单 ReAct agent；本实验测量其动态工具选择、防护、成本与局限，而不是证明规则系统无法处理分支。

## 2. 离线 100% 是不是写死答案？

ScriptedBackend 只读取工具观察，不读 expected 文件；但它仍是确定性测试替身。因此 100% 只证明集成与规则回放，模型能力看独立 live battery。

## 3. writer 重新算规则，会不会掩盖模型错误？

它只验证或拒绝 proposal，不自动把错误改成答案。被阻断且未完成的 run 在 grader 中失败，不能因“安全”得到任务成功分。

## 4. 为什么部分拒付仍然 approve？

固定业务路由要求可决定的各行在一个 first response 内说明：covered 与 not_covered 并存。需要人工判断的触发才升级。

## 5. 确认回调直接 True 可靠吗？

它仅是评测 operator fixture，明确标注。核心默认 None 会拒绝写入；不能把模拟回调说成真人审批。

## 6. “并行”到底做了什么？

多个独立工具合并到一个模型响应，减少 provider 轮数。当前本地读按确定顺序执行；不声称线程并发或磁盘加速。

## 7. v2 是不是一定更好？

返回平均更小；Gemini assessed 从 40/64 到 43/64，但样本用于开发且有重复 trial，不能断言所有模型或新数据都会提升。

## 8. Haiku 64/64 能否部署？

不能据此批准部署。样本有限、合成数据、已知攻击、相关 trial 和生产 case mix 都限制外推，确认与常规人工成本也未完全计入。

## 9. 为什么 D7 正常循环组也没有成功任务？

固定故障 backend 永远重复。去重只让失败快速可见并减少花费；正常业务全集另外验证 64/64，二者不是同一实验。

## 10. 最有说服力的改进是什么？

不是功能数量，而是能从真实失败追到修改与回归：例如角色标签漏检和正常文本误报；授权候选证据丢失；最终字段反馈与早退说明；每项都有文件、轨迹和局限。

---PAGE---
# 25｜来源、数值核对与阅读索引

## 作业与课程依据

PE6201_A2_Applied_AI_System.pdf：D0–D7、提交要求、评分标准、Appendix A Problem A。PE6201_A2_FAQ.pdf：负例、trial、代码/判断评分、成本及团队活动解释。Adding Extra Cases 指南：追加规则、答案键与不可修改原记录约束。Class 4 与 Class 5 notebook：手写循环、token 累积和三层成本方法。

## 当前实现的主要入口

claim_agent/agent.py：ScriptedBackend、run_case、轮次与预算。claim_agent/tools.py：_signature、_policy_result、_coverage、_preauth、call、_issue、tool_descriptors。claim_agent/backends.py：system_prompt、provider_request、LiveBackend.next。claim_agent/harness.py：grade、trial_manifest、summarize。

scripts/run_live.py：模型清单、fingerprint、恢复和任务预算。scripts/run_judgement.py：独立 judge prompt 与预选集合。scripts/build_analysis.py：assessed rate、baseline 成本、敏感性与表格。scripts/reproduce.py：完整离线再生。源码定位页提供生成时行号与摘录。

## 结果文件的职责

results/live/ 是最终六组正式运行；live_initial/ 是此前整轮，不能合并计算最终 pass rate。pilot* 是开发试跑。judgement/ 是最终独立 verdict，旧两轮判断保留在其他 judgement 目录。scripted.json、sequential.json、scripted_v1.json 为离线对照。d7_failures.json 是两项受控失败。cost_model.json、spend_reconciliation.json 分别记录业务模型与真实 API 扣费，不可混用。

## 固定数值检查清单

40 案，12 个负例，每配置 64 trials，六配置 384；两个完整 live battery 共 768，另有 pilot 和 judge，不把 768 写成正式最终分母。33 项测试、双版本各 16 checklist。最终 assessed 五模型依次 43、26、48、40、64（均除 64），Gemini v1 为 40/64。全部实验实际扣费约 2.41 美元。

## 文档边界

本手册依据实际文件解释实现，不新增业务规则，不改变正式实验。示范英文段落可供改写，但提交前必须与最新代码和结果一致。未经发生的个人贡献、真实审批、视频录制、发布和提交都不得在报告中改写成已经完成。
