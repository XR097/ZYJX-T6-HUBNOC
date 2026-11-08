# MAE_WSU 篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-06｜改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`。

## 再生成

```bash
python -X utf8 -I _build/draw_mae_conn.py
```

```bash
python -X utf8 -I _build/draw_mae_wsu.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

## 图

| 图文件 | 脚本 / 函数 | 正文位置 | 画什么 | 常量与断言 |
|---|---|---|---|---|
| `figs/FIG-MAE_WSU-CONN.svg` | `draw_mae_conn.py` / `fig_wsu()` | §2 | MAE 组统一五单元外框：WSU 与 NI_INT（入 + 出）、MAE_ENG（命令）、MAE_IDN（出）直接往来，NI_EXT 画灰；组外全部画灰（无直接对外口） | 默认 `MEMBER_SLOTS`；交叉 ≤ 2 |
| `figs/FIG-MAE_WSU-SPLICE.svg` | `draw_mae_wsu.py` / `fig_splice()` | §4.1 | 同一 $k$ 下相邻两个列块的两个 8 B 半行字拼成一个 16 B $W^{\mathsf T}$ 列字（每半字按 4 个通道缩画） | `K_ROW = 5`、`HALF_A / HALF_B`；断言拼出的码序 = 两个半字按序、$k$ 恒定 |
| `figs/FIG-MAE_WSU-TRANSPOSE.svg` | `draw_mae_wsu.py` / `fig_transpose()` | §4.2 | 4 × 4 缩小例：列深度优先的列字（$m$ 固定、沿 $k$）转成 $W^{\mathsf T}$ 列字（$k$ 固定、沿 $m$） | `N = 4`；断言 `OUT[j][m] == IN[m][j] == (j, m)` |
| `figs/FIG-MAE_WSU-SIDEBAND.svg` | `draw_mae_wsu.py` / `fig_sideband()` | §5.1 | 4 个 E8M0 指数 5 / 2 / 7 / 4 → $e_{\max} = 7$、$\Delta = (2, 5, 0, 3)$；旁带行 1 B + 16 B + 15 B 保留 | `E`；断言 $2^{e_m} = 2^{e_{\max}} / 2^{\Delta_m}$、$\Delta_m$ 在 4 bit 内 |

## 约定

- 连接图在 `draw_mae_conn.py` 里加函数、共用 `frame()` / `members()`；数值小例在 `draw_mae_wsu.py`，数值由脚本算出并断言；改常量要同步正文图下说明。
- 图里不画片外出口（V18-NII-03 修订：DDR 只存前向形式的权重）。
