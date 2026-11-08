"""V1.7 阶段 3 F5 组图件的出图收尾（不改 figkit3 / svgkit_num 本体）。Owner: WangYizhao · 2026-11-02
按 TEMPLATE_FIGURES_V17.md：图内不写长标题、不写 Owner；图例只列本图用到的线型。
- finalize(f, crop=True)：figkit3 Figure.save() 之后调用。删去空标题与 Owner，按本图实际用到的
  线型重写图例（无连线时删去图例），并把画布顶部空带裁掉（框与容器的最上沿以上留 28 px）。
- SvgF5：svgkit_num.Svg 的子类，save() 不写 Owner，其余不变（越界自检照旧）。
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit_num import Svg, FIGS  # noqa: E402

LEGEND_OLD = '━━ 主要数据　┄ 控制 / 事件　● 同网分支'


def finalize(f, crop=True):
    d = f.d
    p = f.out_dir / 'figs' / f'{d["id"]}.svg'
    s = p.read_text(encoding='utf-8')
    # Owner 文字（figkit3 写在右下）
    s = re.sub(r'<text[^>]*>' + re.escape(f.owner) + r'</text>', '', s)
    # 空标题
    s = re.sub(r'<text x="28(?:\.0)?" y="34"[^>]*></text>', '', s)
    # 图例：只列用到的线型
    kinds = {n['kind'] for n in d['nets']}
    has_branch = any(n.get('junctions') for n in d['nets'])
    parts = []
    if 'data' in kinds:
        parts.append('━━ 数据')
    if kinds & {'ctrl', 'event'}:
        parts.append('┄ 控制 / 事件')
    if has_branch:
        parts.append('● 同网分支')
    if parts:
        s = s.replace(LEGEND_OLD, '　'.join(parts))
    else:
        s = re.sub(r'<text[^>]*>' + re.escape(LEGEND_OLD) + r'</text>', '', s)
    if crop:
        tops = [b['rect'][1] for b in d['blocks']] + [c['rect'][1] for c in d.get('containers', [])]
        top = max(0, min(tops) - 28)
        W, H = d['width'], d['height']
        if top > 0:
            s = s.replace(f'width="{W}" height="{H}" viewBox="0 0 {W} {H}"',
                          f'width="{W}" height="{H - top}" viewBox="0 {top} {W} {H - top}"', 1)
            # 白底跟着上移
            s = s.replace('<rect width="100%" height="100%" fill="white"/>',
                          f'<rect x="0" y="{top}" width="{W}" height="{H - top}" fill="white"/>', 1)
    p.write_bytes(s.replace('\r\n', '\n').encode('utf-8'))


class SvgF5(Svg):
    def save(self, name, date=None):
        self.check_fit()
        self.out.append('</svg>')
        FIGS.mkdir(parents=True, exist_ok=True)
        (FIGS / name).write_bytes(('\n'.join(self.out)+'\n').encode('utf-8'))
        print('wrote', name)
