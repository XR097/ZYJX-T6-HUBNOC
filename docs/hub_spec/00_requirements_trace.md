# 当前需求追踪矩阵

| ID | 来源 | 责任方 | 可检查要求 | 状态 |
|---|---|---|---|---|
| HUB-01 | HUB_NOC §1-2 | HUB_NOC | 四条 H2C、四条 C2H、命令网；H2C/C2H 均为单源/单去向 | 已定 |
| HUB-02 | HUB_NOC §3.2/§5 | HUB_NOC/L2 | H2C 道 n 只读象限 n；每道 32 B；读总带宽 128 B/拍 | 已定 |
| HUB-03 | HUB_NOC §6 | HUB_NOC/L2 | 核 n 的 C2H 只写象限 n；集成输出端口是唯一来源 | 已定 |
| HUB-04 | Protocol §3 | HUB_NOC | 地址/控制随数据传输；ready 反压；不生成地址 | 已定 |
| HUB-05 | HUB_NOC §3.5 | HUB_NOC/backend | 级数、分叉位置、skid 和回程可参数化 | 待仿真 |
| HUB-06 | HUB_NOC §5.2 | HUB_NOC/LDP | H2C 多播按已取位分叉，各目的独立 ready | 已定 |
| HUB-07 | HUB_NOC §7 | HUB_NOC/MAE | LDP/L2 最终写入回 `valid+src`；发令方计数 | 待仿真 |
| HUB-08 | HUB_NOC §8 | HUB_NOC/LIC | 命令网透明转发；标量不走命令网 | 待审查 |
| IDN-01 | HUB_IDN §1-3 | HUB_IDN | NI 一路 32 B 输入，四核各一路 32 B 输出 | 已定 |
| IDN-02 | HUB_IDN §4-5 | HUB_IDN/MAE | 每字 4-bit 核集合随 `din/addr/seg/be/src` 同拍对齐 | 待仿真 |
| IDN-03 | HUB_IDN §5 | HUB_IDN/NWB | 多播按已取位分叉；每核独立 ready；写入握手按 `src` 汇总 | 待仿真 |
| CRU-01 | MAE_CRU §2-4 | MAE_CRU/MAE_ENG | 各核先写 L2；NI 读口按参与象限同址取数 | 已定 |
| CRU-02 | MAE_CRU §4 | MAE/LIC | 收齐参与核发出报告后才启动合并 | 待审查 |
| CRU-03 | MAE_CRU §3/5 | MAE_CRU | 输入/输出编码由指令给出；支持多编码和压缩输出 | 待标定 |
| CRU-04 | MAE_CRU §5 | MAE_CRU/NI-L2C | 合并结果写回 L2；完成由 NI 写入握手计数 | 待仿真 |
| CRU-05 | MAE_CRU §4/MAE_ENG | LIC/MAE | 归约与残差加是两条指令；Fusion 可循环调度 | 待仿真 |
| LEN-01 | Protocol §8/MAE_ENG §10 | MAE/L1/L2 | 紧挨对象+独立 token 长度表；搬完后转发实际应写量 | 待仿真 |
| ADDR-01 | Protocol §3/L1/L2 | MAE/L1/L2 | `addr` 与 `seg` 的段内地址、类选/堆选解释一致 | 待审查 |
