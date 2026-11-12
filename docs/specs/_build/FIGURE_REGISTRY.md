# 图件登记表（自动生成）：specs

> 由 `_build/build_figure_registry.py` 扫描生成，不要手改；手写说明放各篇的 FIGURE_REGISTRY_<篇>.md。扫描范围：本目录下全部 *.md（图引用）与 _build/*.py（生图函数）。

## CCU_STAGING.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-DORG-L1-STREAM | 2.14 来自 DATA_ORGANIZATION（V1.8 第二轮回改） | —（未找到生图函数） | — | ✓ |

## CIF.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-CIF-IF | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-CIF-STOP-RESUME | 3.5 调用中途的停止与继续：请求 / 应答，继续后不丢、不重 | —（未找到生图函数） | — | ✓ |

## DATA_ORGANIZATION.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-DORG-PIECE-BLOCKS | 2.1 总览图与格式汇总 | —（未找到生图函数） | — | ✓ |
| FIG-TP-OBJECT-ALIGN | 2.3 对齐：SRAM 支持紧密存储，数据组织默认 32 B 对齐 | —（未找到生图函数） | — | ✓ |
| FIG-TP-FIXED-ITEM | 2.7 定长项与标量 | —（未找到生图函数） | — | ✓ |
| FIG-DORG-READSET | 3.5.4 数值例 | —（未找到生图函数） | — | ✓ |
| FIG-DORG-COLPOS | 3.5.4 数值例 | —（未找到生图函数） | — | ✓ |
| FIG-DORG-SPLIT-T | 3.6.2 核间按 T 切分：各核算不同 token，产出留本核 | —（未找到生图函数） | — | ✓ |
| FIG-DORG-SPLIT-M | 3.6.3 核间按 M 切分：各核算不同输出通道，四个象限同址 | —（未找到生图函数） | — | ✓ |
| FIG-DORG-SPLIT-K | 3.6.4 核间按 K 切分：各核算部分和，同址异象限，MAE_CRU 归约 | —（未找到生图函数） | — | ✓ |
| FIG-TP-WINDOW-GATHER | 3.6.8 权重驻留位点的产出：每个权重窗口一组数据块，MAE 按元数据项聚集 | —（未找到生图函数） | — | ✓ |
| FIG-DORG-DDR-STD | 3.7.1 权重标准布局：一拍一个 $k$ 行 × 4 个列组，尺度与 bias 另成数据块 | —（未找到生图函数） | — | ✓ |
| FIG-DORG-DDR-COL | 3.7.2 权重列深度优先布局：一拍一列 64 个连续 $k$，尺度另成数据块 | —（未找到生图函数） | — | ✓ |
| FIG-DORG-DDR-ACT | 3.7.3 激活值、残差与 K / V 在 DDR | —（未找到生图函数） | — | ✓ |

## DATA_TRANSFER_PROTOCOL.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-TP-ARCH-INTERCORE | 2.2 核间链路：带地址的握手写流 | —（未找到生图函数） | — | ✓ |
| FIG-TP-ARCH-INCORE | 2.3 核内 RRAM 口 | —（未找到生图函数） | — | ✓ |
| FIG-TP-STALL-CHAIN | 2.4 核内相邻级 stall 信号 | —（未找到生图函数） | — | ✓ |
| FIG-TP-ARCH-CTRL | 2.5 命令网 | —（未找到生图函数） | — | ✓ |
| FIG-TP-ADDR-ACCUM | 3.3.1 核内：CCU 从基址累加 | —（未找到生图函数） | — | ✓ |
| FIG-TP-LENGTH-REPORT | 3.13 变长数据块：CCU 发送并报告，MAE 先搬元数据项、握手数满后发写完通知 | —（未找到生图函数） | — | ✓ |
| FIG-TP-INCORE-TIMING | 3.15 核内 RRAM 的时序：写当拍、读 1 拍，时序确定 | —（未找到生图函数） | — | ✓ |
| FIG-TP-CTRL-MSG | 3.19 命令网：端点按 addr 写入，指令写全才生效 | —（未找到生图函数） | — | ✓ |
| FIG-TP-ADDR-MAP | 7.1 段内地址到 bank 与深度的换算 | —（未找到生图函数） | — | ✓ |
| FIG-TP-BYTE-START | 7.2 字节移位：首地址不在字边界时 SRAM 内部拆到相邻 bank | —（未找到生图函数） | — | ✓ |
| FIG-TP-COMPACT | 7.2 字节移位：首地址不在字边界时 SRAM 内部拆到相邻 bank | —（未找到生图函数） | — | ✓ |
| FIG-TP-STREAM-BEAT | 7.5 接收桥与 L2 写入口：每道一条 FIFO、轮流、握手计数器 | —（未找到生图函数） | — | ✓ |

## HUB_IDN.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-HUB_IDN-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-HUB_IDN-CORE-SET | 3.3 几核共享 M0 带宽：MAE_ENG 把连续存储字轮流排给各核 | —（未找到生图函数） | — | ✓ |
| FIG-HUB_IDN-MCAST | 7.3 多播数值例：一个慢核只让自己晚收 | —（未找到生图函数） | — | ✓ |

## HUB_NOC.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-HUB_NOC-ARCH-DATA | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-HUB_NOC-ARCH-CTRL | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-HUB_NOC-ACK | 3.6 写入握手逐核回发令方，hub 里不汇总 | —（未找到生图函数） | — | ✓ |
| FIG-HUB_NOC-MCAST | 7.2 多播分叉点：一级链路块 + 各核已取标记，不另配存储 | —（未找到生图函数） | — | ✓ |

## L1_LANDING_BRIDGE.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-L1_LANDING_BRIDGE-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-L1_LANDING_BRIDGE-PACK | 7.2 轮到时取队头连续的 1–4 项；有效字节不足 32 的一项结束本次请求 | —（未找到生图函数） | — | ✓ |
| FIG-L1_LANDING_BRIDGE-RR | 7.3 道间按拍轮流，未选中的道保留资格 | —（未找到生图函数） | — | ✓ |
| FIG-L1_LANDING_BRIDGE-ACK | 7.5 握手计数器：写进后按拍数加，之后每拍沿本道回一个 | —（未找到生图函数） | — | ✓ |

## L1_SRAM.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-L1_SRAM-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-L1_SRAM-TIGHT | 3.3 紧密存储：数据可从任意字节起连续写入、首尾相接，不补齐 | —（未找到生图函数） | — | ✓ |
| FIG-L1_SRAM-LANE-PICK | 3.6 W 类读口取字：读集里的行或列按读集次序读出、每路带"哪些 pod 收"，读什么交什么 | —（未找到生图函数） | — | ✓ |
| FIG-L1_SRAM-BANKS | 7.1 存储组织：每堆 W 类 4 个 bank + A 类 4 个 bank，按字交织 | —（未找到生图函数） | — | ✓ |
| FIG-L1_SRAM-MAP-W | 7.3 W 类读口第 $b$ 路接第 $b$ 个 bank；列字区的参考落位 | —（未找到生图函数） | — | ✓ |
| FIG-L1_SRAM-PINGPONG | 7.8 用法例：两堆 ping-pong 与核内环形回绕 | —（未找到生图函数） | — | ✓ |
| FIG-L1_SRAM-RING | 7.8 用法例：两堆 ping-pong 与核内环形回绕 | —（未找到生图函数） | — | ✓ |
| FIG-L1_SRAM-KHI-RESIDENT-VS-REREAD | 7.9 用法例：精算 K hi 的两种来源 | —（未找到生图函数） | — | ✓ |

## L2_SRAM.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-L2_SRAM-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-L2_SRAM-TIGHT | 3.3 紧密存储：数据可从任意字节起连续写入、首尾相接，不补齐 | —（未找到生图函数） | — | ✓ |
| FIG-L2_SRAM-MAP-HEAP | 7.2 段内地址到 bank 与深度的换算 | —（未找到生图函数） | — | ✓ |

## L3PU_EXTERNAL_INFORMATION.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-INFO-FOUR-KINDS | 2.1 架构图与接口汇总：五类信息的进入口 | —（未找到生图函数） | — | ✓ |

## MAE_CRU.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_CRU-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_CRU-SUM | 3.2 逐元素相加（归约）：解码后逐元素求和，加法次序按象限固定 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_CRU-RESID | 3.3 逐元素相加（残差加）：归约结果与 L2 里的残差相加，一次编码写回残差流 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_CRU-READSET | 3.6 读集合并：按位取并 | —（未找到生图函数） | — | ✓ |

## MAE_DSU.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_DSU-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_DSU-TRANSPOSE-STD | 3.3 转置的定义：输入、输出次序与尾块（以标准布局 → 行字区为例） | —（未找到生图函数） | — | ✓ |
| FIG-MAE_DSU-TRANSPOSE | 3.4 列深度优先权重送训练核：转置（4 bit、$J = 64$、$N = 64$） | —（未找到生图函数） | — | ✓ |
| FIG-MAE_DSU-TWOPLANE | 3.6 直通：只给地址 | —（未找到生图函数） | — | ✓ |

## MAE_ENG.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-TP-LENGTH-REPORT | 3.19 发出报告：按地址配给指令 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_ENG-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_ENG-ARITH | 3.6.2 算术生成器：几级规律跳变 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_ENG-LIST | 3.6.3 列表驱动生成器：外层循环换成列表项 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_ENG-QSPLICE | 3.10.3 紧凑 token 记录的四部分在合并送中怎样落位 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_ENG-KHI-GATHER | 3.12 精算 K hi 驻留 / 重读：只差 hi 段从 L2 还是从 DDR 取 | —（未找到生图函数） | — | ✓ |

## MAE_INTEGRATION.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_INTEGRATION-ARCH-DATA | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_INTEGRATION-ARCH-CTRL | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_INTEGRATION-PATH | 3.4 按口对看整组的数据路径 | —（未找到生图函数） | — | ✓ |

## MAE_NI_EXT.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_NI_EXT-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MAE_NI_EXT-PIN-WORDPACK | 7.3 PIN 写入拍的切法与数值例 | —（未找到生图函数） | — | ✓ |

## MAE_NI_INT.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_NI_INT-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |

## MXU_ARR.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MXU_ARR-IF | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MXU_ARR-DIGITS | 3.2 一种乘法：4 bit 权重数字 × 激活有效数 | —（未找到生图函数） | — | ✓ |
| FIG-MXU_ARR-TREE | 7.2 分段归约树 | —（未找到生图函数） | — | ✓ |

## MXU_CONTROLLER.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MXU_CONTROLLER-IF | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MXU_CONTROLLER-ORDER | 3.2 给到达的数据排位置：权重字按读集内序号认，激活码按固定次序数 | —（未找到生图函数） | — | ✓ |

## MXU_FEED.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MXU_FEED-IF | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MXU_FEED-SLOT | 3.2 权重缓冲：装与取互不等待 | —（未找到生图函数） | — | ✓ |
| FIG-MXU_FEED-COMPACT | 3.3 按选择位图取数 | —（未找到生图函数） | — | ✓ |
| FIG-MXU_FEED-LANE-OFFSET | 3.6.2 尺度沿归约维逐位置不同时：每条数字道一个指数偏移 | —（未找到生图函数） | — | ✓ |

## MXU_INTEGRATION.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MXU-IF | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-MXU-MODE-IN | 3.3.1 输入稀疏：只读被选中的归约位置 | —（未找到生图函数） | — | ✓ |
| FIG-MXU-MODE-OUT | 3.3.2 输出稀疏：只算被选中的输出通道 | —（未找到生图函数） | — | ✓ |
| FIG-MXU-POD | 7.1 一个 pod 的结构与一拍的数据流 | —（未找到生图函数） | — | ✓ |

## ONCHIP_DATAPATH_ARCH.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-TP-ARCH-INTERCORE | 2.4 核间链路：一组信号、单向、点到点 | —（未找到生图函数） | — | ✓ |
| FIG-TP-ARCH-INCORE | 2.2 核内口：L1 的 RRAM 读口、写口与 L1 外的使用者入口 | —（未找到生图函数） | — | ✓ |
| FIG-TP-ARCH-CTRL | 2.5 命令网与专用信号组 | —（未找到生图函数） | — | ✓ |
| FIG-TP-ARCH-LINKS | 2.1 架构图与接口汇总：全芯片部件、三种总线与全部口 | —（未找到生图函数） | — | ✓ |

## TRANSFER_DATA_REGISTRY.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-TP-ARCH-LINKS | 2.1 架构图与接口汇总：条目路径引用的口 | —（未找到生图函数） | — | ✓ |

## VNU_CONTROLLER.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_CONTROLLER-IF | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_CONTROLLER-REORDER | 3.5 接收 AEB 条目并排回原来的次序 | —（未找到生图函数） | — | ✓ |

## VNU_EPI.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_EPI-CONN | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_EPI-RESID | 3.3 残差加：核内残差位点，两种残差存储格式都支持 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_EPI-ROUND | 7.2 可选做法：条目整轮先进寄存器堆、两个分堆轮换 | —（未找到生图函数） | — | ✓ |

## VNU_INTEGRATION.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_INTEGRATION-ARCH | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_INTEGRATION-RF-SPLIT | 7.1 共用寄存器堆的参考用途、容量与分堆 | —（未找到生图函数） | — | ✓ |

## VNU_LOSS.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_LOSS-CONN | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_LOSS-ORDER | 3.4 输出合同：词号升序去重，dz 与列表同序压紧 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_LOSS-LOGPROB | 3.7 截断分布统计：对 K_top 项分布求所选 token 的 log-prob | —（未找到生图函数） | — | ✓ |

## VNU_NLU.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_NLU-CONN | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_NLU-NORM-SPLIT | 3.4 沿向量的归约与归一化：先求统计量，再缩放 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_NLU-ONLINE-SOFTMAX | 3.7 在线 softmax 与 attention 输出累加：分数分组到达，按更新组统一基准 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_NLU-STREAM-SUM | 3.9 跨向量的流式累加：逐通道累加，可从读回的部分和继续 | —（未找到生图函数） | — | ✓ |

## VNU_OPT.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_OPT-CONN | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |

## VNU_QNT.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_QNT-CONN | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_QNT-MX-ENCODE | 3.2.2 默认选码规则 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_QNT-AMAX-SPLIT | 3.2.5 尺度的两种来源：本核求出与跨核取最大 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_QNT-PLANE-BITSPLIT | 3.3 两平面表示：一个码按位拆成 hi / lo | —（未找到生图函数） | — | ✓ |
| FIG-VNU_QNT-KEEP-PACK | 3.4 按判决位压紧：去掉不读的元素，其余按原序连续存放 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_QNT-DECODE | 3.6 解码与还原：码 × 尺度，还原成计算用的值 | —（未找到生图函数） | — | ✓ |

## VNU_SEL.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_SEL-CONN | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_SEL-THRESH | 3.3.2 评分按 BF16 比较，平方尺度阈值由编译链换算 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_SEL-TOPK | 3.5.3 LM Head 的 TOPK 重算词号列表由 SEL 产出 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_SEL-MASK | 3.8.3 屏蔽优先 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_SEL-RELATIVE | 7.2 相对阈值最大值的两遍暂存 | —（未找到生图函数） | — | ✓ |

## VNU_SMP.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_SMP-CONN | 2.1 架构图与接口汇总 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_SMP-PICK | 3.2 按随机数取项：取最大项，或沿词号升序累积到第一个超过 $u$ 的项 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_SMP-ACCEPT-GREEDY | 3.3.3 须支持的情形 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_SMP-ACCEPT-RS | 3.3.3 须支持的情形 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_SMP-BACKFILL | 3.6.1 补算开启时：运算用全码重算的精确值 | —（未找到生图函数） | — | ✓ |
| FIG-VNU_SMP-TREE | 7.2 截断建树的参考算法：best-first | —（未找到生图函数） | — | ✓ |

## 核对

- 有 SVG 但无文档引用（0）：无
- 被引用但 SVG 不存在（0）：无
- 被引用但找不到生图函数（115）：FIG-CIF-IF、FIG-CIF-STOP-RESUME、FIG-DORG-COLPOS、FIG-DORG-DDR-ACT、FIG-DORG-DDR-COL、FIG-DORG-DDR-STD、FIG-DORG-L1-STREAM、FIG-DORG-PIECE-BLOCKS、FIG-DORG-READSET、FIG-DORG-SPLIT-K、FIG-DORG-SPLIT-M、FIG-DORG-SPLIT-T、FIG-HUB_IDN-ARCH、FIG-HUB_IDN-CORE-SET、FIG-HUB_IDN-MCAST、FIG-HUB_NOC-ACK、FIG-HUB_NOC-ARCH-CTRL、FIG-HUB_NOC-ARCH-DATA、FIG-HUB_NOC-MCAST、FIG-INFO-FOUR-KINDS、FIG-L1_LANDING_BRIDGE-ACK、FIG-L1_LANDING_BRIDGE-ARCH、FIG-L1_LANDING_BRIDGE-PACK、FIG-L1_LANDING_BRIDGE-RR、FIG-L1_SRAM-ARCH、FIG-L1_SRAM-BANKS、FIG-L1_SRAM-KHI-RESIDENT-VS-REREAD、FIG-L1_SRAM-LANE-PICK、FIG-L1_SRAM-MAP-W、FIG-L1_SRAM-PINGPONG、FIG-L1_SRAM-RING、FIG-L1_SRAM-TIGHT、FIG-L2_SRAM-ARCH、FIG-L2_SRAM-MAP-HEAP、FIG-L2_SRAM-TIGHT、FIG-MAE_CRU-ARCH、FIG-MAE_CRU-READSET、FIG-MAE_CRU-RESID、FIG-MAE_CRU-SUM、FIG-MAE_DSU-ARCH、FIG-MAE_DSU-TRANSPOSE、FIG-MAE_DSU-TRANSPOSE-STD、FIG-MAE_DSU-TWOPLANE、FIG-MAE_ENG-ARCH、FIG-MAE_ENG-ARITH、FIG-MAE_ENG-KHI-GATHER、FIG-MAE_ENG-LIST、FIG-MAE_ENG-QSPLICE、FIG-MAE_INTEGRATION-ARCH-CTRL、FIG-MAE_INTEGRATION-ARCH-DATA、FIG-MAE_INTEGRATION-PATH、FIG-MAE_NI_EXT-ARCH、FIG-MAE_NI_EXT-PIN-WORDPACK、FIG-MAE_NI_INT-ARCH、FIG-MXU-IF、FIG-MXU-MODE-IN、FIG-MXU-MODE-OUT、FIG-MXU-POD、FIG-MXU_ARR-DIGITS、FIG-MXU_ARR-IF、FIG-MXU_ARR-TREE、FIG-MXU_CONTROLLER-IF、FIG-MXU_CONTROLLER-ORDER、FIG-MXU_FEED-COMPACT、FIG-MXU_FEED-IF、FIG-MXU_FEED-LANE-OFFSET、FIG-MXU_FEED-SLOT、FIG-TP-ADDR-ACCUM、FIG-TP-ADDR-MAP、FIG-TP-ARCH-CTRL、FIG-TP-ARCH-INCORE、FIG-TP-ARCH-INTERCORE、FIG-TP-ARCH-LINKS、FIG-TP-BYTE-START、FIG-TP-COMPACT、FIG-TP-CTRL-MSG、FIG-TP-FIXED-ITEM、FIG-TP-INCORE-TIMING、FIG-TP-LENGTH-REPORT、FIG-TP-OBJECT-ALIGN、FIG-TP-STALL-CHAIN、FIG-TP-STREAM-BEAT、FIG-TP-WINDOW-GATHER、FIG-VNU_CONTROLLER-IF、FIG-VNU_CONTROLLER-REORDER、FIG-VNU_EPI-CONN、FIG-VNU_EPI-RESID、FIG-VNU_EPI-ROUND、FIG-VNU_INTEGRATION-ARCH、FIG-VNU_INTEGRATION-RF-SPLIT、FIG-VNU_LOSS-CONN、FIG-VNU_LOSS-LOGPROB、FIG-VNU_LOSS-ORDER、FIG-VNU_NLU-CONN、FIG-VNU_NLU-NORM-SPLIT、FIG-VNU_NLU-ONLINE-SOFTMAX、FIG-VNU_NLU-STREAM-SUM、FIG-VNU_OPT-CONN、FIG-VNU_QNT-AMAX-SPLIT、FIG-VNU_QNT-CONN、FIG-VNU_QNT-DECODE、FIG-VNU_QNT-KEEP-PACK、FIG-VNU_QNT-MX-ENCODE、FIG-VNU_QNT-PLANE-BITSPLIT、FIG-VNU_SEL-CONN、FIG-VNU_SEL-MASK、FIG-VNU_SEL-RELATIVE、FIG-VNU_SEL-THRESH、FIG-VNU_SEL-TOPK、FIG-VNU_SMP-ACCEPT-GREEDY、FIG-VNU_SMP-ACCEPT-RS、FIG-VNU_SMP-BACKFILL、FIG-VNU_SMP-CONN、FIG-VNU_SMP-PICK、FIG-VNU_SMP-TREE
