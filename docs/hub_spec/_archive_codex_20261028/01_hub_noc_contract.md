# HUB NoC 接口合同（V1.5 梳理稿）

> 状态：第一阶段规格梳理；可用于 RTL 接口评审，不能替代项目最终 ISA/物理宏定义。
> 权威来源：`docs/HUB_NOC.pdf` §1–§7、`docs/SPEC_TRANSFER_PROTOCOL_V1.5.pdf` §2.4–§4.5。
> 所有标记“待审查/待仿真/待标定”的字段必须进入未决项台账，不得在 RTL 中静默固化。

## 1. 边界和拓扑

HUB 是以中央 L2 为中心的两级集中式互连。中心包含四个 L2 象限读引擎、HUB-UP、L2 单写口、HUB-ATT、HUB-SYNC 和 R-hub；第二级是四个 D-40 道发端。CC0–CC3 之间没有点对点链路。

| 边界 | 方向 | 合同 |
|---|---|---|
| D-40 | HUB-DN → CC0..CC3 | 4 道，每道 32 B/拍；每道 12 bit 侧带；不携带地址 |
| 上行 | CC0..CC3 → HUB-UP | 每核 32 B/拍；每拍 32 B 载荷和 14 bit 侧带；不携带地址 |
| L2 单写口 | HUB-UP/HUB-ATT → L2 | 四核共享，32 B/拍；实际落 bank 后由 L2 更新 WCNT |
| R-hub | HUB-UP ↔ R-hub | 上行 VC2 输入 BF16 部分和；结果经 HUB-DN VC2 返回属主核 |
| LIC 控制 | LIC ↔ HUB-SYNC/HUB-DN | hub 位点描述符、SFD、GO、错误/合并结果 |
| MAE 事件 | MAE ↔ HUB | 读/写完成门限、资源和性能事件；计数器存放在 L2 侧 |

训练权重由 NI/SDN 直达训练核，不进入 HUB-DN。HUB 不发 DDR 请求，不做 TOPK、阈值判定、采样或普通 payload 的量化/解包。

## 2. 逻辑模块树和所有权

原始 HUB_NOC §0 只规定 HUB-DN、HUB-UP、HUB-ATT、HUB-SYNC 四个子单元，并明确 hub 内部不再细拆。下面的叶子名是本梳理包为 RTL/验证建立的**派生实现分解**，不是新的架构条款；叶子之间的边界在接口矩阵中用于评审，最终 RTL 可以合并或重命名，但不能改变四个子单元的职责归属。

```text
hub_top
├── hub_control             # LIC descriptor/SFD、GO、错误和性能事件
├── hub_dn
│   ├── dn_l2_read_engine[4]
│   ├── dn_stream_cursor_segmenter
│   ├── dn_vc_scheduler
│   ├── dn_credit_tracker
│   ├── dn_multicast_tracker
│   └── dn_lane_tx[4]
├── hub_up
│   ├── up_ingress_fifo[4][VC0..VC3]
│   ├── up_vc_class_router
│   ├── up_credit_return
│   ├── up_write_cursor
│   └── l2_single_write_arbiter
├── hub_att
│   ├── accept_bitmap_merge
│   ├── block_bitmap_merge
│   ├── lo_readset_merge
│   ├── list_ring_writer
│   └── decision_broadcast
├── hub_sync
│   ├── scalar_pair_table
│   ├── scalar_merge
│   ├── barrier_counter_go
│   ├── barrier_timeout
│   └── sync_response_tx
└── protocol_b_common      # sideband、nw8/last检查、credit和完成断言
```

HUB-DN 拥有下行发送序、段片切分、目的掩码和读完成跟踪；HUB-UP 拥有上行入口队列、VC/类别分流和区域写游标；HUB-ATT 拥有位图合并及列表环写请求；HUB-SYNC 拥有标量配对、barrier 与超时。L2 拥有 bank 仲裁以及 WCNT/RCNT 存储和比较，LIC 拥有调用级 watchdog。

## 3. 协议 B 信号和字段

### 3.1 D-40 下行

每道一个 `valid/data/sideband` 发送束。`data[255:0]` 为不透明 32 B 载荷；`sideband[11:0]` 语义为：

```text
dest_mask[3:0] | vc[1:0] | class[2:0] | last | nw8[1:0]
```

`dest_mask=0001/0010/0100/1000` 表示单播，`1111` 表示四核多播。`nw8` 表示本拍前 1–4 个 8 B 字有效，非末拍必须为 4。D-40 不带地址，接收端按本地描述符和游标生成落地地址。

下行 VC：VC0 重放/灌入，VC1 数据，VC2 R-hub/标量响应，VC3 控制。VC3 源端严格优先；VC1 必须受 32 槽加权窗口保护。

### 3.2 上行

每核一个 `valid/data/sideband` 发送束。`data[255:0]` 为 32 B 载荷；`sideband[13:0]` 语义为：

```text
vc[1:0] | class[2:0] | last | nw8[1:0] |
reduction_owner[1:0] | region[3:0]
```

