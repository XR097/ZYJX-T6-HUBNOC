# RHUB 退役与 MAE_CRU 当前合同

旧 R-hub（独立四路 VC2 入口、pid/owner 对齐、固定加法树、MXFP6 g32 量化、组序号和 D-40 VC2 回送）属于历史架构，见 `_archive_codex_20261028/03_rhub_contract.md` 与 `legacy/`。

当前对应模块是 `Module_Docs_Redraft_20261103/MAE_CRU.md`，它属于 MAE 组，不属于 HUB 组：

- 搬运指令选择直通、MAE_DSU 或 MAE_CRU 运算级。
- 指令给合并种类、参与核、CRU 内地址范围和每地址应到份数。
- C2H 或读路径按地址写入 CRU；到齐即做部分和、标量合并或读集合并。
- 结果为 BF16 直出；不做旧 RHUB 的 MXFP6 量化、owner/pid 管理或独立回送协议。
- 输出可作为 H2C MUX 的第二源，或经 MAE 的 L2 写客户送出。

本文件只保留迁移边界，RTL 不应再实例化名为 `rhub_*` 的独立中心单元。
