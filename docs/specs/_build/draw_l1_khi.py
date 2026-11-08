"""L1 篇 §7.8a：精算 K hi 的驻留模式与重读模式（用户 11-06，V18-ATT-01）。Owner: WangYizhao · 2026-11-06
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_l1_khi.py
输出（figs/）：
  FIG-L1_SRAM-KHI-RESIDENT-VS-REREAD  同一条粗算 / 录取时间线下，两种模式 L1 里 K 区的占用与释放点
例子：粗算 tile 0…4 依次在时段 0…4 到达并粗算；录取单位 u0 的 64 个 key 取自 tile 0–3，
在时段 3 末录取，时段 4 补读并精算，时段 4 末精算完。
脚本断言：
  - u0 的 key 数 = N_u，覆盖的粗算 tile 集合 T(u0) = {0, 1, 2, 3}（4 个）；
  - 驻留模式：tile 0 的 K hi 列字份留到 u0 精算完；K hi 列字区同时占用份数最大 = 1 + |T(u0)| = 5
    （为 u0 留住的 4 个 tile + 正在写入的 tile 4，即 n_hi 的下限）；
  - 重读模式：每个 tile 的 K hi 行字份粗算完即释放；行字区与全码区同时占用份数最大 = 1 + 在用全码份数 = 2；
  - 全码记录 128 B/key = hi 64 + lo 64（尺度 4 B 落 S 类，用户 11-06 平面分开的记录级）；红字 ≤ 2 处、每处 ≤ 12 字。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fig_f5_post import SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, CTRL, C_HI, C_LO, C_KEEP, C_W, C_OFF  # noqa: E402

# ---- 参考尺寸（head_dim 128；N_ct = N_u = 64 为参考值） ----
HEAD_DIM = 128
N_CT = 64
N_U = 64
HI_B = HEAD_DIM * 4 // 8            # hi 列字 64 B/key
LO_B = HEAD_DIM * 4 // 8            # lo 列字 64 B/key
SC_B = HEAD_DIM // 32               # E8M0 尺度 4 B/key，落 S 类、不进记录（用户 11-06）
FC_B = HI_B + LO_B                  # 全码记录 128 B/key = hi 4 个存储字 + lo 4 个存储字
assert (HI_B, LO_B, SC_B, FC_B) == (64, 64, 4, 128) and FC_B % 32 == 0

# ---- 时间线 ----
N_SLOT = 5                          # 时段 0…4；粗算 tile k 在时段 k
U0_KEYS = {0: 24, 1: 8, 2: 12, 3: 20}   # u0 的录取 key 来自哪些 tile（个数为示例）
U0_ADMIT = 3                        # 时段 3 末录取
U0_EXACT = 4                        # 时段 4 补读并精算，时段 4 末精算完
U0_DONE = U0_EXACT + 1              # 释放时点（时段边界）
N_FC_USED = 1                       # 本例在用的全码份数（只画 u0）
assert sum(U0_KEYS.values()) == N_U
T_U0 = sorted(U0_KEYS)
assert T_U0 == [0, 1, 2, 3] and len(T_U0) == 4


def resident_release(k):
    """驻留模式：tile k 的 K hi 列字份留到覆盖它的全部录取单位精算完；tile 4 留给后续单位（图内不释放）。"""
    return U0_DONE if k in U0_KEYS else None


def occ_resident(s):
    return sum(1 for k in range(N_SLOT) if k <= s and (resident_release(k) is None or s < resident_release(k)))


def occ_reread(s):
    row = 1                         # 行字份：tile s 粗算完即释放，任一时段只有本 tile
    fc = N_FC_USED if s == U0_EXACT else 0
    return row + fc


OCC_RES = [occ_resident(s) for s in range(N_SLOT)]
OCC_RR = [occ_reread(s) for s in range(N_SLOT)]
assert resident_release(0) == U0_DONE          # tile 0 跨 tile 0…3 留到 u0 精算完
assert OCC_RES == [1, 2, 3, 4, 5] and max(OCC_RES) == 1 + len(T_U0)
assert OCC_RR == [1, 1, 1, 1, 2] and max(OCC_RR) == 1 + N_FC_USED

RED_NOTES = []


def red(s, x, y, txt, anchor='start'):
    RED_NOTES.append(txt)
    assert len(RED_NOTES) <= 2 and len(txt.replace(' ', '')) <= 12, txt
    s.red(x, y, txt, 13, anchor)


def main():
    W, H = 1180, 690
    LX, SW = 250, 170
    xs = [LX + i * SW for i in range(N_SLOT + 1)]
    x_done = xs[U0_DONE]
    s = SvgF5(W, H)

    # ---- 时间线表头 ----
    for i in range(N_SLOT):
        s.rich(xs[i] + SW / 2, 30, f'时段 {i}', 13, 'middle', GREY, 600)
    s.rich(LX - 14, 63, '粗算', 15, 'end')
    for i in range(N_SLOT):
        s.cell(xs[i] + 4, 48, SW - 8, 30, f'tile {i} 粗算', fill=C_W, size=13)
    s.rich(LX - 14, 101, '录取 / 精算', 15, 'end')
    s.cell(xs[U0_ADMIT] + 4, 86, SW - 8, 30, f'u0 录取（{N_U} key）', fill=C_OFF, size=13)
    s.cell(xs[U0_EXACT] + 4, 86, SW - 8, 30, 'u0 补读 + 精算', fill=C_KEEP, size=13)
    cnt = ' / '.join(str(U0_KEYS[k]) for k in T_U0)
    s.rich(LX, 132, f'u0 的 {N_U} 个 key 取自 tile 0–3（各 {cnt} 个）', 13, 'start', GREY, 600)
    s.rich(x_done - 6, 132, 'u0 精算完', 13, 'end', NAVY, 700)

    # ---- 驻留模式 ----
    y0 = 150
    s.panel(20, y0, W - 40, 284, '驻留模式：K hi 双写，列字留给精算', 17)
    yr = y0 + 42
    s.rich(LX - 14, yr + 13, 'K hi 行字区（粗算）', 14, 'end')
    for i in range(N_SLOT):
        s.cell(xs[i] + 4, yr, SW - 8, 26, f't{i} 行字', fill=C_W, size=12)
    yc = yr + 38
    for k in range(N_SLOT):
        y = yc + k * 26
        rel = resident_release(k)
        if rel is None:
            s.cell(xs[k] + 4, y, x_done + 44 - xs[k] - 4, 22, 'tile 4 列字（留给后续单位）', fill=C_HI, size=12, dash='5,3')
        else:
            s.rect(xs[k] + 4, y, xs[rel] - xs[k] - 8, 22, fill=C_HI, sw=1.2)
            s.rich(xs[k] + 12, y + 11, f'tile {k} 列字', 12, 'start', NAVY, 600)
    red(s, x_done - 14, yc + 11, '留到 u0 精算完', 'end')
    s.rich(LX - 14, yc + 52, 'K hi 列字区', 14, 'end')
    s.rich(LX - 14, yc + 72, '（精算的 hi 道）', 13, 'end', GREY, 600)
    yl = yc + N_SLOT * 26 + 10
    s.rich(LX - 14, yl + 11, 'lo 区（精算的 lo 道）', 14, 'end')
    s.cell(xs[U0_EXACT] + 4, yl, SW - 8, 22, 'u0 lo，64 B/key', fill=C_LO, size=12)
    yn = yl + 38
    s.rich(LX - 14, yn, '列字区同时占用份数', 14, 'end')
    for i in range(N_SLOT):
        txt = f'{OCC_RES[i]} = 1 + {len(T_U0)}' if OCC_RES[i] == max(OCC_RES) else str(OCC_RES[i])
        s.rich(xs[i] + SW / 2, yn, txt, 15, 'middle', NAVY, 700)
    assert yn + 18 <= y0 + 284

    # ---- 重读模式 ----
    y1 = y0 + 300
    s.panel(20, y1, W - 40, 170, '重读模式：K hi 只落行字，录取后 hi + lo 同次 gather', 17)
    yr = y1 + 42
    s.rich(LX - 14, yr + 13, 'K hi 行字区（粗算）', 14, 'end')
    for i in range(N_SLOT):
        s.cell(xs[i] + 4, yr, SW - 8, 26, f't{i} 行字', fill=C_W, size=12)
    red(s, xs[0] + 8, yr + 40, '粗算完即释放')
    yf = yr + 56
    s.rich(LX - 14, yf + 11, '录取 key 全码区', 14, 'end')
    s.cell(xs[U0_EXACT] + 4, yf, SW - 8, 22, f'u0 全码，{FC_B} B/key', fill=C_KEEP, size=12)
    yn = yf + 42
    s.rich(LX - 14, yn, '行字区 + 全码区份数', 14, 'end')
    for i in range(N_SLOT):
        txt = f'{OCC_RR[i]} = 1 + {N_FC_USED}' if OCC_RR[i] == max(OCC_RR) else str(OCC_RR[i])
        s.rich(xs[i] + SW / 2, yn, txt, 15, 'middle', NAVY, 700)
    assert yn + 18 <= y1 + 170

    # u0 精算完的竖线（贯穿两种模式）
    s.line([(x_done, 140), (x_done, y1 + 170)], color=GREY, sw=1.4, marker=None, dash='5,4')

    # ---- 图下蓝字：实际尺寸 ----
    yb = y1 + 196
    s.rich(30, yb, f'实际尺寸（head_dim {HEAD_DIM}；N_{{ct}} = N_{{u}} = {N_CT} 为参考值）：'
                   f'hi 列字 {HI_B} B/key，一个 tile、一个 kv 头 {N_CT * HI_B // 1024} KB；lo {LO_B} B/key',
           14, 'start', CTRL, 600)
    s.rich(30, yb + 24, f'全码记录 {FC_B} B/key = hi {HI_B} + lo {LO_B}（尺度 {SC_B} B 落 S 类），'
                        f'一份 = 一个录取单位 {N_U * FC_B / 1024:g} KB；全码区份数 n_{{fc}} 随流水深度，参考 3',
           14, 'start', CTRL, 600)
    assert yb + 24 + 14 <= H
    s.save('FIG-L1_SRAM-KHI-RESIDENT-VS-REREAD.svg')


if __name__ == '__main__':
    main()
