# HUB NoC 当前合同

## 1 边界

HUB 全芯片一个，由四条 H2C 道、四路 C2H 分流和一条 64-bit 控制道组成。HUB 只传输和分路；MAE_ENG/CCU 负责发令，L2/L1/MAE_CRU 负责最终存储或运算。

## 2 数据接口

| 接口 | 宽度 | 主控 | 语义 |
|---|---:|---|---|
| L2 象限 n → H2C n | 32 B × 4 | MAE_ENG | 引擎给读 en/addr；L2 busy 时保持重发 |
| H2C n → 四核 LDP | 32 B × 4 目的 | MAE_ENG | 引擎给目的 addr/be/核掩码；分叉点按各核 ready 独立取走 |
| 四核 C2H → L2WP n | 32 B/核 | 本核 CCU | 核 n 只写象限 n；分流选择随单位边界 |
| 四核 C2H → MAE_CRU | 32 B/核 | 本核 CCU | addr 是 CRU 内地址；到齐计数由 CRU 维护 |
| MAE_CRU → H2C MUX | 32 B/道参考 | MAE_ENG | 作为 H2C 第二源，源顺序由 MAE 给 |
| 控制道 | 64 bit 握手 | LIC/MAE/CCU/L2 | 透明转发，独立于数据网 |

正向信号为 `en/din/be/addr/src`，反向为 `ready`；写入完成回程为 `valid+src`，没有 ready。

## 3 明确不属于 HUB

HUB 不生成/累加地址，不做环形回绕，不解析 payload，不做 VC/credit/flit 语义，不维护 WCNT/RCNT，不判单位完成，不执行归约、量化、合并、排序或中心仲裁。

## 4 不变量

- 同一链路保序；链路级数只改变延迟。
- H2C 道 n 只读象限 n；C2H 核 n 只写象限 n。
- 多播只在掩码内复制，目的链路分别按 ready 成交。
- `src` 只由发令方解释，完成计数只在发令方/CCU。
- 控制网和数据网不保证先后；端点必须能处理先到/后到两种顺序。
