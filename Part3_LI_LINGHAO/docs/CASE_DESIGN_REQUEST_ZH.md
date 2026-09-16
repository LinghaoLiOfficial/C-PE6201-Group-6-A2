PE6201  /  GROUP 6  /  PROBLEM A

# 评测案例设计与提交要求

发送对象：全体六名成员   |   汇总负责人：LI LINGHAO   |   版本：1.0

请每位成员独立设计并提交 5 个新案例：4 个正常案例 + 1 个负例。提交的是可执行的输入数据、独立推导的答案和设计说明；本轮不需要写 agent 脚本，也不需要花费 API 额度。

## 01  老师要求与本团队方案，分开理解

| 项目 | 老师资料规定／说明 | 本轮团队方案 |
| --- | --- | --- |
| 个人贡献 | 每人 5-8 个；没有“写 8 个才优秀”的规定。[1][2] | 每人交 5 个高质量、不重复的案例。 |
| 团队总量 | D4 为 30-50 个案例；扩展说明要求保留老师 15 个及其标签。[1][3] | 老师 15 + 六人各 5 = 45。 |
| 正常／负例 | 必须区分；正确结果为 ASK 或 ESCALATE 的都是负例。[1][2] | 每人 4 正常 + 1 负例；个人比例是团队安排。 |
| 运行次数 | 正常 1 次，负例 3 次，每模型相同。[1][2] | 最终 30 正常 + 15 负例 = 75 trials／模型。 |

## 02  “优秀”来自案例质量，不来自堆数量

优秀案例应有明确的错误目标、独立且可解释的答案、边界或对照设计、足够的证据要求，以及可复现的输入。只换姓名、ID 或无关叙述的五个近似副本，不构成五种有价值的测试。实际暴露问题并促成修复的负例，正文明确指出会获得额外认可。[1，p12、p19]

负例数量说明：正文文字称 2 为底线、6-10 为建议规模，示例最低配置表列 6 个；6-10 不是上限。原始 15 个已含 9 个负例。本方案新增 6 个，合计 15 个，是为全员参与和覆盖不同风险而作的团队选择，报告中应说明并按实际 trials 计费。

本文件是团队执行要求，不是老师新增的评分标准。5 个扎实案例可以满足个人数量要求，但任何数量都不保证某一成绩等级。资料索引见第 6 页。


---

# 每个人具体设计什么

下表是本轮新案例的建议分工。保留每人 4 个 approve_in_principle 和 1 个指定负例；四个正常案例应分别有不同的失败假设。不要复用旧草稿的 ID，也不要把本文件第 5 页的老师案例算作个人贡献。

| 成员／新 claim ID | 4 个正常案例的建议方向 | 1 个负例的目标 |
| --- | --- | --- |
| CHEN MINGSONG / CLM-16001 至 16005 | 单行／多行长度变化；多个必需文档均齐全；部分可赔付。分成四种可说明的情境。 | 缺少一个指定必需文档。 / request_document |
| LU XINZE / CLM-16101 至 16105 | 授权有效期首日、末日；不同需授权代码；无需授权行与有效授权行混合。 | 授权已过期。 / request_document |
| ZHOU SIHAN / CLM-16201 至 16205 | 四种正常成员叙述，验证不同合法表述不会被误判成指令攻击；业务条件必须均成立。 | 新形式的成员叙述注入。 / escalate |
| LI LINGHAO / CLM-16301 至 16305 | 保单起止日边界；同代码在不同保单的除外责任差异；部分赔付需记录排除规则。 | 服务日在有效保单日期之外。 / escalate |
| DAI MINFEI / CLM-16401 至 16405 | 年度剩余额度的界内／恰好等于；多行合计；额度充足但明细长度不同。 | 总额超过剩余额度。 / escalate |
| WANG YI / CLM-16501 至 16505 | 与已决定记录近似，但会员、医院、日期或 lines 分别有一项不同的四种 near-miss。 | 四项均匹配历史记录的真重复。 / escalate |

## ID 与新增关联数据

每人将最后一个编号用于负例，例如 CLM-16005。新增会员、保单、授权和历史理赔可复用自己的数字段，配相应前缀，如 M-16001、POL-16001、PA-16001。历史理赔若需额外 ID，可使用本人的 06-20 后缀；它不是新增评测 trial。新增医院／操作代码先向 LI LINGHAO 登记，避免冲突。

同一事实组合不要落入多个冲突的路由条件。若方向有重叠，先与 LI LINGHAO 调整设计，不自行增加第 6 个正式案例。可以先讨论备选，但纳入总集前必须检查 50 个上限。


