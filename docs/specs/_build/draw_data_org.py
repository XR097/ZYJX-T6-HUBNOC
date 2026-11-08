"""数据组织篇（DATA_ORGANIZATION.md）的数值小例。Owner: WangYizhao · 2026-11-08
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_data_org.py
输出（figs/）：
  FIG-DORG-SEGMENT   同一段 32 通道、保留 20 个：w = 6 / 8 / 16 三种元素位宽的段字节（§2.1）
  FIG-DORG-SPLIT-T   核间按 T 切分：8 个 token 分四核，各核产出在本核象限各成一个数据块 + 长度表（§5.2）
  FIG-DORG-SPLIT-M   核间按 M 切分：128 列分四核，token t 的记录 = 四象限各一片，消费核四区域基址模 4 互不相同（§5.3）
  FIG-DORG-SPLIT-K   核间按 K 切分：四核 BF16 部分和同址异象限 → MAE_CRU 归约 → 与 L2 残差相加写回（§5.4）
  FIG-DORG-DDR-STD   DDR 标准布局：1 KB 单元的 k 行与列组、独立尺度数据块（两种排序）、bias 数据块（§6.1）
  FIG-DORG-DDR-COL   DDR 列深度优先布局：一列连续，一拍 = 该列 64 个连续 k = L1 列字区一个存储字（§6.2）
  FIG-DORG-DDR-ACT   DDR 里的激活数据块（记录紧挨 + 长度表）与 K / V 平面（按 key 连续）（§6.3）
迁入引用（脚本仍在 draw_transfer_protocol.py）：FIG-TP-OBJECT-ALIGN、FIG-TP-FIXED-ITEM、FIG-TP-WINDOW-GATHER。
脚本断言：段长公式三值；T 切分各象限块长 = 记录之和；M 切分四区域基址模 4 互不相同、token 1 四片之和；
          K 切分四份之和与 E2M3 编码；标准布局两种尺度排序同集合、数字单元不含尺度；列深度优先每拍 k 连续；KV 平面步长与 gather 字节。
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fig_f5_post import SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, INK, C_KEEP, C_LO, C_OFF, C_HI, C_SIDE, C_W, C_ACC, C_LEFT  # noqa: E402

DATE = '2026-11-08'


# =====================================================================
# §2.1 段字节
# =====================================================================
def seg_bytes(w, ks):
    return (5 if w in (6, 8) else 4) + math.ceil(ks / 8) + (math.ceil(w * ks / 8) if w != 16 else 2 * ks)


KS = 20
SEG = {w: seg_bytes(w, KS) for w in (6, 8, 16)}
assert SEG == {6: 23, 8: 28, 16: 47}
assert {w: seg_bytes(w, 32) for w in (6, 8, 16)} == {6: 33, 8: 41, 16: 72}


def fig_segment():
    s = SvgF5(1180, 330)
    x0, y0 = 215, 70
    scale = 16          # px / B
    rows = [(6, 'w = 6（MXFP6 E2M3）'), (8, 'w = 8（FP8 E4M3）'), (16, 'w = 16（BF16 / FP16）')]
    s.rich(x0, y0 - 40, f'同一段：32 个通道、保留 k_s = {KS} 个，keep 位图 4 B、F 标志 ⌈20/8⌉ = 3 B', 13, 'start', GREY, 600)
    for i, (w, name) in enumerate(rows):
        y = y0 + i * 62
        s.rich(x0 - 14, y + 16, name, 13, 'end')
        x = x0
        parts = []
        if w != 16:
            parts.append(('尺度 1 B', 1, C_SIDE))
        parts.append(('keep 4 B', 4, C_ACC))
        parts.append(('F 3 B', 3, C_LO))
        code = 2 * KS if w == 16 else math.ceil(w * KS / 8)
        parts.append((f'码 {code} B（{KS} × {w} bit）', code, C_KEEP))
        for label, b, fill in parts:
            s.cell(x, y, b * scale, 32, label if b * scale > 60 else '', fill=fill, size=12)
            if b * scale <= 60:
                s.rich(x + b * scale / 2, y - 8, label.split(' ')[0], 10, 'middle', GREY, 600)
            x += b * scale
        s.rich(x + 10, y + 16, f'= {SEG[w]} B', 14, 'start', NAVY, 700)
    y = y0 + 3 * 62 + 10
    s.red(x0, y, '元素位宽 w 是位点属性；16 bit 段没有尺度字段；keep / F / 长度表三种位宽同一套规则', 14)
    s.rich(x0, y + 24, '全保留（k_s = 32）时三者 33 / 41 / 72 B；一条记录的长度 = 各段字节之和，写进 token 长度表', 13, 'start', NAVY, 600)
    assert y + 40 <= s.h
    s.save('FIG-DORG-SEGMENT.svg', date=DATE)


# =====================================================================
# §5.2 按 T 切分
# =====================================================================
T_LEN = [[70, 40], [55, 61], [48, 52], [66, 45]]        # 核 c 的两条输出记录长度
T_BASE, T_TAB = 4096, 8192
T_BLK = [sum(x) for x in T_LEN]
assert T_BLK == [110, 116, 100, 111] and sum(len(x) for x in T_LEN) == 8


def fig_split_t():
    s = SvgF5(1100, 470)
    x0, y0 = 120, 70
    s.rich(x0, y0 - 40, '8 个 token t0…t7 分四核：核 c 算 t_{2c}、t_{2c+1} 的全部输出通道', 13, 'start', GREY, 600)
    qw, qh = 230, 150
    fills = [C_KEEP, C_LO, C_HI, C_W]
    for c in range(4):
        x = x0 + c * (qw + 14)
        s.rect(x, y0, qw, qh, fill='white', sw=1.6, rx=6)
        s.rich(x + 10, y0 + 18, f'L2 象限 {c}（核 {c} 写）', 13)
        # 数据块
        xb = x + 14
        s.rich(xb, y0 + 46, f'字节 {T_BASE}：', 11, 'start', GREY, 600)
        xx = xb
        for i, L in enumerate(T_LEN[c]):
            wpx = L * 1.3
            s.cell(xx, y0 + 56, wpx, 30, f't{2*c+i} {L} B', fill=fills[c], size=11)
            xx += wpx
        s.rich(xb, y0 + 104, f'字节 {T_TAB}：长度表 [{T_LEN[c][0]}, {T_LEN[c][1]}]（6 B）', 11, 'start', GREY, 600)
        s.cell(xb, y0 + 112, 60, 22, '表', fill=C_SIDE, size=11)
        s.rich(xb + 70, y0 + 123, f'块长 {T_BLK[c]} B', 12, 'start', NAVY, 700)
    # 下一位点两种读法
    y1 = y0 + qh + 50
    s.rich(x0, y1, '下一位点仍按 T：道 c 单播回核 c，每核只收自己的 2 条记录（32 B/拍）', 14, 'start', NAVY, 700)
    for c in range(4):
        x = x0 + c * (qw + 14) + qw / 2
        s.line([(x, y0 + qh + 4), (x, y1 - 18)], sw=1.3)
        s.cell(x - 40, y1 + 16, 80, 26, f'核 {c}', fill=fills[c], size=12)
    y2 = y1 + 70
    s.rich(x0, y2, '下一位点改按 M：四道各搬本象限的数据块、核集合 1111，每核收到全部 8 条记录（128 B/拍）', 14, 'start', NAVY, 700)
    s.red(x0, y2 + 30, '产出留本核象限：一个数据块 + 一张长度表，不同址；残差与记录同驻本核 L1', 14)
    s.rich(x0, y2 + 54, '实际记录 KB 级、每核 T/4 条；地址由编译链给，长度表由生产核 CCU 写', 13, 'start', GREY, 600)
    assert y2 + 70 <= s.h
    s.save('FIG-DORG-SPLIT-T.svg', date=DATE)


# =====================================================================
# §5.3 按 M 切分
# =====================================================================
M_PIECE = [[23, 18, 33, 12], [20, 25, 15, 28], [30, 11, 22, 19], [17, 26, 14, 24]]   # 象限 q 里 token t 的片长
M_REGION = [0, 33, 66, 99]
assert len({b % 4 for b in M_REGION}) == 4
TOK1 = sum(M_PIECE[q][1] for q in range(4))
assert TOK1 == 80 and len({b % 4 for b in [0, 32, 64, 96]}) == 1


def fig_split_m():
    s = SvgF5(1180, 520)
    x0, y0 = 60, 70
    s.rich(x0, y0 - 40, 'M = 128 列分四核：核 c 持列 32c…32c+31（一段），算全部 4 个 token 在这一段上的输出', 13, 'start', GREY, 600)
    fills = [C_KEEP, C_LO, C_HI, C_W]
    qw = 262
    sc = 2.6
    for q in range(4):
        x = x0 + q * (qw + 14)
        s.rect(x, y0, qw, 120, fill='white', sw=1.6, rx=6)
        s.rich(x + 10, y0 + 18, f'象限 {q}：4 个 token 的第 {q} 段', 12)
        xx = x + 12
        for t, L in enumerate(M_PIECE[q]):
            wpx = L * sc
            s.cell(xx, y0 + 34, wpx, 28, f't{t} {L}' if wpx >= 46 else f't{t}', fill=fills[t], size=11)
            xx += wpx
        s.rich(x + 12, y0 + 84, f'长度表 [{", ".join(map(str, M_PIECE[q]))}]', 11, 'start', GREY, 600)
        s.rich(x + 12, y0 + 104, f'道 {q} 按本表顺序搬 → 区域 {q}', 11, 'start', NAVY, 700)
    # 消费核 L1 四个区域
    y1 = y0 + 170
    s.rich(x0, y1 - 20, '消费核 L1 A 类（4 bank 配置）：四个区域，基址字号 0 / 33 / 66 / 99（模 4 = 0 / 1 / 2 / 3）→ 四道首拍落 bank 8 / 9 / 10 / 11', 13, 'start', NAVY, 700)
    for q in range(4):
        x = x0 + q * (qw + 14)
        s.line([(x + qw / 2, y0 + 122), (x + qw / 2, y1 - 2)], sw=1.3)
        s.rect(x, y1, qw, 86, fill='white', sw=1.6, rx=6)
        s.rich(x + 10, y1 + 16, f'区域 {q}：基址字 {M_REGION[q]}（bank {8 + M_REGION[q] % 4}）', 12)
        xx = x + 12
        for t, L in enumerate(M_PIECE[q]):
            wpx = L * sc
            s.cell(xx, y1 + 30, wpx, 28, f't{t}', fill=fills[t] if t == 1 else C_OFF, size=11)
            xx += wpx
        s.rich(x + 12, y1 + 74, f'token 1 的片在 +{M_PIECE[q][0]}，长 {M_PIECE[q][1]} B', 11, 'start', GREY, 600)
    y2 = y1 + 120
    s.red(x0, y2, f'token 1 的记录 = 四个区域各一片：18 + 25 + 11 + 26 = {TOK1} B，CCU 按四张表依次给四段地址，段解包器按 k 顺序接着解', 14)
    s.rich(x0, y2 + 26, '基址若取字 0 / 32 / 64 / 96（模 4 都是 0），四道首拍都落 bank 8、每拍只能写一项；错开后各道各自推进、偶发撞 bank 由入口 FIFO 吸收', 13, 'start', NAVY, 600)
    s.rich(x0, y2 + 48, '实际每段 32 个输出通道、片长随 keep 变；四个象限的数据块各自独立、不同址（V18-MAE-33）', 13, 'start', GREY, 600)
    assert y2 + 64 <= s.h
    s.save('FIG-DORG-SPLIT-M.svg', date=DATE)


# =====================================================================
# §5.4 按 K 切分（数值与 FIG-MAE_CRU-RESID 相同）
# =====================================================================
K_PART = [[0.5, -0.25, 1.0, 3.0], [0.25, -0.25, -1.0, 2.0], [0.25, 0.0, 0.5, 4.0], [0.0, 0.0, -0.5, 0.0]]
K_SUM = [sum(K_PART[c][i] for c in range(4)) for i in range(4)]
assert K_SUM == [1.0, -0.5, 0.0, 9.0]
RES_CODE, RES_SCALE = [1.5, -3.0, 4.0, 1.0], 0.5
RES_VAL = [c * RES_SCALE for c in RES_CODE]
NEW = [a + b for a, b in zip(K_SUM, RES_VAL)]
assert NEW == [1.75, -2.0, 2.0, 9.5]


def e2m3_rne(v):
    """E2M3（偏置 1）：子规格步 1/8；e=1 [1,2) 步 1/8；e=2 [2,4) 步 1/4；e=3 [4,8) 步 1/2。RNE。"""
    a = abs(v)
    assert a <= 7.5
    step = 0.125 if a < 2 else 0.25 if a < 4 else 0.5
    q = a / step
    r = math.floor(q)
    frac = q - r
    if frac > 0.5 or (frac == 0.5 and r % 2 == 1):
        r += 1
    return math.copysign(r * step, v)


amax = max(abs(v) for v in NEW)
NEW_SCALE = 2 ** math.floor(math.log2(amax / 7.5)) if amax > 7.5 else 1.0
NEW_SCALE = 2.0
assert amax / NEW_SCALE <= 7.5 and amax / (NEW_SCALE / 2) > 7.5
NEW_CODE = [e2m3_rne(v / NEW_SCALE) for v in NEW]
assert NEW_CODE == [0.875, -1.0, 1.0, 5.0]


def fmt(v):
    return f'{v:g}'


def fig_split_k():
    s = SvgF5(1100, 570)
    x0, y0 = 230, 70
    cw, ch = 70, 28
    fills = [C_KEEP, C_LO, C_HI, C_W]
    s.rich(x0, y0 - 40, '1 个 token、4 个输出通道 m0…m3（实际一字 16 个 BF16、一行 M 个）；K 分四份，核 c 算 Y^{(c)} = X_{:,K_c} W_{K_c,:}', 13, 'start', GREY, 600)
    for c in range(4):
        y = y0 + c * (ch + 6)
        s.rich(x0 - 14, y + ch / 2, f'核 {c} → 象限 {c} 字节 8192', 12, 'end')
        for i, v in enumerate(K_PART[c]):
            s.cell(x0 + i * cw, y, cw, ch, fmt(v), fill=fills[c], size=12)
    s.rich(x0 + 4 * cw + 14, y0 + 2 * (ch + 6) - 6, '同一象限内地址（同址异象限），BF16', 12, 'start', NAVY, 600)
    # 归约
    y1 = y0 + 4 * (ch + 6) + 30
    s.line([(x0 + 2 * cw, y0 + 4 * (ch + 6) - 2), (x0 + 2 * cw, y1 - 4)], sw=1.6)
    s.rich(x0 + 2 * cw + 10, y1 - 20, '归约指令：NI 读口一拍取四份 → MAE_CRU 相加', 12, 'start', NAVY, 700)
    s.rich(x0 - 14, y1 + ch / 2, 'Y（BF16）→ L2 字节 12288', 12, 'end')
    for i, v in enumerate(K_SUM):
        s.cell(x0 + i * cw, y1, cw, ch, fmt(v), fill=C_ACC, size=12)
    # 残差
    y2 = y1 + ch + 40
    s.rich(x0 - 14, y2 + ch / 2, "残差 x'（L2，E2M3 码 × 2^{-1}）", 12, 'end')
    for i, v in enumerate(RES_CODE):
        s.cell(x0 + i * cw, y2, cw, ch, f'{fmt(v)} → {fmt(RES_VAL[i])}', fill=C_SIDE, size=11)
    y3 = y2 + ch + 40
    s.line([(x0 + 2 * cw, y1 + ch + 2), (x0 + 2 * cw, y3 - 4)], sw=1.6)
    s.rich(x0 + 4 * cw + 14, y2 + ch / 2, "残差加指令：x'' = x' + Y，解码后相加", 12, 'start', NAVY, 700)
    s.rich(x0 - 14, y3 + ch / 2, "x''（宽格式）", 12, 'end')
    for i, v in enumerate(NEW):
        s.cell(x0 + i * cw, y3, cw, ch, fmt(v), fill=C_ACC, size=12)
    y4 = y3 + ch + 40
    s.rich(x0 - 14, y4 + ch / 2, '一次编码 → 残差流字节 16384', 12, 'end')
    for i, v in enumerate(NEW_CODE):
        s.cell(x0 + i * cw, y4, cw, ch, f'码 {fmt(v)}', fill=C_KEEP if i != 3 else C_LEFT, size=11)
    s.rich(x0 + 4 * cw + 14, y4 + ch / 2, f'组尺度 2^{{1}}（最大幅值 9.5 > 7.5）；4.75 按 RNE 舍到 5（[4, 8) 步长 0.5）', 12, 'start', NAVY, 600)
    y5 = y4 + ch + 30
    s.red(x0, y5, '部分和不含残差；残差流驻 L2；残差只加一次、编码一次（两条搬运指令，MAE_CRU 运算级）', 14)
    s.rich(x0, y5 + 24, '结果在 L2，由一条 L2 → L1 指令经 H2C 送下去；数值与 MAE_CRU 篇图 FIG-MAE_CRU-RESID 相同', 13, 'start', GREY, 600)
    assert y5 + 40 <= s.h
    s.save('FIG-DORG-SPLIT-K.svg', date=DATE)


# =====================================================================
# §6.1 标准布局（缩画：8 个 k 行 × 4 列组 × 每列组 2 个通道）
# =====================================================================
NK, NG, PM = 8, 4, 2
UNIT = [[[(k, g * PM + i) for i in range(PM)] for g in range(NG)] for k in range(NK)]
NS = 2                                 # 两个 K 组（缩画：每 K 组 4 个 k）
M_TOT = NG * PM
SC_KMAJ = [(sidx, m) for sidx in range(NS) for m in range(M_TOT)]
SEGW = 4                               # 缩画的"32 列段"= 4 个通道（两个列组）
SC_SEGMAJ = [(sidx, m) for seg in range(M_TOT // SEGW) for sidx in range(NS) for m in range(seg * SEGW, (seg + 1) * SEGW)]
assert sorted(SC_KMAJ) == sorted(SC_SEGMAJ) and len(SC_KMAJ) == NS * M_TOT
assert all(isinstance(c, tuple) and len(c) == 2 for row in UNIT for g in row for c in g)   # 数字单元里只有码，没有尺度


def fig_ddr_std():
    s = SvgF5(1140, 520)
    x0, y0 = 110, 80
    cw, ch, gap = 44, 26, 16
    fills = [C_KEEP, C_LO, C_HI, C_W]
    s.rich(x0, y0 - 50, '数字单元（纯数字）：一行 = 一拍 = 4 个列组各一个粒子', 13, 'start', GREY, 600)
    for g in range(NG):
        xg = x0 + g * (PM * cw + gap)
        s.rich(xg + PM * cw / 2, y0 - 24, f'列组 g{g}（→ 核 {g}）', 12, 'middle', GREY, 600)
    for k in range(NK):
        y = y0 + k * (ch + 4)
        s.rich(x0 - 12, y + ch / 2, f'k{k}' + ('  K 组 s0' if k == 0 else '  K 组 s1' if k == 4 else ''), 12, 'end')
        for g in range(NG):
            xg = x0 + g * (PM * cw + gap)
            for i, (kk, m) in enumerate(UNIT[k][g]):
                s.cell(xg + i * cw, y, cw, ch, f'W[{kk},{m}]', fill=fills[g], size=10)
    # 尺度数据块
    xs = x0 + NG * (PM * cw + gap) + 60
    s.rich(xs, y0 - 50, '尺度数据块（E8M0，无填充）：两种排序二选一', 13, 'start', GREY, 600)
    sw_ = 48
    s.rich(xs, y0 - 24, '(a) K 组主序：s0 的 m0…m7 连续，再 s1', 12, 'start', NAVY, 700)
    for j, (sidx, m) in enumerate(SC_KMAJ):
        r, c = divmod(j, 8)
        s.cell(xs + c * sw_, y0 + r * (ch + 4), sw_, ch, f'e[{sidx},{m}]', fill=C_SIDE if sidx == 0 else C_ACC, size=10)
    yb = y0 + 2 * (ch + 4) + 30
    s.rich(xs, yb - 10, '(b) 列段主序：列段 0（m0…m3）的 s0、s1，再列段 1', 12, 'start', NAVY, 700)
    for j, (sidx, m) in enumerate(SC_SEGMAJ):
        r, c = divmod(j, 8)
        s.cell(xs + c * sw_, yb + 6 + r * (ch + 4), sw_, ch, f'e[{sidx},{m}]', fill=C_SIDE if sidx == 0 else C_ACC, size=10)
    yb2 = yb + 6 + 2 * (ch + 4) + 30
    s.rich(xs, yb2 - 10, 'bias 数据块（BF16，按 m 连续）', 12, 'start', NAVY, 700)
    for m in range(M_TOT):
        s.cell(xs + m * sw_, yb2 + 6, sw_, ch, f'b[{m}]', fill=C_LEFT, size=10)
    y = y0 + NK * (ch + 4) + 30
    s.red(x0, y, '一拍 = 1 个 k × 4 个列组；按 F 行读一拍一行；尺度与 bias 各是独立数据块，由普通搬运指令整字落 S 类', 14)
    s.rich(x0, y + 24, 'L1 行字区一字 = 1 个列组 × 4 个相邻 k，与一拍正交：由 MAE_DSU 攒 4 行按字重排成各核整字（图 FIG-MAE_DSU-REGROUP）；', 13, 'start', NAVY, 600)
    s.rich(x0, y + 44, '按 M 切分列组 g → 核 g，单核 / 按 T 切分 4 个列组都给该核。实际每 K 组 32 行、每列组 16 个通道（8 B）、一行 32 B、一个单元 1 KB；', 13, 'start', NAVY, 600)
    s.rich(x0, y + 64, '尺度每 32 个 m 一个 32 B 尺度行；LSC 一行 64 B = 4 核各 16 B，同理攒 2 行。', 13, 'start', NAVY, 600)
    assert y + 80 <= s.h
    s.save('FIG-DORG-DDR-STD.svg', date=DATE)


# =====================================================================
# §6.2 列深度优先（缩画：4 列 × 16 个 k，每拍 4 个 k）
# =====================================================================
NCOL, KLEN, KB = 4, 16, 4
BEATS = [(m, list(range(b * KB, (b + 1) * KB))) for m in range(NCOL) for b in range(KLEN // KB)]
for m, ks in BEATS:
    assert ks == list(range(ks[0], ks[0] + KB))
assert [m for m, _ in BEATS] == sorted(m for m, _ in BEATS)      # 列间不交织


def fig_ddr_col():
    s = SvgF5(1100, 430)
    x0, y0 = 120, 80
    bw, bh = 58, 30
    fills = [C_KEEP, C_LO, C_HI, C_W]
    s.rich(x0, y0 - 50, 'DDR 地址 →（一列连续：列 m0 的全部 k，再列 m1 …；每格一拍，实际一拍 32 B = 该列 64 个连续 k）', 13, 'start', GREY, 600)
    for j, (m, ks) in enumerate(BEATS):
        x = x0 + j * bw
        s.cell(x, y0, bw, bh, f'm{m}', fill=fills[m], size=11)
        s.rich(x + bw / 2, y0 + bh + 14, f'k{ks[0]}–{ks[-1]}', 10, 'middle', GREY, 600)
    # L1 列字区
    y1 = y0 + 125
    s.rich(x0, y1 - 44, 'L1 列字区（L1 篇 §4.2）：每拍整字直写一个存储字，列 j → bank ⌊j/2⌋、深度 2p + (j mod 2)；不需要重排', 13, 'start', NAVY, 700)
    for j, (m, ks) in enumerate(BEATS):
        p = ks[0] // (2 * KB)      # 缩画：两拍 = 一对段
        depth = 2 * p + (m % 2)
        bank = m // 2
        x = x0 + bank * 260 + (ks[0] // KB % 2) * 120
        y = y1 + depth * (bh + 6)
        s.cell(x, y, 110, bh, f'm{m} k{ks[0]}–{ks[-1]}', fill=fills[m], size=10)
    for bank in range(2):
        s.rich(x0 + bank * 260 + 115, y1 - 4, f'bank {bank}', 11, 'middle', GREY, 600)
    for d in range(4):
        s.rich(x0 - 12, y1 + d * (bh + 6) + bh / 2, f'深度 {d}', 11, 'end')
    s.rich(x0 + 560, y1 + 10, '尺度：与标准布局同一个尺度数据块', 12, 'start', NAVY, 600)
    s.rich(x0 + 560, y1 + 32, '（两种排序之一），DSU 转置前另读；', 12, 'start', NAVY, 600)
    s.rich(x0 + 560, y1 + 54, '每列 1 B colmax_w 排布归设计者', 12, 'start', NAVY, 600)
    y = y1 + 4 * (bh + 6) + 20
    s.red(x0, y, '一拍 = 一列 64 个连续 k = L1 列字区的一个存储字；按列 gather 时一列连续', 14)
    s.rich(x0, y + 24, '用于输出维度稀疏的位点（up hi、gate / up lo、LM Head lo 等）；一列长 K/2 B、列起点 64 B 对齐、只在列尾补齐', 13, 'start', GREY, 600)
    assert y + 40 <= s.h
    s.save('FIG-DORG-DDR-COL.svg', date=DATE)


# =====================================================================
# §6.3 激活与 KV 在 DDR
# =====================================================================
ACT_LEN = [70, 40, 100]
ACT_START = [sum(ACT_LEN[:i]) for i in range(3)]
assert ACT_START == [0, 70, 110] and sum(ACT_LEN) == 210
KV_STRIDE = {'K hi': 68, 'K lo': 64, 'kmax': 1, 'V hi': 64, 'V lo': 64}
GATHER = KV_STRIDE['K lo'] + KV_STRIDE['V hi'] + KV_STRIDE['V lo']
assert GATHER == 192 and KV_STRIDE['K hi'] == 64 + 4


def fig_ddr_act():
    s = SvgF5(1100, 490)
    x0, y0 = 150, 70
    s.rich(x0, y0 - 40, '上：卸载到 DDR 的激活数据块（与片上相同：记录紧挨 + 长度表另存）', 13, 'start', GREY, 600)
    s.rich(x0 - 14, y0 + 15, '数据块起点 A', 12, 'end')
    x = x0
    fills = [C_KEEP, C_LO, C_HI]
    for i, L in enumerate(ACT_LEN):
        s.cell(x, y0, L * 2.4, 30, f'记录 {i}：{L} B', fill=fills[i], size=11)
        s.rich(x + 2, y0 + 42, f'+{ACT_START[i]}', 10, 'start', GREY, 600)
        x += L * 2.4
    s.rich(x + 10, y0 + 15, '共 210 B，末字带 be', 12, 'start', NAVY, 600)
    s.rich(x0 - 14, y0 + 75, '长度表地址 B', 12, 'end')
    s.cell(x0, y0 + 60, 150, 30, '[70, 40, 100]（9 B）', fill=C_SIDE, size=11)
    s.rich(x0 + 160, y0 + 75, '每项 24 bit = 16 bit 长度 + 8 bit tokmax；重装整块拷贝、不解析', 12, 'start', NAVY, 600)
    # KV
    y1 = y0 + 145
    s.rich(x0, y1 - 24, '下：K / V 每类一个平面、平面内按 key 连续（d_h = 128，3 个 key；实际每平面按 key 步进）', 13, 'start', GREY, 600)
    rows = [('K hi 平面', 68, '64 B 码 + 4 B E8M0', C_HI), ('K lo 平面', 64, '64 B 码（无尺度）', C_LO),
            ('kmax 平面', 1, '1 B', C_SIDE), ('V hi 平面', 64, '64 B', C_W), ('V lo 平面', 64, '64 B', C_ACC)]
    for r, (name, stride, desc, fill) in enumerate(rows):
        y = y1 + r * 36
        s.rich(x0 - 14, y + 14, name, 12, 'end')
        for key in range(3):
            wpx = max(stride * 1.6, 40)
            s.cell(x0 + key * (wpx + 6), y, wpx, 28, f'key {key}', fill=fill if key == 1 else C_OFF, size=11)
        s.rich(x0 + 3 * (max(stride * 1.6, 40) + 6) + 10, y + 14, f'步长 {stride} B/key：{desc}', 12, 'start', NAVY, 600)
    y = y1 + 5 * 36 + 10
    s.red(x0, y, f'粗算顺序扫 K hi 平面 + kmax；录取 key 1 后按列表 gather 它的 K lo + V hi + V lo = {GATHER} B', 14)
    s.rich(x0, y + 24, '每类数据各自连续、不逐 key 交织：顺序流读与 gather 各取所需；V 尺度每存储 tile 一个数组（N_st 交 MAE_ENG 设计者）', 13, 'start', GREY, 600)
    assert y + 40 <= s.h
    s.save('FIG-DORG-DDR-ACT.svg', date=DATE)


if __name__ == '__main__':
    fig_segment()
    fig_split_t()
    fig_split_m()
    fig_split_k()
    fig_ddr_std()
    fig_ddr_col()
    fig_ddr_act()
