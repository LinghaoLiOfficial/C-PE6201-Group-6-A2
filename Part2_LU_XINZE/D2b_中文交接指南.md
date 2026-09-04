# D2(b) 中文交接指南

## 这份 Part2 是什么

这里是**不修改 Part1** 的自包含 D2(b) 整合版本。`Part1_CHEN_MINGSONG` 已保持原样；本目录复制了必须的 agent 和 tools，并只在副本中加入 v1/v2 pre-authorisation interface 和 annual-limit 防呆。队友可以先 review，再选择性合并，不会直接覆盖成员一的实现。

| 文件 | 用途 |
|---|---|
| `D2b_integrated_tools.py` | Part2 专用 tools 副本；含 `PREAUTH_VERSION=v1/v2`、`A2_DATA_DIR` 和 safe policy lookup。 |
| `D2b_integrated_agent.py` | Part2 专用 ReAct agent 副本；prompt/tool descriptor 随版本切换。 |
| `D2b_full_flow_test.py` | 不需要 API 的 scripted end-to-end runner。 |
| `D2b_tool_descriptors.md` | 8 个工具的六字段 descriptor 和两个 poka-yoke。 |
| `D2b_v1_v2_preauthorisation.md` | v1/v2 设计和之后必须补的正式测量表。 |
| `D2b_smoke_test_results.md` | 已真实执行的 tool 与 full-flow 测试记录。 |


## D2(b) 用人话解释

1. 每个最终工具都要有说明书：名字和签名、做什么、输入、返回大小上限、如何失败、是否会造成不可逆操作。
2. 至少两个 poka-yoke（防呆）：不是让模型更认真，而是让确定代码处理容易错的判断。
3. 选一个工具做 v1 到 v2：保留旧接口和新接口，之后在同样模型、同样 cases、同样 trials 下测量差异。

## 两个防呆

### 防呆 1：不要看错 pre-auth 日期

v1 只给模型 `valid_from` 和 `valid_to`，模型必须自己判断服务日。v2 把服务日期传给工具，工具直接返回：

```text
valid
expired_before_service
not_found
```

因此“存在但过期的授权被当作有效”由接口本身消除。这个改动也是正式的 **v1 -> v2 rewrite**。

### 防呆 2：不要算错年度额度

safe `lookup_policy` 接收 service date 和 claim total，直接给出：

```text
service_date_covered
remaining_annual_limit
annual_limit_status = within_limit / exceeded
```

模型不再自行做减法或比较；“额度超了但仍批准”不能由模型算错造成。

## 已运行的完整流程测试

以下测试没有使用 API key。runner 固定模型输出，但真正执行 Part2 的 ReAct loop、Action parser、fixture tools、observations 和 Final decision。

| Version | Case | 结果 |
|---|---|---|
| v1 | `CLM-8842` | 6 turns，`approve_in_principle`；pre-auth 返回 `PA-5521` 原始日期。 |
| v1 | `CLM-8894` | 6 turns，`request_document`；pre-auth 返回 `PA-5640` 原始日期。 |
| v1 | `CLM-8925` | 4 turns，policy 直接返回 `annual_limit_status=exceeded`，最终 escalate。 |
| v2 | `CLM-8842` | 6 turns，`approve_in_principle`；pre-auth 返回 `status=valid`。 |
| v2 | `CLM-8894` | 6 turns，`request_document`；pre-auth 返回 `status=expired_before_service`。 |
| v2 | `CLM-8925` | 4 turns，policy 直接返回 `annual_limit_status=exceeded`，最终 escalate。 |

复跑命令：

```bash
cd Part2_LU_XINZE
python3 D2b_full_flow_test.py \
  --data-dir /path/to/A2_reference_data/A2_reference_data/data_A \
  --version v2
```

将 `--version v2` 改成 `--version v1` 可以测旧接口。

## 后续仍要做什么

1. 先 review `D2b_integrated_tools.py` 和 `D2b_integrated_agent.py`；不要整份覆盖 Part1。
2. 若团队同意进入最终 agent，只合并 pre-auth version switch、safe policy lookup、descriptor switch 和 `A2_DATA_DIR` portability change。
3. 再用 OpenRouter 做 live smoke test；key 不能提交。
4. 等 D4 harness 和最终 evaluation set 后，固定同一模型、cases 和 trials，正式填写 tokens returned per tool call、pass rate 与 guardrail cases passed。

当前已完成：design、两个可运行 poka-yoke、v1/v2 interface、完整 scripted flow test。当前未完成：live-model smoke test 与 harness-based formal measurement；不要编造这些数值。
