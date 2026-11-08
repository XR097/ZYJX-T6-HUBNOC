"""MAE 组四个单元篇的 PPT 式架构图（手写坐标，不用布线器）。Owner: WangYizhao · 2026-11-06
用法（在 docs/specs 目录下）：python -X utf8 -I _build/draw_mae_arch.py
输出（figs/）：
  FIG-MAE_NI_EXT-ARCH   NI_EXT：M0 / M1 主口、PIN 从口、跨域、宽度适配、窗口检查
  FIG-MAE_NI_INT-ARCH   NI_INT：指令执行与分路、读返回分路（六个目的口）、IDN 出口（一路 32 B）、NI-L2C 写客户（五源）/ 返回车道、NI 控制道
  HUB_IDN 架构图由 draw_hub_idn.py 生成。
  FIG-MAE_DSU-ARCH      MAE_DSU：两个入口、四种整形模式（含块尺度与旁带、hi 尺度复用）、两个出口
统一外圈（任务书 _build/MAE_CRU_MERGE_BRIEF_20261106.md §1 规则 11、§2 Agent D）：
  MAE 组框内五单元（MAE_ENG、NI_EXT、NI_INT、MAE_DSU、MAE_CRU；11-07 IDN 归 HUB 组，V18-HUB-01）：本单元展开画内部结构，
  其余四个画小框，与本单元直接往来的点亮、否则画灰；
  框外对端四张图位置相同（PEERS）：上 CIF / LIC / 命令网，左 DDR 控制器 P0 / SoC 片上互联 / 系统 DMA·FMC 从端，
  下 中央 L2 / HUB_IDN（到四核 NWB），右 H2C 道（11-07 晚撤 C2H 去 MAE_CRU 的分支，V18-CRU-07）；本单元不用的画灰、不连线。
  只画与本单元相连的线；线上只标名与位宽，说明在 _build/MAE_ARCH_CAPTIONS_20261106.md。
2026-11-08 晚（V18-HUB-04）：IDN 改为每核一条 32 B 链路；HUB_IDN 对端框改"一路 32 B → 按核集合分发 → 四核 NWB"，
  DSU 出口 → L1 改"经 HUB_IDN · 32 B"。
链路清单（每条线的依据节号）：_build/MAE_ARCH_LINKS_20261106.md。
图元与自检沿用 draw_tp_arch.py 的 Fig 类（复制一份，不 import，避免与协议篇脚本互相牵动）：
  文字不出画布、互不重叠、不压线、不跨色块边框；连线不穿色块；不同连线不共线；横竖交叉自动跳线弧。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / 'figs'
DATE = '2026-11-05'
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
# MAE 组统一外圈
# =====================================================================
DATE = '2026-11-08'
P['dim'] = ('#a3acb9', '#f1f3f6')       # 本单元不用：灰
P['focal'] = ('#334155', '#f5f9ff')     # 本单元展开框
DIMTXT = '#98a2b3'
D = '7,4'

# 组外对端（四张图相同）：key → (x, y, w, h, 标题, 用到时的副标题, 色)
PEERS = {
    'cif':   (520, 100, 280, 70, 'CIF', 'PIN 首个违规', 'ctlu'),
    'lic':   (860, 100, 300, 70, 'LIC', '指令入口 · 完成通知 · 直连口', 'ctlu'),
    'ctl':   (1220, 100, 280, 70, '命令网', 'hub 控制道 · 64 bit', 'ctrl'),
    'ddr':   (20, 330, 250, 80, 'DDR 控制器 P0', '256 bit 独占专线', 'ext'),
    'noc':   (20, 500, 250, 90, 'SoC 片上互联', 'HSRAM P2 · DDR P2 · FMC 主端', 'ext'),
    'dma':   (20, 690, 250, 80, '系统 DMA / FMC 从端', 'PIN 的写入方', 'ext'),
    'l2':    (560, 975, 420, 75, '中央 L2', 'NI 写口 32 B · NI 读口 4 × 32 B · 写入握手', 'mem'),
    'idn':   (1060, 975, 500, 75, 'HUB_IDN（入站分发网）', '一路 32 B → 按核集合分发 → 四核 NWB', 'hub'),
    'hubdn': (1660, 560, 240, 90, 'H2C 道', '道旁引擎给 L2 读地址', 'hub'),
}
GROUP = (300, 200, 1330, 740)           # MAE 组框


def dimblock(s, x, y, w, h, title, sub='本单元不用', size=16, subsize=12):
    """灰框：本单元不用的对端或同组单元（不连线）。"""
    stroke, fill = P['dim']
    s.layers['block'].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" '
                             f'stroke="{stroke}" stroke-width="1.6" stroke-dasharray="5,4"/>')
    rect = (x, y, x + w, y + h)
    s.blocks.append((rect, title))
    lines = sub.split('\n') if sub else []
    th = size + (len(lines) * (subsize + 5) + 4 if lines else 0)
    y0 = y + h / 2 - th / 2 + size / 2
    s._text(x + w / 2, y0, title, size, 'middle', DIMTXT, 700, box=rect)
    for i, t in enumerate(lines):
        s._text(x + w / 2, y0 + size / 2 + 4 + i * (subsize + 5) + subsize / 2 + 1, t, subsize, 'middle', DIMTXT, 500, box=rect)
    return rect


def frame(name, title, sub, uses, focal_title, focal_rect, ftx=None):
    s = Fig(name, title, sub)
    gx, gy, gw, gh = GROUP
    s.group(gx, gy, gw, gh, 'MAE 组 · 五单元（全芯片一组）', 'chip', 16, dash='none', sw=2.4, fill='#fbfcfe')
    for k, (x, y, w, h, t, st, kind) in PEERS.items():
        if k in uses:
            s.block(x, y, w, h, t, st, kind, 16, 12)
        else:
            dimblock(s, x, y, w, h, t)
    fx, fy, fw, fh = focal_rect
    s.group(fx, fy, fw, fh, focal_title, 'focal', 16, tx=ftx, dash='10,5', sw=2.2, fill=P['focal'][1])
    s.legend(20, 800, [('inter', '数据：握手写流 / SRAM 口', 'solid'), ('ctrl', '命令网 / 控制', D),
                       ('axi', '对外 AXI（M0 / M1 / PIN）', 'solid'), ('dim', '灰框 = 本单元不用', 'box')],
             cols=1, colw=232, size=13, rowh=27)
    return s


def member(s, x, y, w, h, title, sub, lit=True):
    if lit:
        return s.block(x, y, w, h, title, sub, 'ctlu' if title == 'MAE_ENG' else 'hub', 16, 12)
    return dimblock(s, x, y, w, h, title, '本单元不用' + (('\n' + sub) if sub else ''))


# =====================================================================
# FIG-MAE_NI_EXT-ARCH
# =====================================================================
def fig_ni_ext():
    s = frame('FIG-MAE_NI_EXT-ARCH.svg', 'FIG-MAE_NI_EXT-ARCH  NI_EXT：三个 AXI 口的协议端、地址换算、跨域、宽度适配与区间检查',
              'M0 / M1 由 MAE_ENG 发起，PIN 由片外主方发起；NI_EXT 只做协议转换、地址换算（头文件参数）、跨时钟、宽度适配与区间检查：不生成请求、不决定目的、不改数据',
              {'cif', 'ctl', 'ddr', 'noc', 'dma'}, 'NI_EXT（本单元）', (560, 225, 685, 605), ftx=1060)
    # ---- 同组单元 ----
    member(s, 1390, 330, 140, 100, 'MAE_ENG', '读写请求')
    member(s, 1390, 470, 220, 360, 'NI_INT', '读返回分路\nNI-L2C 写客户 / 返回车道\nNI 控制道')
    member(s, 600, 850, 200, 65, 'MAE_DSU', '', lit=False)
    member(s, 830, 850, 200, 65, 'MAE_CRU', '', lit=False)
    # ---- 内部 ----
    s.block(600, 260, 350, 75, 'PIN 地址换算 · 区间检查', 'A − A_PIN · 外设输入区（头文件参数，流片定死）\n区外 / FIXED / WRAP → 整笔 SLVERR · 记首个违规', 'ctlu', 15, 12, shadow=False)
    s.block(600, 355, 190, 80, 'M0 主口', 'AXI4 主 · 256 bit\n读 / 写在飞各 32 笔', 'ext', 16, 12, shadow=False)
    s.block(830, 355, 140, 80, '跨域', '同步 / 异步可选', 'ext', 15, 12, shadow=False)
    s.block(600, 495, 190, 105, 'M1 主口', 'AXI4 主 · 64 bit · f_IO\n32 B ↔ 4 拍 64 bit\n非对齐：按地址放字节', 'ext', 16, 12, shadow=False)
    s.block(830, 495, 140, 105, '跨域', '异步 FIFO\n任意时钟比率', 'ext', 15, 12, shadow=False)
    s.block(600, 670, 190, 120, 'PIN 从口', 'AXI4 从 · 64 bit · f_IO\n只收 INCR\n写在飞 ≥ 4 · 读 ≥ 2', 'ext', 16, 12, shadow=False)
    s.block(830, 670, 140, 120, '跨域', '异步 FIFO\n任意时钟比率', 'ext', 15, 12, shadow=False)
    s.block(1010, 355, 225, 245, '选口（M0 / M1）', '每笔 32 B 请求按选口位\n1 bit 选 M0 或 M1 · 默认 M0\nNPU 侧地址 → SoC 地址\n（按区，头文件参数）\n读返回交 NI_INT\n写响应交 MAE_ENG', 'hub', 16, 12, shadow=False)
    s.block(1010, 670, 225, 120, '拼字 · 字节使能', 'L2 地址 = A − A_PIN（线性）\n64 bit 拍拼 32 B 存储字\nWSTRB → be · 尾字随 WLAST 交出', 'hub', 16, 12, shadow=False)
    # 内部连线
    s.line([(790, 395), (830, 395)], 'axi', 2.2, head='both')
    s.line([(970, 395), (1010, 395)], 'axi', 2.2, head='both')
    s.line([(790, 547), (830, 547)], 'axi', 2.2, head='both')
    s.line([(970, 547), (1010, 547)], 'axi', 2.2, head='both')
    s.line([(790, 730), (830, 730)], 'axi', 2.2)
    s.line([(970, 730), (1010, 730)], 'axi', 2.2)
    s.line([(950, 300), (990, 300), (990, 690), (1010, 690)], 'ctlu', 2.0)          # 窗口表 → 地址换算（只合法写落地）
    # ---- 左侧三个 AXI 口 ----
    s.line([(600, 365), (270, 365)], 'axi', 3.2)
    s.tag(435, 350, 'AR · AW · W  256 bit', 'axi', 12)
    s.line([(270, 400), (600, 400)], 'axi', 3.2)
    s.tag(435, 385 + 32, 'R · B  256 bit', 'axi', 12)
    s.line([(600, 520), (270, 520)], 'axi', 2.6)
    s.tag(435, 505, 'M1：AR · AW · W  64 bit', 'axi', 12)
    s.line([(270, 570), (600, 570)], 'axi', 2.6)
    s.tag(435, 587, 'M1：R · B  64 bit', 'axi', 12)
    s.line([(270, 705), (600, 705)], 'axi', 2.6)
    s.tag(435, 690, 'PIN：AW · W · AR  64 bit', 'axi', 12)
    s.line([(600, 755), (270, 755)], 'axi', 2.6)
    s.tag(435, 772, 'PIN：B · R / SLVERR', 'axi', 12)
    # ---- 上方 CIF ----
    s.line([(760, 260), (760, 170)], 'ctrl', 2.2, dash=D)
    s.tag(768, 238, '首个违规', 'ctrl', 12, 'start')
    # ---- MAE_ENG ----
    s.line([(1390, 380), (1235, 380)], 'inter', 2.6)
    s.tag(1320, 365, '请求 32 B · 选口位', 'inter', 12)
    s.line([(1235, 415), (1390, 415)], 'ctrl', 2.2, dash=D)
    s.tag(1320, 400 + 32, '写响应', 'ctrl', 12)
    # ---- NI_INT ----
    s.line([(1235, 490), (1390, 490)], 'inter', 2.8)
    s.tag(1320, 475 - 0, '读返回 32 B', 'inter', 12)
    s.line([(1390, 540), (1235, 540)], 'inter', 2.8)
    s.tag(1320, 525, '写出数据 32 B', 'inter', 12)
    s.line([(1235, 585), (1390, 585)], 'ctrl', 2.2, dash=D)
    s.tag(1320, 570, '主口错误', 'ctrl', 12)
    s.line([(1235, 700), (1390, 700)], 'inter', 2.8)
    s.tag(1320, 685, 'PIN 存储字 32 B', 'inter', 12)
    s.line([(1390, 760), (1235, 760)], 'ctrl', 2.2, dash=D)
    s.tag(1320, 745, 'B 响应放行', 'ctrl', 12)
    # NI_INT → 命令网：主口错误经 NI 控制道转报 LIC
    s.line([(1580, 470), (1580, 188), (1480, 188), (1480, 170)], 'ctrl', 2.2, dash=D)
    s.tag(1572, 300, '主口错误转报', 'ctrl', 12, 'end')
    return s.save()


# =====================================================================
# FIG-MAE_NI_INT-ARCH
# =====================================================================
def fig_ni_int():
    s = frame('FIG-MAE_NI_INT-ARCH.svg', 'FIG-MAE_NI_INT-ARCH  NI_INT：引擎控制入口、读返回分路、NI-L2C、NI 控制道口',
              '不收指令，只收搬运引擎解码后的控制；读返回按读请求记录分到五个目的口；IDN 出口一路 32 B 交 HUB_IDN；NI 进出 L2 只经 NI-L2C（NI 读口 4 × 32 B、写口 32 B）',
              {'lic', 'ctl', 'l2', 'idn'}, 'NI_INT（本单元）', (590, 225, 672, 690), ftx=604)
    # ---- 同组单元 ----
    member(s, 320, 240, 210, 100, 'MAE_ENG', '搬运引擎')
    member(s, 320, 380, 170, 440, 'NI_EXT', 'M0 / M1 / PIN\n协议端')
    member(s, 1400, 395, 210, 205, 'MAE_DSU', '数据整形')
    member(s, 1400, 625, 210, 175, 'MAE_CRU', '数据合并')
    # ---- 内部 ----
    s.block(680, 260, 220, 90, '引擎控制入口', '读请求记录 · 通路选择\n长度转发内容（不是指令）', 'ctlu', 15, 12, shadow=False)
    s.block(960, 260, 290, 90, 'NI 控制道口', '64 bit 通用链路块\n长度转发 · 主口错误转报', 'ctrl', 15, 12, shadow=False)
    s.block(620, 400, 630, 95, '读返回分路（五个目的口）',
            'M0 / M1 读返回 32 B，按读请求记录 (去向, 目的地址) 分路，不设入站缓冲\n'
            '→ IDN 出口 · MAE_DSU · NI-L2C 写客户 · LIC 直连口 · NI_EXT 写通道', 'hub', 16, 12, shadow=False)
    s.block(620, 545, 280, 120, 'NI-L2C 写客户', '五源：M0 · M1 · PIN · DSU · CRU\n单位级合并 · 记来源与拍数\nPIN 记各象限项数 · 到齐放行 B', 'hub', 15, 12, shadow=False)
    s.block(620, 700, 250, 100, 'NI-L2C 返回车道', 'NI 读口 4 × 32 B（每象限一份）\nbusy 时保持 · 去 NI_EXT / DSU / CRU', 'hub', 15, 12, shadow=False)
    s.block(980, 830, 270, 70, 'IDN 出口 1 × 32 B', 'NI 分路 / MAE_DSU 择一（引擎定）', 'hub', 15, 12, shadow=False)
    # 内部连线
    s.line([(790, 350), (790, 400)], 'ctlu', 2.0)                         # 指令执行 → 分路：开路
    s.line([(900, 305), (960, 305)], 'ctlu', 2.0)                         # 指令执行 → 控制道：先发长度转发
    s.line([(755, 495), (755, 545)], 'inter', 2.6)                        # 分路 → 写客户（去 L2）
    s.line([(1150, 495), (1150, 830)], 'inter', 2.6)                      # 分路 → IDN 出口
    # ---- MAE_ENG ----
    s.line([(530, 280), (680, 280)], 'ctrl', 2.2, dash=D)
    s.tag(605, 266, '解码后的控制', 'ctrl', 12)
    s.line([(530, 325), (680, 325)], 'inter', 2.2)
    s.tag(605, 310, '逐拍 addr 24 · be', 'inter', 12)
    # ---- NI_EXT ----
    s.line([(490, 425), (620, 425)], 'inter', 2.8)
    s.tag(555, 410, '读返回 32 B', 'inter', 12)
    s.line([(620, 475), (490, 475)], 'inter', 2.6)
    s.tag(555, 460, '复制写出 32 B', 'inter', 12)
    s.line([(490, 570), (620, 570)], 'inter', 2.8)
    s.tag(555, 555, 'PIN 存储字 32 B', 'inter', 12)
    s.line([(620, 625), (490, 625)], 'ctrl', 2.2, dash=D)
    s.tag(555, 610, 'B 响应放行', 'ctrl', 12)
    s.line([(620, 750), (490, 750)], 'inter', 2.8)
    s.tag(555, 735, '写出数据 32 B', 'inter', 12)
    s.line([(490, 395), (560, 395), (560, 375), (1000, 375), (1000, 350)], 'ctrl', 2.2, dash=D)
    s.tag(631, 362, '主口错误', 'ctrl', 12)
    # ---- LIC / 命令网 ----
    s.line([(930, 400), (930, 170)], 'inter', 2.8)
    s.tag(938, 240, 'LIC 直连口 32 B', 'inter', 12, 'start')
    s.line([(1230, 260), (1230, 170)], 'ctrl', 2.2, dash=D)
    s.tag(1222, 240, 'NI 控制道 64 bit', 'ctrl', 12, 'end')
    # ---- MAE_DSU / MAE_CRU ----
    s.line([(1250, 425), (1400, 425)], 'inter', 2.6)
    s.tag(1325, 410, '整形输入 32 B', 'inter', 12)
    s.line([(1400, 585), (900, 585)], 'inter', 2.6)
    s.tag(1040, 570, '整形输出 → L2 32 B', 'inter', 12)
    s.line([(1400, 645), (900, 645)], 'inter', 2.6)
    s.tag(1040, 630, '合并结果 → L2 32 B', 'inter', 12)
    s.line([(870, 720), (1335, 720), (1335, 555), (1400, 555)], 'inter', 2.6)
    s.tag(1060, 705, '整形输入 32 B', 'inter', 12)
    s.line([(870, 775), (1400, 775)], 'inter', 2.6)
    s.tag(1060, 760, '读四象限 4 × 32 B', 'inter', 12)
    s.line([(1400, 520), (1290, 520), (1290, 865), (1250, 865)], 'inter', 2.4)   # MAE_DSU 整形输出（去 L1）→ IDN 出口
    s.tag(1298, 838, '整形 → IDN', 'inter', 11, 'start')
    # ---- HUB_IDN（组外对端，11-07 V18-HUB-01）----
    s.line([(1115, 900), (1115, 975)], 'inter', 2.8)
    s.tag(1123, 958, '32 B → HUB_IDN', 'inter', 12, 'start')
    # ---- 中央 L2 ----
    s.line([(890, 665), (890, 975)], 'inter', 3.0)                        # 写客户 → NI 写口
    s.tag(883, 685, 'NI 写口 32 B', 'inter', 12, 'end')
    s.line([(950, 975), (950, 610), (900, 610)], 'ctrl', 2.2, dash=D)     # L2 → 写客户：NI 写口各象限写入握手（valid + src，V18-TP-47）
    s.tag(957, 810, '写入握手 × 4 象限（带 src）', 'ctrl', 12, 'start')
    s.line([(640, 800), (640, 975)], 'inter', 2.4)                        # 返回车道 → L2：读 en / addr
    s.tag(648, 840, '读 en · addr', 'inter', 12, 'start')
    s.line([(800, 975), (800, 800)], 'inter', 3.0)                        # L2 → 返回车道：dout
    s.tag(793, 880, 'dout 4 × 32 B', 'inter', 12, 'end')
    return s.save()


# =====================================================================
# FIG-MAE_IDN-ARCH
# =====================================================================


# =====================================================================
# FIG-MAE_DSU-ARCH
# =====================================================================
def fig_dsu():
    # 11-06 晚（用户）：四种整形是同一条数据通路上的模式，不画成四个模块；只有一份暂存是要求存在的存储
    # 11-08（V18-MAE-35）：半字合并 → 按字重排（攒 n 行、2 × 128 B ping-pong 起）；暂存由按字重排与转置共用；控制只来自 MAE_ENG
    s = frame('FIG-MAE_DSU-ARCH.svg', 'FIG-MAE_DSU-ARCH  MAE_DSU：两个入口、一份暂存、一条整形数据通路、两个出口',
              '输入 DDR / L2 原形（都经 NI_INT），输出 L1（经 HUB_IDN）/ L2（经 NI-L2C 写客户），无片外出口；整形模式、几何、两侧地址与停发全部由 MAE_ENG 搬运引擎给出；与 MAE_CRU 并列、无往来',
              {'idn'}, 'MAE_DSU（本单元）', (620, 320, 710, 595), ftx=634)
    # ---- 同组单元 ----
    member(s, 900, 235, 300, 75, 'MAE_ENG', '搬运引擎：模式 · 几何 · 逐拍 addr（唯一控制源）')
    member(s, 330, 235, 200, 75, 'NI_EXT', '', lit=False)
    member(s, 320, 380, 160, 460, 'NI_INT', '读返回分路\nNI-L2C 返回车道\nNI-L2C 写客户')
    member(s, 1460, 760, 150, 100, 'MAE_CRU', '与 DSU 并列', lit=False)
    # ---- 内部 ----
    s.block(640, 400, 180, 80, 'DDR 原形入口', '32 B · addr · be', 'hub', 15, 12, shadow=False)
    s.block(640, 540, 180, 80, 'L2 原形入口', '32 B · addr · be', 'hub', 15, 12, shadow=False)
    s.block(640, 720, 180, 90, '出口 → NI-L2C', '去 L2 · 32 B\n三种模式的输出都可', 'hub', 15, 12, shadow=False)
    s.block(872, 400, 266, 100, '暂存（一份，共用）', '按字重排攒 n 行：≥ 2 × 128 B ping-pong\n转置攒一个子段：容量【设计者定】', 'comp', 15, 12, shadow=False)
    s.block(872, 540, 266, 340, '整形数据通路（一条）',
            '整形模式三选一（搬运引擎给）：\n按字重排：攒 n 行 → 各核整字\n转置：标准 / 列深度优先 → Wᵀ 列字\n两平面合并：hi 4 字 + lo 4 字\n= 128 B 记录，尺度行另落 S 类\n\n随转置：\n块尺度 e_max · Δ_m 与旁带行\n先 hi 后 lo，lo 用 hi 的尺度', 'comp', 15, 12, shadow=False)
    s.block(1190, 560, 130, 140, '出口 → L1', '经 HUB_IDN · 32 B\n整字 + 核集合\n含旁带行 · 全码记录', 'hub', 15, 12, shadow=False)
    # 内部连线
    s.line([(820, 440), (872, 440)], 'inter', 2.6)
    s.line([(820, 580), (872, 580)], 'inter', 2.6)
    s.line([(1005, 500), (1005, 540)], 'inter', 2.4)
    s.line([(872, 765), (820, 765)], 'inter', 2.6)
    s.line([(1138, 630), (1190, 630)], 'inter', 2.6)
    # ---- NI_INT ----
    s.line([(480, 440), (640, 440)], 'inter', 2.8)
    s.tag(560, 425, '整形输入 32 B', 'inter', 12)
    s.line([(480, 580), (640, 580)], 'inter', 2.8)
    s.tag(560, 565, '整形输入 32 B', 'inter', 12)
    s.line([(640, 765), (480, 765)], 'inter', 2.8)
    s.tag(560, 750, '整形输出 32 B', 'inter', 12)
    # ---- HUB_IDN（组外对端）----
    s.line([(1255, 700), (1255, 975)], 'inter', 2.8)
    s.tag(1263, 958, '32 B → HUB_IDN', 'inter', 12, 'start')
    # ---- MAE_ENG ----
    s.line([(1005, 310), (1005, 400)], 'ctrl', 2.2, dash=D)
    s.tag(1013, 365, '整形模式 · 几何 · 停发', 'ctrl', 12, 'start')
    s.line([(1180, 310), (1180, 530), (1255, 530), (1255, 560)], 'inter', 2.2)
    s.tag(1188, 385, '逐拍 addr · be', 'inter', 12, 'start')
    return s.save()

# =====================================================================
# FIG-MAE_ENG-ARCH（11-06 晚，协调者；正文 MAE_ENG.md §2）
# =====================================================================
def fig_eng():
    # 11-06 晚（用户）：框只画真实存在 / 共用的硬件；引擎执行一条指令的步骤不进图，写在正文 §7.1 的专项说明
    s = frame('FIG-MAE_ENG-ARCH.svg', 'FIG-MAE_ENG-ARCH  MAE_ENG：一种搬运引擎 × N，共用指令入口与 M0 / M1 请求仲裁',
              '只有搬运指令；每个引擎执行一条指令（地址生成、发出、运算级、比对、通知都是引擎自己做的事，见正文 §7.1）；引擎之外只有共用的指令入口与请求仲裁',
              {'lic', 'ctl', 'l2', 'hubdn', 'idn'}, 'MAE_ENG（本单元）', (560, 225, 790, 690), ftx=574)
    # ---- 同组单元 ----
    member(s, 320, 410, 150, 110, 'NI_EXT', 'M0 / M1 协议端')
    member(s, 320, 600, 150, 150, 'NI_INT', '分路 · NI-L2C\nNI 控制道')
    member(s, 1460, 390, 160, 70, 'MAE_DSU', '收模式 · addr')
    member(s, 1460, 480, 160, 80, 'MAE_CRU', '收参数 · 回完成')
    # ---- 共用：指令入口、请求仲裁 ----
    s.block(600, 280, 210, 100, '指令入口（两份）', '当前 / 下一 · ping-pong\nLIC 可连续下发多条\n各引擎从这里取指令', 'ctlu', 15, 12, shadow=False)
    s.block(600, 430, 210, 90, 'M0 / M1 请求仲裁', '各引擎共用两个 AXI 口\n优先级 + 老化', 'ctlu', 15, 12, shadow=False)
    # ---- 搬运引擎 × N：叠框（后两层只是示意多例化） ----
    for k in (2, 1):
        s.group(880 + 12 * k, 290 + 12 * k, 400, 330, '', 'ctlu', 14, strip=False, dash='none', sw=1.6, fill='#fffaf0')
    s.group(880, 290, 400, 330, '搬运引擎 × N（一种）', 'ctlu', 15, dash='none', sw=2.2, fill='#fffdf7')
    s.block(900, 340, 360, 190, '搬运引擎 i', '执行一条搬运指令\n口对 · 源 / 目的地址生成器 · 计数\n数量与链路数解耦【设计者定】\n执行内容见正文 §7.1', 'ctlu', 16, 12, shadow=False)
    s.block(900, 545, 360, 62, '在用列表缓存', '每引擎一份或共用【设计者定】', 'ctlu', 14, 12, shadow=False)
    # 共用资源 ↔ 引擎
    s.line([(810, 360), (900, 360)], 'ctlu', 2.0)                                  # 指令入口 → 引擎
    s.line([(900, 470), (810, 470)], 'ctlu', 2.0)                                  # 引擎 → 请求仲裁
    # ---- LIC ----
    s.line([(900, 170), (900, 264), (705, 264), (705, 280)], 'ctrl', 2.2, dash=D)
    s.tag(908, 205, '搬运指令 · 指令标号', 'ctrl', 12, 'start')
    s.line([(1140, 340), (1140, 170)], 'ctrl', 2.2, dash=D)
    s.tag(1148, 228, '完成通知 · 标号', 'ctrl', 12, 'start')
    # ---- 命令网 ----
    s.line([(1300, 170), (1300, 250), (1220, 250), (1220, 340)], 'ctrl', 2.2, dash=D, head='both')
    s.tag(1308, 205, '远端指令 · 长度转发 / 发出报告', 'ctrl', 12, 'start')
    # ---- NI_EXT ----
    s.line([(600, 450), (470, 450)], 'inter', 2.6)
    s.tag(535, 436, '请求 32 B', 'inter', 11)
    s.line([(470, 505), (580, 505), (580, 650), (1080, 650), (1080, 620)], 'ctrl', 2.0, dash=D)
    s.tag(525, 491, '写响应', 'ctrl', 11)
    # ---- NI_INT ----
    s.line([(900, 400), (845, 400), (845, 700), (470, 700)], 'inter', 2.6)
    s.tag(660, 686, '控制 · 逐拍 addr / be · 读请求记录', 'inter', 12)
    # ---- HUB_IDN（组外对端）/ DSU / CRU ----
    s.line([(1260, 335), (1415, 335), (1415, 975)], 'ctrl', 2.0, dash=D, head='both')
    s.tag(1423, 870, '核集合（随字）/ 握手', 'ctrl', 11, 'start')
    s.line([(1260, 425), (1460, 425)], 'inter', 2.2)
    s.line([(1260, 505), (1460, 505)], 'inter', 2.2, head='both')
    # ---- 中央 L2：写入握手（按发令号，经 NI_INT 转交）----
    s.line([(940, 975), (940, 620)], 'ctrl', 2.2, dash=D)
    s.tag(948, 870, 'L2 写入握手（按 src）', 'ctrl', 12, 'start')
    # ---- H2C 道：道旁引擎 ----
    s.line([(1260, 520), (1380, 520), (1380, 800), (1780, 800), (1780, 650)], 'inter', 2.4)
    s.tag(1430, 785, 'H2C：读 en · addr / 目的 addr · be / 核掩码', 'inter', 12, 'start')
    return s.save()

# =====================================================================
# FIG-MAE_CRU-ARCH（11-06 深夜，正文 MAE_CRU.md §2）
# =====================================================================
def fig_cru():
    # 11-07 晚（V18-CRU-07 / MAE-32）：CRU 只经 NI_INT 进出 L2——NI 读口一拍读四个象限同址（4 × 32 B）、合并、经 NI-L2C 写回 L2；
    # 撤 C2H 入口、CRU 存储 SRAM、按地址计数、H2C 出口、命令网端点。CRU 不与 MAE 组外直接相连，外圈全灰
    s = frame('FIG-MAE_CRU-ARCH.svg', 'FIG-MAE_CRU-ARCH  MAE_CRU：从 L2 读四份、合并、写回 L2',
              '输入 = NI 读口一拍读出的四个象限同址存储字（4 × 32 B，按象限掩码取份）；三种合并；输出 = 32 B 经 NI-L2C 写回 L2；由 MAE 收齐参与核的发出报告后启动；地址与停发由 MAE_ENG 控制',
              set(), 'MAE_CRU（本单元）', (600, 340, 940, 580), ftx=760)
    # ---- 同组单元 ----
    member(s, 700, 235, 380, 75, 'MAE_ENG', '合并参数 · 两侧逐拍 addr · 收合并完成')
    member(s, 330, 235, 200, 75, 'NI_EXT', '', lit=False)
    member(s, 1300, 235, 220, 75, 'MAE_DSU', '与 CRU 并列', lit=False)
    member(s, 320, 420, 200, 470, 'NI_INT', 'NI-L2C 返回车道\n（NI 读口 4 × 32 B）\n\nNI-L2C 写客户\n（NI 写口 32 B）')
    # ---- 内部 ----
    s.block(700, 440, 540, 110, '四份对齐（按象限掩码取份）', '一拍 4 × 32 B：四个象限的同一象限内地址各一份\n掩码外的象限不计入 · 份数 > 4 时另读 L2 其他地址累加【设计者定】', 'hub', 16, 12, shadow=False)
    s.block(700, 610, 540, 130, '合并（三种形态，加法次序按象限固定）', '部分和归约：BF16 逐元素求和（标准加法树）\n标量合并：求和 / 取最大 / (m, l) 对合并（FP32）\n读集合并：按位取并 · 并行 lane 数【设计者定】', 'comp', 16, 12, shadow=False)
    s.block(700, 800, 540, 70, '出口', '每拍 32 B（BF16 / FP32 / 位图）· 目的 addr 由引擎给 · 只写 L2', 'hub', 15, 12, shadow=False)
    s.line([(970, 550), (970, 610)], 'inter', 2.6)
    s.line([(970, 740), (970, 800)], 'inter', 2.6)
    # ---- NI_INT ----
    s.line([(520, 495), (700, 495)], 'inter', 3.0)
    s.tag(610, 478, '4 × 32 B', 'inter', 12)
    s.line([(700, 835), (520, 835)], 'inter', 2.8)
    s.tag(610, 818, '32 B → L2', 'inter', 12)
    # ---- MAE_ENG ----
    s.line([(680, 310), (680, 675), (700, 675)], 'ctrl', 2.2, dash=D, head='both')
    s.tag(688, 400, '参数 · addr / 完成', 'ctrl', 12, 'start')
    return s.save()


if __name__ == '__main__':
    bad = 0
    for f in (fig_ni_ext, fig_ni_int, fig_dsu, fig_eng, fig_cru):
        bad += len(f())
    sys.exit(1 if bad else 0)
