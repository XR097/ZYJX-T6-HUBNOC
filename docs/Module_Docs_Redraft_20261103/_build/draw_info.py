"""外部输入信息篇（L3PU_EXTERNAL_INFORMATION.md）的图。Owner: WangYizhao · 2026-11-06
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_info.py
输出（figs/）：FIG-INFO-FOUR-KINDS  五类信息（指令 / 配置表 / 调用描述符 / 列表 / 数据）从哪来、经哪条口、落在哪、谁消费
11-06 第二版（用户："即使是对于 M1 的口，不也是走 MAE 的搬运引擎吗？……只有从 Slave 来的数据是不需要 MAE 的搬运引擎的"）：
  共享内存 / DDR 里的五样全部经 MAE 搬运引擎（M0 / M1 主口）进芯片；只有外部主方经 PIN 从口直写 L2 不经搬运引擎。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize  # noqa: E402

OUT = HERE.parent


def fig_four_kinds():
    _registry = 'FIG-INFO-FOUR-KINDS.svg'
    f = Figure('INFO-FOUR-KINDS', '', width=1580, height=860, out_dir=OUT, max_crossings=3)
    f.container('shm', 24, 40, 300, 680, '共享内存 / DDR')
    f.block('inst', 40, 90, 268, 100, '指令', '编译链排好的指令序列\n每字 1,024 bit', kind='control')
    f.block('cfg', 40, 210, 268, 100, '配置表源', '范围表 · 开核表 · 阈值表\n序列参数表 · 基址表 · 批行表', kind='control')
    f.block('desc', 40, 330, 268, 100, '调用描述符', '每次调用一份参数记录\n+ 调用输入 / 结果记录', kind='control')
    f.block('lst_m', 40, 450, 268, 100, '列表（M55 产）', 'token 列表 · KV 编辑列表', kind='memory')
    f.block('data', 40, 570, 268, 100, '数据', '权重 · KV · 激活 · 梯度\nMAE 不解释类型', kind='memory')
    f.block('chan', 470, 230, 280, 300, 'MAE 搬运引擎', 'M0 / M1 主口（NI_EXT）\n口对 + 两端地址生成器\n在用列表本地缓存\n可多例化', kind='function')
    f.block('lic', 960, 60, 260, 170, 'LIC', '专用小 SRAM（TCM）：\n指令区 · 配置表区\n调用描述符区', kind='control')
    f.block('l2', 960, 420, 260, 150, '中央 L2', '列表区（LRB）\n阈值表（固定区）\n数据', kind='memory')
    f.block('core', 1340, 60, 220, 170, '计算核', 'CCU 指令 + 配置表参数\nSEL 产录取 / TOPK /\n区块列表', kind='function')
    f.block('pin', 960, 680, 260, 110, '外部主方（系统 DMA / FMC）', 'PIN 从口直写 L2 固定窗口\n不经搬运引擎', kind='external')
    f.net('n_inst', 'inst', 'chan', 'M1 读')
    f.net('n_cfg', 'cfg', 'chan', '')
    f.net('n_desc', 'desc', 'chan', '')
    f.net('n_lst', 'lst_m', 'chan', '')
    f.net('n_data', 'data', 'chan', 'M0 读写')
    f.net('n_lic', 'chan', 'lic', '指令 · 配置表 · 调用描述符')
    f.net('n_l2', 'chan', 'l2', '表 · 列表 · 数据')
    f.net('c_mae', 'lic', 'chan', 'MAE 指令', kind='ctrl')
    f.net('c_core', 'lic', 'core', 'CCU 指令', kind='ctrl')
    f.net('n_sel', 'core', 'l2', '核产的列表')
    f.net('n_use', 'l2', 'chan', '列表')
    f.net('n_pin', 'pin', 'l2', 'PIN 直写')
    xs, attempt = f.save()
    print(f.d['id'], 'crossings', xs, 'attempt', attempt)
    finalize(f)
    assert xs <= 3


if __name__ == '__main__':
    fig_four_kinds()
