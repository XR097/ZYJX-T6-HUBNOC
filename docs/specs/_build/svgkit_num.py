"""小矩阵数值图的手写 SVG 工具（ISSCC 版式配色，富文本上下标，越界自检）。Owner: WangYizhao
由 draw_mxu_arch.py 的 Svg 类抽出，供 10-30 新增的数值图脚本共用（draw_grad_uni.py、draw_mxu_attn_exact.py、
draw_mxu_expfold.py、draw_l1_trainwin.py 等）。不走布线器；连线手给坐标。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / 'figs'
NAVY = '#172b4d'
INK = '#1d2530'
GREY = '#8a94a6'
RED = '#b42318'
CTRL = '#2f5d8a'
FONT = 'Microsoft YaHei,Arial,sans-serif'
C_HI = '#f8d3c9'      # hi 数字 / hi 道
C_LO = '#d3e3f6'      # lo 数字 / lo 道
C_KEEP = '#cfe8c6'    # 保留 / 结果
C_OFF = '#eef0f3'     # 空 / 未用
C_LEFT = '#f9e3a6'    # 停放 / 余下
C_W = '#fdf1c7'       # 权重
C_ACC = '#e4dcf3'     # F1b / 累加
C_SIDE = '#fff0d2'    # 旁带 / 尺度字段
C_BOX = '#e8eef7'     # 部件框
CLS = {-6: '#d6e6f7', -7: '#dcefd2', -8: '#fde3c4', -5: '#f3d9ef', -9: '#e9e2c9'}   # 尺度指数着色


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.out, self.texts = w, h, [], []
        self.out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">')
        self.out.append('<defs>'
                        f'<marker id="ad" markerWidth="8" markerHeight="7" refX="7" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7Z" fill="{INK}"/></marker>'
                        f'<marker id="ar" markerWidth="8" markerHeight="7" refX="7" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7Z" fill="{RED}"/></marker>'
                        f'<marker id="ac" markerWidth="8" markerHeight="7" refX="7" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7Z" fill="{CTRL}"/></marker>'
                        '</defs><rect width="100%" height="100%" fill="white"/>')

    def rich(self, x, y, s, size=16, anchor='start', color=NAVY, weight=700):
        # 支持 ^{..} 上标与 _{..} 下标
        self.texts.append((x, y, s, size, anchor))
        s = str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        parts = re.split(r'(\^\{[^}]*\}|_\{[^}]*\})', s)
        spans, shift = [], 0
        for p in parts:
            if not p:
                continue
            if p.startswith('^{') or p.startswith('_{'):
                d = -0.38 * size if p[0] == '^' else 0.25 * size
                spans.append(f'<tspan dy="{d - shift:.1f}" font-size="{size * 0.68:.0f}">{p[2:-1]}</tspan>')
                shift = d
            else:
                spans.append(f'<tspan dy="{-shift:.1f}">{p}</tspan>')
                shift = 0
        self.out.append(f'<text xml:space="preserve" x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="central" '
                        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color}">{"".join(spans)}</text>')

    def note(self, x, y, s, size=15):
        self.rich(x, y, s, size, 'start', INK, 500)

    def red(self, x, y, s, size=15, anchor='start'):
        self.rich(x, y, s, size, anchor, RED, 600)

    def rect(self, x, y, w, h, fill='white', sw=1.4, rx=2, dash=None, stroke=NAVY):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def cell(self, x, y, w, h, s, fill='white', size=15, color=INK, weight=600, sw=1.2, dash=None, stroke=NAVY):
        self.rect(x, y, w, h, fill=fill, sw=sw, dash=dash, stroke=stroke)
        self.rich(x + w / 2, y + h / 2, s, size, 'middle', color, weight)

    def line(self, pts, color=INK, sw=1.8, marker='ad', dash=None):
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        m = f' marker-end="url(#{marker})"' if marker else ''
        ds = f' stroke-dasharray="{dash}"' if dash else ''
        self.out.append(f'<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="none"{m}{ds}/>')

    def ctrl(self, pts):
        self.line(pts, color=CTRL, sw=1.8, marker='ac', dash='6,4')

    def panel(self, x, y, w, h, title, size=18):
        self.rect(x, y, w, h, fill='white', sw=2.2, rx=6)
        self.rich(x + 14, y + 24, title, size)

    def check_fit(self):
        # 粗估文字宽度（CJK 按 1 个字号、其余按 0.55 个字号，上下标按 0.68 倍），不得越出画布
        for x, y, s, size, anchor in self.texts:
            plain = re.sub(r'[\^_]\{([^}]*)\}', lambda m: '\x00' * len(m.group(1)), str(s))
            wid = sum((0.68 * 0.55 * size) if ch == '\x00' else (size if ord(ch) > 0x2E80 else 0.55 * size) for ch in plain)
            left = x - (wid if anchor == 'end' else wid / 2 if anchor == 'middle' else 0)
            assert left >= 0 and left + wid <= self.w - 10, (s, round(left), round(wid))

    def save(self, name, date='2026-10-30'):
        self.check_fit()
        self.rich(self.w - 24, self.h - 12, f'Owner: WangYizhao · {date}', 13, 'end', GREY, 500)
        self.out.append('</svg>')
        FIGS.mkdir(parents=True, exist_ok=True)
        (FIGS / name).write_text('\n'.join(self.out), encoding='utf-8')
        print('wrote', name)


def frac(v):
    """Fraction → 'p/q' 或整数串。"""
    return str(v.numerator) if v.denominator == 1 else f'{v.numerator}/{v.denominator}'
