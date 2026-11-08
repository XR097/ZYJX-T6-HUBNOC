# Agent D 报告：MAE 组四篇 PPT 式架构图（11-06 晚）

> Owner: WangYizhao｜2026-11-06｜任务书 `MAE_CRU_MERGE_BRIEF_20261106.md` §2 Agent D。没有改任何 .md 正文，没有改 `draw_tp_arch.py`、`draw_transfer_protocol.py` 和 `Claude_Design_Spec/`。

## 1 产出

| 文件 | 内容 |
|---|---|
| `_build/MAE_ARCH_LINKS_20261106.md` | 四张图的链路清单：E1–E17、I1–I21、D1–D5、S1–S6，每条写明从、到、线名、位宽和依据的正文节号；§0 是外圈对端在四张图里分别用不用；§5 列待协调者 X1–X7 |
| `_build/draw_mae_arch.py` | 新脚本。复制了 `draw_tp_arch.py` 的 Fig 类，没有 import，免得两个脚本互相牵动。外圈常量是 `PEERS`、`GROUP`，函数有 `frame()`、`member()`、`dimblock()`，四个画图函数是 `fig_ni_ext / fig_ni_int / fig_idn / fig_dsu` |
| `figs/FIG-MAE_NI_EXT-ARCH.svg` | 23 条线、2 处跳线弧，自检 0 项 |
| `figs/FIG-MAE_NI_INT-ARCH.svg` | 25 条线、17 处跳线弧，自检 0 项 |
| `figs/FIG-MAE_IDN-ARCH.svg` | 26 条线、4 处跳线弧，自检 0 项 |
| `figs/FIG-MAE_DSU-ARCH.svg` | 10 条线，自检 0 项 |
| `_build/preview/FIG-MAE_*-ARCH.png` | 渲染结果，四张都逐张看过 |
| `_build/MAE_ARCH_CAPTIONS_20261106.md` | 四段图说，每段 7 句，并附正文里的图片引用写法 |
| `_build/FIGURE_REGISTRY_MAE_{NI_EXT,NI_INT,IDN,DSU}.md` | CONN 行换成 ARCH 行，再生成命令改为 `draw_mae_arch.py`，新增"退役"一节 |

## 2 退役（改前 → 改后）

- `draw_mae_conn.py`：`fig_ni_ext / fig_ni_int / fig_idn / fig_dsu` → `_retired_fig_ni_ext / _retired_fig_ni_int / _retired_fig_idn / _retired_fig_dsu`。`__main__` 里原来调用这四个函数，现在只剩 `pass` 加一段注释；文件头的"输出"行也改成了退役说明。`frame()`、`members()`、`PEERS` 保留不动。
- `figs/FIG-MAE_NI_EXT-CONN.svg`、`FIG-MAE_NI_INT-CONN.svg`、`FIG-MAE_IDN-CONN.svg`、`FIG-MAE_DSU-CONN.svg` 移到了 `figs/_retired_20261106/`。
- 过程中出了一次意外。第一次用 PowerShell 改 `draw_mae_conn.py` 时相对路径失败，脚本没被改动就被运行了，于是把四张 CONN 图又生成回 `figs/`。我核对了哈希，这四张与已移走的旧图逐字节相同，然后删掉了重新生成的那份。`_retired_20261106/` 里的旧图没有受影响。
- `_build/preview/` 里的四张旧 CONN 的 PNG 没有动，它们是渲染副产物。

## 3 统一外圈（四张图相同）

- **组框内六个单元**（规则 1）：本单元展开画内部结构，其余五个画小框。与本单元直接往来的画实框并连线，没有往来的画灰色虚线框，副标题"本单元不用"。
- **组框外的对端**，位置四张图相同：
  - 上方：CIF、LIC、命令与标量网，从左到右排。任务书只要求放在"上方"，没有规定次序；我按"NI_EXT 的窗口表在左上、NI_INT 的控制道在右上"排的。
  - 左侧：DDR 控制器 P0、片上互联、系统 DMA / FMC 从端。
  - 下方：中央 L2、四核 IDN 接收桥。
  - 右侧：HUB-UP 的 dest = CRU 分支、HUB-DN 道。
  - 本单元不用的对端画灰。右侧两个对端只与 MAE_CRU 相连，所以四张图里都是灰的。
- **只画与本单元相连的线**，线上只标名称和位宽；正文没给位宽的只标名称（X3）。

## 4 各图检查清单

| 检查项 | NI_EXT | NI_INT | IDN | DSU |
|---|---|---|---|---|
| 内部结构与正文一致 | ✓ 三口协议端、跨域 × 3、选口位分流、地址换算与拼字、窗口常量表 · 窗口检查 | ✓ 指令执行与分路、读返回分路（六个目的口）、拆拍寄存器 4 × 32 B、写客户（五源）、返回车道（三个去向）、NI 控制道 | ✓ 两源合并 × 4、多播缓冲 × 4、交叉、16 条链路 | ✓ 两个入口、四种整形模式 + hi 尺度复用、两个出口 |
| 链路清单逐条画到 | ✓ E1–E17 | ✓ I1–I21 | ✓ D1–D5 | ✓ S1–S6 |
| 规则 3 / 5（CRU） | CRU 画灰，不写片外 | 读路径 ×2 进 CRU，CRU → 写客户；写客户五源 | CRU 画灰，注"不经 MAE_IDN" | CRU 画灰，注"与 DSU 并列" |
| 规则 10（双目的） | — | — | — | 写进图说（原形那一份不经 DSU） |
| 无重叠、无压线、不穿块、不共线（脚本自检） | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 |
| 看 PNG：文字可读，标签不骑在本单元框线上 | ✓ | ✓（第二轮把 3 个标签移出框线） | ✓（第二轮把核标签下移到组框与对端之间，核 3 改为直落） | ✓（第二轮移开 addr 标签，模式框改名） |
| 方向与文字一致 | ✓ | ✓ | ✓ | ✓ |

迭代了三轮：第一轮初稿；第二轮把本单元框改成灰蓝虚线，免得和蓝色数据线混淆，并移开压在框线上的标签；第三轮把 IDN 核 3 的输出线改为直落。

## 5 待协调者（详见链路清单 §5）

- **X1**：NI_EXT 的主口错误要经 NI_INT 的 NI 控制道转报，但 NI_EXT §2.1 组内接口表没有"主口错误 → NI_INT"这一行。
- **X2**：L2 NI 写口各象限的写计数交给谁，接口表里没有成行。NI_INT §5.5 写的是在 NI-L2C 一侧比对后放行 B；集成篇目录 MI4 建议直连 MAE_ENG。本图只画了 L2 → 写客户。
- **X3**：写响应、PIN 落地依据、单位发完、窗口常量表这几条，正文没给位宽，线上只标了名称。
- **X4**：MAE_IDN 内部按"合并 → 多播缓冲 → 交叉"的顺序画；正文没有明确写出这个先后。
- **X5**：两平面合并的输出是否也可以去 L2，正文只写了去 L1。本图在出口 → NI-L2C 上标了"只半字合并 / 转置"。
- **X6**：MAE_ENG → DSU 的"逐拍 addr"没有写成接口行。本图单独画了一条线，没标位宽。
- **协调者还要做的**：把四篇正文 §2 里的 CONN 引用换成 ARCH，贴上图说；然后重跑 `build_figure_registry.py .`。`draw_mae_conn.py` 里退役函数体内的 `_registry = 'FIG-…-CONN.svg'` 字面量还在，自动索引会把它们列为 `_retired_*` 函数的产出，这符合预期。
