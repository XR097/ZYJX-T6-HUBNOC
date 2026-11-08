# HUB / MAE_CRU 当前规格索引

本目录按 2026-11-07 新版基线重写。当前权威来源是 `../Module_Docs_Redraft_20261103/` 下的 `HUB_NOC.md`、`MAE_CRU.md`、`DATA_TRANSFER_PROTOCOL.md`、`MAE_ENG.md`、`L1_SRAM.md` 和 `L2_SRAM.md`。

旧版 VC/credit/flit/HUB 地址游标/独立 RHUB 归约结论保存在 `_archive_codex_20261028/`，仅用于历史追溯。

| 文件 | 用途 |
|---|---|
| `00_requirements_trace.md` | 新版条款到责任方、接口和验证的追踪 |
| `01_hub_noc_contract.md` | HUB 当前边界与接口合同 |
| `02_hub_noc_timing_fsm.md` | 可调流水、分叉、MUX、分流和握手时序 |
| `03_rhub_contract.md` | RHUB 退役说明及 MAE_CRU 当前合同 |
| `04_rhub_timing_fsm.md` | MAE_CRU 到齐/合并/输出时序 |
| `05_open_issues.md` | 当前未决项，和 `../reviews/open_issues_current.md` 同步 |
| `06_verification_plan.md` | 新版协议的模块级和端到端验证计划 |
| `07_leaf_interface_matrix.md` | 实现分解接口；不代表新增架构边界 |

## 当前结论

HUB 是透明数据/控制转发结构，不发令、不生成或累加地址、不解析载荷、不做归约/合并/排序、不维护完成计数。地址、目的核掩码和源顺序由 MAE 搬运引擎或本核 CCU 提供。MAE_CRU 是 MAE 的运算级，不是独立 RHUB。
