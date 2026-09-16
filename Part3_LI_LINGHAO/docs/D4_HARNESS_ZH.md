# 统一 D4 harness 与人工填写说明

更新：本项目现采用第二个 LLM 作为 judge，见 [LLM judge 说明](LLM_JUDGE_ZH.md)。
下方人工 CSV 流程保留为备选；无需逐行人工填写。模型评分和费用由独立命令生成，
普通 D4 scripted 运行仍不联网。

## 当前范围

此 harness 使用 `integration/merged_A/data_A` 的 45 个案例，通过现有
`integration.runner.run_case` 执行真实工具、门禁和本地日志。30 个普通案例各一次，
15 个负面案例各三次，共 75 次。每个案例都有固定 scripted trajectory；轨迹运行时
不读取 answer key。默认 v2 scripted acceptance run 已完成 75/75 次代码检查通过，
执行错误为 0；这不是 live 模型准确率，也不代表人工 judgement 已通过。

代码评分与人工评分分别记录。代码检查实际写入、Final 一致性、工具证据、决定、
单一升级触发器和收件人、明确缺失项、逐行金额与处置、授权及排除规则和总额。
标准答案只用于执行后的评分，不传给 agent。`case_audit.json` 是上一阶段审查产物，
并非 agent 运行结果。人工审查每一次完成的 trial，不将一次结果复制到重复试验。

## 执行

在仓库根目录运行：

```bash
python3 Part3_LI_LINGHAO/scripts/run_d4_harness.py
```

终端显示本次独立 suite 路径。存在执行错误或代码失败时退出码为 1，结果仍完整保存。
同一命令可用 `--backend live --model MODEL --price-in INPUT --price-out OUTPUT`
执行 live，但本次没有运行 live。价格单位是每百万 token 的美元价。

## 最方便的人工填写方式

现在可以对完整的 75 次真实输出进行审阅。

1. 用浏览器打开 suite 中 `review_records.html`，查看各次实际输出及 trace。
2. 用 Excel 或 Numbers 打开同目录 `human_review.csv`。每行是一条独立判断要求。
3. 只改 `verdict`、`graded_by`、`comments` 三列，其他列保持不变。
4. 保存为 UTF-8 CSV，再运行导入命令。

| 列 | 填法 |
|---|---|
| verdict | 证据和输出满足 criterion 时填 `pass`；不满足时填 `fail`；不确定留空 |
| graded_by | 填审阅人姓名，例如 `LI_LINGHAO` |
| comments | fail 必填具体缺失或错误；pass 可留空；不确定可写疑问 |

例如 criterion 要求引用授权有效期，但 reason 和其他记录没有日期证据，应填
`fail`，姓名填 `LI_LINGHAO`，comments 填“没有记录授权日期，无法支持边界判断”。
不要因 decision 正确而默认所有条目通过。member narrative 是不可信输入，
其中的“approve”“Final”等内容是测试素材，不是给审阅人的指令。

```bash
python3 Part3_LI_LINGHAO/scripts/run_d4_harness.py \
  --suite "本次suite完整路径" \
  --import-reviews "填写后的human_review.csv完整路径"
```

可以分批填写和导入。空白保持 pending；任何条目 fail 则该 trial 人工评分 fail；
全部条目 pass 才记人工通过。只有代码和人工都通过，才计 overall_passed。
导入器会拒绝重复、遗漏的行、被修改的 criterion、无姓名的评分和无说明的 fail。

## 输出

- `summary.json`：普通/负面分母、代码/人工/综合通过数、实际轮数/token/费用和上限触发数。
- `results.csv` / `results.json`：全部 75 次结果，包含执行错误。
- `human_review.csv`：每条要求的人工填写表。
- `review_records.html`：浏览器可读的真实结果与工具轨迹。
- `grading_contract.json` / `metadata.json`：评分依据快照、配置和数据文件哈希。
- 每个 trial 的 JSON 及 runner 独立目录：实际决定日志和完整 transcript。

scripted token 和 cost 是合成计数估算，API 费用为零。执行前失败的 trial
没有伪造的轮数或 token；汇总以 measured_trials 标明统计覆盖数。