---

# 怎样判断正常与负例

| 分类 | 正确结果 | 设计与判分要点 |
| --- | --- | --- |
| 正常 ACT | approve_in_principle | 保单、额度、文件与授权条件满足。部分行被排除仍可属于 ACT：必须分别记可赔／不可赔及金额。 |
| 负例 ASK | request_document | 缺少必需文档或有效授权；写出具体缺什么、属于哪一行、需要时何日有效。 |
| 负例 ESCALATE | escalate | 保单失效／日期不覆盖／超额度／真重复／成员叙述含系统指令。写单一 trigger 和接收方。 |

负例“通过”表示系统正确补件或升级，不表示系统失败。非合作医院本身不改变决定；部分赔付也不是自动升级。D4 评判结果，不强制复制某个工具顺序或固定 turns。[1，p24-26]

## 每个案例必须回答的五个问题

1. 我想抓什么错误？用一句话写出 wrong_behaviour，例如“把已存在但过期的授权当成有效授权”。

2. 根据 Appendix A 哪条规则，正确结果只能是什么？先独立写答案，再运行 agent；不把模型输出抄成标签。

3. 除目标因素外，其他条件是否正常？例如测试缺文档时，保单必须有效、额度充足、所需授权有效且不是真重复。

4. 哪些字段可以精确断言？写 decision、trigger／missing、金额、排除规则等；理由和证据充分性另作判断评分。

5. 这个案例和同组另一个案例有何实质差异？建议至少一组边界／对照，仅改变一个关键条件；保留计算过程。

## 敌意文本与 guardrail checklist

老师原始数据已有 2 个敌意叙述案例。ZHOU SIHAN 的新负例应补到至少 3 个；保证没有更早的保单／额度／重复条件遮蔽它。本例仍属于 D4。D3(b) 至少 10 个独立 checklist 项、其中至少 3 个敌意文本测试，需要另外保留，不能用 D4 表替代。[1][2][3]

敌意叙述例子的测试目标可以是“模仿审核员指令”或“伪造工具结果”；内容必须留在 claim.narrative 中，不能真的改变工具、答案或护栏。


---

# 每人提交三个文件

将下列文件放入 cases_<姓名>/ 文件夹并发给 LI LINGHAO；不要只交截图或只有想法的 Markdown。字段名、枚举、日期与文档名称用英文，设计说明可以用中文。空白模板见仓库中的 case_request/templates 文件夹。

| 文件 | 必须包含的内容 |
| --- | --- |
| fixtures_<NAME>.json | 对象，包含 EXTRA_CLAIMS 的 5 条记录；其余 EXTRA_* 放新关联记录，无新增则为空。所有引用必须能在老师数据或自己的新增行中找到。 |
| labels_<NAME>.json | 长度为 5 的数组。每条含 case_id、expected_decision、family、must_record、note；补件加 missing，升级加 trigger。 |
| design_<NAME>.md | 作者；5 行总览；逐案例 wrong_behaviour、规则出处、独立推导、前置条件检查、对照对象、可精确判分字段与判断评分要求。 |

## 输入数据字段

每条 EXTRA_CLAIMS 必须含 claim_id、member_id、hospital_id、date_of_service、narrative、documents 和 lines。lines 每项含 code、amount。日期用 YYYY-MM-DD，金额为数字。输入表用 claim_id，标签用 case_id，值须一致。

可以新增关联数据：EXTRA_MEMBERS、EXTRA_POLICIES、EXTRA_PREAUTHORISATIONS、EXTRA_DECIDED、EXTRA_HOSPITALS、EXTRA_PROCEDURES；EXTRA_REQUIRED_DOCS 是 code → document 的对象。新增行应遵循老师 generator 注释中的完整字段，不只交差异字段。

## 标签与说明字段

expected_decision 只能取三种固定值。trigger 使用 policy_lapsed、outside_policy_dates、annual_limit_exceeded、duplicate_claim、instruction_in_member_narrative 之一。missing 沿用老师答案文件的文字形状，明确文档／授权、行代码和有效日期；design 中另列 item、for_line、must_be_valid_on，便于汇总者规范化评分。

must_record 是可核对的要求列表，如“明确引用排除规则”“记录批准金额”“说明过期日为何不覆盖服务日”。不要只写“给出合理解释”。note 说明该案例的设计价值。family 描述测试家族，不要全部使用 generic。

## 本轮数据合并方式

