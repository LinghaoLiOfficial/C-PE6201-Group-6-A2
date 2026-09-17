# 团队对齐：LI_LINGHAO 本次完整 live battery 的经验

先阅读本说明，再进入自己的 D5_NAME 文件夹，按 README_EN.md 操作。
这是流程补充，不是新运行版本。契约仍为 d5-live-1.1，原始个人包的代码、
prompt、案例、配置和 package_manifest.json 均保持不变。

## 本次结果与含义

2026 年 9 月 17 日（新加坡时间），LI_LINGHAO 使用 DeepSeek v3.2、
descriptor v2 完成 45 个案例、75 次试验。代码检查 72/75 通过，独立
GPT-4.1 mini judge 对 72 条可审阅记录全部判为通过；综合为 72/75（96%）。
普通案例 28/30，负面案例 44/45，另外 3 条始终保留为失败。

“跑完”意味着实验和评分完成，并非所有案例都成功。不同模型不需要达到相同分数。
本说明不提供成功轨迹、参考答案或逐案例解题提示，也不要将本说明或成绩输入 agent。

## 大家统一采用的流程

1. 新建文件夹解压自己的新版包，先执行 verify 和 offline。需要 Python 3.10+，
   无需第三方 Python 库。
2. 核对 API 余额及 assignment.json 中的价格。模型不可用或价格变化时联系
   LI_LINGHAO，不要自行更换模型、价格、路由或 prompt。通过隐藏输入提示填写自己的 key，
   不提交到 Git，也不发给队友。
3. 执行一次 6 案例预检，把完整结果、assignment.json 和 package_manifest.json
   提交到个人分支并创建 Draft PR。最终决定正确也要如实报告工具问题与费用。
4. 等 LI_LINGHAO 审阅后发回绑定你自己的包和预检的 release.json。不能借用他人的
   放行文件。协调人区分公共接口/服务问题与真实模型错误，不能仅因分数低反复预检刷分。
5. 按个人 README 执行 full 一次，保持终端打开。正式 battery 为普通案例 30 次，
   负面案例 15 个各 3 次，共 75 次。不得筛选案例、因低分中止、删除 full-started.json，
   或重跑失败替换结果。若中断，保留部分输出并报告；当前脚本不支持断点续跑。
6. 在终端打印的 suite 文件夹写 OBSERVATIONS.md，再按 pack 命令打包。保留全部
   75 行、轨迹、工具日志、响应、tokens、错误和 dispatch receipt，不修改生成的证据。
   预算/后端停止后的记录也必须保留在分母中。
7. 在同一分支/PR 提交返回 ZIP、release.json 和观察说明。由 LI_LINGHAO 集中调用
   GPT-4.1 mini judge，队友不需要填写 human_review.csv 或自行评分。原始结果中的
   judgement pending 正常，最终综合通过必须同时满足代码检查和 judge。

## 失败带来的经验

两条记录重复调用 get_claim，被去重保护阻止；即使最终决定正确，仍算执行违规。
一条模型自行生成禁止的 Observation，未完成有效决策写入。这三条没有改成通过。
保护机制必须保留，也不要各自加 prompt 提醒或补丁消除这些失败。后续改进应统一发布
新版本，作为另一个实验记录。

revision 1.1 已统一澄清之前预检暴露的输出 schema、字段类型、状态值和评分判据，
并支持安全的 JSON 常量。这些改动已经在包内，不需要手动补丁。旧版与新版成绩不能
直接用于声称模型能力提升，因为实验契约和新的随机输出也发生了变化。

## Git 提交及观察报告

仓库：https://github.com/LinghaoLiOfficial/C-PE6201-Group-6-A2

使用个人分支 d5/YOUR_NAME-r1.1，建立指向 main 的 Draft PR；仅将结果放在
Part3_LI_LINGHAO/d5_live_submissions/YOUR_NAME/r1.1/。具体 Git 命令见个人 README。
把 PR 链接发给 LI_LINGHAO，不直接 push main，不覆盖旧证据。

观察说明应写日期、实际模型/版本、预检和正式运行状态、出错案例/trial、保护机制行为
及费用证据。区分执行完成率、代码通过率和综合通过率，区分标价估算与 API usage.cost，
预检费用与正式费用分开。LI_LINGHAO 正式 agent + judge 的标价估算为 US$0.370868770，
仅作已发生的参考，不是其他模型的费用保证。

收齐团队结果后再讨论跨模型差异。ZHOU_SIHAN 运行 DeepSeek v1，与 LI_LINGHAO 的 v2
做同模型对比；其余成员运行各自分配的 v2 模型。大家使用相同 revision、案例、上限和
评分政策。LI_LINGHAO 自己已经完成，不需再次运行。
