# Section 3 数据出处与整合说明

负责人：LI LINGHAO。正文依据 2026-09-18 已冻结的团队 D5 证据撰写。本次只生成报告文件并核算已有记录，没有调用付费模型、重跑 battery 或修改冻结成绩。

## 交付与使用

- [Report_SECTION3_LI_LINGHAO.docx](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/report_section3/Report_SECTION3_LI_LINGHAO.docx)：可直接并入团队 Report 的英文正文与 Table 3。
- [SECTION3_EN.md](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/report_section3/SECTION3_EN.md)：同一内容的可编辑 Markdown。
- [SECTION3_ZH.md](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/report_section3/SECTION3_ZH.md)：中文理解与核对稿，不加入正式英文 Report。
- [SECTION3_METRICS_AUDIT.json](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/report_section3/SECTION3_METRICS_AUDIT.json)：逐模型复算结果、分母、原始数据 SHA-256 与核验记录。

英文五段正文按空白分词计 **341 词**，不含标题、表格标题与表格。不要把这份核对说明加入 350 词正文。团队合稿时保留五段正文和 Table 3，并与 Section 2 的 v1/v2 结果、Section 4 的成本口径对齐。全文上限仍为 2,000 词。

## 与老师要求的对应

老师原始文件：[PE6201_A2_Applied_AI_System.pdf](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/materials/PE6201_A2_Applied_AI_System.pdf)。

| 页码 | 要求 | 本节落实 |
|---|---|---|
| 12 | 普通案例一次、负例三次；通过率带试验数；v1/v2 固定同一模型 | 30 + 15 × 3 = 75；表格逐项给分母；ZHOU 的 DeepSeek v1 单列 paired |
| 13 | 代码检查与判断检查区分；judge 必须与被测模型不同 | 代码与综合通过分列；live 统一 judge 为 openai/gpt-4.1-mini |
| 13 | scripted 无网络、无密钥；live 比较相对表现 | scripted 75/75 只作为整合复现证据，未称为 live 准确率 |
| 14 | 六人五个模型家族使用同一 v2；第六人为 v1 对照 | 五个 v2 家族加 DeepSeek v1；不是六个不同模型 |
| 14 | 表格呈现所有模型，正文分析差异、负例与成本两端 | Table 3 全部配置；正文聚焦 DeepSeek 与最昂贵的 Claude，并解释低分协议失败 |
| 18 | Section 3：D4 + D5、通过率、模型分歧、负例发现；约 350 词 | 英文正文 341 词；表格不计入正文预算 |

没有找到预先约定的模型整体部署通过率阈值，因此正文没有事后创造“达到 90% 即可部署”等标准，也没有称某模型获得生产部署资格。最便宜的配置与可靠性最佳配置并非同一个；正文据实比较，不把成本最低等同于可用。

## 数据口径

1. **Case 与 trial**：45 个不同案例 = 30 个团队原创 + 15 个教师参考。团队原创部分有 6 个负例，参考部分有 9 个负例。不能写成“45 个案例全部由团队原创”，也不能写成“75 个不同案例”。出处：[案例来源 manifest](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/integration/merged_A/manifest.json)、[标准答案](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/integration/merged_A/expected_outcomes_A.json)。
2. **综合通过**：`code_passed == true` 且 `judgement == "pass"`。执行失败、判断 fail 和 uncertain 均不计通过。判断通过本身不能覆盖代码失败。
3. **Live 分母**：每位成员都是 75 次。所有六种配置合计 203/450（45.1%）代码通过、200/450（44.4%）综合通过、237 次执行失败。这个汇总混合五个 v2 与一个 v1，不能当作任何单个部署模型的成功率。
4. **仅 v2 比较**：139/375（37.1%）代码通过、136/375（36.3%）综合通过；普通案例 67/150（44.7%），负例 69/225（30.7%）。正文主张依赖逐模型数据，未将 pooled 分数解释为模型能力排名。
5. **judge 完成与 uncertain 不同**：213 次可审查 trial 的 judge 调用全部完成，调用错误及待调用数为零。LI 的 CLM-8933 trial 3 有一个 criterion 为 uncertain，trial 字段表现为 `judgement: pending`；这是内容层面不确定，不是漏跑 judge。因此 LI 为 **71/75**，不是早期的 72/75。
6. **成本**：表中为 75 次正式 agent 试验的 API token 数乘冻结输入/输出单价，含失败试验的已记录 token；不是供应商发票、每次成功成本或完整 cost-to-serve。排除 preflight、诊断、历史重跑、judge、人工兜底与固定月度开支。Claude 1.356233 美元高于其他正式 battery。D6 的完整成本另由 Section 4 解释。
7. **两种 scripted 结果**：[D5a code summary](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/results/d5a_v2_summary.json) 为 75/75 代码通过；[历史 D5a judge summary](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/results/d5a_judge_summary.json) 另记录 Claude Haiku 对该 scripted 输出的 75/75 判断通过。后者需要联网和费用，不属于默认无密钥执行过程。英文正文只引用免费 scripted code 结果；不能把当前录屏重新生成的 pending judge 结果说成已经独立判断通过。
8. **重复试验解释**：负例重复三次不等于新增三个不同案例。本文报告同一负例三次均通过的稳定性指标，但不将这些相关试验冒充更大的独立样本，也未宣称 v1/v2 差异达到统计显著。

