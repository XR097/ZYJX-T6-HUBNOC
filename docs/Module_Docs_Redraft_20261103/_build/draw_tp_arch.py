"""片上数据传输协议篇的四张架构图（手写坐标，不用布线器）。Owner: WangYizhao · 2026-11-05
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_tp_arch.py
输出（figs/）：
  FIG-TP-ARCH-LINKS      图 A 全芯片物理链路（任务书 §1.2 的 21 条链路）
  FIG-TP-ARCH-INCORE     图 B 一核内 RRAM 口与分级 stall
  FIG-TP-ARCH-INTERCORE  图 C 核间带地址的握手写流（11-05 夜改版：dest、独立取走、IDN 4 条独立链路；11-06：C2H 由 CCU 发令、写计数、通用链路块；11-06 深夜 V18-TP-50：所有核间写链路回写入握手）
  FIG-TP-ARCH-CTRL       图 D 命令网（11-06：撤 MAE → 核的 C2H 发送命令，发出报告；11-07 晚：标量不走本网、MAE_CRU 端点撤、改名命令网）
  11-07 晚（V18-CRU-07 / TP-55 / 56 / MAE-32 / HUB-03）：LINKS / INTERCORE 撤 C2H 去 MAE_CRU 的分支、CRU → H2C 第二源、标量线；
  MAE_CRU 只连 NI_INT（读 4 × 32 B、写回 L2）；核的发送桥改称集成输出端口（C2H 唯一来源）；INCORE 撤 AEB 桥，MXU / VNU 输出可进集成输出端口
  11-06 晚（V18-MAE-11…18）：LINKS / INTERCORE / CTRL 的 CRU 移进 MAE 组框（mae_frame）并改名 MAE_CRU；
  CTRL 撤操作 18 与"完成计数"，LIC ⇄ MAE 改为指令标号 + 完成通知，MAE_CRU 单独一个命令网端点
自检（save 时执行，任一项不过即报错退出）：
  1. 文字 / 标签不出画布、互不重叠、不压任何连线；
  2. 标签不跨色块边框（要么整块在框外，要么整块在框内）；
  3. 连线不穿过任何色块内部（虚线分组框不计）；
  4. 不同连线不共线重叠；
  5. 横线与竖线的不相连交叉自动画跳线弧，交叉点离拐角太近时报错。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / 'figs'
DATE = '2026-11-08'
FONT = 'Microsoft YaHei,Arial,sans-serif'
NAVY = '#172b4d'
INK = '#1d2530'
GREY = '#8a94a6'

# 调色：(描边 / 线色, 填充)
P = {
    'incore': ('#0f766e', '#ccfbf1'),   # 核内 RRAM 口：青
    'inter':  ('#1d4ed8', '#dbeafe'),   # 核间数据网：蓝
    'ctrl':   ('#c2410c', '#ffedd5'),   # 命令网：橙
    'axi':    ('#4b5563', '#f3f4f6'),   # 对外 AXI / APB：灰
    'stall':  ('#b91c1c', '#fee2e2'),   # stall：红
    'push':   ('#6d28d9', '#ede9fe'),   # 推送段：紫
    'mem':    ('#334155', '#e2e8f0'),   # 存储
    'comp':   ('#6d28d9', '#ede9fe'),   # 计算单元
    'ctlu':   ('#b45309', '#fef3c7'),   # 控制单元
    'ext':    ('#475569', '#f1f5f9'),   # 片外 / SoC
    'hub':    ('#0369a1', '#e0f2fe'),   # hub
    'core':   ('#0f766e', '#f0fdfa'),   # 核框
    'chip':   ('#172b4d', '#ffffff'),   # 芯片边界
}


def text_w(s, size):
    s = re.sub(r'[\^_]\{([^}]*)\}', lambda m: m.group(1), str(s))
    return sum(size if ord(ch) > 0x2E80 else 0.58 * size for ch in s)


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def overlap(a, b, pad=0.0):
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


def inside(a, b):
    return a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]


def seg_hits_rect(p, q, r, pad=0.0):
    """正交线段 pq 是否与矩形 r（x0,y0,x1,y1）相交（pad>0 外扩，pad<0 内缩）。"""
    x0, y0, x1, y1 = r[0] - pad, r[1] - pad, r[2] + pad, r[3] + pad
    if abs(p[1] - q[1]) < 1e-6:          # 横线
        y = p[1]
        a, b = sorted((p[0], q[0]))
        return y0 < y < y1 and a < x1 and b > x0
    x = p[0]
    a, b = sorted((p[1], q[1]))
    return x0 < x < x1 and a < y1 and b > y0


class Fig:
    def __init__(self, name, title, sub, w=1920, h=1080):
        self.name, self.w, self.h = name, w, h
        self.layers = {'bg': [], 'group': [], 'block': [], 'line': [], 'dot': [], 'tag': [], 'text': []}
        self.blocks = []      # (rect, name)  连线不得穿过
        self.texts = []       # (rect, label, container_rect or None)  文字 / 标签
        self.lines = []       # dict(pts, kind, sw, dash, head, net, hop)
        self.hops_drawn = 0
        self.layers['bg'].append(f'<rect width="100%" height="100%" fill="#f8fafc"/>')
        self.layers['bg'].append(f'<rect x="0" y="0" width="{w}" height="86" fill="{NAVY}"/>')
        self._text(40, 36, title, 30, 'start', 'white', 700, reg=False)
        self._text(40, 66, sub, 16, 'start', '#cbd5e1', 500, reg=False)

    # ---------------- 基本图元 ----------------
    def _text(self, x, y, s, size, anchor, color, weight, reg=True, layer='text', box=None):
        wid = text_w(s, size)
        left = x - (wid if anchor == 'end' else wid / 2 if anchor == 'middle' else 0)
        rect = (left, y - size * 0.62, left + wid, y + size * 0.62)
        if reg:
            self.texts.append((rect, s, box))
        assert rect[0] >= 2 and rect[2] <= self.w - 2, ('text out of canvas', s)
        self.layers[layer].append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" dominant-baseline="central" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(s)}</text>')
        return rect

    def text(self, x, y, s, size=14, anchor='start', color=INK, weight=500, box=None):
        return self._text(x, y, s, size, anchor, color, weight, box=box)

    def block(self, x, y, w, h, title, sub='', kind='mem', size=19, subsize=13, rx=10, shadow=True, align='middle'):
        stroke, fill = P[kind]
        f = ' filter="url(#sh)"' if shadow else ''
        self.layers['block'].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
                                    f'stroke="{stroke}" stroke-width="2.2"{f}/>')
        rect = (x, y, x + w, y + h)
        self.blocks.append((rect, title))
        lines = sub.split('\n') if sub else []
        th = size + (len(lines) * (subsize + 5) + 4 if lines else 0)
        y0 = y + h / 2 - th / 2 + size / 2
        tx = x + w / 2 if align == 'middle' else x + 10
        self._text(tx, y0, title, size, align, stroke, 700, box=rect)
        for i, s in enumerate(lines):
            self._text(tx, y0 + size / 2 + 4 + i * (subsize + 5) + subsize / 2 + 1, s, subsize, align, INK, 500, box=rect)
        return rect

    def group(self, x, y, w, h, title, kind='ext', size=17, tx=None, strip=True, dash='9,6', sw=2.0, fill='white'):
        stroke, sfill = P[kind]
        self.layers['group'].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" '
                                    f'stroke="{stroke}" stroke-width="{sw}" stroke-dasharray="{dash}"/>')
        if strip:
            self.layers['group'].append(f'<path d="M{x + 1},{y + 30} L{x + 1},{y + 12} Q{x + 1},{y + 1} {x + 12},{y + 1} '
                                        f'L{x + w - 12},{y + 1} Q{x + w - 1},{y + 1} {x + w - 1},{y + 12} L{x + w - 1},{y + 30} Z" '
                                        f'fill="{sfill}" stroke="none"/>')
        if title:
            self._text(tx if tx is not None else x + 14, y + 16, title, size, 'start', stroke, 700, box=(x, y, x + w, y + h))
        return (x, y, x + w, y + h)

    def line(self, pts, kind='inter', sw=3.0, dash=None, head='end', net=None, hop=True):
        self.lines.append(dict(pts=[(float(a), float(b)) for a, b in pts], kind=kind, sw=sw, dash=dash,
                               head=head, net=net if net is not None else f'_n{len(self.lines)}', hop=hop))

    def dot(self, x, y, kind='inter', r=4.5):
        self.layers['dot'].append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{P[kind][0]}"/>')

    def tag(self, x, y, s, kind='inter', size=13, anchor='middle', box=None):
        stroke, fill = P[kind]
        wid = text_w(s, size) + 14
        left = x - (wid if anchor == 'end' else wid / 2 if anchor == 'middle' else 0)
        rect = (left, y - size / 2 - 5, left + wid, y + size / 2 + 5)
        self.texts.append((rect, s, box))
        self.layers['tag'].append(f'<rect x="{left:.1f}" y="{rect[1]:.1f}" width="{wid:.1f}" height="{size + 10}" rx="5" '
                                  f'fill="{fill}" stroke="{stroke}" stroke-width="1.1"/>')
        self._text(left + 7, y, s, size, 'start', stroke, 700, reg=False, layer='tag')
        return rect

    def note(self, x, y, lines_, size=14, kind='mem', w=None, title=None):
        """多行说明框（白底细框）。"""
        stroke, fill = P[kind]
        lh = size + 9
        wid = w or max(text_w(s, size) for s in lines_) + 28
        nrow = len(lines_) + (1 if title else 0)
        h = nrow * lh + 16
        rect = (x, y, x + wid, y + h)
        self.layers['block'].append(f'<rect x="{x}" y="{y}" width="{wid:.0f}" height="{h}" rx="8" fill="white" '
                                    f'stroke="{GREY}" stroke-width="1.2" filter="url(#sh)"/>')
        self.blocks.append((rect, 'note'))
        yy = y + 8 + lh / 2
        if title:
            self._text(x + 14, yy, title, size + 1, 'start', NAVY, 700, box=rect)
            yy += lh
        for s in lines_:
            self._text(x + 14, yy, s, size, 'start', INK, 500, box=rect)
            yy += lh
        return rect

    def legend(self, x, y, items, cols=1, colw=230, size=14, rowh=28):
        """items: (kind, label, style)；style ∈ solid / 虚线串 / box / dot / hop / thin。"""
        rows = -(-len(items) // cols)
        w, h = cols * colw + 12, rows * rowh + 16
        rect = (x, y, x + w, y + h)
        self.layers['block'].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="white" '
                                    f'stroke="{GREY}" stroke-width="1.2" filter="url(#sh)"/>')
        self.blocks.append((rect, 'legend'))
        for i, (kind, s, style) in enumerate(items):
            c, r = divmod(i, rows)
            xx, yy = x + 14 + c * colw, y + 8 + rowh / 2 + r * rowh
            col = P[kind][0]
            if style == 'box':
                self.layers['block'].append(f'<rect x="{xx}" y="{yy - 9}" width="36" height="18" rx="4" fill="{P[kind][1]}" stroke="{col}" stroke-width="2"/>')
            elif style == 'dot':
                self.layers['block'].append(f'<path d="M{xx},{yy} L{xx + 36},{yy}" stroke="{col}" stroke-width="2.4"/>'
                                            f'<path d="M{xx + 18},{yy} L{xx + 18},{yy + 10}" stroke="{col}" stroke-width="2.4"/>'
                                            f'<circle cx="{xx + 18}" cy="{yy}" r="4.5" fill="{col}"/>')
            elif style == 'hop':
                self.layers['block'].append(f'<path d="M{xx + 18},{yy - 10} L{xx + 18},{yy + 10}" stroke="{col}" stroke-width="2.4"/>'
                                            f'<path d="M{xx},{yy} L{xx + 12},{yy} A6,6 0 0 1 {xx + 24},{yy} L{xx + 36},{yy}" '
                                            f'stroke="{col}" stroke-width="2.4" fill="none"/>')
            else:
                sw = 1.8 if style == 'thin' else 3
                ds = '' if style in ('solid', 'thin') else f' stroke-dasharray="{style}"'
                self.layers['block'].append(f'<path d="M{xx},{yy} L{xx + 30},{yy}" stroke="{col}" stroke-width="{sw}"{ds} '
                                            f'marker-end="url(#m_{kind})"/>')
            self._text(xx + 46, yy, s, size, 'start', INK, 500, box=rect)
        return rect

    # ---------------- 跳线弧与自检 ----------------
    @staticmethod
    def _segs(ln):
        p = ln['pts']
        return [(p[i], p[i + 1]) for i in range(len(p) - 1)]

    def _hops(self):
        """对每条横线段，找别的连线的竖线段与之严格内部相交的点（不含端点 = T 接）。"""
        """横线默认跳过竖线；横线 hop=False 时改由竖线跳过横线。"""
        R = 6.0
        errs = []
        for ln in self.lines:
            ln['hops'] = {}
        for ln in self.lines:
            for si, (p, q) in enumerate(self._segs(ln)):
                if abs(p[1] - q[1]) > 1e-6:
                    continue
                y = p[1]
                a, b = sorted((p[0], q[0]))
                for other in self.lines:
                    if other is ln or other['net'] == ln['net']:
                        continue
                    for sj, (u, v) in enumerate(self._segs(other)):
                        if abs(u[0] - v[0]) > 1e-6:
                            continue
                        x = u[0]
                        c, d = sorted((u[1], v[1]))
                        if a < x < b and c < y < d:
                            if ln['hop']:
                                if min(x - a, b - x) < R + 2:
                                    errs.append(f'hop too close to corner at ({x:.0f},{y:.0f})')
                                ln['hops'].setdefault(si, set()).add(x)
                            else:
                                if min(y - c, d - y) < R + 2:
                                    errs.append(f'v-hop too close to corner at ({x:.0f},{y:.0f})')
                                other['hops'].setdefault(sj, set()).add(y)
        for ln in self.lines:
            ln['hops'] = {k: sorted(v) for k, v in ln['hops'].items()}
        return errs

    def _path(self, ln):
        R = 6.0
        pts = ln['pts']
        d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
        for si in range(len(pts) - 1):
            p, q = pts[si], pts[si + 1]
            hs = ln.get('hops', {}).get(si, [])
            horiz = abs(p[1] - q[1]) < 1e-6
            if hs and horiz:
                fwd = q[0] > p[0]
                for x in (hs if fwd else hs[::-1]):
                    x0, x1 = (x - R, x + R) if fwd else (x + R, x - R)
                    d += f' L{x0:.1f},{p[1]:.1f} A{R},{R} 0 0 {1 if fwd else 0} {x1:.1f},{p[1]:.1f}'
                    self.hops_drawn += 1
            elif hs:
                fwd = q[1] > p[1]
                for y in (hs if fwd else hs[::-1]):
                    y0, y1 = (y - R, y + R) if fwd else (y + R, y - R)
                    d += f' L{p[0]:.1f},{y0:.1f} A{R},{R} 0 0 {0 if fwd else 1} {p[0]:.1f},{y1:.1f}'
                    self.hops_drawn += 1
            d += f' L{q[0]:.1f},{q[1]:.1f}'
        return d

    def check(self):
        errs = []
        # 文字：互不重叠、不跨框
        T = self.texts
        for i in range(len(T)):
            ri, si, bi = T[i]
            for j in range(i + 1, len(T)):
                rj, sj, bj = T[j]
                if overlap(ri, rj, -0.5):
                    errs.append(f'text overlap: "{si}" / "{sj}"')
            for rb, nb in self.blocks:
                if bi is not None and rb == bi:
                    continue
                if overlap(ri, rb, -0.5) and not inside(ri, rb):
                    errs.append(f'text crosses block border: "{si}" / {nb}')
                if bi is None and inside(ri, rb) and nb not in ('legend', 'note'):
                    errs.append(f'free tag inside block: "{si}" / {nb}')
        # 文字不压线
        for ln in self.lines:
            for (p, q) in self._segs(ln):
                for r, s, _ in T:
                    if seg_hits_rect(p, q, r, 1.5):
                        errs.append(f'line over text: "{s}" at {p}->{q}')
        # 连线不穿色块
        for ln in self.lines:
            for (p, q) in self._segs(ln):
                for rb, nb in self.blocks:
                    if seg_hits_rect(p, q, rb, -2.5):
                        errs.append(f'line through block {nb}: {p}->{q}')
        # 不同连线不共线重叠
        L = self.lines
        for i in range(len(L)):
            for j in range(i + 1, len(L)):
                for (p, q) in self._segs(L[i]):
                    for (u, v) in self._segs(L[j]):
                        if abs(p[1] - q[1]) < 1e-6 and abs(u[1] - v[1]) < 1e-6 and abs(p[1] - u[1]) < 3:
                            a, b = sorted((p[0], q[0])); c, d = sorted((u[0], v[0]))
                            if min(b, d) - max(a, c) > 1:
                                errs.append(f'collinear H overlap y={p[1]:.0f} x={max(a, c):.0f}..{min(b, d):.0f}')
                        if abs(p[0] - q[0]) < 1e-6 and abs(u[0] - v[0]) < 1e-6 and abs(p[0] - u[0]) < 3:
                            a, b = sorted((p[1], q[1])); c, d = sorted((u[1], v[1]))
                            if min(b, d) - max(a, c) > 1:
                                errs.append(f'collinear V overlap x={p[0]:.0f} y={max(a, c):.0f}..{min(b, d):.0f}')
        return errs

    def save(self):
        errs = self._hops() + self.check()
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">',
               '<defs><filter id="sh" x="-5%" y="-5%" width="115%" height="125%">'
               '<feDropShadow dx="2" dy="3" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.20"/></filter>'
               + ''.join(f'<marker id="m_{k}" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="11" refX="12" refY="5.5" orient="auto">'
                         f'<path d="M0,0 L13,5.5 L0,11 Z" fill="{v[0]}"/></marker>'
                         f'<marker id="s_{k}" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="11" refX="1" refY="5.5" orient="auto">'
                         f'<path d="M13,0 L0,5.5 L13,11 Z" fill="{v[0]}"/></marker>' for k, v in P.items())
               + '</defs>']
        for k in ('bg', 'group', 'block'):
            out += self.layers[k]
        for ln in self.lines:
            col = P[ln['kind']][0]
            ds = f' stroke-dasharray="{ln["dash"]}"' if ln['dash'] else ''
            me = f' marker-end="url(#m_{ln["kind"]})"' if ln['head'] in ('end', 'both') else ''
            ms = f' marker-start="url(#s_{ln["kind"]})"' if ln['head'] in ('start', 'both') else ''
            out.append(f'<path d="{self._path(ln)}" stroke="{col}" stroke-width="{ln["sw"]}" fill="none" '
                       f'stroke-linejoin="round"{ds}{me}{ms}/>')
        out += self.layers['dot'] + self.layers['tag'] + self.layers['text']
        out.append(f'<text x="{self.w - 24}" y="{self.h - 12}" text-anchor="end" font-family="{FONT}" font-size="13" '
                   f'font-weight="500" fill="{GREY}">Owner: WangYizhao · {DATE}</text>')
        out.append('</svg>')
        FIGS.mkdir(parents=True, exist_ok=True)
        (FIGS / self.name).write_text('\n'.join(out), encoding='utf-8')
        print(f'wrote {self.name}: {len(self.lines)} lines, {self.hops_drawn} hops, {len(errs)} issues')
        for e in errs:
            print('   !', e)
        return errs


# =====================================================================
# 图 A：全芯片物理链路
# =====================================================================
CX = [110, 550, 990, 1430]          # 四核左边
CW, CY, CH = 405, 750, 215          # 核宽、核顶、核高
LANE_OFF = [170, 190, 210, 230]     # H2C 道 0–3 在核顶的横向偏移
C2H_OFF, CTRL_OFF, IDN_OFF = 100, 60, 380


def core_box(s, i, x, y=CY, w=CW, h=CH):
    """图 A 里的一个计算核：L1 在上，CCU / MXU / VNU 在下；核内 SRAM 口总线青色示意。"""
    s.group(x, y, w, h, '', 'core', strip=False, dash='none', sw=2.4, fill=P['core'][1])
    s.text(x + 14, y + 18, f'计算核 {i}', 15, 'start', P['core'][0], 700, box=(x, y, x + w, y + h))
    s.block(x + 15, y + 38, w - 30, 60, 'L1 SRAM', '两堆 × W / S / A · 接收桥 LDP × 4 / NWB · 发送侧', 'mem', 16, 12, shadow=False)
    s.block(x + 15, y + 120, 110, 55, 'CCU', '地址推理', 'ctlu', 15, 12, shadow=False)
    s.block(x + 140, y + 120, 105, 55, 'MXU', '供数 · 阵列', 'comp', 15, 12, shadow=False)
    s.block(x + 262, y + 120, 98, 55, 'VNU', '', 'comp', 15, 12, shadow=False)
    # 核内 SRAM 口总线（青）：CCU → L1 en/addr；L1 ⇄ MXU；L1 ⇄ VNU
    s.line([(x + 50, y + 120), (x + 50, y + 98)], 'incore', 2.4)
    s.line([(x + 192, y + 120), (x + 192, y + 98)], 'incore', 2.4, head='both')
    s.line([(x + 310, y + 120), (x + 310, y + 98)], 'incore', 2.4, head='both')
    # 命令网口 → CCU；IDN 道 i → L1（NWB）
    s.line([(x + CTRL_OFF, y + h), (x + CTRL_OFF, y + 175)], 'ctrl', 2.2, dash='7,4', head='end', net=f'ctrl{i}')
    s.line([(x + IDN_OFF, y + h), (x + IDN_OFF, y + 98)], 'inter', 2.2, net=f'idn{i}')
    s.text(x + CTRL_OFF + 8, y + 196, '命令网口 → CCU', 12, 'start', P['ctrl'][0], 700, box=(x, y, x + w, y + h))
    s.text(x + IDN_OFF - 8, y + 196, 'IDN 1 × 32 B', 12, 'end', P['inter'][0], 700, box=(x, y, x + w, y + h))


def mae_frame(s, pts, title_xy, title='MAE 组（五单元）', size=15):
    """MAE 组的虚线外框（任意正交多边形，11-06 晚 CRU 并入 MAE 组，V18-MAE-11；11-07 IDN 归 HUB 组，V18-HUB-01，HUB_IDN 仍画在 NI_INT 框里只为连线，框标题注明属 HUB 组）。"""
    stroke = P['ctlu'][0]
    d = 'M' + ' L'.join(f'{x},{y}' for x, y in pts) + ' Z'
    s.layers['group'].append(f'<path d="{d}" fill="#fffcf2" stroke="{stroke}" stroke-width="2.2" stroke-dasharray="9,6"/>')
    s.text(title_xy[0], title_xy[1], title, size, 'start', stroke, 700)


def hub_part(s, x, y, w, h, title, size=13):
    """HUB 组的一部分（11-07 用户：NoC 与 IDN 不必放在一起，但都标注属于 HUB）。"""
    return s.group(x, y, w, h, title, 'hub', size, strip=True, dash='9,6', sw=2.0, fill='#f5fbff')


def fig_links():
    s = Fig('FIG-TP-ARCH-LINKS.svg', 'FIG-TP-ARCH-LINKS  全芯片物理链路',
            '核间无直连；每核对外只有 H2C 入、C2H 出、IDN 入三个数据口 + 命令网口；LIC / MAE 到核的消息一律经 hub 控制道；NI 写 L2 与 NI 读 L2 不经 hub；跨核合并经 L2',
            h=1150)
    # ---------- SoC 侧（芯片边界外） ----------
    s.block(30, 98, 230, 90, 'M55', 'SoC Runtime 处理器', 'ext', 18, 13)
    s.block(640, 98, 760, 90, 'SoC 片上互联（总线矩阵，SoC 设计方）', '系统 DMA · HSRAM · FMC · AXI→APB 桥', 'ext', 18, 13)
    s.block(1700, 98, 190, 90, 'DDR（LPDDR5）', '控制器 P0 · P1 · P2', 'ext', 17, 13)
    s.line([(260, 150), (640, 150)], 'axi', 1.8, head='both')
    s.tag(450, 126, 'M55 经 SoC 片上互联访问 SRAM / DDR P2', 'axi', 12)
    s.line([(1400, 112), (1700, 112)], 'axi', 1.8)
    s.tag(1550, 133, '经 P2 访问 DDR（P1 接小核侧）', 'axi', 12)
    # ---------- 芯片边界 ----------
    s.group(20, 200, 1880, 852, '', 'chip', strip=False, dash='none', sw=2.6, fill='#ffffff')
    s.text(345, 214, 'NPU（大核）芯片边界', 14, 'start', NAVY, 700)
    # ---------- 第一排：CIF、LIC、MAE_ENG、NI_EXT ----------
    s.block(30, 235, 160, 80, 'CIF', 'APB 寄存器 · 邮箱 · 中断', 'ctlu', 18, 11)
    s.block(330, 235, 250, 80, 'LIC（含 LOOP）', '指令 SRAM · 顺序取指', 'ctlu', 18, 13)
    # MAE 组虚线框（L 形：上排 MAE_ENG + NI_EXT，右列 NI_INT + MAE_CRU；11-06 晚 V18-MAE-11；11-07 HUB_IDN 移出，V18-HUB-01）
    mae_frame(s, [(708, 230), (1895, 230), (1895, 636), (1690, 636), (1690, 332), (708, 332)], (1000, 302))
    s.block(720, 235, 260, 80, 'MAE_ENG', '指令引擎 · 搬运引擎（逐拍地址）', 'ctlu', 18, 12)
    s.block(1440, 235, 450, 80, 'NI_EXT', 'M0 / M1 / PIN 三个 AXI 口与跨时钟', 'ext', 18, 13)
    # #13 M55 ↔ CIF：APB 下，IRQ 上
    s.line([(70, 188), (70, 235)], 'axi', 2.2)
    s.line([(150, 235), (150, 188)], 'axi', 2.2)
    s.tag(168, 216, 'APB 32 bit ↓ · IRQ ↑', 'axi', 12, 'start')
    # #10–#12 对外 AXI
    s.line([(1850, 235), (1850, 188)], 'axi', 3.4)                         # M0 → DDR P0
    s.line([(1640, 235), (1640, 155), (1400, 155)], 'axi', 2.4)            # M1 → SoC 片上互联
    s.line([(1400, 175), (1500, 175), (1500, 235)], 'axi', 2.4)            # SoC 片上互联 → PIN
    s.tag(1508, 216, 'PIN 从 64 bit', 'axi', 12, 'start')
    s.tag(1648, 216, 'M1 主 64 bit', 'axi', 12, 'start')
    s.tag(1842, 216, 'M0 256 bit', 'axi', 12, 'end')
    # #14 CIF ↔ LIC
    s.line([(190, 247), (330, 247)], 'axi', 2.2)
    s.tag(260, 264, '门铃 · 指针 · 停止', 'axi', 12)
    s.line([(330, 285), (190, 285)], 'axi', 2.2)
    s.tag(260, 302, '完成 · 致命错误', 'axi', 12)
    # #15 LIC ↔ MAE_ENG
    s.line([(580, 247), (720, 247)], 'ctrl', 2.2, dash='7,4')
    s.tag(645, 264, '指令 · 标号', 'ctrl', 12)
    s.line([(720, 285), (580, 285)], 'ctrl', 2.2, dash='7,4')
    s.tag(645, 302, '完成通知 · 标号', 'ctrl', 12)
    # #21 NI_EXT M1 读返回 → LIC（走第一排上方）
    s.line([(1455, 235), (1455, 214), (560, 214), (560, 235)], 'ctrl', 2.2, dash='7,4')
    s.tag(1210, 247, 'M1 读返回 → LIC 直连口 32 B：指令 · 配置表 · 调用描述符', 'ctrl', 12)
    # 图例（11-06 晚移到芯片边界下方，给 MAE 组框让位）
    s.legend(30, 1064, [('inter', '核间握手写流 32 B/拍', 'solid'), ('ctrl', '命令网 64 bit', '7,4'),
                        ('axi', '对外 AXI / APB · CIF 口', 'solid'), ('incore', '核内 RRAM', 'solid'),
                        ('inter', '分叉 = 多播', 'dot'), ('inter', '跳线 = 不相连', 'hop')],
             cols=3, colw=206, size=13, rowh=26)

    # ---------- 第二排：L2、NI_INT ----------
    s.group(785, 395, 770, 85, '中央 L2 SRAM · 2 MiB · 4 象限 × 8 bank', 'mem', 15, strip=True, dash='none', sw=2.2,
            fill=P['mem'][1])
    QX = [800 + 190 * n for n in range(4)]
    for n, qx in enumerate(QX):
        s.block(qx, 432, 170, 42, f'象限 {n}', '', 'mem', 14, shadow=False)
    s.block(1700, 395, 190, 85, 'NI_INT', 'MAE_DSU · NI-L2C（五源）\n读返回分路 · NI 控制道', 'ext', 14, 12)
    # HUB 组的 HUB_IDN（11-07：与 HUB_NOC 分开画，标注同属 HUB 组）
    hub_part(s, 1693, 642, 204, 72, 'HUB 组', 13)
    s.block(1702, 669, 188, 38, 'HUB_IDN', '32 B 进 · 按核集合分发 · 多播分叉', 'hub', 13, 11, shadow=False)
    # #20 NI_EXT ↔ NI_INT
    s.line([(1790, 315), (1790, 395)], 'inter', 3.0)
    s.line([(1815, 395), (1815, 315)], 'inter', 3.0)
    s.tag(1782, 352, '↓ 读返回 32 B', 'inter', 12, 'end')
    s.tag(1821, 352, '↑ 返回数据', 'inter', 11, 'start')
    # MAE_CRU（11-06 晚并入 MAE 组，V18-MAE-11 / 12）：与 NI_INT 之间 = 结果经 NI-L2C 写 L2 ↑、读路径数据 ↓
    s.block(1700, 522, 140, 104, 'MAE_CRU', '从 L2 读四象限\n合并 · 写回 L2', 'comp', 14, 11, shadow=False)
    s.line([(1715, 522), (1715, 480)], 'inter', 2.4)
    s.line([(1735, 480), (1735, 522)], 'inter', 2.4)
    s.tag(1745, 501, '读 · 写 L2', 'inter', 11, 'start')
    # #19 MAE_ENG ↔ NI_INT
    s.line([(960, 315), (960, 372), (1720, 372), (1720, 395)], 'ctrl', 2.2, dash='7,4', head='both')
    s.tag(1210, 356, 'MAE_ENG → NI_INT / HUB_IDN：解码后的控制 · NI_EXT → MAE：写响应', 'ctrl', 12)
    # #8 NI_INT → L2 NI 写口；#9 L2 NI 返回读口 → NI_INT
    s.line([(1700, 425), (1555, 425)], 'inter', 3.0)
    s.tag(1628, 410, 'NI 写口 32 B', 'inter', 12)
    s.line([(1555, 462), (1700, 462)], 'inter', 3.0)
    s.tag(1628, 447, 'NI 读口 4 × 32 B', 'inter', 12)

    # ---------- hub ----------
    s.group(28, 520, 1652, 194, 'HUB 组 · HUB_NOC（全芯片一个）', 'hub', 17, tx=180)
    s.block(40, 553, 130, 55, 'hub 控制道', '消息转发', 'ctrl', 14, 12, shadow=False)
    s.block(470, 553, 250, 55, 'hub 中心', 'C2H：四核直通 L2 四条写链路\n不扇入 · 不分路', 'hub', 15, 11, shadow=False)
    DNX = [qx + 85 for qx in QX]
    for n, qx in enumerate(QX):
        s.block(qx, 553, 170, 55, f'H2C 道 {n}', f'读象限 {n} · 多播分叉', 'hub', 14, 12, shadow=False)
        # #1 象限 n 读口 → 道 n
        s.line([(DNX[n], 474), (DNX[n], 553)], 'inter', 3.4, net=f'rd{n}')
        s.tag(DNX[n] + 8, 527, '读 32 B', 'inter', 11, 'start')
    # 11-07 晚（V18-CRU-07 / TP-55）：撤 C2H 去 MAE_CRU 的分支、CRU → H2C 第二源、hub 控制道 ⇄ MAE_CRU 标量线
    # #4 hub 中心 → L2WP：每核一条写链路，核 k 只进象限 k（V18-L2-03 / 04）；横段 y 随 k 递增、四条互不交叉
    for k in range(4):
        lx, yk, xq = 630 + 20 * k, 486 + 4 * k, QX[k] + 55
        s.line([(lx, 553), (lx, yk), (xq, yk), (xq, 474)], 'inter', 2.4)
    s.tag(618, 500, 'L2WP：核 k → 象限 k', 'inter', 12, 'end')
    # #16 LIC ⇄ hub 控制道：拆成两条单向线，标签贴在各自线的外侧（11-06 晚用户：原画法看不出标签属于哪一侧）
    s.line([(450, 315), (450, 380), (130, 380), (130, 553)], 'ctrl', 2.4, dash='7,4')
    s.tag(290, 365, 'LIC → 核：位点指令 · Fusion 段 · GO · 阈值装载', 'ctrl', 12)
    s.line([(110, 553), (110, 410), (500, 410), (500, 315)], 'ctrl', 2.4, dash='7,4')
    s.tag(305, 426, '核 → LIC：位点完成 · 核事件（GO 与超时由 LIC 判）', 'ctrl', 12)
    # #18 核 → MAE_ENG：发出报告（经 hub 控制道转发）
    s.line([(90, 553), (90, 460), (740, 460), (740, 315)], 'ctrl', 2.4, dash='7,4')
    s.tag(420, 476, '核 → MAE_ENG：发出报告', 'ctrl', 12)
    # #22 MAE_ENG → H2C 道 0–3：逐拍 L2 读 en / addr、目的 addr / be、核掩码（解码后的控制，V18-MAE-27 / NAME-02）
    s.line([(760, 315), (760, 505), (1400, 505)], 'ctrl', 2.2, dash='7,4', head=None, net='h2caddr')
    for n, qx in enumerate(QX):
        s.line([(qx + 30, 505), (qx + 30, 553)], 'ctrl', 2.2, dash='7,4', net='h2caddr')
    s.tag(1466, 494, '← ENG → H2C 道：地址 · 核掩码', 'ctrl', 11, 'start')
    # ---------- 第三排：四核 ----------
    for i, x in enumerate(CX):
        core_box(s, i, x)
        s.tag(x + C2H_OFF - 8, 732, 'C2H · CCU 发令', 'inter', 12, 'end')
        s.tag(x + 240, 732, 'H2C 4 道 × 32 B', 'inter', 12, 'start')
    # #2 H2C：道 n 的横排在 hub 内，经多播分叉点送四核的第 n 道，各核按自己的 ready 独立取走
    ROWY = [658 + 14 * n for n in range(4)]
    for n in range(4):
        xs = [x + LANE_OFF[n] for x in CX]
        s.line([(DNX[n], 608), (DNX[n], ROWY[n])], 'inter', 2.4, head=None, net=f'h2c{n}')
        s.line([(xs[0], ROWY[n]), (xs[-1], ROWY[n])], 'inter', 2.4, head=None, net=f'h2c{n}')
        s.dot(DNX[n], ROWY[n])
        for k, xx in enumerate(xs):
            s.line([(xx, ROWY[n]), (xx, CY + 38)], 'inter', 2.4, net=f'h2c{n}')
            if k not in (0, 3):
                s.dot(xx, ROWY[n])
        s.text(CX[0] + LANE_OFF[0] - 6, ROWY[n], f'道 {n}', 11, 'end', P['inter'][0], 700)
    # #3 C2H：每核一条进 hub 中心（扇入）
    s.line([(CX[0] + C2H_OFF, CY + 38), (CX[0] + C2H_OFF, 642), (520, 642), (520, 608)], 'inter', 3.0)
    s.line([(CX[1] + C2H_OFF, CY + 38), (CX[1] + C2H_OFF, 608)], 'inter', 3.0)
    s.line([(CX[2] + C2H_OFF, CY + 38), (CX[2] + C2H_OFF, 642), (685, 642), (685, 608)], 'inter', 3.0)
    s.line([(CX[3] + C2H_OFF, CY + 38), (CX[3] + C2H_OFF, 626), (705, 626), (705, 608)], 'inter', 3.0)
    # #7 IDN（11-08 V18-HUB-04）：NI_INT 的 IDN 出口一路 32 B → HUB_IDN，按每字的核集合分发；每核一条 32 B 链路（右侧下行，经核下方进 IDN 口）
    LV = {'c0': 975, 'i3': 985, 'c1': 995, 'i2': 1005, 'c2': 1015, 'i1': 1025, 'c3': 1035, 'i0': 1045}
    IDNX = {3: 1852, 2: 1862, 1: 1872, 0: 1882}
    s.line([(IDNX[0], 480), (IDNX[0], 669)], 'inter', 2.6, net='nib0')                 # IDN 出口 1 × 32 B · 核集合随字（标签见 HUB_IDN 块）
    for i in range(4):
        s.line([(IDNX[i], 707), (IDNX[i], LV[f'i{i}']), (CX[i] + IDN_OFF, LV[f'i{i}']), (CX[i] + IDN_OFF, CY + CH)],
               'inter', 2.2, head=None, net=f'idn{i}')
    # #17 hub 控制道 ⇄ 各核命令网口（左侧下行，经核下方）
    CTX = {0: 88, 1: 76, 2: 64, 3: 52}
    for i in range(4):
        s.line([(CTX[i], 608), (CTX[i], LV[f'c{i}']), (CX[i] + CTRL_OFF, LV[f'c{i}']), (CX[i] + CTRL_OFF, CY + CH)],
               'ctrl', 2.2, dash='7,4', head='start', net=f'ctrl{i}', hop=False)
    return s.save()


# =====================================================================
# 图 B：一核内 RRAM 口与分级 stall
# =====================================================================
def fig_incore():
    s = Fig('FIG-TP-ARCH-INCORE.svg', 'FIG-TP-ARCH-INCORE  一个计算核内的 RRAM 口与分级 stall',
            '青：RRAM：en / wea / be / addr / din / dout / vld（wea 定本次访问是写还是读，堆的角色按阶段互换）· 紫：推送段 · 红虚线：stall（相邻级之间，到 CCU 的三类）· 蓝：核间握手写流')
    s.group(20, 100, 1880, 900, '一个计算核（四核同构）', 'core', 16)
    # ---------- CCU ----------
    s.block(40, 250, 250, 310, 'CCU', '所有 L1 读写的 en / wea / addr\n地址 = 基址 + 字节累加\n决定 dout 去哪个 pod / 入口\n收 stall 即停发该路 en\n不看任何缓冲余量', 'ctlu', 22, 13)
    # ---------- L1 两堆 ----------
    s.group(420, 240, 580, 580, 'L1 SRAM：物理 ping-pong，一堆只读、一堆只写（位点内）', 'mem', 14)
    for k, hx in enumerate((436, 716)):
        s.group(hx, 290, 270, 515, f'堆 {k}（地址最高位 = {k}）', 'mem', 14, dash='5,4', sw=1.4)
        s.block(hx + 12, 330, 246, 170, 'W 类 · bank 0–7', '权重列块 · K / V 平面\n段映射，lane 读口 8 行并读', 'mem', 16, 12, shadow=False)
        s.block(hx + 12, 512, 246, 70, 'S 类 · 尺度 SRAM', '尺度行 · bias 旁带行', 'mem', 16, 12, shadow=False)
        s.block(hx + 12, 594, 246, 200, 'A 类 · bank 8–11', '紧凑激活记录 · 停放\n部分和 · 行状态 · 上行暂存\n线性映射', 'mem', 16, 12, shadow=False)
    # CCU → L1：所有口的 en / addr
    s.line([(290, 400), (420, 400)], 'incore', 4.0)
    s.tag(357, 382, 'en·wea·be·addr', 'incore', 12)
    s.tag(355, 418, '每个口一组', 'incore', 12)
    # ---------- 右侧：供数 → 阵列（AEB）→ VNU（NLU 的出口级子模块，11-08 V18-NLU-06）；选择器 ----------
    s.block(1300, 290, 260, 100, 'MXU 供数（4 pod）', 'WWB · 激活记录缓冲', 'comp', 17, 13)
    s.block(1300, 450, 260, 80, 'MXU 阵列', 'FBA · AEB（MXU 到此为止）', 'comp', 17, 13)
    s.block(1640, 290, 250, 390, 'VNU', 'NLU（含出口级子模块：\nAEB 分发 · 残差加 · 停放）\nSEL · SMP · LOSS · QNT · OPT\n\n每条入口一个缓冲\n\n产出写 L1 只给\ndin + 记录长度', 'comp', 20, 13)
    s.block(1160, 600, 90, 160, '选择器', 'L1 外\n每口每拍\n一个客户', 'incore', 15, 12)
    # 权重 lane 读口 + 尺度 / 旁带行 → 供数
    s.line([(1000, 340), (1300, 340)], 'incore', 4.0)
    s.tag(1145, 322, 'dout 16 lane × 16 B + 尺度行 32 B · vld', 'incore', 12)
    # 激活类口 4 × (读 + 写) ↔ 选择器
    s.line([(1000, 640), (1160, 640)], 'incore', 3.4)
    s.tag(1080, 622, '4 口 dout 32 B · vld', 'incore', 12)
    s.line([(1160, 720), (1000, 720)], 'incore', 3.4)
    s.tag(1080, 702, '4 口 din 32 B', 'incore', 12)
    # 选择器 → pod 激活记录缓冲；↔ VNU（含出口级子模块的残差读入 / 停放 / 读改写）
    s.line([(1205, 600), (1205, 370), (1300, 370)], 'incore', 2.6)
    s.line([(1250, 740), (1680, 740), (1680, 680)], 'incore', 2.6, head='both')
    # ---------- 推送链（紫）：供数 → 阵列 → AEB 条目 → VNU ----------
    s.line([(1450, 390), (1450, 450)], 'push', 3.4)
    s.line([(1560, 490), (1640, 490)], 'push', 3.4)
    s.tag(1600, 472, 'AEB 条目', 'push', 12)
    # ---------- 计算核的集成输出端口：C2H 的唯一来源（11-07 晚 V18-TP-56；11-08 V18-TP-59 两源）----------
    s.block(1440, 790, 440, 80, '集成输出端口（C2H 唯一来源）', 'CCU 选：L1 发送侧 / VNU 输出（MXU 输出经出口级透传）\n发送 FIFO 将满 → stall_tx 门控 CCU', 'inter', 16, 12)
    s.line([(1000, 830), (1440, 830)], 'incore', 3.4)
    s.tag(1070, 812, '发送侧读口 32 B', 'incore', 12)
    s.line([(1800, 680), (1800, 790)], 'push', 3.0)                              # VNU → 端口（写 L2 时）
    s.tag(1808, 768, 'VNU 输出', 'push', 12, 'start')
    s.line([(1600, 870), (1600, 1010)], 'inter', 4.0, net='c2h')
    s.tag(1612, 1030, 'C2H 32 B → hub → L2（每核一条）', 'inter', 13, 'start')
    # ---------- 接收桥 LDP / NWB → L1 写口 ----------
    s.block(430, 890, 250, 70, '接收桥 LDP × 4', 'H2C 4 道 · ready = FIFO 未满', 'inter', 15, 12)
    s.block(730, 890, 250, 70, '接收桥 NWB', 'IDN 1 条 32 B · ready = FIFO 未满', 'inter', 15, 12)
    s.line([(555, 890), (555, 820)], 'incore', 3.4)
    s.tag(563, 840, '写：地址 = 到达的 addr · 字节写使能 = be', 'incore', 12, 'start')
    s.line([(855, 890), (855, 820)], 'incore', 3.4)
    s.tag(863, 840, '写口（be 选字节）', 'incore', 12, 'start')
    for n in range(4):
        s.line([(480 + 50 * n, 1010), (480 + 50 * n, 960)], 'inter', 2.6)
    s.tag(555, 1030, 'H2C 道 0–3 · 各 32 B（来自 hub）', 'inter', 13)
    s.line([(855, 1010), (855, 960)], 'inter', 2.6)
    s.tag(855 + 140, 1030, 'IDN 1 条 32 B（来自 HUB_IDN）', 'inter', 13)
    # ---------- stall（红虚线）----------
    D = '6,4'
    s.line([(1700, 290), (1700, 160), (200, 160), (200, 250)], 'stall', 2.6, dash=D)
    s.tag(800, 142, 'stall_vnu[i]：VNU 第 i 条入口缓冲将满（每入口一根）', 'stall', 12)
    s.line([(1350, 290), (1350, 190), (260, 190), (260, 250)], 'stall', 2.6, dash=D)
    s.tag(800, 208, 'stall_mxu[0..3]：pod 供数缓冲将满（每 pod 一根）', 'stall', 12)
    s.line([(1330, 450), (1330, 390)], 'stall', 2.4, dash=D)            # 阵列 → 供数
    s.tag(1338, 420, 'stall', 'stall', 11, 'start')
    s.line([(1640, 515), (1560, 515)], 'stall', 2.4, dash=D)            # VNU（出口级）→ 阵列：AEB ready
    s.tag(1600, 535, 'AEB ready', 'stall', 11)
    s.line([(1440, 862), (330, 862), (330, 520), (290, 520)], 'stall', 2.6, dash=D)
    s.tag(1125, 882, 'stall_tx（门控 CCU）', 'stall', 12)
    # ---------- 说明与图例 ----------
    s.note(30, 590, ['写：en=1, wea=1 → 当拍写入 be 选中的字节',
                     '读：en=1, wea=0 → 下一拍 dout + vld',
                     '固定 1 拍；无 ready、无 busy',
                     '谁发 en 谁判"有没有地方放"',
                     '写口当拍必收，没有 stall',
                     'stall 在"深度 − L"处拉',
                     'L = 拉起到上游停发的拍数',
                     'VNU（出口级）对 AEB 拉 ready',
                     'C2H ready 只到集成输出端口',
                     'stall_tx 门控 CCU：停算等 ready',
                     'MXU / VNU 输出：写 L1 或写 L2（二选一）'], 12, w=285, title='时序与握手规则')
    s.legend(30, 865, [('incore', 'RRAM 口', 'solid'), ('push', '推送段（归模块篇）', 'solid'),
                       ('stall', 'stall', '6,4'), ('inter', '核间握手写流', 'solid')], cols=1, colw=270, size=12, rowh=24)
    return s.save()


# =====================================================================
# 图 C：核间带地址的握手写流（数据网）
# =====================================================================
def fig_intercore():
    s = Fig('FIG-TP-ARCH-INTERCORE.svg', 'FIG-TP-ARCH-INTERCORE  核间带地址的握手写流与"链路 ↔ 核"',
            '目的核 = 哪组 H2C / IDN 线上有 en；源核 = C2H 线号；addr：C2H 由本核 CCU、H2C / IDN 由 MAE 搬运引擎逐拍给出；接收桥 ready = 入口 FIFO 未满')
    # ---------- 信号说明 ----------
    s.note(30, 100, ['发 → 收：en · din 32 B · be · addr 24 bit · src（发令号）；IDN 与 H2C 同一种链路，IDN 每拍一个整字',
                     '收 → 发：ready；所有核间写链路都回写入握手；每级 = 通用链路块；无单位标记',
                     'addr = 目的逻辑地址（C2H 由 CCU、其余由 MAE 搬运引擎给）；去哪个存储由链路决定（无 dest）',
                     '多播各目的核独立取走；C2H 在 hub 里直通 L2、不仲裁；跨核合并：各核写 L2 → MAE_CRU 读四象限'], 13, w=665,
           title='每条链路 = 一组单向握手线，带地址（图中箭头 = 数据方向）')
    # ---------- L2 与 NI_INT ----------
    s.group(740, 110, 820, 120, '中央 L2 SRAM（写口：L2WP × 4、NI 写口；读口：象限 0–3、NI 返回）', 'mem', 14, dash='none', sw=2.2,
            fill=P['mem'][1])
    QX = [760 + 200 * n for n in range(4)]
    DNX = [qx + 90 for qx in QX]
    for n, qx in enumerate(QX):
        s.block(qx, 150, 180, 66, f'象限 {n}', '8 bank · 读口 32 B', 'mem', 15, 12, shadow=False)
    # MAE 组虚线框（倒 L 形：上 NI_INT，右列 MAE_CRU；11-06 晚 V18-MAE-11；11-07 HUB_IDN 移出，V18-HUB-01）
    mae_frame(s, [(1633, 100), (1910, 100), (1910, 456), (1700, 456), (1700, 252), (1633, 252)], (1712, 440), size=14)
    s.block(1640, 110, 262, 130, 'NI_INT', 'MAE_DSU · NI-L2C（五源）\nIDN 出口 → HUB_IDN 1 × 32 B', 'ext', 17, 12)
    # HUB 组的 HUB_IDN（11-07：与 HUB_NOC 分开画，标注同属 HUB 组；11-08 V18-HUB-04：只剩按核集合的分叉点）
    hub_part(s, 1703, 470, 204, 160, 'HUB 组', 14)
    s.block(1712, 502, 188, 116, 'HUB_IDN', '按每字的核集合分发\n接几核即分叉点（已取位）\n每核 1 条 32 B 链路', 'hub', 15, 11, shadow=False)
    # MAE_CRU：入 = C2H 去 MAE_CRU 的分支；出 = H2C 道的第二源、经 NI-L2C 写 L2；读路径数据（兼容）
    s.block(1710, 300, 128, 120, 'MAE_CRU', '从 L2 读四象限\n合并\n写回 L2', 'comp', 15, 11, shadow=False)
    s.line([(1730, 300), (1730, 240)], 'inter', 2.6)          # MAE_CRU → NI-L2C（写 L2）
    s.line([(1750, 240), (1750, 300)], 'inter', 2.6)          # NI_INT 读路径 → MAE_CRU（兼容）
    s.tag(1758, 270, '读 · 写 L2', 'inter', 11, 'start')
    s.line([(1640, 150), (1560, 150)], 'inter', 3.4)
    s.tag(1600, 134, 'NI 写', 'inter', 12)
    s.line([(1560, 200), (1640, 200)], 'inter', 3.4)
    s.tag(1600, 184, 'NI 读', 'inter', 12)
    # ---------- hub ----------
    s.group(30, 260, 1660, 360, 'HUB 组 · HUB_NOC', 'hub', 16)
    # 11-08：C2H 与 L2WP 合成一个框——两者之间没有任何逻辑，四条线各自直通（用户 11-08 要求优化左上角布局）
    C2HX = [330, 400, 425, 450]                          # 四核 C2H 竖线在框内的 x（k = 0…3 从左到右；核 0 的线在框下方先右移到 330，避开组标题）
    s.block(100, 330, 360, 125, 'C2H → L2WP：四核各一路直通', '核 n 的 C2H = L2WP 第 n 条 → 只写象限 n\n不扇入 · 不仲裁 · 不分路\nhub 里没有逻辑，只是四条线穿过', 'hub', 16, 12, shadow=False)
    # 11-07 晚（V18-CRU-07）：撤 C2H 去 MAE_CRU 的分支与 CRU → H2C 第二源
    for k, xk in enumerate(C2HX):                         # 每条线从框顶同一 x 继续向上，横段 y 随 k 递增、四条互不交叉
        yh = 237 + 7 * k                                  # 237…258：在 L2 底边 216 之下、"读 32 B" 标签之上
        s.line([(xk, 330), (xk, yh), (QX[k] + 30, yh), (QX[k] + 30, 216)], 'inter', 2.4)
    s.tag(600, 300, '写 L2：核 k → 象限 k · 各 32 B', 'inter', 12)
    for n, qx in enumerate(QX):
        s.block(qx, 300, 180, 70, f'H2C 道 {n}', f'读象限 {n} → 分叉点\n四路到各核第 {n} 口', 'hub', 15, 11, shadow=False)
        s.line([(DNX[n], 216), (DNX[n], 300)], 'inter', 3.4)
        s.tag(DNX[n] + 8, 278, f'读 32 B', 'inter', 12, 'start')
    # ---------- 四核 ----------
    X = [90, 525, 960, 1395]
    Y0, H = 680, 270
    LO = [150, 190, 230, 270]
    for i, x in enumerate(X):
        box = (x, Y0, x + 405, Y0 + H)
        s.group(x, Y0, 405, H, '', 'core', strip=False, dash='none', sw=2.4, fill=P['core'][1])
        s.text(x + 395, Y0 + 18, f'计算核 {i}', 15, 'end', P['core'][0], 700, box=box)
        s.block(x + 15, Y0 + 40, 95, 56, '输出端口', 'C2H 唯一来源', 'inter', 14, 11, shadow=False)
        s.block(x + 125, Y0 + 40, 170, 56, '接收桥 LDP × 4', 'ready = FIFO 未满', 'inter', 14, 11, shadow=False)
        s.block(x + 15, Y0 + 120, 375, 62, 'L1 两堆', '按 addr 落 bank · 写入项数 → CCU · 写入握手回发令方', 'mem', 15, 11, shadow=False)
        s.block(x + 200, Y0 + 205, 190, 50, '接收桥 NWB', 'IDN 1 条 32 B · 整字直写', 'inter', 14, 11, shadow=False)
        s.line([(x + 210, Y0 + 96), (x + 210, Y0 + 120)], 'incore', 2.6)          # LDP → L1 写口
        s.line([(x + 295, Y0 + 205), (x + 295, Y0 + 182)], 'incore', 2.6)         # NWB → L1 写口
        s.line([(x + 80, Y0 + 120), (x + 80, Y0 + 96)], 'incore', 2.6)            # L1 发送侧读口 → 发送桥
        s.tag(x + 37, 650, 'C2H 32 B', 'inter', 12, 'end')
        s.tag(x + 282, 650, 'H2C 4 × 32 B', 'inter', 12, 'start')
    # H2C：道 n 的分叉点在道框里，直接引出四路到四核 LDP 的第 n 口（线上不打点；V18-TP-53，用户 11-06）
    for n in range(4):
        for k in range(4):
            ex = QX[n] + 18 + 40 * k                     # 道框底边的第 k 个出口
            yl = 512 + 6 * (4 * n + k)                   # 每路一层横线
            xt = X[k] + LO[n]                            # 核 k 的第 n 个 LDP 口
            s.line([(ex, 370), (ex, yl), (xt, yl), (xt, Y0 + 40)], 'inter', 2.2)
    # C2H：每核一条进 C2H → L2WP 框底（x 与 C2HX 一致，框内同一 x 直通）
    s.line([(X[0] + 45, Y0 + 40), (X[0] + 45, 505), (C2HX[0], 505), (C2HX[0], 455)], 'inter', 3.4)
    s.line([(X[1] + 45, Y0 + 40), (X[1] + 45, 500), (C2HX[1], 500), (C2HX[1], 455)], 'inter', 3.4)
    s.line([(X[2] + 45, Y0 + 40), (X[2] + 45, 485), (C2HX[2], 485), (C2HX[2], 455)], 'inter', 3.4)
    s.line([(X[3] + 45, Y0 + 40), (X[3] + 45, 470), (C2HX[3], 470), (C2HX[3], 455)], 'inter', 3.4)
    # IDN（11-08 V18-HUB-04）：NI_INT 的 IDN 出口一路 32 B → HUB_IDN；HUB_IDN 按每字的核集合分发到各核 NWB，每核一条 32 B 链路（右侧下行，经核下方）
    LV = {3: 963, 2: 978, 1: 993, 0: 1008}
    MX = {3: 1856, 2: 1868, 1: 1880, 0: 1892}
    s.line([(MX[0], 240), (MX[0], 502)], 'inter', 3.0, net='nib0')                     # IDN 出口 1 × 32 B（标签在 NI_INT / HUB_IDN 块里）
    for i in range(4):
        s.line([(MX[i], 618), (MX[i], LV[i]), (X[i] + 330, LV[i]), (X[i] + 330, Y0 + 255)], 'inter', 2.6)
    s.tag(1700, 1024, 'IDN：每核 1 条 32 B（HUB_IDN → NWB）', 'inter', 12, 'end')
    return s.save()


# =====================================================================
# 图 D：命令网
# =====================================================================
def fig_ctrl():
    s = Fig('FIG-TP-ARCH-CTRL.svg', 'FIG-TP-ARCH-CTRL  命令网：端点、CCU 指令寄存器与消息方向',
            '64 bit 握手消息流（en / ready / data 64 bit，消息长度在首字、无末字标记）；每条链路单向点到点、与数据网同为通用链路块实例；端点不经 L1 / L2 SRAM')
    D = '7,4'
    # ---------- 第一排 ----------
    s.block(30, 105, 170, 60, 'M55', 'SoC', 'ext', 17, 12)
    s.block(30, 225, 170, 95, 'CIF', 'APB 寄存器 · 邮箱\n中断', 'ctlu', 18, 12)
    # MAE 组虚线框（上排 MAE_ENG + NI 控制道口，下伸一块放 MAE_CRU；11-06 晚 V18-MAE-11 / 12）
    mae_frame(s, [(940, 190), (1898, 190), (1898, 442), (940, 442)], (1262, 424), size=14)
    s.block(340, 200, 360, 120, 'LIC', '指令 SRAM · 顺序取指 · Fusion 段整段发一次\n收各核位点完成 + 数 MAE 完成通知 → 发 GO\n屏障超时由 LIC 检测', 'ctlu', 20, 13)
    s.block(960, 200, 370, 120, 'MAE_ENG', '指令入口可预存下一条 · 多条指令同时执行\n收发出报告 · 数写入握手（按 src）\n每条执行完 → 带指令标号通知 LIC', 'ctlu', 20, 13)
    s.block(1560, 200, 330, 120, 'NI 控制道口', '不收指令（V18-MAE-27）\n长度转发内容由搬运引擎给\n经 NI 控制道发往目的核 CCU', 'ext', 18, 13)
    s.note(230, 100, ['指令先于数据：LIC 顺序取指；执行搬运的引擎先让 hub / NI 控制道发长度转发，再启动数据',
                      '数据到达而位点指令未装入 = 致命错误（长度转发晚到不算）；发现者经命令网报 LIC，LIC 经 CIF 报 M55；标量不走本网（经 C2H → L2 → MAE_CRU）',
                      'CCU：普通指令由 LIC 逐条装"下一条"；Fusion-CCU 整段进段 SRAM、本地按块循环，LIC 不重发；Fusion-L3PU 只在 LIC 执行'], 13, w=1050)
    s.legend(1300, 100, [('ctrl', '命令网链路（单向）', D), ('axi', 'APB / 中断 / CIF 口（非命令网）', 'solid')],
             cols=2, colw=290, size=13, rowh=26)
    # M55 ↔ CIF（不在命令网）
    s.line([(70, 165), (70, 225)], 'axi', 2.2)
    s.line([(160, 225), (160, 165)], 'axi', 2.2)
    s.tag(168, 195, '↓ APB　↑ IRQ', 'axi', 12, 'start')
    # CIF ↔ LIC
    s.line([(200, 245), (340, 245)], 'axi', 2.4)
    s.tag(270, 263, '门铃 · 指针 · 停止', 'axi', 12)
    s.line([(340, 285), (200, 285)], 'axi', 2.4)
    s.tag(270, 303, '完成 · 致命错误', 'axi', 12)
    # LIC ↔ MAE_ENG
    s.line([(700, 240), (960, 240)], 'ctrl', 2.4, dash=D)
    s.tag(820, 258, '搬运指令 + 指令标号（可多条）', 'ctrl', 12)
    s.line([(960, 285), (700, 285)], 'ctrl', 2.4, dash=D)
    s.tag(820, 303, '完成通知（指令标号）', 'ctrl', 12)
    # MAE_ENG ↔ NI
    s.line([(1330, 240), (1560, 240)], 'ctrl', 2.4, dash=D)
    s.tag(1445, 258, '长度转发内容（组内）', 'ctrl', 12)
    # ---------- hub ----------
    s.group(20, 452, 1872, 138, 'hub（全芯片一个；控制道与数据网物理独立）', 'hub', 15)
    s.block(30, 486, 1852, 90, 'hub 控制道（另含 H2C 道旁搬运引擎，逻辑属 MAE_ENG）',
            'LIC ⇄ 各核 CCU：位点指令 / Fusion 段 / GO 下行，事件 / 位点完成上行（转发）　·　CCU 发出报告 → MAE（转发）\n'
            'H2C 道收 MAE_ENG 给的逐拍地址与核掩码（引擎可放在道旁，逻辑属 MAE_ENG）；随 H2C 搬运先发长度转发 → 目的核 CCU　·　hub 不报完成（发令方数写入握手）',
            'hub', 18, 13)
    # 11-07 晚（V18-TP-55）：MAE_CRU 不在命令网上，标量走数据协议（C2H → L2 → MAE_CRU）
    # LIC ↔ hub 控制道
    s.line([(420, 320), (420, 486)], 'ctrl', 2.6, dash=D)
    s.tag(412, 395, '位点指令 / Fusion 段 / GO ↓', 'ctrl', 12, 'end')
    s.line([(620, 486), (620, 320)], 'ctrl', 2.6, dash=D)
    s.tag(628, 430, '事件 / 位点完成 ↑', 'ctrl', 12, 'start')
    # MAE_ENG ↔ hub 控制道
    s.line([(1020, 320), (1020, 486)], 'ctrl', 2.6, dash=D)
    s.tag(1012, 380, 'H2C 地址 · 核掩码 ↓', 'ctrl', 12, 'end')
    s.line([(1150, 486), (1150, 320)], 'ctrl', 2.6, dash=D)
    s.tag(1158, 430, '发出报告 ↑', 'ctrl', 12, 'start')
    # ---------- 四核 ----------
    X = [30, 500, 970, 1440]
    Y0 = 660
    for i, x in enumerate(X):
        box = (x, Y0, x + 450, Y0 + 360)
        s.group(x, Y0, 450, 360, '', 'core', strip=False, dash='none', sw=2.4, fill=P['core'][1])
        s.text(x + 110, Y0 + 18, f'计算核 {i}', 15, 'middle', P['core'][0], 700, box=box)
        s.block(x + 12, Y0 + 40, 188, 74, '集成输出端口（C2H）', 'CCU 选来源：L1 发送侧 / VNU 输出\n给逐拍 L2 addr · 不 ready 停算', 'mem', 14, 12, shadow=False)
        g = s.group(x + 12, Y0 + 130, 426, 220, 'CCU 端点', 'ctlu', 14, dash='none', sw=1.6)
        s.block(x + 22, Y0 + 182, 240, 38, 'Fusion-CCU 段 SRAM', '≤ 16 字 · 块计数本地循环', 'ctlu', 12, 11, shadow=False)
        s.block(x + 22, Y0 + 234, 240, 38, '下一条指令寄存器 1,024 bit', 'LIC 直接装填，或由段 SRAM 搬入', 'ctlu', 12, 11, shadow=False)
        s.block(x + 22, Y0 + 286, 240, 26, '当前指令寄存器 1,024 bit', '', 'ctlu', 12, shadow=False)
        s.block(x + 290, Y0 + 182, 138, 130, '短消息 RF 队列', 'GO\n长度转发', 'ctlu', 13, 12, shadow=False)
        s.line([(x + 100, Y0 + 220), (x + 100, Y0 + 234)], 'ctlu', 2.0)          # 段 SRAM → 下一条
        s.line([(x + 100, Y0 + 272), (x + 100, Y0 + 286)], 'ctlu', 2.0)          # 下一条 → 当前
        s.text(x + 24, Y0 + 324, 'ready：下一条为空 / 段 SRAM 有空位 / 队列未满', 11, 'start', P['ctlu'][0], 700, box=g)
        s.text(x + 24, Y0 + 340, '↑ 位点完成 → LIC · 发出报告 → MAE', 12, 'start', P['ctrl'][0], 700, box=g)
        # 与 hub 控制道的六条单向链路
        s.line([(x + 100, Y0 + 130), (x + 100, Y0 + 114)], 'ctlu', 2.0)          # CCU → L1 发送侧（C2H 由 CCU 发令）
        s.line([(x + 215, 576), (x + 215, Y0 + 166)], 'ctrl', 2.2, dash=D, head=None, net=f'ccu{i}')   # hub → CCU
        s.line([(x + 140, Y0 + 166), (x + 359, Y0 + 166)], 'ctrl', 2.2, dash=D, head=None, net=f'ccu{i}')
        s.line([(x + 140, Y0 + 166), (x + 140, Y0 + 182)], 'ctrl', 2.2, dash=D, net=f'ccu{i}')        # Fusion 段 → 段 SRAM
        s.line([(x + 278, Y0 + 166), (x + 278, Y0 + 253), (x + 262, Y0 + 253)], 'ctrl', 2.2, dash=D, net=f'ccu{i}')   # 普通指令 → 下一条
        s.line([(x + 359, Y0 + 166), (x + 359, Y0 + 182)], 'ctrl', 2.2, dash=D, net=f'ccu{i}')        # 短消息 → 队列
        for xx in (215, 278):
            s.dot(x + xx, Y0 + 166, 'ctrl', 3.5)
        s.line([(x + 235, Y0 + 130), (x + 235, 576)], 'ctrl', 2.2, dash=D)         # CCU → hub
    # NI 控制道：IDN 搬运变长对象时向目的核 CCU 长度转发（右侧下行，经核下方分四支进短消息队列）
    TY = 1040
    s.line([(1890, 300), (1908, 300), (1908, TY), (X[0] + 400, TY)], 'ctrl', 2.2, dash=D, head=None, net='nilen')
    for i, x in enumerate(X):
        s.line([(x + 400, TY), (x + 400, Y0 + 312)], 'ctrl', 2.2, dash=D, net='nilen')
        if i:
            s.dot(x + 400, TY, 'ctrl', 3.5)
    s.tag(1100, 1060, 'NI 控制道：长度转发（IDN 搬运：段选 · 基址 · 应写量）→ 目的核 CCU 短消息队列', 'ctrl', 12)

    return s.save()


if __name__ == '__main__':
    bad = 0
    for f in (fig_links, fig_incore, fig_intercore, fig_ctrl):
        bad += len(f())
    sys.exit(1 if bad else 0)
