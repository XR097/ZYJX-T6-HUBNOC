# HUB NoC 周期级时序与状态机（V1.5 梳理稿）

> 本文定义可用于 RTL 评审的行为级周期合同。`C0` 表示请求首次被接收的周期；`fire` 表示本周期完成一次有效传输或提交。具体 FIFO 深度、RTT 和流水级数以参数为准。

## 1. 通用周期规则

1. 发送端只有在本地 `valid`、接收方可收且信用大于 0 时才能 `fire`；credit 链路不使用反向数据线承载返还。
2. 接收端弹出一个 flit 后，下一周期在独立返还线上发一个单拍 credit pulse。
3. `last=1` 表示传输单位结束，`nw8` 表示本拍有效 8 B 字数；非末拍 `nw8=4`。
4. 普通链路节点只搬运 `data`，只有段切分器、R-hub 和格式感知落地端点解析 SFD。
5. 所有保持状态的模块在 stall 周期保持队头、游标、sideband 和状态机状态；只有 `fire` 才允许消耗输入或推进地址。

## 2. HUB-DN 时序和 FSM

### 2.1 发送流水和在途表

HUB-DN 不能把整条流串行化为“发送后等待所有返还”。发送流水、信用返还和读完成跟踪并行运行；一个道可以在等待某个末 flit 的目的返还时继续发送其他已授权流。建议的逻辑状态如下：

```text
READ_READY → READ_PIPE → SEGMENT_HOLD → ARBITRATE → TX_FIRE
    ↑             │            │            │          │
    └─────────────┴────────────┴────────────┴──────────┘
                                 │末 flit
                                 ▼
                         INFLIGHT_RETURN_TABLE
                                 │全部目的返还
                                 ▼
                            RCNT_EVENT
```

| 状态/资源 | 动作 | 转移条件 |
|---|---|---|
| `READ_READY` | 为可运行流选择象限和道 | 读请求/描述符有效且在途表有槽 |
| `READ_PIPE` | 向 L2 象限发起读并保持流序 | 读返回进入段切分流水 |
| `SEGMENT_HOLD` | 按 SFD/元素位宽形成段片，锁存 `last/nw8` | 段片可交给仲裁器；不能收时保持 |
| `ARBITRATE` | 控制 VC 严格优先，数据 VC 按保底窗口竞争 | 所有目的信用和共享池限制满足 |
| `TX_FIRE` | 发出一个 flit，扣各目的信用，推进该流游标 | 非末拍回到流水；末拍分配在途项 |
| `INFLIGHT_RETURN_TABLE` | 按读单位和目的掩码记录未返还目的数 | 每个返还脉冲减一；归零产生 `RCNT_EVENT` |
| `ERROR` | 锁存协议/描述符错误并上报 LIC | 复位或集成错误策略清除 |

在途表的槽数、读返回队列和段片缓存深度由参数决定；其目的在于覆盖建议的 22 拍 RTT 和重放落地深度，而不是限制为一个读单位。`RCNT_EVENT` 只释放对应在途项，不阻塞其他流。

### 2.2 正常发送

| 周期 | 行为 |
|---|---|
| C0 | 调度器选择流，读引擎锁存 `(quadrant, stream, cursor)`。 |
| C1… | L2 返回数据；段切分器根据 SFD 计算段长和有效字数。 |
| Cn | VC3 严格优先；重放 VC 的 `wD` 保底窗口调度数据，VC2 与数据 VC 共用保底槽；VC2/VC3 每拍限速按 `SHARED_POOL_RATE_MODE` 取项目裁定。 |
| Cn+1 | 所有目的核信用满足时 `dn_tx_fire=1`，每个目的信用减 1，游标前进。 |
| Cn+2… | 目的落地 FIFO 弹出后分别返还 credit。 |
| Cend | 末 flit 的所有返还到齐，报告 RCNT，读项释放。 |

### 2.3 回压和错误

- 任一多播目的信用不足时，整个 flit 保持，不能只发给部分目的；游标和 `last` 不变。
- 单道信用为 0 时只阻塞该 `(core,vc,lane)`，不能阻塞其他独立道；VC2/VC3 的每核限速存在 HUB_NOC 与协议 PDF 的口径冲突，暂按 `05_open_issues.md` 的冻结结果实现，不在此处硬编码。
- 协议规定的六类链路断言失败时进入 `ERROR`，产生致命协议事件且不重传；`nw8`/目的掩码/SFD 边界等额外检查可作为仿真断言。流量性信用停顿只计数不报错。

## 3. HUB-UP 时序和 FSM

### 3.1 并行路由和单写口提交

四核四 VC 入口队列独立接收；路由、R-hub/ATT/SYNC 消费和 L2 单写口仲裁可以并行。单个队列的抽象状态为：

```text
EMPTY/READY → CLASSIFIED → WAIT_TARGET → TARGET_FIRE → POP/RETURN
                           ↑             │
                           └─────────────┘
```

写口阻塞只能阻塞指向写口的候选队列，不能反压窄口 VC0、控制 VC3 或 R-hub VC2。区域游标只在目标 `fire` 后推进；列表环满属于 ATT 的资源反压，不是普通区域写的全局状态。

### 3.2 路由和写入

| 上行类别 | 目标 | 完成条件 |
|---|---|---|
| VC1 区域写 | L2 单写口 | 最后 32 B 行真正落 bank，由 L2 增加 WCNT |
| VC1 环写 | HUB-ATT → L2 单写口 | 记录落环且 L2 写提交 |
| VC0 位图/判决 | HUB-ATT | 合并项接收；广播由 ATT 管理 |
| VC0 标量 | HUB-SYNC | 进入标量配对表 |
| VC2 部分和 | R-hub FIFO | 入口 FIFO 接收并返还信用 |
| VC3 控制 | 按消息类型分流至 HUB-SYNC、NI/SDN、MAE、LIC 或描述符同步 | 事件校验、份释放或控制状态更新 |

