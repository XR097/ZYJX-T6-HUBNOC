# MAE_NI_EXT 篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-06 晚：CONN 图退役、换 ARCH 图（Agent D）｜2026-11-05｜改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`（`build_figure_registry.py` 生成）。

## 再生成

在 `Final_Architecture/Module_Docs_Redraft_20261103/` 目录下：

```bash
python -X utf8 -I _build/draw_mae_arch.py
```

```bash
python -X utf8 -I _build/draw_mae_ni_ext.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

## 图

| 图文件 | 脚本 / 函数 | 正文位置 | 画什么 | 常量与断言 |
|---|---|---|---|---|
| `figs/FIG-MAE_NI_EXT-ARCH.svg` | `draw_mae_arch.py` / `fig_ni_ext()` | §2 | PPT 式架构图：NI_EXT 展开为 M0 主口 / M1 主口 / PIN 从口三行，各接自己的跨域级，M0 / M1 汇到选口（并按区把 NPU 侧地址换成 SoC 地址，头文件参数），PIN 经拼字；顶部 PIN 地址换算 · 区间检查（A − A_PIN、外设输入区，头文件参数、流片定死；11-06 晚 V18-NIE-03 撤 CIF 装表），只向 CIF 报首个违规；组内 MAE_ENG（请求 32 B · 选口位 / 写响应）、NI_INT（读返回 / 写出数据 / 主口错误 / PIN 存储字 / B 响应放行），NI_INT 再把主口错误转报命令与标量网；MAE_IDN / DSU / CRU 与 LIC、L2、IDN 接收桥、两个 hub 对端画灰 | 外圈常量 `PEERS`、`GROUP` 与 `frame()` / `member()` / `dimblock()` 四篇共用，改位置要四张图一起改；链路清单 E1–E17（`MAE_ARCH_LINKS_20261106.md` §1）；自检 0 项（文字不压线 / 不重叠 / 不跨框、线不穿块、不共线） |
| `figs/FIG-MAE_NI_EXT-PIN-WORDPACK.svg` | `draw_mae_ni_ext.py` / `fig_pin_wordpack()` | §7.2 | 窗口 [堆 0][象限 2] 起始逻辑地址 1280（由编译链固定，V18-NIE-02）、长 256 B；一笔 70 B 的写从逻辑地址 1356 起 → 10 个 AXI 拍 → 3 个存储字，各带字节写使能；另一笔从 1540 起越窗 → SLVERR | `WIN_START = 40`、`WIN_LEN = 8`、`OFF = 76`、`LEN = 70`、`BAD_OFF = 260`；断言拍数 10、首末拍有效字节、三个存储字的字节范围、逐字节相同、未写字节保持原值、越窗判定。改常量要同步 §7.2 图下说明 |

## 约定

- MAE 组五篇（MAE_ENG、NI_EXT、NI_INT、MAE_IDN、MAE_WSU）的连接图都在 `draw_mae_conn.py` 里加函数，用同一个 `frame()`（本单元放 `UNIT_RECT`）与 `members()`（其余四个同组单元依次放进 `MEMBER_SLOTS`，与本单元直接往来的放左列）；本单元不用的对端与同组单元 `dim=True`。
- 图里地址一律写 L2 逻辑地址，不写"偏移"（用户 11-05 夜）。
- 11-06（V18-TP-37，附录 _build/TP_REVISION_BRIEF_20261106_ADDENDUM.md）：正文 §2.1、§7.2、§7.6、§11.2、§12 改为"一个 AXI 写事务 = 一个搬运单位、突发长度不假设"B 响应依据 = L2 写计数经 NI-L2C 仲裁器归属"；本篇两张图未改。CONN 图中 NI_INT → NI_EXT 线标"写出数据 · L2 到达"（draw_mae_conn.py 第 87 行）仍是 11-05 夜字样，本次附录未点名该脚本，待协调者决定是否改为"L2 写计数"。

## 退役

| 图文件 | 原脚本 / 函数 | 退役日期与原因 | 存放 |
|---|---|---|---|
| `FIG-MAE_NI_EXT-CONN.svg` | `draw_mae_conn.py` / `_retired_fig_ni_ext()`（已改名、不在 `__main__` 调用） | 2026-11-06 晚：用户"CONN 图可以退役"，MAE 组单元篇改用协议篇 PPT 式架构图（任务书 `MAE_CRU_MERGE_BRIEF_20261106.md` §1 规则 11）；由 `FIG-MAE_NI_EXT-ARCH` 取代 | `figs/_retired_20261106/` |

- 11-06 晚起，MAE 组单元篇的架构图都在 `draw_mae_arch.py` 里加函数；外圈（六单元 + 组外对端位置）四张图相同，本单元不用的对端与同组单元画灰框；只画与本单元直接相连的线，线上只标名与位宽，图说在 `MAE_ARCH_CAPTIONS_20261106.md`。
- **11-07（V18-HUB-01）IDN 归 HUB 组**：`draw_mae_arch.py` 的 MAE 组外圈改为五单元（标题"MAE 组 · 五单元"），下方对端 `PEERS['idn']` 由"四核 IDN 接收桥"改为"HUB_IDN（入站分发网）"；同组单元里删去 MAE_IDN 小框；`fig_idn()` 改名 `_retired_fig_idn()`，HUB_IDN 的架构图移到 `draw_hub_idn.py` / `fig_arch()`。 本图：底部灰框只剩 MAE_DSU、MAE_CRU。
- **11-08 晚（V18-HUB-04）**：共用外圈的 HUB_IDN 对端副标题改为"一路 32 B → 按核集合分发 → 四核 NWB"（本图中为灰框）；本图其余不变，自检 0 项。
