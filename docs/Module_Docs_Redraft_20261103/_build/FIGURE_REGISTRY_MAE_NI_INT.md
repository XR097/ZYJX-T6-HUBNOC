# MAE_NI_INT 篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-06 晚：CONN 图退役、换 ARCH 图（Agent D）｜2026-11-06｜改图时从这里找脚本、函数与正文位置；改完重跑并看 PNG。自动索引见 `FIGURE_REGISTRY.md`（`build_figure_registry.py` 生成）。

## 再生成

在 `Final_Architecture/Module_Docs_Redraft_20261103/` 目录下：

```bash
python -X utf8 -I _build/draw_mae_arch.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

## 图

| 图文件 | 脚本 / 函数 | 正文位置 | 画什么 | 常量与约定 |
|---|---|---|---|---|
| `figs/FIG-MAE_NI_INT-ARCH.svg` | `draw_mae_arch.py` / `fig_ni_int()` | §2 | PPT 式架构图：NI_INT 展开为 NI 指令执行与分路、NI 控制道端点、读返回分路（六个目的口）、NI-L2C 写客户（五源 M0 / M1 / PIN / DSU / CRU）、NI-L2C 返回车道（去 NI_EXT / DSU / CRU）、拆拍寄存器 4 × 32 B；组内五个单元全部点亮；组外 LIC 直连口 32 B、NI 控制道 64 bit、中央 L2（NI 写口 32 B · 写计数 × 4 象限 · 读 en / addr · dout 32 B） | 外圈常量 `PEERS`、`GROUP` 与 `frame()` / `member()` / `dimblock()` 四篇共用，改位置要四张图一起改；链路清单 I1–I21（`MAE_ARCH_LINKS_20261106.md` §2）；17 处跳线弧；自检 0 项 |

## 约定

- MAE 组各篇的连接图都在 `draw_mae_conn.py` 里加函数，用同一个 `frame()` 与 `members()`；本单元不用的对端与同组单元 `dim=True`。
- 图里地址一律写逻辑地址；不画对端之后的去向。
- 本篇只有连接图：读返回的地址生成、V 散写行位交错归 MAE_ENG 篇配图；链路拆分与多播归 MAE_IDN 篇。

## 退役

| 图文件 | 原脚本 / 函数 | 退役日期与原因 | 存放 |
|---|---|---|---|
| `FIG-MAE_NI_INT-CONN.svg` | `draw_mae_conn.py` / `_retired_fig_ni_int()`（已改名、不在 `__main__` 调用） | 2026-11-06 晚：用户"CONN 图可以退役"，MAE 组单元篇改用协议篇 PPT 式架构图（任务书 `MAE_CRU_MERGE_BRIEF_20261106.md` §1 规则 11）；由 `FIG-MAE_NI_INT-ARCH` 取代 | `figs/_retired_20261106/` |

- 11-06 晚起，MAE 组单元篇的架构图都在 `draw_mae_arch.py` 里加函数；外圈（六单元 + 组外对端位置）四张图相同，本单元不用的对端与同组单元画灰框；只画与本单元直接相连的线，线上只标名与位宽，图说在 `MAE_ARCH_CAPTIONS_20261106.md`。
- **11-07（V18-HUB-01）IDN 归 HUB 组**：`draw_mae_arch.py` 的 MAE 组外圈改为五单元（标题"MAE 组 · 五单元"），下方对端 `PEERS['idn']` 由"四核 IDN 接收桥"改为"HUB_IDN（入站分发网）"；同组单元里删去 MAE_IDN 小框；`fig_idn()` 改名 `_retired_fig_idn()`，HUB_IDN 的架构图移到 `draw_hub_idn.py` / `fig_arch()`。 本图：拆拍寄存器 → HUB_IDN 改为 x = 1115 下行（`uses` 加 `idn`），分路框副标题去向改"→ HUB_IDN"。自检 0 项。
- **11-07 晚**：拆拍寄存器块改为"IDN 出口 1 × 32 B"，加 MAE_DSU 整形输出 → IDN 出口（x = 1290），撤读返回分路 → MAE_CRU；返回车道副标题改为 NI 读口 4 × 32 B。
- **11-08 晚（V18-HUB-04）**：`draw_mae_arch.py` 的 HUB_IDN 对端副标题改为"一路 32 B → 按核集合分发 → 四核 NWB"（撤"拆分"）；文件头注释的 NI_INT 内容"拆拍寄存器"改为"IDN 出口（一路 32 B）"。本图布局不变，自检 0 项。`draw_mae_conn.py` 退役函数里 NI_INT-CONN 的 IDN 标签同步（不出图）。
