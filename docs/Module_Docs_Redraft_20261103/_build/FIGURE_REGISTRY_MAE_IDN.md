# MAE_IDN 篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-06 晚：CONN 图退役、换 ARCH 图（Agent D）｜2026-11-06｜改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`（`build_figure_registry.py` 生成）。

## 再生成

在 `Final_Architecture/Module_Docs_Redraft_20261103/` 目录下：

```bash
python -X utf8 -I _build/draw_mae_arch.py
```

```bash
python -X utf8 -I _build/draw_mae_idn.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

## 图

| 图文件 | 脚本 / 函数 | 正文位置 | 画什么 | 常量与断言 |
|---|---|---|---|---|
| `figs/FIG-MAE_IDN-ARCH.svg` | `draw_mae_arch.py` / `fig_idn()` | §2 | PPT 式架构图：MAE_IDN 展开为两源合并 × 4 → 分叉点 × 4（每目的核 1 位已取、不另配存储，V18-TP-53）→ 交叉（道 → 核集合）；标注"先后与位置【设计者定】"（V18-TP-54）→ 16 条链路（每核 4 × 8 B）；源 1 NI_INT、源 2 MAE_DSU 各经竖总线分到四道；MAE_ENG 给核集合 4 × 4 bit 与单位发完；MAE_CRU 画灰并注"CRU 不经 MAE_IDN" | 外圈常量 `PEERS`、`GROUP` 与 `frame()` / `member()` / `dimblock()` 四篇共用，改位置要四张图一起改；链路清单 D1–D5（`MAE_ARCH_LINKS_20261106.md` §3）；四条核输出线按 y 递增拐弯、互不交叉；自检 0 项 |
| `figs/FIG-MAE_IDN-LANE-SPLIT.svg` | `draw_mae_idn.py` / `fig_lane_split()` | §4.4 | 同一拍 4 条 8 B 道在 {4} / {2, 2} / {2, 1, 1} / {1, 1, 1, 1} 四种核集合下送到的核与各道的 addr；一个存储字由同一条道 4 拍送全，同一核的几条道各送不同存储字的字首 8 B（11-06 改，V18-TP-42） | `ALLOCS`（核集合与各道 addr）；断言各核所得道互不重叠、并起来是整拍 4 道；同一核各道的存储字互不相同且 addr 为 32 的倍数 |
| `figs/FIG-MAE_IDN-MCAST.svg` | `draw_mae_idn.py` / `fig_mcast()`（逐拍模型 `mcast_fork_sim.simulate()`，与 HUB_NOC-MCAST、TP-STREAM-BEAT 共用） | §5 | 一条道 6 拍多播到核 0、核 2：分叉点 = 一级链路块 + 每核 1 位已取（不另配存储）；每核分支容量 4（skid + NWB 入口，示意）；核 2 写进侧在拍 2、3 不 ready；逐拍列送入两核分支、分叉点收 / 停、核 2 分支占用、两核写进的 k；图下对照：核 2 停 4 拍、单位 8 拍 | `N, CAP, NT = 6, 4, 9`；断言分叉点停收 0 拍、核 0 拍 1–6 写完、核 2 拍 1,4–8 写完、核 2 分支占用最大 3；对照 `CX` 分叉点停 2 拍、核 0 的 k = 6 晚 2 拍。11-06 深夜 V18-TP-53 撤多播缓冲后重做；改常量同步 §5 图下说明 |

## 约定

- 连接图在 `draw_mae_conn.py` 里加函数、共用 `frame()` / `members()`；数值小例在 `draw_mae_idn.py`，数值由脚本算出并断言。
- 图里地址一律写逻辑地址（字节号）；红字每张 ≤ 2 处。

## 退役

| 图文件 | 原脚本 / 函数 | 退役日期与原因 | 存放 |
|---|---|---|---|
| `FIG-MAE_IDN-CONN.svg` | `draw_mae_conn.py` / `_retired_fig_idn()`（已改名、不在 `__main__` 调用） | 2026-11-06 晚：用户"CONN 图可以退役"，MAE 组单元篇改用协议篇 PPT 式架构图（任务书 `MAE_CRU_MERGE_BRIEF_20261106.md` §1 规则 11）；由 `FIG-MAE_IDN-ARCH` 取代 | `figs/_retired_20261106/` |

- 11-06 晚起，MAE 组单元篇的架构图都在 `draw_mae_arch.py` 里加函数；外圈（六单元 + 组外对端位置）四张图相同，本单元不用的对端与同组单元画灰框；只画与本单元直接相连的线，线上只标名与位宽，图说在 `MAE_ARCH_CAPTIONS_20261106.md`。
