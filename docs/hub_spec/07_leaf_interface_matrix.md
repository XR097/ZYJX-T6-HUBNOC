# 当前实现分解接口矩阵

这是 RTL 拆分建议，不新增正式接口。模块边界可合并、复制或插级；每个块必须保持 `docs/specs/` 合同中的保序、旁带同拍和计数责任。

| 建议块 | 作用 | 不变量 |
|---|---|---|
| `h2c_l2_reader[4]` | L2 象限读地址/数据流 | 道 n 只读象限 n；不生成地址；三条流按次序配对 |
| `h2c_mcast_fork[4]` | 按单位核掩码复制 | 各目的独立取走；不丢、不重；慢核不拖快核 |
| `h2c_ack_return[4]` | 汇总各核写入握手 | 按（核，`src`）归属；HUB 不做完成判定 |
| `c2h_l2wp_link[4]` | 核输出直达 L2 | 核 n 只写象限 n；反压可到 `stall_tx` |
| `hub_ctrl_fabric` | 命令网透明转发 | 每拍带 `addr`；不解析长度/类型；端点负责队列 |
| `hub_idn_fork` | IDN 按字核集合分叉 | 集合随字旁带；到核链路不带集合 |
| `idn_ack_return` | IDN 回程转交 | valid + `src`，不丢不重 |
| `cru_l2_reader` | NI 读口参与象限对齐 | 独立 ready；掩码外不等待；返回先后不影响结果 |
| `cru_merge_pipe` | 解码和合并 | 编码由指令给；固定象限次序；不新增错误状态 |
| `cru_l2_writer` | 结果交给 NI-L2C | 写回 L2；写入握手由发令方计数 |

端口速查：数据 32 B，`be` 32 bit，`addr` 24 bit，`seg` 5 bit，`src` 按正式篇标定；读返回叫 `vld`，写入握手叫 `valid`，后者无 `ready`。

实现拆分不能恢复旧 RHUB、H2C 第二源、C2H→CRU 分流、VC/credit/flit/`last`/`nw8` 或额外 ERROR 状态。
