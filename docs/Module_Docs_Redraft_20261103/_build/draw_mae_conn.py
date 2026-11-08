"""MAE 组各单元篇连接图的统一外框（用户 11-05："画出全部对端，只是把不需要的标灰"）。Owner: WangYizhao · 2026-11-05（11-05 夜改五单元外框）
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_mae_conn.py
输出（figs/）：无。11-06 晚 FIG-MAE_NI_EXT-CONN / NI_INT-CONN / IDN-CONN / DSU-CONN 退役到 figs/_retired_20261106/，
  生图函数改名 _retired_fig_ni_ext / _retired_fig_ni_int / _retired_fig_idn / _retired_fig_dsu；现行架构图见 draw_mae_arch.py。

MAE 组 = MAE_ENG、NI_EXT、NI_INT、MAE_IDN、MAE_DSU（用户 11-05 夜，V18-NII-03 / 04；11-06 WSU 改名 DSU，V18-MAE-05）。
组框内：本单元画在 UNIT_RECT；其余四个同组单元依次放进 MEMBER_SLOTS 的四个位置，
        与本单元直接往来的画实框并连线，不直接往来的画灰框（副标题"本单元不用"）。
组外直接对端（各篇位置、大小、标题相同）：
  上方：命令与标量网（hub 控制道：搬运指令、事件、错误、长度转发）、LIC（MAE 指令入口）、CIF（PIN 窗口常量表 · 首错）
  左侧：DDR 控制器 P0、SoC 片上互联总线（HSRAM P2 · DDR P2 · FMC 主端）、系统 DMA / FMC 从端
  下方：中央 L2（NI 写口 / NI 返回读口）、四核 IDN 接收桥（每核 1 条 32 B 链路，NWB；11-08 晚 V18-HUB-04 起）
本单元不用的对端画灰（dim），不连线；对端之后的去向不画。
2026-11-08 晚（V18-HUB-04）：本文件全部生图函数已退役、不出图；只把外框对端与 NI_INT-CONN 的 IDN 标签改为每核 1 条 32 B，
  _retired_fig_idn（MAE_IDN-CONN）保留 11-06 原文、不改。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from figkit3 import Figure  # noqa: E402
from fig_f5_post import finalize  # noqa: E402

OUT = HERE.parent
W, H = 1520, 1110
UNIT_RECT = (600, 330, 240, 420)
# 其余四个同组单元的位置：左列与本单元直接相邻（留 ≥ 112 px 给两条网），右列放在外侧
MEMBER_SLOTS = [
    (1040, 400, 190, 120),
    (1040, 620, 190, 140),
    (1255, 400, 185, 120),
    (1255, 620, 185, 140),
]
MEMBER_SLOTS_WIDE = [
    (1040, 400, 190, 120),
    (1040, 620, 190, 140),
    (1300, 400, 150, 120),
    (1300, 620, 150, 140),
]
PEERS = {
    'ctl': (580, 28, 260, 110, '命令与标量网', 'hub 控制道', 'control'),
    'lic': (900, 28, 260, 110, 'LIC', 'MAE 指令入口', 'control'),
    'cif': (1220, 28, 260, 110, 'CIF', 'PIN 窗口常量表 · 首错', 'control'),
    'ddr': (28, 340, 252, 110, 'DDR 控制器 P0', '256 bit 独占', 'external'),
    'noc': (28, 500, 252, 120, 'SoC 片上互联总线', 'HSRAM P2 · DDR P2 · FMC 主端', 'external'),
    'dma': (28, 670, 252, 110, '系统 DMA / FMC 从端', 'PIN 的写入方', 'external'),
    'l2': (600, 940, 300, 100, '中央 L2', 'NI 写口 / NI 返回读口', 'memory'),
    'idn': (1060, 940, 380, 100, '四核 IDN 接收桥（每核 1 条 32 B）', 'NWB', 'memory'),
}


def frame(key, unit_id, unit_title, unit_sub, uses):
    f = Figure(key, '', width=W, height=H, out_dir=OUT, max_crossings=2)
    f.container('mae', 560, 210, 900, 640, 'MAE 组')
    for pid, (x, y, w, h, title, sub, kind) in PEERS.items():
        used = pid in uses
        f.block(pid, x, y, w, h, title, sub if used else '本单元不用', kind=kind, dim=not used)
    f.block(unit_id, *UNIT_RECT, unit_title, unit_sub, kind='function')
    return f


def members(f, items, slots=None):
    """items：四个 (id, 标题, 副标题, 是否与本单元直接往来)，依次放进 slots（默认 MEMBER_SLOTS）。
    四个都与本单元往来时右列要外移（slots 传 MEMBER_SLOTS_WIDE），否则右列的网从左列块之间穿不过去。"""
    slots = slots or MEMBER_SLOTS
    assert len(items) == len(slots)
    for (mid, title, sub, used), rect in zip(items, slots):
        f.block(mid, *rect, title, sub if used else '本单元不用', kind='function', dim=not used)


def save(f):
    xs, attempt = f.save()
    print(f.d['id'], 'crossings', xs, 'attempt', attempt)
    finalize(f)
    p = OUT / 'figs' / f'{f.d["id"]}.svg'
    s = p.read_text(encoding='utf-8')
    s = s.replace('━━ 主要数据', '━━ 数据', 1)
    s = s.replace('┄ 控制 / 事件', '┄ 控制 / 事件　灰框 = 本单元不用的对端或同组单元', 1)
    p.write_bytes(s.replace('\r\n', '\n').encode('utf-8'))
    assert xs <= 2


def _retired_fig_ni_ext():
    _registry = 'FIG-MAE_NI_EXT-CONN.svg'  # 供 build_figure_registry 识别产出
    f = frame('MAE_NI_EXT-CONN', 'ext', 'NI_EXT', 'M0 / M1 主口协议端\nPIN 从口协议端\n跨时钟 · 宽度适配\n固定窗口检查',
              {'cif', 'ctl', 'ddr', 'noc', 'dma'})
    members(f, [
        ('eng', 'MAE_ENG', '发起 M0 / M1 读写', True),
        ('nii', 'NI_INT', '读返回分路 · NI-L2C', True),
        ('idn_u', 'MAE_IDN', '', False),
        ('wsu', 'MAE_DSU', '', False),
    ])
    # 组内
    f.net('c_req', 'eng', 'ext', '读写请求', kind='ctrl')
    f.net('o_resp', 'ext', 'eng', '写响应', kind='ctrl')
    f.net('o_rd', 'ext', 'nii', '读返回 / PIN 存储字')
    f.net('i_wr', 'nii', 'ext', '写出数据 · L2 写计数')
    # 组外
    f.net('m0_i', 'ddr', 'ext', 'M0 读数据 / B 响应')
    f.net('m0_o', 'ext', 'ddr', 'M0 地址 / 写数据')
    f.net('m1_o', 'ext', 'noc', 'M1 地址 / 写数据')
    f.net('m1_i', 'noc', 'ext', 'M1 读数据 / B 响应')
    f.net('p_i', 'dma', 'ext', 'PIN 写 / 调试读')
    f.net('p_o', 'ext', 'dma', 'B 响应 / SLVERR')
    f.net('w_o', 'ext', 'cif', '首个违规', kind='ctrl')
    f.net('w_i', 'cif', 'ext', '窗口常量表（初始化）', kind='ctrl')
    f.net('e_o', 'ext', 'ctl', '主口错误', kind='ctrl')
    save(f)


def _retired_fig_ni_int():
    _registry = 'FIG-MAE_NI_INT-CONN.svg'  # 供 build_figure_registry 识别产出
    f = frame('MAE_NI_INT-CONN', 'nii', 'NI_INT', '指令执行与分路\n读返回分路（五去向）\nL2 客户通道 NI-L2C\nNI 控制道端点',
              {'ctl', 'lic', 'l2'})
    members(f, [
        ('ext', 'NI_EXT', 'M0 / M1 / PIN 协议端', True),
        ('wsu', 'MAE_DSU', '数据整形', True),
        ('eng', 'MAE_ENG', '搬运指令', True),
        ('idn_u', 'MAE_IDN', '按核集合 → 四核', True),
    ], slots=MEMBER_SLOTS_WIDE)
    # 组内
    f.net('c_cmd', 'eng', 'nii', '搬运指令', kind='ctrl')
    f.net('i_rd', 'ext', 'nii', '读返回 / PIN 存储字')
    f.net('o_wr', 'nii', 'ext', '写出数据')
    f.net('o_idn', 'nii', 'idn_u', '32 B + addr + 核集合')
    f.net('o_wsu', 'nii', 'wsu', '整形输入')
    f.net('i_wsu', 'wsu', 'nii', '整形输出')
    # 组外
    f.net('l2_w', 'nii', 'l2', 'NI 写口 32 B')
    f.net('l2_r', 'l2', 'nii', 'NI 返回读口 32 B')
    f.net('lic_d', 'nii', 'lic', '直连口：指令 · 配置表 · 描述符')
    f.net('ctl_o', 'nii', 'ctl', '长度转发 · 错误转报', kind='ctrl')
    save(f)


def _retired_fig_idn():
    _registry = 'FIG-MAE_IDN-CONN.svg'  # 供 build_figure_registry 识别产出
    f = frame('MAE_IDN-CONN', 'idnu', 'MAE_IDN', '4 道 × 8 B 交叉\n每核 4 条独立链路\n多播缓冲（各核独立取走）\n两源按单位轮流',
              {'idn'})
    members(f, [
        ('nii', 'NI_INT', '读返回分路', True),
        ('wsu', 'MAE_DSU', '整形输出', True),
        ('eng', 'MAE_ENG', 'MAE 搬运引擎', True),
        ('ext', 'NI_EXT', '', False),
    ])
    f.net('c_alloc', 'eng', 'idnu', '每单位的核集合 · 单位边界', kind='ctrl')
    f.net('d_nii', 'nii', 'idnu', '4 道数据 + addr')
    f.net('d_wsu', 'wsu', 'idnu', '4 道数据 + addr')
    f.net('o_links', 'idnu', 'idn', '4 核 × 4 条 8 B 链路')
    save(f)


def _retired_fig_dsu():
    _registry = 'FIG-MAE_DSU-CONN.svg'  # 供 build_figure_registry 识别产出
    f = frame('MAE_DSU-CONN', 'dsuu', 'MAE_DSU', '四种整形模式\n按字重排 · 转置\n块尺度与旁带\n两平面合并\n两源 DDR · L2\n两宿 L1 · L2',
              set())
    members(f, [
        ('nii', 'NI_INT', '分路 · NI-L2C', True),
        ('idn_u', 'MAE_IDN', '去核 L1', True),
        ('eng', 'MAE_ENG', '搬运引擎', True),
        ('ext', 'NI_EXT', '', False),
    ])
    f.net('c_cmd', 'eng', 'dsuu', '整形搬运指令', kind='ctrl')
    f.net('i_in', 'nii', 'dsuu', '整形输入')
    f.net('o_l2', 'dsuu', 'nii', '输出 → L2')
    f.net('o_idn', 'dsuu', 'idn_u', 'Wᵀ 列字块 · 全码记录')
    save(f)


if __name__ == '__main__':
    # 11-06 晚：四个单元篇的 CONN 图退役，改用 draw_mae_arch.py 的 PPT 式 ARCH 图
    # （任务书 _build/MAE_CRU_MERGE_BRIEF_20261106.md §1 规则 11）；旧图在 figs/_retired_20261106/，
    # 函数加 _retired_ 前缀保留备查，不再调用。
    pass
