# HUB_IDN 篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-06 建（原 `FIGURE_REGISTRY_MAE_IDN.md`）｜2026-11-07：IDN 归 HUB 组、改名 HUB_IDN（V18-HUB-01 / 02），三张图改名 FIG-HUB_IDN-*；脚本 `draw_mae_idn.py` 改名 `draw_hub_idn.py`｜**2026-11-08 晚（V18-HUB-04）：IDN 改为每核一条 32 B 链路、HUB_IDN 只剩按每字核集合分发的分叉点——ARCH 重画，LANE-SPLIT 退役，新图 CORE-SET，MCAST 不变**｜改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`（`build_figure_registry.py` 生成）。

## 再生成

在 `Final_Architecture/Module_Docs_Redraft_20261103/` 目录下：

```bash
python -X utf8 -I _build/draw_hub_idn.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

## 图

| 图文件 | 脚本 / 函数 | 正文位置 | 画什么 | 常量与断言 |
|---|---|---|---|---|
| `figs/FIG-HUB_IDN-ARCH.svg` | `draw_hub_idn.py` / `fig_arch()`（图元借用 `draw_mae_arch.py` 的 `Fig`、`dimblock`、`D`，不改它） | §2 | PPT 式架构图，**HUB 组外框**：HUB 组框内 HUB_NOC 画灰（与 HUB_IDN 无数据连接）、HUB_IDN 展开为**一个分叉点框**"按每字的核集合分发"（一拍一个存储字；核集合里每个核各拉一路 en、各核独立取走；每目的核 1 位已取、不另配存储；不拆拍、不算地址、不数单位）→ 4 条链路（每核 1 × 32 B）；两条说明标签在框上方："分几级、放在哪【设计者定】（协议篇 A1–A7）"、"几核共享带宽 = MAE_ENG 把连续的字轮流排给各核"。对端：上方中央 L2 / 命令网（灰）、MAE_ENG（核集合 4 bit 随每个存储字；收写入握手，汇总 · 按 src）；左侧 NI_INT（IDN 出口 1 × 32 B，两源在 MAE 内择一）、MAE_DSU（灰，经 NI_INT 的 IDN 出口）、MAE_CRU（灰，只写 L2）；下方四核 LDP / 发送桥（灰，归 HUB_NOC）、四核 IDN 接收桥 NWB（"每核 1 条 32 B 链路 · 与 LDP 相同的接收桥"） | 手写坐标；自检 0 项、0 跳线；**NWB 块放在分叉点正下方（x 900–1420），四条输出线 `xs = 960 + 120c` 竖直直下、不拐弯、不交叉**（用户 11-08："IDN 的这类布局问题需要优化下"，原阶梯拐弯有 6 处跳线）；日期 `M.DATE = '2026-11-08'` |
| `figs/FIG-HUB_IDN-CORE-SET.svg` | `draw_hub_idn.py` / `fig_core_set()` | §4.2 | 连续 8 个存储字（一拍一个）在五行下的核集合与目的字地址：单核吃满（核 2）、双核轮流（核 0、1）、2 : 1 : 1（核 0 两份）、四核均分、多播到核 0、2；每行下方给各核平均 B/拍；红字"一个字一拍整字到一个核" | `SHARES`（五种核集合序列）、`BASE`（各核起始字地址）、`N_WORDS = 8`、`WORD = 32`；断言每拍恰一个字且核集合非空、单播各行各核平均字节数之和 = 32 B/拍、多播行每核都收全部字、字地址都是 32 的倍数。改常量同步 §4.2 图下说明 |
| `figs/FIG-HUB_IDN-MCAST.svg` | `draw_hub_idn.py` / `fig_mcast()`（逐拍模型 `mcast_fork_sim.simulate()`，与 HUB_NOC-MCAST、TP-STREAM-BEAT 共用） | §5 | 一个 6 拍的字流多播到核 0、核 2：分叉点 = 一级链路块 + 每核 1 位已取（不另配存储）；每核分支容量 4（skid + NWB 入口，示意）；核 2 写进侧在拍 2、3 不 ready；逐拍列送入两核分支、分叉点收 / 停、核 2 分支占用、两核写进的 k；图下对照：核 2 停 4 拍、单位 8 拍 | `N, CAP, NT = 6, 4, 9`；断言分叉点停收 0 拍、核 0 拍 1–6 写完、核 2 拍 1,4–8 写完、核 2 分支占用最大 3；对照 `CX` 分叉点停 2 拍、核 0 的 k = 6 晚 2 拍。改常量同步 §5 图下说明（11-08 只删图下"链路宽 8 B"一句，图不变） |

## 约定

- 数值小例在 `draw_hub_idn.py`，数值由脚本算出并断言。图里地址一律写逻辑地址（字节号）；红字每张 ≤ 2 处。
- HUB 组两篇（HUB_NOC、HUB_IDN）不设统一外框脚本：HUB_NOC 的架构图画整个 HUB_NOC（`draw_hub_noc.py`），HUB_IDN 的架构图在本脚本；两篇之间没有数据连接。
- 引用于：HUB_IDN.md §2 / §4.2 / §5；架构篇 `ONCHIP_DATAPATH_ARCH.md` 只引用 FIG-TP-ARCH-*，不引用本篇的图。

## 退役

| 图文件 | 原脚本 / 函数 | 退役日期与原因 | 存放 |
|---|---|---|---|
| `FIG-MAE_IDN-CONN.svg` | `draw_mae_conn.py` / `_retired_fig_idn()`（已改名、不在 `__main__` 调用） | 2026-11-06 晚：MAE 组单元篇改用 PPT 式架构图 | `figs/_retired_20261106/` |
| `FIG-MAE_IDN-ARCH.svg` | `draw_mae_arch.py` / `_retired_fig_idn()`（已改名、不在 `__main__` 调用） | 2026-11-07：IDN 归 HUB 组（V18-HUB-01），由 `FIG-HUB_IDN-ARCH` 取代 | `figs/_retired_20261107/` |
| `FIG-MAE_IDN-LANE-SPLIT.svg`、`FIG-MAE_IDN-MCAST.svg` | 原 `draw_mae_idn.py`（脚本已改名 `draw_hub_idn.py`） | 2026-11-07：改名 FIG-HUB_IDN-*，内容不变 | `figs/_retired_20261107/` |
| `FIG-HUB_IDN-LANE-SPLIT.svg` | `draw_hub_idn.py` / `_retired_fig_lane_split()`（已改名、不在 `__main__` 调用，调用即抛错） | **2026-11-08 晚：V18-HUB-04 撤 4 道 × 8 B，由 `FIG-HUB_IDN-CORE-SET` 取代** | `figs/_retired_20261108/` |

## 改图历史

- **11-07 晚（V18-HUB-03）**：`fig_arch()` 的两源 MUX 换成拆拍寄存器 × 4（32 B → 4 拍 × 8 B，4 拍同一字地址），唯一输入是 NI_INT 的 IDN 出口 1 × 32 B，MAE_DSU 改灰；LANE-SPLIT 图下文字改为"其余 3 拍 addr 不变"。
- **11-08 晚（V18-HUB-04）**：`fig_arch()` 撤拆拍寄存器 × 4 与交叉框，改为一个分叉点框 + 4 条 32 B 输出；MAE_ENG 对端改"核集合随字（旁带）· 收写入握手"；NWB 对端改"每核 1 条 32 B 链路 · 与 LDP 相同的接收桥"。`fig_lane_split()` 退役，新增 `fig_core_set()`。`fig_mcast()` 未改。
