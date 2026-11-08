# 叶子级接口矩阵

本表是接口评审台账。字段名称是合同级 bundle 名称，最终 RTL 端口名可以调整；协议固定字段使用明确位宽，架构未冻结字段标为 `PARAM`，不得自行编码。

## HUB NoC

| 叶子模块 | 输入 bundle | 输出 bundle | 状态/资源 | `fire`、反压和完成 |
|---|---|---|---|---|
| `hub_control` | `lic_desc(PARAM)`、`lic_go`、`mae_event(PARAM)` | `active_desc`、`go_event`、`error_event`、`perf_event` | 描述符上下文、SFD/错误锁存；双份影子寄存器仅为实现假设 | 描述符在 GO 边界交换；错误/事件槽满时反压来源 |
| `protocol_b_common` | `vld`、`data[255:0]`、12/14 bit `sideband`、`credit_return` | 解码字段、`protocol_error`、`fire` | 侧带检查、信用范围检查 | 只有字段合法且目标可收时 `fire`；不解析 payload |
| `dn_l2_read_engine[4]` | `read_req(quadrant,stream,cursor,len)`、L2 `rdata`/`rvalid` | `read_item`、`read_done` | 每象限读队列、在途读项 | L2 接受请求才锁存；读返回按流序提供 |
| `dn_stream_cursor_segmenter` | `read_item`、`active_desc.SFD` | `segment_data`、`segment_meta(last,nw8,vc,dest)` | 流游标、段片残字缓存 | 发送未成交时保持段片和游标；SFD/长度非法报错 |
| `dn_vc_scheduler` | 各 VC 候选、信用可用向量、32 槽窗口计数 | `sched_grant` | VC 优先级、数据保底槽计数 | VC3 严格优先；数据 VC 不得永久饿死 |
| `dn_credit_tracker` | `tx_fire`、每目的 `credit_return` | `credit_avail[core][vc][lane]`、共享池可用量 | VC0/1 分道信用、VC2/3 共享信用 | 发送扣 1、返还加 1；零信用禁止发送 |
| `dn_multicast_tracker` | `dest_mask`、`last`、目的返还脉冲 | `read_unit_complete`/`rcnt_event` | 在途读项、未返还目的数 | 末 flit 需所有目的返还；期间保持读项 |
| `dn_lane_tx[4]` | `sched_grant`、`segment_data`、目的信用 | D-40 `vld/data/sideband`、返还采样 | 每道发送保持寄存器 | 只在 lane `fire` 时弹出/推进；一道停顿不阻塞其他道 |
| `up_ingress_fifo[4][VC]` | 每核上行 `vld/data/sideband`、目标空间 | `fifo_head`、`credit_return[vc]` | 四核四 VC FIFO、读写指针 | 空间足够才接收；弹出后下一拍返还信用 |
| `up_vc_class_router` | `fifo_head`、VC/类别字段 | `l2_req`、`att_req`、`sync_req`、`rhub_req` | 路由判定 | 目标不接受时保持队头；非法 VC/类别报错 |
| `up_credit_return` | 目标模块 `pop`/`fire` | 每核 4 根上行返还脉冲 | 返还延迟寄存器 | 目标实际弹出后下一拍产生单拍脉冲 |
| `up_write_cursor` | `core`、`region`、描述符基址/长度/回绕、目标 `fire` | `l2_addr`、`next_cursor` | 每核每区域写游标 | 仅目标提交后推进；到边界按配置回绕 |
| `l2_single_write_arbiter` | L2/ATT 写请求、`l2_write_ready`、仲裁状态 | 单一 `l2_write`、提交事件 | 有界等待仲裁、当前 owner | 32 B 行真正写入 bank 才提交；提交后允许游标/WCNT推进 |
| `accept/block/lo_readset_merge` | `merge_key(PARAM)`、参与掩码、位图 payload | OR 后 `merge_result`、`ready` | 合并槽、到齐掩码 | 参与核全部到齐才输出；槽满反压对应输入 |
| `list_ring_writer` | 列表记录、环号、记录长度、L2 写口可用 | `l2_write_req`、环满/提交 | 9 类环写指针、长度、满标志 | 环满禁止覆盖；记录落 L2 后释放槽 |
| `decision_broadcast` | 判决/区块并集、参与核掩码 | 下行 VC3 `dest_mask/data/sideband` | 广播保持寄存器 | 下游信用不足时保持；广播完成后释放结果 |
| `scalar_pair_table` | VC0 标量、token/round/参与掩码 | 已配对 scalar item | 按 key 的配对槽、到齐掩码 | 槽可用才接收；key 未齐不输出 |
| `scalar_merge` | 已配对标量、操作类型 | FP32 合并结果、回送请求 | 固定核序合并流水 | 所需值到齐后启动；输出阻塞时保持 |
| `barrier_counter_go` | VC3 完成事件、point_id、参与掩码、提交计数 | VC3 `go_event`、barrier 状态 | 当前位点到齐计数/掩码 | 全部参与核通过校验后发 GO；GO 后 1 拍生效 |
| `barrier_timeout` | barrier 起始时间、门限、到齐状态 | LIC `timeout_event` | 计时器、错误锁存 | 超时只上报，不发 GO；流量性停顿不算协议错误 |
| `sync_response_tx` | 标量结果、GO、错误事件 | D-40 VC2/VC3 注入请求 | 输出保持寄存器 | HUB-DN 接受前保持，成交后清除 |

