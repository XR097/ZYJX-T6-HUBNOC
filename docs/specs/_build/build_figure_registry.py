"""图件登记表生成器：图 ↔ 生图脚本 / 函数 ↔ 文档位置。Owner: WangYizhao · 2026-11-05
用户 11-05："我希望这个关系你对于其他文档，也都要记录，相当于维护一个全局的项目记忆"。

用法：python -X utf8 -I build_figure_registry.py <根目录> [<根目录> ...]
对每个根目录：
  - 递归找 *.md，抽取 ![...](...figs/FIG-xxx.svg) 引用，记下文件、最近的标题；
  - 递归找 _build/*.py（含 draw_*.py 等），按 "def 函数名" 分块，块内出现的 FIG-xxx（save('FIG-xxx.svg')、
    Figure('xxx', ...)、Fig('FIG-xxx.svg', ...) 三种写法）记为该函数产出；
  - 列出 figs/ 下实际存在的 SVG；
  - 写 <根目录>/_build/FIGURE_REGISTRY.md：按文档分节，每图一行（图、函数、脚本、所在节）；末尾列"无人引用的图"
    与"被引用但不存在的图"。
本表只做自动索引；脚本依赖和检查局限见 _build/README.md。默认扫描本脚本所在的 docs/specs。
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

RE_IMG = re.compile(r'!\[[^\]]*\]\(([^)]*?)(FIG-[A-Za-z0-9_\-\.]+?)\.svg\)')
RE_HEAD = re.compile(r'^(#{1,4})\s+(.*)$')
RE_DEF = re.compile(r'^def\s+(\w+)\s*\(')
RE_FIG = [
    re.compile(r"save\(\s*['\"](FIG-[A-Za-z0-9_\-\.]+?)\.svg['\"]"),
    re.compile(r"\bFig\(\s*['\"](FIG-[A-Za-z0-9_\-\.]+?)\.svg['\"]"),
    re.compile(r"\bFigure\(\s*['\"]([A-Za-z0-9_\-\.]+?)['\"]"),
    re.compile(r"['\"](FIG-[A-Za-z0-9_\-\.]+?)\.svg['\"]"),      # 兜底：函数体内任何 'FIG-xxx.svg' 字面量（如经辅助函数转交文件名）
]


def scan_md(root: Path):
    refs = defaultdict(list)          # fig -> [(md 相对路径, 标题)]
    for md in sorted(root.rglob('*.md')):
        if '_build' in md.parts or '_retired' in str(md):
            continue
        head = ''
        try:
            lines = md.read_text(encoding='utf-8').splitlines()
        except UnicodeDecodeError:
            continue
        for ln in lines:
            m = RE_HEAD.match(ln)
            if m:
                head = m.group(2).strip()
                continue
            for im in RE_IMG.finditer(ln):
                refs[im.group(2)].append((md.relative_to(root).as_posix(), head))
    return refs


def scan_py(root: Path):
    funcs = defaultdict(list)         # fig -> [(py 相对路径, 函数名)]
    for py in sorted(root.rglob('*.py')):
        if '_build' not in py.parts:
            continue
        try:
            text = py.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        cur = '(模块级)'
        for ln in text.splitlines():
            m = RE_DEF.match(ln)
            if m:
                cur = m.group(1)
            if cur.startswith('_retired_'):      # 退役的旧生图函数不登记
                continue
            for rx in RE_FIG:
                for fm in rx.finditer(ln):
                    fid = fm.group(1)
                    if not fid.startswith('FIG-'):
                        fid = 'FIG-' + fid
                    rel = py.relative_to(root).as_posix()
                    if (rel, cur) not in funcs[fid]:
                        funcs[fid].append((rel, cur))
    return funcs


def existing(root: Path):
    out = set()
    for d in root.rglob('figs'):
        if d.is_dir() and '_retired' not in str(d):
            out |= {p.stem for p in d.glob('FIG-*.svg')}
    return out


def build(root: Path):
    refs, funcs, have = scan_md(root), scan_py(root), existing(root)
    by_doc = defaultdict(list)
    for fid, places in refs.items():
        for md, head in places:
            by_doc[md].append((fid, head))
    lines = [f'# 图件登记表（自动生成）：{root.name}', '',
             f'> 由 `_build/build_figure_registry.py` 扫描生成，不要手改；工具说明见 `_build/README.md`。'
             f'扫描范围：本目录下全部 *.md（图引用）与 _build/*.py（生图函数）。', '']
    for md in sorted(by_doc):
        lines += [f'## {md}', '', '| 图 | 所在节 | 生图函数 | 脚本 | SVG 存在 |', '|---|---|---|---|---|']
        seen = set()
        for fid, head in by_doc[md]:
            if fid in seen:
                continue
            seen.add(fid)
            fl = funcs.get(fid, [])
            fn = '；'.join(f'`{f}()`' for _, f in fl) or '—（未找到生图函数）'
            sc = '；'.join(f'`{p}`' for p, _ in fl) or '—'
            lines.append(f'| {fid} | {head} | {fn} | {sc} | {"✓" if fid in have else "✗ 缺文件"} |')
        lines.append('')
    unref = sorted(have - set(refs))
    missing = sorted(set(refs) - have)
    nofunc = sorted(f for f in refs if f not in funcs)
    lines += ['## 核对', '',
              f'- 有 SVG 但无文档引用（{len(unref)}）：' + ('、'.join(unref) if unref else '无'),
              f'- 被引用但 SVG 不存在（{len(missing)}）：' + ('、'.join(missing) if missing else '无'),
              f'- 被引用但找不到生图函数（{len(nofunc)}）：' + ('、'.join(nofunc) if nofunc else '无'), '']
    out = root / '_build' / 'FIGURE_REGISTRY.md'
    out.parent.mkdir(exist_ok=True)
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f'{out}: {len(refs)} referenced figures, {len(have)} svg files, {len(funcs)} figure ids in scripts')


if __name__ == '__main__':
    for arg in sys.argv[1:] or [Path(__file__).resolve().parent.parent]:
        build(Path(arg).resolve())
