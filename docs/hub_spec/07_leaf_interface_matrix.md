# 实现分解接口矩阵

以下是 RTL 方便使用的实现分解，不是新版 PDF 新增的架构模块边界。

| 实现块 | 输入 | 输出 | 关键不变量 |
|---|---|---|---|
| `h2c_l2_reader[4]` | MAE `en/addr`、L2 `busy/dout/vld` | 32 B 数据、目的 addr/be/src | busy 保持请求；不生成地址 |
| `h2c_source_mux[4]` | L2 源、MAE_CRU 源、MAE 源顺序 | 单位保序数据 | 只在单位末拍切换 |
| `h2c_mcast_fork[4]` | 数据、4-bit 掩码、各核 ready | 四路 H2C | 每目的 1 位已取；不额外配多播存储 |
| `h2c_ack_merge[4]` | 四路 `valid+src` | MAE/引擎回程 | 不丢、不重、src 归属正确 |
| `c2h_route[4]` | CCU 选择、数据、ready | L2WP 或 CRU | 每核一路直通，不扇入 |
| `c2h_ack_return[4]` | L2/CRU 写入握手 | CCU | 无 ready；按源链路返回 |
| `hub_ctrl_fabric` | 64-bit 端点消息 | LIC/MAE/CCU/L2 | 透明转发，端点隔离 |
| `cru_arrival_table` | C2H/读路径 addr+data | 到齐事件 | 按地址计份数 |
| `cru_merge_pipe` | 到齐数据、运算字段 | BF16 结果 | 无旧 RHUB 量化 |

实现块可合并、复制或插级；任何改变都必须保持 `00_requirements_trace.md` 的不变量。
