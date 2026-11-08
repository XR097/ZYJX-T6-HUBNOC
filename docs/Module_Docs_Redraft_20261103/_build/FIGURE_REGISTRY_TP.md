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
> 11-07 夜（V18-TP-58 / L1-13 / L2-05 / MAE-33，协调者串行改）：`draw_transfer_protocol.py` 的 `DATE` 改 11-07；LENGTH-REPORT 改为"紧挨写 + 长度表 → CCU 发送 → 握手数满后发出报告 → MAE 按表读、搬完后转发应写量"七步，常量 `WIN_BASE, LR_CAP = 6400, 640`、`RECS_LEN = [520, 403, 389]`、`LT_ADDR = 8320`，断言起点 [0, 520, 923]、41 + 1 = 42 项；OBJECT-ALIGN 改为紧挨版（见下表）；SLOT-COUNT 改名 **FIXED-ITEM**（`fig_fixed_item()`，"对象头计数"改"指令给出有效个数"）；TOKEN-SLOT 退役（`_retired_fig_token_slot()`，SVG 移 `figs/_retired_20261107/`），新图 **WINDOW-GATHER**（`fig_window_gather()`）。L1 `draw_l1_sram.py` 的 MAP-A、L2 `draw_l2_sram.py` 的 OBJ-ALIGN、MAE_ENG `draw_mae_eng.py` 的 QSPLICE 同步改为紧挨 / 长度表 / 四区域版（各篇登记表）。
> 11-08（V18-NLU-06 / MXU-06 / TP-59 / TP-60 / TP-61 / TP-62，架构篇正文产出）：`draw_tp_arch.py` 的 `DATE` 改 11-08；ARCH-INCORE 撤"MXU 出口级"块（阵列副标题"FBA · AEB（MXU 到此为止）"，VNU 块注 NLU 含出口级，推送线标"AEB 条目"、stall 标"AEB ready"，集成输出端口副标题"CCU 选：L1 发送侧 / VNU 输出（MXU 输出经出口级透传）"，撤 MXU 输出竖线）；ARCH-CTRL 的集成输出端口框改"CCU 选来源：L1 发送侧 / VNU 输出"、NI 控制道底注改"IDN 搬运：段选 · 基址 · 应写量"。**四张架构图自 11-08 起属于架构篇 `ONCHIP_DATAPATH_ARCH.md`（§1 / §3 / §4 / §5），协议篇切分后只引用**；下表"正文位置"已改为架构篇节号，"引用于"列登记引用它的文件（P4）。STALL-CHAIN 同日重画见第二节。
> 11-08 晚（V18-HUB-04，IDN 每核一条 32 B 链路；用户要求优化 INTERCORE 左上角）：ARCH-LINKS 的 HUB_IDN 块改"32 B 进 · 按核集合分发 · 多播分叉"，NI_INT → HUB_IDN 由 4 根 8 B 线改 1 根 32 B（`nib0`），各核 IDN 标签改"IDN 1 × 32 B"；ARCH-INCORE 的 NWB 块改"IDN 1 条 32 B · ready = FIFO 未满"、下方 4 根短线改 1 根；ARCH-INTERCORE：信号说明撤"IDN 链路 8 B / 4 拍同一字地址"、改 4 行，NI_INT 块"IDN 出口 → HUB_IDN 1 × 32 B"，HUB_IDN 块"按每字的核集合分发 / 接几核即分叉点（已取位）/ 每核 1 条 32 B 链路"，各核 NWB 块"IDN 1 条 32 B · 整字直写"，NI_INT → HUB_IDN 1 根线；**左上角 L2WP 与 C2H 两框合成一个框"C2H → L2WP：四核各一路直通"（x 100–460，y 330–455），四核 C2H 线按 `C2HX = [330, 400, 425, 450]` 从框底进、从框顶同一 x 出，横段 `yh = 237 + 7k` 递增、四条互不交叉；HUB_NOC 组标题缩短为"HUB 组 · HUB_NOC"给线让位**；无新图、无退役；四图自检 0 问题。
> 11-08 晚第二次（协议篇切分，目录稿第三版）：协议篇章序改为 §3 核间 / §4 发送许可与完成 / §5 RRAM / §6 stall / §7 桥 / §8 命令网，下表十张数值小例的"正文位置"已换成新节号（STREAM-BEAT、COMPACT → §3；LENGTH-REPORT → §4；INCORE-TIMING、ADDR-ACCUM、ADDR-MAP → §5；STALL-CHAIN → §6；CTRL-MSG → §8）；**OBJECT-ALIGN、FIXED-ITEM、WINDOW-GATHER 随旧 §9 切到数据组织篇底稿 `DATA_ORGANIZATION.md`（编号暂留 9.x），生图函数仍在 `draw_transfer_protocol.py`，不移动**；四张 ARCH 图属架构篇不变。新旧对照 `_build/TP_SECTION_MAP_20261108.md`。
> 11-08 下午（数据组织篇正文产出）：OBJECT-ALIGN、FIXED-ITEM、WINDOW-GATHER 的正文位置改为数据组织篇 §1.2 / §3 / §5.7（图注里"③ 档对象 / ② 档"的措辞随改名审计一起改）；数据组织篇自己的七张新图在 `draw_data_org.py`，登记表 `FIGURE_REGISTRY_DORG.md`。

