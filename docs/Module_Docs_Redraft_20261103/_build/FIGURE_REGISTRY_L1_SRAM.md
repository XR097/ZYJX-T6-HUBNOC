# L1 SRAM 篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-05 夜｜用途：调整 L1_SRAM.md 任何一张图时，从这里找到它的脚本、函数、数值来源与正文位置；改图后按"再生成"一节重跑并重新看 PNG。自动索引见 `_build/FIGURE_REGISTRY.md`（由协调者跑 `build_figure_registry.py`）。

## 再生成

在 `Final_Architecture/Module_Docs_Redraft_20261103/` 目录下：

```bash
python -X utf8 -I _build/draw_l1_arch.py
```

```bash
python -X utf8 -I _build/draw_l1_sram.py
```

```bash
python -X utf8 -I _build/draw_compact.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

第一条出架构图（复用 `draw_tp_arch.py` 的 `Fig` 类与自检：文字不重叠、不跨框、不压线，连线不穿色块，交叉自动跳线；任一项不满足脚本报错退出）；第二条出十一张数值 / 映射小例（基类 `svgkit_num.py` 的 `SvgF5`，数值由脚本顶部常量算出并 `assert`）；第三条出紧密访存两张（协议篇与本篇各一张）；第四条把 `figs/` 全部渲染成 `_build/preview/*.png`。

## 一、架构图（`_build/draw_l1_arch.py`）

| 图文件 | 函数 | 正文位置 | 画什么 | 依据 |
|---|---|---|---|---|
| `figs/FIG-L1_SRAM-ARCH.svg` | `fig_l1_arch()` | §2 | 两堆 × (W0 / W1 / A / S)；左侧 LDP × 4（H2C 链路 0–3，入口 FIFO + skid）、NWB（IDN 链路 0–3 来自 MAE_IDN，4 条独立 8 B 链路、各一个攒字寄存器）、核内写者 → W 类写集合口 / A 类写集合器 / S 类写口；右侧 lane 读口 → 4 个 pod 的 WWB、激活类读口 × 4 → 客户、发送侧 + 发送桥与 AEB 桥在 C2H 口前合并；上方 CCU（收 stall_tx 与各写计数；发令 C2H，经一条线给发送桥逐拍 addr / dest，单位边界不上链路）与 MAE_ENG（CCU → MAE 一条"发出报告"线）；发送桥框注"= CCU 的 C2H 通道"；C2H 标"按单位合并，AEB 优先" | 正文 §2、§6.4、§7、§8、§10；协议篇 §2.6、§5–§7；V18-TP-26…38 |

11-05 夜改动：图例"核间数据网"改"核间握手写流"；IDN 由一根线改为四条链路、标 MAE_IDN；撤"完成 → MAE"线，改为 MAE_ENG → 发送桥的"addr · dest"；CCU 改收"到达计数与排空"；C2H 标"addr 24 + dest"。

11-06 改动（V18-TP-35…38，附录 `_build/TP_REVISION_BRIEF_20261106_ADDENDUM.md`）：撤 MAE_ENG → CCU 的"发送命令"线与 MAE_ENG → 发送桥的"addr · dest"线，改为 CCU → MAE_ENG"发出报告"、CCU → 发送桥"addr · dest / CCU 逐拍给"；CCU 框改"收 stall_tx 与各写计数 · 发令 C2H"；左下说明框"到达计数 + 排空"改"各入链路、各写者写计数 → CCU"；C2H 标"按单位合并，AEB 优先"。

11-06 第二次改动（V18-TP-41 / 42，任务书 `_build/TP_RENAME_NOLAST_BRIEF_20261106.md`）：全图信号改与核内 RRAM 口同名（ready / addr / dest）；NWB 框改"IDN 接收桥 · 4 条 8 B 链路 / 各一个攒字寄存器 / 四拍凑满整字即写"；CCU 框"发令 C2H：给发送桥逐拍 addr / dest（单位边界不上链路）"；发送桥框与右侧标签撤 last。

## 二、数值 / 映射小例（`_build/draw_l1_sram.py`）

| 图文件 | 函数 | 正文位置 | 例子与断言 | 常量 |
|---|---|---|---|---|
| `figs/FIG-L1_SRAM-BANKS.svg` | `fig_banks()` | §1.2 | 两堆 × 12 个 bank，W0 / W1 / A 三组、成对 | `GROUPS`、`NB_HEAP` |
| `figs/FIG-L1_SRAM-PINGPONG.svg` | `fig_pingpong()` | §1.3 | 三个阶段读一堆写另一堆，阶段 1 内某拍堆 0 bank 3 读、堆 1 bank 3 写 | — |
| `figs/FIG-L1_SRAM-ABANK-CFG.svg` | `fig_abank_cfg()` | §1.6 | A 类 4 / 8 bank 两种配置下字号 0–7 的落位 | `a_word()` |
| `figs/FIG-L1_SRAM-RING.svg` | `fig_ring()` | §3.3 | 环占 A 类字 20–25（L = 6），写对象第 4–8 字；断言字号 [24, 25, 20, 21, 22]；11-05 夜起算地址方标"核内 CCU / 核间 MAE 通道"（图例为落地写；11-06 起 C2H 也由 CCU 算地址，正文 §3.3 已注，图未改） | `RING_BASE`、`RING_L`、`RING_K` |
| `figs/FIG-L1_SRAM-MAP-W.svg` | `fig_map_w()` | §4.2 | 列字区一字一列 64 个连续 $k$，bank $b$ 装列 $2b$、$2b+1$；断言 16 列 × 2 段对落 8 bank × 4 深度 | `wcol_phys()`、`MAPW` |
| `figs/FIG-L1_SRAM-MAP-W-HALF.svg` | `fig_map_w_half()` | §4.3 | 行字区只占 W0：一段落 4 bank × 2 深度 | `w_phys()`、`MAPH` |
| `figs/FIG-L1_SRAM-MAP-A.svg` | `fig_map_a()` | §4.4 | 对象头 8 B + 记录 70 / 40 / 100 B，首字号 1、4、6，共 10 字，轮流落 bank 8–11 | `HDR`、`REC_LEN`、`FIRST_ROW`、`MAPA` |
| `figs/FIG-L1_SRAM-LANE-PICK.svg` | `fig_lane_pick()` | §6.1 | 一个 pass 每 bank ≤ 2 列，按掩码进 4 个 pod；$m_{17}$ 顺延 | `POD_NEED`、`PASS_COLS`、`BEAT0` |
| `figs/FIG-L1_SRAM-COLREAD-1SRC.svg` | `fig_colread_1src()` | §6.1a | 单来源读口重组器逐拍，稳态一段一拍、每 bank ≤ 96 B | `colread_sim()`、`RG_CAP` |
| `figs/FIG-L1_SRAM-COLREAD-2SRC.svg` | `fig_colread_2src()` | §6.1a | 两来源（来源 A）逐拍，半段交出、起步气泡、峰值 128 B/bank | 同上 |
| `figs/FIG-L1_SRAM-TWO-SRC.svg` | `fig_two_src()` | §6.2 | 两来源 1 + 3：槽 $s$ 在 lane $s$ / $s \oplus 8$ 间静态二选一 | `slot_select()` |

退役函数（不生成）：`_retired_fig_partition()`（FIG-L1_SRAM-PARTITION）、`_retired_fig_conn()`（FIG-L1_SRAM-CONN，由 ARCH 取代，函数内仍是 11-05 前的旧字样，保留原样作历史）、`_retired_fig_colarrive()` 与 `_retired_md()`（FIG-L1_SRAM-COLARRIVE）。

## 三、紧密访存（`_build/draw_compact.py`）

| 图文件 | 函数 | 正文位置 | 画什么 | 断言 |
|---|---|---|---|---|
| `figs/FIG-L1_SRAM-COMPACT-A.svg` | `draw('FIG-L1_SRAM-COMPACT-A.svg', 8, …)` | §3.4a | A 类 8 bank 配置下 20 B 记录从字节 248 起，跨 bank 7（借来的 W1）深度 0 与 bank 8 深度 1 | 两次写落不同 bank；未选字节保持原值；读回移位 24 后与写入相同 |

## 四、精算 K hi 两种来源（`_build/draw_l1_khi.py`，11-06 第十二次，V18-ATT-01）

再生成：`python -X utf8 -I _build/draw_l1_khi.py`，再跑渲染。

| 图文件 | 函数 | 正文位置 | 画什么 | 断言 / 常量 |
|---|---|---|---|---|
| `figs/FIG-L1_SRAM-KHI-RESIDENT-VS-REREAD.svg` | `main()` | §7.8a | 同一时间线（粗算 tile 0…4 在时段 0…4；录取单位 u0 的 64 个 key 取自 tile 0–3，时段 3 末录取、时段 4 补读并精算）下：上半驻留模式的 K hi 行字区、K hi 列字区（tile 0–3 列字留到 u0 精算完，tile 4 留给后续单位）、lo 区与列字区占用份数；下半重读模式的 K hi 行字区（粗算完即释放）、录取 key 全码区与份数；图下蓝字为实际尺寸 | `U0_KEYS`、`N_SLOT`、`N_FC_USED`、`HI_B` / `LO_B` / `SC_B` / `FC_B`；断言 $\lvert\mathcal T(u_0)\rvert = 4$、驻留列字区最大份数 $= 1 + 4 = 5$、重读最大份数 $= 1 + 1 = 2$、全码 128 B/key（尺度落 S 类）、红字 ≤ 2 处且每处 ≤ 12 字 |

## 五、改图时的约定

- 正文图注与图里的数字同源：改常量后同时改正文图注。
- 架构图的接线以正文 §2.1 口表与协议篇链路表为准；接线变了先改正文，再改图。
- 每次改完都跑脚本、渲染、用 Read 看 PNG。

> 11-06 深夜第三次（V18-TP-51 / NAME-04）：撤 dest 后重跑相关生图脚本，图上"dest = CRU 分支"改为"去 MAE_CRU 的分支"，C2H 分流改为"按 CCU 的通路选择"，信号框不再列 dest，远端引擎的短消息改名"执行完成"；自检均 0 问题。
