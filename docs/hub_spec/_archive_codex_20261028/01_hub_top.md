# 01 hub 顶层：组成、外部端口、内部接口、位点描述符

版本：初版 v0.1（2026-10-28）。字段与参数定义见 `00_common_conventions.md`（下称 00）。

## 1. hub 在片上的位置与职责

hub 是以中央 L2 为中心的两级集中式互连的中心节点：D-40 是全部下行，上行复用核 → 中心链路；R-hub 与 HUB-ATT 挂在 hub 中心，LIC 是 hub 的控制客户；核间没有直连，NoC 之外不另拉链路（HUB_NOC p7 §4.1.1）。跨核功能（多播重放、位图 OR、标量合并、barrier、K 切分归约）都在中心一处完成，代价是单写口和 D-40 口宽成为全局约束，由编译期的阈值套与分区表保证不超（HUB_NOC p3 §2）。

hub 不做的事（HUB_NOC p1 §1.3、p10 §4.2.7；HUB_RHUB p2 §1.3）：不分发训练权重（改由 NI 经 SDN 直送）；不设集中判决与集中采样单元；不持写完成 / 读完成计数器（在 L2 侧）；不持调用级计数窗与看门狗（在 LIC）；R-hub 不做 L2 读改写、不做匹配。

## 2. 组成与实例树

```
hub_top
├── hub_dn            下行：4 道读引擎、段片切分、仲裁、信用、多播跟踪、4 道发端      → 02
├── hub_up            上行：4 核 × 4 VC 入口、分流、写游标、单写口                    → 03
├── hub_att           位图 OR、列表环写指针、判决与区块并集广播                        → 04
├── hub_sync          标量合并、barrier / GO、超时；含 hub_sync_ctrl（LIC 控制口）   → 05
└── rhub              K 切分部分和固定序归约与出口量化                                → 06
```

PDF 把"经 hub 控制口与 LIC 交换 hub 位点描述符与 GO"划给 HUB-SYNC（HUB_NOC p3 §2）。本 spec 据此把描述符寄存器组 `hub_sync_ctrl` 放在 `hub_sync` 之下，不另立顶层控制单元。描述符的字段表放在本文件 §5，因为五个子单元都要读它。

R-hub 在 PDF 里是独立模块篇（HUB_RHUB），它的全部数据接口都只连 HUB-UP 和 HUB-DN。本 spec 把它实例化在 `hub_top` 里，便于集成；模块边界与归属不变，spec 见 06。

## 3. 外部端口

方向以 `hub_top` 为准。`c` 为核号 0–3，`l` 为道号 0–3，`q` 为 L2 象限号 0–3。

### 3.1 时钟复位

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `clk` | 1 | in | hub 中心时钟 |
| `rst_n` | 1 | in | 同步复位，低有效 |

### 3.2 D-40 下行（hub → 核，4 道，每道广播到 4 核）

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `dn_vld[l]` | 1 | out | 本道本拍 flit 有效 |
| `dn_sb[l]` | 12 | out | `dn_sb_t`，含 `dest_mask`（00 §4.1） |
| `dn_data[l]` | 256 | out | 载荷 |
| `dn_crd_vc0[c]` | 4 | in | 核 c 的 VC0 每道返还脉冲 |
| `dn_crd_vc1[c]` | 4 | in | 核 c 的 VC1 每道返还脉冲 |
| `dn_crd_vc2[c]` | 1 | in | 核 c 的 VC2 共享池返还脉冲 |
| `dn_crd_vc3[c]` | 1 | in | 核 c 的 VC3 共享池返还脉冲 |

道 l 的数据由 4 核共同接收，核 c 以 `dn_vld[l] && dn_sb[l].dest_mask[c]` 判断是否收本拍（00 §3.1）。所有输出寄存器打出，返还输入先打一拍再用（00 §3.4）。

### 3.3 上行（核 → hub，每核一条）

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `up_vld[c]` | 1 | in | 核 c 本拍 flit 有效 |
| `up_sb[c]` | 14 | in | `up_sb_t`（00 §4.2） |
| `up_data[c]` | 256 | in | 载荷 |
| `up_crd[c]` | 4 | out | hub 给核 c 的每 VC 返还脉冲；`up_crd[c][2]` 由 R-hub 入口 FIFO 弹出产生 |

### 3.4 L2 象限读口（HUB-DN，每象限一个）

