# -*- coding: utf-8 -*-
"""把各正式稿标题下的修订注记、依据与历史说明搬进一份修改日志，正文头部只留一行 Owner + 日期（用户 11-08）。
Owner: WangYizhao · 2026-11-08。一次性脚本；跑前已整目录备份 _backup_20261108d_headers_Module_Docs_Redraft/。
用法（在 Module_Docs_Redraft_20261103 下）：python -X utf8 -I _build/move_headers_to_changelog_20261108.py
规则：
  - 头部 = 标题行之后、第一个 '## ' 之前的所有 '>' 行；全部搬进日志（例外见 KEEP_Q：是内容不是历史，转成普通段落留在正文）。
  - 头部里的普通段落保留（例外见 MOVE_B：历史说明，搬进日志）。
  - DATA_ORGANIZATION.md 的 '## 0 本底稿与目录稿的对应' 一节同样搬进日志。
  - 新头部：'> Owner: WangYizhao｜2026-11-dd'，dd = 搬走的注记里出现的最晚日期。
  - 日志按文档分章；每章先给"按节索引"（节号 → 条目号），再按时间列条目，条目原文照搬。
    节号取注记里本篇的节号（"X 篇 §…"一串属别的文档，不计）；协议篇 11-08 切分前的注记用旧号，索引里换成新号。
"""
import io
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from split_protocol_20261108 import remap_num  # noqa: E402

LOG = ROOT / 'CHANGELOG_FORMAL_DOCS.md'

CODE = {
    'ONCHIP_DATAPATH_ARCH.md': ('ARCH', '片上数据通路架构（架构篇）'),
    'DATA_TRANSFER_PROTOCOL.md': ('TP', '片上数据传输协议（协议篇）'),
    'DATA_ORGANIZATION.md': ('DORG', '片上数据组织（数据组织篇，底稿）'),
    'L1_SRAM.md': ('L1', 'L1 SRAM'),
    'L2_SRAM.md': ('L2', 'L2 SRAM'),
    'HUB_NOC.md': ('NOC', 'HUB_NOC'),
    'HUB_IDN.md': ('IDN', 'HUB_IDN'),
    'MAE_INTEGRATION.md': ('MINT', 'MAE 集成篇'),
    'MAE_ENG.md': ('ENG', 'MAE_ENG'),
    'MAE_NI_EXT.md': ('NIE', 'MAE_NI_EXT'),
    'MAE_NI_INT.md': ('NII', 'MAE_NI_INT'),
    'MAE_DSU.md': ('DSU', 'MAE_DSU'),
    'MAE_CRU.md': ('CRU', 'MAE_CRU'),
    'VNU_NLU.md': ('NLU', 'VNU_NLU'),
    'VNU_QNT.md': ('QNT', 'VNU_QNT'),
    'VNU_SEL.md': ('SEL', 'VNU_SEL'),
    'VNU_LOSS.md': ('LOSS', 'VNU_LOSS'),
    'VNU_OPT.md': ('OPT', 'VNU_OPT'),
    'L3PU_EXTERNAL_INFORMATION.md': ('INFO', '外部输入信息'),
}
KEEP_Q = {('ONCHIP_DATAPATH_ARCH.md', '> **本篇回答'), ('VNU_OPT.md', '> 用户 11-04："最大程度放权')}
MOVE_B = {('HUB_NOC.md', '旧稿 `V17_3_MODULE_TOC_HUB_NOC')}

DATE = re.compile(r'(?:2026-)?1([01])-(\d\d)')
XDOC = re.compile(r'[^\s（(，、；：]*篇 §\d+(?:\.\d+)*[a-z]?(?:(?: / |、| 与 | 和 |–|—)§\d+(?:\.\d+)*[a-z]?)*')
SEC = re.compile(r'§(\d+(?:\.\d+)*)([a-z]?)(?:\s*[–—]\s*§?(\d+(?:\.\d+)*)([a-z]?))?')


