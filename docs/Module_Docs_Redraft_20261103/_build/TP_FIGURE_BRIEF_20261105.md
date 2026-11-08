# 传输协议篇四张架构图任务书（交 Opus Agent）

> Owner: WangYizhao｜2026-11-05｜目标文档：`Module_Docs_Redraft_20261103/DATA_TRANSFER_PROTOCOL.md`｜图写到 `figs/`，脚本放 `_build/draw_tp_arch.py`，渲染到 `_build/preview/`｜用户 11-05 原话："你产出的物理接线完全是错的……给我产出一个结构正确，连接线指向正确，布线美观的架构图"；风格以用户给的参考图为准（PPT 美学：色块、圆角、阴影、端口标名、箭头标信号、图例在图内）。

## 0 四张图与它们各自要回答的问题

| 图 | 文件名 | 回答什么 |
|---|---|---|
| A | FIG-TP-ARCH-LINKS.svg | 全芯片有哪些模块、哪些物理链路、每条链路的位宽与方向、属于三种总线中的哪一种 |
| B | FIG-TP-ARCH-INCORE.svg | 一个计算核内，哪些单元与 L1 之间有 SRAM 口总线，信号是什么，stall 从谁到谁 |
| C | FIG-TP-ARCH-INTERCORE.svg | 核间 AXI4-Stream 数据网：hub 两级、L2、NI_INT、四核三个端口，每条链路五个信号与方向，"目的核 = 哪组线" |
| D | FIG-TP-ARCH-CTRL.svg | 命令与标量网：端点（LIC、MAE_ENG、hub 控制道、NI、各核 CCU / L1 命令单元、CRU）、每类消息的方向、两槽命令 SRAM |

## 1 全芯片物理接线（已按 V1.7_3 条款核实，V1.8 改动已并入；图 A 必须与此一致）

来源：`Claude_Design_Spec/V1.7_3/Modules/HUB_NOC.md` §1.1–1.2，`CORE_INTEGRATION.md` §1.2 与〔CORE-F-410〕，`SPEC_INTEGRATION_V1.7.md` 2.2–2.7、2.3.7，`LIC.md` §1，`V1.8_DESIGN_REVISIONS.md` V18-TP-01…16。

### 1.1 模块

- **第一排（控制与访存）**：CIF、LIC（含 LOOP）、MAE_ENG、NI_EXT。
- **第二排（挂在 hub 上）**：CRU、HUB NoC、中央 L2、NI_INT。
- **第三排**：计算核 ×4（CC0–CC3），每核 = CCU + L1 + MXU + VNU。
- **芯片外 / SoC 侧**：DDR（LPDDR5，控制器 P0 / P1 / P2）、片上互联（SoC 设计方）、M55（经 APB）、系统 DMA / HSRAM（经片上互联）。

### 1.2 链路清单（每条一行；"类"是三种总线之一：核间数据网 / 命令与标量网 / 对外 AXI / 核内）

