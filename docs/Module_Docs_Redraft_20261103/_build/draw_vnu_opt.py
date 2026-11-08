"""VNU 优化器单元（OPT）需求篇（11-04 重写稿）的连接图。Owner: WangYizhao · 2026-11-04
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_vnu_opt.py
输出（figs/）：
  FIG-VNU_OPT-CONN  对外连接：VNU 组框内的 NLU（合作通路），经组对外的 CCU、CRU（命令网）、RRAM 口、IDN 落地与 L1 发送侧
更新算法由设计者定（V18-OPT-01），本篇不画算法数值例。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize  # noqa: E402

OUT = HERE.parent


def _retired_fig_conn():  # 11-05 起由 draw_vnu_conn.py 统一外框生成，本函数不再调用
    # 状态与梯度经 IDN 由 L1 组落入 L1，OPT 经 VNU 的 L1 口读；写回数据写 L1 后由 L1 组按 MAE 命令经 C2H 发出（V18-L1-03）
    f = Figure('VNU_OPT-CONN', '', width=1512, height=1218, out_dir=OUT, max_crossings=2)
    f.container('vnu', 406, 196, 924, 784, 'VNU 组')
    # 11-05 晚第二轮：写 L1 = 向 A 类写集合器里本单元的入口 FIFO 写、wr_stall 回本单元
    # 11-05 按传输协议篇同步：RRAM 口、stall_vnu；CRU 结果经命令网；撤保留标记（读完 = 最后读者完成事件）
    f.block('ccu', 588, 28, 308, 126, '本核 CCU', '转 LIC', kind='control')
    # 11-05 第三轮（V18-TP-21）：与 CRU 的标量经 CCU 中转，OPT 在命令网上无端口；CRU 只与 CCU 相连
    f.block('cru', 42, 28, 266, 126, 'CRU', '命令网（FP32）', kind='external')
    f.block('opt', 588, 294, 308, 434, 'OPT', '一步参数更新\n算法由设计者定', kind='function')
    f.block('nlu', 1036, 448, 252, 98, 'NLU', '合作通路', kind='function')
    f.block('l1p', 588, 840, 308, 84, 'VNU 的 RRAM 口', '激活类读口 / 写集合器 FIFO', kind='external')
    f.block('idn', 42, 1064, 336, 84, 'IDN 落地', '状态 / 梯度随权重流到达', kind='external')
    f.block('l1', 588, 1064, 308, 84, 'L1 的 A 类空间', '', kind='memory')
    f.block('c2h', 1008, 1064, 336, 84, 'L1 发送侧', 'MAE 发送命令 → C2H', kind='external')
    f.net('c_cmd', 'ccu', 'opt', '指令 / 标量参数', kind='ctrl')
    f.net('o_ccu', 'opt', 'ccu', '读完 / 组完成 / 共享量 / stall', kind='event')
    # 11-05 用户定：OPT 不设结果寄存器（梯度范数平方部分和由 NLU 累加），CCU → CRU 的部分值线撤
    f.net('i_cru', 'cru', 'ccu', '跨核归约结果', kind='ctrl')
    f.net('b_nlu', 'opt', 'nlu', '借用元件')
    f.net('m_rsp', 'l1p', 'opt', '读：副本 / 状态 / 梯度；wr_stall')
    f.net('m_req', 'opt', 'l1p', '写 → FIFO：新副本 / 新状态')
    f.net('p_req', 'l1p', 'l1', '')
    f.net('p_rsp', 'l1', 'l1p', '')
    f.net('i_idn', 'idn', 'l1', '')
    f.net('o_up', 'l1', 'c2h', '写回 DDR')
    xs, attempt = f.save()
    print(f.d['id'], 'crossings', xs, 'attempt', attempt)
    finalize(f)
    p = OUT / 'figs' / 'FIG-VNU_OPT-CONN.svg'
    p.write_bytes(p.read_bytes().decode('utf-8').replace('━━ 主要数据', '━━ 数据').encode('utf-8'))


if __name__ == '__main__':
    pass  # 连接图改由 draw_vnu_conn.py 生成
