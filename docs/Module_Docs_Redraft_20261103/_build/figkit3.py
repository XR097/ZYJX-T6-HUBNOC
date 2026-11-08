"""figkit3：ISSCC 版式模块框图（沿用 isscc_v3 工具链的 router.py 自动布线 + build.py 版式，去掉口索引与引用校验）。
Owner: WangYizhao

- 坐标只描述框（14 px 网格），连线全部由 router.route 自动布线：自动选边、端口分槽、
  多宿一网（分支点 ●）、交叉数上限（默认 2，交叉处画桥）、标签在布线后自动放置且不压线不压框。
- 文字支持公式标记：_{..} 下标、^{..} 上标、~{..} 上加波浪号（不依赖组合字符）。
- 版式：框内居中粗体标题 + 副标题，浅色填充按 kind（function 浅绿 / memory 浅蓝 / control / external 浅灰），
  数据线黑色实线 3 px、控制线蓝色虚线、事件线蓝色虚线，底部图例与 Owner。

用法：
    from figkit3 import Figure
    f = Figure('NLU-CONN', '标题', width=1400, height=900, out_dir=Path(...))
    f.block('id', x, y, w, h, '标题', '副标题（可含 \\n 与公式标记）', kind='function')
    f.container('nlu', x, y, w, h, 'NLU')
    f.net('n1', 'src', 'dst' 或 ['d1','d2'], '标签', kind='data'|'ctrl'|'event')
    f.save()   # 写 out_dir/figs/FIG-<key>.svg，返回 (交叉数, 尝试号)
"""
from pathlib import Path
from html import escape
import re, math, sys, json
from PIL import ImageFont
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from router import route
from geometry import segments

STEP = 14
FONT_B = 'C:/Windows/Fonts/msyhbd.ttc'
NAVY, BLUE, INK = '#172b4d', '#466b89', '#1d2530'
FILLS = dict(compute='#fff0d2', memory='#e8eef4', control='#e5edf6', function='#e5f1ec', external='#f4f4f4', note='#ffffff')
DIM_FILL, DIM_LINE, DIM_TEXT = '#f7f8fa', '#b6bec9', '#9aa4b0'   # 本单元不用的对端（标灰）
_fonts = {}


def _font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT_B, size)
    return _fonts[size]


def snap(v):
    return round(v / STEP) * STEP


# ---------- 公式富文本 ----------
_TOKEN = re.compile(r'(_\{[^}]*\}|\^\{[^}]*\}|~\{[^}]*\})')


def parse_rich(s):
    runs = []
    for part in _TOKEN.split(s):
        if not part:
            continue
        if part.startswith('_{'):
            runs.append(('sub', part[2:-1]))
        elif part.startswith('^{'):
            runs.append(('sup', part[2:-1]))
        elif part.startswith('~{'):
            runs.append(('tilde', part[2:-1]))
        else:
            runs.append(('n', part))
    return runs


def measure(s, size):
    w = 0.0
    for kind, t in parse_rich(s):
        w += _font(round(size * 0.72) if kind in ('sub', 'sup') else size).getlength(t)
    return w


def rich_text(x, y, s, size, color=NAVY, anchor='middle'):
    """居中基线（dominant-baseline=central）的粗体富文本；返回 svg 片段。"""
    width = measure(s, size)
    left = x - width / 2 if anchor == 'middle' else x
    parts, extra, cx, pending = [], [], left, 0.0
    for kind, t in parse_rich(s):
        if kind in ('sub', 'sup'):
            sz = round(size * 0.72)
            shift = size * 0.30 if kind == 'sub' else -size * 0.40
            dy = pending + shift; pending = -shift
            parts.append(f'<tspan dy="{dy:.1f}" font-size="{sz}">{escape(t)}</tspan>')
            cx += _font(sz).getlength(t)
            continue
        dy = pending; pending = 0.0
        w = _font(size).getlength(t)
        parts.append(f'<tspan dy="{dy:.1f}">{escape(t)}</tspan>' if dy else escape(t))
        if kind == 'tilde':
            extra.append(f'<text x="{cx + w / 2:.1f}" y="{y - size * 0.62:.1f}" text-anchor="middle" dominant-baseline="central" '
                         f'font-family="Microsoft YaHei,Arial,sans-serif" font-size="{round(size * 0.95)}" font-weight="700" fill="{color}">~</text>')
        cx += w
    return (f'<text x="{left:.1f}" y="{y}" text-anchor="start" dominant-baseline="central" font-family="Microsoft YaHei,Arial,sans-serif" '
            f'font-size="{size}" font-weight="700" fill="{color}">{"".join(parts)}</text>' + ''.join(extra))