| # | 从 | 到 | 内容 | 位宽 / 拍 | 类 | 依据 |
|---|---|---|---|---|---|---|
| 1 | L2 象限 $n$ 读口（$n$ = 0…3） | HUB-DN 道 $n$ | 下行数据 | 4 × 32 B | 核间数据网 | HUB_NOC §1.1："L2 象限 $n_q$ 的读口固定接 H2C 第 $n_q$ 道" |
| 2 | HUB-DN 道 $n$ | **每个核**的 H2C 第 $n$ 道（按目的掩码，多播 = 同拍驱动几核） | 下行数据 | 每核 4 道 × 32 B | 核间数据网 | HUB_NOC §1.2 H2C 行 |
| 3 | 每核 C2H（发送桥） | HUB-UP（hub 中心） | 上行数据 | 每核 32 B | 核间数据网 | HUB_NOC §1.2 C2H 行 |
| 4 | HUB-UP → L2WP | L2 写口 | 四核上行汇流 | 32 B | 核间数据网 | HUB_NOC §1.2 L2 写行；L2 只有 L2WP 与 NI 写两个写口 |
| 5 | HUB-UP | CRU（挂在 hub 中心） | K 切分部分和（AEB 直达口）；V1.8 下位图 / 标量 / 事件改走命令与标量网 | — | 核间数据网（部分和）/ 命令与标量网（标量） | HUB_NOC §1.2 CRU 入口；V18-TP-06 / 07 |
| 6 | CRU | HUB-DN（RSP / GO） | 归约值；GO | — | 命令与标量网（V1.8） | HUB_NOC §1.2 CRU 出口 |
| 7 | NI_INT | **每个核**的 IDN 入口（NWB） | 入站数据直接分发进核 L1 | 芯片合计 32 B = 4 道 × 8 B，道 $i$ 固定接核 $i$ | 核间数据网 | CORE_INTEGRATION §1.2 IDN 行；V18-TP-15 |
| 8 | NI_INT（NI-L2C） | L2 NI 写口 | 入站数据落 L2（含 PIN 写入） | 32 B | 核间数据网（NI 侧） | SPEC_INTEGRATION 2.2 节 NI-L2C 行；"NI 写 L2 与 NI 返回走 L2 自己的 NI 写口与 NI 返回读口，不经 hub" |
| 9 | L2 NI 返回读口 | NI_INT → NI_EXT | 写回 DDR / M1 | 32 B | 核间数据网（NI 侧） | 同上 |
| 10 | NI_EXT M0 | DDR 控制器 P0 | 主存专线 | 256 bit AXI 主口 | 对外 AXI | SPEC_INTEGRATION 2.2.3 / 2.4 |
| 11 | NI_EXT M1 | 片上互联（→ HSRAM / LSRAM / DDR P2 / FMC） | 调用描述符、表、结果 | 64 bit AXI 主口，$f_{\mathrm{IO}}$ | 对外 AXI | 同上 |
| 12 | 片上互联（系统 DMA / FMC） | NI_EXT PIN | 外设数据直写 L2 外设输入区 | 64 bit AXI 从口 | 对外 AXI | 同上 |
| 13 | M55 | CIF | 描述符指针、门铃、邮箱、停止命令；中断回 M55 | APB 32 bit | 对外 | SPEC_INTEGRATION 时钟与端口表；LIC §1.1 |
| 14 | CIF ↔ LIC | | 门铃 / 指针 / 停止；完成与异常事件 | 片内 | 命令与标量网 | LIC §1.1 |
| 15 | LIC ↔ MAE_ENG | | MAE 命令（搬运、端点配置、M1 写）；完成计数、端点收妥 | 片内 | 命令与标量网 | LIC §1.1 |
| 16 | LIC ↔ hub 控制口 | | 下：位点命令 / Fusion 段 / GO 分发 / 阈值装载；上：GO 通知（CRU 发）、核事件、barrier 超时 | 64 bit Stream（V1.8） | 命令与标量网 | HUB_NOC §1.2 控制口；LIC-R-350"控制信息只经 hub 与 MAE 本地口" |
| 17 | hub 控制道 ↔ **每个核**的 CCU | | 下：位点命令 / Fusion 段 / GO / 长度转发；上：事件 / 位点完成 / 对象长度报告 | 64 bit Stream | 命令与标量网 | V18-TP-07（物理走 hub 控制道） |
| 18 | MAE_ENG ↔ hub 控制口 | | 下：H2C 搬运命令、Hub / CRU 端点配置、C2H 发送命令（转发到核 L1 命令单元）；上：完成报告 | 64 bit Stream | 命令与标量网 | HUB_NOC §1.2 端点配置 / 完成报告行；V18-TP-07 |
| 19 | MAE_ENG ↔ NI_INT | | 下：IDN 搬运命令（地址与顺序）；上：完成 | 片内 | 命令与标量网 | SPEC_INTEGRATION 2.7.1"MAE 只生成地址、NI 不改字" |
| 20 | NI_EXT ↔ NI_INT | | 入站数据（NIB）、返回数据 | 片内 | 核间数据网（NI 侧） | SPEC_INTEGRATION 2.7.1 |
| 21 | NI_EXT M1 读返回 → LIC | | 调用描述符、KV 计划、表镜像 | 片内 | 命令与标量网 | LIC §1.1 |

**硬性规则**：四核之间没有直连（HUB_NOC §1.1）；每核对外只有 H2C 入、C2H 出、IDN 入三个数据端口（CORE-F-410）加命令与标量网口；LIC 没有直达核的线、没有直写 hub / CRU 端点的口（LIC-R-350）；NI 写 L2 与 NI 返回不经 hub；L2 的四个象限读口只接 HUB-DN 四道；hub 全芯片一个。

### 1.3 旧图的错误（不得再犯）

1. 把 LIC 画成一条绕开 hub、直达各核 CCU 的"控制总线"——错，LIC 的控制只经 hub 控制口，物理走 hub 的控制道。
2. 把 L2 画成与 hub 并列的独立块、只有一条读一条写——错，L2 的四个象限读口分别接 HUB-DN 四道，写口只有 L2WP（来自 hub 中心）与 NI 写口（来自 NI_INT），另有 NI 返回读口。
3. 缺 CRU、缺 NI_EXT / NI_INT 的区分、缺 M0 / M1 / PIN / CIF-APB、缺 DDR 与片上互联。
4. 把 IDN 画成一条从 NI 拉到各核上方的总线——应画成 NI_INT 的 4 条 8 B 道各自直连一个核的 IDN 入口。
5. 标签压线、标签互相重叠、箭头方向与文字矛盾。

## 2 每张图必须包含的要素

