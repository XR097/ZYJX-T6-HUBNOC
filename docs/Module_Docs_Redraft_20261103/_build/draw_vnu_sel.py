"""VNU 选择单元（SEL）需求篇（11-04 重写稿）的五张图。Owner: WangYizhao · 2026-11-04
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_vnu_sel.py [--md]
输出（figs/）：
  FIG-VNU_SEL-CONN      对外连接：输入口、输出口、RRAM 口与 L1 发送侧、控制与阈值套
  FIG-VNU_SEL-THRESH    阈值模式 2 bit 分档：8 个评分与两个门限（平方尺度阈值换算成 BF16 平方根门限）
  FIG-VNU_SEL-RELATIVE  相对阈值：第一遍求最大值，第二遍与 α × 最大值比较
  FIG-VNU_SEL-TOPK      流式 TOPK：12 个评分逐个到达，k = 3，中途暂存与域末发布
  FIG-VNU_SEL-MASK      屏蔽与强制入选：前 2 名 + 强制位 + 屏蔽位，屏蔽优先
脚本断言：各图的判决结果由本脚本按正文规则算出（BF16 舍入、并列取序号小者、强制不占名额、屏蔽优先）。
"""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize, SvgF5  # noqa: E402
from svgkit_num import GREY, NAVY, C_OFF, C_KEEP, C_HI, C_LO, C_LEFT  # noqa: E402

OUT = HERE.parent


def bf16(x):
    """FP32 → BF16（RNE），返回 Python float。"""
    b = struct.unpack('<I', struct.pack('<f', x))[0]
    b = (b + 0x7FFF + ((b >> 16) & 1)) & 0xFFFF0000
    return struct.unpack('<f', struct.pack('<I', b))[0]


# ---------------- 阈值 2 bit 分档（正文 §3.2） ----------------
TAU_F, TAU_C = 0.25, 0.0625                          # 平方尺度阈值
G_F, G_C = bf16(TAU_F ** 0.5), bf16(TAU_C ** 0.5)     # 装表的 BF16 平方根门限
assert (G_F, G_C) == (0.5, 0.25)
TH_SCORES = [0.625, 0.125, 0.3125, 0.0625, 0.5, 0.1875, 0.875, 0.25]
assert all(bf16(v) == v for v in TH_SCORES)


def fcz(v):
    v = abs(bf16(v))
    return 'F' if v >= G_F else ('C' if v >= G_C else 'Z')


TH_OUT = [fcz(v) for v in TH_SCORES]
assert TH_OUT == ['F', 'Z', 'C', 'Z', 'F', 'Z', 'F', 'C']    # 等于门限的 0.5、0.25 分别判 F、C

# ---------------- 相对阈值（正文 §3.3） ----------------
ALPHA = 0.5
REL = [3, 9, 1, 6, 2, 4, 10, 5]
RUNMAX = [max(REL[:i + 1]) for i in range(len(REL))]
REL_TH = ALPHA * RUNMAX[-1]
REL_OUT = [int(v >= REL_TH) for v in REL]
assert RUNMAX[-1] == 10 and REL_TH == 5 and REL_OUT == [0, 1, 0, 1, 0, 0, 1, 1]

# ---------------- 流式 TOPK（正文 §3.4） ----------------
K = 3
STREAM = [0.5, 2.0, 1.2, 3.1, 0.7, 2.6, 1.9, 0.2, 2.8, 1.0, 0.4, 2.6]


def topk(items, k):
    # 评分降序；并列取序号小者
    return sorted(items, key=lambda p: (-p[1], p[0]))[:k]


def stream_topk(vals, k):
    buf, snaps = [], {}
    for i, v in enumerate(vals):
        buf = topk(buf + [(i, v)], k)             # 每到一个评分插入一次
        snaps[i] = list(buf)
    return snaps


SNAPS = stream_topk(STREAM, K)
assert SNAPS[len(STREAM) - 1] == topk(list(enumerate(STREAM)), K)     # 流式结果 = 整体排序
SNAP_AT = [5, 8, 11]
assert [i for i, _ in SNAPS[5]] == [3, 5, 1]
assert [i for i, _ in SNAPS[8]] == [3, 8, 5]
assert [i for i, _ in SNAPS[11]] == [3, 8, 5]                         # 第 11 个与第 5 个同为 2.6，取序号小的 5

# ---------------- 屏蔽与强制入选（正文 §4） ----------------
MK_SCORES = [0.2, 1.5, 0.4, 2.1, 0.9, 1.1, 3.0, 2.5]
MK_K = 2
MASK = [0, 0, 0, 0, 0, 0, 1, 1]
FORCE = [1, 0, 0, 0, 0, 0, 0, 1]
cand = [(i, v) for i, v in enumerate(MK_SCORES) if not MASK[i] and not FORCE[i]]   # 强制入选不占名额
MODE = [0] * 8
for i, _ in topk(cand, MK_K):
    MODE[i] = 1
