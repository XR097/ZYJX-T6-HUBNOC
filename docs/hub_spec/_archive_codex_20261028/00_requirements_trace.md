# 需求追踪矩阵

状态含义：`已定` 表示可作为接口合同；`派生` 表示为 RTL/验证方便的实现分解，不是 PDF 新增架构条款；`建议值` 表示必须参数化；`待审查/待仿真/待标定` 表示不得自行冻结。叶子级归属必须回溯到 HUB-DN/HUB-UP/HUB-ATT/HUB-SYNC 四个 PDF 子单元。

| ID | 来源 | 归属 | 可检查要求 | 接口/时序产物 | 验证点 | 状态 |
|---|---|---|---|---|---|---|
| NOC-TOPO-01 | HUB_NOC §1.1, §3.1 | hub_top | 中央 L2 与 CC0–CC3 采用两级集中式互连，核间无直连 | 拓扑和边界图 | 端口连通性 | 已定 |
| PROTO-DN-01 | Protocol §4.4.1 | HUB-DN | 每道 32 B/拍，12 bit 侧带：目的掩码/VC/类别/last/nw8 | `dn_flit`, `dn_sideband` | 字段宽度断言 | 已定 |
| PROTO-UP-01 | Protocol §4.4.2 | HUB-UP | 每核 32 B/拍，14 bit 侧带：VC/类别/last/nw8/属主/区域 | `up_flit`, `up_sideband` | 字段宽度断言 | 已定 |
| PROTO-CREDIT-01 | Protocol §4.4.4–§4.4.8；HUB_NOC §4.1.5 | common | VC0/1 按核、VC、道计信用；VC2/3 按核共享池。每拍限速存在“VC2/VC3 各 1”与“VC2+VC3 合计 1”的原文冲突 | 信用扣减/返还表、`SHARED_POOL_RATE_MODE` | 下溢、溢出、共享池限速 | 待审查 |
| DN-SEG-01 | HUB_NOC §2, §4.2.1–§4.2.4 | HUB-DN | 按 SFD 和元素位宽切段；同流保持顺序；超口不降档 | 游标/段切分状态机 | 6/8 bit 段边界和末拍 | 派生/待审查 |
| DN-SCHED-01 | HUB_NOC §4.1.2, §4.2.5 | HUB-DN | 控制 VC 严格优先，数据 VC 采用 32 槽加权保底 | 仲裁状态机 | 控制优先且数据不饿死 | 派生 |
| DN-MCAST-01 | HUB_NOC §4.1.3, §4.1.5 | HUB-DN | 多播每个目的端分别扣信用，末 flit 等所有目的返还后报告 RCNT | 多播在飞表 | 目的端乱序返还 | 派生 |
| UP-WRITE-01 | HUB_NOC §4.3.1–§4.3.3 | HUB-UP | VC1 区域数据进入唯一 32 B/拍 L2 单写口，地址由核+区域游标生成 | 写游标和写口仲裁表 | 有界等待、区域回绕 | 派生 |
| UP-ROUTE-01 | HUB_NOC §2, §3.1 | HUB-UP | VC0/VC1 元数据分流 ATT，VC0 标量和 VC3 控制分流 SYNC，VC2 分流 R-hub | 类别路由表 | 每类唯一目的 | 派生 |
| ATT-BM-01 | HUB_NOC §4.4.1, §4.4.10 | HUB-ATT | 录取/区块/lo 读集按规定键收齐后按位 OR | 合并键和到齐位 | 缺核不提前输出 | 派生/待审查 |
| ATT-LIST-01 | HUB_NOC §4.3.5–§4.3.6, §4.4.3 | HUB-ATT | 列表环维护写指针、回绕和满标志，环满反压 | 列表环写接口 | 不覆盖未消费记录 | 派生/待审查 |
| ATT-DEC-01 | HUB_NOC §4.4.5 | HUB-ATT | K 切分判决和区块并集按参与掩码经 VC3 广播 | 广播目的掩码 | 广播顺序和延迟 | 派生/待标定 |
| SYNC-SCALAR-01 | HUB_NOC §4.5.1 | HUB-SYNC | 按 token/轮次/参与掩码配对，按固定核顺序做 FP32 合并 | 配对表和合并器 | 到齐前不输出、到达序无关 | 派生/待标定 |
| SYNC-BARRIER-01 | HUB_NOC §4.5.4–§4.5.6 | HUB-SYNC | 收齐参与核完成事件后发 GO；GO 后 1 拍生效；超时上报 LIC | barrier FSM | 缺核、错位点号、超时 | 派生 |
| RHUB-IN-01 | HUB_RHUB §3.1, §4.1.3 | R-hub | 四路上行 VC2 入口 FIFO；每条 16×BF16=256 bit；不带数据标签 | FIFO/credit 接口 | 单路满只反压该路 | 已定/建议值 |
| RHUB-ALIGN-01 | HUB_RHUB §2.2, §4.2.1 | R-hub | 四核按同一 pid 顺序放行，四路 FIFO 头部位置对齐 | 对齐状态机 | 任意回压下结果不变 | 派生 |
| RHUB-TREE-01 | HUB_RHUB §2.1, §4.1.2 | R-hub | 固定 `RNE(RNE(c0+c1)+RNE(c2+c3))`，无跨拍累加状态 | BF16 tree pipeline | 逐位参考模型一致 | 派生 |
| RHUB-GROUP-01 | HUB_RHUB §4.1.4 | R-hub | 相邻两条 16 元素结果组成一个 32 元素量化组 | 组缓存状态机 | 单条不提前量化 | 派生 |
| RHUB-QNT-01 | HUB_RHUB §4.3.1–§4.3.2 | R-hub | `amax`→E8M0→MXFP6 g32；输出 25 B，额外携带 16 bit 组序号 | 量化/回送接口 | 编码、RNE、限幅、组序号 | 派生/待标定 |
| RHUB-EGR-01 | HUB_RHUB §3.1, §4.3.2–§4.3.3 | rhub_egress | 保持量化结果、组序号和 owner 直到 HUB-DN VC2 成交；R-hub 不选道 | 输出保持/回送接口 | 阻塞稳定、无重复发送 | 派生 |
| COMP-01 | HUB_NOC §3.1, §3.3, §4.2.6, §4.5.2–§4.5.3 | L2/HUB | `WCNT/RCNT` 存储和递增在 L2 侧；HUB 提供门限比较请求、读/写完成事件和放行条件，不直接改计数器 | `wcnt/rcnt_threshold_req`, 完成事件合同 | 门限未满足时不发起对应读回/重放；计数器归属一致 | 派生/待审查 |
| CTRL-DESC-01 | HUB_NOC §3.2, Protocol §3.3 | hub_control | GO 前装载描述符，GO 后统一生效；SFD 不在普通链路节点解析；影子/双份寄存器仅为实现假设 | 描述符记录/生效边界 | GO 后 1 拍生效 | 派生/待审查 |
| PROTO-CHECK-01 | Protocol §4.2.2, §4.4.13；HUB_NOC §4.1.7 | protocol_b_common | 六类协议致命检查按原文实现；`nw8`、空目的掩码和 SFD 边界等增补项仅作仿真断言，流量性停顿不报协议错 | 断言/错误事件 | 致命协议错上报且不重传；增补项单独统计 | 派生/待审查 |
| DN-READ-01 | HUB_NOC §2, §3.1 | dn_l2_read_engine[4] | 每个 L2 象限读引擎按流请求提供顺序数据 | 读请求/返回接口 | 读流顺序和释放 | 派生 |
| DN-CURSOR-01 | HUB_NOC §2, §4.2.3 | dn_stream_cursor_segmenter | 游标仅在发送成交后推进，段片长度按 SFD 计算 | 游标/段状态机 | stall 保持、段边界正确 | 派生/待审查 |
| DN-CREDIT-01 | Protocol §4.4.4–§4.4.7 | dn_credit_tracker | 各信用池独立扣减/返还，零信用禁止发送 | 信用表 | 无下溢/溢出 | 派生 |
| DN-TX-01 | HUB_NOC §4.1.5, §4.2.5；Protocol §5.3 | dn_vc_scheduler/lane_tx | 控制优先、数据保底；VC2/VC3 每核限速按 `SHARED_POOL_RATE_MODE` 处理原始条款冲突 | 仲裁/发送束 | 不饿死且不超最终裁定 | 派生/待审查 |
| UP-FIFO-01 | HUB_NOC §3.1, §4.1.4 | up_ingress_fifo[4][VC] | 每核四 VC 独立入口，满时只反压对应源 | FIFO/返还接口 | 局部反压 | 已定/建议值 |
| UP-CURSOR-01 | HUB_NOC §4.3.1 | up_write_cursor | `(core,region)` 独立基址、长度和回绕；只在目标成交后更新 | 游标记录 | 不串区、不丢序 | 派生 |
| UP-ARB-01 | HUB_NOC §4.3.2 | l2_single_write_arbiter | 四核共享 32 B/拍单写口，必须有界等待 | 仲裁/提交接口 | 无永久饥饿 | 派生 |
| ATT-LEAF-01 | HUB_NOC §4.4.1, §4.4.4, §4.4.10 | accept/block/lo merge | 各合并器使用独立 key、到齐掩码和可配 payload 宽度 | merge item | 收齐前不输出 | 派生/待审查 |
| ATT-RING-01 | HUB_NOC §4.3.5–§4.3.6 | list_ring_writer | 9 类列表环分别维护指针、回绕、满标志 | ring write request | 环满反压、不覆盖 | 派生/待审查 |
| ATT-BCAST-01 | HUB_NOC §4.4.5 | decision_broadcast | 判决/区块并集按参与掩码经 VC3 发送 | 广播 flit | 目的掩码不扩大 | 派生/待标定 |
| SYNC-TABLE-01 | HUB_NOC §4.5.1 | scalar_pair_table | 按 token/round/参与掩码配对标量，不覆盖不同 key | 配对槽 | 槽满反压 | 派生/待标定 |
| SYNC-MERGE-01 | HUB_NOC §4.5.1 | scalar_merge | 固定核序 FP32 合并，结果经 VC2 回送 | 合并输出 | 到齐前不输出 | 派生/待标定 |
| SYNC-BAR-01 | HUB_NOC §4.5.4 | barrier_counter_go | 收齐参与核并校验计数后发送 GO | barrier FSM | GO 后 1 拍生效 | 派生 |
| SYNC-TIMEOUT-01 | HUB_NOC §4.5.6 | barrier_timeout | 超门限只向 LIC 报告 timeout，不自行发 GO | 错误事件 | 缺核/超时覆盖 | 派生 |