### 图 A（全芯片物理链路）
- §1.1 的全部模块，按三排布置；芯片边界框；SoC 侧的 DDR、片上互联、M55 画在边界外。
- §1.2 的 21 条链路，每条标位宽与方向；三种总线三种颜色（核间数据网蓝、命令与标量网橙、对外 AXI 灰），核内总线只在核框内用青色示意。
- 多播画法：HUB-DN 道 $n$ 一分四到四核的第 $n$ 道（可用一根线分叉）。
- 图例；标题条写"全芯片物理链路"。

### 图 B（一核内 SRAM 口总线与分级 stall）
依据 `DATA_TRANSFER_PROTOCOL.md` §3、§4 与 `L1_SRAM.md` §2：
- L1 画两堆，每堆 W（bank 0–7）/ S（尺度 SRAM）/ A（bank 8–11）三类；堆位由地址给。
- 口：CCU → L1 的 en / wea / addr（所有口）；权重 lane 读口 16 × 16 B + 尺度行 → MXU 供数（4 pod）；激活类口 4 × (dout 32 B · vld / din 32 B) ↔ VNU、出口级、pod 激活记录缓冲（经 L1 外选择器）；接收桥 LDP（H2C 4 道）/ NWB（IDN）→ L1 写口；C2H 发送侧读口。
- 推送链：供数 → 阵列 → 出口级 → VNU → 发送桥；AEB → C2H 直达口。
- stall：stall_mxu[0..3]、stall_vnu[i]、stall_tx 到 CCU；相邻级 stall 各一根；写口无 stall。
- 图内注明：写当拍、读 1 拍、无 ready / busy；阈值 = 深度 − L。

### 图 C（核间 Stream 数据网）
- hub 两级：中心（HUB-UP 汇流 → L2WP；CRU 挂中心；HUB-ATT 可略）与 4 个 HUB-DN 道发端；每个道发端读 L2 象限 $n$、扇出到四核的第 $n$ 道。
- 四核各：接收桥 LDP × 4（H2C）、接收桥 NWB（IDN）、发送桥（C2H）、L1 两堆。
- NI_INT：4 条 8 B 道直连四核 NWB；NI-L2C → L2 NI 写口；L2 NI 返回读口 → NI_INT。
- 每条链路标 TVALID / TREADY / TDATA 32 B / TLAST / TUSER 与方向（可在图例统一标一次，线上只标名与位宽）。
- 注明：目的核 = 哪组线有 TVALID，源核 = 线号，道 $i$ 直连核 $i$；接收桥 TREADY 恒高；hub 内扇入仲裁拉低 TREADY。

### 图 D（命令与标量网）
- 端点：CIF（→ M55）、LIC、MAE_ENG、hub 控制道 / 命令执行单元、NI 命令执行单元、CRU、四核各自的 CCU 端点（两槽命令 SRAM + 当前成员 RF + 短消息 RF 队列）与 L1 命令单元、VNU / AEB 标量发出口。
- 消息与方向（按 `DATA_TRANSFER_PROTOCOL.md` §8.1 的表）：位点命令 / Fusion 段 / GO（LIC → hub → CCU）；事件 / 位点完成（CCU → hub → LIC）；H2C 搬运命令与完成（MAE ↔ hub）；IDN 搬运命令与完成（MAE ↔ NI）；C2H 发送命令（MAE → hub → L1 命令单元）与完成（L1 → hub → MAE）；对象长度报告（CCU → hub → MAE）；长度转发（hub → 目的核 CCU）；标量（VNU / AEB → CRU，CRU → CCU / VNU）；致命错误（LIC → CIF → M55）。
- **LIC、MAE 到核的所有消息都经 hub 控制道，不画直达线。**
- 注明：64 bit Stream，TLAST = 消息结束，端点不经 L1 / L2 SRAM，Fusion 段整段一次分发、CCU 本地按块循环。

## 3 工具与产出

- 手写 SVG（Python 生成即可，不用 figkit3 布线器）；画布 1920 × 1080；字体 Microsoft YaHei / Arial；可用 `<filter>` 阴影、圆角、渐变。
- 渲染：`F:\QQ_Agent\vendor\napcat-shell\node.exe _build\render.cjs figs _build\preview`（在 `Module_Docs_Redraft_20261103` 目录下运行），然后用 Read 看 PNG。
- 每张图至少迭代 3 轮：渲染 → 逐项对照 §1.2 与 §2 的清单 → 修正；最终提交前把检查清单逐条打勾写进报告。
- 不改 `DATA_TRANSFER_PROTOCOL.md` 正文；图注由主会话回写。
- 交付：四个 SVG、四个 PNG、脚本、检查报告（每张图：模块清单 ✓、链路清单逐条 ✓、无压线 / 无重叠 ✓、方向与文字一致 ✓）。