## R-hub

| 叶子模块 | 输入 bundle | 输出 bundle | 状态/资源 | `fire`、反压和完成 |
|---|---|---|---|---|
| `rhub_ingress_fifo[4]` | 上行 VC2 `vld/data[255:0]/sideband[13:0]` | `head_valid/data`、每路 `rhub_pop` | 每核 FIFO、满/空 | 只在空间足够时接收；满只反压对应核；信用返还由 HUB-UP 根据 pop 发出 |
| `rhub_head_align` | 四路 FIFO head、参与核掩码、`enable` | `align_fire`、四路对齐向量 | 参与掩码、组相位 | 所有参与核 head 有效且下游可接收才同时弹出 |
| `rhub_bf16_tree` | 四路 16×BF16 对齐向量 | 16×BF16 result | 两级加法流水，无跨拍累加 | `align_fire` 后固定执行 `RNE(c0+c1)`、`RNE(c2+c3)`、再相加 |
| `rhub_group_buffer` | 16×BF16 result、owner/组相位上下文 | 第一条缓存、第二条拼组 | 32 B 暂存、组相位、owner 上下文 | 第一条只写缓存；缓存有效时禁止覆盖；R-hub 不保存 token/pid 标签 |
| `rhub_mxfp6_quant` | 32×BF16 group | 200 bit MXFP6 + E8M0、量化状态 | amax/尺度/编码流水 | 第二条结果到齐后启动；结果必须保持到 egress 接收 |
| `rhub_egress` | 200 bit 量化数据、`group_seq[15:0]`、owner | VC2 回送请求、保持状态 | 输出保持寄存器、组序号 | HUB-DN VC2 不可收时保持；成交一次后清除，不重复发送 |

## 所有叶子模块的共同约束

- stall 周期保持队头、payload、sideband、游标和状态；只有 `fire` 才能消费或推进。
- 协议 B 普通节点不携带地址、不解析格式；地址/格式只在规定的格式感知端点处理。
- `WCNT` 由 L2 实际落 bank 产生，`RCNT` 由 HUB-DN 多播返还配对产生；叶子模块不能重复拥有这些计数器。
- 未冻结的 FIFO 深度、SFD 编码、RTT、合并键宽度和流水级数使用 `PARAM`，并在 `05_open_issues.md` 登记。
