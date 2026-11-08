# MAE_INTEGRATION 篇图件登记

> Owner: WangYizhao｜2026-11-06｜改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`（`build_figure_registry.py` 生成）。

| 图 | 脚本 / 函数 | 正文节 | 画什么 | 常量与断言；改图约定 |
|---|---|---|---|---|
| `figs/FIG-MAE_INTEGRATION-ARCH-DATA.svg` | `draw_mae_integration.py` / `fig_data()` | §3.1 | PPT 式：MAE 组六单元（MAE_ENG 展开为指令入口两份、M0 / M1 请求仲裁、搬运引擎叠 × N），对外数据链路 D1–D9：D1 M0 256 bit、D2 M1 64 bit、D3 PIN 64 bit、D4 NI 写口 32 B（任一象限 · 象限掩码）、D5 NI 返回读口 32 B（任一象限）、D6 IDN 4 核 × 4 条 × 8 B、D7 LIC 直连口 32 B、D8 C2H dest = CRU 4 × 32 B、D9 MAE_CRU → H2C 道（第二源）；组内：NI_EXT ↔ NI_INT（读返回 / 写出 / PIN 存储字）、NI_INT → MAE_IDN（4 道 × 8 B）、NI_INT ↔ MAE_DSU、MAE_DSU → MAE_IDN、NI_INT ↔ MAE_CRU（读路径 / 合并结果 → NI-L2C） | 手写坐标；外框、对端位置取 `draw_mae_arch.PEERS / GROUP`，六单元位置在本脚本 `UNITS`，两张架构图共用，改一张要两张一起改；自检 0 问题 |
| `figs/FIG-MAE_INTEGRATION-ARCH-CTRL.svg` | `draw_mae_integration.py` / `fig_ctrl()` | §3.2 | 同一外框的命令类连线 C1–C8：C1 LIC → 指令入口（64 bit · 标号）、C2 完成通知 + 致命错误上报 → LIC、C3 命令网端点 (a)（MAE_ENG 与 NI 控制道合一）、C4 端点 (b)（MAE_CRU 标量）、C5 引擎 → H2C 道 0–3（en · addr · 核掩码，一条指令驱动四道）、C6 L2 写入握手 4 × (valid + src) → NI_INT、C7 LIC 直连口写入握手 → NI_INT、C8 NI_EXT ↔ CIF（PIN 首个违规 · Monitor）、**C9 H2C 落地写入握手（H2C 道 (1660, 600) → x 1585 走廊 → 引擎右缘 y 280）、C10 IDN 落地写入握手（四核 NWB → MAE_IDN，x 1310；组内 MAE_IDN → 引擎走 x 1165，"按 src 交引擎"）、C11 CRU 入口写入握手（MAE_CRU → C2H 分流框，y 395）**（11-06 深夜第二次加，V18-TP-50；C4 标签缩为"C4 端点 (b)"并移到 y 305 给 C9 让位）；组内：请求 · 选口 / 写响应、读请求记录 · 通路选择、按 src 分给引擎、模式 · 地址（DSU）、核集合 · 单位发完（IDN）、参数 · 地址 / 合并完成（CRU）；地址线、使能线都画成命令线、不细分（用户 11-06） | 同上 |
| `figs/FIG-MAE_INTEGRATION-PATH.svg` | `draw_mae_integration.py` / `fig_path()` | §4 | 一条 M0 → L1 指令、IDN 道分配 {2, 2}（道 0、1 → 核 0，道 2、3 → 核 1）、每核 64 B：4 笔 32 B 读请求（DDR 0x40000 / 0x40020 / 0x40040 / 0x40060）与读请求记录 → 拆成 4 × 8 B 的逐拍 addr（核 0 与核 1 都是 1024…1048、1056…1080）→ 各核 NWB 攒满一个存储字写进 L1 → 两核写计数各到 2 | `DDR_BASE, L1_BASE, LANE_CORE, N_WORD = 0x40000, 1024, [0, 0, 1, 1], 4`；断言 DDR 地址序列、目的 (核, 地址)、各道 4 拍 addr、一个存储字由同一条道送全、字节守恒 128 B、两核写计数各 2；改常量同步 §4 图说 |

再生成：在 `Module_Docs_Redraft_20261103` 下 `python -X utf8 -I _build/draw_mae_integration.py`，再 `F:\QQ_Agent\vendor\napcat-shell\node.exe _build\render.cjs figs _build\preview`，最后 `python -X utf8 _build/build_figure_registry.py .`。

> 11-06 深夜第三次（V18-TP-51 / NAME-04）：撤 dest 后重跑相关生图脚本，图上"dest = CRU 分支"改为"去 MAE_CRU 的分支"，C2H 分流改为"按 CCU 的通路选择"，信号框不再列 dest，远端引擎的短消息改名"执行完成"；自检均 0 问题。
