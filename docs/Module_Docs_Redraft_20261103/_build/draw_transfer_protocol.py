"""片上数据传输协议篇的数值 / 时序小例图。Owner: WangYizhao · 2026-11-05（11-05 夜按 V18-TP-26…34 改）
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_transfer_protocol.py
输出（figs/）：四张架构图（FIG-TP-ARCH-*）由 _build/draw_tp_arch.py 产出，不在本脚本。
  十张数值 / 时序小例（svgkit_num 规则，数值由脚本算出并断言）
    FIG-TP-ADDR-ACCUM      核内例：CCU 基址 + 字节累加 → [堆][类][字号]，记录级对齐，含环形回绕；bank 落位；多道口
    FIG-TP-ADDR-MAP        同一个 A 类地址在两堆、四核的落位
    FIG-TP-INCORE-TIMING   写当拍、读 1 拍、读写交错
    FIG-TP-STREAM-BEAT     6 拍单位的逐拍 addr（链路上无末拍标记），多播到两核、分叉点按已取位分叉（V18-TP-53）
    FIG-TP-LENGTH-REPORT   变长对象：按上限分槽 → CCU 发送 → 握手数满后发出报告 → 按槽读
    FIG-TP-CTRL-MSG        Fusion 段进段 SRAM、成员进"下一条"寄存器、可选的执行完成进队列
    FIG-TP-STALL-CHAIN     分级握手
    FIG-TP-OBJECT-ALIGN    ③ 档对象：对象头与 4 条记录各占整个存储字
    FIG-TP-SLOT-COUNT      ② 档 K 组末组 20 / 32 有效 + 计数
    FIG-TP-TOKEN-SLOT      权重驻留：4 token × 3 MX 组的段到达顺序与各 token 槽
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit_num import Svg, NAVY, INK, GREY, RED, C_OFF, C_KEEP, C_W, C_SIDE, C_ACC, C_LEFT  # noqa: E402

DATE = '2026-11-05'
ROW = 32

# ---------------- PPT 风格调色 ----------------
P = {
    'incore': ('#0f766e', '#ccfbf1'),   # 核内 SRAM 口总线：青
    'inter':  ('#1d4ed8', '#dbeafe'),   # 核间数据网：蓝
    'ctrl':   ('#c2410c', '#ffedd5'),   # 命令与标量网：橙
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
    s.note(30, 62, 'A 类 = bank 8–11 线性映射：字 j → bank 8 + (j mod 4)，深度 ⌊j / 4⌋；字 300 → bank 8、深度 75。堆位只换堆，不换 bank 与深度；四核物理同构', 15)
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
    s.note(30, 520, '多播同一个 addr 到核 0 与核 2：两核都落到各自堆 1 的 bank 8 深度 75；写哪一堆由地址的堆位决定，L1 没有角色状态', 15)
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
# 小例 5：变长对象按离线上限分槽 → CCU 发送 → 握手数满后发出报告 → 按槽读（V18-TP-40 / 47 / 49）
# =====================================================================
WIN_BASE_ROW, LR_SLOT_ROWS = 200, 20      # 窗口起点字号、每槽上限（存储字，离线给出）
RECS_LEN = [520, 403, 389]             # 三条记录字节数
N_REC = len(RECS_LEN)
REC_ROWS = [-(-b // ROW) for b in RECS_LEN]
ROWS_USED = sum(REC_ROWS)              # C2H 实际发出的项数（各槽只写记录本身）
WIN_ROWS = LR_SLOT_ROWS * N_REC           # 窗口 = 槽长 × 个数；读方按槽长整槽读
assert REC_ROWS == [17, 13, 13] and ROWS_USED == 43 and WIN_ROWS == 60
assert max(REC_ROWS) <= LR_SLOT_ROWS      # 每条不超槽（超窗口 = 致命错误）
WIN_END_ROW = WIN_BASE_ROW + WIN_ROWS
assert WIN_END_ROW == 260


def fig_length_report():
    s = Svg(1500, 620)
    s.rich(30, 30, 'FIG-TP-LENGTH-REPORT  变长对象：按上限分槽 → CCU 发送 → 握手数满后发出报告 → 按槽读（核 0 产出，经 L2 给核 2）', 20)
    s.note(30, 62, f'窗口 [字 {WIN_BASE_ROW}, 字 {WIN_END_ROW}) = {N_REC} 槽 × {LR_SLOT_ROWS} 个存储字（离线上限）；3 条记录 {RECS_LEN} B 各占 {REC_ROWS} 个存储字，写在各自槽的开头、槽尾空着', 15)
    lanes = ['编译链 / 指令', '核 0 QNT + CCU', '核 0 CCU（C2H）', 'MAE', 'MAE（H2C）', '核 2 CCU']
    X0, Y0, LW, RH = 40, 110, 1420, 62
    steps = [
        (0, f'位点指令：输出对象 {N_REC} 个槽、每槽 {LR_SLOT_ROWS} 个存储字，从 [0][A][字 {WIN_BASE_ROW}] 起；发送指令：目的 L2 窗口基址（象限 = 本核号）、目标存储 = L2'),
        (1, f'QNT 写 3 条记录，CCU 逐记录推地址：记录 i 写进第 i 槽开头，共 {ROWS_USED} 项（{" + ".join(map(str, REC_ROWS))}）'),
        (2, f'CCU 读 L1、经 C2H 发 {ROWS_USED} 拍，每拍 addr 与通路选择由 CCU 给出、不标末拍；L2 每写进一项回一个写入握手，CCU 数满 {ROWS_USED} 个 = 已写进 L2'),
        (2, '握手数满 → 命令与标量网发 发出报告（只带目的起始地址 = L2 窗口基址）→ MAE；不带对象标识、项数与记录数'),
        (3, '按目的起始地址找到源起始地址相同的那条 L2 → 核 2 指令，放行；该指令执行完时带它的标号通知 LIC'),
        (4, f'搬运引擎按槽长整槽读 {WIN_ROWS} 个存储字（{N_REC} 槽 × {LR_SLOT_ROWS}）、经 H2C 写进核 2 的 L1；应写量 {WIN_ROWS} 在位点指令里，不经长度转发'),
        (5, f'核 2 写入项数达到 {WIN_ROWS}、CCU 比对通过即可消费（核内）；引擎数满 {WIN_ROWS} 个写入握手 = 指令执行完（核间）；消费时按记录头个数忽略槽尾'),
    ]
    fills = [C_SIDE, C_KEEP, C_KEEP, C_KEEP, C_ACC, C_ACC, C_LEFT]
    for i, (lane, text) in enumerate(steps):
        y = Y0 + i * RH
        s.cell(X0, y, 190, RH - 8, lanes[lane], fills[i], 14)
        s.rect(X0 + 200, y, LW - 200, RH - 8, fill='white', sw=1, stroke=GREY)
        s.note(X0 + 212, y + (RH - 8) / 2, f'{i + 1}. {text}', 14)
        if i:
            s.line([(X0 + 95, y - 8), (X0 + 95, y)], INK, 1.6)
    s.red(30, 562, '按槽静态分配；握手数满再报；报告按地址对应指令；读方按槽长读', 15)
    s.save('FIG-TP-LENGTH-REPORT.svg', DATE)


# =====================================================================
# 小例 6：命令与标量网消息进两槽 SRAM / RF
# =====================================================================
SEG_WORDS = 3                      # 段头 + 2 成员？本例：首字 + 3 个成员字
BEATS_PER_WORD = 1024 // 64
assert BEATS_PER_WORD == 16
SEG_BEATS = 1 + SEG_WORDS * BEATS_PER_WORD
assert SEG_BEATS == 49


def fig_ctrl_msg():
    s = Svg(1500, 560)
    s.rich(30, 30, 'FIG-TP-CTRL-MSG  一段 Fusion-CCU 进段 SRAM、成员逐条进"下一条"寄存器、一条可选的执行完成进 RF 队列', 20)
    s.note(30, 62, f'命令与标量网 64 bit/拍；1,024 bit 命令字 = {BEATS_PER_WORD} 拍；本段 = 首字 1 拍 + {SEG_WORDS} 个成员字 × {BEATS_PER_WORD} 拍 = {SEG_BEATS} 拍；首字含长度，接收方按长度收完，无末字标记', 15)
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
    s.red(30, 500, '两种端点都不经 L1 / L2 SRAM；命令 SRAM 无类位、不在数据网上；每条链路单向点到点，无 addr', 15)
    s.save('FIG-TP-CTRL-MSG.svg', DATE)


# =====================================================================
# 小例 7：③ 档对象对齐
# =====================================================================
OHDR = 8
RLEN = [22, 30, 18, 10]
# 记录级对齐：对象头占整行；每条记录从整行起、占 ceil(n/32) 行、尾部补 0
ITEMS = [('对象头', OHDR)] + [(f'记录 {i}', n) for i, n in enumerate(RLEN)]
ROWS_OF = [-(-n // ROW) for _, n in ITEMS]
FIRST_ROW = [sum(ROWS_OF[:i]) for i in range(len(ITEMS))]
NR = sum(ROWS_OF)
PADS = [r * ROW - n for (_, n), r in zip(ITEMS, ROWS_OF)]
assert ROWS_OF == [1, 1, 1, 1, 1] and FIRST_ROW == [0, 1, 2, 3, 4] and NR == 5
assert PADS == [24, 10, 2, 14, 22] and sum(PADS) == NR * ROW - OHDR - sum(RLEN)


def fig_object_align():
    s = Svg(1500, 570)
    s.rich(30, 30, 'FIG-TP-OBJECT-ALIGN  ③ 档对象：对象头与 4 条记录各自补到整个存储字（记录级 32 B 对齐）', 20)
    s.note(30, 62, f'对象头 {OHDR} B + 记录 {RLEN} B；每项从存储字起、尾部补 0 到 32 B，共 {NR} 个存储字 = {NR * ROW} B，补 0 合计 {sum(PADS)} B；一个存储字只属于一项，没有跨字', 15)
    X0, Y0, CW, RH = 150, 110, 1100 / ROW, 42
    cols = [C_SIDE, '#fde3c4', '#d6e6f7', '#dcefd2', '#f3d9ef']
    for i, ((nm, n), r0, pad) in enumerate(zip(ITEMS, FIRST_ROW, PADS)):
        y = Y0 + r0 * RH
        s.rich(X0 - 12, y + RH / 2, f'字 {r0}', 15, 'end')
        for b in range(ROW):
            if b < n:
                s.rect(X0 + b * CW, y, CW, RH, fill=cols[i], sw=0.6, stroke=GREY)
            else:
                s.rect(X0 + b * CW, y, CW, RH, fill='white', sw=0.6, stroke=GREY, dash='3,2')
        s.rich(X0 + 4, y + RH / 2, f'{nm}（{n} B）', 13, 'start', INK, 700)
        s.rich(X0 + n * CW + 4, y + RH / 2, f'补 0 {pad} B', 12, 'start', RED, 700)
    y = Y0 + NR * RH + 44
    s.rich(30, y, '项', 15); s.rich(200, y, '长度 B', 15); s.rich(330, y, '占字', 15); s.rich(460, y, 'CCU 记下的首字号', 15); s.rich(720, y, '读法', 15)
    for (nm, n), r0, rows in zip(ITEMS, FIRST_ROW, ROWS_OF):
        y += 26
        s.note(30, y, nm); s.note(200, y, f'{n}'); s.note(330, y, f'{rows}'); s.note(460, y, f'{r0}')
        s.note(720, y, f'从字 {r0} 起连读 {rows} 个存储字，按头里的长度忽略补 0')
    s.red(30, 540, '写：生产方攒满 32 B 才写一个存储字，记录尾字写满 0；读：从首字起整字读；32 B = 一个 bank 的宽度，所以没有任何访问跨 bank', 15)
    s.save('FIG-TP-OBJECT-ALIGN.svg', DATE)


# =====================================================================
# 小例 8：② 档 K 组末组计数
# =====================================================================
NKEY, G = 52, 32
NGRP = -(-NKEY // G)
LASTV = NKEY - (NGRP - 1) * G
assert NGRP == 2 and LASTV == 20


def fig_slot_count():
    s = Svg(1500, 420)
    s.rich(30, 30, 'FIG-TP-SLOT-COUNT  ② 档固定槽 + 有效计数：K 平面 52 个 key，末存储 tile 20 / 32 有效', 20)
    s.note(30, 62, f'一个 key 一槽，存储 tile 取 32 槽（示例，实际 N_st 可配）；对象头计数 = {NKEY}；末 tile 槽 21–32 填 0；decode 追加 key 只填下一个槽，已有 key 的量化不变', 15)
    X0, Y0, CW, RH = 150, 150, 1100 / G, 60
    for g in range(NGRP):
        y = Y0 + g * (RH + 30)
        s.rich(X0 - 12, y + RH / 2, f'组 {g}', 15, 'end')
        for k in range(G):
            idx = g * G + k
            valid = idx < NKEY
            s.cell(X0 + k * CW, y, CW, RH, f'{idx}' if valid else '0', C_KEEP if valid else 'white', 11, INK if valid else GREY, 600, 0.6, None if valid else '3,2', GREY)
    s.cell(X0, Y0 - 50, 300, 34, f'对象头：类型 K hi · 计数 {NKEY} · 组数 {NGRP}', C_SIDE, 13)
    s.red(30, 370, f'读方只用计数内的槽（0–{NKEY - 1}）；量化组在 key 内部（沿 head_dim 每 32 维），与槽的分 tile 无关，没有沿 key 方向的重量化', 15)
    s.save('FIG-TP-SLOT-COUNT.svg', DATE)


# =====================================================================
# 小例 9：权重驻留 token 槽
# =====================================================================
T, NG = 4, 3
SEGLEN = [[14, 9, 11], [6, 15, 10], [12, 12, 7], [8, 5, 13]]      # [token][组] 段长（B），由 keep 数决定
SLOT_ROWS = 4                                                       # 每 token 槽 4 行（上限）
ARRIVAL = [(g, t) for g in range(NG) for t in range(T)]            # 权重驻留：组外层、token 内层
OFFS = {t: [] for t in range(T)}
acc = {t: 0 for t in range(T)}
for g, t in ARRIVAL:
    OFFS[t].append((g, acc[t]))
    acc[t] += SEGLEN[t][g]
assert [a for a in acc.values()] == [34, 31, 31, 26]
assert all(v <= SLOT_ROWS * ROW for v in acc.values())
assert OFFS[1] == [(0, 0), (1, 6), (2, 21)]


def fig_token_slot():
    s = Svg(1500, 600)
    s.rich(30, 30, 'FIG-TP-TOKEN-SLOT  权重驻留：段按 (组, token) 顺序到达，按 token 槽拼接', 20)
    s.note(30, 62, f'{T} 个 token × {NG} 个 MX 组；到达顺序 = 组 0 的 token 0…3，再组 1…；A 类里每 token 一个 {SLOT_ROWS} 字槽（上限）；CCU 每 token 一个写累加器', 15)
    # 到达序列
    X0, Y0 = 60, 110
    s.rich(X0, Y0, '到达顺序 →', 15)
    cols = ['#fde3c4', '#d6e6f7', '#dcefd2', '#f3d9ef']
    x = X0 + 130
    for i, (g, t) in enumerate(ARRIVAL):
        s.cell(x, Y0 - 16, 94, 32, f'组{g}·tok{t}', cols[t], 12)
        x += 100
    # 槽
    Y1 = Y0 + 50
    CW = 24
    for t in range(T):
        y = Y1 + t * 100
        s.rich(X0, y + 36, f'token {t} 槽', 15)
        for r in range(SLOT_ROWS):
            for b in range(ROW):
                s.rect(X0 + 130 + (r * ROW + b) * (CW / 3), y, CW / 3, 60, fill=C_OFF, sw=0.4, stroke=GREY)
        for g, o in OFFS[t]:
            n = SEGLEN[t][g]
            s.rect(X0 + 130 + o * (CW / 3), y, n * (CW / 3), 60, fill=cols[t], sw=1, stroke=NAVY)
            s.rich(X0 + 130 + (o + n / 2) * (CW / 3), y + 30, f'组 {g}', 11, 'middle', INK, 700)
        s.note(X0 + 130 + acc[t] * (CW / 3) + 8, y + 30, f'← {acc[t]} B 已写，余下留空', 12)
        for r in range(1, SLOT_ROWS):
            s.line([(X0 + 130 + r * ROW * (CW / 3), y), (X0 + 130 + r * ROW * (CW / 3), y + 60)], GREY, 1.2, None)
    s.note(X0 + 130, Y1 + T * 100 - 20, '每格 1 B，竖线 = 存储字边界（32 B）；槽内记录紧凑、槽尾留空；记录头含 token 序号', 13)
    s.red(30, 560, 'token 驻留时同样的段按 (token, 组) 顺序到达，记录首尾紧挨、一个累加器；记录格式相同，消费方不感知', 15)
    s.save('FIG-TP-TOKEN-SLOT.svg', DATE)


# =====================================================================
# 小例 10：分级反压简图（用户 11-05 要求在 §4 给一张简图）
# =====================================================================
CHAIN = [('CCU', '发 en / addr', C_SIDE), ('L1 读口', '1 拍返回', C_OFF), ('MXU 供数', '缓冲 D₁', C_ACC),
         ('阵列', '流水 D_arr', C_ACC), ('出口级', '缓冲 D₂', C_ACC), ('VNU', '入口缓冲 D₃', C_ACC), ('L1 写集合器', '写者 FIFO\n将满 → wr_stall', C_OFF)]
STALLS = [(2, 0, 'stall_mxu[p]：供数缓冲将满 → CCU 停发该 pod 的 en'),
          (3, 2, 'stall：阵列不能再收 → 供数停发列'),
          (4, 3, 'stall：出口级将满 → 阵列冻结'),
          (5, 4, 'stall：VNU 入口将满 → 出口级停推'),
          (5, 0, 'stall_vnu[i]：VNU 读 L1 的入口将满 → CCU 停发该入口的 en')]
DEPTH, L_LAT = 8, 2
THRESH = DEPTH - L_LAT
assert THRESH == 6


def fig_stall_chain():
    s = Svg(1500, 620)
    s.rich(30, 30, 'FIG-TP-STALL-CHAIN  分级握手：每根 stall 只在相邻两级之间，最终汇到发 en 的 CCU（没有全局 stall）', 20)
    s.note(30, 62, '数据从左向右推送；红色箭头是 stall，指向"谁该停"。链末端是 L1 写集合器里该写者的 FIFO，只在撞 bank 的瞬时堆积、将满才拉 wr_stall；CCU 自身不拉 stall', 15)
    X0, Y0, BW, BH, GAP = 60, 130, 170, 80, 30
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
    s.note(X0, Y0 + BH + 22, '→ 数据 / 请求方向（CCU → L1 是 en / addr，其余是推送）', 13)
    # stall 弧线：画在框下方，按层错开
    y = Y0 + BH + 60
    for k, (src, dst, text) in enumerate(STALLS):
        yy = y + k * 46
        xa, xb = xs[src] + BW / 2, xs[dst] + BW / 2
        s.line([(xa, Y0 + BH), (xa, yy), (xb, yy), (xb, Y0 + BH + 2)], RED, 2, 'ar', '6,4')
        s.red(min(xa, xb) + 10, yy - 12, text, 13)
    y2 = y + len(STALLS) * 46 + 20
    s.rich(30, y2, '将满阈值', 16)
    s.note(30, y2 + 28, f'例：某级缓冲深度 {DEPTH}，从它拉 stall 到上游真正停发要 {L_LAT} 拍（CCU 停发 1 拍 + L1 读返回 1 拍），所以在占用到 {THRESH} 时就拉，留 {L_LAT} 个空位接在途的拍；各级 L 由设计者登记', 14)
    s.note(30, y2 + 54, '规则：谁发 en，谁判断"有没有地方放"；发 en 的不是消费者本人时，消费者给发 en 者一根 stall。核间 ready 不进核，只在发送桥处变成一根 stall', 14)
    s.save('FIG-TP-STALL-CHAIN.svg', DATE)


if __name__ == '__main__':
    fig_stall_chain()
    # 四张架构图（FIG-TP-ARCH-*）自 11-05 起由 _build/draw_tp_arch.py 产出（Opus Agent，任务书 TP_FIGURE_BRIEF_20261105.md）；
    # 本脚本里的 fig_links / fig_incore / fig_intercore / fig_ctrl 是被用户判定接线错误的旧版，保留代码不再调用。
    fig_addr_accum(); fig_addr_map(); fig_timing(); fig_stream_beat(); fig_length_report()
    fig_ctrl_msg(); fig_object_align(); fig_slot_count(); fig_token_slot()
    print('10 numeric figures written')