def day_of(text):
    ds = [(int(m.group(1)), int(m.group(2))) for m in DATE.finditer(text)]
    return max(ds) if ds else None


def lead_day(text):
    m = DATE.search(text[:40])
    return (int(m.group(1)), int(m.group(2))) if m else None


def phase(text):
    m = DATE.search(text[:40])
    rest = text[m.end():m.end() + 4] if m else ''
    rest = rest.lstrip()
    for k, r in (('深夜', 3), ('夜', 2), ('晚', 1)):
        if rest.startswith(k):
            return r
    return 0


def expand(a, sa, b, sb):
    if not b:
        return [a + sa]
    pa, pb = a.split('.'), b.split('.')
    if len(pa) == len(pb) and pa[:-1] == pb[:-1] and not sa and not sb:
        lo, hi = int(pa[-1]), int(pb[-1])
        if 0 <= hi - lo <= 12:
            pre = '.'.join(pa[:-1])
            return [(pre + '.' if pre else '') + str(i) for i in range(lo, hi + 1)]
    return [a + sa, b + sb]


GROUP = re.compile(r'（(§[^（）]*)）')


def scope_of(text):
    """注记里"本篇改了哪些节"的那一段：优先取最后一个以 § 开头的全角括号（注记惯例"（§1.1、§2、…）"）；
    清晰度遍历一类写"改写了 §x（…）、§y …"，取"改写了"之后的文字；都没有 = 全篇（例如"依据"一类，里面的 § 是别的文档的节）。"""
    gs = GROUP.findall(text)
    if gs:
        return gs[-1]
    k = text.find('改写了')
    if k >= 0:
        return re.sub(r'（[^（）]*）', '', text[k:])
    return ''


def sections(fname, text, old_tp):
    t = XDOC.sub('', scope_of(text))
    out = []
    for m in SEC.finditer(t):
        for s in expand(m.group(1), m.group(2), m.group(3), m.group(4)):
            if old_tp:
                num = re.match(r'(\d+)((?:\.\d+)*)([a-z]?)$', s)
                top = int(num.group(1))
                try:
                    nt, nr, dorg = remap_num(top, num.group(2))
                except KeyError:
                    continue
                s = (f'数据组织篇 §{nt}{nr}{num.group(3)}' if dorg else f'§{nt}{nr}{num.group(3)}')
            else:
                s = '§' + s
            if s not in out:
                out.append(s)
    return out


def sec_key(s):
    if s.startswith('数据组织篇'):
        return (1, [])
    nums = re.findall(r'\d+', s)
    return (0, [int(x) for x in nums], s)


