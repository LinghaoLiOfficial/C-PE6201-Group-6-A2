# Layer 3 负责人批准的固定月度成本

**负责人：** LI_LINGHAO  
**批准日期：** 2026-09-19  
**状态：** A2 D6 的情景假设，**不是实测生产账单**。

## 决定

Problem A 的 Layer 3 基准值采用 **US$200/月**。它只在月度公式中加一次：

```text
monthly total = (Layer 1 + Layer 2) × 8,000 claims + Layer 3
```

US$200 的组成是：hosting/runtime $80、logs and retained evidence $20、monitoring/alerting $30、storage/backups $20、evaluation/regression $30、maintenance/fixed software $20。按 8,000 claims/月分摊，相当于 **US$0.025/claim**。

## 证据边界

当前仓库没有生产 hosting 账单、存储发票、监控订阅、数据库/vector-store 合同或固定软件合同。因此不能把 US$200 写成 measured production spend。D5 的 agent、preflight 和 independent judge API 费用仍单独保留为实测证据；人工失败处理成本属于 Layer 2，每次 US$7.60（`$38/hour × 12/60`）。

## 敏感性情景

D6 应同时展示 **$0、$100、$200、$500、$1,000/月**。其中 $0 只表示原型范围内没有增量固定现金承诺，不表示未来生产部署免费。

## 运行边界

8,000 claims/month 是 Problem A 的规划量，不是已测得的容量上限或硬性用户配额。若采用其他月度量，必须重新计算。已冻结的运行控制为 8 个响应轮次 step cap、每 trial $0.05 guardrail 和每成员 battery $3.00 ceiling。