上行 VC：VC0 位图/判决/标量，VC1 区域写和列表环写，VC2 K 切分部分和，VC3 控制事件。上行不带地址；`up_write_cursor` 按 `(core, region)` 的基址、长度和回绕规则生成写位置。`region` 在列表类载荷中解释为环号。

### 3.3 信用和完成

- 下行 VC0/VC1 信用按 `(core, vc, lane)` 独立计数；VC2/VC3 按 `(core, vc)` 共享池计数。HUB_NOC §4.1.5 写作同一核的 VC2、VC3 每拍各至多 1 flit，而协议总规范的汇总条款写作共享池合计每拍至多 1 flit；在项目裁定关闭前由 `SHARED_POOL_RATE_MODE` 参数承载，不能静默选择其一。
- 上行每核四个 VC 有独立源队列，信用按 `(core, vc)` 计，不按 D-40 的道计；返还线每核 4 根，每 VC 一根。D-40 的返还线为每核 10 根：VC0/VC1 各 4 道，VC2/VC3 各 1 根。
- 初始信用等于接收 FIFO 深度。发送成交时减 1，接收端弹出后下一拍返还一个单拍脉冲并加 1。信用不能下溢或超过配置深度。
- 多播发送前必须确认所有目的核都有信用，并分别扣减。一个读单位只有在末 flit 发出且所有目的核的返还均到达后才报告 RCNT 完成。
- WCNT 只在 L2 写仲裁确认最后一个 32 B 行真正落入 bank 后递增。HUB 不持有 WCNT/RCNT。

### 3.4 时钟、复位和内部记录

所有 HUB 状态机按集成提供的同步时钟运行；V1.5 尚未冻结时钟域数量、复位极性和同步/异步形式，因此接口合同使用抽象的 `clk/reset` 语义，不预先规定端口命名。复位或重新初始化时：所有入口 FIFO 为空、发送 `valid` 清零、信用恢复为配置初值、游标/合并槽/barrier 状态清零、错误和性能事件清零；在 GO 生效前不得发送数据。复位策略由 `RESET_POLICY` 参数和系统集成确认。

HUB 内部格式感知端点使用以下逻辑记录，字段位宽除协议固定字段外由描述符或未决项参数定义：

| 记录 | 必备字段 | 生产者 → 消费者 | 成交/提交条件 |
|---|---|---|---|
| hub descriptor | enable、参与核掩码、目的掩码、VC/类别、SFD、区域基址/长度/回绕、barrier 门限、R-hub 映射 | LIC → hub_control/各子模块 | GO 后锁存生效 |
| L2 read request | 象限、流号、游标、字节/段长度、SFD 上下文 | `dn_l2_read_engine` → `dn_stream_cursor_segmenter` | L2 读口接受 |
| L2 write request | 32 B data、last、nw8、来源核、region、传输单位标志 | HUB-UP/ATT → L2 单写口 | L2 bank 真正写入 |
| ATT merge item | 合并键、参与掩码、到齐掩码、位图 payload | HUB-UP → ATT merge | 所需参与核全部到齐 |
| SYNC scalar/event | token、round/point、参与掩码、操作类型、FP32 值或完成计数 | HUB-UP → HUB-SYNC | key 合法且配对槽可用 |
| barrier/GO | point_id、参与掩码、完成计数、超时门限 | CC/LIC ↔ HUB-SYNC | 收齐并校验后发 GO |

## 4. 子模块合同

### 4.1 HUB-DN

输入为四个 L2 象限读结果，以及 R-hub、HUB-ATT、HUB-SYNC、LIC、MAE 事件/门限和表装载请求的下行注入请求；输出为四道 D-40 flit 和信用返还状态。`dn_stream_cursor_segmenter` 依据 hub 位点描述符中的 SFD/元素位宽切分紧凑记录，`dn_vc_scheduler` 依据 VC3 严格优先、`wD` 数据保底和挂 hub 单元当拍最短队列选择调度，`dn_multicast_tracker` 维护每个在途读单位的未返还目的数。

游标只在发送成交时前进；信用不足、目的端部分不足或目的 FIFO 未弹出时必须保持 flit 和游标。`wD=8` 时允许短时超口（约 120→143 B/拍），链路按信用自然停顿且不自动降档；超口计数由核侧产生、HUB 按位点汇总。`wD`（0..8，描述符 4 bit）是相对重放 VC 的保底窗口，VC2 与数据 VC 共用该窗口。

### 4.2 HUB-UP

输入为四核上行 flit 和信用返还；输出到 L2 单写口、R-hub、HUB-ATT 和 HUB-SYNC。按 `(vc,class)` 分流：VC1 区域写进入单写口，VC1 环写和 VC0 位图/判决进入 HUB-ATT，VC0 标量和 VC3 控制进入 HUB-SYNC，VC2 部分和进入 R-hub。

单写口采用有界等待仲裁，不允许固定优先级造成永久饥饿。写游标只在写口成交后更新；队列满、环满或 L2 不可提交时保持队头和游标。写口拥塞不得反压窄口 VC0、控制 VC3 或 R-hub VC2；实际写完成由 L2 产生 WCNT。NI 写分叉、PIN 写和 MAE 拷贝不经过该单写口。

