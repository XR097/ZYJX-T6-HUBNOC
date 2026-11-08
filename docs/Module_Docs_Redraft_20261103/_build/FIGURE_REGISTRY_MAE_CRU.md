# MAE_CRU 篇图件登记

> Owner: WangYizhao｜2026-11-07｜改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`（`build_figure_registry.py` 生成）。依据 V18-MAE-30、V18-CRU-02…05、用户 11-06 深夜"一个基础的 ping-pong 设计"，MAE_CRU 目录第二版。

| 图 | 脚本 / 函数 | 正文节 | 画什么 | 常量与断言；改图约定 |
|---|---|---|---|---|
| `figs/FIG-MAE_CRU-ARCH.svg` | `draw_mae_arch.py` / `fig_cru()` | §2 | PPT 式架构图，MAE 组统一外圈（`PEERS`、`GROUP`、`frame()` / `member()` / `dimblock()` 与其余五张 MAE 架构图共用）：用到的对端 = 命令与标量网、C2H 去 MAE_CRU 的分支、H2C 道；同组 MAE_ENG、NI_INT 亮，NI_EXT / MAE_DSU / MAE_IDN 灰。本单元展开为 C2H 入口 × 4、CRU 存储（SRAM，32 B / 地址，字节写使能）、合并（三种形态）、出口；读路径从 NI_INT 进、去 L2 / M1 回 NI_INT；写入握手回发数据核；标量入 · 合并值出（独立端点）；MAE_ENG 给参数与 addr、收完成 | 手写坐标，自检 0 问题；本单元框标题 `ftx=760` 避开 MAE_ENG 竖线；改外圈要六张一起改 |
| `figs/FIG-MAE_CRU-SUM.svg` | `draw_mae_cru.py` / `fig_sum()` | §3.1 | 参与核 {0, 1, 2} 的部分和按 2 → 0 → 1 到达同一 CRU 内地址 e（应到 3 份），第 3 份到达时按 (核 0 + 核 1) + 核 2 相加 | `S_PART`、`S_ORDER = [2, 0, 1]`；断言结果 [1, −0.5, 0, 9]，换任何到达先后结果相同；一个地址实际 16 元素，图中 4 个 |
| `figs/FIG-MAE_CRU-READSET.svg` | `draw_mae_cru.py` / `fig_readset()` | §3.3 | 地址 0 由核 {0, 1, 2}、地址 1 由核 {0, 2} 做读集合并，两地址的拍交错到达，各自到齐后按位取并 | `R_BITS`、`R_NEED = {0: 3, 1: 2}`、`R_ORDER`；断言并集 {0: 11010010, 1: 00100101}、地址 1 拍 3 先到齐、地址 0 拍 4 到齐；图中 8 bit，实际 256 bit / 地址 |
| `figs/FIG-MAE_CRU-PINGPONG.svg` | `draw_mae_cru.py` / `fig_pingpong()`（`pp_sim()`） | §4.3 | CRU 内地址 ping-pong：参与核 {0, 1}，tile 0 用 A 区地址 0–1、tile 1 用 B 区地址 2–3、tile 2 回到 A 区；到齐即合并、下一拍送出、送出后地址清零 | `P_ADDR`、`P_NEED = 2`、`P_EV`（拍 → 核 · tile · 地址）、`P_NT = 13`；断言合并序列 (0,t0)(1,t0)(2,t1)(3,t1)(0,t2)(1,t2)、tile 0 / 1 / 2 在拍 5 / 9 / 12 报完成、上一 tile 结果送出前新 tile 不写进同一地址、A 区 tile 0 全部送出后 tile 2 才写进 A 区；拍号只示意先后 |

再生成：在 `Module_Docs_Redraft_20261103` 下 `python -X utf8 -I _build/draw_mae_arch.py`、`python -X utf8 -I _build/draw_mae_cru.py`，再 `F:\QQ_Agent\vendor\napcat-shell\node.exe _build\render.cjs figs _build\preview`，最后 `python -X utf8 _build/build_figure_registry.py .`。