FINAL = [int((MODE[i] or FORCE[i]) and not MASK[i]) for i in range(8)]             # 屏蔽优先
assert MODE == [0, 1, 0, 1, 0, 0, 0, 0]
assert FINAL == [1, 1, 0, 1, 0, 0, 0, 0]
assert FORCE[7] and MASK[7] and not FINAL[7]


# ---------------- 图 1：对外连接 ----------------
def _retired_fig_conn():  # 11-05 起由 draw_vnu_conn.py 统一外框生成，本函数不再调用
    # 虚线框 = VNU 组；框内是 SEL 与和它直接往来的 VNU 单元；跨出框的连线都是 VNU 组的对外接口，
    # 其中访问 L1 与上行两项经 VNU 的共用口（口的个数与共享方式由 VNU 集成篇定义，用户 11-04）
    f = Figure('VNU_SEL-CONN', '', width=1512, height=1218, out_dir=OUT, max_crossings=2)
    f.container('vnu', 406, 196, 924, 784, 'VNU 组')
    # 11-05 晚第二轮：写 L1 = 向 A 类写集合器里本单元的入口 FIFO 写、wr_stall 回本单元
    # 11-05 按传输协议篇同步：RRAM 口（地址由 CCU 推理）、stall_vnu、上行先写 L1 由 L1 发送侧发出；撤 ULB 与"VNU 上行口"
    f.block('ccu', 588, 28, 308, 98, '本核 CCU', '指令 / 档号 / 地址推理', kind='control')
    f.block('fba', 42, 322, 266, 84, 'MXU FBA', '粗分数直达口', kind='compute')
    f.block('exit', 42, 476, 266, 84, 'MXU 出口级', '长流评分', kind='compute')
    f.block('thr', 42, 630, 266, 84, '阈值套', 'H2C 落地 L1 后读入', kind='control')
    f.block('sel', 588, 294, 308, 434, 'SEL', '比较与排序\n阈值 / 相对阈值\n流式 TOPK / 封顶', kind='function')
    f.block('nlu', 1036, 266, 252, 84, 'NLU', '', kind='function')
    f.block('qnt', 1036, 406, 252, 98, 'QNT', '', kind='function')
    f.block('smp', 1036, 560, 252, 70, 'SMP', '', kind='function')
    f.block('loss', 1036, 672, 252, 70, 'LOSS', '', kind='function')
    f.block('l1p', 448, 840, 308, 84, 'VNU 的 RRAM 口', '激活类读口 / 写集合器 FIFO', kind='external')
    f.block('l1', 448, 1064, 308, 84, 'L1 的 A 类空间', '名次缓冲 / 暂存 / 上行对象', kind='memory')
    f.block('ulb', 1008, 1064, 300, 84, 'L1 发送侧', 'MAE 发送命令 → C2H', kind='external')
    f.net('c_cmd', 'ccu', 'sel', '模式 / 参数 / 屏蔽位 / 档号', kind='ctrl')
    f.net('o_ccu', 'sel', 'ccu', '判决位 / 计数 / 最大类号 / stall_vnu')
    f.net('i_fba', 'fba', 'sel', '粗分数')
    f.net('i_exit', 'exit', 'sel', '长流评分')
    f.net('c_thr', 'thr', 'sel', '阈值套', kind='ctrl')
    f.net('i_nlu', 'nlu', 'sel', '评分 / 统计量')
    f.net('i_qnt', 'qnt', 'sel', '激活通道幅值')
    f.net('o_qnt', 'sel', 'qnt', '判决位')
    f.net('o_rank', 'sel', ['smp', 'loss'], '名次项')
    f.net('m_req', 'sel', 'l1p', '写 → FIFO')
    f.net('m_rsp', 'l1p', 'sel', '读出（1 拍）/ wr_stall')
    f.net('p_req', 'l1p', 'l1', '')
    f.net('p_rsp', 'l1', 'l1p', '')
    f.net('o_up', 'l1', 'ulb', '位图 / 序号列表')
    xs, attempt = f.save()
    print(f.d['id'], 'crossings', xs, 'attempt', attempt)
    finalize(f)


# ---------------- 图 2：阈值 2 bit 分档 ----------------
FCZ_FILL = {'F': C_HI, 'C': C_LO, 'Z': C_OFF}


def fig_thresh():
    s = SvgF5(1080, 260)
    x0, cw, ch = 150, 110, 44
    for i, v in enumerate(TH_SCORES):
        s.rich(x0 + i * cw + (cw - 10) / 2, 30, f'元素 {i}', 15, 'middle', GREY, 600)
        s.cell(x0 + i * cw, 52, cw - 10, ch, f'{v:g}', size=15)
        s.cell(x0 + i * cw, 124, cw - 10, ch, TH_OUT[i], fill=FCZ_FILL[TH_OUT[i]], size=16)
    s.rich(x0 - 16, 52 + ch / 2, '|评分|', 15, 'end')
    s.rich(x0 - 16, 124 + ch / 2, '分档', 15, 'end')
    s.note(x0, 206, f'门限 F：bf16(√{TAU_F:g}) = {G_F:g}　　门限 C：bf16(√{TAU_C:g}) = {G_C:g}', 15)
    s.red(x0 + 4 * cw + (cw - 10) / 2, 186, '等于门限判通过', 14, 'middle')
    s.save('FIG-VNU_SEL-THRESH.svg')


