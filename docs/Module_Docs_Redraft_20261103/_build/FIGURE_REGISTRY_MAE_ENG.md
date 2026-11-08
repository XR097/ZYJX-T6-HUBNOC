# MAE_ENG 篇图件登记

> Owner: WangYizhao｜2026-11-06｜改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`（`build_figure_registry.py` 生成）。

| 图 | 脚本 / 函数 | 正文节 | 画什么 | 常量与断言；改图约定 |
|---|---|---|---|---|
| `figs/FIG-MAE_ENG-ARCH.svg` | `draw_mae_arch.py` / `fig_eng()` | §2 | PPT 式架构图：MAE 组六单元统一外圈；MAE_ENG 展开为指令入口、搬运引擎池、运算级控制、M0 / M1 请求合流、在用列表缓存与完成通知；对外 LIC（指令 / 完成通知）、命令与标量网（远端指令 · 长度转发 / 发出报告）、中央 L2（写入握手，按发令号，11-06 深夜起）、H2C 道（道旁引擎地址） | 手写坐标；脚本自检文字不重叠、不压线、不穿框、不共线；对端位置与其他四张 MAE 架构图相同（`PEERS`），改外圈要五张一起改 |
| `figs/FIG-MAE_ENG-ARITH.svg` | `draw_mae_eng.py` / `fig_arith()` | §5.2 | 两级嵌套：基址 4096、行 48 B、3 行 × 256 B、2 块 × 1024 B → 12 拍源地址；目的 L2 行跨距 64 B；行尾 16 B 用 be | `A_BASE, A_ROWB, A_ROWS, A_RSTR, A_BLKS, A_BSTR, A_DROW = 4096, 48, 3, 256, 2, 1024, 64`；断言源地址序列、目的地址 0…352、有效字节 288、两端余数相同；改常量同步 §5.2 图说 |
| `figs/FIG-MAE_ENG-LIST.svg` | `draw_mae_eng.py` / `fig_list()` | §5.3 | 行号 [2, 5, 6, 11] 与位图 `1000 0110 0100` 展开出相同的 8 拍源地址 0x10080…0x102E0；目的 0…224 | `L_ITEMS, L_STRIDE, L_BASE, L_NBITS = [2, 5, 6, 11], 64, 0x10000, 12`；断言两种载荷地址逐拍相同、位图串；改常量同步 §5.3 图说 |
| `figs/FIG-MAE_ENG-KHI-GATHER.svg` | `draw_mae_eng.py` / `fig_khi()` | §5.4 | 录取列表 [3, 7]：驻留只取 lo（B + 192 / 448 → lo 区 0 / 64）；重读取 hi + lo 两段 → 全码记录 0–127、128–255 | `K_KEYS, K_SEG, K_HI, K_LO = [3, 7], 64, 0x100000, 0x200000`；断言源 / 目的地址；改常量同步 §5.4 图说 |
| `figs/FIG-MAE_ENG-QSPLICE.svg` | `draw_mae_eng.py` / `fig_qsplice()` | §5.9 | 11-07 改（V18-MAE-33）：按 $m$ 切分的四象限对象各带长度表（片长 [50,38,61,44] / [47,52,40,58] / [55,36,49,60] / [42,57,39,53] B），道 $q$ 按表顺序取、写 L1 第 $q$ 个区域；区域基址字 [0, 33, 66, 99] → 首拍 bank 8 / 9 / 10 / 11，反例 [0, 32, 64, 96] 都落 bank 8；token 1 = 四区域各一片 | `Q_T`、`Q_LEN`、`Q_SRC`、`Q_REGION_GOOD / BAD`、`Q_ABANK`、`Q_START`、`Q_TOK1`；断言首拍 bank 互不相同 / 反例相同、各片起点、token 1 四段位置；改常量同步 §5.9 图说 |
| `figs/FIG-TP-LENGTH-REPORT.svg`（引用） | `draw_transfer_protocol.py` / `fig_length_report()` | §10.4 | 协议篇的变长对象走查图，本篇引用 | 归协议篇登记表 `FIGURE_REGISTRY_TP.md` |

再生成：在 `Module_Docs_Redraft_20261103` 下 `python -X utf8 -I _build/draw_mae_arch.py`、`python -X utf8 -I _build/draw_mae_eng.py`，再 `F:\QQ_Agent\vendor\napcat-shell\node.exe _build\render.cjs figs _build\preview`，最后 `python -X utf8 _build/build_figure_registry.py .`。

> 11-06 深夜第三次（V18-TP-51 / NAME-04）：撤 dest 后重跑相关生图脚本，图上"dest = CRU 分支"改为"去 MAE_CRU 的分支"，C2H 分流改为"按 CCU 的通路选择"，信号框不再列 dest，远端引擎的短消息改名"执行完成"；自检均 0 问题。
- **11-07（V18-HUB-01）IDN 归 HUB 组**：`draw_mae_arch.py` 的 MAE 组外圈改为五单元（标题"MAE 组 · 五单元"），下方对端 `PEERS['idn']` 由"四核 IDN 接收桥"改为"HUB_IDN（入站分发网）"；同组单元里删去 MAE_IDN 小框；`fig_idn()` 改名 `_retired_fig_idn()`，HUB_IDN 的架构图移到 `draw_hub_idn.py` / `fig_arch()`。 本图：引擎 → HUB_IDN 一条双向控制线（核集合 · 单位 · 源顺序 / 握手，x = 1415 下行）；MAE_DSU、MAE_CRU 小框副标题改为"收模式 · addr""收参数 · 回完成"（原两处线上标签删去，给竖线让位）；H2C 标签改左对齐、缩短。自检 0 项。
- **11-08 晚（V18-HUB-04）**：`draw_mae_arch.py` 本图引擎 → HUB_IDN 控制线标签由"核集合 · 单位 · 源顺序 / 握手"改为"核集合（随字）/ 握手"；HUB_IDN 对端副标题改"一路 32 B → 按核集合分发 → 四核 NWB"。布局不变，自检 0 项。
