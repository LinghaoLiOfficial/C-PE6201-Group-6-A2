# D5 live 执行分发说明（LI_LINGHAO）

你负责 D5 的协调、harness、scripted、收集和汇总；live 执行由全员参加。此前把 D5(b) 单独交给 DAI 的建议不准确：团队声明中 DAI 负责 D6，D5(b) 是 Everyone。

## 已分配的六个任务

| 成员 | 模型 | 版本 | 工作 |
|---|---|---|---|
| LI_LINGHAO | DeepSeek V3.2 | v2 | 廉价基线 + 总协调 |
| ZHOU_SIHAN | 同一 DeepSeek V3.2 | v1 | 与 LI 的 v2 配对，完成 D2(b) 对照运行 |
| CHEN_MINGSONG | Gemini 2.5 Flash Lite | v2 | live battery |
| LU_XINZE | Qwen3 235B A22B 2507 | v2 | live battery |
| WANG_YI | Mistral Small 3.2 24B | v2 | live battery |
| DAI_MINFEI | Claude Haiku 4.5 | v2 | 中价层 live battery，同时接收团队成本数据用于 D6 |

老师建议六人采用 5 个不同家族的 v2 模型 + 1 次相同廉价模型的 v1 对照。不能把 v1 放进 v2 五模型排名。五个模型包含廉价层与中价层；价格层级是本团队的预算分组，实际价格见 MODEL_ASSIGNMENT.csv。模型 ID 和价格已查询公开目录，但尚未进行付费 API 兼容性验证。

每人正式 75 次（30 普通 + 45 负面），六人合计 450 次；每人另做三种结果各一次预检，团队另有 18 次诊断，不加入正式分母。保留原冻结的 15 个老师案例 + 30 个队员案例，不再重新设计案例。

## 你现在怎么做

1. 从 packets 发给各人自己的 D5_姓名.zip。包内已有代码、固定案例、实名配置、英文步骤与中文速查；不要求他们先获取尚未 push 的新文件。
2. 你先用自己的 ZIP 做 verify、offline、preflight；其他成员随后做同样预检。密钥由每人自己在隐藏输入框填写，无需发给你。尚未执行任何付费 live 调用。
3. 收齐 preflight 文件夹及剩余额度数字。检查通信/token、解析、工具与门禁日志、上限和费用；答错属于实验结果，不要求预检全过才准测试，不删失败案例、不刷分。
4. 在对应成员解压包中，按 README_EN 的 release 命令生成离线放行文件 release.json，再发回成员。USD 3 预测门槛只是本包协调策略；三案例外推并不保证实际账单，必须包含此前重试等支出。
5. 成员按包内 full 命令跑完整 75 次，按 pack 命令回传 D5_RETURN_姓名.zip。中断要保留部分结果，不能悄悄重跑。
6. 由你统一使用 GPT-4.1 mini 对每个新的 live 输出做第二模型 judge，与全部被测模型都不同。包内有命令；先试 3 个 judge 请求，再按相同参数继续。每套先设 USD 0.50 评分预算，实际剩余额度不足或评分 pending 时先评估，不自动增加预算。judge 开销与 agent 开销分开。
7. 汇总五模型 v2 表与 DeepSeek v1/v2 表，把成本字段交 DAI、报告图表交 WANG。让每人根据真实 case/trial 写差异观察。

## 验收与限制

代码、数据、prompt、gate 和上限都使用冻结字节，未改原 release/tag。新增的是外层分发脚本。正式 run 的 code pass 不等于最终 overall pass；judge pending/error 不计通过，失败和未执行行不从 75 分母剔除。

日志真实保存在 run-* 子目录；工具顺序、上限、usage 等在 results.json 的 record 内；家族/价格层在 assignment.json。不要要求原 results.csv 存在它并未实现的列。第二模型评分结果输出到独立 judge 子目录，源记录保留。

现有 trial 费用上限在一次响应之后判断，新增成员总预算在 trial 间判断，不能保证 API 账单硬封顶；通信错误可能有未测量费用。价格变更、模型不可用、普遍接口问题先通知你，不能成员各自改 prompt/model。若需要改共用实现，应统一发新版本并重新预检。

完整英文流程、资料页码、放行及 judge 命令见 README_EN.md。生成包的公开目录快照与单一分配源保留在本目录，方便追溯。