L2 SRAM 篇不在本仓库，下面的口形是本 spec 为写出 HUB-DN 而拟的通用形式，以 L2 SRAM 篇为准【拟定】。数据组织篇给出的事实是：每象限 8 bank × 32 B × 2048 深，象限 q 硬连道 q（数据组织篇 p2、p11）。

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `l2_rd_req_vld[q]` | 1 | out | 读请求 |
| `l2_rd_req_row[q]` | 14 | out | 象限内 32 B 行地址（8 bank × 2048 深 = 16,384 行）；全局行地址与象限内行地址的映射（含 bank 着色）以 L2 SRAM 篇为准，hub 内用 16 bit 全局行地址、由 `l2_quad_of(row)` 取象限【拟定】 |
| `l2_rd_req_rdy[q]` | 1 | in | L2 接受（bank 冲突时可拉低） |
| `l2_rd_rsp_vld[q]` | 1 | in | 读数据返回，按请求序，固定时延 `L2_RD_LAT`【参数】 |
| `l2_rd_rsp_data[q]` | 256 | in | 一行 32 B |

### 3.5 L2 单写口（HUB-UP）

hub → L2 只有 1 个写口，四核合计 32 B/拍（HUB_NOC p11 §4.3.1）。

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `l2_wr_vld` | 1 | out | 写一行 |
| `l2_wr_row` | 16 | out | 32 B 行地址 |
| `l2_wr_data` | 256 | out | 整行数据；末拍不足 4 字时其余字补 0（00 §3.1） |
| `l2_wr_unit_last` | 1 | out | 本行是该写单位的最后一行，L2 写仲裁据此在落 bank 时给对应区域 WCNT 加 1（HUB_NOC p14 §4.5.2）【拟定：PDF 只规定"最后一个 32 B 行落 bank 即计 1"，没规定 hub 如何告知 L2 哪行是最后一行】 |
| `l2_wr_rdy` | 1 | in | L2 写仲裁接受（与 NI-L2C、NI-FORK、PIN 共用 bank 时可拉低） |

### 3.6 L2 侧计数接口

#### 读完成上报（HUB-DN → L2 RCNT）

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `rcnt_inc_vld` | 1 | out | 一个读单位完成（末标记 flit 全部目的返还） |
| `rcnt_inc_region` | `L2_REGION_W`【参数】 | out | 该单位所属 L2 区域号（L2 区域表索引） |

#### 门限比较口（HUB-DN、HUB-ATT 用）

计数器的存放与比较在 L2 侧；MAE、HUB-DN、LIC 经 hub 中心内部的门限比较接口读它（HUB_NOC p5 §3.1；协议篇 p22 §4.5.2）。hub_top 引出 `N_THR_SLOT` = 4 + `N_RING` = 13 个比较槽【拟定】：

- 槽 0–3 给 HUB-DN：重放 / 灌入、PS 读回、表装载、Draft 分布各 1。
- 槽 4–12 给 HUB-ATT：列表环 k 用槽 4 + k，比较该环区域的 RCNT，用来判断环满（04 §6）。

PDF 列出的门限读者只有 MAE、HUB-DN 和 LIC，没有 HUB-ATT。但 PDF 又要求 HUB-ATT 维护各环"满标志"、写者"覆写某单位前等该单位读完成"（HUB_NOC p12 §4.3.6）。读进度只在 L2 侧 RCNT 里，HUB-ATT 不读它就判断不了环满。所以本 spec 给 HUB-ATT 也接了比较槽【拟定，需 HUB_NOC 作者确认 HUB-ATT 是门限读者；环的读完成由谁计入 RCNT（MAE 读环走哪条读路）以 L2 SRAM 篇为准】。

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `thr_vld[k]` | 1 | out | 槽 k 有效 |
| `thr_kind[k]` | 1 | out | 0 = WCNT，1 = RCNT |
| `thr_region[k]` | `L2_REGION_W` | out | 区域号 |
| `thr_nth[k]` | 32 | out | 门限 |
| `thr_ge[k]` | 1 | in | 计数 ≥ 门限，电平信号，时延 ≤ 2 拍【拟定】 |

### 3.7 LIC 控制口

