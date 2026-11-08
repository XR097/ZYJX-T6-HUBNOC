# HUB / RHUB 规格文档索引

当前基线是 `Module_Docs_Redraft_20261103/` 内 2026-11-08 版本的正文模块稿和协议稿。旧 PDF、易读稿、旧审查台账和旧 Codex 草案仍保留在历史目录，仅用于追溯。

## 当前基线

- `HUB_NOC.md`：中央 L2 侧的四条 H2C 道、四条 C2H 通路和命令网转发。
- `HUB_IDN.md`：NI 侧一路 32 B 输入、按每字核集合分发到四核的 IDN 多播网。
- `MAE_CRU.md`：MAE 内部的 L2→CRU→L2 合并运算级；不经 HUB/HUB_IDN。
- `DATA_TRANSFER_PROTOCOL.md`：地址、段选、握手、完成、长度表和两条 MAE_CRU 指令依赖的协议基线。
- `MAE_ENG.md`、`L1_SRAM.md`、`L2_SRAM.md`：地址主、存储端点、紧密对象和最终写入语义。

## 我们维护的分析

- `hub_spec/`：当前 HUB_NOC、HUB_IDN、MAE_CRU 责任范围的合同、时序、验证和接口矩阵。
- `reviews/module_delta_20261107.md`：截至 2026-11-08 的新旧结论审查。
- `reviews/open_issues_current.md`：当前仍需审查、仿真或标定的问题。

历史资料不作为当前 RTL 合同；若与当前正文冲突，以新版模块稿、协议稿和本目录的当前分析为准。
