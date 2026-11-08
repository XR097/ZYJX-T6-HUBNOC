"""HUB_NOC 篇的四张图。Owner: WangYizhao · 2026-11-06
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_hub_noc.py
输出（figs/）：
  FIG-HUB_NOC-ARCH-DATA  PPT 式架构图（数据）：H2C 道 0–3（L2 读出 → 多播分叉点）、C2H 通路 × 4（直通 L2WP）；对端 L2、MAE_ENG、四核；数据线 D1 / D2 / D4 / D5
  FIG-HUB_NOC-ARCH-CTRL  PPT 式架构图（命令，含地址与使能，不细分）：同外框与对端；C1 / C4 / C5 / C7
  11-07 晚（V18-CRU-07、TP-55 / 56）：撤 MUX、C2H 去 MAE_CRU 的分支、D3 / D6 / C2 / C3 / C6，编号不重排；MAE_CRU 不再画（只经 NI 进出 L2）
  FIG-HUB_NOC-MCAST      数值小例：H2C 道 0 一个 6 拍单位多播到核 0、核 2，分叉点已取位与各核分支占用（模型 mcast_fork_sim.py）
  FIG-HUB_NOC-ACK        数值小例：两条指令交替用 H2C 道 0，四核 LDP 回的写入握手按 src 归并
架构图复用 draw_tp_arch.py 的 Fig 类与自检（只 import，不改它）；数值图用 svgkit_num.Svg，数值由脚本算出并断言。
依据：V18-TP-47 / 50 / 51 / 52、V18-NAME-02 / 04、V18-L2-03 / 04；HUB 目录第五版。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import draw_tp_arch as T                                   # noqa: E402
from draw_tp_arch import Fig, P                            # noqa: E402
from svgkit_num import Svg, C_HI, C_LO, C_KEEP, C_OFF, C_SIDE, C_LEFT  # noqa: E402

DATE = '2026-11-07'
T.DATE = DATE
D = '7,4'

# ---------------- 两张架构图共用的外框与对端 ----------------
X0 = [50 + 420 * n for n in range(4)]          # 第 n 列（象限 n / H2C 道 n / C2H 分流 n / 核 n）左边
W_COL = 400
L2_Y, L2_H = 140, 80                           # 象限块
BUF_Y, BUF_H = 560, 70                         # 分叉点块（与 C2H 分流同一行）
SPL_Y, SPL_H = 560, 70                         # C2H 分流块
CORE_Y, CORE_H = 900, 240                      # 11-06 深夜：四核下移 120，给 D2 横线留 12 px 间距
LDP_Y, LDP_H = 940, 64
L1_Y = CORE_Y + 130
ENG = (1745, 292, 145, 118)
LIC = (1745, 910, 145, 70)
HCTL = (55, 500, 160, 50)                      # hub 控制道块
C6_Y, C5_Y, C7_Y = 700, 775, 845
D3_Y, CRUBUS_Y, C1_Y = 455, 652, 305         # D3 / C2 总线、去 MAE_CRU 总线、C1 总线（与块边留足距离）                # 命令图三条总线（拉开间距）


# D2：道 n → 核 c（c ≠ n）的横线各占一层，y = 652 + 6i
D2_LEVEL = {}
for _n in range(4):
    _others = sorted((c for c in range(4) if c != _n), key=lambda c: -abs(c - _n))   # 远的在上
    for _j, _c in enumerate(_others):
        D2_LEVEL[(_n, _c)] = 684 + 48 * _n + 12 * _j
assert len(D2_LEVEL) == 12 and max(D2_LEVEL.values()) < 870


def frame(s, data):
    s.group(40, 110, 1680, 124, '中央 L2 SRAM（象限读口带 busy · L2WP 每核一条）', 'mem', 15)
    for n, x in enumerate(X0):
        s.block(x, L2_Y, W_COL, L2_H, f'象限 {n}', f'读口 → H2C 道 {n} · L2WP {n} 写入（只来自核 {n}）', 'mem', 16, 12, shadow=False)
    s.group(30, 260, 1690, 610, 'HUB 组 · HUB_NOC', 'hub', 15, tx=455)
    for n, x in enumerate(X0):
        s.block(x + 30, BUF_Y, 200, BUF_H, f'分叉点 {n}', '每核 1 位已取 · 不另配存储\n位置与级数由后端定', 'hub', 14, 11, shadow=False)
        s.block(x + 250, SPL_Y, 140, SPL_H, f'C2H 通路 {n}', '直通 L2WP {n}'.format(n=n), 'hub', 14, 11, shadow=False)
    s.block(*HCTL, 'hub 控制道', '本图不用' if data else '命令网转发', 'ext' if data else 'ctrl', 14, 11, shadow=False)
    T.mae_frame(s, [(1732, 262), (1905, 262), (1905, 430), (1732, 430)], (1742, 272), title='MAE 组', size=14)
    s.block(*ENG, 'MAE_ENG', '搬运引擎（可在道旁）' if not data else '本图无数据线', 'ctlu' if not data else 'ext', 15, 11, shadow=False)
    s.block(*LIC, 'LIC', '本图不用' if data else '位点指令 · 事件', 'ext' if data else 'ctlu', 15, 11, shadow=False)
    for n, x in enumerate(X0):
        box = (x, CORE_Y, x + W_COL, CORE_Y + CORE_H)
        s.group(x, CORE_Y, W_COL, CORE_H, '', 'core', strip=False, dash='none', sw=2.4, fill=P['core'][1])
        s.text(x + 180, CORE_Y + 18, f'计算核 {n}', 15, 'start', P['core'][0], 700, box=box)
        s.block(x + 20, LDP_Y, 210, LDP_H, 'LDP × 4', 'H2C 道 0–3 落地', 'inter', 14, 11, shadow=False)
        s.block(x + 250, LDP_Y, 140, LDP_H, '集成输出端口', 'CCU 选核内来源', 'inter', 14, 11, shadow=False)
        s.block(x + 20, L1_Y, 370, 60, 'L1 SRAM', '写集合器 · 发送侧（核内 RRAM）', 'mem', 14, 11, shadow=False)
        s.line([(x + 125, LDP_Y + LDP_H), (x + 125, L1_Y)], 'incore', 2.2)
        s.line([(x + 320, L1_Y), (x + 320, LDP_Y + LDP_H)], 'incore', 2.2)


def fig_data():
    s = Fig('FIG-HUB_NOC-ARCH-DATA.svg', 'FIG-HUB_NOC-ARCH-DATA  HUB NoC：数据通路（D1 / D2 / D4 / D5）',
            'H2C 道 n 只读象限 n（唯一源）、分叉点按已取位分叉、各核独立取走；C2H 每核一路，核集成输出端口直通 L2WP n；HUB 不算地址、不仲裁；MAE_CRU 只经 NI 进出 L2，不连 HUB', h=1250)
    frame(s, True)
    for n, x in enumerate(X0):
        # D1 象限 n 读出 → 分叉点 n（H2C 道只有 L2 一个源）
        s.line([(x + 215, L2_Y + L2_H), (x + 215, BUF_Y)], 'inter', 2.8)
        # D2 分叉点 n 直接引出四路 → 四核 LDP 的第 n 个落地口（分叉在分叉点块里，线上不再打点）
        for c in range(4):
            xt = X0[c] + 50 + 40 * n                     # 核 c 的第 n 个落地口
            if c == n:
                s.line([(xt, BUF_Y + BUF_H), (xt, LDP_Y)], 'inter', 2.2)
            else:
                ex = x + 70 + 40 * c                     # 出口错开各核落地口的竖线
                yl = D2_LEVEL[(n, c)]
                s.line([(ex, BUF_Y + BUF_H), (ex, yl), (xt, yl), (xt, LDP_Y)], 'inter', 2.2)
        # D4 集成输出端口 → C2H 通路 n
        s.line([(x + 320, LDP_Y), (x + 320, SPL_Y + SPL_H)], 'inter', 2.6)
        # D5 C2H 通路 n → L2WP n（象限 n）
        s.line([(x + 320, SPL_Y), (x + 320, L2_Y + L2_H)], 'inter', 2.6)
    # 标签
    s.tag(X0[3] + 207, 300, 'D1 读象限 32 B · busy', 'inter', 12, 'end')
    s.tag(X0[3] + 312, 520, 'D5 → L2WP n', 'inter', 12, 'end')
    s.tag(X0[3] + 312, 885, 'D4 C2H 32 B', 'inter', 12, 'end')
    s.tag(X0[0] + 190, 885, 'D2 H2C 四路', 'inter', 12, 'start')
    s.legend(30, 1162, [('inter', '核间数据链路 32 B/拍', 'solid'), ('incore', '核内 RRAM', 'solid'),
                        ('ext', '灰框 = 本图不用', 'box'), ('inter', '实心点 = 分支 · 跳线 = 不相连', 'dot')],
             cols=4, colw=250, size=13, rowh=26)
    return s.save()


def fig_ctrl():
    s = Fig('FIG-HUB_NOC-ARCH-CTRL.svg', 'FIG-HUB_NOC-ARCH-CTRL  HUB NoC：命令类连线（C1 / C4 / C5 / C7，地址与使能不细分）',
            '每拍地址与核掩码由发令方给、随 HUB 通路传送；写入握手沿原链路反向回发令方；hub 控制道只转发命令网消息（标量不走命令网）', h=1250)
    frame(s, False)
    # C1 MAE 搬运引擎 → H2C 道：L2 读 en / addr（向上进象限读口）、目的 addr / be、核掩码（向下进分叉点）
    s.line([(ENG[0], C1_Y), (X0[0] + 140, C1_Y)], 'ctrl', 2.2, dash=D, head=None, net='c1')
    for x in X0:
        s.line([(x + 140, C1_Y), (x + 140, L2_Y + L2_H)], 'ctrl', 2.0, dash=D, net='c1')
        s.line([(x + 180, C1_Y), (x + 180, BUF_Y)], 'ctrl', 2.0, dash=D, net='c1')
        s.dot(x + 140, C1_Y, 'ctrl'); s.dot(x + 180, C1_Y, 'ctrl')
    for n, x in enumerate(X0):
        # C4 L2 象限 n → 核 n CCU 的写入握手（沿 C2H 反向）
        s.line([(x + 300, L2_Y + L2_H), (x + 300, 545), (x + 396, 545), (x + 396, LDP_Y + 32), (x + 390, LDP_Y + 32)], 'ctrl', 2.0, dash=D)
        # C5 各核 LDP 写入握手 → 握手总线 y 700
        s.line([(x + 110, LDP_Y), (x + 110, C5_Y)], 'ctrl', 2.0, dash=D, head=None, net='c5')
        s.dot(x + 110, C5_Y, 'ctrl')
        # C7 控制道 → 各核 CCU
        s.line([(x + 240, C7_Y), (x + 240, CORE_Y)], 'ctrl', 2.0, dash=D, head='both', net='c7')
        s.dot(x + 240, C7_Y, 'ctrl')
    s.line([(X0[0] + 110, C5_Y), (1735, C5_Y), (1735, 425), (1800, 425), (1800, ENG[1] + ENG[3])], 'ctrl', 2.2, dash=D, net='c5')
    # C7 hub 控制道 ⇄ 四核 CCU、MAE_ENG、LIC；L2 → 控制道（致命错误）
    s.line([(70, HCTL[1] + HCTL[3]), (70, C7_Y), (1898, C7_Y)], 'ctrl', 2.2, dash=D, head=None, net='c7')
    s.line([(1898, C7_Y), (1898, 345), (ENG[0] + ENG[2], 345)], 'ctrl', 2.2, dash=D, head='both', net='c7')
    s.line([(1790, C7_Y), (1790, LIC[1])], 'ctrl', 2.0, dash=D, head='both', net='c7')
    s.dot(1790, C7_Y, 'ctrl')
    s.line([(60, L2_Y + L2_H), (60, HCTL[1])], 'ctrl', 2.0, dash=D)
    # 标签
    s.tag(X0[3] + 194, 289, 'C1 地址·核掩码', 'ctrl', 12, 'start')
    s.tag(X0[1] + 306, 515, 'C4 L2 写入握手', 'ctrl', 12, 'start')
    s.tag(170, C5_Y - 14, 'C5 LDP 写入握手 · 道汇总后交引擎', 'ctrl', 12, 'start')
    s.tag(600, C7_Y - 14, 'C7 控制道', 'ctrl', 12, 'start')
    s.tag(68, 290, 'L2 致命错误', 'ctrl', 11, 'start')
    s.legend(30, 1162, [('ctrl', '命令类（含地址、使能、写入握手）', D), ('incore', '核内 RRAM', 'solid'),
                        ('ext', '灰框 = 本图不用', 'box')], cols=3, colw=300, size=13, rowh=26)
    return s.save()


# ---------------- MCAST：多播分叉点（一级链路块 + 每核 1 位已取，不另配存储；V18-TP-53） ----------------
from mcast_fork_sim import simulate  # noqa: E402
M_UNIT, M_CAP = 6, 4                       # 单位 6 拍；每核分支容量 = 分支 skid + LDP 入口 FIFO（示意）
M_NT = 9
M_READY = {0: [1] * M_NT, 2: [0 if t in (2, 3) else 1 for t in range(M_NT)]}   # 各核写进 L1 一侧的 ready
MC = simulate(M_UNIT, M_READY, M_CAP, M_NT)
assert MC['stall'] == 0                                            # 分叉点从不停收上游
assert MC['write'][0] == {t: t - 1 for t in range(1, 7)}           # 核 0 拍 1–6 写进 k = 0–5
assert sorted(MC['write'][2]) == [1, 4, 5, 6, 7, 8]
assert max(MC['occ'][2].values()) == 3
# 对照：核 2 停 4 拍、单位 8 拍 → 分支占满，分叉点停收 2 拍，核 0 的 k = 6、7 晚 2 拍
CX_NT = 14
CX = simulate(8, {0: [1] * CX_NT, 2: [0 if t in (2, 3, 4, 5) else 1 for t in range(CX_NT)]}, M_CAP, CX_NT)
CX0 = simulate(8, {0: [1] * CX_NT, 2: [1] * CX_NT}, M_CAP, CX_NT)
CX_K6 = {v: k for k, v in CX['write'][0].items()}[6]
CX0_K6 = {v: k for k, v in CX0['write'][0].items()}[6]
assert CX['stall'] == 2 and max(CX['occ'][2].values()) == M_CAP and CX_K6 - CX0_K6 == 2


def fig_mcast():
    s = Svg(1500, 600)
    s.rich(30, 34, 'H2C 道 0：一个 6 拍单位多播到核 0、核 2（掩码 0101）；核 2 写进 L1 的一侧在拍 2、3 不 ready', 17)
    s.note(30, 66, f'分叉点 = 一级链路块 + 每核 1 位已取，不另配存储；两核都取走才收下一拍；每核分支容量 {M_CAP} 拍（skid + LDP 入口 FIFO，示意）', 15)
    cols = [('拍', 60), ('送入核 0 分支', 140), ('送入核 2 分支', 140), ('分叉点收下一拍', 150), ('核 2 分支占用', 140),
            ('核 0 写进 k', 130), ('核 2 写进侧 ready', 160), ('核 2 写进 k', 130)]
    x0, y0, rh = 30, 92, 40
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    for t in range(M_NT):
        y = y0 + (t + 1) * rh
        p0, p2 = MC['push'][0].get(t), MC['push'][2].get(t)
        acc = MC['accept'].get(t)
        w0, w2 = MC['write'][0].get(t), MC['write'][2].get(t)
        oc = MC['occ'][2][t]
        vals = [str(t), '—' if p0 is None else f'k {p0}', '—' if p2 is None else f'k {p2}',
                '—' if acc is None else ('收' if acc else '停'), str(oc),
                '—' if w0 is None else f'k {w0}', str(M_READY[2][t]), '—' if w2 is None else f'k {w2}']
        fills = ['white', C_LO if p0 is not None else 'white', C_LO if p2 is not None else 'white',
                 C_KEEP if acc else ('white' if acc is None else C_HI), C_LEFT if oc >= 2 else 'white',
                 C_KEEP if w0 is not None else 'white', C_HI if M_READY[2][t] == 0 else 'white', C_KEEP if w2 is not None else 'white']
        for xx, (_, w), v, f in zip(xs, cols, vals, fills):
            s.cell(xx, y, w - 6, rh - 4, v, fill=f, size=13)
    yb = y0 + (M_NT + 1) * rh + 26
    s.red(30, yb, '分叉点不停，核 0 不等', 15)
    s.note(210, yb, '：核 0 拍 1–6 写完；核 2 停的两拍由它的分支接住（占用最多 3），拍 1、4–8 写完', 15)
    s.note(30, yb + 32, f'对照：核 2 停 4 拍、单位 8 拍 → 核 2 分支占满 {M_CAP}，分叉点停收 {CX["stall"]} 拍，核 0 的 k = 6、7 晚 {CX_K6 - CX0_K6} 拍写进；余量 = 该核分支容量', 15)
    s.save('FIG-HUB_NOC-MCAST.svg', DATE)


# ---------------- ACK：四核写入握手按 src 归并 ----------------
A_SRC, B_SRC = 3, 5
UNITS = [(A_SRC, 3, {0, 1, 2, 3}), (B_SRC, 2, {0, 3})]       # (src, 存储字数, 目的核)
K_READY = {0: [1] * 9, 1: [1, 0, 0, 1, 1, 1, 1, 1, 1], 2: [0, 1, 1, 1, 1, 1, 1, 1, 1], 3: [1] * 9}


def ack_sim():
    seq = {c: [src for src, nw, cores in UNITS if c in cores for _ in range(nw)] for c in range(4)}
    pos = {c: 0 for c in range(4)}
    rows = []
    for t in range(9):
        if all(pos[c] == len(seq[c]) for c in range(4)):
            break
        took = {}
        for c in range(4):
            if K_READY[c][t] and pos[c] < len(seq[c]):
                took[c] = seq[c][pos[c]]
                pos[c] += 1
        rows.append(took)                            # 取走即写进 L1 bank，回握手（拍号示意）
    return rows


AK = ack_sim()
TOT = {A_SRC: 0, B_SRC: 0}
MERGED = []
for took in AK:
    m = {}
    for src in took.values():
        m[src] = m.get(src, 0) + 1
    MERGED.append(m)
    for k, v in m.items():
        TOT[k] += v
assert TOT[A_SRC] == 3 * 4 and TOT[B_SRC] == 2 * 2
assert any(len(m) == 2 for m in MERGED)              # 至少一拍里两个 src 同时出现
assert len(AK) == 5


def fig_ack():
    s = Svg(1500, 440)
    s.rich(30, 34, f'H2C 道 0：引擎 {A_SRC} 的单位（3 个存储字，多播四核）后接引擎 {B_SRC} 的单位（2 个存储字，多播核 0、核 3）', 17)
    s.note(30, 66, '各核按自己的 ready 写进 L1（短时堵住由分支接住、分叉点不停），写进一个存储字就回一个 (valid, src)；道把同一拍四核的握手按 src 归并后交引擎', 15)
    cols = [('拍', 60), ('核 0', 130), ('核 1', 130), ('核 2', 130), ('核 3', 130), (f'引擎 {A_SRC} 本拍', 150), (f'引擎 {B_SRC} 本拍', 150)]
    x0, y0, rh = 30, 92, 40
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    for i, took in enumerate(AK):
        y = y0 + (i + 1) * rh
        m = MERGED[i]
        vals = [str(i)] + [('—' if c not in took else f'src {took[c]}') for c in range(4)] + \
               [f'+{m.get(A_SRC, 0)}' if m.get(A_SRC) else '—', f'+{m.get(B_SRC, 0)}' if m.get(B_SRC) else '—']
        fills = ['white'] + [(C_OFF if c not in took else (C_LO if took[c] == A_SRC else C_HI)) for c in range(4)] + \
                [C_KEEP if m.get(A_SRC) else 'white', C_KEEP if m.get(B_SRC) else 'white']
        for xx, (_, w), v, f in zip(xs, cols, vals, fills):
            s.cell(xx, y, w - 6, rh - 4, v, fill=f, size=13)
    y = y0 + (len(AK) + 1) * rh
    s.cell(xs[0], y, sum(w for _, w in cols[:5]) - 6, rh - 4, '累计（= 应写量 = 存储字数 × 目的核数）', fill=C_SIDE, size=14)
    s.cell(xs[5], y, cols[5][1] - 6, rh - 4, f'{TOT[A_SRC]} = 3 × 4', fill=C_KEEP, size=13)
    s.cell(xs[6], y, cols[6][1] - 6, rh - 4, f'{TOT[B_SRC]} = 2 × 2', fill=C_KEEP, size=13)
    s.red(30, y + rh + 18, '同一拍可出现两个 src', 15)
    s.note(208, y + rh + 18, '：归并成"某 src 本拍 +几"交引擎，或原样转交由引擎挑出自己的，【设计者定】；不丢、不重', 15)
    s.save('FIG-HUB_NOC-ACK.svg', DATE)


if __name__ == '__main__':
    bad = len(fig_data()) + len(fig_ctrl())
    fig_mcast()
    fig_ack()
    sys.exit(1 if bad else 0)
