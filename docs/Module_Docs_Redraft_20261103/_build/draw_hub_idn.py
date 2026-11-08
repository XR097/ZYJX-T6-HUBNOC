"""HUB 入站分发网（HUB_IDN，原 MAE_IDN，11-07 归 HUB 组，V18-HUB-01；11-08 晚每核一条 32 B 链路，V18-HUB-04）正式稿的架构图与数值小例。
Owner: WangYizhao · 2026-11-06 / 11-07 / 11-08
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_hub_idn.py
输出（figs/）：
  FIG-HUB_IDN-ARCH      HUB 组外框：HUB_IDN 展开（一路 32 B 输入 → 按每字核集合分发的分叉点 → 每核一条 32 B 链路；11-08 V18-HUB-04），对端 = MAE 组的 MAE_ENG / NI_INT（IDN 出口）、四核 NWB
  FIG-HUB_IDN-CORE-SET  连续 8 个存储字在四种共享方式（单核 / 双核轮流 / 2:1:1 / 四核均分）与一种多播下的核集合，各核平均每拍字节数（替代 11-07 的 LANE-SPLIT）
  FIG-HUB_IDN-MCAST     一个字流 6 拍多播到核 0、核 2：分叉点已取位（不另配存储），核 2 写进侧在拍 2、3 不 ready，分支接住、核 0 不等
架构图图元（Fig 类、dimblock）借用 draw_mae_arch.py，不改它。
脚本断言：
  - 每种共享方式下每拍恰有一个字、每字至少一个核；各核平均字节数之和 = 32 B/拍（多播例除外：每核都收全部字）；
  - 多播：分叉点停收 0 拍；核 0 拍 1–6 写完、核 2 拍 1,4–8 写完；核 2 分支占用最大 3；对照（停 4 拍）分叉点停 2 拍、核 0 晚 2 拍。
退役：fig_lane_split（11-07 的 4 道 × 8 B 图）改名 _retired_fig_lane_split，不再调用；SVG 移到 figs/_retired_20261108/。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fig_f5_post import SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, C_KEEP, C_LO, C_OFF  # noqa: E402

WORD = 32
N_WORDS = 8
# 连续 8 个存储字的核集合（每字一个集合，由 MAE_ENG 的地址状态机随字给出；V18-HUB-04）。
# 字地址 = 该核 L1 里的目的字节地址（[堆][类] 略）：同一核连续收到的字地址连续递增 32。
SHARES = [
    ('单核吃满（核 2）', [{2}] * N_WORDS),
    ('双核轮流（核 0、1）', [{0}, {1}] * (N_WORDS // 2)),
    ('2 : 1 : 1（核 0 两份）', [{0}, {0}, {1}, {2}] * (N_WORDS // 4)),
    ('四核均分', [{0}, {1}, {2}, {3}] * (N_WORDS // 4)),
    ('多播到核 0、2', [{0, 2}] * N_WORDS),
]
BASE = {0: 4096, 1: 6144, 2: 2048, 3: 10240}


def per_core_bytes(sets):
    """各核平均每拍字节数 = 该核在 N_WORDS 拍里收到的字数 × 32 / N_WORDS。"""
    got = {}
    for s_ in sets:
        for c in s_:
            got[c] = got.get(c, 0) + 1
    return {c: n * WORD / N_WORDS for c, n in sorted(got.items())}


def word_addrs(sets):
    """每拍每核收到的字地址：同一核按收到次序连续递增 32。"""
    nxt = dict(BASE)
    out = []
    for s_ in sets:
        d = {}
        for c in sorted(s_):
            d[c] = nxt[c]
            nxt[c] += WORD
        out.append(d)
    return out


for name, sets in SHARES:
    assert len(sets) == N_WORDS and all(len(s_) >= 1 for s_ in sets), name
    pb = per_core_bytes(sets)
    if '多播' not in name:
        assert abs(sum(pb.values()) - WORD) < 1e-9, (name, pb)       # 单播：各核平均字节数之和 = 32 B/拍
    else:
        assert all(v == WORD for v in pb.values()), (name, pb)        # 多播：每核都收全部字
    for d in word_addrs(sets):
        assert all(a % WORD == 0 for a in d.values())

# 多播分叉点（V18-TP-53）：一个字流 6 拍，目的核 0、2；每核分支容量 4（分支 skid + NWB 入口，示意）；
# 核 2 写进 L1 的一侧在拍 2、3 不 ready。逐拍模型与 HUB_NOC、协议篇共用 mcast_fork_sim.py
from mcast_fork_sim import simulate  # noqa: E402
N, CAP, NT = 6, 4, 9
CORES = [0, 2]
READY = {0: [1] * NT, 2: [0 if t in (2, 3) else 1 for t in range(NT)]}
MC = simulate(N, READY, CAP, NT)
assert MC['stall'] == 0                                      # 分叉点从不停收上游
assert MC['write'][0] == {t: t - 1 for t in range(1, 7)}     # 核 0 拍 1–6 写进 k = 0–5，不等核 2
assert sorted(MC['write'][2]) == [1, 4, 5, 6, 7, 8]
assert max(MC['occ'][2].values()) == 3
CXT = 14
CX = simulate(8, {0: [1] * CXT, 2: [0 if t in (2, 3, 4, 5) else 1 for t in range(CXT)]}, CAP, CXT)
CX0 = simulate(8, {0: [1] * CXT, 2: [1] * CXT}, CAP, CXT)
CX_DELAY = {v: k for k, v in CX['write'][0].items()}[6] - {v: k for k, v in CX0['write'][0].items()}[6]
assert CX['stall'] == 2 and CX_DELAY == 2

FILLS = {0: C_KEEP, 1: C_LO, 2: '#fde8c8', 3: '#e9d5ff'}


def fig_core_set():
    cw, ch = 150, 44
    x0, y0 = 330, 64
    s = SvgF5(x0 + N_WORDS * (cw + 6) + 40, y0 + len(SHARES) * (ch + 40) + 108)
    s.rich(x0 - 14, 30, '连续存储字（每拍一个，32 B）', 15, 'end')
    for t in range(N_WORDS):
        s.cell(x0 + t * (cw + 6), y0 - 36, cw, 26, f'字 {t}（拍 {t}）', fill=C_OFF, size=12)
    for r, (name, sets) in enumerate(SHARES):
        y = y0 + r * (ch + 40)
        s.rich(x0 - 14, y + ch / 2 + 5, name, 14, 'end')
        addrs = word_addrs(sets)
        for t, s_ in enumerate(sets):
            cores = sorted(s_)
            label = '核 ' + '+'.join(str(c) for c in cores)
            sub = '/'.join(f'{addrs[t][c]}' for c in cores)
            fill = FILLS[cores[0]] if len(cores) == 1 else '#e2e8f0'
            s.cell(x0 + t * (cw + 6), y, cw, ch, f'{label} · {sub}', fill=fill, size=11)
        pb = per_core_bytes(sets)
        s.rich(x0, y + ch + 18, '；'.join(f'核 {c} 平均 {b:g} B/拍' for c, b in pb.items()) +
               ('（多播：每核都收全部字）' if '多播' in name else '（之和 32 B/拍 = M0 上限）'), 12, 'start', GREY, 600)
    y = y0 + len(SHARES) * (ch + 40) + 10
    s.red(x0, y, '一个字一拍整字到一个核', 14)
    s.rich(x0, y + 26, '核集合随每个存储字由 MAE_ENG 给出；HUB_IDN 只按它分发，几核共享带宽就是连续的字轮流排给各核', 13, 'start', NAVY, 600)
    s.rich(x0, y + 48, '每核一条 32 B 链路：轮到的那一拍收一个整字（be 全 1），没轮到的拍 en = 0；同一核收到的字地址连续递增 32', 13, 'start', NAVY, 600)
    s.rich(x0, y + 70, '格内：目的核 · 该字在目的核 L1 里的字地址（[堆][类] 略）；多播格写两核各自的字地址', 13, 'start', GREY, 600)
    assert y + 84 <= s.h
    s.save('FIG-HUB_IDN-CORE-SET.svg')


def fig_mcast():
    cw, ch = 86, 36
    x0, y0 = 190, 56
    rows = ['送入核 0 分支', '送入核 2 分支', '分叉点收下一拍', '核 2 分支占用', '核 0 写进 k', '核 2 写进侧 ready', '核 2 写进 k']
    s = SvgF5(x0 + NT * (cw + 6) + 40, y0 + len(rows) * (ch + 10) + 100)
    for t in range(NT):
        s.cell(x0 + t * (cw + 6), y0 - 32, cw, 24, f'拍 {t}', fill=C_OFF, size=12)
    for r, name in enumerate(rows):
        y = y0 + r * (ch + 10)
        s.rich(x0 - 14, y + ch / 2 + 5, name, 14, 'end')
        for t in range(NT):
            x = x0 + t * (cw + 6)
            if r in (0, 1):
                k = MC['push'][CORES[r]].get(t)
                s.cell(x, y, cw, ch, '—' if k is None else f'k {k}', fill=C_LO if k is not None else 'white', size=13)
            elif r == 2:
                a = MC['accept'].get(t)
                s.cell(x, y, cw, ch, '—' if a is None else ('收' if a else '停'), fill=C_KEEP if a else ('white' if a is None else '#fde8c8'), size=13)
            elif r == 3:
                o = MC['occ'][2][t]
                s.cell(x, y, cw, ch, str(o), fill='#fde8c8' if o >= 2 else 'white', size=13)
            elif r == 4:
                k = MC['write'][0].get(t)
                s.cell(x, y, cw, ch, '—' if k is None else f'k {k}', fill=C_KEEP if k is not None else 'white', size=13)
            elif r == 5:
                rd = READY[2][t]
                s.cell(x, y, cw, ch, str(rd), fill='white' if rd else '#fde8c8', size=13)
            else:
                k = MC['write'][2].get(t)
                s.cell(x, y, cw, ch, '—' if k is None else f'k {k}', fill=C_KEEP if k is not None else 'white', size=13)
    y = y0 + len(rows) * (ch + 10) + 10
    s.red(x0, y, '分叉点不停，核 0 不等核 2', 14)
    s.rich(x0, y + 26, f'分叉点 = 一级链路块 + 每核 1 位已取，不另配存储；两核都取走才收下一拍；核 2 停的两拍由它的分支接住（容量 {CAP}，示意）', 13, 'start', NAVY, 600)
    s.rich(x0, y + 50, f'对照：核 2 停 4 拍、单位 8 拍 → 分支占满，分叉点停收 {CX["stall"]} 拍，核 0 的 k = 6、7 晚 {CX_DELAY} 拍；余量 = 该核分支容量', 13, 'start', NAVY, 600)
    assert y + 64 <= s.h
    s.save('FIG-HUB_IDN-MCAST.svg')


# =====================================================================
# FIG-HUB_IDN-ARCH（11-08：只剩按核集合的分叉点；每核一条 32 B 链路）
# =====================================================================
def fig_arch():
    import draw_mae_arch as M
    M.DATE = '2026-11-08'
    s = M.Fig('FIG-HUB_IDN-ARCH.svg', 'FIG-HUB_IDN-ARCH  HUB_IDN：一路 32 B 进，按每字的核集合分发，每核一条 32 B 链路',
              '输入只有一路 32 B（MAE 的 IDN 出口，NI 分路 / MAE_DSU 已在 MAE 内择一）；核集合随每个存储字由 MAE_ENG 给；接几核即多播分叉点，各核独立取走；不拆拍、不缓存、不算地址')
    D = M.D
    # ---- HUB 组框 ----
    s.group(300, 200, 1330, 740, 'HUB 组 · 两篇（全芯片一组）', 'chip', 16, dash='none', sw=2.4, fill='#fbfcfe')
    M.dimblock(s, 330, 235, 330, 75, 'HUB_NOC', '本单元不用 · 中心端 L2 · 与 HUB_IDN 无数据连接')
    # ---- 组外对端 ----
    M.dimblock(s, 520, 100, 280, 70, '中央 L2', '本单元不用')
    M.dimblock(s, 860, 100, 300, 70, '命令网', '本单元不用')
    s.block(1220, 100, 380, 70, 'MAE_ENG（MAE 组）', '核集合随字（旁带）· 收写入握手', 'ctlu', 16, 12)
    s.block(20, 470, 250, 170, 'NI_INT（MAE 组）', 'IDN 出口：1 × 32 B\nNI 读返回分路 / MAE_DSU\n在 MAE 内择一', 'hub', 16, 12)
    M.dimblock(s, 20, 690, 250, 95, 'MAE_DSU（MAE 组）', '本单元不用 · 经 NI_INT 的 IDN 出口')
    M.dimblock(s, 20, 820, 250, 95, 'MAE_CRU（MAE 组）', '本单元不用 · 只写 L2')
    M.dimblock(s, 540, 975, 340, 75, '四核 LDP / 发送桥', '本单元不用 · H2C / C2H 归 HUB_NOC')
    s.block(900, 975, 520, 75, '四核 IDN 接收桥（NWB）', '每核 1 条 32 B 链路 · 与 LDP 相同的接收桥', 'mem', 16, 12)
    # ---- 本单元 ----
    s.group(740, 325, 870, 590, 'HUB_IDN（本单元）', 'focal', 16, tx=754, dash='10,5', sw=2.2, fill=M.P['focal'][1])
    s.block(900, 470, 470, 200, '分叉点：按每字的核集合分发',
            '一拍 = 一个存储字（din 32 B · addr · be · src）\n核集合里的每个核各拉一路 en，各核独立取走\n每目的核 1 位已取，全部取走才收下一拍\n不另配存储 · 不拆拍 · 不算地址 · 不数单位', 'hub', 17, 13, shadow=False)
    s.tag(750, 405, '分几级、放在哪【设计者定】（协议篇 A1–A7），本图为一种画法', 'ctrl', 13, 'start')
    s.tag(750, 432, '几核共享带宽 = MAE_ENG 把连续的字轮流排给各核；单核吃满 32 B/拍', 'ctrl', 13, 'start')
    # 唯一输入：MAE 的 IDN 出口 1 × 32 B
    s.line([(270, 555), (900, 555)], 'inter', 3.2, net='in32')
    s.tag(520, 538, '32 B · 字地址 · be 32 · src', 'inter', 12)
    s.tag(520, 572, '每拍一个存储字', 'inter', 12)
    # MAE_ENG：核集合（随字，旁带）→ 分叉点；写入握手（汇总、按 src）→ 引擎
    s.line([(1300, 170), (1300, 470)], 'ctrl', 2.2, dash=D)
    s.tag(1292, 320, '核集合 4 bit · 随每个存储字', 'ctrl', 12, 'end')
    s.line([(1560, 470), (1560, 170)], 'ctrl', 2.2, dash=D)
    s.tag(1568, 320, '写入握手（汇总 · 按 src）', 'ctrl', 12, 'start')
    s.line([(1370, 500), (1560, 500), (1560, 470)], 'ctrl', 2.2, dash=D, head=None)
    # 4 条链路 → 四核 IDN 接收桥：NWB 块放在分叉点正下方，四条线竖直直下、不拐弯、不交叉（用户 11-08 布局要求；写入握手沿链路反向回来，不另画）
    for c in range(4):
        xs = 960 + 120 * c
        s.line([(xs, 670), (xs, 975)], 'inter', 2.8)
        s.tag(xs - 8, 957, f'核 {c}：1 × 32 B', 'inter', 12, 'end')
    s.legend(20, 975, [('inter', '数据：握手写流', 'solid'), ('ctrl', '控制旁带 / 写入握手', D),
                       ('dim', '灰框 = 本单元不用', 'box')], cols=2, colw=236, size=13, rowh=27)
    return s.save()


def _retired_fig_lane_split():
    """11-07 的 4 道 × 8 B 图（FIG-HUB_IDN-LANE-SPLIT），11-08 V18-HUB-04 退役；SVG 在 figs/_retired_20261108/。不再调用。"""
    raise RuntimeError('retired 2026-11-08 (V18-HUB-04)')


if __name__ == '__main__':
    fig_core_set()
    fig_mcast()
    sys.exit(1 if fig_arch() else 0)