hub 对 LIC 只有这一个控制口。PDF 另提到"hub 配置口"，本 spec 按它就是 LIC 控制口处理【建议值·OI-25】。口形为寄存器写 + 事件出，字段级格式待 OI-24。

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `lic_sd_wr_vld` | 1 | in | 写 hub 位点描述符的待生效份 |
| `lic_sd_wr_addr` | 10 | in | 描述符字地址（32 bit 字） |
| `lic_sd_wr_data` | 32 | in | |
| `lic_sd_wr_rdy` | 1 | out | |
| `lic_sd_commit` | 1 | in | 待生效份写完（单拍脉冲）；之后的 GO 把它切为当前份 |
| `lic_cmd_vld` / `lic_cmd_rdy` | 1 / 1 | in / out | HUB-DN 命令：表装载、调用输入分发、阈值套装载 |
| `lic_cmd_data` | 128 | in | 命令内容（类型、源区域、行地址、长度、目的掩码、VC/类别），见 02 §4.6 |
| `lic_vc3_vld` / `lic_vc3_rdy` | 1 / 1 | in / out | LIC 经 VC3 单播核描述符 |
| `lic_vc3_dest` | 4 | in | 目的掩码（单播时只有 1 位） |
| `lic_vc3_data` | 256 | in | |
| `lic_vc3_last` / `lic_vc3_nw8` | 1 / 2 | in | |
| `lic_go_vld` | 1 | out | 本拍发出 GO |
| `lic_go_point_id` | 16 | out | |
| `lic_evt_vld` / `lic_evt_rdy` | 1 / 1 | out / in | 上行 VC3 中去 LIC 的消息（属主核完成、系数就绪） |
| `lic_evt_core` | 2 | out | 来源核 |
| `lic_evt_data` | 256 | out | 原样 flit |
| `lic_evt_last` | 1 | out | |
| `lic_err_vld` | 1 | out | 错误事件（00 §8.1），含 barrier 超时 |
| `lic_err_code` / `lic_err_core` / `lic_err_vc` / `lic_err_lane` / `lic_err_info` | 4 / 2 / 2 / 2 / 16 | out | |
| `lic_perf_rd_addr` | 8 | in | 读已锁存的上一位点计数器 |
| `lic_perf_rd_data` | 32 | out | 1 拍后有效 |
| `lic_perf_latched` | 1 | out | GO 时锁存完成（单拍脉冲） |

### 3.8 MAE 事件口

MAE → HUB-DN → VC3 → CCU（模板完成计数达门限、gather 计数等）；WB 槽释放事件经 hub 直达 MAE，不经 LIC（HUB_NOC p5 §3.1）。

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `mae_evt_in_vld` / `mae_evt_in_rdy` | 1 / 1 | in / out | MAE 注入单 flit VC3 消息 |
| `mae_evt_in_dest` | 4 | in | 目的掩码 |
| `mae_evt_in_data` | 256 | in | 首字节为类型 |
| `mae_evt_out_vld` / `mae_evt_out_rdy` | 1 / 1 | out / in | 上行 VC3 中的 WB 槽释放消息，转给 MAE |
| `mae_evt_out_core` | 2 | out | 来源核 |
| `mae_evt_out_data` | 256 | out | |

### 3.9 NI SDN 事件口

训练核的份释放事件（1 flit）经上行控制 VC 进 hub，由 hub 直达 MAE 内 NI 的 SDN，作该核的资源信用；不经 LIC，不计入 barrier 与区域计数（HUB_NOC p15 §4.5.7）。

| 信号 | 位宽 | 方向 | 说明 |
|---|---|---|---|
| `sdn_evt_vld` / `sdn_evt_rdy` | 1 / 1 | out / in | 份释放消息 |
| `sdn_evt_core` | 2 | out | 来源训练核 |
| `sdn_evt_data` | 256 | out | |

`mae_evt_out_rdy` 或 `sdn_evt_rdy` 拉低时，只停住 HUB-UP 的 VC3 出口，VC3 入口 FIFO 满后经上行 VC3 信用反压到核；它们不影响其他 VC（00 §3.3、03 §5）。

## 4. 子单元间接口

所有内部接口用 `vld/rdy` 握手（00 §3.3）。命名约定 `<源>2<目的>_<名>`。

### 4.1 hub 内"下行注入"接口（→ HUB-DN）

挂 hub 中心的单元（R-hub、HUB-ATT、HUB-SYNC、LIC、MAE）发 VC2 / VC3 时不绑定道，由 HUB-DN 选当拍排队最短的道（HUB_NOC p7 §4.1.5）。本 spec 把这类请求统一成一种接口 `inj_*`，每个源一组：

| 字段 | 位宽 | 说明 |
|---|---|---|
| `inj_vld` / `inj_rdy` | 1 / 1 | 握手；`rdy` 表示 HUB-DN 已收入该源的注入队列 |
| `inj_vc` | 2 | 只能是 2 或 3 |
| `inj_cls` | 3 | |
| `inj_dest` | 4 | 目的掩码 |
| `inj_data` | 256 | |
| `inj_last` | 1 | |
| `inj_nw8` | 2 | |

