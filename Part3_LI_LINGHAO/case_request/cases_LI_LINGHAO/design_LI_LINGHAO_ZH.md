# LI LINGHAO 的 Problem A 原创案例

作者：LI LINGHAO。案例编号：`CLM-16301`–`CLM-16305`。分配为 4 个普通 ACT
案例和 1 个负面 ESCALATE 案例。所有案例均为新增记录，未修改老师提供的 15 个案例，
也未合并队友案例。

| 案例 | 类型 | 预期决定 | 测试重点 |
|---|---|---|---|
| CLM-16301 | 普通 | `approve_in_principle` | 保单开始日 2026-06-01 应包含在保障区间 |
| CLM-16302 | 普通 | `approve_in_principle` | 保单结束日 2027-05-31 应包含在保障区间 |
| CLM-16303 | 普通 | `approve_in_principle` | 15823 按 EX-14 拒付，但已解决的单行不应升级 |
| CLM-16304 | 普通 | `approve_in_principle` | 同一索赔中一条可赔、一条按 EX-14 拒付 |
| CLM-16305 | 负面 | `escalate` | 服务日期早于 POL-6001 开始日，触发 `outside_policy_dates` |

## 设计依据

- `CLM-16301`：M-5502 的 POL-6001 从 2026-06-01 开始；服务日期等于开始日，99213
  金额 200，应全额批准。
- `CLM-16302`：服务日期等于 POL-6001 的结束日 2027-05-31；99213 金额 250，应全额批准。
- `CLM-16303`：M-3390 的 POL-4102 排除 15823，规则为 EX-14 cosmetic dermatology；
  因此批准决定中应记录该行 `not_covered`、批准 0、拒付 180。
- `CLM-16304`：M-2214 的 POL-3310 覆盖 47120（900），排除 31255（250）；两条线都
  已经可以确定，不应因一条排除而升级，批准总额 900、拒付总额 250。
- `CLM-16305`：服务日期 2026-05-31 早于 POL-6001 开始日 2026-06-01；唯一触发条件为
  `outside_policy_dates`，应升级给 `human claims assessor`。

## 验证

```bash
python3 Part3_LI_LINGHAO/case_request/validate_cases.py
python3 Part3_LI_LINGHAO/run_li_cases.py
python3 -m unittest discover -s Part3_LI_LINGHAO/tests -v
```

脚本运行普通案例各 1 次、负面案例 3 次，共 7 次。结果中的代码检查确认决定、逐行结果、
金额、证据工具和升级触发器；自然语言理由的质量仍需人工审阅。