## 模型标识与精确金额

| 负责人 | OpenRouter model ID | Prompt | 综合通过 | 负例三次均通过 | Agent cost US$ | Judge cost US$ |
|---|---|---|---|---|---|---|
| LI_LINGHAO | `deepseek/deepseek-v3.2` | v2 | 71/75 | 13/15 | 0.282861170 | 0.082051 |
| CHEN_MINGSONG | `google/gemini-2.5-flash-lite` | v2 | 3/75 | 1/15 | 0.147102500 | 0.004757 |
| LU_XINZE | `qwen/qwen3-235b-a22b-2507` | v2 | 11/75 | 0/15 | 0.072874112 | 0.014962 |
| WANG_YI | `mistralai/mistral-small-3.2-24b-instruct` | v2 | 23/75 | 0/15 | 0.086623094 | 0.030585 |
| DAI_MINFEI | `anthropic/claude-haiku-4.5` | v2 | 28/75 | 4/15 | 1.356233000 | 0.038666 |
| ZHOU_SIHAN | `deepseek/deepseek-v3.2` | v1 | 64/75 | 11/15 | 0.291398606 | 0.072223 |

完整冻结结论：[D5_FINAL_REPORT.md](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/D5_FINAL_REPORT.md)。绑定与版本解释：[HASH_AND_VERSION_BINDING.md](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/HASH_AND_VERSION_BINDING.md)。模型清单、来源 ZIP 与 judge 路径：[D5_EVIDENCE_MANIFEST.json](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/D5_EVIDENCE_MANIFEST.json)。

## 正文案例与可核验记录

| 正文发现 | 证据位置 | 解读边界 |
|---|---|---|
| Mistral CLM-8925 trials 2、3：决定与触发器正确，但把 11,400 写成 13,200；代码通过、judge fail | [WANG_YI · results.json](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/suites/WANG_YI/suite/llm_judge_e5533a954891/results.json)；[WANG_YI · model_reviews.csv](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/suites/WANG_YI/suite/llm_judge_e5533a954891/model_reviews.csv) | 数据输入仍是 9,800 + 1,400 + 200；模型把错误总额传给 lookup_policy，并在 reason 中重复。不是数据集被改成 13,200 |
| Claude CLM-16105 trials 1、2、3：请求有效授权正确，但未通过文件检查证据规则 | [DAI_MINFEI · results.json](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/suites/DAI_MINFEI/suite/llm_judge_cc6ec39749f7/results.json) | `29881: missing check_documents`；不是“Claude 批准了过期授权”。这是当前 harness 的严格证据要求 |
| Qwen 51 次自行生成 Observation，被协议拒绝 | [LU_XINZE · results.json](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/suites/LU_XINZE/suite/llm_judge_0afe343b1754/results.json) | 计数依据精确 error 字段；其他 10 次执行失败有其他原因，不能全部叫 Observation 伪造 |
| Gemini 70 次执行失败，含四次 step cap | [CHEN_MINGSONG · results.json](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/suites/CHEN_MINGSONG/suite/llm_judge_0bc6ef30c084/results.json)；[CHEN_MINGSONG · summary.json](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/suites/CHEN_MINGSONG/suite/llm_judge_0bc6ef30c084/summary.json) | 5 次可审查 trial 中仅 3 次代码通过；低分不是只由一个原因导致 |
| DeepSeek CLM-8933 trial 3 不确定，不计入通过 | [LI_LINGHAO · model_reviews.csv](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/suites/LI_LINGHAO/suite/llm_judge_d85d3ccf6936/model_reviews.csv)；[LI_LINGHAO · results.json](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/d5_team_review/final_freeze/suites/LI_LINGHAO/suite/llm_judge_d85d3ccf6936/results.json) | judge 认为重复理赔匹配的四项事实证据不足。其他重复 trial 被判通过，说明 judge 本身存在判断差异，不应包装为绝对真值 |
| 同一负例三次均通过：LI 13/15、ZHOU 11/15、CHEN 1/15、LU 0/15、WANG 0/15、DAI 4/15 | [复算 JSON](/Users/llh/PycharmProjects/C-PE6201-Group-6-A2/Part3_LI_LINGHAO/report_section3/SECTION3_METRICS_AUDIT.json) 与上述每位 results.json | 分母是 15 个负例，不是 45 个负例 trial；单次通过不等于重复稳定 |

## 本次核验范围与限制

已重新读取六位成员的原始 results、独立 judge results、summary 和 metadata，逐项核对 75 个唯一 case/trial、45 个 case、30/45 普通与负例试验、代码分数、综合分数、执行状态、judge 完成数和 API 成本之和。已确认 judge 结果保留的 record 与原始 trial record 相同，且代码分数未改变。

六位成员记录的 implementation、dataset、rubric、scripted library 哈希一致；Windows 路径分隔符仅在比较内正规化，没有修改源文件。所有数字来自已冻结结果，详见复算 JSON 内的 `source_sha256`。

研究限制仍需保留：人工构造小样本、教师参考案例可见、单一 live judge、严格工具证据与 ReAct 协议会影响成绩、不同日期/API 路由与随机性未形成完全控制实验。因而正文只说“observed improvement”，不宣称提示词修改已被严格证明具有确定因果效果，也不把这些结果外推为通用模型排名。