| 源 | 实例名 | 允许的（VC, 类别） |
|---|---|---|
| R-hub | `rhub2dn_inj` | (2, 0) 单播 |
| HUB-SYNC | `sync2dn_inj` | (2, 1) 标量；(3, 0) GO |
| HUB-ATT | `att2dn_inj` | (3, 0) 判决广播、区块并集广播 |
| HUB-UP | `up2dn_inj` | (3, 0) 档表同步转发 |
| LIC | `lic_vc3_*`（顶层口直连） | (3, 0) 核描述符 |
| MAE | `mae_evt_in_*`（顶层口直连） | (3, 0) MAE 事件 |

多 flit 单位（如区块并集广播）在一个源内连续发；HUB-DN 保证同一源的一个单位走同一道、不被同 VC 同核的其他单位插入【拟定】。理由：核侧 VC3 只有一个单写入 FIFO，单位交错会让核侧无法按 `last` 定界。

### 4.2 HUB-UP 分流出口（HUB-UP →）

| 实例名 | 目的 | 内容 | 位宽要点 |
|---|---|---|---|
| `up2att_bmp` | HUB-ATT | 上行 VC0 类别 0–3 的单位 | `core` 2、`cls` 3、`data` 256、`last` 1、`nw8` 2 |
| `up2att_ring` | HUB-ATT | 上行 VC1 类别 1（环写）的单位 | `core` 2、`ring` 4、`data` 256、`last`、`nw8` |
| `up2sync_scalar` | HUB-SYNC | 上行 VC0 类别 4 | `core`、`data`、`last`、`nw8` |
| `up2sync_msg` | HUB-SYNC | 上行 VC3 位点完成 | `core`、`point_id` 16、`nflit` 16 |
| `up2rhub_psum[c]` | R-hub | 上行 VC2 每核一路，直接写 R-hub 入口 FIFO | `data` 256、`owner` 2、`last`、`nw8` |
| `rhub2up_pop[c]` | HUB-UP | R-hub 入口 FIFO 弹出脉冲，HUB-UP 据此打 `up_crd[c][2]` | 1 |

### 4.3 单写口请求（→ HUB-UP 单写口仲裁）

| 实例名 | 源 | 说明 |
|---|---|---|
| `cur2wr[c]` | HUB-UP 游标（每核一路） | 区域写，地址由（核, 区域）游标生成 |
| `att2wr` | HUB-ATT | 列表环写，地址由环写指针生成 |

字段：`vld/rdy`、`row` 16、`data` 256、`unit_last` 1、`src_core` 2、`is_ring` 1。单写口每拍放行一个请求（03 §6）。`wr2sync_commit[c]`：核 c 的区域写在 `l2_wr_vld && l2_wr_rdy` 时的 flit 提交脉冲，供 HUB-SYNC 比较 nflit（05 §4）。

### 4.4 描述符与 GO 分发

| 信号 | 源 → 目的 | 说明 |
|---|---|---|
| `sd_cur` | `hub_sync_ctrl` → 全部子单元 | 当前份描述符（结构体，按子单元拆字段组，见 §5） |
| `go_pulse` | `hub_sync` → 全部子单元 | GO 发出的当拍为 1 |
| `sd_swap` | `hub_sync_ctrl` → 全部子单元 | `go_pulse` 的下一拍为 1；本拍起 `sd_cur` 为新位点内容（"位点控制命令在 GO 后 1 拍生效"，HUB_NOC p14 §4.5.4） |
| `point_id_cur` | `hub_sync_ctrl` → 全部子单元 | 当前位点号，供断言与计数锁存 |

### 4.5 错误与计数汇总

每个子单元引出 `err_*`（00 §8.1 格式）和 `perf_*` 计数器向量，`hub_sync_ctrl` 汇总后送 LIC 控制口。计数器在 `sd_swap` 拍锁存到"上一位点"影子组并清零。

## 5. hub 位点描述符字段表（暂定）

### 5.1 背景

hub 位点描述符（SD）由 LIC 按（阶段, 层, 位点）下发，在 hub 内直达，随 GO 生效（HUB_NOC p6 §3.2）。PDF 只列了内容："目的掩码与 D-40 发送表、部分和读回表、wD（4 bit）、R-hub 归约配置（使能、参与核、归约属主核）、位图 OR 与列表环配置（参与核掩码、kv 头 → 核映射、OR 粒度、Batch 段号）、判决广播映射、barrier 模式、HUB-UP 各（核, 区域）的写游标基址 / 长度 / 回绕，以及本位点各条下行流的 SFD"。字段位宽、排布、条目上限和装载方式都没有（OI-24）。

