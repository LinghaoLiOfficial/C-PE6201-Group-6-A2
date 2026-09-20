# DAI_MINFEI——正式 D5 live battery 交接说明

本文件只用于**正式 75-trial D5 live battery**。六案例诊断 preflight 已经完成，不要为了寻找更高分而重复运行。

## 当前授权状态

- 包版本：`d5-live-1.1`
- 指定模型：`anthropic/claude-haiku-4.5`，descriptor `v2`
- 规模：45 个案例 / 75 次 trial（30 normal + 45 negative）
- Preflight：6/6 条记录完整，`transport_ok=true`
- Preflight 包 SHA-256：`7686c348bdac62a1f9ee0362c9d90fa408c5b92d33aeb2e55744a53879244272`
- Preflight JSON SHA-256：`b5c41b18057acc3baee51ed0e1d74a72394c67e00f8a9f5750883c3ebaba1e5f`
- 第二次 preflight 已记录成本：USD 0.103667
- 预计 agent 总成本：USD 2.5533095（低于成员 USD 3 预算）

LI_LINGHAO 已审阅该 preflight，并授权按下述方式执行正式运行。此授权只适用于上述精确版本和精确 preflight。

## 运行前

1. 先拉取共享仓库最新 `main`，保留本地工作，不要覆盖或删除证据。
2. 使用原始 DAI alignment package 的**全新解压目录**。不得修改 package、assignment、runtime、prompt、案例、价格、模型、guardrail 或评分。
3. 确认 `assignment.json` 仍是 `anthropic/claude-haiku-4.5`、`v2`、`d5-live-1.1`。
4. 确认个人 OpenRouter 余额。不要发送 API key，也不要提交 `.env`、key 或 credentials。
5. 除非 LI_LINGHAO 明确授权新的版本化尝试，不要再跑 preflight。

## 正式命令

在包含 `run_member.py` 的解压目录中运行：

```sh
python3 run_member.py verify
python3 run_member.py offline
python3 run_member.py full --preflight "/绝对路径/preflight_attempt_2_authorized/preflight.json" --release "/绝对路径/preflight_attempt_2_authorized/release.json"
```

使用含六条完整记录的同一个 preflight 目录。保持终端打开直到运行结束。正式命令只执行一次，当前工具不支持 resume。所有 75 条记录都必须保留，包括 parse error、not_recorded、tool failure、backend failure 以及预算/step-cap 停止。不要筛选、修复、重命名或单独重跑 trial。低分也是有效实验结果。

## 打包和记录

`full` 完成后，在输出 suite 目录写 `OBSERVATIONS.md`，记录日期、系统、Python、完整命令、模型/version、75/75 完整性、normal/negative 分母、代码通过数、所有失败类别及 case/trial ID、模型失败与基础设施失败的区分、配置价格与 provider usage 成本，以及未测量的未知费用或余额信息。

然后运行：

```sh
python3 run_member.py pack --suite "/绝对路径/SUITE_FOLDER"
```

## Git 回传

先拉取 `main`，使用个人分支；不要直接 push `main`，也不要修改其他成员目录。

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c d5/DAI_MINFEI-r1.1-formal
mkdir -p Part3_LI_LINGHAO/d5_live_submissions/DAI_MINFEI/r1.1
# 只复制最终 ZIP、release.json、OBSERVATIONS.md 到上述目录。
# 保持 preflight_attempt_2_authorized/ 和之前中断尝试分开保存。
git add Part3_LI_LINGHAO/d5_live_submissions/DAI_MINFEI/r1.1
git commit -m "Add DAI_MINFEI revision 1.1 formal live battery"
git push -u origin d5/DAI_MINFEI-r1.1-formal
```

创建目标为 `main` 的 Draft PR，并将 PR URL 发给 LI_LINGHAO。最终回传必须包含 `D5_RETURN_DAI_MINFEI.zip`、`release.json`、`OBSERVATIONS.md` 和完整保留的 preflight 证据。不要填写 `human_review.csv`，也不要自行运行 judge；LI_LINGHAO 会统一运行 `openai/gpt-4.1-mini` judge。
