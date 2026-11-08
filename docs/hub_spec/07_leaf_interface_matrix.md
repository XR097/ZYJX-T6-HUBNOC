# 当前实现分解接口矩阵

以下是 RTL 便于验证和综合的叶级分解，不改变新版正文的模块边界。所有块都使用通用握手链路；HUB 不生成地址、不解析载荷、不判断完成。

| 实现块 | 输入 | 输出 | 关键不变量 |
|---|---|---|---|
| `h2c_l2_reader[4]` | MAE `en/addr`、L2 `busy/dout/vld` | 32 B 数据、目的 addr/be/src | busy 保持请求；不生成地址 |
| `h2c_mcast_fork[4]` | 数据、4-bit 掩码、各核 ready | 四路 H2C | 每目的 1 位已取；不额外配多播存储 |
| `h2c_ack_merge[4]` | 四路 `valid+src` | MAE/引擎回程 | 不丢、不重、src 归属正确 |
| `c2h_l2wp_link[4]` | 核集成输出端口、L2WP ready | L2WP 写流 | 核 n 只写象限 n；ready 低沿链路反压并门控 CCU |
| `c2h_ack_return[4]` | L2 写入握手 | 对应 CCU | 只转交本核 `valid+src`，无独立 CRU 入口 |
| `hub_ctrl_fabric` | 64-bit 端点消息 | LIC/MAE/CCU/L2 | 透明转发，端点隔离 |
| `hub_idn_fork` | MAE IDN 32 B 写流、每字 4-bit 核集合 | 四核 IDN 分支 | 核集合随字旁带；分叉只用已取位和 skid |
| `idn_ack_merge` | 四路 IDN `valid+src` | MAE_ENG | 多播按目的核数汇总，不阻塞回程 |
| `cru_l2_reader` | MAE_ENG 地址/象限掩码、NI-L2C 返回数据 | 四象限同址份 | 等参与象限数据到齐后交合并流水 |
| `cru_merge_pipe` | 解码后的参与份、合并种类/编码 | 32 B 结果、实际字节数 | 支持逐元素、标量、读集合并；加法次序固定 |
| `cru_l2_writer` | 结果、目的 `addr/be/src` | NI-L2C 写客户、写入握手 | 写回 L2；引擎按握手计数并通知 LIC |

实现块可合并、复制或插级；任何改变都必须保持 `00_requirements_trace.md` 的不变量。已删除的 `h2c_source_mux`、C2H 到 CRU 分流、`cru_arrival_table` 和旧 RHUB 量化块不属于当前设计。
