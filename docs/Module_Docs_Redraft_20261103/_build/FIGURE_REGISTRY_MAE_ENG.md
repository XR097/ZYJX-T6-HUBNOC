# MAE_ENG 篇图件登记

> Owner: WangYizhao｜2026-11-06｜改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`（`build_figure_registry.py` 生成）。

| 图 | 脚本 / 函数 | 正文节 | 画什么 | 常量与断言；改图约定 |
|---|---|---|---|---|
| `figs/FIG-MAE_ENG-ARCH.svg` | `draw_mae_arch.py` / `fig_eng()` | §2 | PPT 式架构图：MAE 组六单元统一外圈；MAE_ENG 展开为指令入口、搬运引擎池、运算级控制、M0 / M1 请求合流、在用列表缓存与完成通知；对外 LIC（指令 / 完成通知）、命令与标量网（远端指令 · 长度转发 / 发出报告）、中央 L2（写入握手，按发令号，11-06 深夜起）、H2C 道（道旁引擎地址） | 手写坐标；脚本自检文字不重叠、不压线、不穿框、不共线；对端位置与其他四张 MAE 架构图相同（`PEERS`），改外圈要五张一起改 |
| `figs/FIG-MAE_ENG-ARITH.svg` | `draw_mae_eng.py` / `fig_arith()` | §5.2 | 两级嵌套：基址 4096、行 48 B、3 行 × 256 B、2 块 × 1024 B → 12 拍源地址；目的 L2 行跨距 64 B；行尾 16 B 用 be | `A_BASE, A_ROWB, A_ROWS, A_RSTR, A_BLKS, A_BSTR, A_DROW = 4096, 48, 3, 256, 2, 1024, 64`；断言源地址序列、目的地址 0…352、有效字节 288、两端余数相同；改常量同步 §5.2 图说 |
| `figs/FIG-MAE_ENG-LIST.svg` | `draw_mae_eng.py` / `fig_list()` | §5.3 | 行号 [2, 5, 6, 11] 与位图 `1000 0110 0100` 展开出相同的 8 拍源地址 0x10080…0x102E0；目的 0…224 | `L_ITEMS, L_STRIDE, L_BASE, L_NBITS = [2, 5, 6, 11], 64, 0x10000, 12`；断言两种载荷地址逐拍相同、位图串；改常量同步 §5.3 图说 |
| `figs/FIG-MAE_ENG-KHI-GATHER.svg` | `draw_mae_eng.py` / `fig_khi()` | §5.4 | 录取列表 [3, 7]：驻留只取 lo（B + 192 / 448 → lo 区 0 / 64）；重读取 hi + lo 两段 → 全码记录 0–127、128–255 | `K_KEYS, K_SEG, K_HI, K_LO = [3, 7], 64, 0x100000, 0x200000`；断言源 / 目的地址；改常量同步 §5.4 图说 |
| `figs/FIG-MAE_ENG-QSPLICE.svg` | `draw_mae_eng.py` / `fig_qsplice()` | §5.9 | 四道并行读时合并：4 token × 每段 2 个存储字，四个象限的段都从象限内字节 4096 起（同址异象限）；道 $q$ 写 L1 A 类字 $12t + 3q + w$，四道同拍落 4 个不同 bank；反例步长 2 撞 bank | `Q_T, Q_SEGW, Q_SRC, Q_DSTEP, Q_FULL = 4, 2, 4096, 3, 12`，`Q_ABANK = [8, 9, 10, 11]`；断言每拍四道源地址相同、bank 互不相同、反例道 0/2 与 1/3 撞 bank；改常量同步 §5.9 图说（11-06 深夜新增，V18-MAE-28） |
| `figs/FIG-TP-LENGTH-REPORT.svg`（引用） | `draw_transfer_protocol.py` / `fig_length_report()` | §10.4 | 协议篇的变长对象走查图，本篇引用 | 归协议篇登记表 `FIGURE_REGISTRY_TP.md` |

再生成：在 `Module_Docs_Redraft_20261103` 下 `python -X utf8 -I _build/draw_mae_arch.py`、`python -X utf8 -I _build/draw_mae_eng.py`，再 `F:\QQ_Agent\vendor\napcat-shell\node.exe _build\render.cjs figs _build\preview`，最后 `python -X utf8 _build/build_figure_registry.py .`。

> 11-06 深夜第三次（V18-TP-51 / NAME-04）：撤 dest 后重跑相关生图脚本，图上"dest = CRU 分支"改为"去 MAE_CRU 的分支"，C2H 分流改为"按 CCU 的通路选择"，信号框不再列 dest，远端引擎的短消息改名"执行完成"；自检均 0 问题。
