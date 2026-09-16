# D4 / D5(a) 冻结版本与团队交接

版本标识：`part3-d4-d5a-v1.0.0`。
Git tag 指向本次完整交付 commit；不将 commit hash 写入其自身文件，避免自引用。
查看唯一 commit：`git rev-parse part3-d4-d5a-v1.0.0^{commit}`。

## 冻结范围

- 45 个案例与 labels：15 个老师案例 + 六人各 5 个新增案例。
- 30 个普通、15 个负面；普通一次、负面三次，共 75 trials。
- v2 prompt、工具接口、guardrails、真实 runner、固定 scripted 轨迹、D4 评分规则。
- 默认 scripted；step_cap=8、单 trial budget_usd=0.05、autonomy=confirm。
  harness 明确模拟操作员批准，仅写本地日志。
- 第二模型 judge 为 anthropic/claude-haiku-4.5，rubric 位于 integration/judge_prompt.md。
- 全部脚本、标签、数据、提示词、说明和交付证据的 SHA-256 在 release_manifest.json。

## 验收与复现

```bash
python3 Part3_LI_LINGHAO/scripts/verify_freeze.py
python3 -m unittest discover -s Part3_LI_LINGHAO/tests -q
python3 Part3_LI_LINGHAO/scripts/run_d4_harness.py
```

默认脚本完全离线，不需要 key。35 项回归测试通过；v2 全量 75/75 代码通过。
轮数、token、cost 由真实 runner instrumentation 记录，其中 scripted token 是合成值，
API 成本为零，不能作为 live 费用。每次独立日志均保存。

之前的真实 judge 调用共 75 次、263 条要求均被该模型判为通过，估算费用 $0.3489。
judge 不是人工，也不是绝对正确。原始响应、请求、rubric 和配置保存于
results/d5a_judge_evidence.zip。Agent 运行证据在 results/d5a_scripted_evidence.zip。
ZIP 内绝对路径、时间戳记录原运行环境；重跑不依赖这些路径。
新的 scripted 运行默认 judgement pending，不能把旧判分冒充新运行判分。

## 已知边界

- v1 全量为 72/75：CLM-8888 三次因 v1 缺失授权 ERROR 与证据门禁不兼容而失败。
  此冻结版本不为提高通过率修改 v1 接口或删减案例。
- 当前人工/模型评分按每次 trial 的所有 must_record 执行，这是团队采取的严格策略，
  不是声称老师强制每条都手工填写。
- 原作者 labels 保留，missing 的结构化映射在单独文件中。
- 早期规则模拟 d4_full 不作为真实验收结果交付。
- 本版本没有运行 D5(b) live battery；模型分配和当前价格需要在 live 开始前确定。

## 团队使用

在独立目录 clone 后使用 tag（或该 tag 对应 commit），不要混用各自工作树未提交修改：

```bash
git fetch origin --tags
git checkout --detach part3-d4-d5a-v1.0.0
```

先核对 release_manifest，再运行离线验收。正式实验需统一案例、评分器、prompt 版本、
工具、上限和 judge rubric，变动实验变量必须记录。模型及价格由命令行明确指定。
Judge 必须与被评 live 模型不同。API key 留在个人环境或 .env，永不提交。

如修正缺陷，不移动或覆盖此 tag：另建提交和新版本，并重新验收受影响结果。
交付步骤包括本地 commit、带说明的 tag、推送分支和 tag；远程是否成功以实际
`git ls-remote` 与本地 commit 一致为准。
