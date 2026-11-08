"""L1 SRAM 需求篇（11-04 重写稿，物理 bank 分区 + 硬化 ping-pong）的图。Owner: WangYizhao · 2026-11-04（第二版，按用户审图意见重画）
2026-11-05 第三版：按片上数据传输协议篇定稿同步（地址 = [堆][类][行号]、撤分配表与角色位、RRAM、接收桥 / 发送桥、
命令网、32 B 最小写、记录级对齐）。FIG-L1_SRAM-PARTITION 退役（_retired_ 前缀，不再生成）。
同日第二轮（S14–S20）：32 B 单位改称存储字 / 字号；FIG-L1_SRAM-CONN 退役（由 _build/draw_l1_arch.py 的 FIG-L1_SRAM-ARCH 取代）；
新增 FIG-L1_SRAM-ABANK-CFG（A 类 4 / 8 bank 配置）。
2026-11-05 晚（V18-L1-09 / L1-10，任务书 _build/L1_COLWORD_FIGURE_BRIEF_20261105.md）：列字区改为"一个存储字 = 一列 64 个连续 k"
（bank ⌊j/2⌋、深度 2p + (j mod 2)）+ 读口重组器；重画 MAP-W、LANE-PICK，新增 COLREAD-1SRC / -2SRC；
FIG-L1_SRAM-COLARRIVE 退役（NWB 配对暂存撤销；函数 _retired_fig_colarrive，SVG 移 figs/_retired_20261105/），--md 一并撤。
2026-11-05 夜（V18-TP-26…34）：RING 的算地址方改为"核内 CCU / 核间 MAE 搬运引擎"；_retired_fig_conn 保持退役原样（不生成）。
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_l1_sram.py
依据：DATA_TRANSFER_PROTOCOL.md（定稿）；Claude_Design_Spec/V1.8_DESIGN_REVISIONS.md V18-TP-01…16、V18-L1-01…10。
输出（figs/）：
  FIG-L1_SRAM-BANKS        两堆 × 12 个 bank：W0 / W1 / A 三组、成对；W 类 / A 类的 bank 集合
  FIG-L1_SRAM-ABANK-CFG    A 类 4 bank 与 8 bank 两种配置：写集合口道数与 bank 对应、字号落位
  FIG-L1_SRAM-PINGPONG     物理两堆 ping-pong：同一拍读一堆、写另一堆；阶段之间切换地址堆位
  FIG-L1_SRAM-RING         环形回绕只在核内、由 CCU 做：基址 + (k mod L)，L1 只收字号（MAE 搬运不用环，V18-MAE-17）
  FIG-L1_SRAM-MAP-W        列字区（OAS）：一个存储字 = 一列 64 个连续 k（两段）；16 列 × 2 段对落 8 个 bank × 4 个深度，bank b 装列 2b、2b+1
  FIG-L1_SRAM-MAP-W-HALF   行字区（IAS）只占 W0：一段落 4 个 bank × 2 个深度
  FIG-L1_SRAM-MAP-A        A 类线性映射：记录按实际长度紧挨（11-07 V18-TP-58），轮流落 bank 8–11，长度表单独存
  FIG-L1_SRAM-LANE-PICK    稀疏取列：一个 pass 每 bank ≤ 2 列，lane 2b / 2b+1 = bank b 的第一 / 第二列，按掩码进 4 个 pod
  FIG-L1_SRAM-TWO-SRC      两来源：W0 / W1 两条总线，pod 槽在 lane s 与 s⊕8 间静态二选一
  FIG-L1_SRAM-COLREAD-1SRC 读口重组器逐拍（单来源 8 bank）：拍 0–5，稳态一段一拍
  FIG-L1_SRAM-COLREAD-2SRC 读口重组器逐拍（两来源，来源 A 4 bank）：拍 0–9，每拍半段、起步气泡、峰值 128 B/bank
脚本断言：各图数值由本脚本按正文 §3、§4、§6、§7、§9 的规则算出。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize, SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, RED, INK, CTRL, C_OFF, C_W, C_LO, C_KEEP, C_SIDE, C_HI, C_LEFT, C_ACC  # noqa: E402

OUT = HERE.parent
UNIT = 32
NB_HEAP = 12
GROUPS = {'W0': range(0, 4), 'W1': range(4, 8), 'A': range(8, 12)}
GFILL = {'W0': C_W, 'W1': '#f6e3b0', 'A': C_LO}
C_B = '#f3d9ef'                                  # 来源 B


def group_of(b):
    return next(g for g, r in GROUPS.items() if b in r)


assert sum(len(r) for r in GROUPS.values()) == NB_HEAP


def krange(s):
    return f'k{32 * s}–{32 * s + 31}'


# ---------------- 换算（正文 §4.3–§4.4） ----------------
def w_phys(j, s, nbank=8):
    """一段第 j 个 16 B 字（j = 0…15）、段 s → (bank, 字位, 深度)。nbank = 8：一段一个深度；4：两个深度。"""
    if nbank == 8:
        return j // 2, j % 2, s
    half, jj = divmod(j, 8)
    return jj // 2, jj % 2, 2 * s + half


def wcol_phys(j, p, nbank=8):
    """列字区（11-05 晚 V18-L1-09）：一个存储字 = 列 j（j = 0…15）在段 2p、2p+1 的 64 个连续 k → (bank, 深度)。
    nbank = 8（单来源）：bank ⌊j/2⌋，深度 2p + (j mod 2)；
    nbank = 4（两来源，每来源 4 个 bank）：bank ⌊(j mod 8)/2⌋，深度 4p + 2⌊j/8⌋ + (j mod 2)。"""
    if nbank == 8:
        return j // 2, 2 * p + j % 2
    return (j % 8) // 2, 4 * p + 2 * (j // 8) + j % 2


MAPW = {}                                         # 列字区：(bank, 深度) → (列 j, 段对 p)
for p in range(2):
    for j in range(16):
        key = wcol_phys(j, p)
        assert key not in MAPW
        MAPW[key] = (j, p)
    assert {wcol_phys(j, p)[1] for j in range(16)} == {2 * p, 2 * p + 1}       # 深度 2p、2p+1 的 16 个字覆盖 16 列
for j in range(16):
    (b0, d0), (b1, d1) = wcol_phys(j, 0), wcol_phys(j, 1)
    assert b0 == b1 == j // 2 and d1 - d0 == 2                                  # 每列两个字，同一 bank
for b in range(8):
    for p in range(2):
        assert [MAPW[(b, 2 * p)][0], MAPW[(b, 2 * p + 1)][0]] == [2 * b, 2 * b + 1]   # bank b 相邻深度装列 2b、2b+1
assert set(MAPW) == {(b, d) for b in range(8) for d in range(4)}
MAPW2 = {}                                        # 两来源（来源 A，bank 0–3）
for p in range(2):
    for j in range(16):
        key = wcol_phys(j, p, nbank=4)
        assert key not in MAPW2 and key[0] < 4
        MAPW2[key] = (j, p)
for b in range(4):
    assert [MAPW2[(b, 4 * 0 + i)][0] for i in range(4)] == [2 * b, 2 * b + 1, 2 * b + 8, 2 * b + 9]
MAPH = {}                                         # 行字区：第 j 个字 = k 2j、2j+1（段内）× m 0–15
for s in range(2):
    for j in range(16):
        key = w_phys(j, s, nbank=4)
        assert key not in MAPH and key[0] < 4
        MAPH[key] = (j, s)
    assert {w_phys(j, s, nbank=4)[2] for j in range(16)} == {2 * s, 2 * s + 1}

# ---------------- A 类线性映射（正文 §4.4）：行 j → bank 列表第 (j mod n) 项、深度 ⌊j / n⌋ ----------------
A_BANKS = [8, 9, 10, 11]                          # 未改配 W1 时 A 类的 bank 列表
REC_LEN = [70, 40, 100]                           # 三个 token 的记录长度（字节）
# 11-07（V18-TP-58）：记录按实际长度紧挨，长度表单独存；11-05 的"对象头 + 每条记录占整字"退役
REC_START = [sum(REC_LEN[:t]) for t in range(len(REC_LEN))]   # 字节起点 = 前几项之和
OBJ_BYTES = sum(REC_LEN)
A_ROWS = -(-OBJ_BYTES // UNIT)
LT_ROW = 16                                       # 长度表所在字（编译链另给）
ROWSEG = {}                                       # 字 j → [(名, 记录内起, 止, 字节)]
for j in range(A_ROWS):
    segs = []
    for t, (a, n) in enumerate(zip(REC_START, REC_LEN)):
        lo, hi = max(a, j * UNIT), min(a + n, (j + 1) * UNIT)
        if lo < hi:
            segs.append((f't{t}', lo - a, hi - a - 1, hi - lo))
    used = sum(x[3] for x in segs)
    if used < UNIT:
        segs.append(('空', 0, UNIT - used - 1, UNIT - used))
    ROWSEG[j] = segs
assert REC_START == [0, 70, 110] and OBJ_BYTES == 210 and A_ROWS == 7
assert ROWSEG[2] == [('t0', 64, 69, 6), ('t1', 0, 25, 26)] and ROWSEG[6][-1] == ('空', 0, 13, 14)   # 一个字可含两条记录；末字空 14 B
assert all(sum(x[3] for x in ROWSEG[j]) == UNIT for j in range(A_ROWS))
RD_T = 1                                          # 例：读 token 1
RD_WORDS = (REC_START[RD_T] // UNIT, (REC_START[RD_T] + REC_LEN[RD_T] - 1) // UNIT)
RD_SHIFT = REC_START[RD_T] % UNIT
assert RD_WORDS == (2, 3) and RD_SHIFT == 6
MAPA = {}
for j in range(A_ROWS):
    key = (A_BANKS[j % len(A_BANKS)], j // len(A_BANKS))
    assert key not in MAPA
    MAPA[key] = j
assert MAPA[(10, 0)] == 2 and MAPA[(10, 1)] == 6 and (11, 1) not in MAPA
LT_KEY = (A_BANKS[LT_ROW % 4], LT_ROW // 4)
assert LT_KEY == (8, 4)

# ---------------- 环形回绕由核内 CCU / 核间 MAE 搬运引擎做（正文 §3.3） ----------------
RING_BASE, RING_L, RING_K = 20, 6, range(4, 9)    # 环占 A 类行 20–25；本次写对象的第 4–8 行
RING = [(k, k % RING_L, RING_BASE + k % RING_L) for k in RING_K]
assert [a for _, _, a in RING] == [24, 25, 20, 21, 22]   # L1 只收到这些行号，不知道环长

# ---------------- 稀疏取列（正文 §6.1，11-05 晚 V18-L1-10）：一个 pass，同一段 ----------------
# 列 m → 列组 ⌊m/16⌋、j = m mod 16、bank ⌊j/2⌋；一个 pass 每个 bank 至多两列（任意两列），没人要的列不读。
POD_NEED = {0: {1, 5, 17}, 1: {5, 17, 34}, 2: set(), 3: {0, 1, 20, 35, 40}}
UNION = set().union(*POD_NEED.values())


def col_bank(m):
    return wcol_phys(m % 16, 0)[0]


PASS_COLS, DEFER = {}, []                         # bank → 本 pass 读的列（按 m 升序）；下一 pass 的列
for m in sorted(UNION):
    lst = PASS_COLS.setdefault(col_bank(m), [])
    (lst.append(m) if len(lst) < 2 else DEFER.append(m))
assert PASS_COLS == {0: [0, 1], 1: [34, 35], 2: [5, 20], 4: [40]} and DEFER == [17]
assert all(len(v) <= 2 for v in PASS_COLS.values())                   # 每 bank ≤ 2 列
BEAT0 = {}                                        # lane → (m, 掩码集合)；lane 2b / 2b+1 = bank b 的第一 / 第二列
for b, ms in PASS_COLS.items():
    for i, m in enumerate(ms):
        BEAT0[2 * b + i] = (m, {p for p in range(4) if m in POD_NEED[p]})
assert BEAT0[5] == (20, {3}) and BEAT0[1] == (1, {0, 3}) and BEAT0[4] == (5, {0, 1}) and 9 not in BEAT0
assert all(pods for _, pods in BEAT0.values())                       # 没人要的列不出现
assert all(2 not in pods for _, pods in BEAT0.values())              # pod 2 本 pass 不锁存
assert sorted(lane for lane in range(16) if lane not in BEAT0) == [6, 7, 9, 10, 11, 12, 13, 14, 15]

# ---------------- 读口重组器（正文 §6，11-05 晚 V18-L1-09）：逐拍模拟一个 bank ----------------
# 每拍 bank 读一个存储字（32 B = 前半 16 B + 后半 16 B）；重组器以 16 B 半字为单位持有；
# 交出单位按固定顺序，本拍交出的半字必须在拍初已在重组器内（上一拍或更早读入）。
RG_CAP = 128                                      # 每 bank 重组器 2 × 64 B


def colread_units(nsrc, nunit):
    """交出单位序列：[(名, [(深度, 'F'/'B')…])]。nsrc = 1：一个单位 = 一段（16 列）；2：一个单位 = 半段（8 列）。"""
    out = []
    if nsrc == 1:
        for s in range(nunit):
            d0 = 2 * (s // 2)
            out.append(((s, None), [(d0, 'FB'[s % 2]), (d0 + 1, 'FB'[s % 2])]))
    else:
        for p in range(-(-nunit // 4)):
            d = 4 * p
            for seg, half, ds, fb in ((2 * p, 0, (d, d + 1), 'F'), (2 * p, 1, (d + 2, d + 3), 'F'),
                                      (2 * p + 1, 0, (d, d + 1), 'B'), (2 * p + 1, 1, (d + 2, d + 3), 'B')):
                out.append(((seg, half), [(x, fb) for x in ds]))
    return out[:nunit]


def colread_sim(nsrc, nbeat):
    units, held, log = colread_units(nsrc, nbeat), set(), []
    for t in range(nbeat):
        start = set(held)
        need = units[0][1] if units else None
        out = None
        if need and set(need) <= start:
            out = units.pop(0)[0]
            held -= set(need)
        occ = 16 * len(start) + UNIT                  # 拍初持有 + 本拍读入的一个存储字
        assert occ <= RG_CAP
        held |= {(t, 'F'), (t, 'B')}                  # 本拍读深度 t
        log.append(dict(t=t, depth=t, start=16 * len(start), occ=occ, out=out))
    return log


CR1 = colread_sim(1, 6)
assert [r['out'] for r in CR1] == [None, None, (0, None), (1, None), (2, None), (3, None)]   # 稳态一段一拍，多 1 拍时延
assert [r['start'] for r in CR1] == [0, 32, 64, 64, 64, 64] and max(r['start'] for r in CR1) * 4 == 256   # 拍初持有：每 4 bank ≤ 256 B
assert [r['occ'] for r in CR1] == [32, 64, 96, 96, 96, 96]
CR2 = colread_sim(2, 10)
assert [r['out'] for r in CR2] == [None, None, (0, 0), None, (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0)]
assert [r['start'] for r in CR2] == [0, 32, 64, 64, 96, 96, 96, 96, 96, 96]
assert [r['occ'] for r in CR2] == [32, 64, 96, 96, 128, 128, 128, 128, 128, 128]
assert max(r['occ'] for r in CR2) * 4 == 512                       # 峰值：每来源 512 B = 每 bank 128 B
assert [t for t, r in enumerate(CR2) if r['out'] is None and t >= 2] == [3]   # 起步气泡只在拍 3


def cr_cols(nsrc, depth):
    """该深度上（每个 bank 一个字）这一拍读出的列，按 bank 排。"""
    nb, per, mp = (8, 2, MAPW) if nsrc == 1 else (4, 4, MAPW2)
    return [mp[(b, depth % per)][0] for b in range(nb)]       # 列号与段对 p 无关，只看深度在段对内的位置


assert cr_cols(1, 0) == list(range(0, 16, 2)) and cr_cols(1, 3) == list(range(1, 16, 2))
assert cr_cols(2, 2) == [8, 10, 12, 14] and cr_cols(2, 5) == [1, 3, 5, 7]

# ---------------- 两来源（正文 §6.2） ----------------
SRC_OF_POD = {0: 'A', 1: 'B', 2: 'B', 3: 'B'}     # 1 + 3


def slot_select(pod, half):
    """返回该 pod 半段（0 = 槽 0–7，1 = 槽 8–15）选的总线：'A'（lane 0–7）或 'B'（lane 8–15）。"""
    return SRC_OF_POD[pod]


for p in range(4):
    for half in (0, 1):
        bus = slot_select(p, half)
        for s in range(8 * half, 8 * half + 8):
            lane = s % 8 + (0 if bus == 'A' else 8)
            assert lane in (s, s ^ 8)             # 槽 s 只在 lane s 与 s⊕8 间二选一
SINGLE = {(p, h): ('A' if h == 0 else 'B') for p in range(4) for h in (0, 1)}   # 单来源：直连

# ---------------- 按列到达（正文 §7.6，11-05：NWB 攒整行再写） ----------------
# 一行 = 同一段的相邻两列 (m_{2q}, m_{2q+1})；列深度优先到达，每拍 32 B = 同一列相邻两段的两个列字。
# NWB 暂存列字，等同一段的配对列到齐后拼成整行写出；每个 bank 每拍至多写一行。
COLS = ['m0', 'm1', 'm2', 'm3']
NSEG = 4
ARRIVE = [[(c, 2 * h), (c, 2 * h + 1)] for c in COLS for h in range(NSEG // 2)] + [[], []]
BANK_OF = {c: w_phys(int(c[1:]), 0)[0] for c in COLS}
assert BANK_OF == {'m0': 0, 'm1': 0, 'm2': 1, 'm3': 1}
PAIR_OF = {'m0': 'm1', 'm1': 'm0', 'm2': 'm3', 'm3': 'm2'}
held, ready, LOG = [], [], []                    # held：未配对的列字；ready：已拼成、待写的整行 (bank, 段, 列对)
for t, arr in enumerate(ARRIVE):
    for c, g in arr:
        mate = (PAIR_OF[c], g)
        if mate in held:
            held.remove(mate)
            lo, hi = sorted((c, PAIR_OF[c]))
            ready.append((BANK_OF[c], g, f'{lo}+{hi}'))
        else:
            held.append((c, g))
    written, used = [], set()
    for row in list(ready):
        if row[0] not in used:                    # 每个 bank 每拍一行
            used.add(row[0])
            written.append(row)
            ready.remove(row)
    LOG.append((t, arr, written, list(held), list(ready)))
assert [len(w) for _, _, w, _, _ in LOG] == [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
assert max(len(h) for _, _, _, h, _ in LOG) == 4 and not LOG[-1][3] and not LOG[-1][4]
# 稳态写出 1 行/拍 = 到达 32 B/拍；代价是 NWB 暂存一整列（这里 4 段 = 64 B，实际 K/2 字节）


def wname(c, g):
    return f'{c} {krange(g)}'


# ======================================================================
def fig_banks():
    s = SvgF5(1240, 310)
    x0, cw, ch = 130, 88, 56
    for r in (0, 1):
        y = 70 + r * 110
        s.rich(x0 - 16, y + ch / 2, f'堆 {r}', 17, 'end')
        for b in range(NB_HEAP):
            s.cell(x0 + b * cw, y, cw - 8, ch, f'bank {b}', fill=GFILL[group_of(b)], size=14)
    for g, rg in GROUPS.items():
        xa, xb = x0 + rg[0] * cw, x0 + (rg[-1] + 1) * cw - 8
        s.rich((xa + xb) / 2, 40, g, 17, 'middle', NAVY, 700)
        s.line([(xa, 52), (xb, 52)], color=NAVY, sw=1.4, marker=None)
    for cls, b0, b1 in (('W 类（bank 0–7）', 0, 7), ('A 类（bank 8–11）', 8, 11)):   # 地址的类位所指 bank 集合
        xa, xb = x0 + b0 * cw, x0 + (b1 + 1) * cw - 8
        s.line([(xa, 254), (xb, 254)], color=CTRL, sw=1.4, marker=None)
        s.rich((xa + xb) / 2, 280, cls, 16, 'middle', CTRL, 700)
    for b in (0, 5, 10):
        cx = x0 + b * cw + (cw - 8) / 2
        s.line([(cx, 128), (cx, 178)], color=RED, sw=1.6, marker=None, dash='4,3')
    s.red(x0 + 10 * cw + (cw - 8) / 2 + 10, 158, '一对', 15)
    s.save('FIG-L1_SRAM-BANKS.svg')


# ---------------- 分区：bank 示意 + 虚线框（11-05 退役：分配表撤销，见 V18-TP-14） ----------------
def _retired_part_panel(s, x, y, title, regions):
    cw, rh, ndep = 64, 26, 8
    s.panel(x, y, 12 * cw + 70, ndep * rh + 120, title, 16)
    gx = x + 50
    for b in range(NB_HEAP):
        s.rich(gx + b * cw + cw / 2 - 3, y + 50, f'{b}', 13, 'middle', GREY, 600)
        for d in range(ndep):
            s.rect(gx + b * cw, y + 64 + d * rh, cw - 6, rh - 4, fill=GFILL[group_of(b)], sw=0.6, stroke=GREY)
    for g, rg in GROUPS.items():
        xa, xb = gx + rg[0] * cw, gx + (rg[-1] + 1) * cw - 6
        s.rich((xa + xb) / 2, y + ndep * rh + 84, g, 14, 'middle', NAVY, 700)
    for banks, d0, d1, label, col in regions:      # 每个区：bank 号列表（连续段画一个框）、深度区间
        runs, cur = [], [banks[0]]
        for b in banks[1:]:
            if b == cur[-1] + 1:
                cur.append(b)
            else:
                runs.append(cur)
                cur = [b]
        runs.append(cur)
        for i, run in enumerate(runs):
            bx0 = gx + run[0] * cw - 3
            bx1 = gx + (run[-1] + 1) * cw - 3
            s.rect(bx0, y + 61 + d0 * rh, bx1 - bx0, (d1 - d0) * rh + 2, fill='none', sw=2.4, dash='7,4', stroke=col)
            s.rich((bx0 + bx1) / 2, y + 64 + (d0 + d1) / 2 * rh - 2, label, 13, 'middle', col, 700)


def _retired_fig_partition():
    _part_panel = _retired_part_panel
    s = SvgF5(1730, 400)
    X = [
        ([0, 1, 2, 3], 0, 6, '来源 A 行字区', NAVY),
        ([4, 5, 6, 7], 0, 8, '来源 B 列字区', RED),
        ([8], 0, 8, '口 0', CTRL), ([9], 0, 8, '口 1', CTRL), ([10], 0, 8, '口 2', CTRL), ([11], 0, 8, '口 3', CTRL),
    ]
    Y = [
        ([0, 1, 2, 3], 0, 4, 'K hi 段区', NAVY),
        ([0, 1, 2, 3], 4, 8, 'V 段区', RED),
        ([4, 8], 0, 8, '口 0', CTRL),
        ([5, 9], 0, 8, '口 1', '#6b4f9e'),
        ([10], 0, 8, '口 2', CTRL), ([11], 0, 8, '口 3', CTRL),
        ([6, 7], 0, 8, '未用', GREY),
    ]
    _part_panel(s, 20, 20, '位点 X：两来源（W0、W1 各一个区）', X)
    _part_panel(s, 880, 20, '位点 Y：只用 W0，W1 的 4、5 改配给口 0、1', Y)
    s.save('FIG-L1_SRAM-PARTITION.svg')


# ---------------- 对外连接 ----------------
def _retired_fig_conn():   # 11-05 第二轮退役，由 draw_l1_arch.py 的 FIG-L1_SRAM-ARCH 取代
    f = Figure('L1_SRAM-CONN', '', width=1820, height=1316, out_dir=OUT, max_crossings=4, attempts=64, side_strategy='visibility')
    f.container('inter', 14, 196, 336, 924, '核间数据网')
    f.container('l1g', 420, 196, 910, 924, 'L1 组')
    f.container('intra', 1400, 196, 406, 924, '核内 RRAM 口')
    f.block('mae', 462, 28, 308, 98, 'MAE', '命令网（经 hub 控制道）', kind='control')
    f.block('ccu', 980, 28, 308, 98, '本核 CCU', 'en / wea / addr，dout 去向', kind='control')
    f.block('c2h', 42, 266, 266, 112, 'C2H 口前合并', '→ C2H 分流，32 B/拍\nAEB 直达口优先', kind='external')
    f.block('idn', 42, 504, 266, 112, 'IDN（HUB_IDN）', '32 B/拍 + addr', kind='external')
    f.block('h2c', 42, 770, 266, 112, 'H2C（H2C 道）', '4 道 × 32 B + addr', kind='external')
    f.block('tx', 462, 252, 640, 98, 'L1 命令单元 + 发送侧（发送桥）',
            '收发送命令、报完成、单位计数；发送桥 FIFO，addr = 目的 L2 地址', kind='function')
    f.block('nwb', 462, 504, 280, 112, 'NWB（IDN 接收桥）', '整字直写', kind='function')
    f.block('ldp', 462, 770, 280, 112, 'LDP × 4（H2C 接收桥）', 'ready 恒高，写地址 = addr', kind='function')
    f.block('scale', 1008, 980, 280, 98, '尺度 SRAM（S 类）', '两堆 / E8M0 / 旁带 / bias', kind='memory')
    f.block('banks', 1008, 440, 280, 420, 'bank 两堆', '24 × 32 B × D\nW 类：bank 0–7\nA 类：bank 8–11\n堆由段选的堆选选', kind='memory')
    f.block('pods', 1442, 826, 322, 252, '4 个 pod 的 WWB', '16 条 lane\n按掩码锁存', kind='compute')
    f.block('act', 1442, 420, 322, 252, '激活类口的客户', 'pod 激活记录缓冲\nNLU（含出口级）/ QNT\nSEL 等（L1 外选择）', kind='external')
    f.net('n_mae', 'mae', 'tx', '发送命令', kind='ctrl')
    f.net('n_done', 'tx', 'mae', '完成', kind='ctrl')
    f.net('n_ccu', 'ccu', 'banks', 'en / wea / addr', kind='ctrl')
    f.net('n_stall', 'tx', 'ccu', 'stall_tx / 单位计数', kind='ctrl')
    f.net('n_rd', 'banks', 'tx', '读')
    f.net('n_up', 'tx', 'c2h', '')
    f.net('n_idn', 'idn', 'nwb', '')
    f.net('n_h2c', 'h2c', 'ldp', '')
    f.net('n_nwb', 'nwb', ['banks', 'scale'], '写')
    f.net('n_ldp', 'ldp', ['banks', 'scale'], '写')
    f.net('n_lane', 'banks', 'pods', '')
    f.net('n_sc', 'scale', 'pods', '')
    f.net('n_ar', 'banks', 'act', '读')
    f.net('n_aw', 'act', 'banks', '写')
    xs, attempt = f.save()
    print(f.d['id'], 'crossings', xs, 'attempt', attempt)
    finalize(f)


# ---------------- ping-pong 同步读写 ----------------
def fig_pingpong():
    s = SvgF5(1400, 520)
    x0, colw, rowh = 200, 380, 120
    phases = ['阶段 1', '阶段 2', '阶段 3']
    for i, ph in enumerate(phases):
        s.rich(x0 + i * colw + (colw - 20) / 2, 34, ph, 17, 'middle', NAVY, 700)
    for r in (0, 1):
        y = 60 + r * rowh
        s.rich(x0 - 20, y + 45, f'堆 {r} 的 W 组', 16, 'end')
        for i in range(3):
            reading = (i % 2 == 0) == (r == 0)
            n = i + (0 if reading else 1)
            if reading:
                s.cell(x0 + i * colw, y, colw - 20, 90, f'读窗口 {n} → 16 条 lane', fill=C_KEEP, size=16)
            else:
                s.cell(x0 + i * colw, y, colw - 20, 90, f'NWB 写窗口 {n}', fill=C_HI, size=16)
    for i in range(2):                               # 阶段边界：地址堆位翻转（L1 无角色状态）
        xb = x0 + (i + 1) * colw - 10
        s.line([(xb, 52), (xb, 60 + 2 * rowh - 20)], color=RED, sw=1.8, marker=None, dash='6,4')
        s.red(xb, 60 + 2 * rowh, '翻转堆选', 14, 'middle')
    yb = 60 + 2 * rowh + 50                          # 同一拍内的放大
    s.rich(x0 - 20, yb + 40, '阶段 1 内某一拍', 16, 'end')
    s.cell(x0, yb, 200, 80, '堆 0 bank 3：读', fill=C_KEEP, size=16)
    s.cell(x0 + 220, yb, 200, 80, '堆 1 bank 3：写', fill=C_HI, size=16)
    s.line([(x0 + 100, yb + 80), (x0 + 100, yb + 104)], marker=None)
    s.line([(x0 + 320, yb + 80), (x0 + 320, yb + 104)], marker=None)
    s.rich(x0 + 210, yb + 118, '两颗宏，同拍各做一次访问', 15, 'middle', INK, 600)
    s.save('FIG-L1_SRAM-PINGPONG.svg')


# ---------------- 环形区 ----------------
def fig_ring():
    s = SvgF5(1240, 380)
    # 左：算地址的一方（核内 CCU；核间 MAE 搬运引擎，11-05 夜 V18-TP-27）逐字算 基址 + (k mod L)
    x0, y0, rh = 30, 30, 46
    cols = [('对象第 k 字', 130), ('k mod 6', 110), ('addr 字号', 130)]
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 8, 38, name, fill=C_SIDE, size=14)
        x += w
    s.rich(x0, y0 + 38 + len(RING) * rh + 30, f'核内 CCU：基址 {RING_BASE} + (k mod L)，L = {RING_L}', 15, 'start', NAVY, 700)
    for i, (k, km, a) in enumerate(RING):
        y = y0 + 46 + i * rh
        wrap = km < RING_K[0] % RING_L
        for xx, (_, w), v in zip(xs, cols, (str(k), str(km), str(a))):
            s.cell(xx, y, w - 8, 38, v, fill=C_LEFT if wrap else 'white', size=14)
    # 右：L1 的 A 类第 20–25 行，只按收到的行号落位
    rx, ry, cw = 470, 120, 120
    s.rich(rx, ry - 50, 'L1（A 类，堆 1）：只按字号落位，不取模', 15, 'start', NAVY, 700)
    beat_of = {a: i for i, (_, _, a) in enumerate(RING)}
    for i, row in enumerate(range(RING_BASE, RING_BASE + RING_L)):
        hit = row in beat_of
        s.cell(rx + i * cw, ry, cw - 8, 50, f'字 {row}', fill=(C_LEFT if hit and beat_of[row] >= 2 else C_LO) if hit else 'white', size=14)
        if hit:
            s.rich(rx + i * cw + (cw - 8) / 2, ry - 14, f'第 {beat_of[row]} 拍', 13, 'middle', GREY, 600)
    s.red(rx, ry + 90, '第 2 拍起字号回到环首 20：取模在 CCU 完成，L1 不知道环长', 15)
    s.save('FIG-L1_SRAM-RING.svg')


# ---------------- 字的落位（真实 k、m 分组） ----------------
def _grid2(s, mp, nbank, ndep, x0, y0, label):
    cw, ch, rh = 92, 50, 60
    for b in range(nbank):
        s.rich(x0 + b * 2 * cw + cw - 4, y0 - 26, f'bank {b}', 15, 'middle', GREY, 600)
    for d in range(ndep):
        y = y0 + d * rh
        s.rich(x0 - 14, y + ch / 2, f'深度 {d}', 15, 'end')
        for b in range(nbank):
            for h in (0, 1):
                j, sg = mp[(b, h, d)]
                top, bot = label(j, sg)
                fill = [C_W, '#f6e3b0', C_KEEP, C_SIDE][sg % 4]
                xx = x0 + (2 * b + h) * cw
                s.rect(xx, y, cw - 6, ch, fill=fill)
                s.rich(xx + (cw - 6) / 2, y + 16, top, 13, 'middle')
                s.rich(xx + (cw - 6) / 2, y + 35, bot, 12, 'middle', GREY, 600)


def fig_map_w():
    """列字区：8 个 bank × 4 个深度，每格一个 32 B 存储字 = 一列的 64 个连续 k（两段）。"""
    s = SvgF5(1640, 470)
    x0, y0, bw, ch, rh = 120, 96, 186, 78, 92
    for g, rg in (('W0', range(0, 4)), ('W1', range(4, 8))):
        xa, xb = x0 + rg[0] * bw, x0 + (rg[-1] + 1) * bw - 8
        s.rich((xa + xb) / 2, 22, g, 16, 'middle', NAVY, 700)
        s.line([(xa, 36), (xb, 36)], color=NAVY, sw=1.4, marker=None)
    for b in range(8):
        s.rich(x0 + b * bw + (bw - 8) / 2, y0 - 26, f'bank {b}', 15, 'middle', GREY, 600)
    for d in range(4):
        y = y0 + d * rh
        s.rich(x0 - 14, y + ch / 2, f'深度 {d}', 15, 'end')
        for b in range(8):
            j, p = MAPW[(b, d)]
            xx, w = x0 + b * bw, bw - 8
            s.rect(xx, y, w, ch, fill=[C_W, C_KEEP][p])
            s.rich(xx + w / 2, y + 14, f'm{j}', 14, 'middle')
            s.rich(xx + w / 2, y + 32, f'k{64 * p}–{64 * p + 63}', 12, 'middle', GREY, 600)
            s.line([(xx, y + 44), (xx + w, y + 44)], color=GREY, sw=0.8, marker=None)
            s.line([(xx + w / 2, y + 44), (xx + w / 2, y + ch)], color=GREY, sw=0.8, marker=None)
            for h in (0, 1):
                s.rich(xx + w / 4 + h * w / 2, y + 61, f'段 {2 * p + h}', 12, 'middle', INK, 600)
    s.save('FIG-L1_SRAM-MAP-W.svg')


def fig_map_w_half():
    s = SvgF5(900, 330)
    _grid2(s, MAPH, 4, 4, 120, 60, lambda j, sg: (f'k{32 * sg + 2 * j}–{32 * sg + 2 * j + 1}', 'm0–15'))
    s.save('FIG-L1_SRAM-MAP-W-HALF.svg')


TFILL = [C_LO, C_KEEP, C_LEFT]


SEGFILL = {'头': C_SIDE, 't0': C_LO, 't1': C_KEEP, 't2': C_LEFT, '填 0': C_OFF, '空': C_OFF}


def fig_map_a():
    s = SvgF5(1420, 400)
    x0, cw, ch, rh = 120, 320, 60, 96
    for i, b in enumerate(A_BANKS):
        s.rich(x0 + i * cw + (cw - 12) / 2, 34, f'bank {b}（激活类口 {b - 8}）', 15, 'middle', GREY, 600)
    nd = -(-A_ROWS // len(A_BANKS))
    for d in range(nd):
        y = 70 + d * rh
        s.rich(x0 - 14, y + ch / 2, f'深度 {d}', 15, 'end')
        for i, b in enumerate(A_BANKS):
            xx = x0 + i * cw
            j = MAPA.get((b, d))
            if j is None:
                s.cell(xx, y, cw - 12, ch, '（下一个对象）', fill='white', size=13, color=GREY, dash='3,3')
                continue
            s.rich(xx, y - 8, f'字 {j}', 13, 'start', NAVY, 700)
            px = xx
            for name, a, z, nbytes in ROWSEG[j]:          # 一个存储字 32 B 按字节比例切段，可含两条记录
                w = (cw - 12) * nbytes / UNIT
                txt = name if name == '空' or w < 60 else f'{name} {a}–{z}'
                s.cell(px, y, w, ch, txt, fill=SEGFILL[name], size=12 if w > 60 else 11)
                px += w
    yb = 70 + nd * rh + 6
    s.rich(x0, yb, f'记录 {REC_LEN} B 紧挨：起点字节 {REC_START}，共 {OBJ_BYTES} B = {A_ROWS} 个存储字（末字空 {UNIT - OBJ_BYTES % UNIT} B，be 不选）；长度表 {REC_LEN} 由 CCU 写在字 {LT_ROW}（bank {LT_KEY[0]}、深度 {LT_KEY[1]}）', 13, 'start', INK, 500)
    s.rich(x0, yb + 24, f'读 token {RD_T}：字节 {REC_START[RD_T]} 起 {REC_LEN[RD_T]} B → 字 {RD_WORDS[0]}、{RD_WORDS[1]} 两次 1 拍读（bank {A_BANKS[RD_WORDS[0] % 4]}、{A_BANKS[RD_WORDS[1] % 4]}），激活类读口出口按 {RD_SHIFT} 移位', 13, 'start', INK, 500)
    s.save('FIG-L1_SRAM-MAP-A.svg')


# ---------------- 广播：bank → lane → 4 个 pod ----------------
def fig_lane_pick():
    s = SvgF5(1560, 640)
    x0, lw = 150, 84
    ytop, ylane, ypod0, podh = 40, 150, 260, 70
    for b in range(8):                               # bank 行
        xa, w = x0 + 2 * b * lw, 2 * lw - 8
        ms = PASS_COLS.get(b)
        if ms is None:
            s.cell(xa, ytop, w, 54, f'bank {b}：不读', fill=C_OFF, size=13, color=GREY)
            continue
        s.rect(xa, ytop, w, 54, fill=GFILL['W0' if b < 4 else 'W1'])
        s.rich(xa + w / 2, ytop + 18, f'bank {b}：读 ' + '、'.join(f'm{m}' for m in ms), 13, 'middle', INK, 600)
        s.rich(xa + w / 2, ytop + 38, f'（{"两" if len(ms) == 2 else "一"}个深度）', 12, 'middle', GREY, 600)
    s.rich(x0 - 14, ytop + 27, 'W 组读堆', 15, 'end')
    for lane in range(16):                           # lane 行
        xl = x0 + lane * lw
        cx = xl + (lw - 8) / 2
        c = BEAT0.get(lane)
        s.line([(cx, ytop + 54), (cx, ylane)], color=GREY, sw=1.2, marker=None)
        if c is None:
            s.cell(xl, ylane, lw - 8, 46, f'lane {lane}' + ('：空' if lane // 2 in PASS_COLS else ''), fill=C_OFF, size=12, color=GREY)
            continue
        m, pods = c
        mask = ''.join('1' if p in pods else '0' for p in (3, 2, 1, 0))
        s.rect(xl, ylane, lw - 8, 46, fill='white')
        s.rich(cx, ylane + 15, f'lane {lane}: m{m}', 12, 'middle')
        s.rich(cx, ylane + 33, f'掩码 {mask}', 11, 'middle', GREY, 600)
        if pods:                                     # 广播线：从 lane 竖直穿过 4 个 pod
            s.line([(cx, ylane + 46), (cx, ypod0 + 3 * (podh + 14) + 12)], color=INK, sw=1.6, marker=None)
    s.rich(x0 - 14, ylane + 23, 'lane', 15, 'end')
    for p in range(4):                               # pod 行
        y = ypod0 + p * (podh + 14)
        s.rich(x0 - 14, y + podh / 2, f'pod {p}', 16, 'end')
        for lane in range(16):
            xl = x0 + lane * lw
            c = BEAT0.get(lane)
            hit = c is not None and p in c[1]
            if hit:
                s.cell(xl, y + 12, lw - 8, podh - 24, f'槽 {lane}: m{c[0]}', fill=C_KEEP if len(c[1]) > 1 else C_W, size=12)
                s.rect(xl + (lw - 8) / 2 - 4, y + 6, 8, 8, fill=INK, sw=0)
            else:
                s.rect(xl, y + 12, lw - 8, podh - 24, fill='white', sw=0.8, dash='3,3', stroke=GREY)
    s.red(x0, ypod0 + 4 * (podh + 14) + 20, '、'.join(f'm{m}' for m in DEFER) + ' → 下一 pass', 15)
    s.save('FIG-L1_SRAM-LANE-PICK.svg')


# ---------------- 读口重组器逐拍（正文 §6，11-05 晚） ----------------
def _colread(log, nsrc, name):
    nb = 8 if nsrc == 1 else 4
    nbeat = len(log)
    s = SvgF5(1560, 368)
    x0, y0 = 230, 30
    cw = (1560 - 20 - x0) / nbeat
    rows = [('', 40), (f'{nb} 个 bank 读的深度', 64), ('拍初持有（每 bank）', 44), ('含本拍读入（每 bank）', 44), ('交出', 64)]
    ys, y = [], y0
    for lab, h in rows:
        ys.append(y)
        if lab:
            s.rich(x0 - 14, y + h / 2, lab, 14, 'end')
        y += h + 8
    peak = max(r['occ'] for r in log)
    for r in log:
        t = r['t']
        xx, w = x0 + t * cw, cw - 8
        s.cell(xx, ys[0], w, 40, f'拍 {t}', fill=C_SIDE, size=14)
        cols = cr_cols(nsrc, r['depth'])
        p = r['depth'] // (2 if nsrc == 1 else 4)
        s.rect(xx, ys[1], w, 64, fill=[C_W, C_KEEP, C_LO][p % 3])
        s.rich(xx + w / 2, ys[1] + 20, f'深度 {r["depth"]}', 14, 'middle', INK, 600)
        s.rich(xx + w / 2, ys[1] + 44, (f'm{cols[0]}、{cols[1]}…{cols[-1]}' if nsrc == 1 else
                                        f'm{cols[0]}、' + '、'.join(map(str, cols[1:]))), 12, 'middle', GREY, 600)
        s.cell(xx, ys[2], w, 44, f'{r["start"]} B', fill='white', size=13)
        s.cell(xx, ys[3], w, 44, f'{r["occ"]} B', fill=C_LEFT if r['occ'] == peak else 'white', size=13)
        out = r['out']
        if out is None:
            s.cell(xx, ys[4], w, 64, '—', fill=C_OFF, size=14, color=GREY)
            continue
        seg, half = out
        s.rect(xx, ys[4], w, 64, fill=[C_W, C_KEEP, C_LO][(seg // 2) % 3])
        s.rich(xx + w / 2, ys[4] + 20, f'段 {seg}', 14, 'middle', INK, 600)
        s.rich(xx + w / 2, ys[4] + 44, 'm0–15' if half is None else ('m0–7' if half == 0 else 'm8–15'), 12, 'middle', GREY, 600)
    if nsrc == 2:
        tb = next(r['t'] for r in log if r['t'] >= 2 and r['out'] is None)
        s.red(x0 + tb * cw + (cw - 8) / 2, ys[4] + 64 + 22, '起步气泡', 14, 'middle')
    s.save(name)


def fig_colread_1src():
    _colread(CR1, 1, 'FIG-L1_SRAM-COLREAD-1SRC.svg')


def fig_colread_2src():
    _colread(CR2, 2, 'FIG-L1_SRAM-COLREAD-2SRC.svg')


# ---------------- 两来源：两条总线、每半段一个 2:1 ----------------
def fig_two_src():
    s = SvgF5(1520, 470)
    # 两组 bank
    s.cell(150, 30, 420, 56, 'W0（4 个 bank）= 来源 A', fill=C_W, size=15)
    s.cell(900, 30, 420, 56, 'W1（4 个 bank）= 来源 B', fill=C_B, size=15)
    ya, yb = 150, 186                                # 总线 A：lane 0–7；总线 B：lane 8–15
    s.line([(360, 86), (360, ya)], marker=None, sw=2.4)
    s.line([(1110, 86), (1110, yb)], marker=None, sw=2.4, color='#7a3b6e')
    s.line([(60, ya), (1490, ya)], marker=None, sw=2.4)
    s.line([(60, yb), (1490, yb)], marker=None, sw=2.4, color='#7a3b6e')
    s.rich(40, ya, 'A', 15, 'middle', INK, 700)
    s.rich(40, yb, 'B', 15, 'middle', '#7a3b6e', 700)
    s.rich(1490, ya - 14, 'lane 0–7', 13, 'end', GREY, 600)
    s.rich(1490, yb + 16, 'lane 8–15', 13, 'end', GREY, 600)
    pw = 340
    for p in range(4):
        px = 60 + p * (pw + 20)
        s.rect(px, 300, pw, 130, fill='white', sw=1.6)
        s.rich(px + pw / 2, 412, f'pod {p}（{"来源 A，掩码 0001" if SRC_OF_POD[p] == "A" else "来源 B"}）', 14, 'middle')
        for half in (0, 1):
            hx = px + 14 + half * (pw / 2)
            hw = pw / 2 - 28
            fill = C_W if slot_select(p, half) == 'A' else C_B
            s.cell(hx, 330, hw, 54, f'槽 {8 * half}–{8 * half + 7}', fill=fill, size=14)
            mx = hx + hw / 2                          # 2:1 选择器
            s.out.append(f'<path d="M{mx - 34},{238} L{mx + 34},{238} L{mx + 22},{270} L{mx - 22},{270} Z" fill="white" stroke="{NAVY}" stroke-width="1.4"/>')
            s.rich(mx, 254, '2:1', 12, 'middle')
            s.line([(mx, 270), (mx, 330)], sw=1.8)
            sel = slot_select(p, half)
            for bus, yy, xo in (('A', ya, -20), ('B', yb, 20)):
                on = (bus == sel)
                s.line([(mx + xo, yy), (mx + xo, 238)], color=(INK if bus == 'A' else '#7a3b6e') if on else GREY,
                       sw=2.2 if on else 1.0, marker=None, dash=None if on else '3,3')
    s.save('FIG-L1_SRAM-TWO-SRC.svg')


# ---------------- A 类 4 / 8 bank 两种配置（正文 §1.6） ----------------
ABANK_CFG = {4: [8, 9, 10, 11], 8: [8, 9, 10, 11, 4, 5, 6, 7]}


def a_word(r, n):
    lst = ABANK_CFG[n]
    return lst[r % n], r // n


assert [a_word(r, 4) for r in range(8)] == [(8, 0), (9, 0), (10, 0), (11, 0), (8, 1), (9, 1), (10, 1), (11, 1)]
assert [a_word(r, 8)[1] for r in range(8)] == [0] * 8 and [a_word(r, 8)[0] for r in range(8, 16)] == ABANK_CFG[8]


def fig_abank_cfg():
    s = SvgF5(1520, 600)
    for k, n in enumerate((4, 8)):
        y = 20 + k * 290
        title = ('4 bank 配置（默认）：A 类 = bank 8–11，写集合口 4 道；W1 仍出权重 lane 8–15' if n == 4 else
                 '8 bank 配置：W1 整组改配给 A 类，写集合口 8 道；权重 lane 只剩 W0（lane 0–7，128 B/拍）')
        s.panel(10, y, 1500, 270, title, 15)
        s.cell(30, y + 90, 200, 110, '写者入口 FIFO ≤ 9 条', fill=C_SIDE, size=14)
        s.rich(130, y + 220, '（两种配置相同）', 13, 'middle', GREY, 600)
        s.cell(270, y + 70, 150, 150, f'A 类写集合器', fill=C_LO, size=14)
        s.line([(230, y + 145), (270, y + 145)])
        x0, cw = 500, 120
        for i, b in enumerate(ABANK_CFG[n]):
            cx = x0 + i * cw
            s.rich(cx + 58, y + 68, f'道 {i}', 13, 'start', NAVY, 700)
            s.line([(cx + 50, y + 44), (cx + 50, y + 92)], sw=1.6)
            s.cell(cx, y + 92, 100, 40, f'bank {b}', fill=GFILL[group_of(b)], size=13)
            for d in range(2):
                words = [r for r in range(16 if n == 8 else 8) if a_word(r, n) == (b, d)]
                s.cell(cx, y + 140 + d * 44, 100, 38, '、'.join(f'字 {r}' for r in words), fill='white', size=12)
        s.line([(420, y + 145), (470, y + 145), (470, y + 44), (x0 + (n - 1) * cw + 50, y + 44)], marker=None, sw=1.6)
        s.rich(x0 - 12, y + 159, '深度 0', 12, 'end', GREY, 600)
        s.rich(x0 - 12, y + 203, '深度 1', 12, 'end', GREY, 600)
        if n == 4:
            for i, b in enumerate((4, 5, 6, 7)):
                cx = x0 + (4 + i) * cw
                s.cell(cx, y + 92, 100, 40, f'bank {b}', fill=GFILL['W1'], size=13, dash='4,3')
            s.rich(x0 + 6 * cw + 50, y + 150, 'W 类（W1）：出 lane 8–15', 13, 'middle', GREY, 600)
    s.save('FIG-L1_SRAM-ABANK-CFG.svg')

# ---------------- 按列到达（11-05：NWB 攒整行再写） ----------------
def _words(lst):
    """列字清单按列归并：m0 段 0–3。"""
    if not lst:
        return '—'
    by = {}
    for c, g in lst:
        by.setdefault(c, []).append(g)
    out = []
    for c, gs in by.items():
        gs = sorted(gs)
        out.append(f'{c} 段 {gs[0]}–{gs[-1]}' if len(gs) > 1 and gs == list(range(gs[0], gs[-1] + 1)) else f'{c} 段 ' + '、'.join(map(str, gs)))
    return '；'.join(out)


def _rows(lst):
    return '；'.join(f'bank {b} 段 {g}（{pr}）' for b, g, pr in lst) if lst else '—'


def _retired_fig_colarrive():   # 11-05 晚退役：NWB 配对暂存撤销（V18-L1-09，一个存储字 = 一列 64 个连续 k，整字直写）
    s = SvgF5(1360, 640)
    cols = [('拍', 70), ('到达（32 B = 同列相邻两段）', 300), ('写出整字（每 bank ≤ 1 个）', 330), ('NWB 暂存的未配对列字', 300), ('已拼成、待写的整字', 330)]
    x, y0, xs = 20, 30, []
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 8, 40, name, fill=C_SIDE, size=14)
        x += w
    for i, (t, arr, wr, held, ready) in enumerate(LOG):
        y = y0 + 52 + i * 52
        vals = [str(t), _words(arr), _rows(wr), _words(held), _rows(ready)]
        for k, ((name, w), xx, v) in enumerate(zip(cols, xs, vals)):
            fill = C_LEFT if k in (3, 4) and v != '—' else ('white' if k != 2 or v == '—' else C_KEEP)
            s.cell(xx, y, w - 8, 42, v, fill=fill, size=12)
    s.save('FIG-L1_SRAM-COLARRIVE.svg')


def _retired_md():   # 11-05 晚随 COLARRIVE 一并退役
    print('| 拍 | 到达 | 写出整字 | NWB 暂存的未配对列字 | 待写整字 |')
    print('|---|---|---|---|---|')
    for t, arr, wr, held, ready in LOG:
        print(f'| {t} | {_words(arr)} | {_rows(wr)} | {_words(held)} | {_rows(ready)} |')


if __name__ == '__main__':
    old = OUT / 'figs' / 'FIG-L1_SRAM-SWAP.svg'
    if old.exists():
        old.unlink()                                  # 由 PINGPONG 取代
    fig_banks()
    fig_pingpong()
    fig_ring()
    fig_map_w()
    fig_map_w_half()
    fig_map_a()
    fig_abank_cfg()
    fig_lane_pick()
    fig_two_src()
    fig_colread_1src()
    fig_colread_2src()
