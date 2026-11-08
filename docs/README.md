# HUB / RHUB 规格文档索引

本目录按“当前基线、分析结论、历史资料”分层。当前实现依据是 `Module_Docs_Redraft_20261103/` 下的新版模块稿与协议稿；根目录旧版 PDF、易读稿和 2026-10-28 的审查台账已移入 `legacy/` 与 `reviews/archive_20261028/`，仅用于追溯。

## 当前基线

- `Module_Docs_Redraft_20261103/HUB_NOC.md`：HUB NoC 当前合同。HUB 是透明搬运、分叉和分流链路，不产生地址、不做归约、不做完成计数。
- `Module_Docs_Redraft_20261103/MAE_CRU.md`：MAE_CRU 当前合同。它取代旧 R-hub 中心归约单元，归约由 MAE 搬运指令驱动，输出 BF16 直出。
- `Module_Docs_Redraft_20261103/DATA_TRANSFER_PROTOCOL.md`：当前传输、地址、握手和完成语义的协议基线。
- `Module_Docs_Redraft_20261103/MAE_ENG.md`、`L1_SRAM.md`、`L2_SRAM.md`：地址主、存储端点和完成计数的配套合同。

## 我们维护的分析结论

- `hub_spec/`：面向 HUB/RHUB 责任范围的追踪、合同、时序、验证和接口矩阵。内容已按新版基线重写。
- `reviews/module_delta_20261107.md`：旧版与新版的差异，以及旧问题的解决状态。
- `reviews/open_issues_current.md`：对新版仍有效的问题点和关闭门槛。

## 历史资料

- `legacy/`：旧 HUB_NOC/HUB_RHUB/协议/数据布局 PDF 与易读稿。
- `reviews/archive_20261028/`：旧版审查报告和旧未决项台账。
- `hub_spec/_archive_codex_20261028/`：旧版 Codex 规格草案。

历史资料不作为当前 RTL 合同；如与当前基线冲突，以新版模块稿、协议稿和本目录的当前分析为准。
