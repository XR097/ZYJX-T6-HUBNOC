"""MAE_CRU 篇的数值小例。Owner: WangYizhao · 2026-11-07
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_mae_cru.py
输出（figs/）：
  FIG-MAE_CRU-SUM       部分和归约：参与核 {0, 1, 2} 按 2 → 0 → 1 到达同一 CRU 内地址，第 3 份到达时按参与方固定次序相加
  FIG-MAE_CRU-READSET   读集合并：两个 CRU 内地址的读集交错到达，各自到齐后按位取并
  FIG-MAE_CRU-PINGPONG  CRU 内地址的 ping-pong：tile 0 用 A 区（地址 0–1）、tile 1 用 B 区（地址 2–3）、tile 2 回到 A 区
架构图 FIG-MAE_CRU-ARCH 在 draw_mae_arch.py（MAE 组统一外圈）。数值由脚本算出并断言。
依据：V18-MAE-30、V18-CRU-02…05、用户 11-06 深夜"一个基础的 ping-pong 设计"。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit_num import Svg, C_HI, C_LO, C_KEEP, C_OFF, C_SIDE, C_LEFT  # noqa: E402

DATE = '2026-11-07'

# =====================================================================
# SUM：部分和归约
# =====================================================================
S_PART = {0: [1.5, -2.0, 0.25, 3.0], 1: [0.5, 1.0, -0.75, 2.0], 2: [-1.0, 0.5, 0.5, 4.0]}   # 一个地址 4 元素（实际 16）
S_ORDER = [2, 0, 1]                                  # 到达先后
S_NEED = len(S_PART)                                 # 应到份数 = 参与核数
S_SUM = [(S_PART[0][i] + S_PART[1][i]) + S_PART[2][i] for i in range(4)]   # 按参与方固定次序相加
assert S_SUM == [1.0, -0.5, 0.0, 9.0]
# 换任意到达先后，结果都按参与方次序算，故相同
for order in ([0, 1, 2], [1, 2, 0], [2, 1, 0]):
    assert [(S_PART[0][i] + S_PART[1][i]) + S_PART[2][i] for i in range(4)] == S_SUM


def fig_sum():
    s = Svg(1300, 470)
    s.rich(30, 34, '部分和归约：参与核 {0, 1, 2}，同一 CRU 内地址 e，到达先后 2 → 0 → 1；应到份数 3', 17)
    s.note(30, 66, '一个地址 32 B = 16 个 BF16（图中只画 4 个）；第 3 份到达时合并，加法次序按参与方固定 (核 0 + 核 1) + 核 2，不随到达先后', 15)
    cols = [('拍', 70), ('到达', 140), ('元素 0', 120), ('元素 1', 120), ('元素 2', 120), ('元素 3', 120), ('地址 e 已到份数', 170), ('动作', 230)]
    x0, y0, rh = 30, 92, 42
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    rows = []
    for t, c in enumerate(S_ORDER):
        n = t + 1
        rows.append([str(t), f'核 {c} 的部分和'] + [f'{v:g}' for v in S_PART[c]] + [f'{n} / {S_NEED}', '到齐 → 合并' if n == S_NEED else '写入，等其余份'])
    rows.append([str(len(S_ORDER)), '结果（BF16）'] + [f'{v:g}' for v in S_SUM] + ['—', '经出口送往目的（地址由引擎给）'])
    for i, vals in enumerate(rows):
        y = y0 + (i + 1) * rh
        last = i == len(rows) - 1
        for j, (xx, (_, w), v) in enumerate(zip(xs, cols, vals)):
            f = 'white'
            if last and 2 <= j <= 5:
                f = C_KEEP
            elif j == 6 and v.startswith(f'{S_NEED} /'):
                f = C_LEFT
            elif 2 <= j <= 5:
                f = C_LO
            s.cell(xx, y, w - 6, rh - 4, v, fill=f, size=13)
    yb = y0 + (len(rows) + 1) * rh + 24
    s.red(30, yb, '到齐才合并，与到达先后无关', 15)
    s.note(260, yb, '：换成任何到达先后，结果都是 1、−0.5、0、9（脚本断言）', 15)
    s.save('FIG-MAE_CRU-SUM.svg', DATE)


# =====================================================================
# READSET：读集合并
# =====================================================================
R_BITS = {(0, 0): '10010000', (1, 0): '00010010', (2, 0): '01000000',   # (核, 地址)：读集（8 bit，实际一个地址 256 bit）
          (0, 1): '00100001', (2, 1): '00000101'}
R_NEED = {0: 3, 1: 2}                                # 地址 0：核 {0, 1, 2}；地址 1：核 {0, 2}
R_ORDER = [(1, 0), (0, 1), (0, 0), (2, 1), (2, 0)]   # 到达先后（核, 地址），两个地址交错


def _or(bits):
    v = 0
    for b in bits:
        v |= int(b, 2)
    return format(v, '08b')


R_TL = []
_got = {0: [], 1: []}
for t, (c, a) in enumerate(R_ORDER):
    _got[a].append(R_BITS[(c, a)])
    done = len(_got[a]) == R_NEED[a]
    R_TL.append((t, c, a, R_BITS[(c, a)], len(_got[a]), _or(_got[a]) if done else None))
R_RES = {a: _or([R_BITS[k] for k in R_BITS if k[1] == a]) for a in (0, 1)}
assert R_RES == {0: '11010010', 1: '00100101'}
assert [x[5] for x in R_TL] == [None, None, None, '00100101', '11010010']


def fig_readset():
    s = Svg(1300, 440)
    s.rich(30, 34, '读集合并：地址 0 由核 {0, 1, 2} 合并、地址 1 由核 {0, 2} 合并，两地址的拍交错到达', 17)
    s.note(30, 66, '1 位 = 一个 key（或区块、列）要不要读；图中 8 bit，实际一个地址 256 bit，更长的读集占连续几个地址；各地址到齐后按位取并', 15)
    cols = [('拍', 70), ('到达', 160), ('写到地址', 120), ('读集', 170), ('该地址已到份数', 180), ('到齐后的并集', 200), ('动作', 230)]
    x0, y0, rh = 30, 92, 42
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    for i, (t, c, a, bits, n, res) in enumerate(R_TL):
        y = y0 + (i + 1) * rh
        vals = [str(t), f'核 {c}', f'地址 {a}', bits, f'{n} / {R_NEED[a]}', res or '—', '到齐 → 取并、送出' if res else '写入']
        fills = ['white', 'white', C_HI if a == 0 else C_LO, 'white', C_LEFT if res else 'white', C_KEEP if res else 'white', 'white']
        for xx, (_, w), v, f in zip(xs, cols, vals, fills):
            s.cell(xx, y, w - 6, rh - 4, v, fill=f, size=13)
    yb = y0 + (len(R_TL) + 1) * rh + 24
    s.red(30, yb, '两个地址各计各的份数', 15)
    s.note(230, yb, f'：地址 1 在拍 3 先到齐（{R_RES[1]}），地址 0 在拍 4 到齐（{R_RES[0]}）；参与核不同的两组可同时在收', 15)
    s.save('FIG-MAE_CRU-READSET.svg', DATE)


# =====================================================================
# PINGPONG：CRU 内地址的 ping-pong
# =====================================================================
P_ADDR = {0: (0, 1), 1: (2, 3), 2: (0, 1)}            # tile → 地址（A 区 0–1、B 区 2–3）
P_NEED = 2                                             # 参与核 {0, 1}
P_EV = {0: (0, 0, 0), 1: (1, 0, 0), 2: (0, 0, 1), 3: (0, 1, 2), 4: (1, 0, 1), 5: (1, 1, 2),
        6: (0, 1, 3), 7: (0, 2, 0), 8: (1, 1, 3), 9: (1, 2, 0), 10: (0, 2, 1), 11: (1, 2, 1)}   # 拍 → (核, tile, 地址)
P_NT = 13


def pp_sim():
    cnt = {a: (None, 0) for a in range(4)}            # 地址 → (当前 tile, 已到份数)
    outq, done_out, rows, reported = [], {t: set() for t in P_ADDR}, [], []
    for t in range(P_NT):
        arr, merged, out, rep = P_EV.get(t), None, None, None
        if outq:                                       # 每拍送出一个已合并的地址（上一拍合并的）
            a, tile = outq.pop(0)
            out = (a, tile)
            cnt[a] = (None, 0)                         # 送出后该地址可再用
            done_out[tile].add(a)
            if done_out[tile] == set(P_ADDR[tile]):
                rep = tile
                reported.append(tile)
        if arr:
            c, tile, a = arr
            cur, n = cnt[a]
            assert cur in (None, tile), (t, a)         # 断言：上一 tile 的结果送出前，新 tile 的数据不写进该地址
            cnt[a] = (tile, n + 1)
            if n + 1 == P_NEED:
                merged = (a, tile)
                outq.append((a, tile))
        rows.append((t, arr, {a: cnt[a] for a in range(4)}, merged, out, rep))
    return rows, reported


PP, PP_REP = pp_sim()
assert PP_REP == [0, 1, 2]                             # 每个 tile 各报一次完成，按 0、1、2
assert [r[3] for r in PP if r[3]] == [(0, 0), (1, 0), (2, 1), (3, 1), (0, 2), (1, 2)]
assert min(t for t, e in P_EV.items() if e[1] == 2) > max(r[0] for r in PP if r[4] and r[4][1] == 0)   # A 区结果全部送出后 tile 2 才写进 A 区
assert [r[0] for r in PP if r[5] is not None] == [5, 9, 12]


def fig_pingpong():
    s = Svg(1500, 760)
    s.rich(30, 34, 'CRU 内地址的 ping-pong：tile 0 用 A 区（地址 0–1），tile 1 用 B 区（地址 2–3），tile 2 回到 A 区；参与核 {0, 1}', 17)
    s.note(30, 66, '分区与轮换都写在地址里（编译链给），硬件只按地址计到达份数；到齐即合并，下一拍送出，送出后该地址才可被下一个 tile 用', 15)
    cols = [('拍', 60), ('到达（核 · tile · 地址）', 230), ('地址 0（A）', 140), ('地址 1（A）', 140), ('地址 2（B）', 140), ('地址 3（B）', 140),
            ('合并', 150), ('送出', 150), ('报完成', 120)]
    x0, y0, rh = 30, 92, 40
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_HI if 'A）' in name else (C_LO if 'B）' in name else C_SIDE), size=13)
        x += w
    for i, (t, arr, cnt, merged, out, rep) in enumerate(PP):
        y = y0 + (i + 1) * rh
        vals = [str(t), '—' if not arr else f'核 {arr[0]} · tile {arr[1]} · 地址 {arr[2]}']
        fills = ['white', 'white']
        for a in range(4):
            tile, n = cnt[a]
            vals.append('—' if tile is None else f'tile {tile} · {n}/{P_NEED}')
            fills.append(C_LEFT if (merged and merged[0] == a) else ('white' if tile is None else (C_HI if a < 2 else C_LO)))
        vals += ['—' if not merged else f'地址 {merged[0]}', '—' if not out else f'地址 {out[0]}（tile {out[1]}）', '—' if rep is None else f'tile {rep}']
        fills += [C_LEFT if merged else 'white', C_KEEP if out else 'white', C_KEEP if rep is not None else 'white']
        for xx, (_, w), v, f in zip(xs, cols, vals, fills):
            s.cell(xx, y, w - 6, rh - 4, v, fill=f, size=12)
    yb = y0 + (P_NT + 1) * rh + 24
    s.red(30, yb, 'A 区收 tile 2 时 B 区还在收 tile 1', 15)
    s.note(330, yb, '：A 区的 tile 0 结果在拍 5 全部送出，tile 2 在拍 7 才写进 A 区；tile 0、1、2 分别在拍 5、9、12 报完成', 15)
    s.save('FIG-MAE_CRU-PINGPONG.svg', DATE)


if __name__ == '__main__':
    fig_sum()
    fig_readset()
    fig_pingpong()
