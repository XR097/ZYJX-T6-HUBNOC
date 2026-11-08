"""MAE 数据整形单元（MAE_DSU，原 MAE_WSU）正式稿的数值小例。Owner: WangYizhao · 2026-11-06（第二版：改名、加两平面合并）
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_mae_dsu.py
输出（figs/）：
  FIG-MAE_DSU-SPLICE     半字合并：同一 k 下相邻两个列块的两个 8 B 半行字落进一个 16 B Wᵀ 列字（按每半字 4 个通道缩画）
  FIG-MAE_DSU-TRANSPOSE  转置：4 × 4 缩小例，列深度优先的列字（m 固定、沿 k）转成 Wᵀ 列字（k 固定、沿 m）
  FIG-MAE_DSU-SIDEBAND   块尺度：4 个 E8M0 → e_max 与 Δ_m，打成 32 B 旁带行
  FIG-MAE_DSU-TWOPLANE   两平面合并：DDR 里 key 7 的 hi 列字（地址 A）、lo 列字（地址 B）、尺度（地址 C）→ L1 同一记录相邻地址
连接图 FIG-MAE_DSU-CONN 在 draw_mae_conn.py（MAE 组统一外框）。
脚本断言：合并出的码序 = 两个半字按序；转置后 O[j][m] == I[m][j]；2^e_m == 2^e_max / 2^Δ_m；
          两平面合并后每个码的字节值不变、只改地址，记录内顺序 hi → lo → 尺度且相邻。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fig_f5_post import SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, C_KEEP, C_LO, C_OFF, C_HI, C_SIDE  # noqa: E402

# ---- 半字合并（缩画：每个半行字 4 个通道，实际 16）----
K_ROW = 5
HALF_A = [(K_ROW, m) for m in range(0, 4)]       # 列块 2b 里核 c 的半行字：m0–m3（实际 m0–m15）
HALF_B = [(K_ROW, m) for m in range(4, 8)]       # 列块 2b+1 里核 c 的半行字：m4–m7（实际 m16–m31）
WT_WORD = HALF_A + HALF_B                        # Wᵀ 列字：k 固定、沿 m
assert [m for _, m in WT_WORD] == list(range(8)) and all(k == K_ROW for k, _ in WT_WORD)

# ---- 转置（4 × 4）----
N = 4
W = [[(k, m) for m in range(N)] for k in range(N)]           # W[k][m]
IN_WORDS = [[W[k][m] for k in range(N)] for m in range(N)]   # 列深度优先：字 m = (W[0][m] … W[3][m])
OUT_WORDS = [[IN_WORDS[m][j] for m in range(N)] for j in range(N)]  # Wᵀ 列字 j = k 固定、沿 m
for j in range(N):
    for m in range(N):
        assert OUT_WORDS[j][m] == (j, m) == IN_WORDS[m][j]

# ---- 块尺度 ----
E = [5, 2, 7, 4]
E_MAX = max(E)
DELTA = [E_MAX - e for e in E]
assert DELTA == [2, 5, 0, 3] and all(2.0 ** e == 2.0 ** E_MAX / 2.0 ** d for e, d in zip(E, DELTA))
assert all(0 <= d < 16 for d in DELTA)           # 4 bit 字段

# ---- 两平面合并（缩画：每个平面列字 4 个码，实际 128 个码 = 64 B）----
KEY = 7
HI = [0x3, 0xA, 0x5, 0xC]                        # key 7 的 hi 4 bit 码 h（DDR 地址 A）
LO = [0x7, 0x1, 0xE, 0x4]                        # key 7 的 lo 4 bit 码 ℓ（DDR 地址 B）
SCALE = [0x79]                                   # E8M0 尺度（DDR 地址 C；实际 4 个，4 B）——不进记录，落 S 类
DDR = {'A': list(HI), 'B': list(LO), 'C': list(SCALE)}
# 合并（平面分开的记录级，用户 11-06）：按搬运引擎给的目的地址把 hi 字、lo 字落进同一记录相邻位置（偏移以"码"为单位缩画）
SEGS = [('hi', 'A'), ('lo', 'B')]
RECORD, OFFS = [], {}
for name, src in SEGS:
    OFFS[name] = len(RECORD)
    RECORD.extend(DDR[src])
S_ROW = list(DDR['C'])                             # 尺度行另落 S 类
assert RECORD[OFFS['hi']:OFFS['hi'] + 4] == HI and RECORD[OFFS['lo']:OFFS['lo'] + 4] == LO
assert SCALE not in (RECORD[i:i + 1] for i in range(len(RECORD))) and S_ROW == SCALE
assert DDR == {'A': HI, 'B': LO, 'C': SCALE}      # 源字节不变
assert OFFS == {'hi': 0, 'lo': 4}                  # hi → lo 相邻、无空隙；尺度不在记录内
assert all(0 <= v < 16 for v in HI + LO)          # 每个码仍是 4 bit，未交织、未按 8 bit 打包
# 数值等价 MXINT8：c = 16h + ℓ（h 按 4 bit 补码）
C8 = [16 * (h - 16 if h >= 8 else h) + l for h, l in zip(HI, LO)]
assert all(-128 <= c < 128 for c in C8)
# 实际字节数：记录 128 B = 4 + 4 个存储字，32 B 对齐；尺度 4 B 在 S 类
assert 128 * 4 // 8 + 128 * 4 // 8 == 128 and 128 % 32 == 0 and 128 // 32 == 4


def cell_code(s, x, y, w, h, k, m, fill):
    s.cell(x, y, w, h, f'W[{k},{m}]', fill=fill, size=11)


def fig_splice():
    cw, ch = 74, 34
    x0, y0 = 150, 60
    s = SvgF5(1000, 340)
    s.rich(x0 - 14, y0 - 30, f'k = {K_ROW} 的一行', 14, 'end')
    # 上排：两个单元各自的半行字（核 c 那一份）
    s.rich(x0 + 2 * cw, y0 - 30, '列块 2b 的单元 · 核 c 的 8 B 半行字', 12, 'middle', GREY, 600)
    s.rich(x0 + 4 * cw + 60 + 2 * cw, y0 - 30, '列块 2b+1 的单元 · 核 c 的 8 B 半行字', 12, 'middle', GREY, 600)
    for i, (k, m) in enumerate(HALF_A):
        cell_code(s, x0 + i * cw, y0, cw, ch, k, m, C_KEEP)
    xb = x0 + 4 * cw + 60
    for i, (k, m) in enumerate(HALF_B):
        cell_code(s, xb + i * cw, y0, cw, ch, k, m, C_LO)
    # 下排：合并成的 Wᵀ 列字
    y1 = y0 + 120
    s.rich(x0 - 14, y1 + ch / 2 + 5, 'Wᵀ 列字', 14, 'end')
    for i, (k, m) in enumerate(WT_WORD):
        cell_code(s, x0 + i * cw, y1, cw, ch, k, m, C_KEEP if i < 4 else C_LO)
    s.rich(x0 + 2 * cw, y1 + ch + 18, '前半：来自列块 2b', 12, 'middle', GREY, 600)
    s.rich(x0 + 6 * cw, y1 + ch + 18, '后半：来自列块 2b+1', 12, 'middle', GREY, 600)
    s.line([(x0 + 2 * cw, y0 + ch + 4), (x0 + 2 * cw, y1 - 4)], sw=1.3)
    s.line([(xb + 2 * cw, y0 + ch + 4), (x0 + 6 * cw, y1 - 4)], sw=1.3)
    y = y1 + 84
    s.red(x0, y, '半字合并：只改落地地址，不产生新字节', 14)
    s.rich(x0, y + 24, '实际每半行字 16 个输出通道（8 B），一个 Wᵀ 列字 32 个通道（16 B）；两个半字落进训练核 L1 同一个列字的两半', 13, 'start', NAVY, 600)
    assert y + 40 <= s.h
    s.save('FIG-MAE_DSU-SPLICE.svg', date='2026-11-06')


def fig_transpose():
    cw, ch = 70, 32
    x0, y0 = 170, 60
    s = SvgF5(1000, 110 + N * (ch + 8) + 90)
    s.rich(x0 + 2 * cw, y0 - 30, '输入：列深度优先的列字（m 固定、沿 k）', 12, 'middle', GREY, 600)
    xo = x0 + N * cw + 250
    s.rich(xo + 2 * cw, y0 - 30, '输出：Wᵀ 列字（k 固定、沿 m）', 12, 'middle', GREY, 600)
    for m in range(N):
        y = y0 + m * (ch + 8)
        s.rich(x0 - 14, y + ch / 2 + 5, f'列字 m={m}', 13, 'end')
        for i, (k, mm) in enumerate(IN_WORDS[m]):
            cell_code(s, x0 + i * cw, y, cw, ch, k, mm, C_OFF if (k + mm) % 2 else 'white')
    for j in range(N):
        y = y0 + j * (ch + 8)
        s.rich(xo - 14, y + ch / 2 + 5, f'Wᵀ 列字 k={j}', 13, 'end')
        for i, (k, mm) in enumerate(OUT_WORDS[j]):
            cell_code(s, xo + i * cw, y, cw, ch, k, mm, C_OFF if (k + mm) % 2 else 'white')
    ymid = y0 + N * (ch + 8) / 2 - 4
    s.line([(x0 + N * cw + 10, ymid), (xo - 120, ymid)], sw=1.6)
    s.rich((x0 + N * cw + 10 + xo - 120) / 2, ymid - 10, '攒齐后整块转置', 12, 'middle', NAVY, 600)
    y = y0 + N * (ch + 8) + 20
    s.red(x0, y, 'Wᵀ[m, 32s+j] = W[32s+j, m]：只改位置，码不变', 14)
    s.rich(x0, y + 24, '实际一个子段 = 32 列 × L_DSU 个 k，每 32 个 k 出一块（32 个列字 + 旁带行 = 544 B）', 13, 'start', NAVY, 600)
    assert y + 40 <= s.h
    s.save('FIG-MAE_DSU-TRANSPOSE.svg', date='2026-11-06')


def fig_sideband():
    cw, ch = 90, 34
    x0, y0 = 170, 60
    s = SvgF5(1000, 330)
    s.rich(x0 - 14, y0 + ch / 2 + 5, 'E8M0 指数 e_m', 14, 'end')
    for i, e in enumerate(E):
        s.cell(x0 + i * cw, y0, cw, ch, f'm{i}: {e}', fill=C_OFF, size=12)
    y1 = y0 + ch + 16
    s.rich(x0 - 14, y1 + ch / 2 + 5, 'Δ_m = e_max − e_m', 14, 'end')
    for i, d in enumerate(DELTA):
        s.cell(x0 + i * cw, y1, cw, ch, f'{d}', fill=C_KEEP if d == 0 else C_LO, size=12)
    s.cell(x0 + 4 * cw + 30, y0, 150, ch, f'e_max = {E_MAX}', fill=C_KEEP, size=12)
    # 旁带行字节编排
    y2 = y1 + ch + 50
    s.rich(x0 - 14, y2 + 18, '旁带行 32 B', 14, 'end')
    s.cell(x0, y2, 60, 34, '1 B e_max', fill=C_KEEP, size=11)
    s.cell(x0 + 60, y2, 16 * 20, 34, '16 B：32 个 Δ_m，各 4 bit', fill=C_LO, size=11)
    s.cell(x0 + 60 + 16 * 20, y2, 15 * 20, 34, '15 B 保留 / 标志', fill='white', size=11)
    y = y2 + 70
    s.red(x0, y, '2^e_m = 2^e_max / 2^Δ_m，无损', 14)
    s.rich(x0, y + 24, '实际每块 32 个输出通道；lo 块复用同块 hi 的 e_max 与 Δ_m；消费侧把 Δ_m 折进道级指数偏移', 13, 'start', NAVY, 600)
    assert y + 40 <= s.h
    s.save('FIG-MAE_DSU-SIDEBAND.svg', date='2026-11-06')


def fig_twoplane():
    cw, ch = 66, 36
    sw = 110                                       # 尺度格宽
    s = SvgF5(1000, 370)
    # 上排：DDR 三处
    y0 = 78
    xa, xb, xc = 130, 470, 810
    s.rich(xa - 14, y0 + ch / 2, 'DDR', 15, 'end')
    s.rich(xa + 2 * cw, y0 - 30, f'地址 A：key {KEY} 的 hi 列字', 12, 'middle', GREY, 600)
    s.rich(xb + 2 * cw, y0 - 30, f'地址 B：key {KEY} 的 lo 列字', 12, 'middle', GREY, 600)
    s.rich(xc + sw / 2, y0 - 30, '地址 C：尺度（另落 S 类）', 12, 'middle', GREY, 600)
    for i, v in enumerate(DDR['A']):
        s.cell(xa + i * cw, y0, cw, ch, f'h{i}=0x{v:X}', fill=C_HI, size=12)
    for i, v in enumerate(DDR['B']):
        s.cell(xb + i * cw, y0, cw, ch, f'ℓ{i}=0x{v:X}', fill=C_LO, size=12)
    s.cell(xc, y0, sw, ch, f'E8M0 0x{SCALE[0]:X}', fill=C_SIDE, size=12)
    # 下排：L1 全码区的一条记录（相邻）
    y1 = y0 + 130
    xr = 130
    s.rich(xr - 14, y1 + ch / 2, 'L1 记录', 15, 'end')
    seg_x = {}
    for name, src in SEGS:
        off = OFFS[name]
        seg_x[name] = xr + off * cw
        vals = RECORD[off:off + len(DDR[src])]
        if name == 'hi':
            for i, v in enumerate(vals):
                s.cell(xr + (off + i) * cw, y1, cw, ch, f'h{i}=0x{v:X}', fill=C_HI, size=12)
        else:
            for i, v in enumerate(vals):
                s.cell(xr + (off + i) * cw, y1, cw, ch, f'ℓ{i}=0x{v:X}', fill=C_LO, size=12)
    s.rich(seg_x['hi'] + 2 * cw, y1 + ch + 18, 'hi 字（4 个存储字）', 12, 'middle', GREY, 600)
    s.rich(seg_x['lo'] + 2 * cw, y1 + ch + 18, 'lo 字（4 个存储字）', 12, 'middle', GREY, 600)
    # S 类的尺度行（不在记录内）
    xs_row = xr + 9 * cw
    s.rich(xs_row - 14, y1 + ch / 2, 'S 类', 15, 'end')
    s.cell(xs_row, y1, sw, ch, f'E8M0 0x{S_ROW[0]:X}', fill=C_SIDE, size=12)
    s.rich(xs_row + sw / 2, y1 + ch + 18, '尺度行', 12, 'middle', GREY, 600)
    # 箭头：每段从 DDR 源到落点
    s.line([(xa + 2 * cw, y0 + ch + 4), (seg_x['hi'] + 2 * cw, y1 - 4)], sw=1.3)
    s.line([(xb + 2 * cw, y0 + ch + 4), (seg_x['lo'] + 2 * cw, y1 - 4)], sw=1.3)
    s.line([(xc + sw / 2, y0 + ch + 4), (xs_row + sw / 2, y1 - 4)], sw=1.3)
    y = y1 + ch + 62
    s.red(xr, y, '字节不变，只改地址', 14)
    s.red(xr + 300, y, '平面分开，不交织', 14)
    s.rich(xr, y + 28, '实际 head_dim 128：记录 = 64 B + 64 B = 128 B（4 + 4 个存储字，32 B 对齐）；尺度 4 B 落 S 类，与粗算共用', 13, 'start', NAVY, 600)
    assert y + 44 <= s.h
    s.save('FIG-MAE_DSU-TWOPLANE.svg', date='2026-11-06')


if __name__ == '__main__':
    fig_splice()
    fig_transpose()
    fig_sideband()
    fig_twoplane()
