"""MAE 片外接口（NI_EXT）正式稿的数值小例。Owner: WangYizhao · 2026-11-05（11-05 夜：窗口起始由编译链固定，V18-NIE-02）
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_mae_ni_ext.py
输出（figs/）：
  FIG-MAE_NI_EXT-PIN-WORDPACK  一笔不对齐的 PIN 写（AXI 偏移 76、长 70 B）→ 10 个 64 bit 拍 → 3 个存储字，各带字节写使能；
                               另一笔越窗写整笔 SLVERR
连接图 FIG-MAE_NI_EXT-CONN 在 draw_mae_conn.py（MAE 组统一外框）。
脚本断言：
  - L2 逻辑地址 = 窗口起始逻辑地址 + (A − A_PIN)；跨的存储字与字节范围按此算出（用户 11-05 夜：统一叫逻辑地址，不叫偏移）；
  - 10 个 AXI 拍的 WSTRB 恰好覆盖 70 B，写进 L2 的字节与 AXI 数据逐字节相同，未写字节保持原值；
  - 越窗写（偏移 260 ≥ 窗口 8 字 × 32 B = 256 B）判 SLVERR，L2 不变。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fig_f5_post import SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, C_KEEP, C_LO, C_OFF  # noqa: E402

WORD, BEAT = 32, 8
WIN_START, WIN_LEN = 40, 8              # 编译链固定的窗口：起始字 40、长 8 个存储字（堆 0、象限 2）
OFF, LEN = 76, 70                       # 这笔写：A − A_PIN = 76（逻辑地址 1356 起），长 70 B
BAD_OFF = 260                           # 越窗的另一笔
OLD = 0xEE

# AXI 64 bit 拍：地址按 8 B 对齐的拍边界，WSTRB 标出有效字节
first_beat = OFF // BEAT * BEAT
last_byte = OFF + LEN - 1
BEATS = []
for b0 in range(first_beat, last_byte + 1, BEAT):
    lo, hi = max(OFF, b0), min(last_byte, b0 + BEAT - 1)
    BEATS.append((b0, lo - b0, hi - b0))
assert len(BEATS) == 10 and BEATS[0] == (72, 4, 7) and BEATS[-1] == (144, 0, 1)
assert sum(hi - lo + 1 for _, lo, hi in BEATS) == LEN

# 落到 L2：逻辑地址 = 窗口起始逻辑地址 + (A − A_PIN)
WIN_BASE = WORD * WIN_START           # 窗口起始逻辑地址 1280
byte0 = WIN_BASE + OFF
WORDS = []
for w in range(byte0 // WORD, (byte0 + LEN - 1) // WORD + 1):
    lo, hi = max(byte0, w * WORD), min(byte0 + LEN - 1, w * WORD + WORD - 1)
    WORDS.append((w, lo - w * WORD, hi - w * WORD))
assert [w for w, _, _ in WORDS] == [42, 43, 44]
assert WORDS == [(42, 12, 31), (43, 0, 31), (44, 0, 17)]

# 逐字节模拟：写入字节与 AXI 数据相同，未写字节保持原值
data = [(i * 7 + 3) & 0xFF for i in range(LEN)]
mem = {w: [OLD] * WORD for w, _, _ in WORDS}
for i, v in enumerate(data):
    a = byte0 + i
    mem[a // WORD][a % WORD] = v
assert mem[42][:12] == [OLD] * 12 and mem[44][18:] == [OLD] * 14
assert [mem[(byte0 + i) // WORD][(byte0 + i) % WORD] for i in range(LEN)] == data

# 越窗
assert BAD_OFF >= WIN_LEN * WORD          # 落到窗口第 9 个字 → SLVERR，整笔丢弃


def fig_pin_wordpack():
    cw = 12
    x0 = 200
    s = SvgF5(x0 + 3 * WORD * cw + 2 * 30 + 40, 360)
    y = 28
    # 上排：10 个 AXI 拍
    s.rich(x0 - 14, y + 22, 'AXI 写数据拍', 15, 'end')
    s.rich(x0 - 14, y + 42, '（逻辑地址）', 12, 'end', GREY, 600)
    bw = 3 * WORD * cw / 10 - 6
    for i, (b0, lo, hi) in enumerate(BEATS):
        bx = x0 + i * (bw + 6)
        full = lo == 0 and hi == BEAT - 1
        s.cell(bx, y, bw, 44, f'{WIN_BASE + b0}', fill=C_OFF, size=13)
        s.rich(bx + bw / 2, y + 60, '全 8 B' if full else f'字节 {lo}–{hi}', 12, 'middle', GREY, 600)
    y += 122
    # 下排：3 个存储字（格子在上、字节写使能与字号在下，箭头只落在格子上沿）
    xs = [x0 + k * (WORD * cw + 30) for k in range(3)]
    s.rich(x0 - 14, y + 15, '写进 L2', 15, 'end')
    for k, (w, lo, hi) in enumerate(WORDS):
        for b in range(WORD):
            s.cell(xs[k] + b * cw, y, cw, 30, '', fill=C_KEEP if lo <= b <= hi else 'white', size=9, sw=0.7)
        txt = '整字' if (lo, hi) == (0, WORD - 1) else f'字节写使能：{lo}–{hi}'
        s.cell(xs[k] + lo * cw, y + 42, (hi - lo + 1) * cw, 26, txt, fill=C_LO, size=12)
        s.rich(xs[k] + WORD * cw / 2, y + 92, f'逻辑地址 {w * WORD}–{w * WORD + WORD - 1}', 14, 'middle')
    # 拍与存储字的对应：首拍（逻辑地址 1356–1359）、末拍（1424–1425）
    s.line([(x0 + bw / 2, 28 + 70), (xs[0] + 14 * cw, y - 2)], sw=1.3)
    s.line([(x0 + 9 * (bw + 6) + bw / 2, 28 + 70), (xs[2] + 17 * cw, y - 2)], sw=1.3)
    y += 124
    s.rich(x0 - 14, y + 16, '另一笔', 15, 'end')
    s.cell(x0, y, 560, 32, f'起始逻辑地址 {WIN_BASE + BAD_OFF} > 窗口末 {WIN_BASE + WIN_LEN * WORD - 1}', fill='white', size=13)
    s.red(x0 + 580, y + 21, '整笔 SLVERR，L2 不变', 14)
    y += 60
    s.rich(x0, y, f'窗口 = [堆 0][象限 2] 起始逻辑地址 {WIN_BASE}（由编译链固定）、长 {WIN_LEN * WORD} B；L2 逻辑地址 = {WIN_BASE} + (A − A_PIN)，本笔从 {byte0} 起、长 {LEN} B', 13, 'start', NAVY, 600)
    assert y + 20 <= s.h
    s.save('FIG-MAE_NI_EXT-PIN-WORDPACK.svg')


if __name__ == '__main__':
    fig_pin_wordpack()
