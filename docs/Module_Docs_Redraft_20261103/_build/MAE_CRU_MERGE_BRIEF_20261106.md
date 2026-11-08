# 任务书：CRU 并入 MAE · 运算级 MUX · LIC ↔ MAE 握手 · 报告与长度通知 · 不回绕 · MAE 组 PPT 式架构图（11-06 晚）

> Owner: WangYizhao｜2026-11-06｜状态：**已完成**（四个 Opus Agent 报告 `_build/MAE_CRU_MERGE_REPORT_{A,B,C,D}_20261106.md`；协调者补：L1 / L2 / VNU_OPT 的不回绕改写、FIG-L2_SRAM-MAP-RING 退役、FIG-L1_SRAM-RING 与 FIG-L2_SRAM-ARCH 改字、外部输入信息篇 §6 加 5 行、DSU 整形模式三选一（"原样" = 运算字段直通）、四篇 CONN → ARCH 换图换图说、NI_EXT §2.1 加主口错误行、FIG-TP-ARCH-INCORE / -CTRL-MSG / -LINKS 残留字样；图索引 64 图无缺漏；残留词 grep 只剩修订注记、名称表与否定句）。依据 `Claude_Design_Spec/V1.8_DESIGN_REVISIONS.md` V18-MAE-11…18（§1 行与 §2 节）、§3 11-06 架构图行；目录稿 `Final_Architecture/V17_3_MODULE_TOC_MAE_ENG_20261106.md`（第四版）、`V17_3_MODULE_TOC_MAE_INTEGRATION_20261106.md`（第二版）。名称基准 `../L3PU_EXTERNAL_INFORMATION.md`。

## 0 用户原话（11-06 晚）

- "要不咱们重新划分下，CRU 归纳到 MAE 中，和 DSU 并行，这样 MAE 除了搬运指令的基础功能外，还可以叠加数据运算和数据操作，这样分组看起来更合理"
- "我认为 CRU 归入 MAE，这是正确的设计，只是现在需要调整接口的，我认为可以选择一个 MUX，决定数据要不要过 CRU 还是直接传，我认为 DSU 也是一样的，DSU 和 CRU 可以是并行的，因为他们没有依赖关系……MAE 也可以直接放在物理中心，但这是后端的事情，咱们不感知"
- "C1 可以接""C2 我认可""我认为可以单独一个端点""C4 认可"
- "这里我认为不应该是完成计数器，而是 LIC 和 MAE 的握手机制……MAE 只需要在一个指令执行完的时候，通知 LIC 即可"；"添加指令标号没有问题，ME6 撤回没问题，V18-TP-22 改没问题，CRU 交给 MAE 通知也没问题"
- "当前的对象标识概念到底是什么？不是说不分对象，完全通过地址和指令来配置吗"；"对于 ME8，我认可"
- ME9："我认为应该选 A"
- "对于环形缓冲问题，我认为 MAE 不感知这件事"；"环形缓冲交给（a）"
- ME11："必须保留，这要直接写成需求"
- "对于 MAE 组……它的每一个模块的架构图（包括模块内架构和模块外接口），采用协议中的架构图片的风格，我认为那个风格更详细，也更易懂"；"CONN 图可以退役"

## 1 新规则（各篇统一按此写）

