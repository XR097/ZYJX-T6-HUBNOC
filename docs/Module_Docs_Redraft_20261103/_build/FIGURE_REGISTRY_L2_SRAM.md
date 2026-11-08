# L2 SRAM 篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-05｜改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`（`build_figure_registry.py` 生成）。11-05 夜按核间协议改版（V18-TP-26…34、V18-NIE-02）改了 ARCH 与 MAP-RING 两张。11-06 按附录 `_build/TP_REVISION_BRIEF_20261106_ADDENDUM.md`（V18-TP-35…38）只改 ARCH：HUB-UP 框注"C2H 由各核 CCU 发令、给地址"，下方"到达计数 · 排空 → MAE 本地计数器"改"L2 写计数（写进 bank 时加一）→ MAE（比对应收量后才发读）"，说明框改"通用链路块""写计数"。

> 11-06 深夜（V18-L2-04 / TP-47）：FIG-L2_SRAM-ARCH 改为核 $q$ 的 L2WP 只下到象限 $q$（`X_BUS_C = [343, 330, 317, 304]`，下得越远越靠左、四条互不交叉），每象限 2 条入口 FIFO（`FY = [72, 124]`），集合器框改"两来源先后：头文件参数 / 写进 bank 即回握手"，底部改为"写入握手（链路反向旁带）"与"L2 致命错误上报"，撤"L2 写计数 × 20"与 MAE 比对框。

## 再生成

在 `Final_Architecture/Module_Docs_Redraft_20261103/` 目录下：

```bash
python -X utf8 -I _build/draw_l2_arch.py
```

```bash
python -X utf8 -I _build/draw_l2_sram.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

第一条出架构图（复用 `draw_tp_arch.py` 的 `Fig` 类与自检，0 问题才算通过）；第二条出三张数值小例，加 `--md` 打印正文 §3.3、§4.3 两张表；第三条渲染 `figs/` 全部 SVG 到 `_build/preview/*.png`。

## 图

| 图文件 | 脚本 / 函数 | 正文位置 | 画什么 | 常量与断言 |
|---|---|---|---|---|
| `figs/FIG-L2_SRAM-ARCH.svg` | `draw_l2_arch.py` / `fig_arch()` | §2 | 4 象限 × 两堆（4 + 4 bank）；左侧 C2H 分流（只按 dest 分流、不扇入；核 n 的 C2H → L2WP 第 n 条，4 条 × 32 B，addr 24 bit 由各核 CCU 给）四条竖总线与 NI_INT 写一条竖总线；每象限五条入口 FIFO（核 0–3、NI 写）→ 写集合器（四核轮转、NI 写按 MAE 静态表）→ 两堆 bank；象限读口 q ↔ H2C 道 q（dout、en / addr、busy；多播各核独立取走）；NI 返回读竖总线；下方 L2 写计数（(核 0–3, NI 写) × 4 象限 = 20 个，11-06 V18-L2-03）→ MAE（比对应收量后才发读）、错误出口 → hub 控制道 | `phys(h, q, j)` 与 §4.2 同式，断言 `phys(0,2,5) == (17,1)`；`QY`、`QH`、`X_BUS_C`（四核竖总线）/ `X_BUS_N` / `X_NIR`、`FY`（象限内 5 条 FIFO 中线）为版式常量 |
| `figs/FIG-L2_SRAM-MAP-HEAP.svg` | `draw_l2_sram.py` / `fig_map_heap()` | §4.2、§4.3 | 象限 0 缩小例：堆 0 放对象 X（字 0–9）、Z（字 12–19），堆 1 放 Y（字 0–7），6 个深度 | `OBJS`；断言对象不重叠、两堆 bank 不相交、同拍写堆 1 读堆 0 不撞 bank、§6.5 冲突例落点 |
| ~~`figs/FIG-L2_SRAM-MAP-RING.svg`~~ **11-06 晚退役**（移至 `figs/_retired_20261106/`，函数改 `_retired_fig_map_ring()`；L2 里的对象不按环形使用，V18-MAE-17） | `draw_l2_sram.py` / `_retired_fig_map_ring()` | §3.3（已改写，无图） | 环形回绕由 MAE 通道做：象限 1 堆 0，基址字 4、环长 12，5 拍从 k = 10 起 → 字 14、15、4、5、6 | `RING_Q, RING_H, RING_BASE, RING_L, RING_K0, RING_N = 1, 0, 4, 12, 10, 5`；断言字号序列；改常量要同步 §3.3 表 |
| `figs/FIG-L2_SRAM-OBJ-ALIGN.svg` | `draw_l2_sram.py` / `fig_obj_align()` | §3.4 | 对象头 8 B + 记录 17 / 40 / 32 B，各从整字起、尾部补 0，共 5 个存储字 | `PIECES`；断言起始字 `[0,1,2,4]`、补 0 字节数、逐字节读回相同 |

## 退役

| 图 / 函数 | 退役日期 | 取代 |
|---|---|---|
| `FIG-L2_SRAM-CONN` / `draw_l2_sram.py` `_retired_fig_conn()` | 11-05 晚 | `FIG-L2_SRAM-ARCH` |
| `FIG-L2_SRAM-MAP-REGION`、`FIG-L2_SRAM-UNIT-ALIGN`（SVG 在 `figs/_retired_20261105/`） | 11-05 | MAP-HEAP、OBJ-ALIGN |

> 11-06 深夜第三次（V18-TP-51 / NAME-04）：撤 dest 后重跑相关生图脚本，图上"dest = CRU 分支"改为"去 MAE_CRU 的分支"，C2H 分流改为"按 CCU 的通路选择"，信号框不再列 dest，远端引擎的短消息改名"执行完成"；自检均 0 问题。
