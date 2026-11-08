"""片上数据传输协议篇的数值 / 时序小例图。Owner: WangYizhao · 2026-11-05（11-05 夜按 V18-TP-26…34 改）
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_transfer_protocol.py
输出（figs/）：四张架构图（FIG-TP-ARCH-*）由 _build/draw_tp_arch.py 产出，不在本脚本。
  十张数值 / 时序小例（svgkit_num 规则，数值由脚本算出并断言）
    FIG-TP-ADDR-ACCUM      核内例：CCU 基址 + 字节累加 → [堆][类][字号]，记录级对齐，含环形回绕；bank 落位；多道口
    FIG-TP-ADDR-MAP        同一个 A 类地址在两堆、四核的落位
    FIG-TP-INCORE-TIMING   写当拍、读 1 拍、读写交错
    FIG-TP-STREAM-BEAT     6 拍单位的逐拍 addr（链路上无末拍标记），多播到两核、分叉点按已取位分叉（V18-TP-53）
    FIG-TP-LENGTH-REPORT   变长对象：紧挨写 + 长度表 → CCU 发送 → 握手数满后发出报告 → MAE 按表读、搬完后转发应写量（11-07 V18-TP-58）
    FIG-TP-CTRL-MSG        Fusion 段进段 SRAM、成员进"下一条"寄存器、可选的执行完成进队列
    FIG-TP-STALL-CHAIN     分级握手
    FIG-TP-OBJECT-ALIGN    ③ 档对象：4 条记录紧挨存放，长度表单独存（11-07 V18-TP-58）
    FIG-TP-FIXED-ITEM      ② 档 K 平面末 tile 20 / 32 有效，个数由指令给（原 FIG-TP-SLOT-COUNT，11-07 改名）
    FIG-TP-WINDOW-GATHER   权重驻留：4 token × 3 窗口的产出次序，每窗口一个对象 + 长度表，MAE 按表聚集（取代 FIG-TP-TOKEN-SLOT）
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit_num import Svg, NAVY, INK, GREY, RED, C_OFF, C_KEEP, C_W, C_SIDE, C_ACC, C_LEFT  # noqa: E402

DATE = '2026-11-08'
ROW = 32

# ---------------- PPT 风格调色 ----------------
P = {
    'incore': ('#0f766e', '#ccfbf1'),   # 核内 SRAM 口总线：青
    'inter':  ('#1d4ed8', '#dbeafe'),   # 核间数据网：蓝
    'ctrl':   ('#c2410c', '#ffedd5'),   # 命令网：橙
    'stall':  ('#b91c1c', '#fee2e2'),   # stall：红
    'mem':    ('#334155', '#e2e8f0'),   # 存储
    'comp':   ('#6d28d9', '#ede9fe'),   # 计算单元
    'ctlu':   ('#b45309', '#fef3c7'),   # 控制单元
    'ext':    ('#475569', '#f1f5f9'),   # 外部
    'hub':    ('#0369a1', '#e0f2fe'),   # hub
}


class Ppt(Svg):
    """PPT 美学：标题条、阴影圆角色块、带底色的线标签、图例。"""

    def __init__(self, w=1920, h=1080):
        super().__init__(w, h)
        self.out.insert(1, '<defs>'
                        '<filter id="sh" x="-5%" y="-5%" width="115%" height="120%">'
                        '<feDropShadow dx="3" dy="4" stdDeviation="4" flood-color="#0f172a" flood-opacity="0.22"/></filter>'
                        + ''.join(f'<marker id="m_{k}" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto">'
                                  f'<path d="M0,0 L9,4 L0,8Z" fill="{v[0]}"/></marker>' for k, v in P.items())
                        + '</defs>')
        self.out.append(f'<rect width="100%" height="100%" fill="#f8fafc"/>')

    def title(self, t, sub=''):
        self.out.append(f'<rect x="0" y="0" width="{self.w}" height="86" fill="{NAVY}"/>')
        self.rich(40, 36, t, 30, 'start', 'white', 700)
        if sub:
            self.rich(40, 66, sub, 17, 'start', '#cbd5e1', 500)

    def block(self, x, y, w, h, title, sub='', kind='mem', size=20, subsize=15, rx=12, shadow=True):
        stroke, fill = P[kind]
        f = ' filter="url(#sh)"' if shadow else ''
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2.4"{f}/>')
        lines = sub.split('\n') if sub else []
        th = size + 8 + len(lines) * (subsize + 6)
        y0 = y + h / 2 - th / 2 + size / 2 + 2
        self.rich(x + w / 2, y0, title, size, 'middle', stroke, 700)
        for i, s in enumerate(lines):
            self.rich(x + w / 2, y0 + size / 2 + 8 + i * (subsize + 6) + subsize / 2, s, subsize, 'middle', INK, 500)

    def group(self, x, y, w, h, title, kind='ext', size=18):
        stroke, fill = P[kind]
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="white" stroke="{stroke}" stroke-width="2" stroke-dasharray="10,6"/>')
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{size + 16}" rx="14" fill="{fill}" stroke="none"/>')
        self.out.append(f'<rect x="{x}" y="{y + 10}" width="{w}" height="{size + 6}" fill="{fill}" stroke="none"/>')
        self.rich(x + 16, y + (size + 16) / 2, title, size, 'start', stroke, 700)

    def arrow(self, pts, kind='inter', sw=3.2, dash=None, both=False, head=True):
        stroke = P[kind][0]
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        ds = f' stroke-dasharray="{dash}"' if dash else ''
        m = f' marker-end="url(#m_{kind})"' if head else ''
        ms = f' marker-start="url(#m_{kind})"' if both else ''
        self.out.append(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="none" stroke-linejoin="round"{m}{ms}{ds}/>')

    def tag(self, x, y, s, kind='inter', size=14, anchor='middle'):
        """带底色的线标签。"""
        stroke, fill = P[kind]
        plain = s
        wid = sum((size if ord(ch) > 0x2E80 else 0.56 * size) for ch in plain) + 14
        left = x - (wid if anchor == 'end' else wid / 2 if anchor == 'middle' else 0)
        self.out.append(f'<rect x="{left:.0f}" y="{y - size / 2 - 5:.0f}" width="{wid:.0f}" height="{size + 10}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
        self.rich(left + 7, y, s, size, 'start', stroke, 700)

    def legend(self, x, y, items, title='图例'):
        h = 34 + len(items) * 30
        wmax = max(sum((15 if ord(ch) > 0x2E80 else 8.3) for ch in s) for _, s, _ in items) + 90
        self.out.append(f'<rect x="{x}" y="{y}" width="{wmax:.0f}" height="{h}" rx="10" fill="white" stroke="{GREY}" stroke-width="1.4" filter="url(#sh)"/>')
        self.rich(x + 14, y + 20, title, 16, 'start', NAVY, 700)
        for i, (kind, s, style) in enumerate(items):
            yy = y + 48 + i * 30
            if style == 'box':
                self.out.append(f'<rect x="{x + 14}" y="{yy - 10}" width="40" height="20" rx="5" fill="{P[kind][1]}" stroke="{P[kind][0]}" stroke-width="2"/>')
            else:
                self.arrow([(x + 14, yy), (x + 54, yy)], kind, 3.2, dash=style if style not in ('solid',) else None)
            self.rich(x + 66, yy, s, 15, 'start', INK, 500)


def port(s, x, y, label, kind, size=13):
    """小端口标签（圆角小牌）。"""
    s.tag(x, y, label, kind, size)


# =====================================================================
# 小例 1：基址 + 字节累加与回绕
# =====================================================================
REC = [40, 24, 56, 20]
BASE_ROW, RING_L = 6, 6          # 基址 [0][A][字 6]，环长 6 行
# 记录级对齐（用户 11-05）：每条记录从整行起、占 ceil(n/32) 行、尾部补 0
REC_ROWS = [-(-n // ROW) for n in REC]
FIRST = [sum(REC_ROWS[:i]) for i in range(len(REC))]             # 每条记录的相对首字号 r_i
TOTAL = sum(REC_ROWS)                                             # 对象占的行数
assert REC_ROWS == [2, 1, 2, 1] and FIRST == [0, 2, 3, 5] and TOTAL == 6
NEXT_ROW = BASE_ROW + (TOTAL % RING_L)
assert NEXT_ROW == 6                                              # 第 7 拍回绕到行 6


# 写侧逐拍：生产方攒满一行交一拍；每拍的 din 装的是哪条记录的哪些字节（尾行补 0）
def write_beats():
    beats = []
    for i, n in enumerate(REC):
        for k in range(REC_ROWS[i]):
            lo, hi = k * ROW, min((k + 1) * ROW, n)
            pad = (k + 1) * ROW - hi
            r = FIRST[i] + k
            beats.append((r, BASE_ROW + r % RING_L, f'记{i} B{lo}–{hi - 1}' + (f' + 补 0 {pad} B' if pad else '')))
    return beats


WB = write_beats()
assert len(WB) == 6 and WB[0][2] == '记0 B0–31' and WB[1][2] == '记0 B32–39 + 补 0 24 B'
assert WB[5][2] == '记3 B0–19 + 补 0 12 B' and [b[1] for b in WB] == [6, 7, 8, 9, 10, 11]
# 读侧：读记录 2（首行 r_2 = 3，长 56 B = 2 个存储字）
R2_FIRST, R2_LEN, R2_ROWS = FIRST[2], REC[2], REC_ROWS[2]
assert R2_FIRST == 3 and R2_ROWS == 2


def fig_addr_accum():
    s = Svg(1500, 1040)
    s.rich(30, 30, 'FIG-TP-ADDR-ACCUM  核内例：CCU 的地址累加落到 RRAM 口的信号上：写一个变长对象、再读其中一条记录', 20)
    s.note(30, 58, f'地址以字节计；对齐使用时是 32 的倍数，图中按存储字序号写（字 j = 字节号 32j）；基址 = [堆 0][类 A][字 {BASE_ROW}]，环长 L = {RING_L} 个存储字 = {RING_L * ROW} B', 14)
    s.note(30, 80, f'4 条记录 {REC} B，记录级对齐：各占 {REC_ROWS} 个存储字、尾部补 0，共 {TOTAL} 个存储字；CCU 保有字计数 r 与各记录首字号 r_i（单位都是存储字）', 14)
    cols = {0: '#fde3c4', 1: '#d6e6f7', 2: '#dcefd2', 3: '#f3d9ef'}
    # ---------- 写：QNT 攒整行 → RRAM 写口，CCU 给 addr ----------
    X0, Y0, CW, RH = 190, 136, 190, 38
    s.rich(30, Y0 - 22, '写（QNT 产出 → L1 A 类）：每拍一个存储字 32 B；addr = 基址字号 + (r mod L)，r 每拍 +1（单位：存储字）', 16)
    rows = ['拍', 'en', 'wea', 'CCU 字计数 r', 'addr（给 L1）', 'din（生产方攒的存储字）']
    for i, nm in enumerate(rows):
        s.rich(X0 - 12, Y0 + i * RH + RH / 2, nm, 14, 'end')
    for k, (r, row, part) in enumerate(WB):
        x = X0 + k * CW
        s.cell(x, Y0, CW, RH, f'{k}', C_OFF, 13)
        s.cell(x, Y0 + RH, CW, RH, '1', C_KEEP, 13)
        s.cell(x, Y0 + 2 * RH, CW, RH, '1', C_W, 13)
        s.cell(x, Y0 + 3 * RH, CW, RH, f'{r}', 'white', 13)
        s.cell(x, Y0 + 4 * RH, CW, RH, f'[0][A][字 {row}]', C_SIDE, 13)
        idx = int(part[1])
        s.rect(x, Y0 + 5 * RH, CW, RH * 1.3, fill=cols[idx], sw=1.2)
        for j, ln in enumerate(part.split(' + ')):
            s.rich(x + CW / 2, Y0 + 5 * RH + 14 + j * 20, ln, 12, 'middle', INK, 600)
    yb = Y0 + 5 * RH + RH * 1.3 + 26
    s.red(30, yb, f'第 7 拍（下一对象或续写）：r = 6 → addr = 字 {BASE_ROW} + (6 mod {RING_L}) = 字 {NEXT_ROW}，回绕由 CCU 的加法做，L1 看到的只是又一个字号', 14)
    s.note(30, yb + 26, f'CCU 按记录头的长度 n_i 记下每条记录的首字号 r_i = r_(i−1) + ⌈n_(i−1)/32⌉：r = {FIRST}；记录之间不共享存储字', 14)
    # ---------- 读：取记录 2 ----------
    Y1 = yb + 80
    s.rich(30, Y1 - 22, f'读（取记录 2：首字 r_2 = {R2_FIRST}，长 {R2_LEN} B = {R2_ROWS} 个存储字）：CCU 从字 {BASE_ROW + R2_FIRST} 起连发 {R2_ROWS} 次普通读', 16)
    rows2 = ['拍', 'en', 'wea', 'addr（给 L1）', 'dout + vld（下一拍）']
    X1, CW2 = 190, 260
    for i, nm in enumerate(rows2):
        s.rich(X1 - 12, Y1 + i * RH + RH / 2, nm, 14, 'end')
    seq = [('t', 1, 0, f'[0][A][字 {BASE_ROW + R2_FIRST}]', '—'),
           ('t+1', 1, 0, f'[0][A][字 {BASE_ROW + R2_FIRST + 1}]', f'字 {BASE_ROW + R2_FIRST} 的 32 B'),
           ('t+2', 0, '—', '—', f'字 {BASE_ROW + R2_FIRST + 1} 的 32 B（含补 0）')]
    for k, (t, en, wea, addr, dout) in enumerate(seq):
        x = X1 + k * CW2
        s.cell(x, Y1, CW2, RH, t, C_OFF, 13)
        s.cell(x, Y1 + RH, CW2, RH, f'{en}', C_KEEP if en else 'white', 13)
        s.cell(x, Y1 + 2 * RH, CW2, RH, f'{wea}', 'white', 13)
        s.cell(x, Y1 + 3 * RH, CW2, RH, addr, C_SIDE if addr != '—' else 'white', 13)
        s.cell(x, Y1 + 4 * RH, CW2, RH, dout, cols[2] if dout != '—' else 'white', 13)
    s.note(30, Y1 + 5 * RH + 22, '消费方从字 9 字节 0 起按记录头解析，长度到 56 B 为止、忽略补 0；没有字内偏移，没有旁带，没有跨字', 14)
    s.red(30, Y1 + 5 * RH + 50, '对应关系：CCU 的字计数 → RRAM 的 addr；生产方攒字 + 补 0 → din；记录头长度 → CCU 的首字号 r_i → 读时的 addr', 14)
    # ---------- 右侧：这 6 行落在 A 类 bank 里的样子 ----------
    BX, BY = 1010, Y1 - 22
    s.rich(BX, BY, '6 个存储字在 A 类 bank 里的落位', 15)
    s.note(BX + 250, BY, '字 j → bank 8+(j mod 4)，深 ⌊j/4⌋', 12)
    bw, bh = 108, 30
    for b in range(4):
        s.rich(BX + 70 + b * bw + bw / 2, BY + 24, f'bank {8 + b}', 13, 'middle', GREY, 600)
    occ = {}
    for k, (r, row, part) in enumerate(WB):
        occ[(8 + row % 4, row // 4)] = (int(part[1]), row)
    for d in (1, 2):
        s.rich(BX + 62, BY + 44 + (d - 1) * bh + bh / 2, f'深 {d}', 13, 'end', GREY, 600)
        for b in range(4):
            key = (8 + b, d)
            if key in occ:
                idx, row = occ[key]
                s.cell(BX + 70 + b * bw, BY + 44 + (d - 1) * bh, bw - 4, bh - 4, f'字 {row}·记{idx}', cols[idx], 12)
            else:
                s.rect(BX + 70 + b * bw, BY + 44 + (d - 1) * bh, bw - 4, bh - 4, fill=C_OFF, sw=0.6, stroke=GREY)
    s.note(BX, BY + 44 + 2 * bh + 16, '一个存储字 = 一个 bank 的一个存储单元（32 B 宽）', 13)
    s.note(BX, BY + 44 + 2 * bh + 36, '为什么取 32 B：矩阵计算的数据单位本来就是 32 B——', 13)
    s.note(BX, BY + 44 + 2 * bh + 56, '一个 MX 组 32 个 8 bit 码、16 个 BF16、32 个 E8M0 尺度、', 13)
    s.note(BX, BY + 44 + 2 * bh + 76, '一个列字的两倍；记录补到 32 B 就是补到一个 bank 的存储字', 13)
    # ---------- 底部：口比 32 B 宽时 en 按 32 B 分位 ----------
    Y2 = Y1 + 5 * RH + 90
    s.rich(30, Y2, '口比 32 B 宽时 = 多条道：每道一个 bank、各自独立的 en / wea / addr / din；128 B 的口就是 4 道（A 类集合口 4 bank 时）', 16)
    Y3 = Y2 + 28
    rows3 = ['128 B 口 = 4 道', 'en[3:0]', 'addr（每道一个）', 'din / dout']
    X3, CW3 = 220, 300
    for i, nm in enumerate(rows3):
        s.rich(X3 - 12, Y3 + i * RH + RH / 2, nm, 14, 'end')
    ex = [('拍 u：4 道都写', '1111', '字 12 · 13 · 14 · 15', '4 个存储字，可属不同对象'),
          ('拍 u+1：只有道 0、2 写', '0101', '字 16 · — · 18 · —', '道 1 / 3 这一拍没有写者选中'),
          ('拍 u+2：4 道都读', '1111', '字 12 · 13 · 14 · 15', '下一拍 dout 4 × 32 B，vld[3:0] = 1111')]
    for k, (t, en, addr, d) in enumerate(ex):
        x = X3 + k * CW3
        s.cell(x, Y3, CW3, RH, t, C_OFF, 13)
        s.cell(x, Y3 + RH, CW3, RH, en, C_KEEP, 13)
        s.cell(x, Y3 + 2 * RH, CW3, RH, addr, C_SIDE, 13)
        s.cell(x, Y3 + 3 * RH, CW3, RH, d, 'white', 12)
    s.note(30, Y3 + 4 * RH + 20, '权重 lane 读口 256 B 就是 8 道：各读 W 类一个 bank，各道 addr 独立；32 B 的口 = 1 道；写集合口的道由集合器按优先级分给各写者', 14)
    s.red(30, Y3 + 4 * RH + 50, '本图只是核内：核间链路每拍的 addr 不由 CCU 累加，由 MAE 的 DMA 搬运引擎逐拍给出（§2.4.2）；接收桥按 addr 写 L1、不经 CCU', 14)
    s.save('FIG-TP-ADDR-ACCUM.svg', DATE)


# =====================================================================
# 小例 2：同一个 A 类地址在两堆、四核的落位
# =====================================================================
A_BANKS = [8, 9, 10, 11]
ROWN = 300
BANK_, DEPTH_ = A_BANKS[ROWN % 4], ROWN // 4
assert (BANK_, DEPTH_) == (8, 75)


def fig_addr_map():
    s = Svg(1500, 560)
    s.rich(30, 30, 'FIG-TP-ADDR-MAP  同一个地址 [堆 h][A][字 300] 在两堆、四核的落位', 20)
    s.note(30, 62, 'A 类 = bank 8–11 线性映射：字 j → bank 8 + (j mod 4)，深度 ⌊j / 4⌋；字 300 → bank 8、深度 75。堆选只换堆，不换 bank 与深度；四核物理同构', 15)
    X0, Y0 = 60, 110
    for ci in range(4):
        cx = X0 + ci * 360
        s.panel(cx, Y0, 330, 360, f'核 {ci}', 17)
        for h in range(2):
            hy = Y0 + 44 + h * 140
            s.rich(cx + 14, hy + 10, f'堆 {h}', 15, 'start', GREY)
            for k, b in enumerate(A_BANKS):
                bx = cx + 14 + k * 78
                s.rect(bx, hy + 24, 70, 96, fill=C_OFF, sw=1, stroke=GREY)
                s.rich(bx + 35, hy + 36, f'bank {b}', 12, 'middle', GREY)
                for d in range(3):
                    dy = hy + 50 + d * 22
                    dep = 74 + d
                    fill = C_KEEP if (b == BANK_ and dep == DEPTH_) else 'white'
                    s.cell(bx + 6, dy, 58, 20, f'深 {dep}', fill, 11)
        s.red(cx + 14, Y0 + 318, f'[0][A][300] → 堆 0 bank {BANK_} 深 {DEPTH_}', 12)
        s.red(cx + 14, Y0 + 342, f'[1][A][300] → 堆 1 bank {BANK_} 深 {DEPTH_}', 12)
    s.note(30, 520, '多播同一个 addr 到核 0 与核 2：两核都落到各自堆 1 的 bank 8 深度 75；写哪一堆由段选的堆选决定，L1 没有角色状态', 15)
    s.save('FIG-TP-ADDR-MAP.svg', DATE)


# =====================================================================
# 小例 3：核内时序
# =====================================================================
OPS = [('W', 'a'), ('R', 'a'), ('R', 'b'), ('R', 'c'), ('W', 'd'), ('R', 'd')]
RET = {t + 1: op[1] for t, op in enumerate(OPS) if op[0] == 'R'}
assert RET == {2: 'a', 3: 'b', 4: 'c', 6: 'd'}


def fig_timing():
    s = Svg(1500, 470)
    s.rich(30, 30, 'FIG-TP-INCORE-TIMING  写当拍、读固定 1 拍、读写交错', 20)
    s.note(30, 62, '每拍一个请求（en = 1）；写在当拍写入；读在下一拍返回 dout 且 vld = 1；拍 1 读字 a 读到拍 0 刚写的新值', 15)
    X0, Y0, CW, RH = 170, 110, 170, 40
    sig = ['拍', 'en', 'wea', 'addr', 'din', 'dout', 'vld']
    for i, nm in enumerate(sig):
        s.rich(X0 - 12, Y0 + i * RH + RH / 2, nm, 15, 'end')
    for t in range(7):
        x = X0 + t * CW
        s.cell(x, Y0, CW, RH, f'{t}', C_OFF, 14)
        op = OPS[t] if t < len(OPS) else None
        s.cell(x, Y0 + RH, CW, RH, '1' if op else '0', C_KEEP if op else 'white', 14)
        s.cell(x, Y0 + 2 * RH, CW, RH, ('1' if op[0] == 'W' else '0') if op else '—', (C_W if op and op[0] == 'W' else 'white'), 14)
        s.cell(x, Y0 + 3 * RH, CW, RH, f'字 {op[1]}' if op else '—', 'white', 14)
        s.cell(x, Y0 + 4 * RH, CW, RH, f'{op[1]}′' if op and op[0] == 'W' else '—', C_W if op and op[0] == 'W' else 'white', 14)
        r = RET.get(t)
        s.cell(x, Y0 + 5 * RH, CW, RH, (f'{r}′' if r in ('a', 'd') else r) if r else '—', C_KEEP if r else 'white', 14)
        s.cell(x, Y0 + 6 * RH, CW, RH, '1' if r else '0', C_KEEP if r else 'white', 14)
    s.red(30, 420, '拍 0 写 a 当拍生效，拍 1 读 a → 拍 2 返回新值 a′；拍 2、3 连续读 b、c → 拍 3、4 各返回一个存储字；没有 ready、busy，返回顺序 = 发出顺序', 15)
    s.save('FIG-TP-INCORE-TIMING.svg', DATE)


# =====================================================================
# 小例 4：逐拍 addr 与多播
# =====================================================================
UNIT_ROWS, UBASE = 6, 40
BEATS = [(k, UBASE + k, k == UNIT_ROWS - 1) for k in range(UNIT_ROWS)]
assert BEATS[-1] == (5, 45, True) and sum(1 for b in BEATS if b[2]) == 1
# 多播在分叉点按已取位分叉、各目的核独立取走（V18-TP-53）：模型见 mcast_fork_sim.py
from mcast_fork_sim import simulate  # noqa: E402
NT = 9
SB_CAP = 4                                   # 每核分支容量 = 分支 skid + LDP 入口 FIFO（示意）
READY = {0: [1] * NT, 2: [0 if t in (2, 3) else 1 for t in range(NT)]}   # 各核写进 L1 一侧的 ready
SB = simulate(UNIT_ROWS, READY, SB_CAP, NT)
assert SB['stall'] == 0                                            # 分叉点从不停收上游
assert SB['write'][0] == {t: t - 1 for t in range(1, 7)}           # 核 0 拍 1–6 写进 k = 0–5，不等核 2
assert sorted(SB['write'][2]) == [1, 4, 5, 6, 7, 8]                # 核 2 晚两拍写完
assert max(SB['occ'][2].values()) == 3 <= SB_CAP


def fig_stream_beat():
    s = Svg(1500, 790)
    s.rich(30, 30, 'FIG-TP-STREAM-BEAT  一个 6 拍单位的逐拍 addr，多播到核 0 与核 2、各自取走（链路上无末拍标记）', 20)
    s.note(30, 62, 'H2C 道 0 从 L2 读出 6 个存储字，经本道分叉点送往核 0、核 2；MAE 搬运引擎逐拍给出目的地址 [1][A][字 40…45]；链路上不标末拍，MAE 搬运引擎自己数到 6；核 1、3 的线上 en = 0', 15)
    X0, Y0, CW, RH = 150, 110, 170, 40
    s.rich(30, Y0 - 12, '单位的 6 拍（单位内序号 k）', 15)
    names = ['k', 'addr', 'din', '搬运引擎内计数']
    Y0 += 8
    for i, nm in enumerate(names):
        s.rich(X0 - 12, Y0 + i * RH + RH / 2, nm, 15, 'end')
    for k, row, last in BEATS:
        x = X0 + k * CW
        s.cell(x, Y0, CW, RH, f'{k}', C_OFF, 14)
        s.cell(x, Y0 + RH, CW, RH, f'[1][A][字 {row}]', C_SIDE, 13)
        s.cell(x, Y0 + 2 * RH, CW, RH, f'字 {row} 的 32 B', 'white', 13)
        s.cell(x, Y0 + 3 * RH, CW, RH, f'{k + 1} / {UNIT_ROWS}（不上链路）', C_LEFT if last else 'white', 12)
    # ---------- 各核按自己的 ready 取走 ----------
    Yt = Y0 + 4 * RH + 44
    s.rich(30, Yt - 14, f'分叉点按已取位分叉：两核都取走才收下一拍；核 2 停的两拍由核 2 分支（skid + LDP 入口 FIFO，示意容量 {SB_CAP}）接住', 15)
    CWt = 140
    trows = ['时钟拍', '分叉点送出 k', '核 0 写进 k', '核 2 写进侧 ready', '核 2 写进 k', '核 2 分支占用']
    for i, nm in enumerate(trows):
        s.rich(X0 - 12, Yt + i * RH + RH / 2, nm, 14, 'end')
    for t in range(NT):
        x = X0 + t * CWt
        s.cell(x, Yt, CWt, RH, f'{t}', C_OFF, 14)
        kp = SB['push'][0].get(t, SB['push'][2].get(t))
        s.cell(x, Yt + RH, CWt, RH, '—' if kp is None else f'{kp}', C_ACC if kp is not None else 'white', 14)
        k0 = SB['write'][0].get(t)
        s.cell(x, Yt + 2 * RH, CWt, RH, '—' if k0 is None else f'{k0}', C_W if k0 is not None else 'white', 14)
        s.cell(x, Yt + 3 * RH, CWt, RH, f'{READY[2][t]}', C_KEEP if READY[2][t] else C_LEFT, 14)
        k2 = SB['write'][2].get(t)
        s.cell(x, Yt + 4 * RH, CWt, RH, '—' if k2 is None else f'{k2}', C_W if k2 is not None else 'white', 14)
        oc = SB['occ'][2][t]
        s.cell(x, Yt + 5 * RH, CWt, RH, f'{oc}', C_LEFT if oc >= 2 else 'white', 14)
    y = Yt + 6 * RH + 24
    for ci in range(4):
        cx = 150 + ci * 330
        on = ci in (0, 2)
        s.rect(cx, y, 300, 110, fill=C_KEEP if on else C_OFF, sw=1.4)
        s.rich(cx + 150, y + 22, f'核 {ci}  H2C 道 0  en = {1 if on else 0}', 15, 'middle', INK, 700)
        if on:
            s.note(cx + 14, y + 52, '堆 1 · A 类 · 字 40–45', 14)
            s.note(cx + 14, y + 78, '→ bank 8,9,10,11,8,9 · 深 10,10,10,10,11,11', 13)
        else:
            s.note(cx + 14, y + 60, '不在目的掩码里，线上无成交', 14)
    for ci in (0, 2):
        rows = [(A_BANKS[r % 4], r // 4) for r in range(UBASE, UBASE + UNIT_ROWS)]
        assert rows == [(8, 10), (9, 10), (10, 10), (11, 10), (8, 11), (9, 11)]
    s.red(30, y + 140, '核 2 停两拍只让它自己晚两拍写完，分叉点不停、核 0 不等；两核收到同一个 addr、落同一位置；到核的链路上不带核掩码', 15)
    s.save('FIG-TP-STREAM-BEAT.svg', DATE)


# =====================================================================
# 小例 5：变长对象紧挨写 + 长度表 → CCU 发送 → 握手数满后发出报告 → MAE 按表读、搬完后转发应写量（V18-TP-40 / 47 / 58）
# =====================================================================
WIN_BASE, LR_CAP = 6400, 640             # 窗口起点字节、token 长度上限（字节，离线给出，只用于容量）
RECS_LEN = [520, 403, 389]               # 三条记录字节数（运行期压缩后）
N_REC = len(RECS_LEN)
LT_ADDR = WIN_BASE + LR_CAP * N_REC      # 长度表地址（编译链另给，紧跟窗口之后只是本例）
REC_START = [sum(RECS_LEN[:i]) for i in range(N_REC)]   # 各记录相对起点 = 前几项之和
DATA_BYTES = sum(RECS_LEN)
DATA_ROWS = -(-DATA_BYTES // ROW)        # 数据占的存储字
LT_ROWS = -(-(N_REC * 3) // ROW)         # 长度表占的存储字（每项 24 bit = 16 bit 长度 + 8 bit tokmax，11-08 V18-TP-60）
ITEMS_SENT = DATA_ROWS + LT_ROWS         # C2H 发出的项数 = H2C 搬运的项数 = 长度转发的应写量
assert REC_START == [0, 520, 923] and DATA_BYTES == 1312 and DATA_ROWS == 41 and LT_ROWS == 1 and ITEMS_SENT == 42
assert max(RECS_LEN) <= LR_CAP and DATA_BYTES <= LR_CAP * N_REC and LT_ADDR == 8320   # 不超上限、不超窗口


def fig_length_report():
    s = Svg(1500, 620)
    s.rich(30, 30, 'FIG-TP-LENGTH-REPORT  变长对象：紧挨写 + 长度表 → CCU 发送 → 握手数满后发出报告 → MAE 按表读、搬完后转发应写量（核 0 → L2 → 核 2）', 20)
    s.note(30, 62, f'窗口 [字节 {WIN_BASE}, {LT_ADDR}) 容量 = 上限 {LR_CAP} B × {N_REC}（只用于容量）；3 条记录 {RECS_LEN} B 紧挨写，共 {DATA_ROWS} 个存储字；长度表 {N_REC} × 24 bit（16 bit 长度 + 8 bit tokmax）在字节 {LT_ADDR}', 15)
    lanes = ['编译链 / 指令', '核 0 QNT + CCU', '核 0 CCU（C2H）', 'MAE', 'MAE（H2C）', '核 2 CCU']
    X0, Y0, LW, RH = 40, 110, 1420, 62
    steps = [
        (0, f'位点指令：窗口 [0][A][字节 {WIN_BASE}, {LT_ADDR})、长度表地址 [0][A][字节 {LT_ADDR}]；发送指令：L2 目的基址与长度表基址（象限由链路固定）'),
        (1, f'QNT 写 3 条记录，CCU 按长度推字节地址：起点 {REC_START}，共 {DATA_BYTES} B = {DATA_ROWS} 字；写完后 CCU 把 {RECS_LEN} 写成 {LT_ROWS} 字的长度表'),
        (2, f'CCU 读 L1、经 C2H 发 {DATA_ROWS} + {LT_ROWS} = {ITEMS_SENT} 拍，每拍 addr 由 CCU 给出；L2 每写进一项回一个写入握手，数满 {ITEMS_SENT} 个 = 已写进 L2'),
        (2, '握手数满 → 命令网发 发出报告（只带目的起始地址 = L2 窗口基址）→ MAE；不带长度、项数、记录数'),
        (3, f'按目的起始地址找到源起始地址相同的那条 L2 → 核 2 指令，放行；引擎先读长度表：总长 {DATA_BYTES} B = {DATA_ROWS} 字'),
        (4, f'先把长度表（{LT_ROWS} 字）搬到核 2 的编译链地址，再搬 {DATA_ROWS} 字；搬完后经 hub 控制道发长度转发：应写量 = 实际发出的 {ITEMS_SENT} 项'),
        (5, f'写计数 ≥ {ITEMS_SENT} 且已收到应写量 → 可消费；CCU 读长度表得各记录起点 {REC_START}；引擎数满 {ITEMS_SENT} 个写入握手 = 执行完、通知 LIC'),
    ]
    fills = [C_SIDE, C_KEEP, C_KEEP, C_KEEP, C_ACC, C_ACC, C_LEFT]
    for i, (lane, text) in enumerate(steps):
        y = Y0 + i * RH
        s.cell(X0, y, 190, RH - 8, lanes[lane], fills[i], 14)
        s.rect(X0 + 200, y, LW - 200, RH - 8, fill='white', sw=1, stroke=GREY)
        s.note(X0 + 212, y + (RH - 8) / 2, f'{i + 1}. {text}', 14)
        if i:
            s.line([(X0 + 95, y - 8), (X0 + 95, y)], INK, 1.6)
    s.red(30, 562, '紧挨写、长度表单独存；握手数满再报；报告按地址对应指令；MAE 按表读、搬完再给应写量', 15)
    s.save('FIG-TP-LENGTH-REPORT.svg', DATE)


# =====================================================================
# 小例 6：命令网消息进两槽 SRAM / RF
# =====================================================================
SEG_WORDS = 3                      # 段头 + 2 成员？本例：首字 + 3 个成员字
BEATS_PER_WORD = 1024 // 64
assert BEATS_PER_WORD == 16
SEG_BEATS = 1 + SEG_WORDS * BEATS_PER_WORD
assert SEG_BEATS == 49


def fig_ctrl_msg():
    s = Svg(1500, 560)
    s.rich(30, 30, 'FIG-TP-CTRL-MSG  一段 Fusion-CCU 进段 SRAM、成员逐条进"下一条"寄存器、一条可选的执行完成进 RF 队列', 20)
    s.note(30, 62, f'命令网 64 bit/拍；1,024 bit 命令字 = {BEATS_PER_WORD} 拍；本段 = 首字 1 拍 + {SEG_WORDS} 个成员字 × {BEATS_PER_WORD} 拍 = {SEG_BEATS} 拍；首字含长度，接收方按长度收完，无末字标记', 15)
    # 链路 1：LIC → CCU
    X0, Y0 = 60, 110
    s.panel(X0, Y0, 900, 200, 'LIC → 核 0 CCU（Fusion-CCU 段，一次整段）', 16)
    segs = [('首字', 1, C_SIDE), ('成员 0（16 拍）', 16, C_W), ('成员 1（16 拍）', 16, C_W), ('成员 2（16 拍）', 16, C_LEFT)]
    x = X0 + 20
    for nm, n, c in segs:
        w = 44 + n * 13
        s.cell(x, Y0 + 44, w, 40, nm, c, 13)
        x += w + 6
    s.note(X0 + 20, Y0 + 110, '→ 写进段 SRAM；ready = 段 SRAM 有空位；容量 ≤ 16 字【设计者定】', 14)
    s.note(X0 + 20, Y0 + 140, '段计数器按操作 15 的块数循环：每块把成员 0、1、2 依次搬进"下一条"寄存器，LIC 不重发', 14)
    s.note(X0 + 20, Y0 + 170, f'普通指令不经段 SRAM：LIC 直接写"下一条"寄存器（ready = 它为空）', 14)
    # CCU 端点图
    s.panel(X0 + 940, Y0, 460, 200, 'CCU 指令端点', 16)
    s.cell(X0 + 960, Y0 + 44, 200, 40, '当前指令：成员 1（块 3）', C_KEEP, 13)
    s.cell(X0 + 1180, Y0 + 44, 200, 40, '下一条：成员 2（块 3）', C_ACC, 13)
    s.cell(X0 + 960, Y0 + 100, 420, 40, 'Fusion-CCU 段 SRAM：首字 + 成员 0 / 1 / 2，块计数 3 / 8', C_W, 13)
    s.cell(X0 + 960, Y0 + 150, 420, 34, 'RF 队列：GO、长度转发、CRU 标量', C_SIDE, 13)
    # 链路 2：远离 MAE 的搬运引擎 → MAE 执行完成（可选，V18-NAME-04）
    Y1 = Y0 + 230
    s.panel(X0, Y1, 900, 120, '远离 MAE 的 DMA 通道 → MAE（可选短消息）', 16)
    s.cell(X0 + 20, Y1 + 44, 260, 40, '执行完成：首字（引擎号，长度 = 1 字）', C_LEFT, 13)
    s.note(X0 + 300, Y1 + 64, '1 拍 → MAE 的 RF 队列；搬运引擎数满命令规定的拍数才发【设计者定】', 14)
    s.panel(X0 + 940, Y1, 460, 120, 'MAE 端点', 16)
    s.cell(X0 + 960, Y1 + 44, 420, 40, 'RF 队列：执行完成 / 发出报告', C_SIDE, 13)
    s.red(30, 500, '两种端点都不经 L1 / L2 SRAM；命令 SRAM 无段选、不在数据网上；每条链路单向点到点，无 addr', 15)
    s.save('FIG-TP-CTRL-MSG.svg', DATE)


# =====================================================================
# 小例 7：③ 档对象：记录紧挨、长度表单独存（11-07 V18-TP-58）
# =====================================================================
OBJ_BASE, LT_BYTE = 64, 256                                  # 对象起点（存储字边界）、长度表地址（编译链另给）
RLEN = [22, 30, 18, 10]
RSTART = [OBJ_BASE + sum(RLEN[:i]) for i in range(len(RLEN))]   # 起点 = 对象起点 + 前几项之和
OBJ_END = OBJ_BASE + sum(RLEN)
W0, W1 = OBJ_BASE // ROW, (OBJ_END - 1) // ROW
NW = W1 - W0 + 1
TAIL_USED = OBJ_END - W1 * ROW
RD = 2                                                       # 例：读记录 2
RD_WORDS = (RSTART[RD] // ROW, (RSTART[RD] + RLEN[RD] - 1) // ROW)
RD_SHIFT = RSTART[RD] % ROW
assert RSTART == [64, 86, 116, 134] and OBJ_END == 144 and (W0, W1, NW, TAIL_USED) == (2, 4, 3, 16)
assert RD_WORDS == (3, 4) and RD_SHIFT == 20
assert OBJ_BASE % ROW == 0 and LT_BYTE % ROW == 0 and len(RLEN) * 3 == 12     # 表项 24 bit（V18-TP-60）


def fig_object_align():
    s = Svg(1500, 600)
    s.rich(30, 30, 'FIG-TP-OBJECT-ALIGN  ③ 档对象：4 条记录紧挨存放，长度表单独存（对象起点在存储字边界）', 20)
    s.note(30, 62, f'记录 {RLEN} B 从字节 {OBJ_BASE} 起紧挨，起点 {RSTART}，占存储字 {W0}–{W1}（末字只用 {TAIL_USED} B）；长度表 {RLEN} × 24 bit = 12 B 在字节 {LT_BYTE}', 15)
    X0, Y0, CW, RH = 150, 110, 1100 / ROW, 42
    cols = ['#fde3c4', '#d6e6f7', '#dcefd2', '#f3d9ef']

    def owner(byte):
        for i, (a, n) in enumerate(zip(RSTART, RLEN)):
            if a <= byte < a + n:
                return i
        return None

    for k in range(NW):
        w = W0 + k
        y = Y0 + k * RH
        s.rich(X0 - 12, y + RH / 2, f'字 {w}', 15, 'end')
        for b in range(ROW):
            i = owner(w * ROW + b)
            if i is None:
                s.rect(X0 + b * CW, y, CW, RH, fill='white', sw=0.6, stroke=GREY, dash='3,2')
            else:
                s.rect(X0 + b * CW, y, CW, RH, fill=cols[i], sw=0.6, stroke=GREY)
        for i, a in enumerate(RSTART):
            if a // ROW == w:
                s.rich(X0 + (a % ROW) * CW + 3, y + RH / 2, f'记录 {i}（{RLEN[i]} B）', 12, 'start', INK, 700)
        if w == W1:
            s.rich(X0 + TAIL_USED * CW + 4, y + RH / 2, f'空 {ROW - TAIL_USED} B（be 不选）', 12, 'start', RED, 700)
    y = Y0 + NW * RH + 30
    s.rich(X0 - 12, y + RH / 2, f'字 {LT_BYTE // ROW}', 15, 'end')
    for b in range(ROW):
        s.rect(X0 + b * CW, y, CW, RH, fill=C_SIDE if b < 8 else 'white', sw=0.6, stroke=GREY, dash=None if b < 8 else '3,2')
    s.rich(X0 + 3, y + RH / 2, f'长度表 {RLEN}（4 × 24 bit = 12 B：16 bit 长度 + 8 bit tokmax，由 CCU 写、编译链另给地址）', 12, 'start', INK, 700)
    y += RH + 44
    s.rich(30, y, '记录', 15); s.rich(150, y, '长度 B', 15); s.rich(280, y, '起点字节 = 对象起点 + 前几项之和', 15); s.rich(640, y, '覆盖字', 15); s.rich(780, y, '读法', 15)
    for i, (n, a) in enumerate(zip(RLEN, RSTART)):
        y += 26
        wa, wz = a // ROW, (a + n - 1) // ROW
        s.note(30, y, f'记录 {i}'); s.note(150, y, f'{n}'); s.note(280, y, f'{a}'); s.note(640, y, f'{wa}' if wa == wz else f'{wa}–{wz}')
        s.note(780, y, f'从字 {wa} 读到字 {wz}，读口出口按 {a % ROW} 移位')
    s.red(30, 565, f'写：攒满 32 B 才写一字、跨记录连着攒，末字带 be；读记录 {RD}：字 {RD_WORDS[0]}、{RD_WORDS[1]} 两次 1 拍读，出口按 {RD_SHIFT} 移位；没有补 0，没有头', 15)
    s.save('FIG-TP-OBJECT-ALIGN.svg', DATE)


# =====================================================================
# 小例 8：② 档 K 平面末 tile 计数（原 FIG-TP-SLOT-COUNT，11-07 改名 FIXED-ITEM）
# =====================================================================
NKEY, G = 52, 32
NGRP = -(-NKEY // G)
LASTV = NKEY - (NGRP - 1) * G
assert NGRP == 2 and LASTV == 20


def fig_fixed_item():
    s = Svg(1500, 420)
    s.rich(30, 30, 'FIG-TP-FIXED-ITEM  ② 档定长项 + 有效计数：K 平面 52 个 key，末存储 tile 20 / 32 有效，个数由指令给', 20)
    s.note(30, 62, f'一个 key 一项，存储 tile 取 32 项（示例，实际 N_st 可配）；有效个数 {NKEY} 由指令给出，没有头；末 tile 第 21–32 项填 0；decode 追加 key 只填下一项，已有 key 的量化不变', 15)
    X0, Y0, CW, RH = 150, 150, 1100 / G, 60
    for g in range(NGRP):
        y = Y0 + g * (RH + 30)
        s.rich(X0 - 12, y + RH / 2, f'tile {g}', 15, 'end')
        for k in range(G):
            idx = g * G + k
            valid = idx < NKEY
            s.cell(X0 + k * CW, y, CW, RH, f'{idx}' if valid else '0', C_KEEP if valid else 'white', 11, INK if valid else GREY, 600, 0.6, None if valid else '3,2', GREY)
    s.cell(X0, Y0 - 50, 360, 34, f'指令给出：K hi · 有效个数 {NKEY} · tile {NGRP} 个', C_SIDE, 13)
    s.red(30, 370, f'读方只用有效个数内的项（0–{NKEY - 1}）；量化组在 key 内部（沿 head_dim 每 32 维），与分 tile 无关，没有沿 key 方向的重量化', 15)
    s.save('FIG-TP-FIXED-ITEM.svg', DATE)


# =====================================================================
# 小例 9：权重驻留按窗口成对象，MAE 按长度表聚集（11-07 V18-TP-58 / MAE-33）
# =====================================================================
WG_T, WG_NW = 4, 3
WG_LEN = [[50, 38, 61, 44], [47, 52, 40, 58], [55, 36, 49, 60]]   # [窗口][token] 片长（B），由保留数决定
WG_BASE = [4096, 4608, 5120]                                        # 三个窗口对象的起点（同一象限内，编译链给）
WG_START = [[sum(row[:t]) for t in range(WG_T)] for row in WG_LEN]  # 各片相对起点 = 表中前几项之和
WG_TOK = 1
WG_PIECES = [(WG_BASE[w] + WG_START[w][WG_TOK], WG_LEN[w][WG_TOK]) for w in range(WG_NW)]
WG_TOTAL = sum(n for _, n in WG_PIECES)
assert WG_START[0] == [0, 50, 88, 149] and WG_PIECES == [(4146, 38), (4655, 52), (5175, 36)] and WG_TOTAL == 126
assert all(sum(row) <= 512 for row in WG_LEN)                      # 每个窗口对象不超本例给它的 512 B


def fig_window_gather():
    s = Svg(1500, 640)
    s.rich(30, 30, f'FIG-TP-WINDOW-GATHER  权重驻留：{WG_T} 个 token × {WG_NW} 个窗口的产出次序，每窗口一个对象 + 长度表，MAE 按表聚集 token {WG_TOK}', 20)
    s.note(30, 62, '产出次序 = 窗口 0 的 token 0…3，再窗口 1…；每个窗口的 4 片紧挨成一个对象（QNT 一个攒字寄存器），长度表 4 × 24 bit 另存；MAE 先读 3 张表，再逐片取', 15)
    X0, Y0 = 60, 110
    s.rich(X0, Y0, '产出次序 →', 15)
    cols = ['#fde3c4', '#d6e6f7', '#dcefd2', '#f3d9ef']
    x = X0 + 130
    for w in range(WG_NW):
        for t in range(WG_T):
            s.cell(x, Y0 - 16, 94, 32, f'窗{w}·tok{t}', cols[t], 12)
            x += 100
    Y1 = Y0 + 50
    PX = 2.4
    for w in range(WG_NW):
        y = Y1 + w * 96
        s.rich(X0, y + 24, f'窗口 {w} 对象', 15)
        s.note(X0, y + 46, f'起点 {WG_BASE[w]}', 12)
        for t in range(WG_T):
            a, n = WG_START[w][t], WG_LEN[w][t]
            s.rect(X0 + 130 + a * PX, y, n * PX, 48, fill=cols[t], sw=1, stroke=NAVY)
            s.rich(X0 + 130 + (a + n / 2) * PX, y + 24, f'tok{t} {n} B', 11, 'middle', INK, 700)
        s.note(X0 + 130, y + 66, f'长度表 {WG_LEN[w]}（另存）；各片相对起点 {WG_START[w]}', 12)
    y = Y1 + WG_NW * 96 + 10
    s.rich(X0, y + 24, f'聚集 token {WG_TOK} →', 15)
    xx = X0 + 130
    for w, (a, n) in enumerate(WG_PIECES):
        s.rect(xx, y, n * PX, 48, fill=cols[WG_TOK], sw=1, stroke=NAVY)
        s.rich(xx + n * PX / 2, y + 16, f'窗{w}', 11, 'middle', INK, 700)
        s.rich(xx + n * PX / 2, y + 34, f'源 {a} 取 {n} B', 10, 'middle', INK, 500)
        xx += n * PX
    s.note(xx + 12, y + 24, f'← 消费核 L1 里 token {WG_TOK} 的记录，共 {WG_TOTAL} B，片片紧挨', 13)
    s.note(X0 + 130, y + 70, f'源地址 = 对象起点 + 表中前 t 项之和（{[a for a, _ in WG_PIECES]}）；目的地址在引擎内顺序累加；消费核 CCU 对三张表求和得每 token 总长', 13)
    s.red(30, 600, 'token 驻留时产出本来就按 token 连续，一个对象一张表、不需要聚集；备选：消费方按窗口分段算、部分和停放 L1，MAE 只顺序搬（数据流篇定）', 15)
    s.save('FIG-TP-WINDOW-GATHER.svg', DATE)


# ---- 11-05 的 token 槽图（11-07 退役，代码保留不再调用） ----
T, NG = 4, 3
SEGLEN = [[14, 9, 11], [6, 15, 10], [12, 12, 7], [8, 5, 13]]
SLOT_ROWS = 4
ARRIVAL = [(g, t) for g in range(NG) for t in range(T)]
OFFS = {t: [] for t in range(T)}
acc = {t: 0 for t in range(T)}
for g, t in ARRIVAL:
    OFFS[t].append((g, acc[t]))
    acc[t] += SEGLEN[t][g]




# =====================================================================
# 小例 10：分级反压简图（用户 11-05 要求在 §4 给一张简图）
# =====================================================================
CHAIN = [('CCU', '发 en / addr', C_SIDE), ('L1 读口', '1 拍返回', C_OFF), ('MXU 供数', '缓冲 D₁', C_ACC),
         ('阵列', '流水 D_arr · AEB', C_ACC), ('VNU', '出口级子模块收 AEB\n入口缓冲 D₃', C_ACC), ('L1 写集合器', '写者 FIFO\n将满 → wr_stall', C_OFF)]
# 11-08（V18-NLU-06）：出口级并入 NLU，链上少一级；AEB 的 ready 由 VNU（出口级子模块）拉
STALLS = [(2, 0, 'stall_mxu[p]：供数缓冲将满 → CCU 停发该 pod 的 en'),
          (3, 2, 'stall：阵列不能再收 → 供数停发列'),
          (4, 3, 'AEB ready 拉低：VNU（出口级）来不及收 → AEB 堆满后 FBA 冻结'),
          (4, 0, 'stall_vnu[i]：VNU 读 L1 的入口将满 → CCU 停发该入口的 en')]
DEPTH, L_LAT = 8, 2
THRESH = DEPTH - L_LAT
assert THRESH == 6


# 11-08 重画（用户："它看起来像是 VNU Gating 住前面的所有模块，而我的需求是每一级的下一级消费者都可以和上一级去握手，
# 同时 C2H 在发数据的时候，有一个 FIFO 来全局 Gating"）：相邻级握手画成框上方的短箭头，只连相邻两框；
# 到 CCU 的 stall（因为该级数据的 en 是 CCU 发的）画在框下方的两条车道；集成输出端口的发送 FIFO 单独一行，stall_tx 从 CCU 左侧进入 = 唯一的全局门控
ADJ = [(3, 2, 'stall：供数停发列'),                       # 阵列 → 供数
       (4, 3, 'AEB ready 拉低：阵列停出条目'),             # VNU（出口级子模块）→ 阵列
       (5, 4, 'wr_stall：该写者停写')]                     # L1 写集合器 → VNU
TO_CCU = [(2, 'stall_mxu[p]：pod 供数缓冲将满 → CCU 停发该 pod 的 en'),
          (4, 'stall_vnu[i]：VNU 读 L1 的入口将满 → CCU 停发该入口的 en')]
assert {a for a, _, _ in ADJ} == {3, 4, 5} and all(a - b == 1 for a, b, _ in ADJ)     # 相邻级：只连相邻两框


def fig_stall_chain():
    s = Svg(1560, 740)
    s.rich(30, 30, 'FIG-TP-STALL-CHAIN  分级握手：相邻级两两握手（上方短箭头）；CCU 只收它发 en 的两级的 stall（下方车道）；stall_tx 是唯一的全局门控', 20)
    s.note(30, 62, '数据从左向右推送；红色箭头指向"谁该停"。每个消费者只对它的直接上游握手，不越级；链末端是 L1 写集合器里该写者的 FIFO，将满才拉 wr_stall；CCU 自身不拉 stall', 15)
    X0, Y0, BW, BH, GAP = 60, 170, 170, 80, 50
    xs = []
    for i, (nm, sub, c) in enumerate(CHAIN):
        x = X0 + i * (BW + GAP)
        xs.append(x)
        s.rect(x, Y0, BW, BH, fill=c, sw=1.6, rx=6)
        s.rich(x + BW / 2, Y0 + 26, nm, 16, 'middle')
        for k, ln in enumerate(sub.split('\n')):
            s.rich(x + BW / 2, Y0 + 50 + k * 18, ln, 13, 'middle', INK, 500)
        if i:
            s.line([(x - GAP, Y0 + BH / 2), (x, Y0 + BH / 2)], INK, 2.2)
    s.note(xs[1], Y0 - 58, '↑ 相邻级握手：消费者对直接上游（一级一根，不越级）', 13)
    # 相邻级：框上方的短箭头，从下游框顶回到上游框顶
    for src, dst, text in ADJ:
        xa, xb = xs[src] + 24, xs[dst] + BW - 24
        yy = Y0 - 26
        s.line([(xa, Y0), (xa, yy), (xb, yy), (xb, Y0 - 2)], RED, 2, 'ar', '6,4')
        s.red((xa + xb) / 2, yy - 8, text, 12, 'middle')
    s.note(xs[1] + 10, Y0 + BH + 20, '→ 数据 / 请求方向（CCU → L1 是 en / addr，其余是推送）', 13)
    # 到 CCU 的 stall：因为这两级的数据是 CCU 发 en 读来的，消费者给发 en 者一根 stall
    # 嵌套车道的布线规则（用户 11-08："右侧的来源在输入端也被放在右侧，会导致重叠"）：
    # 来源越远、车道越靠外（越低）的那根，在目的框上的进入点越靠外侧（这里 = 越靠左），竖线才不会穿过内层车道的横线
    cx = xs[0] + BW / 2
    for k, (src, text) in enumerate(TO_CCU):
        yy = Y0 + BH + 56 + k * 40
        xa = xs[src] + 36
        xb = cx + 24 - k * 48                     # k = 0（近、上层）进右侧，k = 1（远、下层）进左侧
        s.line([(xa, Y0 + BH), (xa, yy), (xb, yy), (xb, Y0 + BH + 2)], RED, 2, 'ar', '6,4')
        s.red(xb + 16, yy - 11, text, 12)
    assert all(xs[TO_CCU[k][0]] > xs[TO_CCU[k - 1][0]] for k in range(1, len(TO_CCU)))   # 车道越低、来源越远
    s.note(xs[0] + 20, Y0 + BH + 56 + 40 + 24, '↑ 到 CCU 的 stall：只有 CCU 发 en 的两级（供数、VNU 入口），不是越级门控', 13)
    # 集成输出端口（发送 FIFO）与 C2H：核间 ready 只到这里；FIFO 将满 → stall_tx 门控 CCU（唯一的全局门控）
    y3 = Y0 + BH + 170
    fx = xs[4]
    # 两个核内来源（V18-TP-59）：L1 发送侧读出（画在 L1 读口下方）、VNU 输出（经出口级透传的 MXU 输出也算在内）
    lx = xs[1]
    s.rect(lx, y3, BW, BH, fill=C_OFF, sw=1.6, rx=6)
    s.rich(lx + BW / 2, y3 + 26, 'L1 发送侧', 16, 'middle')
    s.rich(lx + BW / 2, y3 + 50, '读 L1（CCU 发 en）', 13, 'middle', INK, 500)
    s.rich(lx + BW / 2, y3 + 68, 'CCU 逐拍给 L2 addr', 13, 'middle', INK, 500)
    s.line([(lx + BW / 2, Y0 + BH), (lx + BW / 2, y3)], INK, 2.2)
    s.note(lx + BW / 2 + 8, Y0 + BH + 140, '读出 32 B', 12)
    s.line([(lx + BW, y3 + BH / 2), (fx, y3 + BH / 2)], INK, 2.2)
    s.note(lx + BW + 60, y3 + BH / 2 - 10, '来源 1：L1 发送侧读出', 12)
    s.rect(fx, y3, BW, BH, fill=C_SIDE, sw=1.6, rx=6)
    s.rich(fx + BW / 2, y3 + 26, '集成输出端口', 16, 'middle')
    s.rich(fx + BW / 2, y3 + 50, '两源由 CCU 选 · 发送 FIFO', 13, 'middle', INK, 500)
    s.rich(fx + BW / 2, y3 + 68, '深度 − L 将满', 13, 'middle', INK, 500)
    s.line([(fx + BW - 30, Y0 + BH), (fx + BW - 30, y3)], INK, 2.2)
    s.note(fx + BW - 22, Y0 + BH + 140, '来源 2：VNU 输出（写 L2 时）', 12)
    s.rect(xs[5], y3, BW, BH, fill=C_OFF, sw=1.6, rx=6)
    s.rich(xs[5] + BW / 2, y3 + 26, 'C2H → hub → L2', 16, 'middle')
    s.rich(xs[5] + BW / 2, y3 + 50, '核间 ready 只到', 13, 'middle', INK, 500)
    s.rich(xs[5] + BW / 2, y3 + 68, '左边的发送 FIFO', 13, 'middle', INK, 500)
    s.line([(fx + BW, y3 + BH / 2), (xs[5], y3 + BH / 2)], INK, 2.2)
    # stall_tx：从 FIFO 底部出发，沿最下方绕到 CCU 左侧进入——全局门控
    yt = y3 + BH + 30
    s.line([(fx + BW / 2, y3 + BH), (fx + BW / 2, yt), (28, yt), (28, Y0 + BH / 2), (xs[0] - 2, Y0 + BH / 2)], RED, 3.2, 'ar')
    s.red(cx + 40, yt - 10, 'stall_tx：发送 FIFO 将满 → 门控 CCU（停发全部 en、停算，等 C2H ready）= 唯一的全局门控', 14)
    y2 = yt + 46
    s.rich(30, y2, '将满阈值', 16)
    s.note(30, y2 + 28, f'例：某级缓冲深度 {DEPTH}，从它拉 stall 到上游真正停发要 {L_LAT} 拍（CCU 停发 1 拍 + L1 读返回 1 拍），所以在占用到 {THRESH} 时就拉，留 {L_LAT} 个空位接在途的拍；各级 L 由设计者登记', 14)
    s.note(30, y2 + 54, '规则：谁发 en，谁判断"有没有地方放"；发 en 的不是消费者本人时，消费者给发 en 者一根 stall；推送段上消费者只对直接上游握手；核间 ready 不进核，只在发送 FIFO 处变成 stall_tx', 14)
    s.save('FIG-TP-STALL-CHAIN.svg', DATE)


if __name__ == '__main__':
    fig_stall_chain()
    # 四张架构图（FIG-TP-ARCH-*）自 11-05 起由 _build/draw_tp_arch.py 产出（Opus Agent，任务书 TP_FIGURE_BRIEF_20261105.md）；
    # 本脚本里的 fig_links / fig_incore / fig_intercore / fig_ctrl 是被用户判定接线错误的旧版，保留代码不再调用。
    fig_addr_accum(); fig_addr_map(); fig_timing(); fig_stream_beat(); fig_length_report()
    fig_ctrl_msg(); fig_object_align(); fig_fixed_item(); fig_window_gather()
    print('10 numeric figures written')
