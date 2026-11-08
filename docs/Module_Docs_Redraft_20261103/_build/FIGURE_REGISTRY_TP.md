# 传输协议篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-05｜用途：后续调整任何一张图时，从这里找到它的脚本、函数、数值来源与正文位置；改图后按"再生成"一节重跑并重新看 PNG。用户 11-05："我希望你保存到这些生图的函数和图片的关系，便于咱们后续可能的调整"。

## 再生成

在 `Final_Architecture/Module_Docs_Redraft_20261103/` 目录下：

```bash
python -X utf8 -I _build/draw_tp_arch.py
```

```bash
python -X utf8 -I _build/draw_transfer_protocol.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

第一条出四张架构图，第二条出十张数值小例，第三条把 `figs/` 全部 SVG 渲染成 `_build/preview/*.png`（渲染后用 Read 逐张看）。两个脚本互不覆盖：架构图只在 `draw_tp_arch.py`；`draw_transfer_protocol.py` 里已没有架构图函数。

> 11-05 夜第二次修订（V18-TP-26…34、V18-NIE-02，任务书 `_build/TP_REVISION_BRIEF_20261105_NIGHT.md`）：改了 ARCH-LINKS、ARCH-INCORE、ARCH-INTERCORE、ARCH-CTRL（四个函数）与 ADDR-ACCUM、STREAM-BEAT、LENGTH-REPORT、CTRL-MSG（四个函数）；无退役函数。图里不再出现"AXI4-Stream""等齐""同拍驱动""固定时延""27 bit""道掩码""报完成"。
> 11-06 修订（V18-TP-35…38，附录 `_build/TP_REVISION_BRIEF_20261106_ADDENDUM.md`）：改了 ARCH-LINKS、ARCH-INTERCORE、ARCH-CTRL（`draw_tp_arch.py`）与 LENGTH-REPORT、CTRL-MSG（`draw_transfer_protocol.py`）；无退役函数、无新图。C2H 改标"CCU 发令"，L1 框注改"各入链路写计数 → CCU"，命令网链路注"通用链路块实例"，ARCH-CTRL 撤 MAE → 核的"C2H 发送命令"线与"L1 命令单元"框（改为"L1 发送侧（C2H）· CCU 发令"框），"对象长度报告"改"发出报告"；LENGTH-REPORT 改为"bump 分配 → CCU 发送 → 发出报告"六步。图里不再出现"排空""长度待报""长度报告""C2H 发送命令""目的不同可交错"。
> 11-06 第三次修订（V18-TP-41…44，任务书 `_build/TP_RENAME_NOLAST_BRIEF_20261106.md`）：信号改名、撤 last。改了 ARCH-INCORE、ARCH-INTERCORE、ARCH-CTRL（`draw_tp_arch.py`）与 ADDR-ACCUM、ADDR-MAP、STALL-CHAIN、STREAM-BEAT、LENGTH-REPORT、CTRL-MSG（`draw_transfer_protocol.py`）的文字；STREAM-BEAT 的末拍行改为"搬运引擎内计数（不上链路）"，CTRL-MSG 改为"首字含长度、无末字标记"；无新图、无退役。
> 11-06 第四次修订（V18-L2-03，任务书 `_build/TP_L2WP128_BRIEF_20261106.md`）：改了 ARCH-LINKS、ARCH-INTERCORE（`draw_tp_arch.py`）：HUB-UP 改为"dest 分流 · 不扇入 · 四核直通 L2 四条写链路"，hub → L2 的 L2WP 由 1 条改画 4 条（每核一条 32 B），NI 写口 1 条不变；INTERCORE 信号框末行改"HUB-UP 只按 dest 分流、不仲裁"，框宽 690 → 665 给四条竖线让位。ARCH-CTRL 无相关字样，未改。无新图、无退役。图里不再出现"扇入""按拍仲裁""L2 共享写口"。
> 11-06 晚修订（V18-MAE-11…18，任务书 `_build/MAE_CRU_MERGE_BRIEF_20261106.md`，Agent A）：改了 ARCH-LINKS、ARCH-INTERCORE、ARCH-CTRL（`draw_tp_arch.py` 的 `fig_links / fig_intercore / fig_ctrl`，新增公共件 `mae_frame()` 画 MAE 组正交多边形虚线框）与 LENGTH-REPORT（`draw_transfer_protocol.py` 的 `fig_length_report`）；ARCH-INCORE 与其余数值小例未改、未重跑。CRU 框移出 hub、进 MAE 组框并改标 MAE_CRU；LINKS 画布高 1080 → 1150，图例移到芯片边界下方（给 MAE 组 L 形框让位）；LIC ⇄ MAE 线改标"指令 · 标号 / 完成通知 · 标号"；LENGTH-REPORT 由 6 步改 7 步、画布高 560 → 620。图里不再出现"操作 18""完成计数""CRU（hub 中心）""端点配置""对象 7""1 个单位"。
> 11-06 深夜第二次（V18-TP-50、写法"地址不说指针"，子代理改）：ARCH-INTERCORE 信号框改"所有核间写链路都回写入握手"、L1 框注改"写入项数 → CCU · 写入握手回发令方"；ARCH-CTRL 的 MAE_ENG 框注"比对 L2 / CRU 入口写计数"改"数写入握手（按 src）"、底注"hub 不报完成（发令方数写入握手）"；STREAM-BEAT 的多播说明改"每核记下一拍要取的缓冲地址"；LENGTH-REPORT 第 7 步分写核内消费与核间执行完。无新图、无退役，四张架构图自检 0 问题。
> 11-06 深夜（V18-L2-04、V18-TP-47…49，协调者串行改）：ARCH-LINKS 的 L2WP 四条线改为核 $k$ 只进象限 $k$（`fig_links()` 里 `lx, yk, xq = 630 + 20k, 486 + 4k, QX[k] + 55`，四条横段 y 递增、互不交叉），"ENG → H2C 道"标签移到 (1466, 494)；ARCH-INTERCORE 的 L2WP 四条线同样只进各自象限（`ys, xv, yh = 336 − 9k, 724 − 8k, 252 − 5k`），信号框加 `src` 与"写 L2 的链路另回写入握手"，读口标签下移到 y 278；LENGTH-REPORT 改为"按上限分槽 → CCU 发送 → 握手数满后发出报告 → 按槽读"七步，常量 `WIN_BASE_ROW, LR_SLOT_ROWS = 200, 20`、`RECS_LEN = [520, 403, 389]`，断言各记录 17 / 13 / 13 个存储字、共 43 项、窗口 60（变量名 `LR_SLOT_ROWS` 避开 TOKEN-SLOT 图的 `SLOT_ROWS`）。无新图、无退役。

## 一、四张架构图（`_build/draw_tp_arch.py`，Opus Agent 11-05 产出；检查报告 `_build/TP_FIGURE_CHECK_20261105.md`）

| 图文件 | 函数 | 正文位置 | 画什么 | 依据 |
|---|---|---|---|---|
| `figs/FIG-TP-ARCH-LINKS.svg` | `fig_links()`（+ `mae_frame()`） | §1 | 全芯片物理链路（画布 1920 × 1150，图例在芯片边界下方）：M55 / SoC 片上互联 / DDR、CIF、LIC、**MAE 组 L 形虚线框**（上排 MAE_ENG"指令引擎 · 搬运引擎（逐拍地址）"+ NI_EXT；右列"NI_INT / MAE_IDN"框（含 MAE_DSU、NI-L2C（五源）、IDN 4 条 8 B 链路）+ **MAE_CRU**）、L2 四象限、hub（中心 + 4 个 H2C 道（多播缓冲）+ 控制道；不再含 CRU，组名"HUB NoC（全芯片一个；HUB 组只剩 HUB_NOC）"）、四核；三种总线三色；LIC ⇄ MAE_ENG 标"指令 · 标号 / 完成通知 · 标号"；MAE ↔ NI 线标"搬运指令 / DDR 写响应"；MAE_ENG ⇄ hub 控制道标"H2C 搬运指令（hub 随之长度转发）/ → MAE：发出报告"；hub 中心 → MAE_CRU 一根"dest = CRU"（代表每核一条 32 B），MAE_CRU → H2C 道 3"归约值 → H2C 道"（第二源，代表），MAE_CRU ⇄ NI_INT 两根"写 L2 · 读路径"，hub 控制道 ⇄ MAE_CRU 一根命令网线"标量 · 独立端点"；四核 C2H 标"C2H · CCU 发令"；hub → L2 四条 L2WP 线（每核一条 32 B）+ NI 写口一条（11-06 V18-L2-03） | 任务书 `_build/TP_FIGURE_BRIEF_20261105.md` §1.2 的 21 条链路清单；11-05 夜任务书 §1 规则 1、2、5、9；11-06 附录 TP-35；11-06 晚 `MAE_CRU_MERGE_BRIEF_20261106.md` §1 规则 1–6 |
| `figs/FIG-TP-ARCH-INCORE.svg` | `fig_incore()` | §3（stall 走向也在此图，§4 不另出图） | 一核内：CCU → L1 的 en / wea / addr；L1 两堆 × W / S / A；lane 读口 → 供数；激活类口经选择器 ↔ 出口级 / VNU；接收桥 LDP / NWB → 写口（addr = addr）；NWB 下接 4 条 8 B 链路（来自 MAE_IDN，每条一个攒字寄存器）；L1 发送侧读口 → 发送桥；AEB 桥；全部 stall | 正文 §3、§4、§6；L1_SRAM.md §2 |
| `figs/FIG-TP-ARCH-INTERCORE.svg` | `fig_intercore()` | §5 | 左上信号框（en / din / be / addr 24 bit，与核内 RRAM 口同名；dest 1 bit 每条都带、只在 C2H 上可为 1；每级 = 通用链路块（skid 可配）、addr 由 CCU（C2H）/ MAE 通道（其余）给出、无单位标记、多播各目的独立取走、仲裁只在发令方给的单位边界切换）；hub 中心（C2H 分流：只按 dest 分流、不扇入不仲裁，四核各一路 → L2WP 四条写链路（每核一条 32 B）→ L2 写口 4 条，dest = CRU → MAE_CRU；11-06 V18-L2-03）+ 4 个 H2C 道（多播缓冲、各核独立取走）；L2 象限 $n$ → 道 $n$ → 四核第 $n$ 道（分叉点 = 多播）；四核 C2H（发送桥"C2H · CCU 发令"）→ C2H 分流；**右上 MAE 组倒 L 形虚线框**：上"NI_INT · MAE_IDN"框（MAE_DSU · NI-L2C（五源）· 读返回分路），右列 **MAE_CRU**（C2H 分流 → MAE_CRU 一根"C2H dest = CRU（每核 1 × 32 B）→ MAE_CRU"；MAE_CRU → H2C 道 3"归约值 → H2C 道"；MAE_CRU ⇄ NI_INT 两根"写 L2 · 读路径"）与 MAE_IDN 四个说明标签；MAE_IDN 4 条 8 B 链路（x 1856–1892）按链路分配接各核 NWB；L1 框注"各入链路写计数 → CCU" | 正文 §2.6、§5、§6、§7.4；HUB_NOC §1.1–1.2；V18-TP-26…38、V18-L2-03、V18-MAE-11 / 12 |
| `figs/FIG-TP-ARCH-CTRL.svg` | `fig_ctrl()` | §8 | **11-06 晚改**：MAE 组虚线框（上排 MAE_ENG"指令入口可预存下一条 · 多条指令同时执行 / 收发出报告 · 比对 L2 / CRU 入口写计数 / 每条执行完 → 带指令标号通知 LIC"、NI 指令执行单元；下伸一块放 **MAE_CRU**"命令与标量网独立端点（标量队列）"）；LIC ⇄ MAE_ENG 标"搬运指令 + 指令标号（可多条）/ 完成通知（指令标号）"；LIC 框"收各核位点完成 + 数 MAE 完成通知 → 发 GO"；MAE_ENG ⇄ MAE_CRU 一根棕色组内线"组内：合并参数 ↓ · 合并完成 ↑"（不是命令网）；MAE_CRU ⇄ hub 控制道两根"标量"；hub 组收窄到 y 452–590、控制道框 y 486–576；撤"操作 18""合并完成 → MAE 完成计数""Hub / CRU 端点配置"；CCU 队列框"MAE_CRU 合并值"。以下为此前内容：命令与标量网（64 bit 握手消息流）端点（CIF、LIC、MAE_ENG、NI 命令执行单元、hub 控制道、CRU、四核 CCU 端点 / L1 发送侧（C2H）框）与每类消息方向；无"完成 → MAE"线（完成按写计数）；11-06 撤 MAE → 核的 C2H 发送命令线，L1 发送侧框写"CCU 发令：读 L1，给逐拍 addr / dest"，CCU ↑ 标"发出报告 → MAE"，副标题注"en / ready / data 64 bit，消息长度在首字、无末字标记；与数据网同为通用链路块实例"；左上说明框"数据到达而位点指令未装入 = 致命错误（长度转发晚到不算）"；NI → MAE 标"DDR 写响应"；VNU 不在本网上，只画"VNU 寄存器"与核内 CCU ⇄ VNU 两条短箭头；GO 与屏障超时在 LIC 框；CRU → MAE 一条"合并完成"线；CCU 的当前 / 下一条指令寄存器 + Fusion-CCU 段 SRAM + 短消息 RF 队列 | 正文 §8.1 端点表、§7.4、§8.3 前段、§8.5；V1.8 TP-21…24、TP-28、TP-35、TP-38 |

脚本内部的公共件：`Fig` 类（标题条、色块、分组框、折线、带底色标签、图例）、自检（标签不出画布 / 不互叠 / 不压线、线不穿框、不相连的交叉自动加跳线弧、分叉点画实心点），任何一项不满足脚本直接报错退出。改坐标后先跑脚本看是否报错，再渲染看图。

## 二、十张数值 / 时序小例（`_build/draw_transfer_protocol.py`，基类 `_build/svgkit_num.py`）

每张图的数值由脚本顶部的常量算出并 `assert`，改例子先改常量，断言通不过说明例子与规则矛盾。

| 图文件 | 函数 | 正文位置 | 例子与断言 | 常量 |
|---|---|---|---|---|
| `figs/FIG-TP-ADDR-ACCUM.svg` | `fig_addr_accum()` | §2.4.1（核内例） | 核内例（底部红字注明核间 addr 由 MAE 搬运引擎给出）；按 RRAM 信号逐拍：写一个 4 条变长记录（40 / 24 / 56 / 20 B，记录级对齐各占 2 / 1 / 2 / 1 行）的对象（6 拍 en / wea / addr / din 含补 0，CCU 行计数 r，第 7 拍回绕）；再读记录 2（首行 3，两拍 addr = 行 9、10，dout）；断言每拍 din 内容、各记录首行号 | `REC`、`REC_ROWS`、`FIRST`、`BASE_ROW`、`RING_L`、`write_beats()`、`R2_*` |
| `figs/FIG-TP-ADDR-MAP.svg` | `fig_addr_map()` | §2.2 | 同一地址 [h][A][行 300] 在两堆、四核落 bank 8 深 75；断言 `(BANK_, DEPTH_) == (8, 75)` | `A_BANKS`、`ROWN` |
| `figs/FIG-TP-INCORE-TIMING.svg` | `fig_timing()` | §3.3 | 拍 0 写 a、拍 1 读 a、拍 2–3 读 b c、拍 4 写 d、拍 5 读 d；断言返回拍 = 发出拍 + 1 | `OPS`、`RET` |
| `figs/FIG-TP-STREAM-BEAT.svg` | `fig_stream_beat()` | §5.4 | 6 拍单位 addr = [1][A][行 40…45]，链路上无末拍标记（第 4 行改为"搬运引擎内计数 k / 6（不上链路）"），经 H2C 道 0 的分叉点送往核 0、核 2（11-06 深夜 V18-TP-53 起撤多播缓冲，逐拍模型在共用模块 `mcast_fork_sim.py`）；核 0 写进侧 ready 恒 1、核 2 在拍 2、3 为 0，每核分支容量 4（skid + LDP 入口 FIFO，示意）；断言分叉点停收 0 拍、核 0 拍 1–6 写进 k = 0–5、核 2 拍 1,4,5,6,7,8 写进、核 2 分支占用最大 3；多播到核 0 / 2 落 bank 8,9,10,11,8,9 深 10,10,10,10,11,11 | `UNIT_ROWS`、`UBASE`、`BEATS`、`NT`、`SB_CAP`、`READY`、`SB` |
| `figs/FIG-TP-LENGTH-REPORT.svg` | `fig_length_report()` | §7.3 | **11-06 晚改为 7 步（画布 1500 × 620）**：第 4 步发出报告 = (目的起始地址 = L2 窗口基址, 写入项数 41, 记录数 3, 尾字 32 B)、不带对象标识；第 5 步 MAE 按"第 k 份报告 ↔ 第 k 条'源来自核 0 的 C2H'指令"对应、以 41 设（源核 0, 象限）写计数目标、达到后带指令标号通知 LIC；第 6 步 LIC 收通知后下发 L2 → 核 2 的 H2C 搬运指令（长度取自该报告）、hub 长度转发；第 7 步核 2 比对；红字加"报告按地址对应指令"（V18-MAE-13 / 14）。以下为此前内容：按位点窗口静态分配（窗口 [字 200, 字 264)，上限 64 个存储字，算法侧按位点给；11-06 第二次改，V18-TP-40）、实际 3 条记录 1,312 B = 41 个存储字的消息序（6 步）：位点指令（输出对象窗口；发送指令含目的 L2 窗口基址、"按对象实际长度"）→ QNT 写 → 核 0 CCU 经 C2H 发 41 拍（addr / dest 由 CCU 给，链路上不标末拍）→ 发出报告（对象 7, 1 个单位, 41 个存储字, 3 条, 尾字 32 B）→ MAE 见 L2 写计数达 41 后发 H2C 命令并长度转发 → 核 2 接收桥写计数达 41；红字"窗口静态分配；CCU 先发、发完再报实际长度；读方按实际长度读、不读整个窗口" | `WIN_BASE_ROW`、`WIN_ROWS`、`RECS_LEN`、`ROWS_USED`（断言 ROWS_USED ≤ WIN_ROWS）；正文 §7.3、§2.6；V18-TP-35 / 37 / 40 |
| `figs/FIG-TP-STALL-CHAIN.svg` | `fig_stall_chain()` | §4 开头 | 推送链 7 级 + 5 根 stall；阈值例：深度 8、在途 2 拍 → 占 6 即拉 | `CHAIN`、`STALLS`、`DEPTH`、`L_LAT` |
| `figs/FIG-TP-CTRL-MSG.svg` | `fig_ctrl_msg()` | §8.6 | 首字 + 3 成员字 = 49 拍进 Fusion-CCU 段 SRAM；成员逐条进"下一条"寄存器；远离 MAE 的搬运引擎 → MAE 一条可选的发送完成（通道号）1 拍进 MAE 队列；MAE 端点队列框写"发送完成 / 发出报告 / CRU 合并完成"（11-06） | `SEG_WORDS`、`BEATS_PER_WORD`、`SEG_BEATS` |
| `figs/FIG-TP-OBJECT-ALIGN.svg` | `fig_object_align()` | §9.1 | 记录级对齐：对象头 8 B 与记录 22 / 30 / 18 / 10 B 各占 1 行、各自补 0，共 5 行；断言占行数、首行号、补 0 字节数 | `OHDR`、`RLEN`、`ITEMS`、`ROWS_OF`、`FIRST_ROW`、`PADS` |
| `figs/FIG-TP-SLOT-COUNT.svg` | `fig_slot_count()` | §9.8 末 | K 平面 52 个 key、组 32、末组 20 / 32 有效 | `NKEY`、`G` |
| `figs/FIG-TP-TOKEN-SLOT.svg` | `fig_token_slot()` | §9.7 | 4 token × 3 MX 组按 (组, token) 到达、按 token 槽拼接；断言各槽已写字节 [34, 31, 31, 26] ≤ 4 行 | `T`、`NG`、`SEGLEN`、`SLOT_ROWS`、`ARRIVAL`、`OFFS` |

## 三、改图时的约定

- 正文图注（图下那一段）与图里的数字必须同源：改常量后同时改正文图注。
- 架构图的接线以任务书 §1.2 链路清单为准；接线变了先改清单（并在 V1.8 登记），再改图。
- 每次改完都跑渲染、用 Read 看 PNG，再把改动写进 `_build/TP_FIGURE_CHECK_20261105.md` 的"迭代"一节。

## 三、紧密访存数值小例（`_build/draw_compact.py`，11-05 夜，V18-TP-25）

| 图文件 | 函数 | 正文位置 | 画什么 | 断言 |
|---|---|---|---|---|
| `figs/FIG-TP-COMPACT.svg` | `draw('FIG-TP-COMPACT.svg', 4, …)` | 协议篇 §2.5 | A 类 4 bank：20 B 记录从字节 248 起，前 8 B 在第 7 个存储字字节 24–31（bank 11、深度 1），后 12 B 在第 8 个存储字字节 0–11（bank 8、深度 2）；两次带字节写使能的写；读回移位 24 | 两次写落不同 bank；未选字节保持原值；读回与写入逐字节相同 |
| `figs/FIG-L1_SRAM-COMPACT-A.svg` | `draw('FIG-L1_SRAM-COMPACT-A.svg', 8, …)` | L1 篇 §3.4a | 同一条记录在 A 类 8 bank 配置下跨 bank 7（借来的 W1）、深度 0 与 bank 8、深度 1 | 同上 |

再生成：`python -X utf8 -I _build/draw_compact.py`。常量 `A_START = 248`、`A_LEN = 20` 改了要同步两篇的图下说明。

> 11-06 深夜第三次（V18-TP-51 / NAME-04）：撤 dest 后重跑相关生图脚本，图上"dest = CRU 分支"改为"去 MAE_CRU 的分支"，C2H 分流改为"按 CCU 的通路选择"，信号框不再列 dest，远端引擎的短消息改名"执行完成"；自检均 0 问题。

> 11-06 深夜（用户："现在你的实心点和分叉点功能重叠了"）：ARCH-INTERCORE 的 H2C 改为道框（= 分叉点）底边直接引出四路到四核 LDP 第 n 口（出口 x = QX[n] + 18 + 40k，每路一层横线 y = 512 + 6(4n + k)），撤"道 n"总线与线上实心点；自检 0 问题。ARCH-LINKS 总览图暂保留"道 n"总线画法（hub 框内只有约 4 层横线的空间），待用户定。
> 11-06 深夜（用户："MAE 给的归约槽应该到 4 个 H2C，而当前的画法只到了一个"）：ARCH-INTERCORE 与 ARCH-LINKS 的 MAE_CRU 输出改为一条总线分到四条 H2C 道入口（V18-MAE-22 可进任一道；INTERCORE 总线 y = 292、LINKS 总线 y = 515，各道入口 x = QX[n] + 160），标签改"归约值 → 任一 H2C 道"；LINKS 的"读口 32 B"标签缩为"读 32 B"；自检 0 问题。
