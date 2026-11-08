"""L1 SRAM 架构图（PPT 风格，1920 × 1080，手写坐标）。Owner: WangYizhao · 2026-11-05
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_l1_arch.py
输出（figs/）：
  FIG-L1_SRAM-ARCH   两堆 × (W0 / W1 / A / S)、写集合器（W 类 8 道、A 类 4 / 8 道、S 类 1 道）、来源入口 FIFO、
                     lane 读口 8 道、4 个激活类读口、接收桥 LDP × 4 / NWB、发送侧桥 + AEB 桥合并、
                     命令网、stall_tx / wr_stall / ready 走向
2026-11-05 夜（V18-TP-26…34）：核间改称带地址的握手写流；IDN 当时为 4 条独立 8 B 链路（11-08 晚 V18-HUB-04 起：每核一条 32 B 链路，
                     NWB 与 LDP 相同，一条入口 FIFO + skid、整字直写，撤攒字寄存器）；
                     完成改计数制（撤 L1 向 MAE 报完成）
2026-11-06（V18-TP-35…38）：C2H 由本核 CCU 发令（发送桥 = CCU 的 C2H 通道，CCU 给逐拍 addr / dest，
                     撤 MAE 的 C2H 发送命令）；CCU → MAE 发出报告；写计数（写进 bank 时加一）交 CCU，撤排空；C2H 口前按单位合并
依据：DATA_TRANSFER_PROTOCOL.md §1.1、§3.1–3.3、§4、§6；V1.8 V18-TP-17 / 18 / 20、V18-TP-26…34；用户 11-05："这两个模块比较重要，需要更直观的说明"。
复用 draw_tp_arch.py 的 Fig 类与自检（文字不重叠、不跨框、不压线；连线不穿色块、不共线；交叉自动跳线）。
取代 draw_l1_sram.py 的 FIG-L1_SRAM-CONN（已退役）。
2026-11-06（V18-TP-41 / 42）：信号与核内 RRAM 口同名（en / ready / din / be / addr / dest）；撤 last：IDN 每拍整字直写（11-08 晚起），C2H 单位边界不上链路。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_tp_arch import Fig  # noqa: E402

D = '6,4'


def fig_l1_arch():
    s = Fig('FIG-L1_SRAM-ARCH.svg', 'FIG-L1_SRAM-ARCH  L1 SRAM：两堆、写集合器、读口与核间桥',
            '青：RRAM 道（每道一个 bank）· 蓝：核间握手写流 ·橙：命令网 · 红虚线：stall_tx / wr_stall / ready · '
            '图示某一阶段：堆 0 是写堆、堆 1 是读堆，下一阶段由指令的堆选对调')
    # ---------------- 上方：CCU、MAE ----------------
    s.block(560, 104, 760, 96, '本核 CCU',
            'L1 全部读与发送侧读的 en / wea / addr · 排开激活类读口同拍撞 bank\n'
            '装写集合器优先级表与 A 类配置 · 收 stall_tx 与各写计数\n发令 C2H：给发送桥逐拍 addr、给 C2H 分流下通路选择', 'ctlu', 20, 13)
    s.block(1500, 104, 390, 96, 'MAE_ENG', '收发出报告（命令网）\n落地链路的 addr 由 MAE 搬运引擎给', 'ctlu', 19, 13)
    s.line([(1320, 152), (1500, 152)], 'ctrl', 3.0)
    s.tag(1410, 134, '发出报告', 'ctrl', 12)
    # ---------------- 中间：L1 两堆 ----------------
    s.group(560, 250, 700, 660, 'L1 SRAM（每核一份，24 个 32 B 单端口 bank + 尺度 SRAM）', 'mem', 14)
    rows = [  # (y, h, 名, 说明)
        (340, 120, 'W0 · bank 0–3', 'W 类 · 出 lane 0–7'),
        (472, 120, 'W1 · bank 4–7', 'W 类 · 出 lane 8–15\n8 bank 配置时归 A 类'),
        (604, 150, 'A · bank 8–11', 'A 类 · 字 j 落列表第 j mod n 项\n任一激活类读口可读任一 bank'),
        (766, 110, 'S · 尺度 SRAM', 'S 类 · 尺度 / 旁带 / bias 行'),
    ]
    for k, hx in enumerate((575, 915)):
        s.group(hx, 296, 330, 600, f'堆 {k}（本阶段：{"写堆" if k == 0 else "读堆"}）', 'mem', 14, dash='5,4', sw=1.4)
        for y, h, name, sub in rows:
            s.block(hx + 14, y, 302, h, name, sub, 'mem', 16, 12, shadow=False)
    # CCU → L1：读侧各道 en / wea / addr
    s.line([(1100, 200), (1100, 250)], 'incore', 3.4)
    s.text(1092, 225, 'en · wea · be · addr（每道一组）', 12, 'end', '#0f766e', 700)
    # ---------------- 左侧：来源与写集合口 ----------------
    s.block(90, 350, 210, 110, 'LDP × 4', 'H2C 接收桥 · 4 条链路\n各一条入口 FIFO + skid\nready = FIFO 未满', 'inter', 17, 12)
    s.block(90, 490, 210, 110, 'NWB', 'IDN 接收桥 · 1 条 32 B 链路\n入口 FIFO + skid\nready = FIFO 未满', 'inter', 17, 12)
    s.block(90, 680, 210, 120, '核内写者', 'QNT · NLU（含出口级）\nSEL / SMP / LOSS / OPT\n各一条入口 FIFO\n收自己的 wr_stall', 'comp', 17, 12)
    s.block(400, 360, 140, 220, 'W 类写集合口', 'NWB 或 H2C 多播\n权重块，按位点\n二选一\n8 道\n道 b ↔ bank b', 'incore', 15, 12)
    s.block(400, 600, 140, 170, 'A 类写集合器', '入口 FIFO ≤ 9 条\n每拍每道按优先级\n选队头落该 bank 者\n4 道 / 8 道\n道 i ↔ 列表第 i 项', 'incore', 15, 12)
    s.block(400, 786, 140, 80, 'S 类写口', 'NWB、LDP 两入\n1 道', 'incore', 15, 12)
    # 核间输入与 ready
    for y in (375, 395, 415, 435):
        s.line([(20, y), (90, y)], 'inter', 2.4)
    s.tag(195, 334, 'H2C 链路 0–3（hub）', 'inter', 12)
    s.line([(90, 448), (20, 448)], 'stall', 2.2, dash=D)
    s.tag(55, 470, 'ready', 'stall', 11)
    s.line([(20, 530), (90, 530)], 'inter', 2.4)
    s.tag(195, 476, 'IDN 链路 · 32 B（HUB_IDN）', 'inter', 12)
    s.line([(90, 578), (20, 578)], 'stall', 2.2, dash=D)
    s.tag(55, 600, 'ready', 'stall', 11)
    # 来源 → 集合口
    s.line([(300, 390), (400, 390)], 'incore', 2.6)                                   # LDP → W
    s.line([(300, 520), (400, 520)], 'incore', 2.6)                                   # NWB → W
    s.line([(300, 430), (320, 430), (320, 640), (400, 640)], 'incore', 2.6)           # LDP → A
    s.line([(300, 560), (340, 560), (340, 670), (400, 670)], 'incore', 2.6)           # NWB → A
    s.line([(300, 730), (400, 730)], 'incore', 2.6)                                   # 核内 → A
    s.line([(300, 410), (360, 410), (360, 810), (400, 810)], 'incore', 2.2)           # LDP → S
    s.line([(300, 580), (380, 580), (380, 840), (400, 840)], 'incore', 2.2)           # NWB → S
    s.line([(400, 755), (300, 755)], 'stall', 2.2, dash=D)                            # wr_stall
    # 集合口 → 写堆（堆 0）
    for y in (410, 530, 680, 826):
        s.line([(540, y), (589, y)], 'incore', 3.4)
    # CCU → 集合器：优先级表与 A 类配置
    s.line([(640, 200), (640, 225), (470, 225), (470, 360)], 'incore', 2.0)
    s.text(462, 300, '优先级表 · A 类配置', 12, 'end', '#0f766e', 700)
    # ---------------- 右侧：读出 ----------------
    s.block(1440, 330, 250, 150, '4 个 pod 的 WWB', '16 条 lane · 按 pod 掩码锁存\n槽 s：lane s / s⊕8 二选一\n尺度 / 旁带行同拍到', 'comp', 17, 12)
    s.block(1440, 560, 250, 180, '激活类读口的客户', 'pod 激活记录缓冲\nNLU（含出口级，读旧值）· QNT\nSEL / SMP / LOSS / OPT\n任一拍每口一个客户\ndout 去向由 CCU 定', 'comp', 17, 12)
    s.block(1440, 780, 250, 110, '发送侧 + 发送桥', '= CCU 的 C2H 通道\n读 L1 占一个激活类读口时隙\naddr 由 CCU 逐拍给', 'inter', 16, 12)
    s.block(1440, 930, 200, 64, 'AEB 桥', 'K 切分部分和直达口', 'inter', 15, 12)
    s.line([(1231, 400), (1440, 400)], 'incore', 4.0)                                 # W0 → lane
    s.tag(1335, 382, 'lane 读口 8 道 · 256 B', 'incore', 12)
    s.line([(1231, 530), (1300, 530), (1300, 450), (1440, 450)], 'incore', 4.0)       # W1 → lane
    s.line([(1231, 820), (1320, 820), (1320, 465), (1440, 465)], 'incore', 2.4)       # S → pod
    s.tag(1326, 760, '尺度行', 'incore', 11, 'start')
    s.line([(1231, 650), (1440, 650)], 'incore', 3.4)                                 # A → 客户
    s.tag(1380, 632, '读口 × 4', 'incore', 12)
    s.line([(1231, 740), (1380, 740), (1380, 835), (1440, 835)], 'incore', 3.0)       # A → 发送侧
    s.tag(1326, 722, '发送侧读', 'incore', 11, 'start')
    # C2H 合并
    s.line([(1690, 820), (1820, 820), (1820, 1050)], 'inter', 4.0, net='c2h')
    s.line([(1640, 962), (1820, 962)], 'inter', 3.0, head=None, net='c2h')
    s.dot(1820, 962)
    s.tag(1600, 1040, 'C2H 32 B + addr 24 + src → hub · 按单位合并，AEB 优先', 'inter', 12)
    # stall_tx → CCU；CCU → 发送桥（逐拍 addr 与通路选择，C2H 由 CCU 发令，V18-TP-51）
    s.line([(1690, 800), (1720, 800), (1720, 235), (1200, 235), (1200, 200)], 'stall', 2.4, dash=D)
    s.tag(1460, 253, 'stall_tx', 'stall', 12)
    s.line([(1280, 200), (1280, 215), (1780, 215), (1780, 860), (1690, 860)], 'inter', 2.6)
    s.tag(1788, 500, 'addr · 通路选择', 'inter', 12, 'start')
    s.tag(1788, 530, 'CCU 逐拍给', 'inter', 12, 'start')
    # ---------------- 说明与图例 ----------------
    s.note(30, 880, ['写：每写者一条 32 B 入口 FIFO；每拍每道选队头落该 bank 者',
                     '优先级表每类一张，随位点命令装；默认 H2C > IDN > 核内',
                     '并发写总需求 ≤ 道数 × 32 B/拍（编译链保证）',
                     '读：读堆无写者；CCU 排开撞 bank；固定 1 拍，无 busy',
                     '落地写地址 = addr；各入链路、各写者写计数 → CCU'], 12, w=500, title='写集合与读出规则')
    s.legend(575, 925, [('incore', 'RRAM 道', 'solid'), ('inter', '核间握手写流', 'solid'),
                        ('ctrl', '命令网', 'solid'), ('stall', 'stall / wr_stall / ready', '6,4')],
             cols=1, colw=270, size=12, rowh=24)
    s.note(880, 925, ['4 bank：A = bank 8–11，写集合口 4 道',
                      '8 bank：W1 归 A，写 8 道，lane 只剩 128 B/拍',
                      '两种配置写者接口不变'], 12, w=360, title='A 类配置（§1.6）')
    return s.save()


if __name__ == '__main__':
    errs = fig_l1_arch()
    sys.exit(1 if errs else 0)
