"""L2 SRAM 需求篇的四张图。Owner: WangYizhao · 2026-11-03；2026-11-05 按传输协议篇定稿同步
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_l2_sram.py [--md]
输出（figs/）：
  架构图由 draw_l2_arch.py 生成。
  FIG-L2_SRAM-MAP-HEAP   一个象限内两堆的行落到哪个 bank、哪个深度（缩小例；11-05 取代 MAP-REGION）
  FIG-L2_SRAM-MAP-RING   环形回绕由 MAE 搬运引擎做：第 k 个存储字地址 = 基址 + (k mod L)，L2 只按每拍地址落字
                         （11-05 夜 V18-TP-27：原"发地址方"改为 MAE 搬运引擎）
  FIG-L2_SRAM-OBJ-ALIGN  ③ 档记录紧挨存放、长度表单独存（11-07 V18-TP-58；11-05 的记录级对齐版退役）
脚本断言：
  MAP-HEAP：地址 [堆 h][象限 q][行 j] → bank = 8q + 4h + (j mod 4)，深度 = j div 4；
            同一堆内各对象互不重叠；堆 0 与堆 1 的 bank 不相交，同拍写堆 1 第 t 行、读堆 0 第 t 行不撞 bank。
  MAP-RING：MAE 搬运引擎算的 5 拍行号 = 基址 + (k mod L)；各拍落点与换算式一致；L2 侧不取模。
  OBJ-ALIGN：记录 17 / 40 / 32 B 从字节 0 起紧挨（起点 0 / 17 / 57），攒满 32 B 写一字、末字带 be；长度表另存；
             任何一行只属于一段（无跨行、无行内偏移）；按（首行号, 长度）读回与写入逐字节相同；每次写都是 32 B 整行。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize, SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, INK, C_OFF, C_SIDE  # noqa: E402

OUT = HERE.parent
ROW = 32                           # 一行 32 B
NB_Q, NB_H = 8, 4                  # 一个象限 8 个 bank；一堆 4 个 bank（参考分法 4 + 4）


# ---------------- 换算式（与正文 §4.2 同式） ----------------
def phys(h, q, j):
    """[堆 h][象限 q][行 j] → (全芯片 bank 号, 深度)。"""
    assert h in (0, 1) and 0 <= q < 4 and j >= 0
    return NB_Q * q + NB_H * h + j % NB_H, j // NB_H


# 缩小例：象限 0，堆 0 放对象 X（行 0–9）与对象 Z（行 12–19），堆 1 放对象 Y（行 0–7）
OBJS = {                           # 名: (堆, 起始行, 行数)
    'X': (0, 0, 10),
    'Z': (0, 12, 8),
    'Y': (1, 0, 8),
}
FILL = {'X': '#fde3c4', 'Z': '#dcefd2', 'Y': '#d6e6f7'}
OCC = {}
for name, (h, j0, n) in OBJS.items():
    for i in range(n):
        bd = phys(h, 0, j0 + i)
        assert bd not in OCC, (name, i, bd)              # 互不重叠
        OCC[bd] = (name, h, j0 + i)
BANKS_H = [{phys(h, 0, j)[0] for j in range(64)} for h in (0, 1)]
assert BANKS_H[0].isdisjoint(BANKS_H[1])                 # 两堆 bank 不相交
for t in range(8):                                       # 写堆 1 第 t 行、读堆 0 第 t 行同拍不撞 bank
    assert phys(1, 0, t)[0] != phys(0, 0, t)[0]
CONC = [(t, phys(1, 0, t), phys(0, 0, t)) for t in range(4)]
assert phys(0, 2, 5) == (17, 1)                          # 正文 §4.2 的数值例
# 冲突例（正文 §6.5）：象限 0 读口读 [0][0][行 1]、NI 写 [0][0][行 5]，同在 bank 1
assert phys(0, 0, 1) == (1, 0) and phys(0, 0, 5) == (1, 1)
assert phys(0, 0, 1)[0] != phys(0, 0, 6)[0] and phys(0, 0, 2)[0] != phys(0, 0, 7)[0]   # 拍 1 读重发行 1、拍 2 读行 2

# 环形：象限 1 堆 0，环基址行 4、环长 L = 12 行；一个 5 拍单位从环内第 k = 10 行起
RING_Q, RING_H, RING_BASE, RING_L, RING_K0, RING_N = 1, 0, 4, 12, 10, 5
RING = []
for b in range(RING_N):
    k = RING_K0 + b
    j = RING_BASE + (k % RING_L)                         # MAE 搬运引擎取模；L2 只收 j
    RING.append((b, k, j, *phys(RING_H, RING_Q, j)))
assert [j for _, _, j, _, _ in RING] == [14, 15, 4, 5, 6]

# 11-07（V18-TP-58）：③ 档记录紧挨、长度表单独存；三条记录 17 B、40 B、32 B 从字节 0 起（11-05 的对象头 + 整字对齐退役）
PIECES = [('记录 0', 17), ('记录 1', 40), ('记录 2', 32)]
piece_start = [sum(n for _, n in PIECES[:i]) for i in range(len(PIECES))]   # 字节起点 = 前几项之和
OBJ_BYTES_O = sum(n for _, n in PIECES)
NROWS_O = -(-OBJ_BYTES_O // ROW)
LT_ROW_O = 8                                             # 长度表所在字（编译链另给）
mem = bytearray(NROWS_O * ROW)
payload = []
acc_buf = b''
written_rows = 0
for i, (_, n) in enumerate(PIECES):
    data = bytes((i * 71 + b * 3 + 1) % 255 + 1 for b in range(n))         # 非 0，便于区分空位
    payload.append(data)
    acc_buf += data                                                         # 攒字寄存器：跨记录连着攒
    while len(acc_buf) >= ROW:                                              # 攒满 32 B 才写一个存储字
        mem[written_rows * ROW:(written_rows + 1) * ROW] = acc_buf[:ROW]
        acc_buf = acc_buf[ROW:]
        written_rows += 1
TAIL_O = len(acc_buf)                                                       # 对象末字带 be 写出
if acc_buf:
    mem[written_rows * ROW:written_rows * ROW + TAIL_O] = acc_buf
    written_rows += 1
assert written_rows == NROWS_O
for i, (_, n) in enumerate(PIECES):                                         # 按长度表定位读回（跨字由读口出口移位）
    s0 = piece_start[i]
    assert bytes(mem[s0:s0 + n]) == payload[i]
assert piece_start == [0, 17, 57] and OBJ_BYTES_O == 89 and NROWS_O == 3 and TAIL_O == 25

# ---------------- 图 1（11-05 退役，由 draw_l2_arch.py 的 FIG-L2_SRAM-ARCH 取代）----------------


# ---------------- 图 2：象限内两堆的行 → bank、深度 ----------------
X0, CW, CH, Y0, RH = 130, 116, 40, 92, 50
DEPTHS = range(0, 6)


def fig_map_heap():
    s = SvgF5(1100, 420)
    for h in (0, 1):                                     # 堆标题
        xa = X0 + NB_H * h * CW
        s.rich(xa + (NB_H * CW - 10) / 2, 26, f'堆 {h}（bank {NB_H * h}–{NB_H * h + NB_H - 1}）', 16, 'middle', NAVY, 700)
    for b in range(NB_Q):
        s.rich(X0 + b * CW + (CW - 10) / 2, 60, f'bank {b}', 15, 'middle', GREY, 600)
    for d in DEPTHS:
        y = Y0 + d * RH
        s.rich(X0 - 16, y + CH / 2, f'深度 {d}', 15, 'end')
        for b in range(NB_Q):
            c = OCC.get((b, d))
            if c is None:
                s.cell(X0 + b * CW, y, CW - 10, CH, '·', fill=C_OFF, size=14, color=GREY)
            else:
                name, h, j = c
                s.cell(X0 + b * CW, y, CW - 10, CH, f'{name} 字 {j}', fill=FILL[name], size=14)
    xm = X0 + NB_H * CW - 5                              # 两堆分界
    s.line([(xm, 44), (xm, Y0 + len(DEPTHS) * RH)], color='#b42318', sw=1.8, marker=None, dash='6,4')
    s.save('FIG-L2_SRAM-MAP-HEAP.svg')


# ---------------- 图 3：环形回绕由 MAE 搬运引擎做 ----------------


# ---------------- 图 4：③ 档记录紧挨存放，长度表单独存（11-07 V18-TP-58） ----------------
def fig_obj_align():
    px = 24                                              # 每字节 24 px
    x0, y0, rh = 110, 56, 60
    s = SvgF5(x0 + ROW * px + 40, y0 + (NROWS_O + 1) * rh + 60)
    for bb in (0, 8, 16, 24):
        s.rich(x0 + bb * px, 32, f'{bb} B', 13, 'start', GREY, 600)
    colors = ['#fde3c4', '#d6e6f7', '#dcefd2']
    for rr in range(NROWS_O):
        s.rich(x0 - 16, y0 + rr * rh + 22, f'字 {rr}', 15, 'end')
    for i, (name, n) in enumerate(PIECES):
        a = piece_start[i]
        b = a
        while b < a + n:                                 # 一条记录可能跨字：按字切段画
            rr, off = b // ROW, b % ROW
            ln = min(ROW - off, a + n - b)
            txt = f'{name}（{n} B）' if b == a else f'续 {ln} B'
            s.cell(x0 + off * px, y0 + rr * rh, ln * px - 4, 44, txt, fill=colors[i], size=12, color='#1f2937')
            b += ln
    s.cell(x0 + TAIL_O * px, y0 + (NROWS_O - 1) * rh, (ROW - TAIL_O) * px - 4, 44, f'空 {ROW - TAIL_O} B', fill=C_OFF, size=12, color=GREY)
    yy = y0 + NROWS_O * rh + 16
    s.rich(x0 - 16, yy + 22, f'字 {LT_ROW_O}', 15, 'end')
    s.cell(x0, yy, 6 * px - 4, 44, '长度表 [17, 40, 32]', fill=C_SIDE, size=12, color='#1f2937')
    s.cell(x0 + 6 * px, yy, (ROW - 6) * px - 4, 44, '3 × 24 bit（16 bit 长度 + 8 bit tokmax）；编译链另给地址，由 CCU 写', fill='white', size=12, color=GREY)
    s.rich(x0, yy + 66, f'起点 {piece_start}（前几项之和）；读记录 1 = 字节 17 起 40 B，覆盖字 0、1，读口出口按 17 移位；末字 {TAIL_O} B 带 be 写出', 13, 'start', INK, 500)
    s.save('FIG-L2_SRAM-OBJ-ALIGN.svg')

def md():
    print('| 拍 | 写堆 1 的存储字 | 落点（bank, 深度） | 读堆 0 的存储字 | 落点（bank, 深度） |')
    print('|---|---|---|---|---|')
    for t, a, b in CONC:
        print(f'| {t} | 字 {t} | ({a[0]}, {a[1]}) | 字 {t} | ({b[0]}, {b[1]}) |')
    print()
    print('| 拍 | 环内序号 k | MAE 搬运引擎给的字号 | bank | 深度 |')
    print('|---|---|---|---|---|')
    for b, k, j, bank, d in RING:
        print(f'| {b} | {k} | {j} | {bank} | {d} |')


if __name__ == '__main__':
    fig_map_heap()
    fig_obj_align()
    if '--md' in sys.argv:
        md()
