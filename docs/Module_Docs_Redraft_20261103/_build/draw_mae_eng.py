"""MAE_ENG 篇的数值小例图。Owner: WangYizhao · 2026-11-06
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_mae_eng.py
输出（figs/）：
  FIG-MAE_ENG-ARITH        两级嵌套：行内连续、行间与块间按跨距跳；行尾不满 32 B 用 be；两端字节数相等
  FIG-MAE_ENG-LIST         行号载荷 [2, 5, 6, 11] 与等价位图给出相同源地址；目的端连续压紧
  FIG-MAE_ENG-KHI-GATHER   同一录取列表 [3, 7]：驻留只取 lo 64 B / 重读取 hi + lo 两段经 DSU 拼成 128 B 记录
架构图 FIG-MAE_ENG-ARCH 在 draw_mae_arch.py 的 fig_eng()。
数值全部由脚本算出并断言；改常量要同步正文 MAE_ENG.md §5.2 / §5.3 / §5.4 的图说。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit_num import Svg, NAVY, INK, GREY, C_HI, C_LO, C_KEEP, C_OFF, C_SIDE, C_W  # noqa: E402

DATE = '2026-11-06'
WORD = 32

# ---------------- ARITH：两级嵌套 ----------------
A_BASE, A_ROWB, A_ROWS, A_RSTR, A_BLKS, A_BSTR = 4096, 48, 3, 256, 2, 1024
A_DROW = 64                                            # 目的端：每行一条记录，补到 32 B 边界


def arith_beats():
    out = []                                           # (源地址, 目的地址, 有效字节, 块, 行)
    k = 0
    for b in range(A_BLKS):
        for r in range(A_ROWS):
            row_src = A_BASE + b * A_BSTR + r * A_RSTR
            row_dst = k * A_DROW
            for off in range(0, A_ROWB, WORD):
                out.append((row_src + off, row_dst + off, min(WORD, A_ROWB - off), b, r))
            k += 1
    return out


ARITH = arith_beats()
assert [a for a, *_ in ARITH] == [4096, 4128, 4352, 4384, 4608, 4640, 5120, 5152, 5376, 5408, 5632, 5664]
assert [d for _, d, *_ in ARITH] == list(range(0, 384, 32))
assert sum(v for _, _, v, *_ in ARITH) == A_BLKS * A_ROWS * A_ROWB == 288
assert all(a % WORD == d % WORD for a, d, *_ in ARITH)            # 两端余数相同


def fig_arith():
    s = Svg(1500, 610)
    s.rich(30, 34, f'源端算术生成器：基址 {A_BASE} B，行字节数 {A_ROWB} B，{A_ROWS} 行 × 行跨距 {A_RSTR} B，{A_BLKS} 块 × 块跨距 {A_BSTR} B → 12 拍', 17)
    s.note(30, 66, f'目的端算术生成器：L2 象限 0 字节 0 起，每行一条记录、行跨距 {A_DROW} B（补到 32 B 边界）；两端每拍余数相同', 15)
    cols = [('拍', 60), ('块 i₂', 70), ('行 i₁', 70), ('源地址（B）', 150), ('计算', 300), ('目的地址（B）', 150), ('有效字节 / be', 160)]
    x0, y0, rh = 30, 92, 34
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    for i, (a, d, v, b, r) in enumerate(ARITH):
        y = y0 + (i + 1) * rh
        fill = C_LO if v < WORD else 'white'
        calc = f'{A_BASE} + {b}×{A_BSTR} + {r}×{A_RSTR} + {a - A_BASE - b * A_BSTR - r * A_RSTR}'
        vals = [str(i), str(b), str(r), str(a), calc, str(d), f'{v} B' + ('（be 只选 16 B）' if v < WORD else '')]
        for xx, (_, w), t in zip(xs, cols, vals):
            s.cell(xx, y, w - 6, rh - 4, t, fill=fill, size=13)
    s.red(30, y0 + 13 * rh + 18, '行尾 16 B 用 be 标出；两端有效字节都是 288 B', 15)
    s.save('FIG-MAE_ENG-ARITH.svg', DATE)


# ---------------- LIST：行号与位图等价 ----------------
L_ITEMS, L_STRIDE, L_BASE, L_NBITS = [2, 5, 6, 11], 64, 0x10000, 12
L_BITMAP = sum(1 << n for n in L_ITEMS)
L_BITS = ''.join('1' if L_BITMAP >> (L_NBITS - 1 - i) & 1 else '0' for i in range(L_NBITS))
assert L_BITS == '100001100100'
FROM_ROWNUM = [L_BASE + n * L_STRIDE + o for n in L_ITEMS for o in range(0, L_STRIDE, WORD)]
FROM_BITMAP = [L_BASE + n * L_STRIDE + o for n in range(L_NBITS) if L_BITMAP >> n & 1 for o in range(0, L_STRIDE, WORD)]
assert FROM_ROWNUM == FROM_BITMAP
assert [hex(a) for a in FROM_ROWNUM] == ['0x10080', '0x100a0', '0x10140', '0x10160', '0x10180', '0x101a0', '0x102c0', '0x102e0']
L_DST = list(range(0, len(FROM_ROWNUM) * WORD, WORD))
assert L_DST[-1] == 224


def fig_list():
    s = Svg(1500, 520)
    s.rich(30, 34, f'列表驱动：外层循环变量换成列表项；地址 = 0x{L_BASE:X} + 项值 × {L_STRIDE} B + 拍内偏移（每项 2 拍）', 17)
    # 行号载荷
    s.rich(30, 80, '行号载荷（每项 3 B）', 15)
    for i, n in enumerate(L_ITEMS):
        s.cell(220 + i * 70, 64, 62, 32, str(n), fill=C_KEEP, size=15)
    # 位图载荷
    s.rich(560, 80, f'位图载荷（{L_NBITS} bit，位 11 在左）', 15)
    for i, ch in enumerate(L_BITS):
        s.cell(820 + i * 46, 64, 40, 32, ch, fill=C_KEEP if ch == '1' else C_OFF, size=15)
    # 展开表
    cols = [('拍', 60), ('项值 n', 90), ('源地址（行号载荷）', 220), ('源地址（位图载荷）', 220), ('目的地址（核 L1 A 类，B）', 260)]
    x0, y0, rh = 30, 120, 36
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    for i, (a, b, d) in enumerate(zip(FROM_ROWNUM, FROM_BITMAP, L_DST)):
        n = L_ITEMS[i // 2]
        y = y0 + (i + 1) * rh
        vals = [str(i), str(n), f'0x{a:X}', f'0x{b:X}', str(d)]
        for xx, (_, w), t in zip(xs, cols, vals):
            s.cell(xx, y, w - 6, rh - 4, t, fill=C_LO if i // 2 % 2 else 'white', size=14)
    s.red(30, y0 + 10 * rh - 4, '两种载荷展开出的地址逐拍相同；计数 = 0 时不发任何拍', 15)
    s.save('FIG-MAE_ENG-LIST.svg', DATE)


# ---------------- KHI-GATHER：驻留 / 重读 ----------------
K_KEYS, K_SEG = [3, 7], 64                       # head_dim 128：每平面每 key 64 B
K_HI, K_LO = 0x100000, 0x200000                  # hi 平面基址 A、lo 平面基址 B（示例）
RES_SRC = [K_LO + k * K_SEG for k in K_KEYS]
RES_DST = [i * K_SEG for i in range(len(K_KEYS))]
RR_SRC = [(K_HI + k * K_SEG, K_LO + k * K_SEG) for k in K_KEYS]
RR_DST = [(i * 2 * K_SEG, i * 2 * K_SEG + K_SEG) for i in range(len(K_KEYS))]
assert RES_SRC == [K_LO + 192, K_LO + 448] and RES_DST == [0, 64]
assert RR_DST == [(0, 64), (128, 192)]
assert sum(2 * K_SEG for _ in K_KEYS) == 256


def fig_khi():
    s = Svg(1500, 520)
    s.rich(30, 34, f'同一录取列表 {K_KEYS}，head_dim 128：每个 key 每平面 {K_SEG} B；A = hi 平面基址 0x{K_HI:X}，B = lo 平面基址 0x{K_LO:X}', 17)
    # 驻留
    s.panel(30, 60, 700, 400, '驻留模式：只取 lo，直通')
    s.note(50, 110, '项字节数 64 B，每项 1 段', 15)
    for i, k in enumerate(K_KEYS):
        y = 140 + i * 70
        s.cell(50, y, 260, 50, f'key {k}：B + {k}×64 = B + {k * K_SEG}', fill=C_LO, size=14)
        s.line([(310, y + 25), (420, y + 25)])
        s.cell(420, y, 280, 50, f'lo 区 {RES_DST[i]}–{RES_DST[i] + K_SEG - 1}', fill=C_LO, size=14)
    s.note(50, 320, 'K hi 已驻留在核 L1（粗算落地区），精算时 hi、lo 两条列道各取一处', 14)
    s.note(50, 350, '目的：核 L1 lo 区，按 key 连续，共 128 B', 14)
    # 重读
    s.panel(760, 60, 710, 400, '重读模式：hi + lo 两段，经 DSU 两平面合并')
    s.note(780, 110, '项字节数 128 B，每项 2 段（两处不连续，展开方式【设计者定】）', 15)
    for i, k in enumerate(K_KEYS):
        y = 140 + i * 110
        h, l = RR_SRC[i]
        d0, d1 = RR_DST[i]
        s.cell(780, y, 220, 44, f'key {k} hi：A + {k * K_SEG}', fill=C_HI, size=14)
        s.cell(780, y + 50, 220, 44, f'key {k} lo：B + {k * K_SEG}', fill=C_LO, size=14)
        s.line([(1000, y + 22), (1090, y + 22)])
        s.line([(1000, y + 72), (1090, y + 72)])
        s.cell(1090, y, 360, 44, f'全码记录 {d0}–{d0 + K_SEG - 1}：hi 4 个存储字', fill=C_HI, size=14)
        s.cell(1090, y + 50, 360, 44, f'全码记录 {d1}–{d1 + K_SEG - 1}：lo 4 个存储字', fill=C_LO, size=14)
    s.note(780, 400, '每 key 一条 128 B 记录，平面分开；E8M0 尺度另段落 S 类', 14)
    s.red(30, 490, 'MAE 只看项字节数、段数与运算字段，不知道是哪种模式', 15)
    s.save('FIG-MAE_ENG-KHI-GATHER.svg', DATE)


# ---------------- QSPLICE：同址异象限，四道并行读时合并（V18-TP-48 / MAE-28） ----------------
Q_T, Q_SEGW, Q_SRC = 4, 2, 4096        # token 数、每段存储字数（L2 段槽）、四个象限共同的象限内起始字节
Q_DSTEP, Q_FULL = 3, 12                # L1：道 q 的目的偏移 = q × 3 个存储字（错开 bank），整条记录槽 12 个存储字
Q_ABANK = [8, 9, 10, 11]               # L1 A 类 4 bank 配置的 bank 列表（字号 j → 第 j mod 4 项）


def qsplice_beats(dstep):
    rows = []                          # 每拍一行：[(源象限内字节, 目的字号, bank)] × 4 道
    for t in range(Q_T):
        for w in range(Q_SEGW):
            row = []
            for q in range(4):
                a = Q_SRC + t * Q_SEGW * WORD + w * WORD
                j = t * Q_FULL + q * dstep + w
                row.append((a, j, Q_ABANK[j % 4]))
            rows.append(row)
    return rows


QS = qsplice_beats(Q_DSTEP)
assert len(QS) == Q_T * Q_SEGW == 8
assert all(len({a for a, _, _ in r}) == 1 for r in QS)            # 同址异象限：四道源地址只差象限位
assert all(len({b for _, _, b in r}) == 4 for r in QS)            # 错开后四道同拍落 4 个不同 bank
assert QS[0] == [(4096, 0, 8), (4096, 3, 11), (4096, 6, 10), (4096, 9, 9)]
assert QS[7][0] == (4096 + 7 * WORD, 37, 9)
QS_BAD = qsplice_beats(Q_SEGW)                                     # 反例：L1 段步长 = 段槽 2 个存储字
assert all(r[0][2] == r[2][2] and r[1][2] == r[3][2] for r in QS_BAD)   # 道 0 / 2、道 1 / 3 每拍撞 bank
assert Q_FULL == 4 * Q_DSTEP and Q_DSTEP % 4 in (1, 3)


def fig_qsplice():
    s = Svg(1500, 600)
    s.rich(30, 34, f'四道并行读时合并：{Q_T} 个 token、每段 {Q_SEGW} 个存储字；四个象限的段都从象限内字节 {Q_SRC} 起（同址异象限）', 17)
    s.note(30, 66, f'道 q 读象限 q：源 = [象限 q][{Q_SRC} + t × 64 + w × 32]；目的 = L1 A 类字 t × {Q_FULL} + q × {Q_DSTEP} + w（q × {Q_DSTEP} 错开 bank）；核掩码 1111 多播', 15)
    cols = [('拍', 70)] + [(f'道 {q}：象限 {q} → L1', 330) for q in range(4)]
    x0, y0, rh = 30, 92, 40
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    for i, row in enumerate(QS):
        y = y0 + (i + 1) * rh
        t = i // Q_SEGW
        s.cell(xs[0], y, cols[0][1] - 6, rh - 4, f'{i}（t{t}）', fill='white', size=13)
        for q, (a, j, b) in enumerate(row):
            s.cell(xs[q + 1], y, cols[q + 1][1] - 6, rh - 4, f'字节 {a} → 字 {j} · bank {b}',
                   fill=C_HI if t % 2 else C_LO, size=13)
    s.note(30, y0 + 9 * rh + 22, f'每拍四道的源地址相同（只差象限位），四道落 4 个不同 bank；token t 的四段在 L1 拼成字 {Q_FULL}t … {Q_FULL}t + {Q_FULL - 1} 的一条记录（每段后留 1 个空字）', 14)
    s.note(30, y0 + 9 * rh + 50, f'反例：目的偏移步长取段槽 {Q_SEGW} 个存储字时，道 0 与道 2、道 1 与道 3 每拍落同一 bank，落地降到 64 B/拍', 14)
    s.red(30, y0 + 9 * rh + 82, '读时合并只是地址几何；错开 bank 由编译链保证', 15)
    s.save('FIG-MAE_ENG-QSPLICE.svg', DATE)


if __name__ == '__main__':
    fig_arith()
    fig_list()
    fig_khi()
    fig_qsplice()
