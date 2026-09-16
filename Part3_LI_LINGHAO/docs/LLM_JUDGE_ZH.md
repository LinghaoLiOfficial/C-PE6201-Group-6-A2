# 使用第二个模型完成 judgement check

本阶段改用 `anthropic/claude-haiku-4.5`，不再要求逐行人工填 CSV。
当前被评分的是 v2 scripted acceptance 的 75 次已保存运行，agent 本身没有调用 LLM。
Judge 则通过 OpenRouter 真实调用。之后评分 live agent 时，代码拒绝 judge 与 agent
使用同一模型。不同 agent 的比较应固定同一个独立 judge；若 agent 恰好使用该 judge
模型，需要另选 judge，不能让模型给自己评分。

## 评分材料和规则

- `integration/judge_prompt.md` 是版本控制中的评分提示词。
- 每次调用提供一次 trial 的实际 reason、结构化决定、决定日志、真实工具 trace 和
  对应 must_record，不向 judge 提供审查程序计算出的答案。
- 每条要求返回 pass、fail 或 uncertain，并附理由及证据引用。
- 中文理由是提示词偏好；模型可能返回英文理由，两者均保留原文。
- 每次 trial 单独评分，包括负面案例的三次重复，完全不传播第一次的结论。
- 全部条目 pass 才算 judgement pass；任何条目 fail 则该 trial 失败；uncertain
  在没有其他 fail 时保持 pending。代码通过且 judgement 通过才计综合通过。
- 无效 JSON、缺少条目、重复 ID、无理由或调用错误不会被算作通过。
- claim narrative 与 agent 输出均视为不可信数据，不能改变评分指令。

## 运行与续跑

在仓库根目录执行：

```bash
python3 Part3_LI_LINGHAO/scripts/run_llm_judge.py \
  --suite Part3_LI_LINGHAO/output/d5a_acceptance/suite-com7qgsg
```

默认模型为上述 Haiku，标价输入 $1、输出 $5 / 百万 token，费用上限 $2。
该价格已于本次运行前通过 OpenRouter models API 查询；未来运行请重新核价，并用
`--price-in`、`--price-out` 指定。Key 从环境变量或本工作区的 `.env` 读取，不写入日志。
预算按保守输入估算预留，实际结算估算采用 provider token usage；缓存优惠可能使
实际账户收费更低。Judge 费用与 scripted agent 的合成费用分开报告。

重复命令会复用同一输入、提示词、模型及价格对应的已保存调用，避免重复收费。
断点续跑不自动重试已记录的失败调用。只解析一次完整 JSON 或一个完整 JSON 代码块，
不会从散乱文字中捞出一个答案。接口若返回不符合提示词的代码块但 JSON 有效，可在
本地重新解析，保留原始回复并记录 reparsed_locally。

`--max-calls 0` 可不使用 key、不联网重建已有评分汇总。缺少调用仍保持 pending。
`--max-calls 1` 可先运行一例。普通 D4 harness 默认仍为完全离线 scripted，评分命令
是独立入口，不会因运行 D5(a) 自动花费 judge API 费用。

## 结果与下一步

suite 下的 `llm_judge_*` 目录包含：

- `REPORT.md`：评分概览及所有 fail/uncertain 原因。
- `model_reviews.csv`：自动填写的逐条评分，包含 judge 身份、理由和引用。
- `results.json` / `results.csv` / `summary.json`：加入模型判断的完整结果。
- `call-*.json`：每次真实请求、原始响应、usage、时间、费用及解析状态。
- `judge_config.json` / `judge_prompt.md`：模型、价格、提示词和输入哈希。

原 suite 的人工待审结果保留不变；使用新的 judge 目录中的结果作为模型评分版本。
不用把模型结果冒充人工姓名导入原表。如果 judge 判 fail，保留真实结果，在修复 agent
后创建新的 suite 重新评测；不要修改 verdict 来提高通过率。

LLM judge 是可记录但非绝对可靠的测量工具，可能误读或给出不准确的证据索引。
不能把自动判断写成“人工审阅通过”。可对失败项和少量通过项做抽查来校准 judge，
但本流程不要求先手工填完 263 行才继续。

## 本次真实结果

75 次 judge 调用完成，263/263 条要求被该模型判为 pass；无 fail 或 uncertain。
Code check 75/75，judgement 75/75，综合通过 75/75。输入 172,660 tokens，
输出 35,248 tokens，按标价估算 $0.3489。原始评分响应保存在
`results/d5a_judge_evidence.zip`，可审计而不必重新调用付费 API。
汇总为 `results/d5a_judge_summary.json`，逐项表为
`results/d5a_judge_model_reviews.csv`。这些都是 scripted 输出的第二模型评分。
