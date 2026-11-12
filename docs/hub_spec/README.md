# HUB / MAE_CRU 设计与验证索引

`docs/specs/` 的 V1.8 正式篇是唯一合同来源；本目录只保留面向 HUB / MAE_CRU 的追踪、未决项、验证计划、实现分解和术语，不重复抄写合同正文。

| 文件 | 用途 |
|---|---|
| [00_requirements_trace.md](00_requirements_trace.md) | HUB_NOC、HUB_IDN、MAE_CRU 的要求、责任方和状态 |
| [05_open_issues.md](05_open_issues.md) | 设计前门槛的一页速览 |
| [06_verification_plan.md](06_verification_plan.md) | 用例、参数、退出条件和结果回填规则 |
| [07_leaf_interface_matrix.md](07_leaf_interface_matrix.md) | RTL 分解建议与关键不变量 |
| [10_glossary.md](10_glossary.md) | 信号、缩写和状态词 |

正式合同直接阅读：`docs/specs/HUB_NOC.md`、`HUB_IDN.md`、`MAE_CRU.md`、`MAE_ENG.md`、`DATA_TRANSFER_PROTOCOL.md`、`ONCHIP_DATAPATH_ARCH.md`。历史对照通过 Git 追溯，不放进交付树。

当前真正的设计阻塞项和外部输入见[问题台账](../reviews/open_issues_current.md)。关闭任何条目时，同时更新正式篇、追踪矩阵和验证计划。
