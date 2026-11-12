# L3PU 片上架构文档集 V1.8

> Owner: WangYizhao｜2026-11-11

## 1 这是什么

V1.8 是 L3PU 片上数据通路与各模块的唯一正式需求文档集，给设计和验证使用。**需求章只冻结端口、握手、并发与速率、功能语义和硬约束；内部结构放在参考实现章。** 未决项集中登记在 `docs/reviews/open_issues_current.md`，不能从本目录的历史说明推断为已关闭。

## 2 统一目录（每篇都按此八章）

| 章 | 内容 |
|---|---|
| 1 概述 | 本模块是什么、给谁用、在哪个组里 |
| 2 接口需求 | 2.1 架构图与接口汇总（复用原架构图 / 连接图；图中框内结构是参考实现，以框外各口为准）；2.2 起一个接口一节，2.x.1 起写明细与特殊需求 |
| 3 功能描述 | 3.1 功能一览；3.2 起逐个功能 |
| 4 性能指标 | 各口速率、同时使用的口、并发条件（引用架构篇 CONC-n）、要求值表 |
| 5 约束与由使用者保证的事项 | 硬约束；由编译链、CCU、MAE 等保证的事项 |
| 6 验收 | 只对第 2–5 章条目列验收项，含与上下游的对接检查 |
| 7 参考实现 | 可以换、换了别的模块不用改的内容：内部结构、FIFO、轮流、bank 组织、参考容量与门数、性能计数 |
| 8 为什么 | 需求的理由与参考实现的选型理由；用户原话与 V18 编号 |

架构篇、协议篇、数据组织篇、登记篇、外部信息篇与两篇集成篇是约定篇，按同样八章组织："接口需求"写它定义的口、信号与格式，"功能描述"写规则。

## 3 文档清单与阅读顺序

建议先读约定篇，再按组读模块篇。

**约定篇**
1. `ONCHIP_DATAPATH_ARCH.md`：片上数据通路架构。**全口宽总表（§2.7，PORT-nn）、段选信号 `seg` 与"象限""堆"的定义（§3.3）、存储并发约定 CONC-1…CONC-6（§3.4，并发条件的唯一出处）、计算核两种工作模式表（§3.6）**；术语新旧对照（§1.2）。
2. `DATA_TRANSFER_PROTOCOL.md`：片上数据传输协议（核间握手写流、写入握手、命令网与专用信号组的载荷语义）。
3. `DATA_ORGANIZATION.md`：片上数据组织（数据块、紧凑 token 记录、W 类两种字形态、并行切分与落点、各类数据的推荐放法、DDR 布局）。
4. `TRANSFER_DATA_REGISTRY.md`：传输数据类别登记（REG-nn）。
5. `L3PU_EXTERNAL_INFORMATION.md`：外部输入信息五类（指令、配置表、调用描述符、列表、数据）。

**存储与 HUB**：`L1_SRAM.md`、`L1_LANDING_BRIDGE.md`（接收桥）、`L2_SRAM.md`、`HUB_NOC.md`、`HUB_IDN.md`。

**MAE 组**：`MAE_INTEGRATION.md`（组集成）、`MAE_ENG.md`、`MAE_NI_EXT.md`、`MAE_NI_INT.md`、`MAE_DSU.md`、`MAE_CRU.md`。

**MXU 组**（11-11 由另一会话新写，按同一八章目录）：`MXU_INTEGRATION.md`（组集成）、`MXU_FEED.md`（供数）、`MXU_ARR.md`（阵列）、`MXU_CONTROLLER.md`（MXU 控制器）。

**VNU 组**：`VNU_INTEGRATION.md`（组集成）、`VNU_CONTROLLER.md`（VNU 控制器，11-11 新写）、`VNU_EPI.md`、`VNU_NLU.md`、`VNU_SEL.md`、`VNU_QNT.md`、`VNU_SMP.md`、`VNU_LOSS.md`、`VNU_OPT.md`。

**CIF**：`CIF.md`（与 M55 的调用接口：APB 寄存器、复位与启停、中断；11-11 新写）。

核内有三个控制器：CCU（总控 + 4 个 pod 各自的供数引擎，L1 地址的唯一来源）、MXU_CONTROLLER、VNU_CONTROLLER（各管本模块内部缓冲的位置，不是发令方）。

**暂存文档**（还没成篇的模块；MXU、CIF 两份的条目已大多被新写的正式篇吸收，逐条标了"已吸收，见 X 篇 §n"；各篇移出的属于它们的内容，条目编号 `<模块>-S-nn`，注明来源篇与源稿节号）：`MXU_STAGING.md`、`CCU_STAGING.md`、`LIC_STAGING.md`、`CIF_STAGING.md`、`CORE_INTEGRATION_STAGING.md`（计算核集成）。这些模块的正式需求稿写成后，暂存条目并入正式稿。

## 4 修改记录与辅助文件

- `figs/`：正文引用的现行 SVG 图件。
- `_build/`：只保留登记、交叉引用和分层检查脚本及总图件登记表；历史报告、源稿快照、重整规则、临时片段和缓存通过 Git 追溯。

## 5 写作纪律

文件头只有 `> Owner: WangYizhao｜<日期>` 一行；正文只写现行设计，修订说明进 `CHANGELOG_V1.8.md`；矩阵用 AW 写法（$Y = XW$，$W$ 为 $K \times M$）；写"默认"不写"缺省"；状态标记只用【待确认】【待标定】【设计者定】；当前架构不含容错设计（V18-TP-75）。