### 4.3 HUB-ATT

HUB-ATT 只处理跨核元数据，不承载逐列评分、粗 logits 或完整 logits。录取位图按 `(layer, kv_head, 64-key tile)` 收齐后按位 OR；区块位图按 `(layer, kv_head, query wave)` 收齐后 OR，并从同一并集记录并行产生区块列表环写请求和参与核广播；训练多核场景的 lo 读集按 `(point, column block)` OR。共有 9 类列表环，分别维护写指针、长度、回绕和满标志。K 切分判决由归约属主核产生，HUB-ATT 只经 VC3 转发，不 OR、不进 L2。

收齐条件由参与核掩码和合并键共同决定；输入不齐时保留合并项，环满时对写者反压。列表数据必须经 L2 单写口，环满不能覆盖尚未被 MAE 消费的记录。

### 4.4 HUB-SYNC

HUB-SYNC 收取 VC0 标量和 VC3 控制事件。标量按 `(token, round, participant_mask)` 配对，使用固定核序进行 FP32 合并；barrier 按 `point_id` 和参与掩码收齐位点完成事件后发出 VC3 GO，GO 后 1 拍使下一位点控制生效。超过描述符门限时只向 LIC 上报 barrier 超时；调用级 watchdog 仍由 LIC 负责。

位点号、参与掩码或事件计数不匹配时生成协议/同步错误事件，不提前发 GO。`committed_count` 只统计每核本位点经单写口提交的 VC1 flit，不计 ATT 列表写入或 R-hub 部分和。标量结果经 D-40 VC2 回送，具体运算类型由位点描述符给出。

## 5. 配置、复位和参数化

每个位点开始前由 LIC 下发 hub 位点描述符，至少包含目的掩码、VC/类别、SFD、参与核掩码、区域基址/长度/回绕、barrier 门限和 R-hub 归约配置；GO 作为统一生效边界。

HUB-DN 还接收部分和读回、阈值套、节点档表、祖先掩码、父槽表、Batch 行表、Draft 分布和核描述符等装载/控制流；这些流的 VC/类别、SFD 和目的核来自描述符或 MAE 模板。MAE 的计数事件和门限比较通过中心内部接口进入 HUB-DN；发流前必须满足相应 L2 `WCNT/RCNT` 门限。

训练核份释放事件由上行 VC3 直达 NI/SDN，不经 HUB-SYNC、LIC barrier 或区域计数；WB 槽释放直达 MAE，系数就绪事件按控制消息转给 LIC。HUB-DN 的挂 hub 注入源（R-hub、HUB-ATT、HUB-SYNC、LIC、MAE）按当拍排队最短的道进入发送仲裁。

外部模块合同摘要：L1 集成负责落地 FIFO、强制水位、段片解析、类别分路、返还脉冲和 LAND 在飞表；MAE_NI_INT 负责 SDN 训练权重和两层信用；VNU_EPI/SEL/SMP 负责出口格式、位图/判决产生和采样状态；CCU_CTL 负责位点完成、owner 侧带和份释放事件；CCU_GRP 负责分组/lo 读集产生；MAE_ENG 负责列表读取和计数事件；CIF 负责计数窗汇总；数据流篇负责各调用的负载、份额和执行顺序。

复位极性、同步方式、描述符寄存器编码和错误恢复策略未在 V1.5 冻结，统一保留为集成参数 `RESET_POLICY`、`DESC_ENCODING` 和 `ERROR_POLICY`，在 RTL 启动前由系统集成确认。FIFO 深度、RTT、区块位图宽度、chunk 索引和列表环长度同样不得写死。

协议给出的流控数字仅作为参数默认值，需由阶段二仿真复核：往返预算 `trt=22` 拍（前飞 10、弹出 1、返还 10、下一拍可用）；下行重放每道 22 flit（每核参考 88 flit），数据每道 6 flit（每核参考 24 flit），VC2 每核至少 8 flit，VC3 每核至少 2 flit（建议 4）；上行入口 VC0/VC1/VC3 参考深度分别为 4/12/2，VC2 使用 R-hub 入口 FIFO。R-hub FIFO 的 16 条仅作参考默认值，仍由 `FIFO_DEPTH` 参数承载。

## 6. 必须保留的断言

1. `credit==0` 时禁止发送，信用不下溢/溢出。
2. 非末拍 `nw8==4`；末拍 `nw8∈{1,2,3,4}`。
3. 多播发送必须满足所有目的信用，末拍完成必须等待所有目的返还。
4. VC2/VC3 共享池限速由 `SHARED_POOL_RATE_MODE` 选择；在 VC2/VC3 各自限 1 与合计限 1 的原始条款冲突关闭前，禁止将任一口径写死。
5. 同一 `(source,dest,stream)` 内顺序不变；游标只在成交时更新。
6. 环满时禁止覆盖未消费记录；写游标不能跨区域串写。
7. barrier 未收齐、位点号不匹配或超时均不得发 GO。
8. `WCNT/RCNT` 只能由 L2 的实际落 bank/多播返还事件更新。

