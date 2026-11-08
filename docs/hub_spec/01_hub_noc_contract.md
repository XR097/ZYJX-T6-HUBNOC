# HUB_NOC 当前合同

## 1 边界

HUB_NOC 位于中央 L2 与四核之间，包含四条 H2C 道、四条 C2H 通路和命令网。HUB_NOC 只传输数据、地址、核掩码、`src` 和 ready/写入握手，不发令、不生成地址、不解析载荷、不做归约或完成判定。

## 2 数据接口

| 接口 | 宽度 | 语义 |
|---|---:|---|
| L2 象限 n → H2C n | 4 × 32 B | MAE_ENG 给 L2 读 `en/addr`；busy 时保持重发 |
| H2C n → 四核 LDP | 每核 4 × 32 B | 目的 addr/seg/be/核掩码/src 由 MAE 给；分叉点按各核 ready 取走 |
| 四核集成输出端口 → C2H | 每核 1 × 32 B | CCU 在核内选择来源；HUB 只见一路 |
| C2H → L2WP | 4 × 32 B | 核 n 只写象限 n；ready 反向传回并可门控 CCU |
| 命令网 | 64 bit | LIC、MAE_ENG、CCU、L2 间透明转发；标量不走此网 |

## 3 不属于 HUB_NOC

MAE_CRU 不连接 HUB_NOC；它通过 NI 读口读取 L2、通过 NI-L2C 写回 L2。HUB_IDN 是独立篇，连接 NI IDN 出口与四核 NWB。

HUB_NOC 不维护 VC/credit/flit/`last`/`nw8`，不维护 L2 完成计数，不做 H2C 第二源 MUX，不做 C2H 目标分流。

## 4 不变量

- 同一链路保序，级数只改变延迟。
- H2C 道 n 只读象限 n；C2H 核 n 只写象限 n。
- H2C 多播只在核掩码内复制；掩码为单位参数，随每拍流水，各目的 ready 独立。
- 最终写入握手由 L2/LDP 回到发令方；C2H 不带号，H2C 带 src，回程均无 ready；HUB 只转交。
- C2H ready 低时反压传到集成输出端口发送 FIFO，FIFO 将满的 stall_tx 门控 CCU（协议 §7.1）。
