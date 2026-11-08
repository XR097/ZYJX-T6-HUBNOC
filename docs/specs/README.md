# 当前模块规格（2026-11-08）

本目录是唯一的正文基线；文件名不再带导入批次日期。各篇中的“为什么”和被否方案用于解释当前设计，不是并行生效的旧版本。

| 入口 | 内容 |
|---|---|
| [ONCHIP_DATAPATH_ARCH.md](ONCHIP_DATAPATH_ARCH.md) | 总体数据/控制拓扑；§7 为口宽、条数、方向的统一出处 |
| [DATA_TRANSFER_PROTOCOL.md](DATA_TRANSFER_PROTOCOL.md) | 地址、段选、ready、写入握手、长度表与完成语义 |
| [DATA_ORGANIZATION.md](DATA_ORGANIZATION.md) | 数据记录、紧密对象和存储布局 |
| [TRANSFER_DATA_REGISTRY.md](TRANSFER_DATA_REGISTRY.md) | 搬运对象、路径、打包及完成判据登记 |
| [HUB_NOC.md](HUB_NOC.md) | L2 侧 H2C、C2H 和命令网转发 |
| [HUB_IDN.md](HUB_IDN.md) | NI 一路 32 B 输入、按字核集合多播到四核 |
| [MAE_CRU.md](MAE_CRU.md) | MAE 内 L2→CRU→L2 合并、编解码和压缩 |
| [MAE_INTEGRATION.md](MAE_INTEGRATION.md)、[MAE_ENG.md](MAE_ENG.md) | MAE 模块边界、地址生成、报告及完成 |
| [MAE_NI_EXT.md](MAE_NI_EXT.md)、[MAE_NI_INT.md](MAE_NI_INT.md)、[MAE_DSU.md](MAE_DSU.md) | 外部接口、内部 NI、按字重排 |
| [L1_SRAM.md](L1_SRAM.md)、[L2_SRAM.md](L2_SRAM.md) | 端点接收、bank 落位和最终写入握手 |
| [L3PU_EXTERNAL_INFORMATION.md](L3PU_EXTERNAL_INFORMATION.md) | 外部信息与接口背景 |
| `VNU_*.md` | LOSS、NLU、OPT、QNT、SEL 模块规格 |

`figs/` 只保留当前正文引用的 SVG；`_build/` 保留必要生成/检查工具，运行方法见其 [README](_build/README.md)。预览、缓存、一次性迁移脚本和旧审计报告不作为规格保留。

跨篇残留冲突见 [当前问题台账](../reviews/open_issues_current.md)。