def main():
    docs = []
    for p in sorted(ROOT.glob('*.md')):
        if p.name not in CODE:
            if p.name != LOG.name:
                print('skip (no code):', p.name)
            continue
        L = io.open(p, encoding='utf-8').read().split('\n')
        assert L[0].startswith('# '), p.name
        end = next(i for i, l in enumerate(L) if l.startswith('## '))
        moved, kept = [], []
        for i in range(1, end):
            l = L[i]
            if not l.strip() or l.strip() == '>':
                continue
            if l.startswith('>'):
                if any(p.name == f and l.startswith(pre) for f, pre in KEEP_Q):
                    kept.append(l[1:].lstrip())
                else:
                    moved.append(l[1:].lstrip())
            else:
                if any(p.name == f and l.startswith(pre) for f, pre in MOVE_B):
                    moved.append(l)
                else:
                    kept.append(l)
        rest = L[end:]
        # 数据组织篇底稿的 §0 对照节
        if p.name == 'DATA_ORGANIZATION.md' and rest[0].startswith('## 0 '):
            j = next(k for k in range(1, len(rest)) if rest[k].startswith('## '))
            rows = [r for r in rest[1:j] if r.startswith('| ') and not r.startswith('| 目录稿') and not r.startswith('|---')]
            pairs = [tuple(c.strip() for c in r.strip('|').split('|')) for r in rows]
            moved.append('底稿与目录稿第二版（`../V17_3_MODULE_TOC_DATA_ORG_20261108.md`）的对应：' +
                         '；'.join(f'目录{a} ← 底稿 {b}' for a, b in pairs) + '。')
            rest = rest[j:]
        ds = [d for d in (day_of(x) for x in moved) if d]
        last = max(ds) if ds else (11, 8)
        head = [L[0], '', f'> Owner: WangYizhao｜2026-{last[0] + 10:02d}-{last[1]:02d}', '']
        for k in kept:
            head += [k, '']
        io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(head + rest))
        docs.append((p.name, moved))

    order = list(CODE)
    docs.sort(key=lambda d: order.index(d[0]))
    md = ['# 正式稿修改日志', '',
          '> Owner: WangYizhao｜2026-11-08', '',
          '各正式稿（`Module_Docs_Redraft_20261103/` 下的人类可读正文）标题下原有的修订注记、依据说明与历史说明都集中在本文件，正文只保留现行设计（用户 11-08："我认为这类信息不需要体现在任何一个文档……建立一个专门的修改日志文件来分文档 Section 地记录这些信息"）。'
          '每篇一章：先是"按节索引"（节号 → 条目号），再按时间列出条目；条目文字照原注记搬来，未改写。'
          '条目里的节号是记录当时的节号；**协议篇 11-08 晚切分前的条目用旧节号，索引里已换成现行节号**（对照 `_build/TP_SECTION_MAP_20261108.md`）。'
          '设计决定本身的唯一底稿仍是 `Claude_Design_Spec/V1.8_DESIGN_REVISIONS.md`；本文件只记"哪篇哪节在什么时候因为哪条裁定改过"。', '',
          '**以后改任何正式稿，修订说明一律记在这里，不写进正文头部。** 条目号 `CL-<篇>-nn` 按时间编号，后加的条目接着编号。', '']
    total = 0
    for name, moved in docs:
        code, title = CODE[name]
        entries = []
        for i, txt in enumerate(moved):
            owner = txt.startswith('Owner:')
            body = re.sub(r'^Owner: WangYizhao｜', '', txt)
            d = lead_day(body) or day_of(body) or (11, 8)
            ph = -1 if owner else phase(body)
            entries.append((d, ph, i, owner, body))
        entries.sort(key=lambda e: (e[0], e[1], e[2]))
        md += [f'## {title}（`{name}`）', '']
        index = {}
        lines = []
        for n, (d, ph, i, owner, body) in enumerate(entries, start=1):
            cid = f'CL-{code}-{n:02d}'
            if owner:
                label, text = '首版、依据与状态', body
            else:
                m = re.match(r'(.{1,60}?)：', body)
                label, text = (m.group(1), body[m.end():]) if m else (f'{d[0] + 10}-{d[1]:02d}', body)
            whole = owner or body.startswith('依据') or name == 'DATA_ORGANIZATION.md'
            secs = [] if whole else sections(name, body, old_tp=(name == 'DATA_TRANSFER_PROTOCOL.md'))
            for s in secs or ['全篇 / 未注明节']:
                index.setdefault(s, []).append(cid)
            lines += [f'**{cid}｜{label}**：{text}', '']
        md += ['### 按节索引', '']
        keys = sorted([k for k in index if k != '全篇 / 未注明节'], key=sec_key)
        if '全篇 / 未注明节' in index:
            keys = ['全篇 / 未注明节'] + keys
        for k in keys:
            md.append(f'- **{k}**：' + '、'.join(index[k]))
        md += ['', '### 条目', ''] + lines
        total += len(entries)
        print(f'{name}: {len(entries)} entries, {len(index)} index keys')
    io.open(LOG, 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
    print('total entries:', total)


if __name__ == '__main__':
    main()
