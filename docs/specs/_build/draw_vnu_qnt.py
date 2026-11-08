"""VNU 量化单元（QNT）需求篇（11-04 重写稿）的七张图。Owner: WangYizhao · 2026-11-04
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_vnu_qnt.py [--md]
输出（figs/）：
  FIG-VNU_QNT-CONN            对外连接：画在 VNU 组框内
  FIG-VNU_QNT-MX-ENCODE       按组量化编码：8 个元素一组求 E8M0，编码成 E2M3（含 RNE 中点、饱和、全零组）
  FIG-VNU_QNT-AMAX-SPLIT      一组跨 2 核：部分 amax → CRU 取最大 → 共同尺度；对照各用本核尺度
  FIG-VNU_QNT-PLANE-BITSPLIT  MXINT8 码按位拆 hi / lo，验算还原式
  FIG-VNU_QNT-PLANE-RESIDUAL  P′ 两平面：X1 = MX(P′)，X2 = MX(P′ − X1)，共用基准，全零第二平面组标无效
  FIG-VNU_QNT-KEEP-PACK       按 SEL 交回的保留码压紧：组尺度只看保留通道，段头 + F 标志 + 值区
  FIG-VNU_QNT-DECODE          K 存储码还原：全码与只 hi 两种
脚本断言：各图数值由本脚本按正文规则算出（MXFP6 E2M3 组尺度取最大指数、RNE、饱和；MXINT8 拆 hi / lo）。
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize, SvgF5  # noqa: E402
from svgkit_num import GREY, C_OFF, C_KEEP, C_HI, C_LO, C_LEFT, C_SIDE  # noqa: E402

OUT = HERE.parent


# ---------------- MXFP6 E2M3 参照量化（正文 §3.1） ----------------
def e2m3_grid():
    """E2M3 全部非负可表示值：1 符号 + 2 指数（偏置 1）+ 3 尾数；最大 7.5。"""
    vals = [m / 8 for m in range(8)]                                   # 非规格化 0 … 0.875
    for e in (1, 2, 3):
        vals += [(1 + m / 8) * 2 ** (e - 1) for m in range(8)]
    return sorted(set(vals))


GRID = e2m3_grid()
assert GRID[-1] == 7.5 and len(GRID) == 32


def mant_even(v):
    """可表示值 v 的尾数码是否为偶数（RNE 平局时取偶）。"""
    if v < 1:
        return int(v * 8) % 2 == 0
    e = math.floor(math.log2(v))
    return int(round((v / 2 ** e - 1) * 8)) % 2 == 0


def e2m3_rne(t):
    """t 已除以组尺度；返回 (量化值, 是否饱和)。"""
    a = abs(t)
    if a >= 7.5:
        return math.copysign(7.5, t) if a > 0 else 0.0, a > 7.5
    lo = max(g for g in GRID if g <= a)
    hi = min(g for g in GRID if g >= a)
    if lo == hi:
        q = lo
    elif a - lo < hi - a:
        q = lo
    elif hi - a < a - lo:
        q = hi
    else:
        q = lo if mant_even(lo) else hi                               # 恰在中点：取尾数为偶者
    return math.copysign(q, t) if q else 0.0, False


def mx_e2m3(xs):
    """一组 MXFP6 E2M3：尺度指数 = floor(log2 amax) − 2（E2M3 最大指数为 2）。全零组返回 None 尺度。"""
    amax = max(abs(x) for x in xs)
    if amax == 0:
        return None, [0.0] * len(xs), [False] * len(xs)
    e = math.floor(math.log2(amax)) - 2
    out = [e2m3_rne(x / 2 ** e) for x in xs]
    return e, [q for q, _ in out], [s for _, s in out]


# 图 2：MX-ENCODE
ENC = [31.2, -4.24, 1.6, 10.5, -0.12, 12.4, 0.0, 21.2]
ENC_E, ENC_Q, ENC_SAT = mx_e2m3(ENC)
assert ENC_E == 2                                                     # amax 31.2 → floor(log2) = 4 → 尺度 2^2
assert ENC_Q == [7.5, -1.0, 0.375, 2.5, 0.0, 3.0, 0.0, 5.5]
assert ENC_SAT == [True] + [False] * 7                                # 31.2 / 4 = 7.8 > 7.5，饱和
assert 10.5 / 4 == 2.625 and ENC_Q[3] == 2.5                          # 2.625 在 2.5 与 2.75 正中，取尾数偶的 2.5
ZERO_E, ZERO_Q, _ = mx_e2m3([0.0] * 8)
assert ZERO_E is None and ZERO_Q == [0.0] * 8

# 图 3：AMAX-SPLIT（一组 8 个通道，核 0 持 0–3、核 1 持 4–7）
SPLIT = [1.2, -0.7, 2.9, 0.3, -9.6, 4.1, 0.5, -2.2]
PART = [max(abs(x) for x in SPLIT[:4]), max(abs(x) for x in SPLIT[4:])]
assert PART == [2.9, 9.6]
COMMON = max(PART)
SPLIT_E, SPLIT_Q, _ = mx_e2m3(SPLIT)                                  # 共同尺度 = 整组一起量化
assert SPLIT_E == math.floor(math.log2(COMMON)) - 2 == 1
OWN0_E, OWN0_Q, _ = mx_e2m3(SPLIT[:4])                                # 核 0 只用本核尺度
assert OWN0_E == -1 and OWN0_Q != SPLIT_Q[:4]


# ---------------- MXINT8 hi / lo 拆分（正文 §3.2、§3.5） ----------------
def split_hilo(c):
    h = c // 16                                                       # 算术右移：有符号 4 bit
    l = c - 16 * h                                                    # 0 … 15
    return h, l, l ^ 8


CODES = [127, -127, -75, 0]
HILO = [split_hilo(c) for c in CODES]
for c, (h, l, ls) in zip(CODES, HILO):
    assert -8 <= h <= 7 and 0 <= l <= 15
    assert (2 * h + 1) * 8 + ((ls ^ 8) - 8) == c                     # 还原式
assert [(h, ls) for h, _, ls in HILO] == [(7, 7), (-8, 9), (-5, 13), (0, 8)]
HI_APPROX = [(2 * h + 1) * 8 for h, _, _ in HILO]
assert HI_APPROX == [120, -120, -72, 8]
DEC_E = -4                                                            # 示例组尺度 2^-4
DEC_FULL = [c * 2 ** DEC_E for c in CODES]
DEC_HI = [a * 2 ** DEC_E for a in HI_APPROX]
assert DEC_FULL[0] == 7.9375 and DEC_HI[0] == 7.5 and DEC_HI[3] == 0.5

# ---------------- P′ 两平面（正文 §3.2） ----------------
PG = [[0.83, 0.21, 0.052, 0.4], [0.0625, 0.125, 0.25, 0.5]]           # 2 组，每组 4 个（实际 32 个录取 key）
PLANES = []
for g in PG:
    e1, x1, _ = mx_e2m3(g)
    v1 = [q * 2 ** e1 for q in x1]
    r = [a - b for a, b in zip(g, v1)]
    e2, x2, _ = mx_e2m3(r) if any(abs(v) > 1e-15 for v in r) else (None, [0.0] * 4, None)
    v2 = [q * 2 ** e2 for q in x2] if e2 is not None else [0.0] * 4
    PLANES.append(dict(e1=e1, v1=v1, r=r, e2=e2, v2=v2))
assert PLANES[0]['e1'] == -3 and PLANES[1]['e1'] == -3
assert PLANES[1]['e2'] is None                                         # 组 1 恰好可表示，第二平面全零 → 无效
assert PLANES[0]['e2'] == -8
E_BASE = max(p[k] for p in PLANES for k in ('e1', 'e2') if p[k] is not None)
assert E_BASE == -3
for p in PLANES:
    for k in ('e1', 'e2'):
        assert p[k] is None or p[k] <= E_BASE
# 两平面之和比单平面更接近 P′
err1 = max(abs(a - b) for g, p in zip(PG, PLANES) for a, b in zip(g, p['v1']))
err2 = max(abs(a - b - c) for g, p in zip(PG, PLANES) for a, b, c in zip(g, p['v1'], p['v2']))
assert err2 < err1 / 8

# ---------------- 按保留码压紧（正文 §3.3） ----------------
KX = [0.9, -3.7, 0.2, 1.4, -0.05, 1.85, 0.6, -1.1]
KCODE = ['C', 'Z', 'Z', 'F', 'Z', 'F', 'C', 'C']                      # SEL 交回的保留码
KEPT = [i for i, c in enumerate(KCODE) if c != 'Z']
KK_E, KK_Q, _ = mx_e2m3([KX[i] for i in KEPT])
ALL_E, _, _ = mx_e2m3(KX)
assert KK_E == -2 and ALL_E == -1                                     # 最大幅值通道 1 被判 Z，组尺度变小一级
assert KK_Q == [3.5, 5.5, 7.5, 2.5, -4.5]
KEEP_BITS = ''.join('0' if c == 'Z' else '1' for c in KCODE)
F_BITS = ''.join('1' if KCODE[i] == 'F' else '0' for i in KEPT)
assert KEEP_BITS == '10010111' and F_BITS == '01100'


def seg_bytes(k_s, w=6):
    return 5 + math.ceil(k_s / 8) + math.ceil(w * k_s / 8)


assert seg_bytes(20) == 23 and seg_bytes(20, 8) == 28 and seg_bytes(32) == 33


def fmt(v):
    s = f'{v:.6f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


# ---------------- 图 1：对外连接 ----------------


# ---------------- 图 2：按组量化编码 ----------------
def fig_mx_encode():
    s = SvgF5(1180, 470)
    x0, cw, ch = 250, 110, 42
    for i in range(8):
        s.rich(x0 + i * cw + (cw - 10) / 2, 28, f'元素 {i}', 15, 'middle', GREY, 600)
    rows = [('x（BF16）', [fmt(v) for v in ENC], ['white'] * 8),
            ('x / 2^{2}', [fmt(v / 2 ** ENC_E) for v in ENC], ['white'] * 8),
            ('E2M3 值', [fmt(q) for q in ENC_Q], [C_HI if ENC_SAT[i] else (C_LEFT if i == 3 else C_KEEP) for i in range(8)]),
            ('还原 = 值 × 2^{2}', [fmt(q * 2 ** ENC_E) for q in ENC_Q], ['white'] * 8)]
    for r, (lab, vals, fills) in enumerate(rows):
        y = 48 + r * 66
        s.rich(x0 - 16, y + ch / 2, lab, 15, 'end')
        for i in range(8):
            s.cell(x0 + i * cw, y, cw - 10, ch, vals[i], fill=fills[i], size=15)
    s.red(x0 + (cw - 10) / 2, 48 + 2 * 66 - 12, '7.8 > 7.5 饱和', 14, 'middle')
    s.red(x0 + 3 * cw + (cw - 10) / 2, 48 + 2 * 66 - 12, '2.625 中点取偶', 14, 'middle')
    s.note(x0, 312, '组内最大幅值 31.2，⌊log_{2} 31.2⌋ = 4；E2M3 最大指数为 2，组尺度 E8M0 = 2^{4 − 2} = 2^{2}', 15)
    y = 356
    s.rich(x0 - 16, y + ch / 2, '全零组', 15, 'end')
    for i in range(8):
        s.cell(x0 + i * cw, y, cw - 10, ch, '0', fill=C_OFF, size=15)
    s.note(x0, y + ch + 24, '尺度取合同约定值，码全 0，不产生 NaN', 15)
    s.save('FIG-VNU_QNT-MX-ENCODE.svg')


# ---------------- 图 3：跨核 amax ----------------
def fig_amax_split():
    s = SvgF5(1240, 420)
    x0, cw, ch, gap = 270, 104, 42, 40
    xs = [x0 + i * cw + (gap if i >= 4 else 0) for i in range(8)]
    s.rich(xs[0] + 2 * cw - 5, 24, '核 0（通道 0–3）', 16, 'middle')
    s.rich(xs[4] + 2 * cw - 5, 24, '核 1（通道 4–7）', 16, 'middle')
    q_own = OWN0_Q + [None] * 4
    rows = [('x', [fmt(v) for v in SPLIT], ['white'] * 8),
            ('共同尺度 2^{1} 下的 E2M3', [fmt(q) for q in SPLIT_Q], [C_KEEP] * 8),
            ('核 0 只用本核尺度 2^{−1}', [fmt(q) if q is not None else '—' for q in q_own], [C_HI] * 4 + [C_OFF] * 4)]
    for r, (lab, vals, fills) in enumerate(rows):
        y = 48 + r * 60
        s.rich(x0 - 16, y + ch / 2, lab, 15, 'end')
        for i in range(8):
            s.cell(xs[i], y, cw - 10, ch, vals[i], fill=fills[i], size=15)
    y = 250
    s.cell(xs[0], y, 4 * cw - 10, ch, f'部分 amax = {fmt(PART[0])}', fill=C_SIDE, size=15)
    s.cell(xs[4], y, 4 * cw - 10, ch, f'部分 amax = {fmt(PART[1])}', fill=C_SIDE, size=15)
    s.rich(x0 - 16, y + ch / 2, '交 CRU', 15, 'end')
    s.cell(xs[1], y + 80, xs[6] + cw - 10 - xs[1], ch, f'CRU 取最大 {fmt(COMMON)} → 回送两核 → 共同尺度 2^{{{SPLIT_E}}}', fill=C_LEFT, size=15)
    for cx in (xs[0] + 2 * cw - 5, xs[4] + 2 * cw - 5):
        s.line([(cx, y + ch), (cx, y + 80)])
    s.red(xs[0] + 2 * cw - 5, 48 + 2 * 60 + ch + 14, '与共同尺度下的码不同，不能拼成一组', 14, 'middle')
    s.save('FIG-VNU_QNT-AMAX-SPLIT.svg')


# ---------------- 图 4：hi / lo 按位拆分 ----------------
def fig_bitsplit():
    s = SvgF5(1100, 400)
    x0, cw, ch = 330, 170, 42
    for i, c in enumerate(CODES):
        s.rich(x0 + i * cw + (cw - 12) / 2, 28, f'码 {i}', 15, 'middle', GREY, 600)
    rows = [('MXINT8 码 c', [str(c) for c in CODES], ['white'] * 4),
            ('hi 平面：h = ⌊c / 16⌋', [str(h) for h, _, _ in HILO], [C_HI] * 4),
            ('ℓ = c − 16h', [str(l) for _, l, _ in HILO], ['white'] * 4),
            ('lo 平面：存 ℓ ⊕ 8', [str(ls) for _, _, ls in HILO], [C_LO] * 4),
            ('(2h + 1)·8 + (ℓ − 8)', [str((2 * h + 1) * 8 + (l - 8)) for h, l, _ in HILO], [C_KEEP] * 4)]
    for r, (lab, vals, fills) in enumerate(rows):
        y = 48 + r * 58
        s.rich(x0 - 16, y + ch / 2, lab, 15, 'end')
        for i in range(4):
            s.cell(x0 + i * cw, y, cw - 12, ch, vals[i], fill=fills[i], size=15)
    s.note(x0, 48 + 5 * 58 + 6, 'hi、lo 各 4 bit，两平面共用组尺度；最后一行等于 c，还原无损', 15)
    s.save('FIG-VNU_QNT-PLANE-BITSPLIT.svg')


# ---------------- 图 5：P′ 两平面 ----------------
def fig_residual():
    s = SvgF5(1240, 440)
    x0, cw, ch, gap = 250, 116, 42, 40
    xs = [x0 + i * cw + (gap if i >= 4 else 0) for i in range(8)]
    s.rich(xs[0] + 2 * cw - 5, 24, '组 0（录取 key 0–3）', 16, 'middle')
    s.rich(xs[4] + 2 * cw - 5, 24, '组 1（录取 key 4–7）', 16, 'middle')
    P = PG[0] + PG[1]
    V1 = PLANES[0]['v1'] + PLANES[1]['v1']
    R = PLANES[0]['r'] + PLANES[1]['r']
    V2 = PLANES[0]['v2'] + PLANES[1]['v2']
    rows = [('P′', [fmt(v) for v in P], ['white'] * 8),
            ('X_{1} = MX(P′)', [fmt(v) for v in V1], [C_HI] * 8),
            ('P′ − X_{1}', [fmt(v) for v in R], ['white'] * 8),
            ('X_{2} = MX(P′ − X_{1})', [fmt(v) for v in V2], [C_LO] * 4 + [C_OFF] * 4),
            ('X_{1} + X_{2}', [fmt(a + b) for a, b in zip(V1, V2)], [C_KEEP] * 8)]
    for r, (lab, vals, fills) in enumerate(rows):
        y = 48 + r * 58
        s.rich(x0 - 16, y + ch / 2, lab, 14, 'end')
        for i in range(8):
            s.cell(xs[i], y, cw - 10, ch, vals[i], fill=fills[i], size=14)
    y = 48 + 5 * 58 + 4
    s.note(x0, y, f'组尺度指数：组 0 的 X_{{1}} 为 {PLANES[0]["e1"]}、X_{{2}} 为 {PLANES[0]["e2"]}；'
                  f'组 1 的 X_{{1}} 为 {PLANES[1]["e1"]}，X_{{2}} 全零、标无效', 15)
    s.note(x0, y + 34, f'共用基准 = 非空组指数的最大值 = {E_BASE}，不小于各组指数', 15)
    s.save('FIG-VNU_QNT-PLANE-RESIDUAL.svg')


# ---------------- 图 6：按保留码压紧 ----------------
def fig_keep_pack():
    s = SvgF5(1240, 500)
    x0, cw, ch = 250, 110, 42
    fill = {'F': C_HI, 'C': C_LO, 'Z': C_OFF}
    for i in range(8):
        s.rich(x0 + i * cw + (cw - 10) / 2, 28, f'通道 {i}', 15, 'middle', GREY, 600)
    rows = [('x', [fmt(v) for v in KX], ['white'] * 8),
            ('SEL 交回的保留码', KCODE, [fill[c] for c in KCODE])]
    for r, (lab, vals, fills) in enumerate(rows):
        y = 48 + r * 58
        s.rich(x0 - 16, y + ch / 2, lab, 15, 'end')
        for i in range(8):
            s.cell(x0 + i * cw, y, cw - 10, ch, vals[i], fill=fills[i], size=15)
    s.note(x0, 178, f'只看保留通道：最大幅值 1.85 → 组尺度 2^{{{KK_E}}}（若把通道 1 的 3.7 算进来会是 2^{{{ALL_E}}}）', 15)
    s.red(x0 + 1 * cw + (cw - 10) / 2, 6 + 48 + 58 + ch + 4, '判 Z，不进尺度', 14, 'middle')
    # 压紧后的一段
    y = 230
    s.rich(x0 - 16, y + ch / 2, '保留通道的 E2M3', 15, 'end')
    for j, (i, q) in enumerate(zip(KEPT, KK_Q)):
        s.cell(x0 + j * cw, y, cw - 10, ch, f'#{i}：{fmt(q)}', fill=fill[KCODE[i]], size=15)
    y = 320
    s.rich(x0 - 16, y + ch / 2, '写出的一段', 15, 'end')
    fields = [('段尺度 E8M0', 150, C_SIDE), ('keep 位图 ' + KEEP_BITS, 230, C_SIDE),
              ('F 标志 ' + F_BITS, 170, C_LEFT), ('值区：5 × 6 bit', 250, C_KEEP)]
    xx = x0
    for lab, w, fl in fields:
        s.cell(xx, y, w - 8, ch, lab, fill=fl, size=14)
        xx += w
    s.note(x0, y + ch + 26, '段头 = 段尺度 + keep 位图；F 标志写在值之前（每个保留通道 1 bit，F 为 1）', 15)
    s.note(x0, y + ch + 58, '实际一段 32 个通道：段长 5 + ⌈k_{s}/8⌉ + ⌈w·k_{s}/8⌉ B，k_{s} = 20、w = 6 时 23 B', 15)
    s.note(x0, y + ch + 90, '位序与字段落位归数据组织篇', 15)
    s.save('FIG-VNU_QNT-KEEP-PACK.svg')


# ---------------- 图 7：解码 ----------------
def fig_decode():
    s = SvgF5(1100, 320)
    x0, cw, ch = 330, 170, 42
    for i in range(4):
        s.rich(x0 + i * cw + (cw - 12) / 2, 28, f'码 {i}', 15, 'middle', GREY, 600)
    rows = [('MXINT8 码 c', [str(c) for c in CODES], ['white'] * 4),
            ('全码还原 c × 2^{−4}', [fmt(v) for v in DEC_FULL], [C_KEEP] * 4),
            ('只 hi：(2h + 1)·8 × 2^{−4}', [fmt(v) for v in DEC_HI], [C_HI] * 4),
            ('只 hi 的误差', [fmt(a - b) for a, b in zip(DEC_HI, DEC_FULL)], ['white'] * 4)]
    for r, (lab, vals, fills) in enumerate(rows):
        y = 48 + r * 58
        s.rich(x0 - 16, y + ch / 2, lab, 15, 'end')
        for i in range(4):
            s.cell(x0 + i * cw, y, cw - 12, ch, vals[i], fill=fills[i], size=15)
    s.red(x0 + 3 * cw + (cw - 12) / 2, 48 + 3 * 58 + 56, '只 hi 时 0 变成 0.5，偏半步', 14, 'middle')
    s.save('FIG-VNU_QNT-DECODE.svg')


def md():
    print('MX-ENCODE q:', ENC_Q, 'e', ENC_E)
    print('SPLIT common', SPLIT_Q, 'own0', OWN0_Q)
    print('PLANES', PLANES, 'base', E_BASE)
    print('KEEP', KK_E, KK_Q)


if __name__ == '__main__':
    fig_mx_encode()
    fig_amax_split()
    fig_bitsplit()
    fig_residual()
    fig_keep_pack()
    fig_decode()
    if '--md' in sys.argv:
        md()
