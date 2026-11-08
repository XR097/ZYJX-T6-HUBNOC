"""VNU 损失单元（LOSS）需求篇（11-04 重写稿）的三张图。Owner: WangYizhao · 2026-11-04
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_vnu_loss.py
输出（figs/）：
  FIG-VNU_LOSS-CONN     对外连接：VNU 组框内的 SEL / SMP / NLU / QNT，经组对外的出口级、CRU（命令与标量网）、CCU、RRAM 口、L1 发送侧
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
def _retired_fig_conn():  # 11-05 起由 draw_vnu_conn.py 统一外框生成，本函数不再调用
    # 虚线框 = VNU 组；访问 L1 与上行经 VNU 的 L1 口，上行数据写 L1 后由 L1 组按 MAE 命令经 C2H 发出（V18-L1-03）；
    # 交 CRU 的部分量不落 L1，走专门的核间通路（用户 11-04）
    f = Figure('VNU_LOSS-CONN', '', width=1512, height=1218, out_dir=OUT, max_crossings=2)
    f.container('vnu', 406, 196, 924, 784, 'VNU 组')
    f.block('ccu', 588, 28, 308, 126, '本核 CCU', '指令', kind='control')
    f.block('exit', 42, 322, 266, 98, 'MXU 出口级', '', kind='compute')
    # 11-05 晚第二轮：写 L1 = 向 A 类写集合器里本单元的入口 FIFO 写、wr_stall 回本单元
    # 11-05 按传输协议篇同步：RRAM 口、stall_vnu；与 CRU 的部分量与合并值走命令与标量网；上行由 L1 发送侧发出
    # 11-05 第三轮（V18-TP-21）：交 CRU 的部分量与合并值经 CCU 中转，LOSS 在命令与标量网上无端口；CRU 只与 CCU 相连
    f.block('cru', 42, 28, 266, 126, 'CRU', '命令与标量网（FP32）', kind='external')
    f.block('loss', 588, 294, 308, 434, 'LOSS', '监督梯度\n截断分布统计', kind='function')
    f.block('sel', 1062, 238, 252, 112, 'SEL', '', kind='function')
    f.block('smp', 1062, 392, 252, 112, 'SMP', '', kind='function')
    f.block('nlu', 1062, 560, 252, 70, 'NLU', '', kind='function')
    f.block('qnt', 1062, 686, 252, 70, 'QNT', '', kind='function')
    f.block('l1p', 588, 840, 308, 84, 'VNU 的 RRAM 口', '激活类读口 / 写集合器 FIFO', kind='external')
    f.block('l1', 588, 1064, 308, 84, 'L1 的 A 类空间', '', kind='memory')
    f.block('c2h', 1008, 1064, 336, 84, 'L1 发送侧', 'MAE 发送命令 → C2H', kind='external')
    f.net('c_cmd', 'ccu', 'loss', '启用 / 温度 / CCU → 合并值寄存器', kind='ctrl')
    f.net('o_ccu', 'loss', 'ccu', 'stall_vnu', kind='ctrl')
    f.net('i_exit', 'exit', 'loss', 'logit 流 / z_S')
    # 11-05 用户定：LOSS 不设结果寄存器（梯度范数平方部分和由 NLU 累加），CCU → CRU 的部分量线撤
    f.net('i_cru', 'cru', 'ccu', '合并值', kind='ctrl')
    f.net('i_sel', 'sel', 'loss', '名次项')
    f.net('o_sel', 'loss', 'sel', '释放通知', kind='ctrl')
    f.net('i_smp', 'smp', 'loss', '截断分布')
    f.net('o_smp', 'loss', 'smp', 'log-prob')
    f.net('b_nlu', 'loss', 'nlu', '借用 exp / ln')
    f.net('o_qnt', 'loss', 'qnt', 'dz（BF16）')
    f.net('m_req', 'loss', 'l1p', '写 → FIFO：列表 / 学生侧信息')
    f.net('m_rsp', 'l1p', 'loss', '读：监督记录；wr_stall')
    f.net('p_req', 'l1p', 'l1', '')
    f.net('p_rsp', 'l1', 'l1p', '')
    f.net('o_up', 'l1', 'c2h', '上行数据')
    xs, attempt = f.save()
    print(f.d['id'], 'crossings', xs, 'attempt', attempt)
    finalize(f)
    legend_data(f)


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