def wrap(s, width, size):
    lines = []
    for para in s.split('\n'):
        cur = ''
        for tok in re.findall(r'_\{[^}]*\}|\^\{[^}]*\}|~\{[^}]*\}|[A-Za-z][A-Za-z0-9_-]*|.', para):
            if cur and measure(cur + tok, size) > width and tok not in '，。；：！？、）)]}':
                lines.append(cur); cur = ''
            cur += tok
        lines.append(cur)
    return [l for l in lines if l != '' or len(lines) == 1]


# ---------- 图 ----------
class Figure:
    def __init__(self, key, title, width=1400, height=900, out_dir=None, max_crossings=2, attempts=24,
                 owner='Owner: WangYizhao', side_strategy='relative'):
        """side_strategy：'relative' 按相对位置选边（多数图够用）；'visibility' 按可见路径打分选边（框互相遮挡时用）。"""
        self.out_dir = Path(out_dir) if out_dir else HERE.parent
        self.owner = owner
        self.d = dict(id='FIG-' + key, title=title, width=width, height=height, blocks=[], containers=[], nets=[],
                      max_crossings=max_crossings, attempts=attempts, save_diagnostic=True,
                      side_strategy=side_strategy, allow_complex_visibility=True, multisink_search=True)

    def block(self, id, x, y, w, h, title, subtitle='', kind='function', **extra):
        self.d['blocks'].append(dict(id=id, rect=list(map(snap, (x, y, w, h))), title=title, subtitle=subtitle, kind=kind, **extra))

    def container(self, id, x, y, w, h, title, dashed=True):
        self.d['containers'].append(dict(id=id, rect=list(map(snap, (x, y, w, h))), title=title, dashed=dashed))

    def net(self, id, src, dst, label, kind='data', **extra):
        dsts = dst if isinstance(dst, list) else [dst]
        self.d['nets'].append(dict(net_id=id, src=dict(block=src, side='auto'), dsts=[dict(block=e, side='auto') for e in dsts],
                                   label=label, kind=kind, role='hardware', **extra))

    # 版式沿用 build.py 的 svg()，文字改为富文本
    def _svg(self, m):
        W, H = m['width'], m['height']; out = []
        out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
        out.append('<defs><marker id="ad" markerWidth="8" markerHeight="7" refX="7" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7Z" fill="' + INK + '"/></marker>'
                   '<marker id="ac" markerWidth="8" markerHeight="7" refX="7" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7Z" fill="' + BLUE + '"/></marker></defs>'
                   '<rect width="100%" height="100%" fill="white"/>')
        out.append(rich_text(28, 34, m['title'], 27, anchor='start'))
        for c in m.get('containers', []):
            x, y, w, h = c['rect']; dash = ' stroke-dasharray="9 6"' if c.get('dashed', True) else ''
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{NAVY}" stroke-width="2.2"{dash}/>')
            out.append(rich_text(x + 14, y + 22, c['title'], 22, anchor='start'))
        for b in m['blocks']:
            x, y, w, h = b['rect']
            # dim=True：组的对端里本单元不用的，画灰（用户 11-05：各组连接图画出全部对端，不需要的标灰）
            dim = b.get('dim', False)
            fill = DIM_FILL if dim else FILLS[b['kind']]
            stroke = f'stroke="{DIM_LINE}" stroke-width="2" stroke-dasharray="7 5"' if dim else f'stroke="{NAVY}" stroke-width="2.6"'
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" {stroke}/>')
            lines = [(s, 21) for s in wrap(b['title'], w - 20, 21)] + [(s, 17) for s in wrap(b.get('subtitle', ''), w - 20, 17) if s]
            total = sum(sz * 1.4 for s, sz in lines); yy = y + (h - total) / 2
            for s, sz in lines:
                yy += sz * .7; out.append(rich_text(x + w / 2, yy, s, sz, DIM_TEXT if dim else NAVY)); yy += sz * .7
        for n in m['nets']:
            col = INK if n['kind'] == 'data' else BLUE
            dash = '' if n['kind'] == 'data' else ' stroke-dasharray="9 6"'; stroke = 3 if n['kind'] == 'data' else 2.3
            unique = set()
            for path in n['paths']:
                for a, b in segments(path):
                    unique.add(tuple(sorted((tuple(a), tuple(b)))))
            for a, b in unique:
                out.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" fill="none" stroke="{col}" stroke-width="{stroke}"{dash}/>')
            for path in n['paths']:
                a, b = path[-2:]; dx = b[0] - a[0]; dy = b[1] - a[1]; L = max(abs(dx), abs(dy)); s = (b[0] - dx / L * 12, b[1] - dy / L * 12)
                out.append(f'<path d="M{s[0]},{s[1]} L{b[0]},{b[1]}" stroke="{col}" stroke-width="{stroke}" marker-end="url(#{"ad" if n["kind"] == "data" else "ac"})"/>')
            for x, y in n['junctions']:
                out.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{col}"/>')
        for cr in m['crossings']:
            choices = [n for n in m['nets'] if n['net_id'] in cr['nets']]; n = next((n for n in choices if n['kind'] == 'data'), choices[0])
            x, y = cr['point']; col = INK if n['kind'] == 'data' else BLUE
            horizontal = any(a[1] == b[1] == y and min(a[0], b[0]) < x < max(a[0], b[0]) for p in n['paths'] for a, b in segments(p))
            d = f'M{x-6},{y} A6,6 0 0 1 {x+6},{y}' if horizontal else f'M{x},{y-6} A6,6 0 0 1 {x},{y+6}'
            out.append(f'<circle cx="{x}" cy="{y}" r="6" fill="white"/><path d="{d}" stroke="{col}" fill="none" stroke-width="3"/>')
        for n in m['nets']:
            endpoints = {tuple(n['paths'][0][0])} | {tuple(p[-1]) for p in n['paths']}
            for x, y in endpoints:
                out.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{INK if n["kind"] == "data" else BLUE}"/>')
            if not n['label']:
                continue
            l = n['label_box']; x, y, w, h = l['rect']
            if l.get('leader'):
                a, b = l['leader']; out.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="#777" stroke-width="1" stroke-dasharray="2 2" fill="none"/>')
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="white"/>')
            col = INK if n['kind'] == 'data' else BLUE
            if l['rotate']:
                out.append(f'<g transform="rotate({l["rotate"]} {l["x"]} {l["y"]})">' + rich_text(l['x'], l['y'], n['label'], 17, col) + '</g>')
            else:
                out.append(rich_text(l['x'], l['y'], n['label'], 17, col))
        kinds = {n['kind'] for n in m['nets']}
        legend = '　'.join((['━━ 主要数据'] if 'data' in kinds else []) + (['┄ 控制 / 事件'] if kinds & {'ctrl','event'} else []) + (['● 同网分支'] if any(n.get('junctions') for n in m['nets']) else []))
        if legend:
            out.append(rich_text(70, H - 28, legend, 16, anchor='start'))
        out.append(rich_text(W - 300, H - 28, self.owner, 15, anchor='start'))
        out.append('</svg>')
        return '\n'.join(out)

    def save(self):
        m = self.d
        routed, xs, attempt = route(m, measure, m.get('attempts', 24))
        m['nets'] = routed; m['crossings'] = xs
        (self.out_dir / 'figs').mkdir(parents=True, exist_ok=True)
        (self.out_dir / 'figs' / f'{m["id"]}.svg').write_bytes(self._svg(m).replace('\r\n', '\n').encode('utf-8'))
        return len(xs), attempt
