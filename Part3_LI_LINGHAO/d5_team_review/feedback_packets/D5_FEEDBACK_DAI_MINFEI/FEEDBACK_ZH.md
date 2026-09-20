# DAI_MINFEI：排查预检中断

仓库只有两条完整记录：CLM-8842 为 Action/Final 同轮错误，CLM-8888 为 not_recorded；
第三个 run 仅有空决策日志，没有 result/transcript。没有 preflight.json 或正式 battery。
已知成本 US$0.035591，未记录调用费用未知，不能计为零。

先检查是否有未上传的原始结果，有则补交。否则保留整个中断目录，反馈最后终端输出、
退出码（如有）、是否关闭进程/终端、Python/系统版本、命令、中断时间及余额，去除密钥。
使用原 Claude Haiku 4.5 v2 revision 1.1 包执行 verify/offline，反馈错误。

区分运行中断原因与两条模型协议错误，不通过修改 prompt 或评分掩盖问题。协调人审阅
中断和预算后，再批准在独立输出目录做新的 6 案例诊断预检；保留两次证据，费用分开。
完整预检及匹配 release 后才能首次正式跑 75 次。后续提交返回 ZIP、release 和观察
说明，由协调人集中 judge。不可伪造缺失轨迹。
