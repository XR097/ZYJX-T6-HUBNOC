"""VNU 各单元篇连接图的统一外框（用户 11-05）。Owner: WangYizhao · 2026-11-05
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_vnu_conn.py
输出（figs/）：FIG-VNU_NLU-CONN、FIG-VNU_QNT-CONN、FIG-VNU_SEL-CONN、FIG-VNU_OPT-CONN、FIG-VNU_LOSS-CONN

用户 11-05："对于所有的 VNU 的顶层架构图，我都建议规范下 VNU 外部接口的配置，不要有的有上行，有的没有"；
"我希望画出全部对端，只是把不需要的标灰"。规则：
- 框外只画 VNU 组的全部直接对端，五张图位置、大小、标题相同：
  上方 本核 CCU；左侧 MXU 阵列的 AEB（11-08 起出口级归 NLU，V18-NLU-06）、MXU FBA 粗分数直达口；下方 VNU 的 RRAM 口（框内）→ L1 的 A 类空间。
- 本单元不用的对端画灰（dim），不连线。
- 对端之后的去向（CRU、L1 发送侧 → C2H、IDN / H2C 落地）不画，正文 §2 交代。
- 框内只画与本单元直接往来的同组单元（右列）。QNT / SEL / LOSS 从出口级收到的向量 11-08 起画成来自 NLU（出口级子模块）的组内连线。
各 VNU 的连接图由本脚本统一生成。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize  # noqa: E402

OUT = HERE.parent
W, H = 1640, 1218
UNIT_RECT = (714, 266, 308, 462)
PEER_X, PEER_W = 1214, 266


def frame(key, unit_id, unit_title, unit_sub, uses, ccu_down, ccu_up, l1_sub, exit_in='', exit_out='', fba_in=''):
    """建统一外框。uses ⊆ {'exit', 'fba'}：本单元用到的 MXU 对端；CCU 与 L1 每个单元都用。"""
    f = Figure(key, '', width=W, height=H, out_dir=OUT, max_crossings=2)
    f.container('vnu', 462, 196, 1052, 784, 'VNU 组')
    f.block('ccu', 714, 28, 308, 126, '本核 CCU', '指令 / 地址推理 / 输出去向', kind='control')
    f.block('exit', 42, 280, 266, 126, 'MXU 阵列 AEB', '4 pod 条目 16 × BF16' if 'exit' in uses else '本单元不用（经 NLU 出口级）',
            kind='compute', dim='exit' not in uses)
    f.block('fba', 42, 476, 266, 126, 'MXU FBA 直达口', '粗分数' if 'fba' in uses else '本单元不用',
            kind='compute', dim='fba' not in uses)
    f.block(unit_id, *UNIT_RECT, unit_title, unit_sub, kind='function')
    f.block('l1p', 714, 840, 308, 84, 'VNU 的 RRAM 口', '激活类读口 / 写集合器 FIFO', kind='external')
    f.block('l1', 714, 1064, 308, 84, 'L1 的 A 类空间', l1_sub, kind='memory')
    f.net('c_cmd', 'ccu', unit_id, ccu_down, kind='ctrl')
    f.net('o_ccu', unit_id, 'ccu', ccu_up, kind='ctrl')
    if 'exit' in uses:
        f.net('i_exit', 'exit', unit_id, exit_in)
        if exit_out:
            f.net('o_exit', unit_id, 'exit', exit_out)
    if 'fba' in uses:
        f.net('i_fba', 'fba', unit_id, fba_in)
    f.net('m_req', unit_id, 'l1p', '写 din + 长度 → FIFO')
    f.net('m_rsp', 'l1p', unit_id, '读出（1 拍）/ wr_stall')
    f.net('p_req', 'l1p', 'l1', '')
    f.net('p_rsp', 'l1', 'l1p', '')
    return f


def peer(f, id, y, h, title, sub=''):
    f.block(id, PEER_X, y, PEER_W, h, title, sub, kind='function')


def save(f):
    xs, attempt = f.save()
    print(f.d['id'], 'crossings', xs, 'attempt', attempt)
    finalize(f)
    p = OUT / 'figs' / f'{f.d["id"]}.svg'
    s = p.read_text(encoding='utf-8')
    s = s.replace('━━ 主要数据', '━━ 数据', 1)
    s = s.replace('┄ 控制 / 事件', '┄ 控制 / 事件　灰框 = 本单元不用的对端', 1)
    p.write_bytes(s.replace('\r\n', '\n').encode('utf-8'))
    assert xs <= 2


def fig_nlu():
    _registry = 'FIG-VNU_NLU-CONN.svg'  # 供 build_figure_registry 识别产出
    f = frame('VNU_NLU-CONN', 'nlu', 'NLU（含出口级子模块）', '逐元素 / 归约与归一化\n二维旋转 / 在线 softmax\n流式累加\n出口级：分发 / 残差加 / 停放', {'exit'},
              '指令 / 参数', 'stall_vnu / AEB ready', '行状态 / 暂存 / 嵌入行 / 残差 / 停放',
              exit_in='AEB 条目')
    peer(f, 'sel', 266, 98, 'SEL')
    peer(f, 'qnt', 434, 98, 'QNT')
    peer(f, 'sol', 602, 112, 'SMP / LOSS / OPT', '分时借用元件 / 收出口级分发')
    f.net('o_sel', 'nlu', 'sel', '评分 / logit 流')
    f.net('i_sel', 'sel', 'nlu', '录取位图')
    f.net('o_qnt', 'nlu', 'qnt', '待量化 / x′ / 投影结果')
    f.net('i_qnt', 'qnt', 'nlu', '量化结果')
    f.net('b_sol', 'sol', 'nlu', '分时借用')
    save(f)


def fig_qnt():
    _registry = 'FIG-VNU_QNT-CONN.svg'  # 供 build_figure_registry 识别产出
    f = frame('VNU_QNT-CONN', 'qnt', 'QNT', '按组量化编码 / 两平面\n按判决位压紧\n记录组装 / 解码', set(),
              '指令 / 参数', 'keep / F / stall', '记录 / 卸载 / 装载表')
    peer(f, 'nlu', 266, 98, 'NLU（含出口级）')
    peer(f, 'sel', 434, 98, 'SEL')
    peer(f, 'loss', 602, 98, 'LOSS')
    f.net('i_nlu', 'nlu', 'qnt', '待量化 / x′ / v / 梯度')
    f.net('o_nlu', 'qnt', 'nlu', '量化结果 / 解码 K')
    f.net('o_sel', 'qnt', 'sel', '激活通道幅值')
    f.net('i_sel', 'sel', 'qnt', '判决位')
    f.net('i_loss', 'loss', 'qnt', 'dz')
    save(f)


def fig_sel():
    _registry = 'FIG-VNU_SEL-CONN.svg'  # 供 build_figure_registry 识别产出
    f = frame('VNU_SEL-CONN', 'sel', 'SEL', '比较与排序\n阈值 / 相对阈值\n流式 TOPK / 封顶', {'fba'},
              '模式 / 参数 / 屏蔽位 / 档号', '判决位 / 计数 / 最大类号 / stall_vnu', '名次缓冲 / 暂存 / 阈值套 / 上行对象',
              fba_in='粗分数')
    peer(f, 'nlu', 266, 84, 'NLU（含出口级）')
    peer(f, 'qnt', 406, 98, 'QNT')
    peer(f, 'smp', 560, 70, 'SMP')
    peer(f, 'loss', 672, 70, 'LOSS')
    f.net('i_nlu', 'nlu', 'sel', '评分 / 长流评分')
    f.net('i_qnt', 'qnt', 'sel', '激活通道幅值')
    f.net('o_qnt', 'sel', 'qnt', '判决位')
    f.net('o_rank', 'sel', ['smp', 'loss'], '名次项')
    save(f)


def fig_opt():
    _registry = 'FIG-VNU_OPT-CONN.svg'  # 供 build_figure_registry 识别产出
    f = frame('VNU_OPT-CONN', 'opt', 'OPT', '一步参数更新\n算法由设计者定', set(),
              '指令 / 参数', '读完 / 组完成 / 共享量 / stall', '副本 / 状态 / 梯度')
    peer(f, 'nlu', 448, 98, 'NLU', '合作通路')
    f.net('b_nlu', 'opt', 'nlu', '借用元件')
    save(f)


def fig_loss():
    _registry = 'FIG-VNU_LOSS-CONN.svg'  # 供 build_figure_registry 识别产出
    f = frame('VNU_LOSS-CONN', 'loss', 'LOSS', '监督梯度\n截断分布统计', set(),
              '启用 / 温度', 'stall_vnu', '监督记录 / 列表 / 学生侧信息 / 合并值')
    peer(f, 'sel', 266, 98, 'SEL')
    peer(f, 'smp', 392, 98, 'SMP')
    peer(f, 'nlu', 518, 98, 'NLU（含出口级）')
    peer(f, 'qnt', 644, 56, 'QNT')
    f.net('i_sel', 'sel', 'loss', '名次项')
    f.net('o_sel', 'loss', 'sel', '释放通知', kind='ctrl')
    f.net('i_smp', 'smp', 'loss', '截断分布')
    f.net('o_smp', 'loss', 'smp', 'log-prob')
    f.net('i_nlu', 'nlu', 'loss', 'logit 流 / z_S')
    f.net('b_nlu', 'loss', 'nlu', '借用 exp / ln')
    f.net('o_qnt', 'loss', 'qnt', 'dz（BF16）')
    save(f)


if __name__ == '__main__':
    fig_nlu()
    fig_qnt()
    fig_sel()
    fig_opt()
    fig_loss()
