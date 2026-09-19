# D6 交接说明（DAI_MINFEI）

你的任务是完成 Problem A 的 D6 cost-to-serve model。无需重新运行 D5，也不要使用 API key。

请阅读 `materials/PE6201_A2_Applied_AI_System.pdf` 第 17-18 页和 Class 5 notebook。必须报告三层成本：每任务变量成本、预期 fallback 成本、固定月度成本。负责人已批准 Layer 3 基准情景为 **US$200/月**；这是情景假设，不是实测生产账单。请阅读 `D6_OWNER_DECISION_EN.md` 和 `D6_OWNER_DECISION_ZH.md`。Problem A 默认值为每月 8,000 个 claims，单次失败人工处理成本为 US$7.60（US$38/小时 × 12 分钟 ÷ 60）。

必须用 D5 的实测 token、turn 和 success 数据，并报告四个 measured levers：tool block、turn count、observation size、success rate。还要给出 sensitivity、cheap-model break-even、step cap、budget ceiling 和 monthly limit。

`reference/D5_COST_INPUTS.json` 已整理六个模型的冻结 D5 数据。仍需向 CHEN_MINGSONG 获取 D2(a)/D2(c) 测量，向 ZHOU_SIHAN 和 LU_XINZE 获取 D2(b) descriptor/observation 测量，Layer 3 基准已经由负责人确定为 US$200/月，并须展示 $0/$100/$200/$500/$1,000 的敏感性。若以后获得真实账单，应引用来源后替换情景；当前值不能改写成 measured。缺失数据必须标为 unavailable，不能编造。

请在 `Part4_DAI_MINFEI/D6/` 提交 cost calculator、CSV ledger、sensitivity、D6_REPORT.md 和 D6_OBSERVATIONS.md，创建目标为 `main` 的 Pull Request，并把 PR 链接发给 LI_LINGHAO。不要提交 API key 或 `.env`。
