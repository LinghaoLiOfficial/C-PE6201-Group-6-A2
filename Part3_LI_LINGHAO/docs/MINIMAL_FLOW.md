# 三种结果的最小离线流程

用户已反馈：第 1 步接口文档已交给陈、陆、周审阅，三位认为没有问题。本次基于该接口继续实现，未导入队友的案例草稿，也未修改老师的数据或答案。

## 一条命令运行

在仓库根目录执行：

```bash
python3 Part3_LI_LINGHAO/run_minimal.py
python3 Part3_LI_LINGHAO/run_minimal.py --version v1
python3 -m unittest discover -s Part3_LI_LINGHAO/tests -v
```

默认完全离线，无第三方 Python 依赖，无 API key。最小集合 runner 明确模拟操作员确认，因此每例会实际写入本地决定日志。单例 `run_case.py` 仍默认不确认，只有 `--approve` 才打开 confirm 门禁。

## 覆盖什么

| Case | 正确结果 | Trials | 每次响应轮数 | 关键记录 |
|---|---|---:|---:|---|
| CLM-8842 | approve_in_principle | 1 | 7 | 三条明细、排除 EX-14、PA-5521、批准 2180、拒付 300 |
| CLM-8894 | request_document | 3 | 7 | 29881 的有效授权缺失；服务日 2026-09-09；过期 PA-5640 的证据 |
| CLM-8925 | escalate | 3 | 5 | annual_limit_exceeded，11400 超过 9200 |

每个 trial 使用真实工具、护栏和独立日志。turns 包括最终回答轮。v1 和 v2 均支持：v1 授权调用不传服务日；v2 传服务日并由工具返回有效性判断。

## 新增实现

- `integration/scripts.py`：三个明确编写的轨迹，只依赖已知 fixture 事实，不加载答案文件。
- `integration/minimal_checks.py`：执行完成后读取老师答案，核对决定、触发原因、规范化缺失项、逐行金额与排除、实际写入及关键工具证据。
- `run_minimal.py`：普通一次、负例三次；输出 JSON、CSV 和各 trial 的真实日志。
- `tests/test_minimal.py`：两个版本完整运行、三种结果未确认时均不写入，以及金额／缺失项错误会被判错。

## 修复了一个证据接口缺口

原 v2 的过期授权返回只有 `status=expired_before_service` 与布尔值，但老师 CLM-8894 的 must_record 要求记录 PA-5640 和到期日 2026-05-31。现在过期响应补充 `preauth_id`、`valid_to`，相应更新 v2 descriptor。v2 仍直接计算有效性，模型不需要自行比较日期；v1 保持原始日期接口。

这是基于最小流程发现的附加修订。先前团队同意的是 Step 1 接口，此次字段补充尚未另行收集反馈；之后向陆交接本记录即可说明差异。真实 v1/v2 测量应使用这份最终版本重新运行。

## 实际验证结果

21 项 unittest 通过。测试中 v1、v2 各运行 7 trials，均通过最小 code checks；另真实运行了一次默认 v2 CLI，7/7 通过。HTTP 在完整流程测试中被禁止；原 live adapter 单元测试只用模拟响应，没有真实 API 调用。

这些是 scripted 代码验证结果，不是 live 模型准确率，也不是完整 D4 评测。`judgement_status` 保持 pending；解释文字的充分性没有自动宣布通过。三条案例的路径中没有读取答案；只有执行后的检查器会读取答案。金额／missing 错误的反例测试验证了 grader 不会只看 decision。

结果保存在 `output/minimal/suite-*/`：总表 `results.json`、`results.csv`；每个 run 下有 `result.json`、`decisions.jsonl`、`transcript.txt`。`results/minimal_v2_summary.json` 是已执行 v2 运行的紧凑记录，适合版本控制。每次运行时间戳、唯一目录会变化。

## 成员案例征集

可发送文件：`output/pdf/Group6_ProblemA_Case_Design_Request_ZH.pdf`。
对应可编辑文本：`docs/CASE_DESIGN_REQUEST_ZH.md`。
空白交接模板：`case_request/templates/`。

建议每人 5 个（4 正常 + 1 负例），与老师 15 个合计 45 个，其中 15 个负例，每模型 75 trials。数量与比例是分开的概念：老师要求每人 5–8 个，没有“优秀必须 8 个”的阈值；个人 4:1 是团队征集方案。PDF 中已区分规则来源与团队安排。

## 范围与后续

未合并队友案例，未创建任何成员的新案例，未执行 live battery，未推送新改动。下一步接收成员输入、独立标签和设计说明，审阅后统一扩展工作数据、正式脚本和完整 harness。原 v2 对“尚未生效”授权的状态命名及同组合多授权问题仍需后续处理；本次三个案例不涉及该边界。
