# MAE_DSU 篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-06 晚：CONN 图退役、换 ARCH 图（Agent D）｜2026-11-06｜第二版（11-06 MAE_WSU 改名 MAE_DSU、加两平面合并图 TWOPLANE；V18-MAE-04 / 05）。改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`。旧图 FIG-MAE_WSU-CONN / -SPLICE / -TRANSPOSE / -SIDEBAND 已移到 `figs/_retired_20261106/`；旧脚本 `draw_mae_wsu.py` 与旧登记表存档在 `_build/_retired_20261106/`。

## 再生成

```bash
python -X utf8 -I _build/draw_mae_arch.py
```

```bash
python -X utf8 -I _build/draw_mae_dsu.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

## 图

| 图文件 | 脚本 / 函数 | 正文位置 | 画什么 | 常量与断言 |
|---|---|---|---|---|
| `figs/FIG-MAE_DSU-ARCH.svg` | `draw_mae_arch.py` / `fig_dsu()` | §2 | PPT 式架构图：MAE_DSU 展开为 DDR 原形入口、L2 原形入口、"暂存（一份，共用）"框（按字重排攒 $n$ 行 ≥ 2 × 128 B ping-pong / 转置攒一个子段）、"整形数据通路（一条）"框（按字重排 / 转置 / 两平面合并、随转置的块尺度与旁带、hi 尺度复用）、出口 → L1（经 HUB_IDN 32 B，整字 + 核集合）、出口 → NI-L2C（32 B）；MAE_ENG 标"唯一控制源"，给整形模式 · 几何 · 停发与逐拍 addr / be；外圈全灰，NI_EXT、MAE_CRU 画灰 | 外圈常量 `PEERS`、`GROUP` 与 `frame()` / `member()` / `dimblock()` 四篇共用，改位置要四张图一起改；链路清单 S1–S6（`MAE_ARCH_LINKS_20261106.md` §4）；自检 0 项 |
| `figs/FIG-MAE_DSU-REGROUP.svg` | `draw_mae_dsu.py` / `fig_regroup()` | §4.1 | 按字重排（V18-MAE-35）：上排连续 4 拍、每拍一个 $k$ 行 = 4 个列组各一个粒子（每粒子按 2 个通道缩画，实际 16 个 = 8 B）；中排重排后的 4 个整字，字 $g$ = 列组 $g$ 的 4 行按行序连排；每字右侧两种核集合（按 $m$ 切分 {核 $g$} / 单核 {核 0}）；红字"攒 4 行后重排：码不变、只改位置；每拍一个整字、一个地址发出" | `NR = 4`、`NG = 4`、`PM = 2`、`ROWS`、`WORDS`、`CORESET_MSPLIT / _SINGLE`；断言每个码恰出现一次且字节值不变、字 $g$ 内按 $k$ 行序、字 $g$ 只含列组 $g$ 的通道、`NR * 8 == 32` |
| `figs/FIG-MAE_DSU-SPLICE.svg` | `draw_mae_dsu.py` / `fig_splice()` | §4.2 | 转置的标准布局输入例：同一 $k$ 行相邻两个列组的两个 8 B 粒子 → 一个 16 B $W^{\mathsf T}$ 列字（每粒子按 4 个通道缩画）；红字"输出列字的码 = 两个粒子按序，不产生新字节"，图下注"中间怎样暂存不规定" | `K_ROW = 5`、`HALF_A / HALF_B`；断言输出码序 = 两个粒子按序、$k$ 恒定 |
| `figs/FIG-MAE_DSU-TRANSPOSE.svg` | `draw_mae_dsu.py` / `fig_transpose()` | §4.2 | 转置 4 × 4 缩小例：列深度优先的列字（$m$ 固定、沿 $k$）转成 $W^{\mathsf T}$ 列字（$k$ 固定、沿 $m$） | `N = 4`；断言 `OUT[j][m] == IN[m][j] == (j, m)` |
| `figs/FIG-MAE_DSU-TWOPLANE.svg` | `draw_mae_dsu.py` / `fig_twoplane()` | §4.3 | 两平面合并：DDR 里 key 7 的 hi 列字（地址 A，4 个码缩画）、lo 列字（地址 B）、尺度（地址 C）→ L1 同一记录相邻的 hi 字、lo 字，尺度行另落 S 类；红字两处（"字节不变，只改地址""不做半字节交织"），图下蓝字"实际 head_dim 128：记录 = 64 B + 64 B = 128 B，尺度 4 B 落 S 类" | `KEY = 7`、`HI = [3, A, 5, C]`、`LO = [7, 1, E, 4]`、`SCALE = [0x79]`；断言每个码字节合并前后不变、源不变、记录内 hi → lo 相邻无空隙（偏移 0 / 4）、尺度不在记录内、每码仍 4 bit、$c = 16h + \ell$ 在 INT8 内、64 + 64 = 128、32 B 对齐 |
| `figs/FIG-MAE_DSU-SIDEBAND.svg` | `draw_mae_dsu.py` / `fig_sideband()` | §5.1 | 4 个 E8M0 指数 5 / 2 / 7 / 4 → $e_{\max} = 7$、$\Delta = (2, 5, 0, 3)$；旁带行 1 B + 16 B + 15 B 保留 | `E`；断言 $2^{e_m} = 2^{e_{\max}} / 2^{\Delta_m}$、$\Delta_m$ 在 4 bit 内 |

## 约定

- 连接图在 `draw_mae_conn.py` 里加函数、共用 `frame()` / `members()`；数值小例在 `draw_mae_dsu.py`，数值由脚本算出并断言；改常量要同步正文图下说明。
- 图里不画片外出口（V18-NII-03 修订：DDR 只存前向形式的权重）。
- `draw_mae_conn.py` 其他三个函数（NI_EXT / NI_INT / IDN）里同组单元块的标题已改 MAE_DSU（块 id 仍为 `wsu`，只是内部标识）。

## 退役

| 图文件 | 原脚本 / 函数 | 退役日期与原因 | 存放 |
|---|---|---|---|
| `FIG-MAE_DSU-CONN.svg` | `draw_mae_conn.py` / `_retired_fig_dsu()`（已改名、不在 `__main__` 调用） | 2026-11-06 晚：用户"CONN 图可以退役"，MAE 组单元篇改用协议篇 PPT 式架构图（任务书 `MAE_CRU_MERGE_BRIEF_20261106.md` §1 规则 11）；由 `FIG-MAE_DSU-ARCH` 取代 | `figs/_retired_20261106/` |

- 11-06 晚起，MAE 组单元篇的架构图都在 `draw_mae_arch.py` 里加函数；外圈（六单元 + 组外对端位置）四张图相同，本单元不用的对端与同组单元画灰框；只画与本单元直接相连的线，线上只标名与位宽，图说在 `MAE_ARCH_CAPTIONS_20261106.md`。
- **11-07（V18-HUB-01）IDN 归 HUB 组**：`draw_mae_arch.py` 的 MAE 组外圈改为五单元（标题"MAE 组 · 五单元"），下方对端 `PEERS['idn']` 由"四核 IDN 接收桥"改为"HUB_IDN（入站分发网）"；同组单元里删去 MAE_IDN 小框；`fig_idn()` 改名 `_retired_fig_idn()`，HUB_IDN 的架构图移到 `draw_hub_idn.py` / `fig_arch()`。 本图：出口 → L1 经 x = 1255 下行接 HUB_IDN 对端（`uses = {'idn'}`），标签"4 道 × 8 B → HUB_IDN"。自检 0 项。
- **11-08 晚（V18-HUB-04）**：本图出口 → L1 块副标题改"经 HUB_IDN · 32 B / 含旁带行 · 全码记录"，下行标签"4 道 × 8 B → HUB_IDN"改为"32 B → HUB_IDN"；HUB_IDN 对端副标题改"一路 32 B → 按核集合分发 → 四核 NWB"。布局不变，自检 0 项。
- **11-08 下午（V18-MAE-35）**：新图 FIG-MAE_DSU-REGROUP（`fig_regroup()`，§4.1）；FIG-MAE_DSU-SPLICE 由"半字合并"改为转置的标准布局输入例并移到 §4.2；FIG-MAE_DSU-TRANSPOSE 箭头文字改"转置（实现不规定）"；FIG-MAE_DSU-ARCH 的"子段暂存"块改"暂存（一份，共用）"、模式文字改按字重排 / 转置（两种输入布局）/ 两平面合并、MAE_ENG 标"唯一控制源"；`draw_mae_arch.py` 的 `DATE` 改 2026-11-08；`draw_mae_conn.py` 退役函数外框文字"半字合并"改"按字重排"。改常量 `NR / NG / PM` 要同步 §4.1 图下说明。