# ---------------- 图 3：相对阈值 ----------------
def fig_relative():
    s = SvgF5(1080, 300)
    x0, cw, ch = 210, 104, 44
    rows = [('评分', [f'{v}' for v in REL], ['white'] * 8),
            ('第一遍：当前最大值', [f'{m}' for m in RUNMAX], [C_LEFT if RUNMAX[i] == REL[i] else 'white' for i in range(8)]),
            (f'第二遍：≥ {ALPHA:g} × {RUNMAX[-1]} = {REL_TH:g}', ['选中' if o else '—' for o in REL_OUT],
             [C_KEEP if o else C_OFF for o in REL_OUT])]
    for i in range(8):
        s.rich(x0 + i * cw + (cw - 10) / 2, 30, f'元素 {i}', 15, 'middle', GREY, 600)
    for r, (lab, vals, fills) in enumerate(rows):
        y = 52 + r * 64
        s.rich(x0 - 16, y + ch / 2, lab, 15, 'end')
        for i in range(8):
            s.cell(x0 + i * cw, y, cw - 10, ch, vals[i], fill=fills[i], size=15)
    s.red(x0 + 7 * cw + (cw - 10) / 2, 52 + 3 * 64 + 8, '5 ≥ 5，选中', 14, 'middle')
    s.save('FIG-VNU_SEL-RELATIVE.svg')


# ---------------- 图 4：流式 TOPK ----------------
def fig_topk():
    s = SvgF5(1240, 420)
    x0, cw, ch = 180, 86, 44
    for i, v in enumerate(STREAM):
        s.rich(x0 + i * cw + (cw - 8) / 2, 30, f'#{i}', 15, 'middle', GREY, 600)
        s.cell(x0 + i * cw, 52, cw - 8, ch, f'{v:g}', size=15)
    s.rich(x0 - 16, 52 + ch / 2, '到达顺序', 15, 'end')
    labels = {5: '#5 到达后（暂存）', 8: '#8 到达后（暂存）', 11: '域末发布'}
    for r, at in enumerate(SNAP_AT):
        y = 150 + r * 76
        s.rich(x0 - 16, y + ch / 2, labels[at], 15, 'end')
        for j, (i, v) in enumerate(SNAPS[at]):
            s.cell(x0 + j * 170, y, 160, ch, f'#{i}：{v:g}', fill=C_KEEP if at == SNAP_AT[-1] else C_LEFT, size=15)
    s.red(x0 + 3 * 170 + 10, 150 + 1 * 76 + ch / 2, '#8 挤掉 #1', 15)
    s.red(x0 + 3 * 170 + 10, 150 + 2 * 76 + ch / 2, '#11 与 #5 同为 2.6，留序号小的 #5', 15)
    s.save('FIG-VNU_SEL-TOPK.svg')


# ---------------- 图 5：屏蔽与强制入选 ----------------
def fig_mask():
    s = SvgF5(1080, 400)
    x0, cw, ch = 210, 104, 40
    rows = [('评分', [f'{v:g}' for v in MK_SCORES], ['white'] * 8),
            ('屏蔽位', ['1' if m else '0' for m in MASK], [C_HI if m else 'white' for m in MASK]),
            ('强制入选位', ['1' if v else '0' for v in FORCE], [C_LO if v else 'white' for v in FORCE]),
            (f'前 {MK_K} 名（不含强制与屏蔽）', ['1' if v else '0' for v in MODE], [C_LEFT if v else 'white' for v in MODE]),
            ('最终选中', ['1' if v else '0' for v in FINAL], [C_KEEP if v else C_OFF for v in FINAL])]
    for i in range(8):
        s.rich(x0 + i * cw + (cw - 10) / 2, 30, f'元素 {i}', 15, 'middle', GREY, 600)
    for r, (lab, vals, fills) in enumerate(rows):
        y = 52 + r * 58
        s.rich(x0 - 16, y + ch / 2, lab, 15, 'end')
        for i in range(8):
            s.cell(x0 + i * cw, y, cw - 10, ch, vals[i], fill=fills[i], size=15)
    s.red(x0 + 7 * cw + (cw - 10) / 2, 52 + 5 * 58 + 6, '屏蔽优先', 14, 'middle')
    s.save('FIG-VNU_SEL-MASK.svg')


def md():
    print('| 元素 | ' + ' | '.join(str(i) for i in range(8)) + ' |')
    print('|---|' + '---|' * 8)
    print('| 评分 | ' + ' | '.join(f'{v:g}' for v in TH_SCORES) + ' |')
    print('| 分档 | ' + ' | '.join(TH_OUT) + ' |')


if __name__ == '__main__':
    fig_thresh()
    fig_relative()
    fig_topk()
    fig_mask()
    if '--md' in sys.argv:
        md()
