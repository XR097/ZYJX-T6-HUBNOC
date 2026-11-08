"""L2 SRAM 篇的 PPT 风格架构图（手写坐标，复用 draw_tp_arch.py 的 Fig 类与自检）。Owner: WangYizhao · 2026-11-05
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_l2_arch.py
输出（figs/）：
  FIG-L2_SRAM-ARCH  4 象限 × 两堆（4 + 4 bank）；每象限写集合器（核 q 的 L2WP、NI 写两条入口 FIFO → 4 道）；
                    象限读口 q → H2C 道 q（addr / dout / busy）；NI 返回读口；写入握手回发令方；致命错误上报经 hub 控制道。
11-05 夜（V18-TP-26…34、V18-NIE-02）：addr 24 bit + dest（L2 不看）、每拍地址由 MAE 搬运引擎给、撤抢占优先级与"完成由 hub / NI / L1 报"、
                    加计数出口、PIN 窗口由编译链固定。
11-06（V18-TP-35…38）：C2H 分流来源注 C2H 由各核 CCU 发令（逐拍地址由 CCU 给）；计数改写计数（写进 bank 时加一），撤排空。
11-06（V18-TP-41…43）：信号与核内 RRAM 口同名（addr / be / dest / ready），撤 last；写计数按（入链路, 象限）分别维护。
11-06（V18-L2-03）：L2WP 改为每核一条 32 B 写链路（4 条竖总线），C2H 在 hub 里只按 dest 分流、不扇入；每象限 5 条入口 FIFO
                    （核 0–3、NI 写）→ 写集合器（四核轮转、NI 写按 MAE 静态表）；写计数 5 × 4 = 20 个。
11-06 深夜（V18-L2-04 / TP-47）：核 n 的 L2WP 只进象限 n（四条线各下到一个象限，不再是竖总线）；每象限 2 条入口 FIFO（核 q、NI 写）；
                    两来源先后为 RTL 头文件参数；撤写计数与 MAE 比对，改为写入握手（链路反向旁带，NI 写带 src）；NI 写带象限掩码。
自检同 draw_tp_arch.py（文字不出画布、不重叠、不压线、不跨框；连线不穿色块、不共线；交叉自动跳线），0 问题才算通过。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from draw_tp_arch import Fig, P  # noqa: E402

D = '7,4'
QY = [188 + 196 * q for q in range(4)]          # 四象限行的顶
QH = 180
X_BUS_C = [343, 330, 317, 304]                  # L2WP 核 0–3 写链路的竖线（核 q 只下到象限 q；下得越远越靠左，避免交叉）
X_BUS_N = 362                                   # NI 写的竖总线（可进任一象限）
FY = [72, 124]                                  # 象限内 2 条入口 FIFO 的中线偏移（核 q、NI 写）
X_NIR = 1512                                    # NI 返回读的竖总线


def phys(h, q, j):
    return 8 * q + 4 * h + j % 4, j // 4


assert phys(0, 2, 5) == (17, 1) and phys(1, 3, 6) == (30, 1)     # 与正文 §4.2 一致


def fig_arch():
    s = Fig('FIG-L2_SRAM-ARCH.svg', 'FIG-L2_SRAM-ARCH  L2 SRAM：4 象限 × 两堆、每象限写集合器、象限读口与 busy',
            '2 MiB · 32 个单端口 bank × 32 B（一个存储字）· 每象限 8 bank = 堆 0（4 个）+ 堆 1（4 个）· 地址 [堆 1][象限 2][字节号 21]，以字节计')
    s.note(30, 96, ['地址 [堆 h][象限 q][字节号 a]，存储字 j = ⌊a / 32⌋ → bank 8q + 4h + (j mod 4)，深度 ⌊j / 4⌋；写带字节写使能，默认整字写',
                    '核 q 的 L2WP 只写象限 q；NI 写可写任一象限（单位不跨象限，可按象限掩码广播）；每象限 2 条入口 FIFO → 写集合器 → 4 道，先后为头文件参数',
                    '接收桥 ready = 本来源入口 FIFO 未满（通用链路块）；读口撞 bank 拉 busy、重发；每写进一项沿来源链路反向回写入握手，由发令方计数'],
           13, w=1250)
    s.legend(1300, 112, [('inter', '数据 32 B / 拍', 'solid'), ('incore', '读地址 en / addr', 'thin'),
                         ('stall', 'busy / 停发', D)], cols=3, colw=192, size=13, rowh=26)

    # ---------- 左：两个写来源 ----------
    s.block(30, 290, 260, 200, 'C2H 分流', '按 CCU 的通路选择分流 · 不扇入\n核 q 的 C2H → 象限 q\n4 条 × 32 B（合计 128 B）\naddr 24 bit · 各核 CCU 给\n← 写入握手 1 bit / 拍', 'hub', 17, 12)
    s.block(30, 640, 260, 150, 'NI_INT 写（五源）', 'M0 / M1 读入 · PIN 写入\nMAE_DSU 整形 · MAE_CRU 合并\naddr · src · 象限掩码\n← 握手 4 ×（valid + src）', 'ext', 17, 12)
    for k, xb in enumerate(X_BUS_C):                                                # L2WP 第 k 条（核 k）只到象限 k
        ys = 320 + 44 * k
        s.line([(290, ys), (xb, ys), (xb, QY[k] + FY[0]), (400, QY[k] + FY[0])], 'inter', 2.2, net=f'l2wp{k}')
    s.tag(160, 512, 'L2WP 4 条 × 32 B（核 q → 象限 q）', 'inter', 12)
    s.line([(290, 715), (X_BUS_N, 715)], 'inter', 2.6, head=None, net='niw')
    s.line([(X_BUS_N, QY[0] + FY[1]), (X_BUS_N, QY[3] + FY[1])], 'inter', 2.6, head=None, net='niw')
    s.dot(X_BUS_N, 715)

    # ---------- 中：四个象限 ----------
    for q, y0 in enumerate(QY):
        s.group(380, y0, 1340, QH, f'象限 {q}（bank {8 * q}–{8 * q + 7}）', 'mem', 15)
        s.block(400, y0 + FY[0] - 11, 160, 22, f'核 {q} 入口 FIFO', '', 'hub', 12, shadow=False)
        s.block(400, y0 + FY[1] - 11, 160, 22, 'NI 写入口 FIFO', '', 'ext', 12, shadow=False)
        s.line([(X_BUS_N, y0 + FY[1]), (400, y0 + FY[1])], 'inter', 2.2, net='niw')
        if q in (1, 2):                                                             # NI 总线中段的分叉点
            s.dot(X_BUS_N, y0 + FY[1])
        for k in range(2):
            s.line([(560, y0 + FY[k]), (600, y0 + FY[k])], 'inter', 2.2)
        s.block(600, y0 + 40, 190, 127, '写集合器', '每拍每道选一个写者\n两来源先后：头文件参数\n写进 bank 即回握手\n道 i → bank i 或 4+i', 'ctlu', 15, 12, shadow=False)
        # 两堆
        g = s.group(830, y0 + 36, 660, 136, '', 'mem', strip=False, dash='5,4', sw=1.4, fill='#f8fafc')
        s.text(1002, y0 + 52, '堆 0', 14, 'middle', P['mem'][0], 700, box=g)
        s.text(1332, y0 + 52, '堆 1', 14, 'middle', P['mem'][0], 700, box=g)
        for h in (0, 1):
            for i in range(4):
                x = 850 + 330 * h + 78 * i
                s.block(x, y0 + 66, 70, 96, f'bank {8 * q + 4 * h + i}', '', 'mem', 12, shadow=False)
        s.line([(790, y0 + 103), (830, y0 + 103)], 'inter', 3.0)                       # 4 写道
        # 象限读口
        s.block(1530, y0 + 40, 170, 127, f'象限读口 {q}', f'addr ← 道 {q}\ndout / vld → 道 {q}\nbusy：撞 bank 顺延', 'inter', 15, 12, shadow=False)
        s.line([(1490, y0 + 90), (1530, y0 + 90)], 'inter', 3.0)
        # NI 返回读的分支
        s.line([(1490, y0 + 150), (X_NIR, y0 + 150)], 'inter', 2.6, head=None, net='nir')
        if q:
            s.dot(X_NIR, y0 + 150)
        # H2C 道 q
        s.block(1750, y0 + 40, 150, 127, f'H2C 道 {q}', f'→ 四核第 {q} 道\nMAE 搬运引擎逐字\n发读地址\n多播各核独立取走', 'hub', 15, 12)
        s.line([(1700, y0 + 70), (1750, y0 + 70)], 'inter', 3.0)                      # dout
        s.line([(1750, y0 + 105), (1700, y0 + 105)], 'incore', 1.8)                   # en / addr
        s.line([(1700, y0 + 140), (1750, y0 + 140)], 'stall', 2.0, dash=D)            # busy
    s.line([(X_NIR, QY[0] + 150), (X_NIR, 985)], 'inter', 2.6, net='nir')

    # ---------- 下：写入握手、致命错误上报、NI 返回读口 ----------
    s.block(30, 985, 420, 70, '写入握手（链路反向旁带）', '每写进一项回一个 · 核 q ← 象限 q · NI 写带 src\n发令方数满应写量 = 写入完成', 'mem', 15, 11)
    s.block(490, 985, 300, 70, 'L2 致命错误上报', '超出堆容量 · 读 / 写地址象限不符', 'mem', 15, 11)
    s.block(840, 985, 400, 70, 'hub 控制道（命令与标量网）', '→ LIC → CIF → M55：致命错误', 'hub', 15, 11)
    s.line([(790, 1020), (840, 1020)], 'ctrl', 2.4, dash=D)
    s.block(1400, 985, 260, 70, 'NI 返回读口', '→ NI_INT → DDR / M1 · addr ← NI · busy', 'ext', 15, 11)
    return s.save()


if __name__ == '__main__':
    sys.exit(1 if fig_arch() else 0)
