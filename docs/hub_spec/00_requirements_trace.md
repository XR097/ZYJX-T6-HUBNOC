# 当前需求追踪矩阵

> 本表是 HUB_NOC、HUB_IDN、MAE_CRU 的派生追踪，不覆盖正式篇。端口、位宽和握手以 `docs/specs/ONCHIP_DATAPATH_ARCH.md`、`DATA_TRANSFER_PROTOCOL.md` 及对应模块篇为准。

| ID | 要求 | 主责 | 状态 | 台账 |
|---|---|---|---|---|
| HUB-01 | 4 条 H2C、4 条 C2H、命令网，H2C 单源、C2H 单去向 | HUB_NOC | 已定 | — |
| HUB-02 | H2C 道 n 连接 L2 象限 n，四核独立取走 | HUB_NOC/L2 | 待仿真 | N-01、N-07 |
| HUB-03 | C2H 核 n 只写象限 n，反压传到发送端 | HUB_NOC/CCU | 待仿真 | N-02、N-07 |
| HUB-04 | 正向 `en/ready`、读返回 `vld`、写入 `valid`，旁带同拍 | HUB_NOC | 已定 | — |
| HUB-05 | 级数、skid、分叉和回程可参数化，插级只增加延迟 | HUB_NOC | 待仿真 | N-01 |
| HUB-06 | 命令网每拍带 `addr`，无长度/类型/末字 | HUB_NOC/ISA | 待审查 | N-04 |
| IDN-01 | NI 一路 32 B 输入、四核各一路 32 B 输出 | HUB_IDN | 已定 | — |
| IDN-02 | 每字核集合与 `din/addr/seg/be/src` 同拍，到核链路不带集合 | HUB_IDN | 待仿真 | N-13 |
| IDN-03 | 多播按核独立取走，valid + `src` 回程不丢不重 | HUB_IDN/MAE | 待仿真 | N-13、N-14 |
| CRU-01 | 各核先写 L2，NI 读口按参与象限取数，掩码外不等待 | MAE_CRU/MAE_ENG | 待仿真 | N-05、N-15 |
| CRU-02 | 合并启动所需报告范围和地址配对规则 | MAE_ENG/LIC | 待审查 | N-18 |
| CRU-03 | 逐元素、标量、读集合并及编码输出 | MAE_CRU | 待仿真/待标定 | N-06、N-17 |
| CRU-04 | 结果经 NI-L2C 写回 L2，完成由发令方计数 | MAE_CRU/MAE_ENG | 待仿真 | N-08、N-11 |
| CRU-05 | 归约和残差是两条指令，依赖由 LIC 表达 | LIC/MAE | 待仿真 | N-16 |
| LEN-01 | 紧凑对象先元数据，再 F 列表和码块；完成后转发应写量 | MAE_ENG/L1/L2 | 待仿真 | N-09 |
| ADDR-01 | `addr` 24 bit，`seg` 5 bit（堆选 1 + 段掩码 4 独热） | 架构/L1/L2 | 已定 | N-03（已关闭） |

验证状态只表示动作类别；未决项的详细关闭证据在[台账](../reviews/open_issues_current.md)。