## 一、四张架构图（`_build/draw_tp_arch.py`，Opus Agent 11-05 产出，11-08 起归架构篇；检查报告 `_build/TP_FIGURE_CHECK_20261105.md`）

| 图文件 | 函数 | 正文位置 | 画什么（现状，11-08） | 依据 | 引用于 |
|---|---|---|---|---|---|
| `figs/FIG-TP-ARCH-LINKS.svg` | `fig_links()`（+ `mae_frame()`） | 架构篇 §1 | 全芯片物理链路（画布 1920 × 1150，图例在芯片边界下方）：M55 / SoC 片上互联 / DDR、CIF、LIC（含 LOOP）、**MAE 组虚线框（五单元：MAE_ENG、NI_EXT、NI_INT（MAE_DSU · NI-L2C 五源 · 读返回分路 · NI 控制道）、MAE_CRU"从 L2 读四象限 · 合并 · 写回 L2"，只与 NI_INT 相连）**、中央 L2 四象限（NI 写口 32 B、NI 读口 4 × 32 B）、**HUB 组两个虚线框：HUB_NOC（hub 中心"C2H：四核直通 L2 四条写链路 · 不扇入 · 不分路"、H2C 道 0–3 各读象限 n · 多播分叉、hub 控制道）与 HUB_IDN（32 B 进 · 按核集合分发 · 多播分叉）**、四核（L1 两堆 × W / S / A · LDP × 4 · NWB · 发送侧，CCU / MXU / VNU）；三种总线三色；LIC ⇄ MAE_ENG"指令 · 标号 / 完成通知 · 标号"；MAE_ENG → NI_INT / HUB_IDN"解码后的控制"；核 → MAE_ENG"发出报告"经 hub 控制道；L2WP 四条"核 k → 象限 k"；C2H 标"CCU 发令"；每核 IDN 1 × 32 B（11-08 晚 V18-HUB-04） | `_build/TP_FIGURE_BRIEF_20261105.md` §1.2 链路清单；V18-TP-26…62、L2-03 / 04、HUB-01…03、CRU-07、MAE-32 | 架构篇 §1；协议篇 §1（切分后只引用） |
| `figs/FIG-TP-ARCH-INCORE.svg` | `fig_incore()` | 架构篇 §3（stall 走向也在此图；协议篇 §6 另有 FIG-TP-STALL-CHAIN） | 一核内：CCU → L1 的 en / wea / addr；L1 两堆 × W / S / A；lane 读口 → 供数；供数 → 阵列（FBA · AEB，MXU 到此为止）→ "AEB 条目"推送线 → VNU（NLU 含出口级子模块），反向"AEB ready"；激活类口经选择器 ↔ VNU；接收桥 LDP / NWB → 写口（addr = 到达的 addr）；NWB 下接 1 条 32 B 链路（来自 HUB_IDN，11-08 晚 V18-HUB-04）；**集成输出端口"CCU 选：L1 发送侧 / VNU 输出（MXU 输出经出口级透传）"→ C2H**；全部 stall（红虚线） | 架构篇 §3；协议篇 §5 / §6；L1_SRAM.md §2；V18-TP-56 / 59、NLU-06 / MXU-06 | 架构篇 §3；协议篇 §5（切分后只引用） |
| `figs/FIG-TP-ARCH-INTERCORE.svg` | `fig_intercore()` | 架构篇 §4 | 左上信号框（发 → 收 en / din 32 B（IDN 8 B）/ be / addr 24 / src；**去哪个存储由链路决定：C2H 只到 L2（无 dest）；IDN 与 H2C 同一种链路、IDN 每拍一个整字**；收 → 发 ready，所有核间写链路回写入握手；每级 = 通用链路块；addr 由 CCU（C2H）/ MAE 搬运引擎（其余）给；无单位标记；多播各目的独立取走；跨核合并：各核写 L2 → MAE_CRU 读四象限）；中央 L2（写口 L2WP × 4、NI 写口；读口象限 0–3、NI 返回）；HUB_NOC 框："C2H → L2WP：四核各一路直通"一个框（核 n → 象限 n，框内无逻辑，四条线从框底进、框顶同 x 出；11-08 晚合框）、H2C 道 0–3（读象限 n → 分叉点 → 四核第 n 口）；右侧 MAE 组框：NI_INT（IDN 出口 → HUB_IDN 1 × 32 B）、MAE_CRU（从 L2 读四象限 · 合并 · 写回 L2，只与 NI_INT 相连）；HUB 组另一框 HUB_IDN（按每字的核集合分发 · 接几核即分叉点 · 每核 1 条 32 B 链路，11-08 晚 V18-HUB-04）；四核：输出端口（C2H 唯一来源）、接收桥 LDP × 4（ready = FIFO 未满）、L1 两堆（按 addr 落 bank · 写入项数 → CCU · 写入握手回发令方）、接收桥 NWB（IDN 1 条 32 B · 整字直写） | 架构篇 §4；协议篇 §3；HUB_NOC §1.1–1.2；V18-TP-26…61、L2-03 / 04、HUB-03、CRU-07、MAE-32 | 架构篇 §4；协议篇 §3（切分后只引用） |
| `figs/FIG-TP-ARCH-CTRL.svg` | `fig_ctrl()` | 架构篇 §5 | 命令网（64 bit 握手消息流，en / ready / data，首字含长度、无末字标记，与数据网同为通用链路块实例）端点与每类消息方向：M55 ⇄ CIF（APB / IRQ，非命令网）；CIF ⇄ LIC（门铃 · 指针 · 停止 / 完成 · 致命错误）；LIC ⇄ MAE_ENG（搬运指令 + 指令标号（可多条）/ 完成通知（指令标号））；MAE 组框（MAE_ENG"指令入口可预存下一条 · 多条指令同时执行 / 收发出报告 · 数写入握手（按 src）/ 每条执行完 → 带指令标号通知 LIC"、NI 控制道口"不收指令 · 长度转发由搬运引擎给"）；hub 控制道（LIC ⇄ 各核 CCU 位点指令 / Fusion 段 / GO 下行、事件 / 位点完成上行；CCU 发出报告 → MAE；H2C 道收 MAE_ENG 的逐拍地址与核掩码；hub 不报完成）；四核 CCU 端点（Fusion-CCU 段 SRAM、下一条 / 当前指令寄存器 1,024 bit、短消息 RF 队列（GO · 长度转发）、ready 条件）与**集成输出端口"CCU 选来源：L1 发送侧 / VNU 输出 · 给逐拍 L2 addr · 不 ready 停算"**；底注"NI 控制道：长度转发（IDN 搬运：段选 · 基址 · 应写量）→ 目的核 CCU 短消息队列"；VNU、MAE_CRU 不在网上（标量不走本网，经 C2H → L2 → MAE_CRU） | 架构篇 §5；协议篇 §8；V18-TP-21…24 / 28 / 35 / 38 / 55 / 58 / 59、MAE-27 | 架构篇 §5；协议篇 §8（切分后只引用） |

