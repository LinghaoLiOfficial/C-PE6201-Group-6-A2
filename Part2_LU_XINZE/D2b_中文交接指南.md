# D2(b) 中文交接指南

## 这部分现在完成了什么

Part2 已新增四份英文提交材料和一份独立的 Python 工具模块：

| 文件 | 用途 |
|---|---|
| `D2b_tool_descriptors.md` | 8 个工具的六字段 descriptor，以及两个 poka-yoke。 |
| `D2b_v1_v2_preauthorisation.md` | `get_preauthorisation` 的 v1/v2 改写方案和正式测量表模板。 |
| `D2b_preauthorisation_versions.py` | 可直接运行的 v1/v2 pre-auth 工具，以及 policy annual-limit 的防呆函数。 |
| `D2b_smoke_test_results.md` | 已完成的工具级测试与待完成的 agent 测试记录。 |

这部分没有修改 `Part1_CHEN_MINGSONG` 的任何文件，也没有把 D2(b) 的代码直接塞进主 agent。这样整合时可以由主 agent/harness 负责人明确选择如何合并，而不会覆盖别人的实现。

## D2(b) 用人话解释

D2(b) 有三件事：

1. **每个工具的说明书。**
   8 个工具都要说明：叫什么、做什么、输入是什么、最多返回多少、何时失败、会不会造成不可逆操作。

2. **两个 poka-yoke（防呆）。**
   不是提醒模型“仔细一点”，而是把容易错的判断交给确定的代码，让这个错误不能发生。

3. **一个工具的 v1 到 v2 对比。**
   选一个工具，保留旧接口 v1 和新接口 v2；之后在完全相同的条件下比较效果。

## 两个防呆设计

### 防呆 1：不要看错 pre-auth 日期

原来的工具只返回授权起止日期，模型需要自己判断服务日是否在范围内。存在但已过期的授权可能被错当有效。

新版 `get_preauthorisation` 多接收 `date_of_service`，并直接返回：

```text
valid
expired_before_service
not_found
```

所以模型不需要比较日期；“过期授权被当成有效”这个错误由工具接口消除。这个改动同时就是本组正式的 **v1 -> v2 rewrite**。

### 防呆 2：不要算错年度额度

原来的 policy lookup 给出年度总额和已用额度，模型自己做减法，再比较本次 claim 金额。

安全版接口直接给出：

```text
remaining_annual_limit
annual_limit_status = within_limit / exceeded
```

所以模型不需要做金额计算；“额度已经超了但仍批准”这个错误由工具接口消除。

## 已经真实跑过的工具级测试

不需要 API key 的直接工具测试已完成：

| Case | 结果 |
|---|---|
| `CLM-8842` v1 | 返回 `PA-5521`，有效期 `2026-08-01` 到 `2026-10-31`。 |
| `CLM-8842` v2 | 返回 `status=valid`、`valid_on_service_date=true`、`PA-5521`。 |
| `CLM-8894` v2 | 返回 `status=expired_before_service`、`valid_on_service_date=false`。 |
| `CLM-8925` policy 防呆 | 正确给出剩余额度 `9200` 与 `annual_limit_status=exceeded`。 |

运行命令：

```bash
python3 D2b_preauthorisation_versions.py \
  --data-dir /path/to/A2_reference_data/A2_reference_data/data_A
```

## 仍需谁来做、什么时候做

### 需要主 agent 整合负责人做

把 `get_preauthorisation` 的 v1/v2 开关接进最终 agent：

- v1 prompt 使用 v1 signature 和 raw dates return shape；
- v2 prompt 使用 v2 signature 和固定 status return shape；
- agent 读取 v2 的 `valid` / `expired_before_service` / `not_found` 并正确决定。

整合后可以用 OpenRouter 做两个 live smoke tests：

| Case | 预期最终 decision |
|---|---|
| `CLM-8842` | `approve_in_principle` |
| `CLM-8894` | `request_document` |

### 需要 D4/harness 负责人完成后再做

这才是正式的 v1/v2 对比：固定**同一模型、同一 evaluation set、同一 trials、同一 agent loop**，只改 v1/v2 descriptor 和 return shape；填写真实的：

```text
tokens returned per tool call
evaluation pass rate
guardrail cases passed
```

现在不要编造这些数字。当前完成的是 design、可运行工具接口和 direct smoke tests；正式测量依赖 final harness。