没有这张表，各子单元的配置寄存器写不出来。下面这张表是本 spec 拟的，原则是：PDF 列出的每一项都有对应字段；PDF 给了位宽的照用；条目上限取能覆盖 PDF 已知场景的最小值。整张表【拟定·OI-24】，HUB_NOC 或 LIC 作者给出正式表后整体替换，子单元逻辑只依赖字段名。

### 5.2 生效方式

`hub_sync_ctrl` 持两份 SD：当前份与待生效份。LIC 在当前位点运行期间写待生效份，写完发 `lic_sd_commit`；HUB-SYNC 发出本位点 GO 的下一拍，待生效份整体切为当前份。commit 未到而 GO 已到时，沿用当前份并计"描述符未就绪"计数【拟定】。

双份寄存使 SD 的存储翻倍（约 2 × 0.76 KB，见 §5.3 末尾的合计），这部分不在 HUB_NOC p16 §5.2 的约 10 KB RF 总账里，需在 OI-11a 的 RF 总账中补记。

### 5.3 字段

地址按 32 bit 字编址，块内字段低位在前。

| 块 | 字段 | 位宽 × 条数 | 使用者 | PDF 依据 |
|---|---|---|---|---|
| 公共 | `point_id` | 16 | 全部 | HUB_NOC p14 §4.5.4 |
| 公共 | `barrier_mode` | 2：0 无栅栏、1 位点 barrier、2–3 保留 | HUB-SYNC | HUB_NOC p6 §3.2、p11 §4.2.10 |
| 公共 | `barrier_part_mask` | 4 | HUB-SYNC | HUB_NOC p14 §4.5.4"参与核计满" |
| 公共 | `barrier_timeout` | 16（拍） | HUB-SYNC | HUB_NOC p15 §4.5.6（门限值由 LIC 定） |
| 公共 | `tbl_wait_mask` | 4：本位点放行前须等到齐的装载完成计数（阈值套、档表、档表同步、Batch 行表） | HUB-DN、HUB-SYNC | HUB_NOC p10 §4.2.8、p11 §4.2.9 |
| 公共 | `tier_sync_mask` | 4：档表同步的多播目的（attention 帮手核） | HUB-UP | HUB_NOC p11 §4.2.9 |
| HUB-DN | `wd` | 4（0–8） | HUB-DN 仲裁 | HUB_NOC p9 §4.2.5 |
| HUB-DN | `dn_stream[i]` | 128 × 8 条 | HUB-DN 读引擎 | "目的掩码与 D-40 发送表" |
| HUB-DN | `dn_sfd[i]` | 39 × 8 条（与 `dn_stream[i]` 一一对应） | HUB-DN 段片切分 | "本位点各条下行流的 SFD"；协议篇 p11 §4.1.2 |
| HUB-DN | `ps_rb[i]` | 64 × 8 条 | HUB-DN PS 读回 | "部分和读回表" |
| HUB-UP | `up_cur[c][r]` | 48 × 4 核 × 16 区域 | HUB-UP 游标 | 协议篇 p19 §4.4.3 |
| HUB-ATT | `att_cfg` | 64 | HUB-ATT | "位图 OR 与列表环配置" |
| HUB-ATT | `att_kv2core[h]` | 4 × 16 kv 头 | HUB-ATT | "kv 头 → 核映射" |
| HUB-ATT | `att_seg_mask[s]` | 4 × 64 段 | HUB-ATT | "Batch 段号"；【建议值·OI-06】 |
| HUB-ATT | `att_dec_map[o]` | 4 × 4（属主核 o → 广播目的掩码） | HUB-ATT | "判决广播映射" |
| HUB-ATT | `att_ring[k]` | 64 × 9 | HUB-ATT | "列表环配置"；【建议值·OI-22】 |
| R-hub | `rhub_cfg` | 16 | R-hub | HUB_RHUB p3 §3.1–3.2 |
| HUB-SYNC | `sync_scalar[k]` | 16 × 8 类 | HUB-SYNC | HUB_NOC p14 §4.5.1 |

合计（紧凑存放）：公共 50 + `dn_stream` 1,024 + `dn_sfd` 312 + `ps_rb` 512 + `up_cur` 3,072 + HUB-ATT 976 + R-hub 16 + HUB-SYNC 128 ≈ 6,100 bit ≈ 0.76 KB；双份约 1.5 KB。§5.5 的字地址图占 0x000–0x0FF（256 个 32 bit 字），10 bit 字地址留了 4 倍余量；寄存器只实现有定义的位。