脚本内部的公共件：`Fig` 类（标题条、色块、分组框、折线、带底色标签、图例）、自检（标签不出画布 / 不互叠 / 不压线、线不穿框、不相连的交叉自动加跳线弧、分叉点画实心点），任何一项不满足脚本直接报错退出。改坐标后先跑脚本看是否报错，再渲染看图。

## 二、十张数值 / 时序小例（`_build/draw_transfer_protocol.py`，基类 `_build/svgkit_num.py`）

每张图的数值由脚本顶部的常量算出并 `assert`，改例子先改常量，断言通不过说明例子与规则矛盾。

| 图文件 | 函数 | 正文位置 | 例子与断言 | 常量 |
|---|---|---|---|---|
| `figs/FIG-TP-ADDR-ACCUM.svg` | `fig_addr_accum()` | §2.4.1（核内例） | 核内例（底部红字注明核间 addr 由 MAE 搬运引擎给出）；按 RRAM 信号逐拍：写一个 4 条变长记录（40 / 24 / 56 / 20 B，记录级对齐各占 2 / 1 / 2 / 1 行）的对象（6 拍 en / wea / addr / din 含补 0，CCU 行计数 r，第 7 拍回绕）；再读记录 2（首行 3，两拍 addr = 行 9、10，dout）；断言每拍 din 内容、各记录首行号 | `REC`、`REC_ROWS`、`FIRST`、`BASE_ROW`、`RING_L`、`write_beats()`、`R2_*` |
| `figs/FIG-TP-ADDR-MAP.svg` | `fig_addr_map()` | §2.2 | 同一地址 [h][A][行 300] 在两堆、四核落 bank 8 深 75；断言 `(BANK_, DEPTH_) == (8, 75)` | `A_BANKS`、`ROWN` |
| `figs/FIG-TP-INCORE-TIMING.svg` | `fig_timing()` | §5.3 | 拍 0 写 a、拍 1 读 a、拍 2–3 读 b c、拍 4 写 d、拍 5 读 d；断言返回拍 = 发出拍 + 1 | `OPS`、`RET` |
| `figs/FIG-TP-STREAM-BEAT.svg` | `fig_stream_beat()` | §3.4 | 6 拍单位 addr = [1][A][行 40…45]，链路上无末拍标记（第 4 行改为"搬运引擎内计数 k / 6（不上链路）"），经 H2C 道 0 的分叉点送往核 0、核 2（11-06 深夜 V18-TP-53 起撤多播缓冲，逐拍模型在共用模块 `mcast_fork_sim.py`）；核 0 写进侧 ready 恒 1、核 2 在拍 2、3 为 0，每核分支容量 4（skid + LDP 入口 FIFO，示意）；断言分叉点停收 0 拍、核 0 拍 1–6 写进 k = 0–5、核 2 拍 1,4,5,6,7,8 写进、核 2 分支占用最大 3；多播到核 0 / 2 落 bank 8,9,10,11,8,9 深 10,10,10,10,11,11 | `UNIT_ROWS`、`UBASE`、`BEATS`、`NT`、`SB_CAP`、`READY`、`SB` |
| `figs/FIG-TP-LENGTH-REPORT.svg` | `fig_length_report()` | §4.3 | **11-06 晚改为 7 步（画布 1500 × 620）**：第 4 步发出报告 = (目的起始地址 = L2 窗口基址, 写入项数 41, 记录数 3, 尾字 32 B)、不带对象标识；第 5 步 MAE 按"第 k 份报告 ↔ 第 k 条'源来自核 0 的 C2H'指令"对应、以 41 设（源核 0, 象限）写计数目标、达到后带指令标号通知 LIC；第 6 步 LIC 收通知后下发 L2 → 核 2 的 H2C 搬运指令（长度取自该报告）、hub 长度转发；第 7 步核 2 比对；红字加"报告按地址对应指令"（V18-MAE-13 / 14）。以下为此前内容：按位点窗口静态分配（窗口 [字 200, 字 264)，上限 64 个存储字，算法侧按位点给；11-06 第二次改，V18-TP-40）、实际 3 条记录 1,312 B = 41 个存储字的消息序（6 步）：位点指令（输出对象窗口；发送指令含目的 L2 窗口基址、"按对象实际长度"）→ QNT 写 → 核 0 CCU 经 C2H 发 41 拍（addr / dest 由 CCU 给，链路上不标末拍）→ 发出报告（对象 7, 1 个单位, 41 个存储字, 3 条, 尾字 32 B）→ MAE 见 L2 写计数达 41 后发 H2C 命令并长度转发 → 核 2 接收桥写计数达 41；红字"窗口静态分配；CCU 先发、发完再报实际长度；读方按实际长度读、不读整个窗口" | `WIN_BASE_ROW`、`WIN_ROWS`、`RECS_LEN`、`ROWS_USED`（断言 ROWS_USED ≤ WIN_ROWS）；正文 §4.3、§2.6；V18-TP-35 / 37 / 40 |
| `figs/FIG-TP-STALL-CHAIN.svg` | `fig_stall_chain()` | §6 开头 | 11-08 重画（用户："看起来像是 VNU Gating 住前面的所有模块"）：推送链 6 级；**相邻级握手 = 框上方短箭头**（阵列 → 供数、VNU → 阵列 AEB ready、写集合器 → VNU wr_stall，`ADJ`，断言只连相邻两框）；**到 CCU 的两根**（stall_mxu[p]、stall_vnu[i]，`TO_CCU`）画在框下方车道；**集成输出端口发送 FIFO 单独一行，两个来源都画出（L1 发送侧读出在 L1 读口下方、VNU 输出），stall_tx 沿最下方绕到 CCU 左侧进入 = 唯一全局门控**；阈值例：深度 8、在途 2 拍 → 占 6 即拉 | `CHAIN`、`ADJ`、`TO_CCU`、`DEPTH`、`L_LAT`（旧 `STALLS` 保留未用） |
| `figs/FIG-TP-CTRL-MSG.svg` | `fig_ctrl_msg()` | §8.5 | 首字 + 3 成员字 = 49 拍进 Fusion-CCU 段 SRAM；成员逐条进"下一条"寄存器；远离 MAE 的搬运引擎 → MAE 一条可选的发送完成（通道号）1 拍进 MAE 队列；MAE 端点队列框写"发送完成 / 发出报告 / CRU 合并完成"（11-06） | `SEG_WORDS`、`BEATS_PER_WORD`、`SEG_BEATS` |
| `figs/FIG-TP-OBJECT-ALIGN.svg` | `fig_object_align()` | 数据组织篇 §1.2 | 11-07 改：记录 22 / 30 / 18 / 10 B 从字节 64 起紧挨（起点 64 / 86 / 116 / 134，占字 2–4，末字用 16 B），长度表 8 B 在字节 256；断言起点、覆盖字、读记录 2 = 字 3–4 按 20 移位 | `OBJ_BASE`、`LT_BYTE`、`RLEN`、`RSTART`、`W0 / W1 / NW / TAIL_USED`、`RD_WORDS / RD_SHIFT` |
| `figs/FIG-TP-FIXED-ITEM.svg` | `fig_fixed_item()` | 数据组织篇 §3 | 原 FIG-TP-SLOT-COUNT（11-07 改名）：K 平面 52 个 key、tile 32、末 tile 20 / 32 有效，个数由指令给 | `NKEY`、`G` |
| `figs/FIG-TP-WINDOW-GATHER.svg` | `fig_window_gather()` | 数据组织篇 §5.7 | 11-07 新（取代 FIG-TP-TOKEN-SLOT，旧函数 `_retired_fig_token_slot()`）：3 个窗口对象各 4 片（[50,38,61,44] / [47,52,40,58] / [55,36,49,60] B）紧挨、各配长度表；聚集 token 1 = 从 4146 取 38、4655 取 52、5175 取 36，共 126 B；断言各片起点与聚集结果 | `WG_T`、`WG_NW`、`WG_LEN`、`WG_BASE`、`WG_START`、`WG_PIECES`、`WG_TOTAL` |

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
- **11-07（V18-HUB-01）**：`draw_tp_arch.py` 只改字、不动布局：MAE 组框标题"MAE 组（五单元）"；LINKS / INTERCORE 的 NI_INT 框改标"NI_INT / HUB_IDN""NI_INT · HUB_IDN"，副标题注"HUB_IDN（属 HUB 组）"，只为连线画在此框；LINKS 的 hub 组标题"HUB_NOC（全芯片一个；HUB_IDN 见右侧）"；IDN 链路标签与 INCORE 的"来自 HUB_IDN"。四图自检 0 项。
- **11-07 第二次（用户："总览图可以调整下，不需要把 HUB 的 NoC 部分和 IDN 部分放在一起，但是需要标注他们都属于 HUB"）**：新增 `hub_part()`（HUB 组虚线框）；LINKS 的 MAE 组框右列底边 716 → 636，HUB_IDN 单独放在 `hub_part(1693, 642, 204, 72, 'HUB 组')` 里，块 `(1702, 669, 188, 38)`，NI_INT → HUB_IDN 四道（x 1852–1882，y 480 → 669）与 HUB_IDN → 各核（y 707 起）分成两段；NoC 框标题"HUB 组 · HUB_NOC（全芯片一个）"。INTERCORE 的 MAE 组框底边 632 → 456（标题移到 y 440），HUB_IDN 放在 `hub_part(1703, 470, 204, 160, 'HUB 组')`，块 `(1712, 502, 188, 116)`，NI_INT → HUB_IDN 四道（MX，y 240 → 502）、HUB_IDN → 各核（y 618 起）；右侧四个说明标签并进 HUB_IDN 块副标题；hub 框标题"HUB 组 · HUB_NOC（全芯片一个）：中心 + 4 个 H2C 道发端"。四图自检 0 项。
- **11-07 晚（V18-CRU-07 / TP-55 / 56 / MAE-32 / HUB-03）**：LINKS / INTERCORE 撤 C2H 去 MAE_CRU、CRU → H2C 第二源、标量线，MAE_CRU 只连 NI_INT（读 · 写 L2）；核的发送桥改称集成输出端口；CTRL 撤 MAE_CRU 端点、VNU 寄存器块与标量消息，改名命令网；INCORE 撤 AEB 桥，MXU / VNU 输出可进集成输出端口，规则框改为"stall_tx 门控 CCU"。四图自检 0 项。
- **11-08（V18-NLU-06 / TP-59 / TP-60）**：INCORE（`fig_incore()`）撤"MXU 出口级"框：阵列框副标题"FBA · AEB（MXU 到此为止）"，推送链改为阵列 → VNU 一条（标签"AEB 条目"），stall 改为 VNU → 阵列的"AEB ready"，VNU 框注"NLU（含出口级子模块：AEB 分发 · 残差加 · 停放）"，集成输出端口副标题"CCU 选：L1 发送侧 / VNU 输出（MXU 输出经出口级透传）"，撤"MXU 输出"竖线与选择器 ↔ 出口级线，规则框"VNU（出口级）对 AEB 拉 ready"；STALL-CHAIN（`fig_stall_chain()`）`CHAIN` 去掉出口级一级（6 级）、`STALLS` 改 4 根（第 3 根"AEB ready 拉低"）；LENGTH-REPORT / OBJECT-ALIGN / WINDOW-GATHER 的长度表改 24 bit 表项（`LT_ROWS` 按 3 B 算，`len(RLEN) * 3 == 12`，OBJECT-ALIGN 表字 12 B），数字与断言不变。自检 0 项。上表 INCORE / STALL-CHAIN / OBJECT-ALIGN 三行中的"出口级 / 7 级 / 8 B"以本条为准。
