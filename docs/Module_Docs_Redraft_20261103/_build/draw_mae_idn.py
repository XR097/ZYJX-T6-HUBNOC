"""MAE 入站分发网（MAE_IDN）正式稿的数值小例。Owner: WangYizhao · 2026-11-06
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_mae_idn.py
输出（figs/）：
  FIG-MAE_IDN-LANE-SPLIT  同一拍 32 B 的 4 条 8 B 道在四种链路分配（核集合）下送到的核与各道的 addr
  FIG-MAE_IDN-MCAST       一条道 6 拍多播到核 0、核 2：分叉点已取位（不另配存储），核 2 写进侧在拍 2、3 不 ready，分支接住、核 0 不等
连接图 FIG-MAE_IDN-CONN 在 draw_mae_conn.py（MAE 组统一外框）。
脚本断言：
  - 四种分配下各核所得道互不重叠、并起来是整拍 4 道；一个存储字由同一条道送全；
  - 多播：分叉点停收 0 拍；核 0 拍 1–6 写完、核 2 拍 1,4–8 写完；核 2 分支占用最大 3；对照（停 4 拍）分叉点停 2 拍、核 0 晚 2 拍。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fig_f5_post import SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, C_KEEP, C_LO, C_OFF  # noqa: E402

LANE = 8
LANES = 4
# 四种链路分配：每条道一个目的核；各道本拍的 addr（该 8 B 的起始字节地址，[堆][类] 略）
# 一个存储字由同一条道 4 拍送全（V18-TP-42）：本拍是各道所送存储字的第 0 拍（字节 0–7），
# 同一核的几条道送的是不同的存储字；{4}：核 2 的四个相邻存储字 2048 / 2080 / 2112 / 2144 各走一条道
ALLOCS = [
    ('{4}', [2, 2, 2, 2], [2048, 2080, 2112, 2144]),
    ('{2, 2}', [0, 0, 1, 1], [4096, 4128, 6144, 6176]),
    ('{2, 1, 1}', [0, 0, 1, 2], [4096, 4128, 6144, 2048]),
    ('{1, 1, 1, 1}', [0, 1, 2, 3], [4096, 6144, 2048, 10240]),
]
for name, cores, tuser in ALLOCS:
    got = {}
    for lane, c in enumerate(cores):
        got.setdefault(c, set()).update(range(lane * LANE, lane * LANE + LANE))
    allb = set()
    for c, bs in got.items():
        assert not (allb & bs), name
        allb |= bs
    assert allb == set(range(LANES * LANE)), name
    # 一个存储字由同一条道送全：同一核的各道送不同的存储字，本拍都是字首 8 B
    for c in got:
        addrs = [tuser[l] for l in range(LANES) if cores[l] == c]
        assert all(a % 32 == 0 for a in addrs)
        assert len({a // 32 for a in addrs}) == len(addrs)

# 多播分叉点（V18-TP-53）：一条道 6 拍，目的核 0、2；每核分支容量 4（分支 skid + NWB 入口，示意）；
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


def fig_lane_split():
    cw, ch = 150, 40
    x0, y0 = 150, 60
    s = SvgF5(max(x0 + LANES * (cw + 8) + 40, 1010), y0 + len(ALLOCS) * (ch + 34) + 70)
    s.rich(x0 - 14, 30, '同一拍 4 道 × 8 B', 15, 'end')
    for l in range(LANES):
        s.cell(x0 + l * (cw + 8), y0 - 36, cw, 26, f'道 {l}（8 B）', fill=C_OFF, size=12)
    fills = {0: C_KEEP, 1: C_LO, 2: '#fde8c8', 3: '#e9d5ff'}
    for r, (name, cores, tuser) in enumerate(ALLOCS):
        y = y0 + r * (ch + 34)
        s.rich(x0 - 14, y + ch / 2 + 5, name, 15, 'end')
        for l in range(LANES):
            s.cell(x0 + l * (cw + 8), y, cw, ch, f'核 {cores[l]} · addr {tuser[l]}', fill=fills[cores[l]], size=12)
        per = {}
        for c in cores:
            per[c] = per.get(c, 0) + LANE
        s.rich(x0, y + ch + 18, '；'.join(f'核 {c} 每拍 {b} B' for c, b in sorted(per.items())), 12, 'start', GREY, 600)
    y = y0 + len(ALLOCS) * (ch + 34) + 10
    s.rich(x0, y, '每条道一个核集合，随单位给出；一个存储字由同一条道 4 拍送全，同一核的几条道各送不同的存储字', 13, 'start', NAVY, 600)
    s.rich(x0, y + 22, '本拍是各存储字的字节 0–7；下一拍各道 addr 加 8，4 拍凑满一个字即整字写入（NWB 无末拍标记）', 13, 'start', NAVY, 600)
    assert y + 40 <= s.h
    s.save('FIG-MAE_IDN-LANE-SPLIT.svg')


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
    s.save('FIG-MAE_IDN-MCAST.svg')


if __name__ == '__main__':
    fig_lane_split()
    fig_mcast()