`up_cur` 占了四分之三。如果负责人认为每核 16 个区域在单个位点里用不满，可以把条目数降到 8，SD 降到约 0.5 KB；这只改参数 `UP_CURSOR_PER_CORE`，不改结构。

### 5.4 子字段排布

各块内低位在前；未列出的位为保留，写 0、读 0。全部【拟定·OI-24】。

`dn_stream[i]`（128 bit，一条下行读流）。本 spec 把"一条流"定义为：一个（VC, 类别）、一组参与道，各道从本道象限内同一偏移处开始读（L2 区域按象限同样条带化）【拟定，以 L2 SRAM 篇区域规则为准，见 OI-04】。

| 位 | 字段 | 说明 |
|---|---|---|
| [0] | `en` | 本条有效 |
| [1] | `vc_sel` | 0 → VC0 重放，1 → VC1 数据 |
| [4:2] | `cls` | 下行类别（00 §4.3） |
| [5] | `seg_mode` | 1 = 段片交错重放（要求 `dn_sfd[i].fmt = 1`），0 = 整单位透传 |
| [6] | `nsplit` | 1 = N 切分子记录重放（每 token 4 条子记录，02 §5.3） |
| [7] | `dmode` | 0 = 全部道用 `dest_lane[0]`；1 = 逐道掩码（1 × 4 单播、2 × 2 同片多播，HUB_NOC p10 §4.2.4） |
| [11:8] | `lane_mask` | 参与的道 |
| [27:12] | `dest_lane[l]` | 每道 4 bit 目的掩码，道 0 在低位 |
| [41:28] | `qrow_base` | 象限内起始行（14 bit） |
| [55:42] | `qrow_len` | 象限内区域长度（行），读指针到末尾回绕 |
| [71:56] | `n_unit` | 每道本位点要发的单位数；0 表示由 `dn_sfd[i].count` 给 |
| [77:72] | `wcnt_region` | 放行门限所看的 L2 区域号（`L2_REGION_W` = 6【参数】） |
| [93:78] | `nth0` | 门限基值 |
| [94] | `gate_mode` | 0 = 整流一次门限（WCNT ≥ `nth0` 后整条流放行）；1 = 逐单位门限（发第 k 个单位前 WCNT ≥ `nth0` + k + 1） |
| [95] | `rcnt_en` | 1 = 每个单位读完成时报 RCNT |
| [101:96] | `rcnt_region` | 报 RCNT 的区域号 |
| [102] | `fill_tap` | 1 = 本流是另一条重放流的同流灌入截取（N3，HUB_NOC p10 §4.2.4），不单独读 L2 |
| [105:103] | `tap_src` | `fill_tap = 1` 时被截取的流号 |

`dn_sfd[i]`（39 bit）：格式见 00 §5。HUB-DN 只用 `fmt` 与 `w`，其余字段原样保留供验证比对。

`ps_rb[i]`（64 bit，一条 PS 读回，D-40 VC1 类别 3 单播，HUB_NOC p10 §4.2.6）：

| 位 | 字段 | 说明 |
|---|---|---|
| [0] | `en` | |
| [2:1] | `dest_core` | 单播目的 |
| [4:3] | `lane` | 所在象限 = 所走道 |
| [18:5] | `qrow_base` | 象限内起始行 |
| [34:19] | `n_row` | 行数 |
| [40:35] | `wcnt_region` | 读回前须等的区域 |
| [56:41] | `nth` | 门限：WCNT ≥ `nth` 才发（"发前须写完成计数达门限"） |
| [57] | `rcnt_en` | 读完成后报 RCNT（同一区域） |
`up_cur[c][r]`（48 bit，核 c 的区域 r 的写游标，协议篇 p19 §4.4.3）：

| 位 | 字段 | 说明 |
|---|---|---|
| [20:0] | `base` | L2 字节地址，须 32 B 对齐（低 5 位写 0） |
| [41:21] | `len` | 区域长度（字节，32 B 的整数倍）；游标到 `base + len` 回绕到 `base` |
| [42] | `en` | 本区域可写；为 0 时收到写该区域的 flit 计"非法区域"并丢弃 |
| [43] | `wrap_en` | 0 = 不回绕，写满再写计"区域越界"并丢弃【拟定】 |
| [44] | `keep` | 1 = 本位点沿用上一位点结束时的游标；0 = 本位点开始时游标复位为 `base` |

