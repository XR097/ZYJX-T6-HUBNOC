# 图件登记表（自动生成）：specs

> 由 `_build/build_figure_registry.py` 扫描生成，不要手改；工具说明见 `_build/README.md`。扫描范围：本目录下全部 *.md（图引用）与 _build/*.py（生图函数）。

## DATA_ORGANIZATION.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-TP-OBJECT-ALIGN | 1.2 对齐：数据块起点在存储字边界，记录紧挨，段按字节对齐；跨字由存储处理 | `fig_object_align()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-DORG-SEGMENT | 2.1 32 通道段：段尺度 + keep 位图 + 每个保留通道的 F 标志与码，元素位宽是位点属性 | `fig_segment()` | `_build/draw_data_org.py` | ✓ |
| FIG-TP-FIXED-ITEM | 3 定长项与标量 | `fig_fixed_item()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-DORG-SPLIT-T | 5.2 核间按 T 切分：各核算不同 token，产出留本核 | `fig_split_t()` | `_build/draw_data_org.py` | ✓ |
| FIG-DORG-SPLIT-M | 5.3 核间按 M 切分：各核算不同输出通道，四象限各一个数据块 | `fig_split_m()` | `_build/draw_data_org.py` | ✓ |
| FIG-DORG-SPLIT-K | 5.4 核间按 K 切分：各核算部分和，同址异象限，MAE_CRU 归约 | `fig_split_k()` | `_build/draw_data_org.py` | ✓ |
| FIG-TP-WINDOW-GATHER | 5.7 权重驻留位点的产出：每个窗口一个数据块，MAE 按长度表聚集 | `fig_window_gather()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-DORG-DDR-STD | 6.1 权重标准布局：一拍一个 $k$ 行 × 4 个列组，尺度与 bias 另成数据块 | `fig_ddr_std()` | `_build/draw_data_org.py` | ✓ |
| FIG-DORG-DDR-COL | 6.2 权重列深度优先布局：一拍一列 64 个连续 $k$，尺度另成数据块 | `fig_ddr_col()` | `_build/draw_data_org.py` | ✓ |
| FIG-DORG-DDR-ACT | 6.3 激活值、残差与 K / V 在 DDR | `fig_ddr_act()` | `_build/draw_data_org.py` | ✓ |

## DATA_TRANSFER_PROTOCOL.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-TP-ADDR-MAP | 2.2 地址 = 24 bit 段内字节位置；堆、类、象限由段选单独给出 | `fig_addr_map()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-ADDR-ACCUM | 2.4.2 核间：C2H 由本核 CCU 逐拍给出，H2C / IDN / NI 由 MAE 搬运引擎逐拍给出 | `fig_addr_accum()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-COMPACT | 2.5 对齐与紧密存放 | `draw()` | `_build/draw_compact.py` | ✓ |
| FIG-TP-ARCH-INTERCORE | 3 核间协议：带地址的握手写流 | `fig_intercore()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-STREAM-BEAT | 3.4 逐拍地址由该链路的发令方生成：C2H 归本核 CCU，其余归 MAE 搬运引擎 | `fig_stream_beat()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-LENGTH-REPORT | 4.3 变长对象：按实际长度紧挨存放，长度表单独存，CCU 发送，写进 L2 后发出报告，MAE 搬完后转发应写量 | `fig_length_report()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-ARCH-INCORE | 5 核内协议：RRAM | `fig_incore()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-INCORE-TIMING | 5.3 读：固定 1 拍，无 ready，无 busy | `fig_timing()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-STALL-CHAIN | 6 核内握手：相邻级 stall | `fig_stall_chain()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-ARCH-CTRL | 8 命令网协议：64 bit 握手消息流 | `fig_ctrl()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-CTRL-MSG | 8.5 消息骨架 | `fig_ctrl_msg()` | `_build/draw_transfer_protocol.py` | ✓ |

## HUB_IDN.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-HUB_IDN-ARCH | 2 数据从哪来、到哪去 | `fig_arch()` | `_build/draw_hub_idn.py` | ✓ |
| FIG-HUB_IDN-CORE-SET | 4.2 几核共享 M0 带宽：MAE_ENG 把连续存储字轮流排给各核 | `fig_core_set()` | `_build/draw_hub_idn.py` | ✓ |
| FIG-HUB_IDN-MCAST | 5 多播：分叉点按已取位分叉，各目的核独立取走 | `fig_mcast()` | `_build/draw_hub_idn.py` | ✓ |

## HUB_NOC.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-HUB_NOC-ARCH-DATA | 2 数据从哪来、到哪去 | `fig_data()` | `_build/draw_hub_noc.py` | ✓ |
| FIG-HUB_NOC-ARCH-CTRL | 2 数据从哪来、到哪去 | `fig_ctrl()` | `_build/draw_hub_noc.py` | ✓ |
| FIG-HUB_NOC-MCAST | 5.2 多播：分叉点按已取位分叉，各目的核独立取走 | `fig_mcast()` | `_build/draw_hub_noc.py` | ✓ |
| FIG-HUB_NOC-ACK | 7 写入握手的回程 | `fig_ack()` | `_build/draw_hub_noc.py` | ✓ |

## L1_SRAM.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-L1_SRAM-BANKS | 1.2 24 个单端口 bank 分两堆，成对做 ping-pong | `fig_banks()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-PINGPONG | 1.3 一堆只读、一堆只写，由指令的堆选选 | `fig_pingpong()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-ABANK-CFG | 1.6 配置项：A 类 4 bank 或 8 bank | `fig_abank_cfg()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-ARCH | 2 数据从哪来、到哪去 | `fig_l1_arch()` | `_build/draw_l1_arch.py` | ✓ |
| FIG-L1_SRAM-RING | 3.3 核内与 C2H 地址由 CCU 给出，落地地址由 MAE 搬运引擎逐拍给出，L1 不做取模 | `fig_ring()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-COMPACT-A | 3.4a 任意字节起点的访问：A 类的读写口自己处理，W / S 类除外 | `draw()` | `_build/draw_compact.py` | ✓ |
| FIG-L1_SRAM-MAP-W | 4.2 W 类占 8 个 bank：行字区一段落同一深度，列字区一个存储字 = 一列 64 个连续 $k$ | `fig_map_w()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-MAP-W-HALF | 4.3 两来源时一段落 4 个 bank 的相邻两个深度 | `fig_map_w_half()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-MAP-A | 4.4 A 类：相邻存储字轮流落 bank | `fig_map_a()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-LANE-PICK | 6.1 权重 lane：按（列, pod 掩码）列表逐道取字 | `fig_lane_pick()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-COLREAD-1SRC | 6.1a 列字区的读口重组器：按段对读，拼回整段 | `fig_colread_1src()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-COLREAD-2SRC | 6.1a 列字区的读口重组器：按段对读，拼回整段 | `fig_colread_2src()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-TWO-SRC | 6.2 两来源：W0 与 W1 各供一组 pod | `fig_two_src()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-KHI-RESIDENT-VS-REREAD | 7.8a 精算 K hi 的两种来源：驻留模式与重读模式 | `main()` | `_build/draw_l1_khi.py` | ✓ |

## L2_SRAM.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-L2_SRAM-ARCH | 2 数据从哪来、到哪去 | `fig_arch()` | `_build/draw_l2_arch.py` | ✓ |
| FIG-L2_SRAM-OBJ-ALIGN | 3.4 片上数据的排法：③ 档记录紧挨、对象起点对齐、长度表单独存 | `fig_obj_align()` | `_build/draw_l2_sram.py` | ✓ |
| FIG-L2_SRAM-MAP-HEAP | 4.2 地址 [h][q][j] 落在哪个 bank、哪个深度 | `fig_map_heap()` | `_build/draw_l2_sram.py` | ✓ |

## L3PU_EXTERNAL_INFORMATION.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-INFO-FOUR-KINDS | L3PU 的外部输入信息：指令、配置表、调用描述符、列表、数据 | `fig_four_kinds()` | `_build/draw_info.py` | ✓ |

## MAE_CRU.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_CRU-ARCH | 2 数据从哪来、到哪去 | `fig_cru()` | `_build/draw_mae_arch.py` | ✓ |
| FIG-MAE_CRU-SUM | 3.1 逐元素相加（归约）：解码后逐元素求和，标准加法树，次序按象限固定 | `fig_sum()` | `_build/draw_mae_cru.py` | ✓ |
| FIG-MAE_CRU-RESID | 3.1a 逐元素相加（残差加）：归约结果与 L2 里的残差相加，一次编码写回残差流 | `fig_resid()` | `_build/draw_mae_cru.py` | ✓ |
| FIG-MAE_CRU-READSET | 3.3 读集合并：按位取并 | `fig_readset()` | `_build/draw_mae_cru.py` | ✓ |

## MAE_DSU.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_DSU-ARCH | 2 数据从哪来、到哪去 | `fig_dsu()` | `_build/draw_mae_arch.py` | ✓ |
| FIG-MAE_DSU-REGROUP | 4.1 按字重排：攒 $n$ 行，把一拍里分属几个核的粒子重排成各核的整字 | `fig_regroup()` | `_build/draw_mae_dsu.py` | ✓ |
| FIG-MAE_DSU-SPLICE | 4.2 转置：两种 DDR 布局的前向权重 → $W^{\mathsf T}$ 列字块 | `fig_splice()` | `_build/draw_mae_dsu.py` | ✓ |
| FIG-MAE_DSU-TRANSPOSE | 4.2 转置：两种 DDR 布局的前向权重 → $W^{\mathsf T}$ 列字块 | `fig_transpose()` | `_build/draw_mae_dsu.py` | ✓ |
| FIG-MAE_DSU-TWOPLANE | 4.3 两平面合并：DDR 两处的 hi 字与 lo 字 → 同一记录相邻地址 | `fig_twoplane()` | `_build/draw_mae_dsu.py` | ✓ |
| FIG-MAE_DSU-SIDEBAND | 5.1 块尺度：$e_{\max}$ 与 $\Delta_m$，整数运算无损 | `fig_sideband()` | `_build/draw_mae_dsu.py` | ✓ |

## MAE_ENG.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-TP-LENGTH-REPORT | 10.4 C2H 的发出报告：按地址配给指令 | `fig_length_report()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-MAE_ENG-ARCH | 2 数据从哪来、到哪去 | `fig_eng()` | `_build/draw_mae_arch.py` | ✓ |
| FIG-MAE_ENG-ARITH | 5.2 算术生成器：为什么要嵌套，要解决什么 | `fig_arith()` | `_build/draw_mae_eng.py` | ✓ |
| FIG-MAE_ENG-LIST | 5.3 列表驱动生成器：外层循环换成列表项 | `fig_list()` | `_build/draw_mae_eng.py` | ✓ |
| FIG-MAE_ENG-KHI-GATHER | 5.4 驻留 / 重读只改变 gather 项字节数 | `fig_khi()` | `_build/draw_mae_eng.py` | ✓ |
| FIG-MAE_ENG-QSPLICE | 5.9 象限并存的数据：读时四道并行合并，写 L2 时按象限拆分 | `fig_qsplice()` | `_build/draw_mae_eng.py` | ✓ |

## MAE_INTEGRATION.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_INTEGRATION-ARCH-DATA | 3.1 数据口 | `fig_data()` | `_build/draw_mae_integration.py` | ✓ |
| FIG-MAE_INTEGRATION-ARCH-CTRL | 3.2 命令口 | `fig_ctrl()` | `_build/draw_mae_integration.py` | ✓ |
| FIG-MAE_INTEGRATION-PATH | 4 按口对看整组的数据路径 | `fig_path()` | `_build/draw_mae_integration.py` | ✓ |

## MAE_NI_EXT.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_NI_EXT-ARCH | 2 数据从哪来、到哪去 | `fig_ni_ext()` | `_build/draw_mae_arch.py` | ✓ |
| FIG-MAE_NI_EXT-PIN-WORDPACK | 7.2 地址换算与拼字：L2 逻辑地址 = A − A_PIN | `fig_pin_wordpack()` | `_build/draw_mae_ni_ext.py` | ✓ |

## MAE_NI_INT.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_NI_INT-ARCH | 2 数据从哪来、到哪去 | `fig_ni_int()` | `_build/draw_mae_arch.py` | ✓ |

## ONCHIP_DATAPATH_ARCH.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-TP-ARCH-INTERCORE | 4 核间链路 | `fig_intercore()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-ARCH-INCORE | 3 核内口：收到 L1 读写口与集成输出端口这一级 | `fig_incore()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-ARCH-CTRL | 5 命令网拓扑 | `fig_ctrl()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-ARCH-LINKS | 1 全芯片拓扑与三种总线 | `fig_links()` | `_build/draw_tp_arch.py` | ✓ |

## VNU_LOSS.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_LOSS-CONN | 2 数据从哪来、到哪去 | `fig_loss()` | `_build/draw_vnu_conn.py` | ✓ |
| FIG-VNU_LOSS-ORDER | 3.1.2 输出合同：词号升序去重，dz 与列表同序压紧 | `fig_order()` | `_build/draw_vnu_loss.py` | ✓ |
| FIG-VNU_LOSS-LOGPROB | 3.2 截断分布统计：对 K_top 项分布求所选 token 的 log-prob | `fig_logprob()` | `_build/draw_vnu_loss.py` | ✓ |

## VNU_NLU.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_NLU-CONN | 2 数据从哪来、到哪去 | `fig_nlu()` | `_build/draw_vnu_conn.py` | ✓ |
| FIG-VNU_NLU-NORM-SPLIT | 3.2 沿向量的归约与归一化：先求统计量，再缩放 | `fig_norm_split()` | `_build/draw_vnu_nlu.py` | ✓ |
| FIG-VNU_NLU-ONLINE-SOFTMAX | 3.4 在线 softmax 与 attention 输出累加：分数分组到达，按更新组统一基准 | `fig_online_softmax()` | `_build/draw_vnu_nlu.py` | ✓ |
| FIG-VNU_NLU-STREAM-SUM | 3.5 跨向量的流式累加：逐通道累加，可从读回的部分和继续 | `fig_stream_sum()` | `_build/draw_vnu_nlu.py` | ✓ |

## VNU_OPT.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_OPT-CONN | 2 接口规范 | `fig_opt()` | `_build/draw_vnu_conn.py` | ✓ |

## VNU_QNT.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_QNT-CONN | 2 数据从哪来、到哪去 | `fig_qnt()` | `_build/draw_vnu_conn.py` | ✓ |
| FIG-VNU_QNT-MX-ENCODE | 3.2 按组量化编码：沿一维每 g 个元素求共享尺度，逐元素编码 | `fig_mx_encode()` | `_build/draw_vnu_qnt.py` | ✓ |
| FIG-VNU_QNT-AMAX-SPLIT | 3.2 按组量化编码：沿一维每 g 个元素求共享尺度，逐元素编码 | `fig_amax_split()` | `_build/draw_vnu_qnt.py` | ✓ |
| FIG-VNU_QNT-PLANE-BITSPLIT | 3.3 两平面表示：一个码按位拆成 hi / lo，或把量化误差再量化一次 | `fig_bitsplit()` | `_build/draw_vnu_qnt.py` | ✓ |
| FIG-VNU_QNT-PLANE-RESIDUAL | 3.3 两平面表示：一个码按位拆成 hi / lo，或把量化误差再量化一次 | `fig_residual()` | `_build/draw_vnu_qnt.py` | ✓ |
| FIG-VNU_QNT-KEEP-PACK | 3.4 按判决位压紧：去掉不读的元素，其余按原序连续存放 | `fig_keep_pack()` | `_build/draw_vnu_qnt.py` | ✓ |
| FIG-VNU_QNT-DECODE | 3.6 解码与还原：码 × 尺度，还原成计算用的值 | `fig_decode()` | `_build/draw_vnu_qnt.py` | ✓ |

## VNU_SEL.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-VNU_SEL-CONN | 2 数据从哪来、到哪去 | `fig_sel()` | `_build/draw_vnu_conn.py` | ✓ |
| FIG-VNU_SEL-THRESH | 3.2 阈值模式：与 1 个或 2 个门限比较 | `fig_thresh()` | `_build/draw_vnu_sel.py` | ✓ |
| FIG-VNU_SEL-RELATIVE | 3.3 相对阈值模式：门限随本选择域的统计量变化 | `fig_relative()` | `_build/draw_vnu_sel.py` | ✓ |
| FIG-VNU_SEL-TOPK | 3.4 流式 TOPK 模式：边到达边插入，选择域结束时发布前 k 名 | `fig_topk()` | `_build/draw_vnu_sel.py` | ✓ |
| FIG-VNU_SEL-MASK | 4.4 档号 3 的 token 不参与 | `fig_mask()` | `_build/draw_vnu_sel.py` | ✓ |

## 核对

- 有 SVG 但无文档引用（0）：无
- 被引用但 SVG 不存在（0）：无
- 被引用但找不到生图函数（0）：无
