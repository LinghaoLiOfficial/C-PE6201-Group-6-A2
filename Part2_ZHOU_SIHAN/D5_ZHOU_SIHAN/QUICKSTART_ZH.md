# 中文快速步骤 - ZHOU_SIHAN

你的任务：D2(b) live v1 paired with LI_LINGHAO live v2；模型 `deepseek/deepseek-v3.2`；版本 `v1`。

1. 解压自己的 ZIP，在含 run_member.py 的文件夹打开终端。Python 3.10+，无需安装第三方库。
2. 运行 `python3 run_member.py verify` 和 `python3 run_member.py offline`。Windows 可用 python 替代 python3。
3. 确认个人额度和 assignment.json 的模型价格。运行 `python3 run_member.py preflight`，按提示输入自己的 key（不显示、不保存）。不要把 key 发给任何人。
4. 将终端打印的整个 preflight 文件夹发给 LI_LINGHAO。三个预检案例不计入正式 75 次。
5. 等 LI_LINGHAO 发回 release.json，再按英文 README 的 full 命令运行，两个路径指向你的预检文件和放行文件。
6. 完成后编辑 suite 文件夹内 OBSERVATIONS.md（可自行新建），写真实观察、错误和额度差异，再按 pack 命令打包回传。
7. 不修改案例、模型、prompt、上限；不因答错重跑刷分；中断保留全部部分结果并联系负责人。
8. 你不需人工填写 judgement，也不需调用 judge：由 LI_LINGHAO 集中使用另一个 LLM 评分。原始输出 judgement pending 是正常状态。

详细命令与费用局限见 README_EN.md。每个正式任务 75 次：普通 30，负面 45。v1 是同模型对照，不计入五模型 v2 排名。