`keep` 是本 spec 补的：PDF 只说"基址、长度与回绕"，没说跨位点时游标从哪里续。同一区域跨多个位点连续写（如 chunk 池）需要续写，新一层的区域需要复位，两种都有，所以留 1 位【拟定】。chunk 池按 token 对齐的规则未定（OI-04），游标先按"到达序紧排、单位末尾补到 32 B 行"写。

`att_cfg`（64 bit）：

| 位 | 字段 | 说明 |
|---|---|---|
| [3:0] | `part_mask` | 本位点 attention 参与核 |
| [5:4] | `eblk` | 区块大小 64·2^eblk key（HUB_NOC p14 §4.4.10） |
| [6] | `adm_or_en` | 录取位图 OR 使能 |
| [7] | `blk_or_en` | 区块位图 OR 使能 |
| [8] | `lo_or_en` | 多核 lo 读集 OR 使能 |
| [9] | `dec_bc_en` | K 切分判决广播使能 |
| [10] | `batch_en` | Batch 合并键（段号）使能 |
| [14:11] | `n_kv_m1` | 本层 kv 头数 − 1 |
| [18:15] | `ring_adm` | 录取并集写入的环号 |
| [22:19] | `ring_blk` | 区块并集写入的环号 |
| [26:23] | `ring_lo` | lo 读集 OR 结果写入的环号 |
| [30:27] | `lo_part_mask` | lo 读集 OR 的参与核 |
| [34:31] | `dec_src_mask` | 允许发 K 切分判决的核（归约属主核集合），用于校验 |

`att_kv2core[h]`（4 bit × 16）：kv 头 h 的参与核掩码，录取 / 区块位图按它等齐（HUB_NOC p12 §4.4.1）。`att_seg_mask[s]`（4 bit × 64）：Batch 段 s 的参与核掩码，s = 0 为共享前缀段【建议值·OI-06】。`att_dec_map[o]`（4 bit × 4）：归约属主核 o 发来的判决要广播给哪些核。

`att_ring[k]`（64 bit，列表环 k）：

| 位 | 字段 | 说明 |
|---|---|---|
| [15:0] | `row_base` | 环起始 32 B 行 |
| [31:16] | `row_len` | 环长（行） |
| [32] | `en` | |
| [33] | `ptr_init` | 1 = 本位点开始时写指针复位到 `row_base`、在途记录表清空（调用开始时用）；0 = 沿用 |
| [39:34] | `rcnt_region` | 环所在区域，判环满用（§3.6 槽 4 + k） |

环号与环的对应见 04 §2【建议值·OI-22】。

`rhub_cfg`（16 bit，HUB_RHUB p3 §3.1）：

| 位 | 字段 | 说明 |
|---|---|---|
| [0] | `en` | 本位点启用 K 切分归约 |
| [4:1] | `part_mask` | 参与核；缺位按 +0（HUB_RHUB p4 §4.1.2） |
| [8:5] | `owner_mask` | 允许作归约属主的核，只用于校验 flit 头的属主号【建议值·OI-19】 |
| [9] | `sfd_chk` | 1 = 校验本位点 SFD（入口 fmt 8、出口 fmt 12 / g32 / 组内联），不符计数 |
| [10] | `ext_en` | down / o 的 K 切分扩展，本期须为 0【建议值·OI-20】 |

`sync_scalar[k]`（16 bit × 8，标量合并表，HUB_NOC p14 §4.5.1）：

| 位 | 字段 | 说明 |
|---|---|---|
| [0] | `en` | |
| [3:1] | `kind` | 0 Σx²、1 Σ\|xγ\|、2 amax、3 lse（mrun, l）、4 梯度范数² Draft、5 梯度范数² Target |
| [7:4] | `exp_mask` | 期望来源核 |
| [11:8] | `dest_mask` | 合并值回送目的；梯度范数类只填该模型首个 OPT 执行核 |
| [15:12] | `exp_cnt` | 期望份数；0 表示 = popcount(`exp_mask`)。梯度范数按"各组参与核掩码派生期望数"，可能多于核数 |

### 5.5 字地址图

`lic_sd_wr_addr` 按 32 bit 字编址。跨字字段低位在低地址。

