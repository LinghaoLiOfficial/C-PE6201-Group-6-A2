# D5 全员交付审查（2026-09-18）

审查快照：main / cff4286（完整 SHA 见 audit_results.json）。已 fetch 并快进本地 main。
所有可见远程分支均没有尚未纳入 main 的提交，因此缺失的正式结果不是隐藏在这些分支中。
原有未跟踪旧交付目录和 ZIP 保留不动。本次仅检查，没有付费运行模型、重新评分 judge、
改写队友原始结果或向队友发送通知。

## 结论

不能宣布全员 D5 已完成。三份新版正式 battery 已交付，另外两份只有完整预检，一份预检中断。
无需让已完成者为了提高通过率修改输出或重跑。可以并行推进已交付结果的独立 judge，
同时让未完成成员补齐阶段性任务；暂时不能形成完整五模型 v2 排名。

| 成员 | 仓库实际状态 | 代码检查 | 是否反馈 / 下一步 |
|---|---|---|---|
| LI_LINGHAO | revision 1.1 正式 75 次；独立 judge 已完成 | 72/75；综合 72/75 | 无需重跑，可作为已完成交付 |
| CHEN_MINGSONG | revision 1.1 正式 75 次，证据完整 | 3/75；5 条待 judge，70 条不可审阅 | 不因低分返工；由协调人评分全部 5 条可审阅记录 |
| ZHOU_SIHAN | revision 1.1 正式 75 次，证据完整 | 64/75；64 条待 judge，11 条不可审阅 | 不重跑；由协调人评分，再做 DeepSeek v1/v2 对比 |
| LU_XINZE | 仅 6 次完整预检，无 release / 正式返回 ZIP | 0/6 | 需反馈任务未完成；确认余额并放行后执行首次正式 75 次 |
| WANG_YI | 仅 6 次完整预检，无 release / 正式返回 ZIP | 1/6 | 需反馈任务未完成；确认余额并放行后执行首次正式 75 次 |
| DAI_MINFEI | 预检中断，仅 2 条 result；无 preflight.json | 0/2，不能称为完整六案例预检 | 需反馈：补查中断、保留旧输出，经协调后开展新诊断预检；尚不能 full |

## 核验范围与证据

审查程序 audit.py 读取原文件及 ZIP，不修改交付。审查了原始个人包 assignment 和 manifest、
预检案例集合/原始 run 记录、正式 45 案例和 75 个唯一 case/trial 对、每条结果与独立
case 文件及 run/result.json 的一致性、transcript 存在性、公共代码/数据/判据哈希、
release 与预检/包的哈希绑定、模型/descriptor/backend、8 轮和 US$0.05 上限、
按配置价格计算的 token 成本、dispatch 总额及原始 summary。使用公共 code_check 对
全部 225 条正式记录逐条复算，与保存的 failures 和 code_passed 一致。

三份正式提交以上检查均通过，审查结果 findings 为空；公共版本 13 项回归测试通过。
Windows 数据路径反斜线仅在比较哈希键名时标准化；不同 Python 浮点求和的尾数误差
按 1e-9 容差比较，原始证据没有修改。ZIP 中未检出 OpenRouter key 格式。

这说明提交内部一致且符合当前冻结接口，不是对远程模型身份、未记录的额外尝试或账单的
独立证明。现有元数据中的模型、运行代码哈希属于运行方记录；没有重新付费复现。
本次也没有逐条人工审判语义：CHEN/ZHOU 的语义检查应由统一第二 LLM 接续完成。

## 完整 battery 的质量

CHEN：33 条 error、32 条 not_recorded、5 条 completed、4 条 step cap 停止、
1 条 completed_with_tool_issues。普通 0/30，负面 3/45。3 条代码通过均为
CLM-16305 的三次试验。其余两条 completed 仍未通过代码检查，但依规则也要 judge。
Final 中 Python None / 单引号、Action 与 Final 同轮、空 reason、缺少逐行处置等
是当前明确公共契约下的真实失败。公共 prompt 已明确 Final 必须为 JSON、不得伪造
Observation、Action 与 Final 必须分轮，没有发现需要专门给 Gemini 改判据的理由。
正式 agent 标价估算 US$0.1471025。3/75 是代码通过率，不是最终综合成绩。

ZHOU：64 条 completed、9 条工具问题、2 条解析 error；普通 25/30、负面 39/45。
正式 agent 标价估算 US$0.291398606。其 Part2_ZHOU_SIHAN/D5_results 是旧版本历史
证据，不能拿来替代 Part3_LI_LINGHAO/d5_live_submissions/ZHOU_SIHAN/r1.1 的新结果。
新版与 LI_LINGHAO 使用同一 DeepSeek 模型及公共 revision，仅 descriptor v1/v2 不同。
judge 完成前不能将 64/75 直接称为综合通过率。

CHEN 和 ZHOU 均说明 release 由成员本地生成，依据协调人的微信指令。
哈希绑定检查通过，但 reviewed_by=LI_LINGHAO 字段本身不能证明是谁实际审批。
建议协调人在最终审计说明补充一次真实的事后确认（日期、适用成员、是否确有该授权），
不要修改原 release，也不需要仅因该来源说明重跑。若授权事实存在争议，另作偏差说明。

## 未完成成员的具体反馈

LU：六条预检均有真实响应且 transport_ok=true，均因模型生成 Observation 被拒绝；
这不是六次 API 不通。预检估算 US$0.0057162，预计 agent 总额 US$0.12504804375。
确认运行环境和余额仍有效、价格校验通过后，可协调放行首次完整 battery。
如本人声称已跑 full，应先提交已有原始 suite/返回 ZIP，而不是再次跑。

WANG：六条预检 transport_ok=true，1 条代码通过；其余为 Action/Final 混合、
未写入和语法错误。预检估算 US$0.007353875，预计 agent 总额 US$0.1685860625。
处理方式同 LU：先确认是否有未上传 full；没有则放行后首次执行。Part8 下旧预检不替代
新版正式结果。低预检分数不是无限重跑或个人修改 prompt 的理由。

DAI：完整记录为 CLM-8842（Action/Final 同轮，error）和 CLM-8888（not_recorded）；
第三个 run 仅有空 decisions.jsonl，没有 result/transcript，不能推断后续成功。
已记录成本 US$0.035591，第三次是否发生付费调用未知，不能按零认定。
要求反馈终端最后输出、退出情况、环境及余额（不含 key）。当前没有 preflight.json，
无法生成绑定该预检的正常 release。保留本次中断证据，修复执行环境或解释中断后，
由协调人批准新的六案例诊断尝试；不要伪造剩余记录，不以两条结果代替六案例预检。
DAI 文件放在本人 Part4 名称工作区可以审查，不应仅为路径不同要求重跑。

## 推荐推进顺序

1. 给 LU、WANG、DAI 发阶段性反馈，优先询问是否有完成但未上传的原始结果。
2. 对 CHEN 的 5 条和 ZHOU 的 64 条可审阅记录运行统一 GPT-4.1 mini judge，
   保留各自完整 75 分母；不对不可审阅记录制造通过。
3. 放行 LU/WANG 的首次正式运行；处理 DAI 中断再预检/放行。额度与模型价格运行时再核对。
4. 收齐五模型 v2 和 DeepSeek v1 的六份完整 battery，再做总表、v1/v2 及负面案例差异分析。

当前 CHEN/ZHOU 的 pending 不是需要成员人工填写 judgement 的缺陷。可以开始以上下一步，
但不能跳过其余三人的缺失正式实验，也不能把预检的六行补成正式 75 行。
