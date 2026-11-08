# HUB NoC / R-hub 规格包

本目录把 V1.5 架构需求整理成可进入 RTL 设计和模块级验证的规格。它定义接口语义、周期级行为、状态机、验证点和未决项；不替代原始需求 PDF。

## 权威来源

1. `../SPEC_TRANSFER_PROTOCOL_V1.5.pdf`：协议 A/B、flit、侧带、VC、信用和 `last/nw8` 语义。
2. `../HUB_NOC.pdf`：HUB-DN、HUB-UP、HUB-ATT、HUB-SYNC 的模块合同。
3. `../HUB_RHUB.pdf`：四路部分和归约、量化和回送合同。
4. `../DATA_LAYOUT_V1.5.pdf`：L2/L1 存储布局和完成计数背景。

`*_易读版.md` 只作为导航。若与原始 PDF 不一致，以原始 PDF 和项目最新裁定为准。

## 文档索引

| 文件 | 内容 | 阶段 |
|---|---|---|
| `00_requirements_trace.md` | 条款到模块、接口、时序和验证点的追踪 | M0 |
| `01_hub_noc_contract.md` | HUB NoC 子模块和边界接口合同 | M1 |
| `02_hub_noc_timing_fsm.md` | HUB NoC 周期级时序和状态机 | M2 |
| `03_rhub_contract.md` | R-hub 子模块和边界接口合同 | M1 |
| `04_rhub_timing_fsm.md` | R-hub 周期级时序和状态机 | M2 |
| `05_open_issues.md` | 未决参数、影响、负责人和冻结门槛 | M3 |
| `06_verification_plan.md` | 断言、定向测试、参考模型和场景覆盖 | M4 |
| `07_leaf_interface_matrix.md` | 每个叶子模块的 bundle、状态资源和成交/反压条件 | M1/M2 |

## 统一约定

- 周期编号从复位释放后的第一个时钟沿开始；`fire` 表示本周期完成一次传输。
- 协议 B 的普通 flit 为 32 B；下行侧带 12 bit，上行侧带 14 bit，均不携带地址。
- 地址由接收端的区域/游标逻辑生成；真正写入 L2 bank 后才更新 `WCNT`。
- 末 flit 的所有目的端信用返还完成后才更新 `RCNT`；链路信用和资源完成不可互相替代。
- 文档中的“建议值”必须在 RTL 中做成参数，并由 `05_open_issues.md` 的冻结记录驱动。

## 阶段门槛

M0 追踪矩阵完整 → M1 接口合同无孤立信号 → M2 周期时序/状态机通过评审 → M3 未决项均有处置 → M4 验证计划覆盖三条端到端场景 → M5 才允许开始 RTL。