| 字地址 | 内容 |
|---|---|
| `0x000` | `point_id`[15:0]、`barrier_mode`[17:16]、`barrier_part_mask`[21:18]、`tbl_wait_mask`[25:22]、`tier_sync_mask`[29:26] |
| `0x001` | `barrier_timeout`[15:0]、`wd`[19:16] |
| `0x010 + 4i` … `+3` | `dn_stream[i]`，i = 0–7 |
| `0x030 + 2i` … `+1` | `dn_sfd[i]` |
| `0x040 + 2i` … `+1` | `ps_rb[i]` |
| `0x050`–`0x051` | `att_cfg` |
| `0x052`–`0x053` | `att_kv2core[0..15]` |
| `0x054` | `att_dec_map[0..3]` |
| `0x058`–`0x05F` | `att_seg_mask[0..63]` |
| `0x060 + 2k` … `+1` | `att_ring[k]`，k = 0–8 |
| `0x078` | `rhub_cfg` |
| `0x07C`–`0x07F` | `sync_scalar[0..7]`，每字两条 |
| `0x080 + 32c + 2r` … `+1` | `up_cur[c][r]` |

其余地址保留：写忽略，并计"描述符非法地址"。

## 6. 顶层计数器

各子单元的计数器在 02–06 定义，这里只给统一读出地址（`lic_perf_rd_addr`，8 bit）和顶层自己的几项。全部 32 bit、饱和不回绕，`sd_swap` 拍锁存到影子组并清零（00 §8.2）。

| 地址 | 内容 |
|---|---|
| `0x00`–`0x1F` | HUB-DN（02 §9） |
| `0x20`–`0x3F` | HUB-UP（03 §9） |
| `0x40`–`0x4F` | HUB-ATT（04 §9） |
| `0x50`–`0x5F` | HUB-SYNC（05 §9） |
| `0x60`–`0x6F` | R-hub（06 §9） |
| `0xF0` | 位点拍数（上一 GO 到本 GO） |
| `0xF1` | 描述符未就绪次数（GO 时待生效份未 commit） |
| `0xF2` | 描述符非法地址写次数 |
| `0xF3` | 错误溢出粘滞位与已报错误数 |

PDF 的"D-40 等待汇总"指各核段片解析器因重放落地 FIFO 为空而等待的拍数，由核侧计、hub 按位点汇总（HUB_NOC p9 §4.2.2）。核侧怎样把这个数交给 hub，PDF 没写。本 spec 让它随位点完成消息上来（00 §6.2 类型 `8'h01` 的字节 6–9），由 HUB-SYNC 按位点求和后放进 05 §9 的计数器；"计数 ÷ 位点拍数越阈值"的判断交给 LIC，hub 只提供两个数【拟定】。

## 7. 本文件涉及的未决项

| OI | 在本文件的落点 | 当前做法 |
|---|---|---|
| OI-24 | §5 整张 SD 表、§3.7 装载方式 | 本 spec 拟定，双份 + commit + GO 后 1 拍切换 |
| OI-25 | §3.7 | "hub 配置口"按 LIC 控制口处理 |
| OI-23 | §3.7–3.9 事件口内容 | 按 00 §6 暂定类型码分流 |
| OI-22 | §5.4 `att_ring`、`att_cfg` 环号字段 | 9 个环 |
| OI-19 / OI-20 | §5.4 `rhub_cfg` | 以 flit 头为准、扩展位置 0 |
| OI-06 | §5.4 `att_seg_mask` | 64 段 × 4 bit |
| OI-04 | §5.4 `up_cur` | 到达序紧排 |
| OI-11a | §5.2 | 双份 SD 约 1.5 KB 计入 RF 总账 |

## 8. 顶层验证要点

顶层只验证集成关系，子单元功能在各自 tb 里验。用例名见 07。

1. 侧带头打包 / 解包：00 §4 的三个例子（`12'h45E`、`14'h12C5`、`14'h2150`）在 `hub_pkg` 函数和顶层端口上都对得上。
2. 描述符生效：在位点 n 运行中写待生效份并 commit，检查 GO 当拍各子单元仍用旧份、GO + 1 拍起用新份；不 commit 时沿用旧份并计数。
3. 端到端通路：每类上行（VC0 各类别、VC1 两类、VC2、VC3 各类型）都能到达 01 §4.2 表中的去向；每类下行注入源都能出 D-40。
4. 信用返还线：56 根线每根单独打脉冲，只有对应计数器 +1。
5. 错误汇总：6 类致命错误各触发一次，`lic_err_*` 字段正确；同拍两个错误时小码先报、溢出位置 1。
6. 复位：复位释放后所有 `dn_vld`、`up_crd`、事件口 `vld` 为 0，信用计数器为初值，SD 为全禁用。


