# 中文代码导读

## 先理解一条数据流

`run_eval.py` 选择案件和 trial → `agent.run_case` 创建隔离会话 → backend 提议工具调用 → 主循环检查上限、去重、同轮依赖 → `ToolSession` 查询真实 JSON → 观察返回模型 → 模型提议 decision → 独立校验及确认门 → 本地 ledger → harness 对比独立答案。

只有 `claim_agent/harness.py` 读取答案键；agent/backend 不读取。scripted backend 按工具观察决定下一步，供教师离线复现。live backend 调用真实模型，它的表现必须单独测量。

## 六个工具

1. `get_claim`：读案件、判断严格重复，标识已知 narrative 注入形式。
2. `lookup_policy`：由案件找到会员和保单，检查状态、日期和剩余额度。不能由模型随便提供低金额绕过校验。
3. `check_coverage`：逐代码查排除规则和必需文档；只有前一轮已经查保单才能调用。
4. `get_preauthorisation`：只查确实需要授权且未排除的 procedure，返回所有候选及有效性；存在不等于有效。
5. `get_hospital_status`：返回 panel 状态。非 panel 本身不是升级条件。
6. `issue_decision_letter`：名字代表业务动作，实际上只验证并写一条 JSONL，不生成信件、不发送邮件。

## 主循环与安全

每次 backend 响应算一轮，包括提出写入以及被拒绝的响应。多个独立工具可在同一响应中调用，减少模型重复阅读历史的次数。工具读取本身按确定顺序执行，不声称并发磁盘加速。

默认最多 10 轮，因为完整串行合法路径最长 9 轮；默认 60,000 token 上限。真实运行还受美元预算控制，已经发出的请求不能撤回，因此 runner 会预留一笔在途费用。live 格式/依赖错误最多给两次反馈修正，不能无限重试。

核心默认没有人工批准，`confirm` 会阻止写入。评测脚本明确注入模拟确认回调，以验证正常业务路径；这不是六位成员真实审核。确认对象为已验证决策的副本，不能在回调中偷改批准金额。

所有案件和 trial 使用独立 ledger。持久 ledger 的文件锁加重复检查避免不同会话重复写同案。金额使用 Decimal 校验，不接受负数、布尔值、NaN 或超过分的精度。

## 如何读评测

```bash
python3 run_eval.py
python3 run_eval.py CLM-8894 --demo
python3 scripts/reproduce.py
```

40 案中 12 个负例各运行三次，28 个普通案运行一次，共 64 trials。`grade.pass` 不是只看 decision：还对比精确升级原因、缺失项、各行状态、金额、工具证据和 gate。自由文字是否解释充分另交不同模型 judgement，不能用关键词出现代替语义判断。

`results/live` 是正式真实实验；`pilot_initial` 和 `pilot` 是开发试跑，不能混入正式通过率。所有模型比较使用同一冻结版本，失败也保留。来源指纹用于发现代码或数据漂移。

## 两项失败实验如何答辩

- 循环：同一个重复 get_claim 的故障 backend；有去重时第二轮停止，删掉去重则一直到 step cap。两边都不完成任务；差别是多花了多少轮、token 和估算成本。
- 接口：只删除授权有效性投影，使已过期授权被呈现为可用。scripted planner 提议批准，但独立写入校验挡住。恢复后正确请求授权。应说“出现并被阻断的不安全提议”，不能说“已经非法批准”。

## 应能回答的问题

为什么部分拒付仍为 ACT？为什么文档缺失是 ASK？为什么非 panel 不自动升级？为什么不能把 policy 和依赖它的 coverage 放同轮？为什么离线 100% 不能证明模型可靠？为什么共享 key 不能证明每人亲自运行？答案均可在代码、业务规则和改进文档中逐一定位。