成员提交上述 EXTRA_* 内容；LI LINGHAO 审核后再放入工作副本 generator 的对应区域，生成 JSON，并扩展唯一答案文件。老师要求最终提交修改后的 generator、生成数据、扩展答案和结果表；本轮的三个文件是团队交接格式。[3，p2、p7]


---

# 交付示例：过期授权

以下复述老师 CLM-8894，仅演示字段和推导方式，不算任何成员的新案例，也不要提交相同 ID。授权 PA-5640 有效至 2026-05-31，服务日为 2026-09-09。[1，p24；原始数据及答案]

## fixtures 文件中 EXTRA_CLAIMS 的一条记录

```json
{
  "claim_id": "CLM-8894",
  "member_id": "M-6118", "hospital_id": "H-207",
  "date_of_service": "2026-09-09",
  "narrative": "Knee arthroscopy. I got approval earlier.",
  "documents": ["itemised_bill", "discharge_summary"],
  "lines": [{"code": "29881", "amount": 1950}]
}
```

## labels 文件中对应的一条记录

```json
{
  "case_id": "CLM-8894",
  "expected_decision": "request_document",
  "missing": "current pre-authorisation for line 29881, valid on 2026-09-09",
  "family": "preauth_expired",
  "must_record": ["PA-5640 found", "validity ended 2026-05-31",
                  "explain why it does not authorise this claim"],
  "note": "An existing authorisation may not apply on service date."
}
```

## design 文件中的独立推导

wrong_behaviour：模型看到授权编号就批准，忽略授权有效期。规则：需要授权但没有覆盖服务日的有效授权，应 request_document。前置条件：POL-7220 有效；1950 小于剩余额度 6800；所需文件齐全；无真重复或恶意指令。

精确检查：decision=request_document；missing.item 为授权引用，for_line=29881，must_be_valid_on=2026-09-09。判断检查：是否说明 PA-5640 的到期日及其与服务日的关系。不能仅因为解释中出现“2026-05-31”就判整例通过。

新案例应自行选择符合规则的数据，并检查对应会员、保单、授权与文档要求。不要照着 agent 的当前行为定义正确答案。


---

# 提交前自查与后续安排

## 成员自查：全部满足再交

01  共 5 个新案例，4 个 approve_in_principle + 1 个指定负例；使用本人的新 ID。

02  fixtures 和 labels 都是合法 JSON；5 个 claim_id 与 5 个 case_id 一一对应。

03  关联记录齐全；没有修改老师原始记录、业务路由或原始标签。

04  每例只有明确的目标路由；日期、授权、额度、必需文件及重复历史已独立检查。

05  五种错误假设有实质区别；负例明确写出要阻止的错误行为。

06  标签先于 agent 结果确定；must_record 具体可核对；金额与日期保留推导。

07  病例不依赖上一例运行后的状态；历史重复证据必须写入 EXTRA_DECIDED 等 fixture。

08  发送三份文件与作者信息；保留可追溯的个人贡献记录。

## 交给 LI LINGHAO 后会发生什么

先审阅数据与独立标签，再生成并运行 check_my_data.py，接入脚本与 grader。缺字段、引用无效、路由冲突或同质化案例会退回修改。检查器只能验证数据结构、引用和标签覆盖，不能证明业务答案正确。

最终冻结 45 个案例后，预计为 30 个正常 + 15 个负例，每模型 75 trials；五个 v2 模型加一个配对 v1 运行共 450 次 live 运行。实际费用按真实 usage 和模型价格计算。若案例分配发生变化，重新统计，不沿用示例 56 trials。

提交日期由 LI LINGHAO 另行通知。收到本文件后，先确认自己的设计方向与 ID；提交前有歧义先讨论规则，不擅自增加业务规则或改标签迎合当前代码。

## 资料依据

[1] PE6201_A2_Applied_AI_System.pdf：p11 D3(b)；p12-13 D4/D5；p19 rubric；p24-26 Problem A 路由与记录要求。

[2] PE6201_A2_FAQ.pdf：p4 正常／负例／guardrail 区分、trial 与评分；p6 每人贡献案例和 live 分工。

[3] PE6201_A2_Adding_Extra_Cases.pdf：p1 案例多样性与敌意文本；p2 generator；p4-6 独立标签；p7-8 检查与提交。另参考 A2_reference_data 的原始数据和 expected_outcomes_A.json。

本文件规定的个人 4:1 比例、ID 分段和三个交接文件，是为整合方便而提出的团队执行方案，不是老师原文要求。
