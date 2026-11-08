# 图件登记表（自动生成）：Module_Docs_Redraft_20261103

> 由 `_build/build_figure_registry.py` 扫描生成，不要手改；手写说明放各篇的 FIGURE_REGISTRY_<篇>.md。扫描范围：本目录下全部 *.md（图引用）与 _build/*.py（生图函数）。

## DATA_TRANSFER_PROTOCOL.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-TP-ARCH-LINKS | 1 协议分层与覆盖范围 | `fig_links()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-ADDR-MAP | 2.2 逻辑地址 = 堆位 + 类位 + 字节号 | `fig_addr_map()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-ADDR-ACCUM | 2.4.2 核间：C2H 由本核 CCU 逐拍给出，H2C / IDN / NI 由 MAE 搬运引擎逐拍给出 | `fig_addr_accum()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-COMPACT | 2.5 对齐使用与紧密访存 | `draw()` | `_build/draw_compact.py` | ✓ |
| FIG-TP-ARCH-INCORE | 3 核内协议：RRAM | `fig_incore()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-INCORE-TIMING | 3.3 读：固定 1 拍，无 ready，无 busy | `fig_timing()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-STALL-CHAIN | 4 核内握手：相邻级 stall | `fig_stall_chain()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-ARCH-INTERCORE | 5 核间协议：带地址的握手写流 | `fig_intercore()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-STREAM-BEAT | 5.4 逐拍地址由该链路的发令方生成：C2H 归本核 CCU，其余归 MAE 搬运引擎 | `fig_stream_beat()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-LENGTH-REPORT | 7.3 变长对象：按离线上限分槽存储，CCU 发送，写进 L2 后发出报告 | `fig_length_report()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-ARCH-CTRL | 8 命令与标量网协议：64 bit 握手消息流 | `fig_ctrl()` | `_build/draw_tp_arch.py` | ✓ |
| FIG-TP-CTRL-MSG | 8.6 消息骨架 | `fig_ctrl_msg()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-OBJECT-ALIGN | 9.1 对齐使用：每条记录占整数个存储字 | `fig_object_align()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-TOKEN-SLOT | 9.7 段按 MX 组产生，记录按 token 槽拼接 | `fig_token_slot()` | `_build/draw_transfer_protocol.py` | ✓ |
| FIG-TP-SLOT-COUNT | 9.8 token 位置 | `fig_slot_count()` | `_build/draw_transfer_protocol.py` | ✓ |

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
| FIG-L1_SRAM-PINGPONG | 1.3 一堆只读、一堆只写，由地址的堆位选 | `fig_pingpong()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-ABANK-CFG | 1.6 配置项：A 类 4 bank 或 8 bank | `fig_abank_cfg()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-ARCH | 2 数据从哪来、到哪去 | `fig_l1_arch()` | `_build/draw_l1_arch.py` | ✓ |
| FIG-L1_SRAM-RING | 3.3 核内与 C2H 地址由 CCU 给出，落地地址由 MAE 搬运引擎逐拍给出，L1 不做取模 | `fig_ring()` | `_build/draw_l1_sram.py` | ✓ |
| FIG-L1_SRAM-COMPACT-A | 3.4a 紧密访存：A 类支持任意字节起点，W / S 类与 MXU 供数除外 | `draw()` | `_build/draw_compact.py` | ✓ |
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
| FIG-L2_SRAM-OBJ-ALIGN | 3.4 对齐使用（默认）：每条记录占整数个存储字 | `fig_obj_align()` | `_build/draw_l2_sram.py` | ✓ |
| FIG-L2_SRAM-MAP-HEAP | 4.2 地址 [h][q][j] 落在哪个 bank、哪个深度 | `fig_map_heap()` | `_build/draw_l2_sram.py` | ✓ |

## L3PU_EXTERNAL_INFORMATION.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-INFO-FOUR-KINDS | L3PU 的外部输入信息：指令、配置表、调用描述符、列表、数据 | `fig_four_kinds()` | `_build/draw_info.py` | ✓ |

## MAE_CRU.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_CRU-ARCH | 2 数据从哪来、到哪去 | `fig_cru()` | `_build/draw_mae_arch.py` | ✓ |
| FIG-MAE_CRU-SUM | 3.1 部分和归约：BF16 逐元素求和，标准加法树，次序按参与方固定 | `fig_sum()` | `_build/draw_mae_cru.py` | ✓ |
| FIG-MAE_CRU-READSET | 3.3 读集合并：按位取并 | `fig_readset()` | `_build/draw_mae_cru.py` | ✓ |
| FIG-MAE_CRU-PINGPONG | 4.3 CRU 内地址由编译链做 ping-pong | `fig_pingpong()` | `_build/draw_mae_cru.py` | ✓ |

## MAE_DSU.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_DSU-ARCH | 2 数据从哪来、到哪去 | `fig_dsu()` | `_build/draw_mae_arch.py` | ✓ |
| FIG-MAE_DSU-SPLICE | 4.1 半字合并：标准布局 → $W^{\mathsf T}$ 列字，地址级完成 | `fig_splice()` | `_build/draw_mae_dsu.py` | ✓ |
| FIG-MAE_DSU-TRANSPOSE | 4.2 转置：列深度优先布局 → $W^{\mathsf T}$ 列字，攒齐一个子段整块转置 | `fig_transpose()` | `_build/draw_mae_dsu.py` | ✓ |
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

## MAE_IDN.md

| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |
|---|---|---|---|---|
| FIG-MAE_IDN-ARCH | 2 数据从哪来、到哪去 | `fig_idn()` | `_build/draw_mae_arch.py` | ✓ |
| FIG-MAE_IDN-LANE-SPLIT | 4.4 分配只在单位边界切换 | `fig_lane_split()` | `_build/draw_mae_idn.py` | ✓ |
| FIG-MAE_IDN-MCAST | 5 多播：交叉的分叉点按已取位分叉，各目的核独立取走 | `fig_mcast()` | `_build/draw_mae_idn.py` | ✓ |

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
