# D5 公共契约修复版 1.1

原冻结代码、案例、标签以及第一次 live 的 10/75 综合结果均保留，不追溯改分。
新代码位于本目录 runtime/integration；两个 descriptor 版本共用同一修复。

## 修复内容

1. 明确逐行 status、升级接收人、缺失项、日期及 totals 的结构；同时用于 prompt 和写入校验。
2. 修正逐行匹配，单个 status 错误不再连带误报正确的 code/amount；重复行仍逐个核对。
3. 拒绝模型伪造 Observation，不接受 Action/Final 混写，不自动替换或补齐错误答案。
   Action 参数安全支持 JSON 的 null/true/false 常量，不执行变量、函数或表达式；Final 仍须严格 JSON。
4. 原始 must_record 不变，通过独立澄清映射解释“逐行定价”、旧工具名称和升级时未批准某行的含义；新评分记录保留映射。
5. 评分汇总明确 not_reviewable 数量；新 judge 入口拒绝对旧版本 suite 评分。

## 接下来如何协作

- 发给各人 packets 内自己的新版 ZIP，并附 TEAM_MESSAGE_EN.md。必须解压到新目录，不混用旧 receipt/输出。
- 每人先跑 6 次预检，通过 Git 个人分支和 Draft PR 提交到 `Part3_LI_LINGHAO/d5_live_submissions/姓名/r1.1/`。
- 你审核接口、模型错误、预算及剩余额度后生成 release.json。模型仍可能失败，不能刷分；共享接口缺陷则应先解决。
- 放行后再执行正式 75 次。LI 的新 v2 与 ZHOU 的新 v1 配对，不能用旧版 v2 去对照新版 v1。
- 你使用本目录 run_judge.py 统一评分，再汇总五模型 v2 与同模型 v1/v2 两张表。

英文说明中包含具体命令、模型与预算约束。本次修复验证与小规模 live 结果见 VALIDATION.md；不把预检结果冒充新正式 battery。
