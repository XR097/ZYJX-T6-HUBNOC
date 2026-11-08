# MAE 组四张架构图的图说（供协调者贴进正文图下）

> Owner: WangYizhao｜2026-11-06（晚）｜Agent D｜图由 `draw_mae_arch.py` 生成；链路依据见 `MAE_ARCH_LINKS_20261106.md`。四张图共用同一外圈：MAE 组框内六个单元（本单元展开，其余五个画小框，灰框 = 与本单元没有直接往来），框外对端位置相同（上 CIF / LIC / 命令与标量网，左 DDR 控制器 P0 / 片上互联 / 系统 DMA·FMC 从端，下中央 L2 / 四核 IDN 接收桥，右 HUB-UP 的 dest = CRU 分支 / HUB-DN），本单元不用的画灰。线色：蓝 = 数据，橙虚线 = 命令与标量网或控制，灰 = 对外 AXI。

## FIG-MAE_NI_EXT-ARCH（替换 FIG-MAE_NI_EXT-CONN，§2）

```markdown
![FIG-MAE_NI_EXT-ARCH NI_EXT 的内部结构与对外接口](figs/FIG-MAE_NI_EXT-ARCH.svg)
```

NI_EXT 内部按三个口各一行：M0 主口（256 bit，接 DDR 控制器 P0）、M1 主口（64 bit，接片上互联，32 B 拆成 4 拍 64 bit）、PIN 从口（64 bit，系统 DMA / FMC 从端写入），每个口后面是自己的跨域级——M0 同步 / 异步可选，M1、PIN 为任意时钟比率的异步 FIFO。M0、M1 汇到选口位分流：MAE_ENG 的每笔 32 B 请求按选口位送 M0 或 M1，读返回 32 B 交 NI_INT，写响应交回 MAE_ENG。PIN 一路经地址换算与拼字，把 AXI 地址换成 L2 逻辑地址、WSTRB 换成 be，存储字交 NI_INT 的 NI-L2C 写客户；NI_INT 在该笔四个象限都写到之后放行 B 响应。窗口常量表在初始化时由 CIF 装一次，越窗、FIXED、WRAP 的事务整笔回 SLVERR，首个违规报 CIF。主口错误交 NI_INT，由 NI 控制道转报 LIC。LIC、中央 L2、四核 IDN 接收桥与 MAE_IDN、MAE_DSU、MAE_CRU 都画灰：NI_EXT 与它们没有直接往来。

## FIG-MAE_NI_INT-ARCH（替换 FIG-MAE_NI_INT-CONN，§2）

```markdown
![FIG-MAE_NI_INT-ARCH NI_INT 的内部结构与对外接口](figs/FIG-MAE_NI_INT-ARCH.svg)
```

MAE_ENG 给 NI 指令执行与分路两样东西：64 bit 的搬运指令，以及逐拍的 addr / be。指令执行按指令类给每笔读请求记下去向，并在搬运变长对象时让 NI 控制道先发长度转发；NI_INT 本身不算地址。读返回分路把 NI_EXT 交来的 M0 / M1 读返回（32 B）按读请求记录分到六个目的口：MAE_IDN（经 4 × 32 B 拆拍寄存器拆成 4 道 × 8 B）、MAE_DSU（整形输入）、MAE_CRU（读路径，兼容能力）、NI-L2C 写客户（去 L2）、LIC 直连口（32 B），以及区域复制 DDR → DDR 时的 NI_EXT 写通道。NI-L2C 写客户有五个来源（M0、M1、PIN、DSU、CRU），在单位边界切换，经 32 B 的 NI 写口写 L2；L2 的 NI 写口把各象限写计数交回写客户，PIN 那一笔的四个象限都到齐才放行 B 响应。返回车道向 L2 的 NI 返回读口发 en / addr、收 32 B dout，按余量发读，读出数据交 NI_EXT 写出、交 MAE_DSU 整形或交 MAE_CRU 合并。NI 控制道（64 bit）发长度转发，并转报 NI_EXT 的主口错误。MAE_CRU 的主输入（各核 C2H 上 dest = CRU 的拍）和它去核 L1、回 CCU 的输出都不经 NI_INT，所以右侧两个 hub 对端画灰。

## FIG-MAE_IDN-ARCH（替换 FIG-MAE_IDN-CONN，§2）

```markdown
![FIG-MAE_IDN-ARCH MAE_IDN 的内部结构与对外接口](figs/FIG-MAE_IDN-ARCH.svg)
```

MAE_IDN 有两个源，各 4 道 × 8 B：源 1 是 NI_INT 的读返回分路（经拆拍寄存器），源 2 是 MAE_DSU 的整形输出。MAE_CRU 的输出不经 MAE_IDN，所以 MAE_CRU 画灰。每条道先过自己的两源合并：两源只在单位边界切换，"单位发完"由发令的搬运引擎给出，链路上没有标记。合并后进该道的多播缓冲，缓冲为每个目的核设一个读指针，各核按自己的 ready 取走，全部取走才释放。交叉按当前单位随带的核集合（4 bit × 4 道，由 MAE_ENG 给出）把每条道接到一个或几个核的链路上：一核接 $n$ 条道即每拍 $8n$ B；道 $i$ 是否只接各核的链路 $i$ 由设计者定。输出是 16 条链路，每核 4 条 8 B，接四核的 IDN 接收桥 NWB，合计 32 B/拍。

## FIG-MAE_DSU-ARCH（替换 FIG-MAE_DSU-CONN，§2）

```markdown
![FIG-MAE_DSU-ARCH MAE_DSU 的内部结构与对外接口](figs/FIG-MAE_DSU-ARCH.svg)
```

MAE_DSU 有两个入口，都来自 NI_INT，各 32 B：DDR 原形入口接读返回分路，L2 原形入口接 NI-L2C 返回车道；一条指令只用其中一个。执行该指令的搬运引擎随单位给出整形模式（2 bit）与参数（子段长、是否双目的），也给出输出每拍的 addr / be；DSU 不设指令队列、不算地址。中间是四种整形模式，指令选其一：半字合并、转置（攒齐一个子段，子段长不超过硬限 $L_{\text{DSU}}$）、两平面合并（同一 key 的 hi 4 字接 lo 4 字成一条 128 B 记录，尺度行另落 S 类），以及块尺度与旁带（随半字合并、转置一起做）。"先 hi 后 lo"时，lo 复用 hi 的尺度。出口 → L1 经 MAE_IDN（4 道 × 8 B），送出 $W^{\mathsf T}$ 列字块、旁带行与全码记录；出口 → NI-L2C 经写客户写 L2（32 B），只用于半字合并与转置的输出。外圈全部画灰：DSU 没有对外口，没有片外出口，与 MAE_CRU 并列、没有往来。双目的时，原形那一份由 NI_INT 直接交 MAE_IDN、不经 DSU，所以不在本图。