1. **MAE 组六单元**：MAE_ENG、NI_EXT、NI_INT、MAE_IDN、MAE_DSU、**MAE_CRU**（合并单元：归约、标量合并、读集合并，并行 lane 可配）。HUB 组只剩 HUB_NOC。"HUB_CRU 篇" → "MAE_CRU 篇"（待写）。"hub 中心的 CRU / hub 中心的计算级" → "MAE_CRU"；CRU 物理放哪归后端，正文不写"在 hub 中心"。
2. **MAE 只有搬运指令**；源与目的之间有运算级，指令的运算字段经 MUX 选 **直通 / 经 MAE_DSU 整形 / 经 MAE_CRU 合并**，DSU 与 CRU 并列。**撤"MAE 操作 18"的独立配置**：CRU 的合并种类、参与核、期望到齐数是搬运指令的运算参数。
3. **MAE_CRU 的输入**：各核 C2H 上 dest = CRU 的拍（HUB-UP 分流，每核 1 条 × 32 B，入 MAE 组的 CRU 数据入口）；MAE 读路径（DDR 读返回、L2 经 NI 返回读口；兼容能力）；CCU 发来的标量（命令与标量网）。**输出**：经 HUB-DN 作第二源去核 L1；**经 NI-L2C 写客户去 L2（新增）**；标量合并值经命令与标量网回 CCU。**不经 MAE_IDN**。入口写计数按源核，由 MAE_ENG 比对（组内）。
4. **MAE_CRU 在命令与标量网上单独一个端点**（标量不与指令 / 长度转发消息排同一队）。
5. **NI-L2C 写客户来源变五个**：M0 / M1 / PIN / DSU / CRU；返回车道多一个去向 MAE_CRU。
6. **LIC ↔ MAE 握手**：LIC 可同时下发多条 MAE 指令，每条带 LIC 分配的**指令标号**；**MAE 每执行完一条就带标号通知 LIC**；MAE **不设完成计数器**，指令**不带等待条件**；"执行完"：目的 L2 / CRU = 写计数比对达到；目的 DDR / 共享内存 = AXI 写响应收齐；目的核 L1 = 发送完成（写入完成由目的核 CCU 比对、报 LIC 作位点完成）；CRU 合并完成也由 MAE 通知 LIC。**位点屏障：LIC 收各核位点完成事件 + 数 MAE 的完成通知**（取代"读 MAE 的完成计数器"）。"计入 MAE 的完成计数器"一律改写为"由 MAE 带指令标号通知 LIC"。
7. **发出报告**（CCU → MAE）只留：**目的起始地址（类位即 L2 象限）、写入项数、记录数、尾字有效字节数**；撤"对象标识"；核 $c$ 的第 $k$ 份报告按序对应 LIC 发给 MAE 的、标明"源来自核 $c$ 的 C2H"的第 $k$ 条指令。
8. **应写量单独通知（方案 A），撤"列表到齐计数"消息**：变长对象与 gather 到核 L1 的应写量都经长度转发给目的核 CCU（gather 应写量 = 列表计数 × 项字节数）。
9. **MAE 不做环形回绕**：MAE 搬运的数据不用环形缓冲，编译链按静态窗口与 ping-pong 分配、跨环尾拆两条指令；L1 / L2 接收方无状态不变；核内 CCU 的回绕不受影响。删"环形回绕在搬运引擎内展开 / 环长只出现在 ISA 的搬运指令里"一类句子（核间部分）。
10. **双目的是需求**：一条搬运指令可带第二目的，一次 DDR 读同时投原形（经 MAE_IDN 给前向核）与整形（经 MAE_DSU 给训练核 L1 或 L2）。
11. **MAE 组单元篇的架构图**：每篇一张 `FIG-<篇>-ARCH`，协议篇 FIG-TP-ARCH-* 的 PPT 式风格（`draw_tp_arch.py`）；框内单元内部结构，框外全部对外接口（线名 + 位宽 + 方向），外圈是 MAE 组统一外框（六单元 + 组的全部直接对端，本单元不用的画灰）；figkit3 的 `FIG-MAE_NI_EXT-CONN` / `-MAE_NI_INT-CONN` / `-MAE_IDN-CONN` / `-MAE_DSU-CONN` 退役到 `figs/_retired_20261106/`，`draw_mae_conn.py` 里对应函数加 `_retired_` 前缀、不在 `__main__` 调用。

## 2 分工（文件互不重叠）

### Agent A：协议篇 `DATA_TRANSFER_PROTOCOL.md` + 其图

改文字：文件头加一条 11-06 晚修订注记；§1.1 三种总线表（命令与标量网参与方：CRU → MAE_CRU）；§2.4 / §2.4.2（谁拥有源谁发令里 CRU 改 MAE_CRU；撤回绕句，规则 9）；§5（§5.1 拓扑图说、C2H 行"dest = 1 的拍交 MAE_CRU 的 CRU 数据入口"；§5.3.2 实例清单；§5.4 回绕句；§5.6.2 合并点里 HUB-DN 第二源来自 MAE_CRU、NI-L2C 五源、CRU 入口归 MAE 组）；§6.2 / §6.4（"CRU 的握手"改"MAE_CRU 的握手"，输出加"经 NI-L2C 写 L2"）；§7.3（发出报告字段，规则 7）；§7.4.1 / §7.4.2 / §7.4.4（规则 6）；§8.1 端点表（撤"列表到齐计数"行；"CRU 合并完成 CRU → MAE"改为组内、对外改"MAE → LIC 完成通知（指令标号）"新行；发出报告载荷；标量行的端点为 MAE_CRU）；§8.2 短消息类去掉到齐计数；§8.3 撤"CRU 的配置由 MAE 发令（MAE 操作 18）"，改为"CRU 的合并参数随 MAE 搬运指令"；§8.6 搬运指令载荷钩子更新为"见 MAE_ENG 目录第四版 §3.2（待正式稿）"；§11 由谁保证、§12 为什么（加本轮原话）。
改图（`draw_tp_arch.py` / `draw_transfer_protocol.py` 里对应函数，PPT 风格不变）：FIG-TP-ARCH-INTERCORE / -LINKS（CRU 框移进 MAE 组框，标 MAE_CRU；NI-L2C 到 L2 多一路来自 CRU）、FIG-TP-ARCH-CTRL（MAE_CRU 单独端点；MAE → LIC 完成通知；撤到齐计数）、FIG-TP-LENGTH-REPORT（报告字段）。更新 `_build/FIGURE_REGISTRY_TP.md`。

### Agent B：MAE 四篇正文 `MAE_NI_EXT.md`、`MAE_NI_INT.md`、`MAE_IDN.md`、`MAE_DSU.md`

