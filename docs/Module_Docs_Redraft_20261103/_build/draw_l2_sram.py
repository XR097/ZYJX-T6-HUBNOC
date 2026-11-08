"""L2 SRAM 需求篇的四张图。Owner: WangYizhao · 2026-11-03；2026-11-05 按传输协议篇定稿同步
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_l2_sram.py [--md]
输出（figs/）：
  （FIG-L2_SRAM-CONN 11-05 晚退役：函数改名 _retired_fig_conn、不再调用；由 draw_l2_arch.py 的 FIG-L2_SRAM-ARCH 取代）
  FIG-L2_SRAM-MAP-HEAP   一个象限内两堆的行落到哪个 bank、哪个深度（缩小例；11-05 取代 MAP-REGION）
  FIG-L2_SRAM-MAP-RING   环形回绕由 MAE 搬运引擎做：第 k 个存储字地址 = 基址 + (k mod L)，L2 只按每拍地址落字
                         （11-05 夜 V18-TP-27：原"发地址方"改为 MAE 搬运引擎）
  FIG-L2_SRAM-OBJ-ALIGN  记录级对齐：对象头与每条记录各从整行起、占 ceil(n/32) 行、各自补 0（11-05 取代 UNIT-ALIGN；同日由对象级改为记录级）
11-05 退役：FIG-L2_SRAM-MAP-REGION（区表）、FIG-L2_SRAM-UNIT-ALIGN（单位补到 8 B 字），原 SVG 移到 figs/_retired_20261105/。
脚本断言：
  MAP-HEAP：地址 [堆 h][象限 q][行 j] → bank = 8q + 4h + (j mod 4)，深度 = j div 4；
            同一堆内各对象互不重叠；堆 0 与堆 1 的 bank 不相交，同拍写堆 1 第 t 行、读堆 0 第 t 行不撞 bank。
  MAP-RING：MAE 搬运引擎算的 5 拍行号 = 基址 + (k mod L)；各拍落点与换算式一致；L2 侧不取模。
  OBJ-ALIGN：对象头与每条记录各从整行起、占 ceil(n/32) 行；各自尾部补 0 字节数 = 行数 × 32 − n；
             任何一行只属于一段（无跨行、无行内偏移）；按（首行号, 长度）读回与写入逐字节相同；每次写都是 32 B 整行。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize, SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, C_OFF  # noqa: E402

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

# 记录级对齐（用户 11-05 再定）：对象头 8 B + 三条记录 17 B、40 B、32 B，各自从整行起、尾部补 0
PIECES = [('对象头', 8), ('记录 0', 17), ('记录 1', 40), ('记录 2', 32)]
piece_start, r = [], 0
for _, n in PIECES:
    piece_start.append(r)
    r += -(-n // ROW)                                    # 占 ceil(n / 32) 行
NROWS_O = r
mem = bytearray(NROWS_O * ROW)
owner = [None] * NROWS_O
payload = []
for i, (_, n) in enumerate(PIECES):
    data = bytes((i * 71 + b * 3 + 1) % 255 + 1 for b in range(n))         # 非 0，便于区分填充
    payload.append(data)
    nrow = -(-n // ROW)
    buf = data + bytes(nrow * ROW - n)                                      # 尾部补 0 到行边界
    for k in range(nrow):                                                   # 攒整行再写
        row = buf[k * ROW:(k + 1) * ROW]
        assert len(row) == ROW
        rr = piece_start[i] + k
        assert owner[rr] is None                                            # 一行只属于一段
        owner[rr] = i
        mem[rr * ROW:(rr + 1) * ROW] = row
assert all(o is not None for o in owner)
for i, (_, n) in enumerate(PIECES):                                         # 按首行号与长度读回，无行内偏移
    s0 = piece_start[i] * ROW
    assert bytes(mem[s0:s0 + n]) == payload[i]
    nrow = -(-n // ROW)
    assert bytes(mem[s0 + n:s0 + nrow * ROW]) == bytes(nrow * ROW - n)
assert piece_start == [0, 1, 2, 4] and NROWS_O == 5

# ---------------- 图 1（11-05 退役，由 draw_l2_arch.py 的 FIG-L2_SRAM-ARCH 取代）----------------
def _retired_fig_conn():
    f = Figure('L2_SRAM-CONN', '', width=1428, height=812, out_dir=OUT, max_crossings=3)
    f.block('hubup', 70, 154, 280, 112, 'C2H 分流', '四核 C2H 扇入 → L2WP', kind='external')
    f.block('niw', 70, 378, 280, 126, 'NI_INT 写', 'DDR 读入 / 调用输入\nPIN 写入 / MAE 拷贝', kind='external')
    f.block('l2', 546, 154, 308, 546, 'L2 SRAM', '2 MiB · 32 bank × 32 B\n4 象限 × 2 堆 × 4 bank\n两写口为接收桥', kind='memory')
    f.block('hubdn', 1050, 154, 308, 224, 'H2C 道 0–3', '道 n 发读地址\n读出 → 四核第 n 道', kind='external')
    f.block('nir', 1050, 434, 308, 112, 'NI_INT 返回读', '→ DDR / M1 共享内存', kind='external')
    f.block('lic', 1050, 602, 308, 98, 'LIC', '经命令与标量网', kind='control')
    f.net('w1', 'hubup', 'l2', 'L2WP 写 · addr')
    f.net('w2', 'niw', 'l2', 'NI 写 · addr')
    for q in range(4):
        f.net(f'r{q}', 'l2', 'hubdn', f'象限 {q} → 道 {q}')
    f.net('r4', 'l2', 'nir', 'NI 返回读')
    f.net('e1', 'l2', 'lic', '致命错误', kind='event')
    xs, attempt = f.save()
    print(f.d['id'], 'crossings', xs, 'attempt', attempt)
    finalize(f)


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
def _retired_fig_map_ring():   # 11-06 晚退役：L2 里的对象不按环形使用（V18-MAE-17）
    s = SvgF5(1180, 250)
    xs, cw, cy = 90, 84, 96
    beat_of = {j: b for b, _, j, _, _ in RING}
    rows = list(range(RING_BASE, RING_BASE + RING_L))
    cx = {j: xs + (j - RING_BASE) * cw + (cw - 8) / 2 for j in rows}
    s.rich(xs, 26, f'MAE 搬运引擎：第 k 个存储字的地址 = 基址 {RING_BASE} + (k mod {RING_L})；L2 只按每拍地址落字', 15, 'start', NAVY, 700)
    for j in rows:
        hit = j in beat_of
        s.cell(xs + (j - RING_BASE) * cw, cy, cw - 8, 44, f'字 {j}', fill='#fde3c4' if hit else 'white', size=14)
        if hit:
            b = beat_of[j]
            s.rich(cx[j], cy - 36, f'拍 {b}', 14, 'middle', NAVY, 700)
            s.rich(cx[j], cy - 16, f'k = {RING[b][1]}', 13, 'middle', GREY, 600)
    yb = cy + 44 + 40                                  # 回绕箭头：行 15 → 行 4
    s.line([(cx[rows[-1]], cy + 46), (cx[rows[-1]], yb), (cx[rows[0]], yb), (cx[rows[0]], cy + 48)],
           color='#b42318', sw=1.8, marker='ar')
    s.red((cx[rows[0]] + cx[rows[-1]]) / 2, yb + 22, 'MAE 搬运引擎取模回到环首（字 4）', 15, 'middle')
    s.save('FIG-L2_SRAM-MAP-RING.svg')


# ---------------- 图 4：记录级对齐，每条记录占整数行 ----------------
def fig_obj_align():
    px = 24                                              # 每字节 24 px
    x0, y0, rh = 110, 56, 60
    s = SvgF5(x0 + ROW * px + 40, y0 + NROWS_O * rh + 30)
    for bb in (0, 8, 16, 24):
        s.rich(x0 + bb * px, 32, f'{bb} B', 13, 'start', GREY, 600)
    colors = ['#f3d9ef', '#fde3c4', '#d6e6f7', '#dcefd2']
    for rr in range(NROWS_O):
        s.rich(x0 - 16, y0 + rr * rh + 22, f'字 {rr}', 15, 'end')
    for i, (name, n) in enumerate(PIECES):
        for k in range(-(-n // ROW)):
            rr = piece_start[i] + k
            ln = min(ROW, n - k * ROW)
            s.cell(x0, y0 + rr * rh, ln * px - 4, 44, f'{name}（共 {n} B）' if k == 0 else f'{name} 续（{ln} B）',
                   fill=colors[i], size=13, color='#1f2937')
            if ln < ROW:
                s.cell(x0 + ln * px, y0 + rr * rh, (ROW - ln) * px - 4, 44, f'补 0（{ROW - ln} B）',
                       fill=C_OFF, size=13, color=GREY)
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
