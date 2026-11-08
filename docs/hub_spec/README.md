# HUB / MAE_CRU 当前规格索引（2026-11-08）

依据为 [../specs/](../specs/README.md) 中的架构篇、HUB_NOC、HUB_IDN、MAE_CRU、传输协议、MAE_ENG、L1/L2 正文。

| 文件 | 内容 |
|---|---|
| [00_requirements_trace.md](00_requirements_trace.md) | HUB_NOC、HUB_IDN、MAE_CRU 当前条款追踪 |
| [01_hub_noc_contract.md](01_hub_noc_contract.md) | 中央 L2 侧 H2C/C2H/命令网合同 |
| [02_hub_noc_timing_fsm.md](02_hub_noc_timing_fsm.md) | H2C 单源、C2H 直通和回程时序 |
| [03_mae_cru_contract.md](03_mae_cru_contract.md) | MAE_CRU L2↔L2 合同 |
| [04_mae_cru_timing.md](04_mae_cru_timing.md) | 四象限读、报告、合并与写回阶段 |
| [05_open_issues.md](05_open_issues.md) | 当前责任范围的未决项索引 |
| [06_verification_plan.md](06_verification_plan.md) | HUB_NOC、HUB_IDN、MAE_CRU 验证计划 |
| [07_leaf_interface_matrix.md](07_leaf_interface_matrix.md) | 建议的实现分解接口 |
| [08_hub_idn_contract.md](08_hub_idn_contract.md) | HUB_IDN 接口合同 |
| [09_hub_idn_timing_fsm.md](09_hub_idn_timing_fsm.md) | HUB_IDN 流水、分叉与回程时序 |

本目录不另定正文之外的串行状态机、错误状态或检查。旧 RHUB/VC/credit/flit 模型仅从 Git 追溯；跨篇冲突见 [当前问题台账](../reviews/open_issues_current.md)。
