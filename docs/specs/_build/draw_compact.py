"""非对齐紧密访存的数值小例（用户 11-05 夜，V18-TP-25）。Owner: WangYizhao · 2026-11-05
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_compact.py
输出（figs/）：
  FIG-TP-COMPACT          协议篇 §2.5：A 类 4 bank 配置，一条 20 B 记录从字节 248 开始，跨第 7、8 个存储字
  FIG-L1_SRAM-COMPACT-A   L1 篇 §4.4：A 类 8 bank 配置（借用 W1 的 bank 4–7），同一条记录跨 bank 7 与 bank 8
脚本断言：
  - 字节地址 → 存储字 → bank / 深度按 L1 篇 §4.1 的 A 类换算；相邻两个存储字落不同 bank；
  - 两次带字节写使能的写只改写记录的 20 B，两个存储字的其余字节保持原值；
  - 读回两个存储字、按 248 mod 32 = 24 移位后与写入的 20 B 逐字节相同。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fig_f5_post import SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, C_OFF, C_KEEP, C_LO  # noqa: E402

WORD = 32
A_START, A_LEN = 248, 20                         # 记录的起始字节地址与长度
REC = [(0x40 + i) for i in range(A_LEN)]         # 记录内容（任意可辨的字节值）
OLD = 0x11                                       # 两个存储字里原有的字节（示意）
BANK_LIST = {4: [8, 9, 10, 11], 8: [8, 9, 10, 11, 4, 5, 6, 7]}


def place(word_idx, n_bank):
    lst = BANK_LIST[n_bank]
    return lst[word_idx % n_bank], word_idx // n_bank


def simulate(n_bank):
    w0, w1 = A_START // WORD, (A_START + A_LEN - 1) // WORD
    assert (w0, w1) == (7, 8)
    mem = {w: [OLD] * WORD for w in (w0, w1)}
    writes = []
    for w in (w0, w1):
        lo, hi = max(A_START, w * WORD), min(A_START + A_LEN, (w + 1) * WORD)
        be = [lo <= w * WORD + b < hi for b in range(WORD)]
        for b in range(WORD):
            if be[b]:
                mem[w][b] = REC[w * WORD + b - A_START]
        writes.append((w, lo - w * WORD, hi - w * WORD - 1, place(w, n_bank)))
    # 两次写落不同 bank
    assert writes[0][3][0] != writes[1][3][0]
    # 其余字节保持原值
    assert mem[w0][:A_START - w0 * WORD] == [OLD] * (A_START - w0 * WORD)
    assert mem[w1][A_START + A_LEN - w1 * WORD:] == [OLD] * ((w1 + 1) * WORD - A_START - A_LEN)
    # 读回：两个存储字拼接后按 A_START mod 32 移位
    shift = A_START % WORD
    back = (mem[w0] + mem[w1])[shift:shift + A_LEN]
    assert shift == 24 and back == REC
    return writes, shift


def draw(name, n_bank, note):
    writes, shift = simulate(n_bank)
    cw, ch = 15, 30
    x0, gap = 210, 46
    s = SvgF5(x0 + 2 * WORD * cw + gap + 40, 300)
    xw = [x0, x0 + WORD * cw + gap]
    y = 30
    # 两个存储字的标题
    for k, (w, lo, hi, (bank, depth)) in enumerate(writes):
        s.rich(xw[k] + WORD * cw / 2, y, f'第 {w} 个存储字（字节 {w * WORD}–{w * WORD + WORD - 1}）', 15, 'middle')
        s.rich(xw[k] + WORD * cw / 2, y + 24, f'bank {bank}、深度 {depth}', 14, 'middle', GREY, 600)
    y += 48
    # 字内字节号刻度
    for k in range(2):
        for b in (0, 8, 16, 24):
            s.rich(xw[k] + b * cw + cw / 2, y + 6, str(b), 11, 'middle', GREY, 600)
    y += 16
    # 写后的两个存储字
    s.rich(x0 - 14, y + ch / 2, '写后的内容', 15, 'end')
    for k, (w, lo, hi, _) in enumerate(writes):
        for b in range(WORD):
            hit = lo <= b <= hi
            s.cell(xw[k] + b * cw, y, cw, ch, '', fill=C_KEEP if hit else 'white', size=10, sw=0.8)
    y_mem = y
    y += ch + 18
    # 字节写使能
    s.rich(x0 - 14, y + 14, '字节写使能 be', 15, 'end')
    for k, (w, lo, hi, _) in enumerate(writes):
        s.cell(xw[k] + lo * cw, y, (hi - lo + 1) * cw, 28, f'字节 {lo}–{hi}', fill=C_LO, size=13)
    y += 28 + 34
    # 读回：两个字拼接后移位
    s.rich(x0 - 14, y + ch / 2, f'读回：移位 {shift}', 15, 'end')
    for b in range(A_LEN):
        s.cell(x0 + b * cw, y, cw, ch, '', fill=C_KEEP, size=10, sw=0.8)
    s.rich(x0 + A_LEN * cw + 12, y + ch / 2, f'从第 0 字节起的 {A_LEN} B，与写入相同', 14, 'start', NAVY, 600)
    s.line([(xw[0] + 24 * cw + 4 * cw, y_mem + ch + 2), (x0 + 4 * cw, y - 2)], sw=1.4)
    s.line([(xw[1] + 6 * cw, y_mem + ch + 2), (x0 + (8 + 6) * cw, y - 2)], sw=1.4)
    y += ch + 30
    s.red(x0, y, note, 14)
    assert y + 20 <= s.h
    s.save(name)


if __name__ == '__main__':
    draw('FIG-TP-COMPACT.svg', 4, '相邻存储字落不同 bank')
    draw('FIG-L1_SRAM-COMPACT-A.svg', 8, 'bank 7 是借用的 W1')