单写口采用有界等待策略；不能因某一 VC 长期占用而使其他合法流永久饥饿。`up_write_cursor` 只在目标 `fire` 后按 `(core,region)` 更新，区域长度到达后按配置回绕。L2 不可提交时只保持对应写口队头；NI 写分叉、PIN 写和 MAE 拷贝不经过该单写口。

## 4. HUB-ATT 时序和 FSM

### 4.1 状态

```text
COLLECT → KEY_READY → OR_MERGE → WRITE_REQ
    ↑                    │           │
    └──── WAIT_RESOURCE ←─┘           ↓
                         BROADCAST → RELEASE
```

- `COLLECT`：按合并键收取参与核输入，记录到齐掩码。
- `KEY_READY`：参与掩码要求的核全部到齐，锁存输入快照。
- `OR_MERGE`：逐位 OR，不读取或解释 logits。
- `WRITE_REQ`：区块并集/列表记录申请 L2 单写口。
- `BROADCAST`：按参与核掩码经 VC3 发判决或区块并集。
- `RELEASE`：写提交和广播完成后释放合并槽；槽满/环满进入 `WAIT_RESOURCE`。

正常周期示例：C0 收到第一份位图，C1…Cm 收齐参与核，Cm+1 完成 OR；写环请求和广播请求从同一并集记录并行产生，各自等待目标资源。两条路径均完成后释放合并槽。区块位图宽度、环记录格式和广播延迟均为参数/未决项。

关键保持规则：输入未收齐时不提前 OR；环满时不能覆盖旧记录；写游标和合并槽只在对应目标 `fire` 后推进。

## 5. HUB-SYNC 时序和 FSM

### 5.1 状态

```text
IDLE → COLLECT_EVENT → VALIDATE → MERGE_OR_COUNT
  │                         │             │
  │                         └─ ERROR      ↓
  └──── TIMEOUT ← BARRIER_TIMER ← EMIT_GO ←───┘
```

### 5.2 标量和 barrier

标量路径在 `COLLECT_EVENT` 按 `(token, round, participant_mask)` 查表；到齐后在 `MERGE_OR_COUNT` 按固定核序完成 FP32 合并，再排入 D-40 VC2 响应。合并槽满时反压输入，不能丢弃或覆盖不同 key。

barrier 路径在 `COLLECT_EVENT` 收取 `(point_id, core_id, committed_count)`。这里的 `committed_count` 只统计该核经 L2 单写口提交的 VC1 flit，不计 ATT 列表、R-hub 部分和或其他区域。`VALIDATE` 检查位点号、参与掩码和已提交计数；所有参与核满足条件后，`EMIT_GO` 通过 D-40 VC3 发 GO。GO 后一个周期下一位点控制生效。`BARRIER_TIMER` 超门限进入 `TIMEOUT`，向 LIC 发错误事件，不能发 GO；调用级 watchdog 仍归 LIC。

## 6. 跨模块周期场景

### 6.1 Prefill：多播 + K 切分

1. LIC 在 GO 前装载 HUB-DN SFD/目的掩码和 R-hub 归约配置。
2. HUB-DN 分段多播激活；每个目的独立扣信用。
3. 四核 VC1 输出经 HUB-UP 写 L2，真实落 bank 后更新 WCNT。
4. 四核 VC2 部分和进入 R-hub；R-hub 回送经 HUB-DN VC2。
5. VC0 标量和 VC3 位点完成事件进入 HUB-SYNC；barrier 收齐后广播 GO。

### 6.2 Verify：ATT 合并

控制表经 VC3 下发，录取/区块位图经上行 VC0 收齐后 OR；区块列表经单写口落 L2。Verify 场景不产生 K 切分判决广播；该广播属于 Prefill 的 K 切分路径。任一列表环满只反压相关环写流。

### 6.3 Decode：单核退化

使用单播目的掩码验证最小路径：单道信用耗尽只停该道；末 flit 的单目的返还到齐后报告 RCNT；其余核不应被误阻塞。

## 7. 必须实现的断言和覆盖

- 信用计数范围、信用为 0 禁止发送、返还脉冲至多一次/弹出。
- 非末拍 `nw8==4`，末拍 `nw8` 合法；`last` 只在传输单位末拍出现。
- 多播要求所有目的信用；RCNT 等待所有目的返还。
- VC2/VC3 共享池限速断言须引用 `05_open_issues.md` 的裁定：HUB_NOC 写作“每个 VC 各 1 flit/拍”，协议权威写作“VC2+VC3 合计 1 flit/拍”。
- 上行区域写游标只在提交后更新，不能跨区域；L2 WCNT/RCNT 不由 HUB 直接递增。
- ATT 收齐前不输出 OR 结果，环满不覆盖，广播目的掩码不扩大。
- SYNC 位点号不匹配、参与核缺失或超时不能发 GO。
- 覆盖 credit 停顿、FIFO 满、单目的/多目的、乱序到达、反压恢复、环满、barrier 缺核和超时恢复。

## 8. 待冻结参数

`RESET_POLICY`、描述符字段编码、各 FIFO 深度、D-40/上行/SDN RTT、SFD 字段位宽与子字节位序、区块位图 OR 粒度、chunk 索引、列表环长度和写口等待上限必须在未决项台账中登记。本文只定义语义和状态转移，不为这些项目选择最终数值。

