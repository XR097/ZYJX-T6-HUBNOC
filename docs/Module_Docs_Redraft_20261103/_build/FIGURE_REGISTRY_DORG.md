# 数据组织篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-08｜第一版，随 `DATA_ORGANIZATION.md` 正文产出。改图时从这里找脚本、函数、数值来源与正文位置；改完重跑并逐张看 PNG。自动索引见 `FIGURE_REGISTRY.md`。

## 再生成

```bash
python -X utf8 -I _build/draw_data_org.py
```

```bash
python -X utf8 -I _build/draw_transfer_protocol.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

第一条出本篇七张新图；第二条出协议篇的十张数值小例，其中三张（OBJECT-ALIGN、FIXED-ITEM、WINDOW-GATHER）自协议篇旧 §9 迁入本篇，函数不移动。

## 本篇新图（`_build/draw_data_org.py`，`SvgF5` 手写格子）

| 图文件 | 函数 | 正文位置 | 画什么 | 常量与断言 |
|---|---|---|---|---|
| `figs/FIG-DORG-SEGMENT.svg` | `fig_segment()` | §2.1 | 同一段 32 通道、保留 20 个，$w$ = 6 / 8 / 16 三行按字节比例画：尺度 1 B（16 bit 无）+ keep 4 B + F 3 B + 码 15 / 20 / 40 B = 23 / 28 / 47 B | `seg_bytes(w, ks)`、`KS = 20`、`SEG`；断言 {6: 23, 8: 28, 16: 47} 与全保留 {33, 41, 72} |
| `figs/FIG-DORG-SPLIT-T.svg` | `fig_split_t()` | §5.2 | 8 个 token 分四核，核 $c$ 的两条记录（70 / 40、55 / 61、48 / 52、66 / 45 B）紧挨成象限 $c$ 的数据块（字节 4096）+ 长度表（字节 8192）；下排两种读法（T → T 单播、T → M 多播） | `T_LEN`、`T_BASE`、`T_TAB`、`T_BLK`；断言块长 [110, 116, 100, 111]、共 8 条 |
| `figs/FIG-DORG-SPLIT-M.svg` | `fig_split_m()` | §5.3 | $M = 128$ 列分四核，象限 $q$ = 4 个 token 的第 $q$ 段（片长 23/18/33/12、20/25/15/28、30/11/22/19、17/26/14/24 B）各配长度表；消费核四区域基址字 0 / 33 / 66 / 99；token 1 = 四片 80 B | `M_PIECE`、`M_REGION`、`TOK1`；断言基址模 4 互不相同、反例 0/32/64/96 同余、token 1 四片和 = 80 |
| `figs/FIG-DORG-SPLIT-K.svg` | `fig_split_k()` | §5.4 | 四核 BF16 部分和同址异象限（字节 8192）→ 归约 1 / −0.5 / 0 / 9（字节 12288）→ 与残差（码 1.5/−3/4/1 × $2^{-1}$）相加 1.75 / −2 / 2 / 9.5 → 尺度 $2^1$、码 0.875 / −1 / 1 / 5 写回字节 16384；数值与 FIG-MAE_CRU-RESID 相同 | `K_PART`、`K_SUM`、`RES_CODE`、`RES_SCALE`、`NEW`、`NEW_SCALE`、`e2m3_rne()`；断言四份和、尺度选择、E2M3 码（4.75 RNE → 5） |
| `figs/FIG-DORG-DDR-STD.svg` | `fig_ddr_std()` | §6.1 | 标准布局数字单元缩画 8 个 $k$ 行 × 4 列组 × 每列组 2 个通道（纯数字）；右侧尺度数据块两种排序（K 组主序 / 列段主序）与 bias 数据块 | `NK, NG, PM = 8, 4, 2`、`NS = 2`、`SEGW = 4`、`UNIT`、`SC_KMAJ`、`SC_SEGMAJ`；断言两种排序同集合、数字单元只有码 |
| `figs/FIG-DORG-DDR-COL.svg` | `fig_ddr_col()` | §6.2 | 列深度优先缩画 4 列 × 16 个 $k$、每拍 4 个 $k$：DDR 一列连续；落 L1 列字区列 $j$ → bank ⌊j/2⌋、深度 $2p + (j \bmod 2)$ | `NCOL, KLEN, KB = 4, 16, 4`、`BEATS`；断言每拍 $k$ 连续、列间不交织 |
| `figs/FIG-DORG-DDR-ACT.svg` | `fig_ddr_act()` | §6.3 | 上：卸载到 DDR 的激活数据块（70 / 40 / 100 B 紧挨 + 长度表 9 B）；下：K hi / K lo / kmax / V hi / V lo 五个平面各按 key 连续（68 / 64 / 1 / 64 / 64 B/key），录取 key 1 的 gather = 192 B | `ACT_LEN`、`ACT_START`、`KV_STRIDE`、`GATHER`；断言起点 [0, 70, 110]、210 B、gather 192 B |

## 迁入的图（`_build/draw_transfer_protocol.py`，登记细节见 `FIGURE_REGISTRY_TP.md`）

| 图文件 | 函数 | 正文位置 |
|---|---|---|
| `figs/FIG-TP-OBJECT-ALIGN.svg` | `fig_object_align()` | §1.2 |
| `figs/FIG-TP-FIXED-ITEM.svg` | `fig_fixed_item()` | §3 |
| `figs/FIG-TP-WINDOW-GATHER.svg` | `fig_window_gather()` | §5.7 |

## 只引用的图

FIG-L1_SRAM-MAP-A、FIG-L2_SRAM-OBJ-ALIGN（§1.2 提及）；FIG-MAE_DSU-REGROUP（§6.1）；FIG-MAE_ENG-QSPLICE（§5.3）；FIG-MAE_CRU-RESID（§4.1、§5.4）。

## 约定

- 数值由脚本算出并断言；改常量要同步正文图下说明（SPLIT-K 的数值与 MAE_CRU 篇 FIG-MAE_CRU-RESID、SPLIT-M 的区域基址与 MAE_ENG 篇 FIG-MAE_ENG-QSPLICE 保持一致，改一处要改两处）。
- 图里不画拍级握手与 bank 冲突细节（归 L1 / L2 / 协议篇的图）。
