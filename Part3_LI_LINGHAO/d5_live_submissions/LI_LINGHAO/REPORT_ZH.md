# LI_LINGHAO：DeepSeek v2 live 运行结果

已完成 3 次独立预检、75 次正式 live 试验，以及全部 65 个可审阅记录的 GPT-4.1 mini judge 调用。
本次是固定版本的真实测量，不是通过验收的声明。

| 指标 | 结果 |
|---|---|
| 正式试验 | 75/75，45 个案例 |
| 严格代码检查 | 12/75（16%） |
| 顶层 decision 一致 | 70/75，仅辅助指标，不能替代通过率 |
| judge | 59 通过、3 失败、3 不确定；另外 10 条不可审阅 |
| 代码 AND judge | 10/75（13.33%） |
| 普通 / 负面综合通过 | 0/30；10/45 |
| 执行状态 | 65 完成、5 有工具问题、5 解析错误 |
| 轮数 | 共 389，中位数 5，最大 7 |
| Agent tokens | 输入 683234；输出 53053 |
| 上限 | 未触发 step cap 或 trial budget；没有跳过 trial |
| 费用（统一标价） | agent $0.205011，预检 $0.007809，judge $0.070066；合计 $0.282886 |
| API usage 返回费用合计 | $0.199815；不是独立账单核验 |

## 必须说明的评测问题

1. 模型有真实协议错误：Action/Final 混合、无效 Python/JSON 字面量、工具异常；原始输出均保留。
2. prompt 没有枚举 line.status 的 allowed values，评分器却要求 covered/not_covered；模型使用 approved/refused 时严格失败，即使决定和金额正确。匹配机制还会连带报 code/amount 错误。
3. 输出有 human_claims_assessor 与 human claims assessor 的字段差异；request_document 也常缺逐行处置信息。
4. judge 对部分旧判据有疑似歧义：CLM-8925 的“no lines individually priced”被解释成输入里不能有金额；CLM-8952 提到了整合接口中不存在的 check_coverage。原评分不被私自改成通过。

因此，应先与团队统一澄清输出契约和判据，再决定是否创建新的公共版本重跑。不要让成员分别修补 prompt，也不要把本次低严格通过率解释为同等比例的保险业务判断错误。本次旧版本证据永久保留。

## 交付

原始 75 次证据在 D5_RETURN_LI_LINGHAO.zip；独立评分在 judge/；成本见 cost_ledger.json；诊断与英文观察见 diagnostic_summary.json、OBSERVATIONS.md。
源 summary.json 保留 judge pending，最终合并结果以 judge/summary.json 为准。
3 条 uncertain 保留 pending，不算通过；10 条不可审阅仍计入 75 分母。

跨模型差异与 DeepSeek v1/v2 比较需要其他成员回传，当前尚不能完成。你的个人运行及原始评分已完成，但团队级 D5 汇总与契约问题澄清仍待完成。
