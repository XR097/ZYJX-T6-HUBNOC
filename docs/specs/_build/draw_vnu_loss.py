"""VNU 损失单元（LOSS）需求篇（11-04 重写稿）的三张图。Owner: WangYizhao · 2026-11-04
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_vnu_loss.py
输出（figs/）：
  FIG-VNU_LOSS-CONN     对外连接：VNU 组框内的 SEL / SMP / NLU / QNT，经组对外的出口级、CRU（命令网）、CCU、RRAM 口、L1 发送侧
  FIG-VNU_LOSS-ORDER    参与词号列表：两组候选合并、去重、升序；dz 与列表同序压紧，IGE 按同一列表取列
  FIG-VNU_LOSS-LOGPROB  截断分布 log-prob：K_top = 4、T = 1，减最大值、exp、求和、ln
脚本断言：列表与 log-prob 的数值由本脚本按正文规则算出。
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize, SvgF5  # noqa: E402
from svgkit_num import GREY, C_OFF, C_KEEP, C_LEFT, C_W  # noqa: E402

OUT = HERE.parent

# ---------------- 参与词号列表（正文 §3.1.2） ----------------
CAND_A = [3, 12, 40]
CAND_B = [7, 12]
S_LIST = sorted(set(CAND_A) | set(CAND_B))
assert S_LIST == [3, 7, 12, 40]
assert len(CAND_A) + len(CAND_B) - len(S_LIST) == 1          # 重复的 12 只出一次
OUTSIDE = 25
assert OUTSIDE not in S_LIST

# ---------------- 截断分布 log-prob（正文 §3.2） ----------------
LOGITS = [2.0, 1.0, 1.0, -1.0]
T_TEMP = 1.0
Y = 1
ZMAX = max(v / T_TEMP for v in LOGITS)
EXPS = [math.exp(v / T_TEMP - ZMAX) for v in LOGITS]
SUM = sum(EXPS)
LSE = ZMAX + math.log(SUM)
LOGP = LOGITS[Y] / T_TEMP - LSE
PROBS = [e / SUM for e in EXPS]
assert round(SUM, 4) == 1.7855 and round(LSE, 4) == 2.5797 and round(LOGP, 4) == -1.5797
assert PROBS[1] == PROBS[2] and round(PROBS[1], 4) == 0.2060      # 并列两项概率相同
assert abs(sum(PROBS) - 1) < 1e-12


# ---------------- 图 1：对外连接 ----------------


def legend_data(f):
    # 本图无同网分支，finalize 不改图例；与 SEL / NLU 图一致写"数据"
    p = OUT / 'figs' / f'{f.d["id"]}.svg'
    p.write_bytes(p.read_bytes().decode('utf-8').replace('━━ 主要数据', '━━ 数据').encode('utf-8'))


# ---------------- 图 2：参与词号列表与 dz 同序 ----------------
def fig_order():
    s = SvgF5(980, 420)
    lx, cw, ch = 250, 110, 44
    # 两组候选
    s.rich(lx - 16, 52 + ch / 2, '候选词号 组 1', 15, 'end')
    for j, v in enumerate(CAND_A):
        s.cell(lx + j * cw, 52, cw - 10, ch, str(v), fill=C_LEFT if v in CAND_B else 'white', size=15)
    s.rich(lx - 16, 116 + ch / 2, '候选词号 组 2', 15, 'end')
    for j, v in enumerate(CAND_B):
        s.cell(lx + j * cw, 116, cw - 10, ch, str(v), fill=C_LEFT if v in CAND_A else 'white', size=15)
    s.cell(lx + 4 * cw + 30, 84, 150, ch, f'词号 {OUTSIDE}', fill=C_OFF, size=15, dash='5,4')
    s.note(lx + 4 * cw + 30, 84 + ch + 22, '不在任一组', 14)
    # 合并后的列表、dz、gather 列
    rows = [('参与词号列表（升序）', [str(v) for v in S_LIST], C_KEEP),
            ('dz（同序压紧）', [f'dz_{{{v}}}' for v in S_LIST], C_KEEP),
            ('IGE 取的 W_{LM} 列', [f'第 {v} 列' for v in S_LIST], C_W)]
    for r, (lab, vals, fill) in enumerate(rows):
        y = 210 + r * 64
        s.rich(lx - 16, y + ch / 2, lab, 15, 'end')
        for j, v in enumerate(vals):
            s.cell(lx + j * cw, y, cw - 10, ch, v, fill=fill, size=15)
    for j in range(len(S_LIST)):
        s.rich(lx + j * cw + (cw - 10) / 2, 196, f'j = {j}', 13, 'middle', GREY, 500)
    s.red(lx + 2 * cw + (cw - 10) / 2, 30, '12 只出一次', 14, 'middle')
    s.red(lx + 4 * cw + 30, 210 + ch / 2, '25 无 dz', 14)
    s.save('FIG-VNU_LOSS-ORDER.svg')


# ---------------- 图 3：截断分布 log-prob ----------------
def fig_logprob():
    s = SvgF5(980, 400)
    lx, cw, ch = 300, 150, 44
    for i in range(len(LOGITS)):
        s.rich(lx + i * cw + (cw - 10) / 2, 30, f'项 {i}', 15, 'middle', GREY, 600)
    rows = [('logit z', [f'{v:g}' for v in LOGITS]),
            (f'z − max（max = {ZMAX:g}）', [f'{v - ZMAX:g}' for v in LOGITS]),
            ('exp', [f'{e:.4f}' for e in EXPS]),
            ('概率 p', [f'{p:.4f}' for p in PROBS])]
    for r, (lab, vals) in enumerate(rows):
        y = 52 + r * 60
        s.rich(lx - 16, y + ch / 2, lab, 15, 'end')
        for i in range(len(LOGITS)):
            fill = C_KEEP if i == Y else (C_LEFT if i == 2 else 'white')
            s.cell(lx + i * cw, y, cw - 10, ch, vals[i], fill=fill, size=15)
    s.red(lx + 2 * cw + (cw - 10) / 2, 52 + 3 * 60 + ch + 16, '与项 1 并列，概率相同', 14, 'middle')
    y = 52 + 4 * 60 + 34
    s.note(lx, y, f'和 = {SUM:.4f}　lse = {ZMAX:g} + ln {SUM:.4f} = {LSE:.4f}', 15)
    s.note(lx, y + 34, f'ln p(项 {Y}) = {LOGITS[Y]:g} − {LSE:.4f} = {LOGP:.4f}', 15)
    s.save('FIG-VNU_LOSS-LOGPROB.svg')


if __name__ == '__main__':
    fig_order()
    fig_logprob()