各篇文件头加 11-06 晚修订注记；"MAE 组五单元 / 五个单元之一"改六单元（列表加 MAE_CRU）；"口的划分见 MAE 集成篇（待写）"保留指向集成篇。NI_INT：§1.1 / §2.1 组内接口加 MAE_CRU（读路径数据出、写 L2 结果入）；§3.1 指令类表加"经 CRU"行；§4.1 目的口加 MAE_CRU；§5.2 / §5.3 / §5.5 写客户五源；§6 完成改规则 6；§3.3 / 其他处回绕句按规则 9。DSU：§2.1 撤"进 DSU 的指令队列"，改为"DSU 收执行该指令的搬运引擎随单位给的整形模式与参数"；双目的写成需求（规则 10，§6.3）；与 CRU 并列一句。IDN：两源仍是 NI 分路 / DSU（CRU 不经 IDN，写一句）。NI_EXT：完成句按规则 6。**连接图引用与图说不要改**（Agent D 出新图后由协调者统一换），只在图下加一行"【协调者：本图将换为 FIG-<篇>-ARCH】"。

### Agent C：措辞类 `L1_SRAM.md`、`L2_SRAM.md`、`VNU_NLU.md`、`VNU_QNT.md`、`VNU_SEL.md`、`VNU_OPT.md`、`VNU_LOSS.md`、`L3PU_EXTERNAL_INFORMATION.md`

只换词与句：HUB_CRU 篇 → MAE_CRU 篇；"hub 中心的 CRU" → "MAE_CRU"；"CRU 由 MAE 发令（操作 18）" → "CRU 的合并参数随 MAE 搬运指令"；"计入 MAE 完成计数器 / 读 MAE 完成计数器" → 规则 6 写法；"列表到齐计数" → 规则 8 写法；发出报告的"对象标识" → 规则 7；L2 篇：NI 写口来源五个（若有列举）、CRU 输出可写 L2。外部输入信息篇 §5 列表进入路径保持"C2H → MAE_CRU 读集合并 → L2"。逐条"改前 → 改后"；替换表没有的词列出交协调者。

### Agent D：MAE 四篇的 PPT 式架构图（只动脚本、图与登记表，不改 .md 正文）

1. 读协议篇 `draw_tp_arch.py` 的风格与 `_build/TP_FIGURE_BRIEF_20261105.md` 的做法；读四篇正文（Agent B 同时在改，以本任务书 §1 规则为准）。
2. **先为每张图写链路清单**（谁连谁、线名、位宽、方向、本单元用不用），写进 `_build/MAE_ARCH_LINKS_20261106.md`，每条注明依据的正文节号；清单与正文不一致处单列"待协调者"。
3. 新脚本 `_build/draw_mae_arch.py`：画 FIG-MAE_NI_EXT-ARCH、FIG-MAE_NI_INT-ARCH、FIG-MAE_IDN-ARCH、FIG-MAE_DSU-ARCH。统一外圈：MAE 组框内六单元（本单元展开画内部结构，其余五个画小框，与本单元直接往来的点亮、否则画灰）；框外对端位置四张图相同（命令与标量网 / LIC / CIF 在上；DDR 控制器 P0、片上互联、系统 DMA / FMC 从端在左；中央 L2、四核 IDN 接收桥在下；HUB-UP 的 dest = CRU 分支、HUB-DN 在右），本单元不用的画灰。线上只标名与位宽，说明写图下（由 Agent D 写进 `_build/MAE_ARCH_CAPTIONS_20261106.md`，每张 4–8 句）。
4. 退役：`draw_mae_conn.py` 中 `fig_ni_ext / fig_ni_int / fig_idn / fig_dsu` 加 `_retired_` 前缀、不在 `__main__` 调用；四张旧 SVG 移到 `figs/_retired_20261106/`。
5. 渲染 `F:\QQ_Agent\vendor\napcat-shell\node.exe _build\render.cjs figs _build\preview`，逐张看 PNG，迭代到无重叠、无穿框、文字可读；更新 `FIGURE_REGISTRY_MAE_NI_EXT / NI_INT / IDN / DSU.md`。

### 协调者

收齐后：把四篇的 CONN 引用换成 ARCH、贴图说；重跑 `_build/build_figure_registry.py .`；看全部新图；按 `_build/RULINGS_AUDIT_BRIEF_20261106.md` 的方法对本轮 V18-MAE-11…18 做落实审计，残留词 grep：`操作 18`、`列表到齐计数`、`完成计数器`、`对象标识`、`hub 中心`、`HUB_CRU`、`五个单元`、`五单元`、`环长`、`回绕`、`-CONN.svg`。

## 3 纪律

- 只改正式稿与本任务书点名的脚本 / 登记表；不改 V1.7_3、ISA、目录稿、`Claude_Design_Spec/`。
- 名称按外部输入信息篇 §6；"通道 / 道"只指物理链路，执行部件叫搬运引擎。
- 每处改动写"改前 → 改后"，报告按文档分节，写到 `_build/MAE_CRU_MERGE_REPORT_<A|B|C|D>_20261106.md`。
- 遇到规则冲突或依据缺失，不自行设计，列"待协调者"。
- 中文写作；矩阵 AW 写法；写"默认"不写"缺省"。
