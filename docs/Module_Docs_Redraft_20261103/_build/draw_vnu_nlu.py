"""VNU 非线性单元（NLU）需求篇（11-04 重写稿）的四张图。Owner: WangYizhao · 2026-11-04
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_vnu_nlu.py [--md]
输出（figs/）：
  FIG-VNU_NLU-CONN            对外连接：VNU 组框内 NLU 与 SEL、QNT、SMP / LOSS / OPT；框外 MXU 出口级、本核 CCU、
                              IDN（落地 L1）、CRU（命令网）；L1 经 VNU 的 RRAM 口（11-05 同步传输协议篇）
  FIG-VNU_NLU-NORM-SPLIT      2 个核各持 4 个通道的 RMSNorm：部分和 → 合并 → 回送 → 各自缩放
  FIG-VNU_NLU-ONLINE-SOFTMAX  1 个查询行、2 个更新组（每组 4 个 key，到达组 2 个 key）：m_run、p~、α、l、O
  FIG-VNU_NLU-STREAM-SUM      6 个 key、区块长 4、2 个通道：逐通道 sum / min / max 的流式状态与区块输出
脚本断言：
  NORM-SPLIT：两核部分和合并后的缩放结果 = 单核对整条 8 通道向量直接计算的结果。
  ONLINE-SOFTMAX：按到达组更新 m_run、按更新组统一基准与重标定后的 O / l = 一次性 softmax 加权和（浮点容差内）；
                  l = 一次性 softmax 的分母（以最终 m_run 为基准）。
  STREAM-SUM：区块 0 的流式 sum / min / max 与成批计算相同，均值 = sum × 2^-2；
              区块 1 未收满的部分状态写出、读回后再收 2 个 key，结果与对这 4 个 key 成批计算相同。
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize, SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, INK, C_OFF, C_KEEP, C_HI, C_LO, C_LEFT, C_ACC, C_SIDE  # noqa: E402

OUT = HERE.parent


def fmt(v, nd=3):
    """数值显示：整数不带小数；有限小数去掉末尾 0；其余保留 nd 位；负号用 −。"""
    if abs(v - round(v)) < 1e-12:
        s = str(int(round(v)))
    else:
        s = f'{v:.{nd}f}'
        if abs(v - round(v, nd)) < 1e-12:
            s = s.rstrip('0').rstrip('.')
    return s.replace('-', '−')


def pair(v):
    return '(' + ', '.join(fmt(a) for a in v) + ')'


# ---------------- RMSNorm 两核切分（正文 §3.2） ----------------
D_NORM = 8                                   # 整条向量 8 个通道，核 0 持通道 0–3，核 1 持通道 4–7
EPS = 0.25                                   # 只为手算方便
X = [1, -2, 3, 0, 2, 2, -2, 2]
GAMMA = [1, 0.5, 2, 1, 1, 1, 0.5, 2]
CORES = [(0, 4), (4, 8)]
PART = [sum(x * x for x in X[a:b]) for a, b in CORES]           # 各核平方和部分和
MERGED = PART[0] + PART[1]                                       # CRU 合并
R_SCALE = 1 / math.sqrt(MERGED / D_NORM + EPS)                   # rsqrt(合并值 / d + ε)，回送两核
Y_SPLIT = [X[i] * R_SCALE * GAMMA[i] for i in range(D_NORM)]     # 各核只缩放自己的搬运引擎
Y_WHOLE = [X[i] / math.sqrt(sum(x * x for x in X) / D_NORM + EPS) * GAMMA[i] for i in range(D_NORM)]
assert PART == [14, 16] and MERGED == 30 and R_SCALE == 0.5
assert Y_SPLIT == Y_WHOLE == [0.5, -0.5, 3.0, 0.0, 1.0, 1.0, -0.5, 2.0]

# ---------------- 在线 softmax（正文 §3.4） ----------------
N_U, N_ADM = 2, 4                            # 到达组 2 个 key，更新组 4 个 key
A = [1, 2, 3, 0, 2, 4, 0, 3]                 # 精确分数（一个查询行对 8 个录取 key）
V = [(1, 0), (0, 1), (2, 1), (1, 1), (0, 2), (1, 0), (3, 3), (0, 1)]   # 每个 key 的 V 行，取 2 维
D_V = 2

m_run = -math.inf
M_AFTER = []           # 每个 key 所在到达组处理完后的 m_run
P_ARR = []             # 到达时以当时 m_run 算的 p~
M_OLD = []
for g0 in range(0, len(A), N_U):
    grp = range(g0, g0 + N_U)
    m_run = max(m_run, max(A[j] for j in grp))
    for j in grp:
        P_ARR.append(math.exp(A[j] - m_run))
        M_OLD.append(m_run)
        M_AFTER.append(m_run)

P_UNI, M_TILE, ALPHA, L_ROW, TILE, O_ROW = [], [], [], [], [], []
l_run, o_run, m_prev = 0.0, [0.0] * D_V, -math.inf
for t0 in range(0, len(A), N_ADM):
    keys = range(t0, t0 + N_ADM)
    m_tile = M_OLD[t0 + N_ADM - 1]                               # 本更新组最后一个精确分数到达后的 m_run
    pu = [P_ARR[j] * math.exp(M_OLD[j] - m_tile) for j in keys]  # 早到 p~ 统一到本组基准
    P_UNI += pu
    alpha = math.exp(m_prev - m_tile) if m_prev > -math.inf else 0.0
    tile = [sum(pu[i] * V[t0 + i][c] for i in range(N_ADM)) for c in range(D_V)]
    l_run = alpha * l_run + sum(pu)
    o_run = [alpha * o_run[c] + tile[c] for c in range(D_V)]
    M_TILE.append(m_tile); ALPHA.append(alpha); L_ROW.append(l_run); TILE.append(tile); O_ROW.append(list(o_run))
    m_prev = m_tile
O_FINAL = [o / l_run for o in o_run]

# 一次性 softmax 加权和
_mx = max(A)
_w = [math.exp(a - _mx) for a in A]
_z = sum(_w)
O_REF = [sum(_w[j] * V[j][c] for j in range(len(A))) / _z for c in range(D_V)]
assert all(abs(O_FINAL[c] - O_REF[c]) < 1e-12 for c in range(D_V))
assert abs(l_run - _z) < 1e-12                                   # 行和 = 以最终 m_run 为基准的分母
assert M_AFTER == [2, 2, 3, 3, 4, 4, 4, 4] and M_TILE == [3, 4]
assert ALPHA[0] == 0.0 and abs(ALPHA[1] - math.exp(-1)) < 1e-15
assert abs(P_UNI[0] - math.exp(-2)) < 1e-15 and abs(P_ARR[0] - math.exp(-1)) < 1e-15   # k0 早到，统一时乘 e^(2-3)

# ---------------- 流式区块摘要（正文 §3.5） ----------------
L_BLK = 4
KEYS = [(1, 4), (3, -2), (2, 0), (-2, 6), (5, 1), (-1, 3)]     # 6 个 key，每个 2 个通道
N_CH = 2


def stream(state, k):
    """一个 key 进来：逐通道 sum / min / max。state = (sum, min, max) 或 None。"""
    if state is None:
        return (list(k), list(k), list(k))
    s, lo, hi = state
    return ([s[c] + k[c] for c in range(N_CH)], [min(lo[c], k[c]) for c in range(N_CH)],
            [max(hi[c], k[c]) for c in range(N_CH)])


def batch(keys):
    return ([sum(k[c] for k in keys) for c in range(N_CH)], [min(k[c] for k in keys) for c in range(N_CH)],
            [max(k[c] for k in keys) for c in range(N_CH)])


SNAP = []              # 每个 key 进来后的状态（区块边界清零）
st = None
for j, k in enumerate(KEYS):
    if j % L_BLK == 0:
        st = None
    st = stream(st, k)
    SNAP.append(st)
BLK0 = SNAP[L_BLK - 1]
assert BLK0 == batch(KEYS[:L_BLK])
MEAN0 = [s * 2 ** -2 for s in BLK0[0]]                           # 均值 = sum × 2^-log2(L_blk)，只改指数
assert MEAN0 == [s / L_BLK for s in BLK0[0]] == [1.0, 2.0]
PART1 = SNAP[-1]                                                  # 区块 1 只收到 2 个 key
assert PART1 == batch(KEYS[L_BLK:]) == ([4, 4], [-1, 1], [5, 3])
_later = [(0, 2), (2, -1)]                                        # 下次读回后续到的 2 个 key（图中不画）
_st = PART1
for k in _later:
    _st = stream(_st, k)
assert _st == batch(KEYS[L_BLK:] + _later)

# ---------------- 矩阵状态递推（正文 §3.6，GDN，11-05 夜） ----------------
# 状态 S 为 d_k × d_v（k 行、v 列）；每个 token：u = kᵀS，w = β(v − αu)，S' = αS + k wᵀ，o = qᵀS'
S0 = [[1.0, 2.0], [0.0, 1.0]]
GDN_TOK = [dict(k=(1, 0), v=(3, 1), q=(1, 1), a=0.5, b=0.5),
           dict(k=(0, 1), v=(2, 2), q=(1, 0), a=1.0, b=1.0)]
D_K = D_VS = 2


def gdn_step(S, t):
    k, v, q, a, b = t['k'], t['v'], t['q'], t['a'], t['b']
    u = [sum(k[i] * S[i][j] for i in range(D_K)) for j in range(D_VS)]
    w = [b * (v[j] - a * u[j]) for j in range(D_VS)]
    Sn = [[a * S[i][j] + k[i] * w[j] for j in range(D_VS)] for i in range(D_K)]
    o = [sum(q[i] * Sn[i][j] for i in range(D_K)) for j in range(D_VS)]
    # 直接公式：S' = α (I − β k kᵀ) S + β k vᵀ
    M = [[a * ((1 if i == r else 0) - b * k[i] * k[r]) for r in range(D_K)] for i in range(D_K)]
    Sd = [[sum(M[i][r] * S[r][j] for r in range(D_K)) + b * k[i] * v[j] for j in range(D_VS)] for i in range(D_K)]
    assert all(abs(Sn[i][j] - Sd[i][j]) < 1e-12 for i in range(D_K) for j in range(D_VS))
    return u, w, Sn, o


GDN_SNAP = []
_S = S0
for _t in GDN_TOK:
    _u, _w, _Sn, _o = gdn_step(_S, _t)
    GDN_SNAP.append((_S, _u, _w, _Sn, _o))
    _S = _Sn
assert GDN_SNAP[0][1] == [1, 2] and GDN_SNAP[0][2] == [1.25, 0] and GDN_SNAP[0][3] == [[1.75, 1], [0, 0.5]]
assert GDN_SNAP[0][4] == [1.75, 1.5]
assert GDN_SNAP[1][3] == [[1.75, 1], [2, 2]] and GDN_SNAP[1][4] == [1.75, 1]
_k2 = GDN_TOK[1]['k']
assert [sum(_k2[i] * GDN_SNAP[1][3][i][j] for i in range(D_K)) for j in range(D_VS)] == list(GDN_TOK[1]['v'])  # β=α=1：写后 kᵀS = v


# ---------------- 图 1：对外连接 ----------------
def _retired_fig_conn():  # 11-05 起由 draw_vnu_conn.py 统一外框生成，本函数不再调用
    # 虚线框 = VNU 组；框内是 NLU 与直接往来的 SEL、QNT、SMP / LOSS / OPT；跨出框的连线都是 VNU 组的对外接口，
    # 访问 L1 与上行经 VNU 的共用口（口的个数与共享方式由 VNU 集成篇定义，用户 11-04）
    f = Figure('VNU_NLU-CONN', '', width=1582, height=1218, out_dir=OUT, max_crossings=2)
    f.container('vnu', 462, 196, 994, 784, 'VNU 组')
    # 11-05 晚第二轮：写 L1 = 向 A 类写集合器里本单元的入口 FIFO 写、wr_stall 回本单元
    # 11-05 按传输协议篇同步：RRAM 口、stall_vnu；IDN 落地 L1 后读入；与 CRU 的标量走命令网；撤 ULB 与"VNU 上行口"
    f.block('ccu', 714, 28, 308, 126, '本核 CCU', '指令 / 参数表 / 地址推理', kind='control')
    f.block('exit', 42, 280, 266, 126, 'MXU 出口级', '', kind='compute')
    f.block('idn', 42, 1064, 266, 84, 'IDN', '经 NWB 落地 L1', kind='external')
    # 11-05 第三轮（V18-TP-21）：交 CRU 的标量经 CCU 中转，NLU 在命令网上无端口；CRU 只与 CCU 相连
    f.block('cru', 42, 28, 266, 126, 'CRU', '命令网（FP32）', kind='external')
    # 11-05 夜：GDN 状态更新暂不写入 NLU（留给 MXU / NLU / CCU 设计者），连接图保持五种运算形态
    f.block('nlu', 714, 266, 308, 462, 'NLU', '逐元素 / 归约与归一化\n二维旋转 / 在线 softmax\n流式累加', kind='function')
    f.block('sel', 1162, 266, 266, 98, 'SEL', '', kind='function')
    f.block('qnt', 1162, 434, 266, 98, 'QNT', '', kind='function')
    f.block('sol', 1162, 602, 266, 112, 'SMP / LOSS / OPT', '分时借用元件', kind='function')
    f.block('l1p', 714, 840, 308, 84, 'VNU 的 RRAM 口', '激活类读口 / 写集合器 FIFO', kind='external')
    f.block('l1', 714, 1064, 308, 84, 'L1 的 A 类空间', '行状态 / 暂存 / 嵌入行', kind='memory')
    f.net('c_cmd', 'ccu', 'nlu', '指令 / 参数', kind='ctrl')
    f.net('o_ccu', 'nlu', 'ccu', 'stall_vnu', kind='ctrl')
    f.net('o_cru', 'ccu', 'cru', '部分值', kind='ctrl')
    f.net('i_cru', 'cru', 'ccu', '合并值', kind='ctrl')
    f.net('i_exit', 'exit', 'nlu', '分数 / P×V / q、k / x′')
    f.net('o_exit', 'nlu', 'exit', '夹心归一化缩放值')
    f.net('i_idn', 'idn', 'l1', '嵌入行 + 两标量')
    f.net('o_sel', 'nlu', 'sel', '评分 / 统计量')
    f.net('i_sel', 'sel', 'nlu', '录取位图')
    f.net('o_qnt', 'nlu', 'qnt', '待量化向量')
    f.net('i_qnt', 'qnt', 'nlu', '量化结果')
    f.net('b_sol', 'sol', 'nlu', '分时借用')
    f.net('m_req', 'nlu', 'l1p', '写 din + 长度 → FIFO')
    f.net('m_rsp', 'l1p', 'nlu', '读出（1 拍）/ wr_stall')
    f.net('p_req', 'l1p', 'l1', '')
    f.net('p_rsp', 'l1', 'l1p', '')
    xs, attempt = f.save()
    print(f.d['id'], 'crossings', xs, 'attempt', attempt)
    finalize(f)
    # 本图无同网分支，finalize 不改图例；与 SEL 图一致写"数据"
    p = OUT / 'figs' / 'FIG-VNU_NLU-CONN.svg'
    p.write_bytes(p.read_bytes().decode('utf-8').replace('━━ 主要数据', '━━ 数据').encode('utf-8'))


# ---------------- 图 2：RMSNorm 两核切分 ----------------
def fig_norm_split():
    s = SvgF5(1140, 560)
    x0, cw, ch, gap = 250, 100, 42, 36
    xs = [x0 + i * cw + (gap if i >= 4 else 0) for i in range(D_NORM)]
    w4 = 4 * cw - 10
    half = [(xs[0], w4), (xs[4], w4)]
    full_w = xs[-1] + cw - 10 - xs[0]
    # 表头
    s.rich(half[0][0] + w4 / 2, 24, '核 0（通道 0–3）', 16, 'middle')
    s.rich(half[1][0] + w4 / 2, 24, '核 1（通道 4–7）', 16, 'middle')
    for i in range(D_NORM):
        s.rich(xs[i] + (cw - 10) / 2, 56, f'通道 {i}', 14, 'middle', GREY, 600)
    y = 76
    rows_y = {}

    def row(label, vals, fill='white'):
        nonlocal y
        rows_y[label] = y
        s.rich(x0 - 16, y + ch / 2, label, 15, 'end')
        for i in range(D_NORM):
            s.cell(xs[i], y, cw - 10, ch, vals[i], fill=fill if isinstance(fill, str) else fill[i], size=15)
        y += ch + 16

    row('x', [fmt(v) for v in X])
    row('x^{2}', [fmt(v * v) for v in X], C_OFF)
    # 部分和
    s.rich(x0 - 16, y + ch / 2, '各核部分和 Σx^{2}', 15, 'end')
    for c, (hx, hw) in enumerate(half):
        s.cell(hx, y, hw, ch, f'核 {c}：{PART[c]}', fill=C_LEFT, size=15)
    y_part = y
    y += ch + 34
    # 合并
    s.rich(x0 - 16, y + ch / 2, 'CRU 合并', 15, 'end')
    s.cell(xs[0], y, full_w, ch, f'{PART[0]} + {PART[1]} = {MERGED}', fill=C_ACC, size=15)
    for hx, hw in half:
        s.line([(hx + hw / 2, y_part + ch), (hx + hw / 2, y - 2)])
    y_merge = y
    y += ch + 34
    # 回送
    s.rich(x0 - 16, y + ch / 2, '回送两核', 15, 'end')
    s.cell(xs[0], y, full_w, ch, f'r = rsqrt({MERGED} / {D_NORM} + {fmt(EPS)}) = {fmt(R_SCALE)}', fill=C_LO, size=15)
    s.line([(xs[0] + full_w / 2, y_merge + ch), (xs[0] + full_w / 2, y - 2)])
    y_ret = y
    y += ch + 30
    for hx, hw in half:
        s.line([(hx + hw / 2, y_ret + ch), (hx + hw / 2, y - 2)])
    row('γ', [fmt(v) for v in GAMMA])
    row('y = x · r · γ', [fmt(v) for v in Y_SPLIT], C_KEEP)
    mid = (half[0][0] + half[0][1] / 2 + half[1][0] + half[1][1] / 2) / 2
    s.red(mid, y_ret + ch + 15, '回送到齐后才缩放', 14, 'middle')
    assert y + 10 <= s.h
    s.save('FIG-VNU_NLU-NORM-SPLIT.svg')


# ---------------- 图 3：在线 softmax ----------------
def fig_online_softmax():
    x0, cw, ch = 290, 104, 40
    # 到达组之间留 8 px，更新组之间留 34 px
    xs = []
    for j in range(len(A)):
        xs.append(x0 + j * cw + (j // N_U) * 8 + (j // N_ADM) * 26)
    s = SvgF5(xs[-1] + cw + 40, 720)
    tw = [xs[t * N_ADM + N_ADM - 1] + cw - 10 - xs[t * N_ADM] for t in range(2)]
    for t in range(2):
        s.rich(xs[t * N_ADM] + tw[t] / 2, 22, f'更新组 {t + 1}', 16, 'middle')
    for j in range(len(A)):
        s.rich(xs[j] + (cw - 10) / 2, 52, f'k{j}', 14, 'middle', GREY, 600)
    for g in range(len(A) // N_U):
        a, b = xs[g * N_U], xs[g * N_U + N_U - 1] + cw - 10
        s.out.append(f'<path d="M{a},68 L{b},68" stroke="{GREY}" stroke-width="2"/>')
    y = 80

    def row(label, vals, fill='white', size=15):
        nonlocal y
        s.rich(x0 - 16, y + ch / 2, label, 15, 'end')
        for j in range(len(A)):
            s.cell(xs[j], y, cw - 10, ch, vals[j], fill=fill if isinstance(fill, str) else fill[j], size=size)
        y += ch + 12

    def grow(label, vals, fill='white', size=15):
        nonlocal y
        s.rich(x0 - 16, y + ch / 2, label, 15, 'end')
        for t in range(2):
            s.cell(xs[t * N_ADM], y, tw[t], ch, vals[t], fill=fill, size=size)
        yy = y
        y += ch + 12
        return yy

    row('精确分数 A', [fmt(a) for a in A])
    row('V 行（2 维）', [pair(v) for v in V], C_OFF, 14)
    row('到达组后 m_{run}', [fmt(m) for m in M_AFTER])
    row('到达时 p̃', [fmt(p) for p in P_ARR], [C_LEFT if abs(P_ARR[j] - P_UNI[j]) > 1e-12 else 'white' for j in range(len(A))])
    y_uni = y
    row('统一基准后 p̃', [fmt(p) for p in P_UNI], [C_KEEP if abs(P_ARR[j] - P_UNI[j]) > 1e-12 else 'white' for j in range(len(A))])
    s.red(xs[0], y + 7, 'k0、k1 乘 e^{2−3}', 14)
    y += 26
    grow('本组基准 m_{tile}', [fmt(m) for m in M_TILE], C_SIDE)
    grow('α', ['首组：l、O 从 0 起', f'e^{{{fmt(M_TILE[0])}−{fmt(M_TILE[1])}}} = {fmt(ALPHA[1])}'], C_SIDE)
    grow('行和 l', [f'{fmt(L_ROW[0])}', f'{fmt(ALPHA[1])} × {fmt(L_ROW[0])} + {fmt(L_ROW[1] - ALPHA[1] * L_ROW[0])} = {fmt(L_ROW[1])}'], C_ACC)
    grow('(P×V)_{tile}', [pair(TILE[0]), pair(TILE[1])], C_LO)
    grow('O', [pair(O_ROW[0]), f'{fmt(ALPHA[1])} × O + (P×V)_{{tile}} = {pair(O_ROW[1])}'], C_ACC)
    y += 6
    s.rich(x0 - 16, y + ch / 2, '末组后 O / l', 15, 'end')
    s.cell(xs[0], y, xs[-1] + cw - 10 - xs[0], ch,
           f'{pair(O_ROW[1])} / {fmt(L_ROW[1])} = {pair(O_FINAL)}', fill=C_KEEP, size=15)
    y_fin = y
    y += ch + 12
    s.red(xs[-1] + cw - 10, y_fin + ch + 16, '与一次性计算相同', 14, 'end')
    assert y_fin + ch + 30 <= s.h
    s.save('FIG-VNU_NLU-ONLINE-SOFTMAX.svg')


# ---------------- 图 4：流式区块摘要 ----------------
def fig_stream_sum():
    x0, cw, ch = 220, 112, 40
    ow = 150                                  # 输出列宽
    xs = [x0 + j * cw for j in range(L_BLK)]
    x_out0 = xs[-1] + cw + 8
    xs += [x_out0 + ow + 28 + j * cw for j in range(len(KEYS) - L_BLK)]
    x_part = xs[-1] + cw + 8
    W = x_part + ow + 30
    s = SvgF5(W, 340)
    s.rich((xs[0] + xs[L_BLK - 1] + cw - 10) / 2, 22, '区块 0（K0–K3）', 16, 'middle')
    s.rich((xs[L_BLK] + xs[-1] + cw - 10) / 2, 22, '区块 1（K4–K5）', 16, 'middle')
    for j in range(len(KEYS)):
        s.rich(xs[j] + (cw - 10) / 2, 52, f'K{j} 到达后', 14, 'middle', GREY, 600)
    s.rich(x_out0 + (ow - 10) / 2, 52, '区块 0 输出', 14, 'middle', NAVY, 700)
    s.rich(x_part + (ow - 10) / 2, 52, '未收满状态', 14, 'middle', NAVY, 700)
    rows = [('key 向量（2 通道）', [pair(k) for k in KEYS], None, None),
            ('逐通道 sum', [pair(st[0]) for st in SNAP], f'均值 {pair(MEAN0)}', pair(PART1[0])),
            ('逐通道 min', [pair(st[1]) for st in SNAP], pair(BLK0[1]), pair(PART1[1])),
            ('逐通道 max', [pair(st[2]) for st in SNAP], pair(BLK0[2]), pair(PART1[2]))]
    y = 72
    for r, (lab, vals, out, part) in enumerate(rows):
        s.rich(x0 - 16, y + ch / 2, lab, 15, 'end')
        for j in range(len(KEYS)):
            s.cell(xs[j], y, cw - 10, ch, vals[j], fill=C_OFF if r == 0 else 'white', size=15)
        if out is not None:
            s.cell(x_out0, y, ow - 10, ch, out, fill=C_KEEP, size=15)
            s.cell(x_part, y, ow - 10, ch, part, fill=C_LEFT, size=15)
        y += ch + 14
    s.red(x_out0 + (ow - 10) / 2, y + 10, '均值只改指数', 14, 'middle')
    s.red(x_part + ow - 10, y + 10, '写出，下次续累加', 14, 'end')
    s.save('FIG-VNU_NLU-STREAM-SUM.svg')


# ---------------- 图 5（已退役 11-05 夜）：矩阵状态递推（GDN） ----------------
# 用户 11-05 夜改判：GDN 状态更新暂不写实现需求，留给 MXU / NLU / CCU 设计者；本图不再生成，
# SVG 已移到 figs/_retired_20261105/。函数与上方断言保留，供以后设计时复用。
def _retired_fig_gdn_state():
    cw, ch = 96, 40
    # 各列起点：S_{t−1}（2×2）、u、w、S_t（2×2）、o
    col = {'S0': 190, 'u': 470, 'w': 700, 'S1': 960, 'o': 1240}
    W = col['o'] + 2 * cw + 30
    s = SvgF5(W, 430)
    y = 20
    heads = [('S0', 'S_{t−1}（读一堆）'), ('u', 'u = k^{T}S_{t−1}'), ('w', 'w = β(v − αu)'),
             ('S1', 'S_{t} = αS_{t−1} + k w^{T}'), ('o', 'o = q^{T}S_{t}')]
    for key, lab in heads:
        s.rich(col[key] + cw - 5, y + 12, lab, 15, 'middle', NAVY, 700)
    y += 36
    for n, (t, (S, u, w, Sn, o)) in enumerate(zip(GDN_TOK, GDN_SNAP)):
        s.rich(24, y + 10, f'token {n + 1}：k = {pair(t["k"])}，v = {pair(t["v"])}，q = {pair(t["q"])}，'
                           f'α = {fmt(t["a"])}，β = {fmt(t["b"])}', 15, 'start')
        y += 26
        for j in range(D_VS):
            for key in ('S0', 'S1'):
                s.rich(col[key] + j * cw + (cw - 8) / 2, y + 10, f'v 列 {j}', 13, 'middle', GREY, 600)
        y += 20
        y_m = y
        for i in range(D_K):
            s.rich(col['S0'] - 12, y + ch / 2, f'k 行 {i}（k_{{{i}}} = {fmt(t["k"][i])}）', 14, 'end')
            for j in range(D_VS):
                s.cell(col['S0'] + j * cw, y, cw - 8, ch, fmt(S[i][j]), fill=C_ACC, size=15)
                changed = abs(Sn[i][j] - S[i][j]) > 1e-12
                s.cell(col['S1'] + j * cw, y, cw - 8, ch, fmt(Sn[i][j]), fill=C_KEEP if changed else 'white', size=15)
            y += ch + 8
        yv = y_m + (ch + 8) / 2
        for key, vec, fill in (('u', u, C_OFF), ('w', w, C_LO), ('o', o, C_KEEP)):
            for j in range(D_VS):
                s.cell(col[key] + j * cw, yv, cw - 8, ch, fmt(vec[j]), fill=fill, size=15)
        if n == 1:
            s.red(col['S1'] + 2 * cw - 8, y + 16, '写后 kᵀS = v', 14, 'end')
        y += 40
    assert y <= s.h
    s.save('FIG-VNU_NLU-GDN-STATE.svg')


def md():
    print('NORM-SPLIT', PART, MERGED, R_SCALE, Y_SPLIT)
    print('ONLINE m_after', M_AFTER, 'p_arr', [round(p, 4) for p in P_ARR], 'p_uni', [round(p, 4) for p in P_UNI])
    print('ONLINE m_tile', M_TILE, 'alpha', ALPHA, 'l', L_ROW, 'tile', TILE, 'O', O_ROW, 'O/l', O_FINAL, 'ref', O_REF)
    print('STREAM', SNAP, MEAN0, PART1)


if __name__ == '__main__':
    fig_norm_split()
    fig_online_softmax()
    fig_stream_sum()
    if '--md' in sys.argv:
        md()
