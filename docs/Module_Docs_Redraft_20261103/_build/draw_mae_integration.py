"""MAE 组集成篇（MAE_INTEGRATION.md）的三张图。Owner: WangYizhao · 2026-11-06
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_mae_integration.py
输出（figs/）：
  FIG-MAE_INTEGRATION-ARCH-DATA  组的数据链路：对外 D1–D9 + 组内数据连线（PPT 式，复用 draw_mae_arch 的 Fig / PEERS / GROUP）
  FIG-MAE_INTEGRATION-ARCH-CTRL  组的命令类连线：对外 C1–C11 + 组内命令连线（11-06 深夜第二次加 C9 H2C 落地握手、C10 IDN 落地握手、C11 CRU 入口握手，V18-TP-50）；地址线、使能线都画成命令线、不细分（用户 11-06）
  FIG-MAE_INTEGRATION-PATH       数值走查：一条 M0 → L1 指令、IDN 道分配 {2, 2}、每核 64 B，逐拍 addr 与两核写计数
两张架构图外框、对端、六单元位置完全相同（UNITS / PEERS）；框内只画真实存在的硬件（六单元、MAE_ENG 的指令入口两份、
M0 / M1 请求仲裁、搬运引擎叠 × N）；单元内部步骤不画。位置一律用地址说明，不用"指针"（用户 11-06）。
自检沿用 draw_mae_arch.Fig：文字不重叠、不压线、不跨框；连线不穿色块、不共线；交叉自动跳线。0 问题才算通过。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import draw_mae_arch as A                                   # noqa: E402
from draw_mae_arch import Fig, P, GROUP, dimblock, D        # noqa: E402
from svgkit_num import Svg, C_HI, C_LO, C_KEEP, C_SIDE      # noqa: E402

DATE = '2026-11-06'
A.DATE = DATE

# 对端：位置与 draw_mae_arch.PEERS 相同，副标题按本篇两张图分别给
PEER_POS = {k: v[:4] for k, v in A.PEERS.items()}
PEER_TITLE = {k: v[4] for k, v in A.PEERS.items()}
PEER_KIND = {k: v[6] for k, v in A.PEERS.items()}

# 六单元（两张图相同）
UNITS = {
    'ext': (400, 300, 180, 500),
    'int': (680, 480, 420, 330),
    'dsu': (1180, 470, 180, 90),
    'idn': (1180, 710, 180, 100),
    'cru': (1400, 330, 160, 290),
}


def frame(name, title, sub, peers_sub, legend):
    s = Fig(name, title, sub)
    gx, gy, gw, gh = GROUP
    s.group(gx, gy, gw, gh, 'MAE 组 · 六单元（全芯片一组）', 'chip', 16, dash='none', sw=2.4, fill='#fbfcfe')
    for k, (x, y, w, h) in PEER_POS.items():
        if k in peers_sub:
            s.block(x, y, w, h, PEER_TITLE[k], peers_sub[k], PEER_KIND[k], 16, 12)
        else:
            dimblock(s, x, y, w, h, PEER_TITLE[k], '本图不用')
    s.legend(20, 800, legend, cols=1, colw=232, size=13, rowh=27)
    return s


def units(s, subs):
    """六单元：MAE_ENG 展开为指令入口（两份）、M0 / M1 请求仲裁、搬运引擎叠 × N；其余五个画单元框。"""
    s.group(700, 230, 600, 195, 'MAE_ENG', 'ctlu', 15, tx=1120, dash='10,5', sw=2.0, fill='#fffdf7')
    s.block(715, 265, 160, 58, '指令入口（两份）', 'ping-pong · 可连续下发', 'ctlu', 14, 11, shadow=False)
    s.block(715, 340, 160, 58, 'M0 / M1 请求仲裁', '各引擎共用 · 优先级', 'ctlu', 14, 11, shadow=False)
    for k in (2, 1):
        s.group(900 + 5 * k, 255 + 5 * k, 380, 150, '', 'ctlu', 14, strip=False, dash='none', sw=1.4, fill='#fffaf0')
    s.group(900, 255, 380, 150, '', 'ctlu', 14, strip=False, dash='none', sw=2.0, fill='#fffdf7')
    s.block(915, 270, 350, 120, '搬运引擎 × N（一种）', '每个引擎执行一条搬运指令\n逐拍源 / 目的地址 · 计数\n个数与链路数解耦【设计者定】', 'ctlu', 15, 12, shadow=False)
    titles = {'ext': 'NI_EXT', 'int': 'NI_INT', 'dsu': 'MAE_DSU', 'idn': 'MAE_IDN', 'cru': 'MAE_CRU'}
    for k, (x, y, w, h) in UNITS.items():
        s.block(x, y, w, h, titles[k], subs[k], 'hub', 16, 12)


# =====================================================================
# FIG-MAE_INTEGRATION-ARCH-DATA
# =====================================================================
def fig_data():
    s = frame('FIG-MAE_INTEGRATION-ARCH-DATA.svg',
              'FIG-MAE_INTEGRATION-ARCH-DATA  MAE 组：数据链路（对外 D1–D9）',
              '每个对外口只有一个组内单元直接驱动；几个单元共用的口在组内先合并（单位级仲裁）；L2 象限读口 → H2C 道 → 核的数据不经 MAE（只给地址，见命令图）',
              {'lic': '直连口 32 B（D7）',
               'ddr': 'M0 · 256 bit', 'noc': 'M1 · 64 bit · f_IO', 'dma': 'PIN 写入方 · 64 bit',
               'l2': 'NI 写口（D4）· NI 返回读口（D5）\n象限读口另接 H2C 道（不经 MAE）',
               'idn': '每核 4 条 8 B 链路（D6）',
               'hubup': '四核 C2H 各 1 × 32 B（D8）',
               'hubdn': 'L2 象限读出 → 核（不经 MAE）\nMAE_CRU 输出作第二源（D9）'},
              [('axi', '对外 AXI（D1–D3）', 'solid'), ('inter', '核间数据链路', 'solid'),
               ('dim', '灰框 = 本图不用', 'box')])
    units(s, {'ext': 'M0 / M1 主口\nPIN 从口\n地址换算 · 跨域\n宽度适配',
              'int': '读返回分路\n（即运算级 MUX：直通 / DSU / CRU）\n拆拍寄存器 4 × 32 B\nNI-L2C 写客户（五源）· 返回车道',
              'dsu': '数据整形', 'idn': '入站分发网\n交叉 · 多播分叉', 'cru': '数据合并\n归约 · 标量合并\n读集合并\n按条目计到达份数'})
    # ---- D1–D3：三个 AXI 口 ----
    s.line([(270, 360), (400, 360)], 'axi', 3.0, head='both')
    s.tag(335, 344, 'D1 M0 · 256 bit', 'axi', 12)
    s.line([(270, 545), (400, 545)], 'axi', 3.0, head='both')
    s.tag(335, 529, 'D2 M1 · 64 bit', 'axi', 12)
    s.line([(270, 730), (400, 730)], 'axi', 3.0)
    s.tag(335, 714, 'D3 PIN · 64 bit', 'axi', 12)
    # ---- 组内：NI_EXT ↔ NI_INT ----
    s.line([(580, 560), (680, 560)], 'inter', 2.6)
    s.tag(630, 544, '读返回 32 B', 'inter', 11)
    s.line([(680, 620), (580, 620)], 'inter', 2.6)
    s.tag(630, 604, '写出 32 B', 'inter', 11)
    s.line([(580, 700), (680, 700)], 'inter', 2.6)
    s.tag(630, 684, 'PIN 存储字', 'inter', 11)
    # ---- D4 / D5：L2 的 NI 写口与 NI 返回读口 ----
    s.line([(760, 810), (760, 975)], 'inter', 3.0)
    s.tag(752, 890, 'D4 NI 写口 32 B · 任一象限 · 象限掩码', 'inter', 12, 'end')
    s.line([(900, 975), (900, 810)], 'inter', 3.0)
    s.tag(908, 890, 'D5 NI 返回读口 32 B · 任一象限', 'inter', 12, 'start')
    # ---- D6：MAE_IDN → 四核 IDN 接收桥 ----
    s.line([(1270, 810), (1270, 975)], 'inter', 3.0)
    s.tag(1278, 890, 'D6 4 核 × 4 条 × 8 B · 合计 32 B/拍', 'inter', 12, 'start')
    # ---- D7：NI_INT → LIC 直连口 ----
    s.line([(680, 500), (650, 500), (650, 190), (880, 190), (880, 170)], 'inter', 2.6)
    s.tag(765, 206, 'D7 直连口 32 B', 'inter', 12)
    # ---- D8 / D9：MAE_CRU ----
    s.line([(1660, 375), (1560, 375)], 'inter', 3.0)
    s.tag(1610, 359, 'D8 4 × 32 B', 'inter', 11)
    s.line([(1560, 600), (1660, 600)], 'inter', 3.0)
    s.tag(1610, 584, 'D9 第二源', 'inter', 11)
    # ---- 组内：NI_INT → MAE_IDN、NI_INT ↔ MAE_DSU、MAE_DSU → MAE_IDN、NI_INT ↔ MAE_CRU ----
    s.line([(1100, 760), (1180, 760)], 'inter', 2.6)
    s.tag(1140, 744, '4 道 × 8 B', 'inter', 11)
    s.line([(1100, 495), (1180, 495)], 'inter', 2.4)
    s.tag(1140, 479, '入 32 B', 'inter', 11)
    s.line([(1180, 540), (1100, 540)], 'inter', 2.4)
    s.tag(1140, 524, '出 32 B', 'inter', 11)
    s.line([(1270, 560), (1270, 710)], 'inter', 2.4)
    s.tag(1278, 600, '4 道 × 8 B', 'inter', 11, 'start')
    s.line([(1100, 650), (1520, 650), (1520, 620)], 'inter', 2.4)
    s.line([(1545, 620), (1545, 665), (1100, 665)], 'inter', 2.4)
    s.tag(1400, 636, '读路径 / 合并结果 → NI-L2C', 'inter', 11)
    return s.save()


# =====================================================================
# FIG-MAE_INTEGRATION-ARCH-CTRL
# =====================================================================
def fig_ctrl():
    s = frame('FIG-MAE_INTEGRATION-ARCH-CTRL.svg',
              'FIG-MAE_INTEGRATION-ARCH-CTRL  MAE 组：命令类连线（对外 C1–C11）',
              '指令、完成通知、致命错误上报、命令与标量网两个端点、逐拍地址与使能（图上不细分）、写入握手、合并参数；只有搬运引擎收指令，其余单元只收解码后的控制',
              {'cif': 'PIN 首个违规 · Monitor（C8）', 'lic': '指令入口（C1）· 完成通知（C2）',
               'ctl': 'hub 控制道 · 64 bit（C3 / C4）',
               'l2': '写入握手（C6）',
               'hubdn': '道 0–3 的地址与核掩码（C5）\n落地写入握手回程（C9）',
               'idn': 'NWB 落地写入握手（C10）',
               'hubup': 'CRU 入口写入握手回各核（C11）'},
              [('ctrl', '命令类（含地址、使能）', D), ('dim', '灰框 = 本图不用', 'box')])
    units(s, {'ext': 'M0 / M1 主口\nPIN 从口\n（收请求 · 回写响应）',
              'int': 'NI-L2C 写客户：写入握手按 src 分发\nNI 控制道（与 MAE_ENG 合一个端点）',
              'dsu': '数据整形', 'idn': '入站分发网', 'cru': '数据合并\n按条目计到达份数'})
    # ---- C1 / C2 / C7：LIC ----
    s.line([(900, 170), (900, 245), (795, 245), (795, 265)], 'ctrl', 2.2, dash=D)
    s.tag(908, 205, 'C1 指令 64 bit · 标号', 'ctrl', 12, 'start')
    s.line([(1080, 255), (1080, 170)], 'ctrl', 2.2, dash=D)
    s.tag(1088, 205, 'C2 完成通知 · 致命错误上报', 'ctrl', 12, 'start')
    s.line([(870, 170), (870, 190), (690, 190), (690, 480)], 'ctrl', 2.2, dash=D)
    s.tag(780, 206, 'C7 直连口写入握手', 'ctrl', 12)
    # ---- C3 / C4：命令与标量网两个端点 ----
    s.line([(1320, 170), (1320, 225), (1270, 225), (1270, 255)], 'ctrl', 2.2, dash=D, head='both')
    s.tag(1328, 205, 'C3 端点 (a)', 'ctrl', 12, 'start')
    s.line([(1450, 170), (1450, 330)], 'ctrl', 2.2, dash=D, head='both')
    s.tag(1458, 305, 'C4 端点 (b)', 'ctrl', 12, 'start')
    # ---- C5：MAE_ENG → H2C 道 0–3 ----
    s.line([(1290, 300), (1385, 300), (1385, 640), (1660, 640)], 'ctrl', 2.2, dash=D)
    s.tag(1395, 656, 'C5 en · addr · 核掩码 · 四道', 'ctrl', 12, 'start')
    # ---- C6：L2 写入握手 → NI_INT → MAE_ENG ----
    s.line([(900, 975), (900, 810)], 'ctrl', 2.2, dash=D)
    s.tag(908, 890, 'C6 写入握手 4 × (valid + src)', 'ctrl', 12, 'start')
    s.line([(960, 480), (960, 415)], 'ctrl', 2.0, dash=D)
    s.tag(952, 464, '按 src 分给引擎', 'ctrl', 11, 'end')
    # ---- C8：NI_EXT ↔ CIF ----
    s.line([(560, 300), (560, 170)], 'ctrl', 2.2, dash=D, head='both')
    s.tag(552, 255, 'C8 PIN 首个违规 · Monitor', 'ctrl', 12, 'end')
    # ---- 组内：MAE_ENG ↔ NI_EXT ----
    s.line([(715, 370), (580, 370)], 'ctrl', 2.0, dash=D)
    s.tag(630, 354, '请求 · 选口', 'ctrl', 11)
    s.line([(580, 445), (930, 445), (930, 415)], 'ctrl', 2.0, dash=D)
    s.tag(640, 461, '写响应', 'ctrl', 11)
    # ---- 组内：MAE_ENG → NI_INT ----
    s.line([(1020, 415), (1020, 480)], 'ctrl', 2.0, dash=D)
    s.tag(1028, 455, '读请求记录 · 通路选择', 'ctrl', 11, 'start')
    # ---- 组内：MAE_ENG → MAE_DSU / MAE_IDN / MAE_CRU ----
    s.line([(1220, 415), (1220, 470)], 'ctrl', 2.0, dash=D)
    s.tag(1228, 452, '模式 · 地址', 'ctrl', 11, 'start')
    s.line([(1260, 415), (1260, 435), (1370, 435), (1370, 760), (1360, 760)], 'ctrl', 2.0, dash=D)
    s.tag(1362, 680, '核集合 · 单位发完', 'ctrl', 11, 'end')
    s.line([(1290, 350), (1400, 350)], 'ctrl', 2.0, dash=D)
    s.tag(1337, 336, '参数 · 地址', 'ctrl', 11)
    s.line([(1400, 390), (1290, 390)], 'ctrl', 2.0, dash=D)
    s.tag(1337, 404, '合并完成', 'ctrl', 11)
    # ---- C9：各核 LDP 的落地写入握手 → H2C 道 → 发地址的引擎 ----
    s.line([(1660, 600), (1585, 600), (1585, 280), (1290, 280)], 'ctrl', 2.2, dash=D)
    s.tag(1593, 470, 'C9 H2C 落地写入握手', 'ctrl', 11, 'start')
    # ---- C10：各核 NWB 的落地写入握手 → MAE_IDN → 按 src 交引擎 ----
    s.line([(1310, 975), (1310, 810)], 'ctrl', 2.2, dash=D)
    s.tag(1318, 890, 'C10 IDN 落地写入握手', 'ctrl', 12, 'start')
    s.line([(1180, 790), (1165, 790), (1165, 415)], 'ctrl', 2.0, dash=D)
    s.tag(1173, 635, '按 src 交引擎', 'ctrl', 11, 'start')
    # ---- C11：MAE_CRU → 各核 CCU（CRU 入口写入握手，经 C2H 分流回程） ----
    s.line([(1560, 395), (1660, 395)], 'ctrl', 2.2, dash=D)
    s.tag(1625, 380, 'C11', 'ctrl', 11)
    return s.save()


# =====================================================================
# FIG-MAE_INTEGRATION-PATH：一条 M0 → L1 指令，IDN 道分配 {2, 2}，每核 64 B
# =====================================================================
WORD, BEAT = 32, 8
DDR_BASE = 0x40000                   # NPU 侧片外字节地址（示例）
L1_BASE = 1024                       # 两核 L1 A 类目的字节地址（堆 1），两核相同
LANE_CORE = [0, 0, 1, 1]             # MAE_IDN 道 → 目的核（{2, 2}）
N_WORD = 4                           # 共 4 个存储字：核 0 两个、核 1 两个


def path_plan():
    reqs, lanes = [], []
    per_core = {0: 0, 1: 0}
    for w in range(N_WORD):
        core = LANE_CORE[w]
        dst = L1_BASE + per_core[core] * WORD
        per_core[core] += 1
        reqs.append((w, DDR_BASE + w * WORD, w, core, dst))               # (请求号, DDR 地址, 去向道, 核, 目的地址)
        lanes.append([dst + j * BEAT for j in range(WORD // BEAT)])       # 该道 4 拍各自的 addr
    return reqs, lanes, per_core


REQS, LANES, PER_CORE = path_plan()
assert [r[1] for r in REQS] == [0x40000, 0x40020, 0x40040, 0x40060]
assert [(r[3], r[4]) for r in REQS] == [(0, 1024), (0, 1056), (1, 1024), (1, 1056)]
assert LANES[0] == [1024, 1032, 1040, 1048] and LANES[1] == [1056, 1064, 1072, 1080]
assert LANES[2] == LANES[0] and LANES[3] == LANES[1]                   # 两核落同样的地址（各自的 L1）
assert all(len({a // WORD for a in ln}) == 1 for ln in LANES)         # 一个存储字由同一条道送全
assert N_WORD * WORD == sum(len(ln) for ln in LANES) * BEAT == 2 * 64  # 字节守恒：128 B
assert PER_CORE == {0: 2, 1: 2}                                       # 两核写计数各到 2


def fig_path():
    s = Svg(1300, 660)
    s.rich(30, 34, 'M0 → L1 一条搬运指令：IDN 道分配 {2, 2}（道 0、1 → 核 0，道 2、3 → 核 1），每核 64 B = 2 个存储字', 17)
    s.note(30, 66, f'源：DDR 字节地址 0x{DDR_BASE:X} 起连续 128 B；目的：两核 L1 A 类 [堆 1][A][字节 {L1_BASE}] 起各 2 个存储字；拍号只示意先后，功能与时延无关', 14)
    # ① 请求与读请求记录
    s.rich(30, 104, '① MAE_ENG 的搬运引擎发 4 笔 32 B 读请求，每笔记下（去向, 目的逻辑地址）', 15)
    cols = [('请求', 70), ('DDR 地址', 160), ('NI_EXT 返回', 170), ('去向（MAE_IDN 道）', 200), ('目的', 260)]
    x0, y0, rh = 30, 120, 34
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=13)
        x += w
    for i, (n, ddr, lane, core, dst) in enumerate(REQS):
        y = y0 + (i + 1) * rh
        vals = [f'#{n}', f'0x{ddr:X}', f'32 B（第 {i} 拍）', f'道 {lane}', f'核 {core} · [1][A][{dst}]']
        for xx, (_, w), t in zip(xs, cols, vals):
            s.cell(xx, y, w - 6, rh - 4, t, fill=C_LO if core else C_HI, size=13)
    # ② 拆拍与四道
    yb = y0 + 5 * rh + 30
    s.rich(30, yb, '② NI_INT 拆拍寄存器把每个 32 B 拆成 4 × 8 B，交 MAE_IDN 道 i；每拍带自己的 addr，be = 8 位全 1', 15)
    cols2 = [('道', 70), ('目的核', 90)] + [(f'第 {j + 1} 拍 addr', 150) for j in range(4)] + [('NWB 攒满一个存储字', 240)]
    y1 = yb + 16
    xs2, x = [], x0
    for name, w in cols2:
        xs2.append(x)
        s.cell(x, y1, w - 6, rh - 4, name, fill=C_SIDE, size=13)
        x += w
    for i, ln in enumerate(LANES):
        y = y1 + (i + 1) * rh
        core = LANE_CORE[i]
        vals = [f'道 {i}', f'核 {core}'] + [str(a) for a in ln] + [f'写 {ln[0]}–{ln[0] + WORD - 1} → 写计数 +1']
        for xx, (_, w), t in zip(xs2, cols2, vals):
            s.cell(xx, y, w - 6, rh - 4, t, fill=C_LO if core else C_HI, size=13)
    # ③ 两核写计数
    yc = y1 + 5 * rh + 30
    s.rich(30, yc, '③ 各核 NWB 每条入链路攒满 4 拍即整字写进 L1；CCU 比对写计数与应写量', 15)
    s.cell(30, yc + 16, 420, 34, f'核 0：入链路 0、1 各写 1 个存储字 → 合计 {PER_CORE[0]} = 应写量 2', fill=C_HI, size=13)
    s.cell(470, yc + 16, 420, 34, f'核 1：入链路 0、1 各写 1 个存储字 → 合计 {PER_CORE[1]} = 应写量 2', fill=C_LO, size=13)
    s.cell(910, yc + 16, 300, 34, '字节守恒：4 × 32 B = 16 × 8 B = 128 B', fill=C_KEEP, size=13)
    s.red(30, yc + 74, '一个存储字由同一条道送全', 15)
    s.save('FIG-MAE_INTEGRATION-PATH.svg', DATE)


if __name__ == '__main__':
    bad = len(fig_data()) + len(fig_ctrl())
    fig_path()
    sys.exit(1 if bad else 0)
