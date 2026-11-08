# 新版需求追踪矩阵

| ID | 当前来源 | 责任方 | 可检查要求 | 状态 |
|---|---|---|---|---|
| HUB-01 | HUB_NOC §1-2 | HUB | 四条 H2C 道、四路 C2H 分流、独立控制道 | 已定 |
| HUB-02 | HUB_NOC §3.2 | HUB/L2 | H2C 道 n 只读 L2 象限 n；每道 32 B；总 128 B/拍 | 已定 |
| HUB-03 | HUB_NOC §3.2 | HUB/L2 | 核 n 的 C2H 只写 L2 象限 n；每核 32 B | 已定 |
| HUB-04 | HUB_NOC §4 | HUB | `en/din/be/addr/src`，同链路保序，ready 反向 | 已定 |
| HUB-05 | HUB_NOC §3.5 | HUB/backend | 每段级数、分叉位置、回程级数可参数化（A1-A7） | 待仿真 |
| HUB-06 | HUB_NOC §5.2 | HUB/LDP | 多播分叉按已取位；每目的独立 ready；不额外配多播存储 | 已定 |
| HUB-07 | HUB_NOC §5.3 | MAE_ENG/HUB | 源顺序由 MAE 给；HUB 只在单位末拍切换 | 待审查 |
| HUB-08 | HUB_NOC §6 | CCU/HUB | C2H 通路选择由本核 CCU 给；四路直通不扇入 | 已定 |
| HUB-09 | HUB_NOC §7 | HUB/发令方 | 最终存储写入回 `valid+src`；发令方按 src 计数 | 待仿真 |
| HUB-10 | HUB_NOC §8 | HUB/LIC | 64-bit 控制道独立握手；与数据网无先后保证 | 待审查 |
| CRU-01 | MAE_CRU §1-4 | MAE_CRU | 合并种类、参与核、地址范围、应到份数由搬运指令给出 | 已定 |
| CRU-02 | MAE_CRU §4-5 | MAE_CRU | 地址到齐即合并；一组完成后报告 MAE_ENG | 已定 |
| CRU-03 | MAE_CRU §3/5 | MAE_CRU | 部分和 BF16 直出；不做旧 RHUB MXFP6 量化 | 已定 |
| CRU-04 | MAE_CRU §5 | MAE_CRU/HUB | 输出可作为 H2C 第二源；入口写入回握手给发数据核 | 已定 |
| CRU-05 | MAE_CRU §7 | MAE_CRU | lane/FIFO/精度/面积参数需标定 | 待标定 |
| CTRL-01 | DATA_TRANSFER_PROTOCOL §8 | HUB | 控制道消息透明转发，端点队列隔离 | 待审查 |
| ERR-01 | HUB_NOC §10 | HUB/L2/LIC | 地址越界/错误上报；流量停顿只计数，不伪装成协议错 | 待审查 |
