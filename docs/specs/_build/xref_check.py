# -*- coding: utf-8 -*-
"""第六轮全范围复审 维度 7：节号与引用核查（只读，不改正式稿）。
解析 24 篇正式稿的标题、"X 篇 §n.m"/"本篇 §n"/裸 §n、PORT-nn、REG-nn、FIG-… 引用，核存在性。
输出 xref_raw.json（全部引用及解析结果）与 xref_problems.txt（不存在 / 可疑项）。
"""
import re, json, os, glob, sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.dirname(os.path.abspath(__file__))

DOCS = [os.path.basename(p) for p in sorted(glob.glob(os.path.join(ROOT, '*.md')))
        if os.path.basename(p) not in ('CHANGELOG_FORMAL_DOCS.md', 'CHANGELOG_V1.8.md', 'README.md')
        and not os.path.basename(p).endswith('_STAGING.md')]

# 篇名 → 文件
ALIAS = {
    '协议': 'DATA_TRANSFER_PROTOCOL.md', '传输协议': 'DATA_TRANSFER_PROTOCOL.md',
    '片上传输协议': 'DATA_TRANSFER_PROTOCOL.md', 'DATA_TRANSFER_PROTOCOL': 'DATA_TRANSFER_PROTOCOL.md',
    '数据组织': 'DATA_ORGANIZATION.md', 'DATA_ORGANIZATION': 'DATA_ORGANIZATION.md',
    '架构': 'ONCHIP_DATAPATH_ARCH.md', '数据通路架构': 'ONCHIP_DATAPATH_ARCH.md', 'ONCHIP_DATAPATH_ARCH': 'ONCHIP_DATAPATH_ARCH.md',
    '接收桥': 'L1_LANDING_BRIDGE.md', 'L1_LANDING_BRIDGE': 'L1_LANDING_BRIDGE.md',
    '登记': 'TRANSFER_DATA_REGISTRY.md', '传输数据类别登记': 'TRANSFER_DATA_REGISTRY.md', 'TRANSFER_DATA_REGISTRY': 'TRANSFER_DATA_REGISTRY.md',
    '外部信息': 'L3PU_EXTERNAL_INFORMATION.md', '外部输入信息': 'L3PU_EXTERNAL_INFORMATION.md', 'L3PU_EXTERNAL_INFORMATION': 'L3PU_EXTERNAL_INFORMATION.md',
    'L1': 'L1_SRAM.md', 'L1_SRAM': 'L1_SRAM.md', 'L2': 'L2_SRAM.md', 'L2_SRAM': 'L2_SRAM.md',
    'MAE_ENG': 'MAE_ENG.md', 'ENG': 'MAE_ENG.md', 'MAE_DSU': 'MAE_DSU.md', 'DSU': 'MAE_DSU.md',
    'MAE_CRU': 'MAE_CRU.md', 'CRU': 'MAE_CRU.md', 'MAE_NI_EXT': 'MAE_NI_EXT.md', 'NI_EXT': 'MAE_NI_EXT.md',
    'MAE_NI_INT': 'MAE_NI_INT.md', 'NI_INT': 'MAE_NI_INT.md', 'MAE_INTEGRATION': 'MAE_INTEGRATION.md',
    'MAE 集成': 'MAE_INTEGRATION.md', 'MAE集成': 'MAE_INTEGRATION.md',
    'HUB_NOC': 'HUB_NOC.md', 'HUB_IDN': 'HUB_IDN.md',
    'VNU_EPI': 'VNU_EPI.md', 'EPI': 'VNU_EPI.md', 'VNU_NLU': 'VNU_NLU.md', 'NLU': 'VNU_NLU.md',
    'VNU_SEL': 'VNU_SEL.md', 'SEL': 'VNU_SEL.md', 'VNU_SMP': 'VNU_SMP.md', 'SMP': 'VNU_SMP.md',
    'VNU_LOSS': 'VNU_LOSS.md', 'LOSS': 'VNU_LOSS.md', 'VNU_OPT': 'VNU_OPT.md', 'OPT': 'VNU_OPT.md',
    'VNU_QNT': 'VNU_QNT.md', 'QNT': 'VNU_QNT.md', 'VNU_INTEGRATION': 'VNU_INTEGRATION.md',
    'VNU 集成': 'VNU_INTEGRATION.md', 'VNU集成': 'VNU_INTEGRATION.md',
    'MXU_INTEGRATION': 'MXU_INTEGRATION.md', 'MXU 集成': 'MXU_INTEGRATION.md', 'MXU集成': 'MXU_INTEGRATION.md',
    'MXU_FEED': 'MXU_FEED.md', 'MXU_ARR': 'MXU_ARR.md', 'MXU_CONTROLLER': 'MXU_CONTROLLER.md',
    'VNU_CONTROLLER': 'VNU_CONTROLLER.md', 'CIF': 'CIF.md',
}
UNWRITTEN = {'MXU', 'CCU', 'CCU_CTL', 'CCU_RTR', 'CCU_INTEGRATION', 'LIC', '计算核集成',
             'CCU 集成', 'ISA', 'L3PU_ISA'}
EXTERNAL_PREFIX = ['V1.8', 'V1.7', 'V1.7_3', 'PENDING', 'V0.2', 'CONFIRM', 'ISA', '旧', '原', 'brief', 'BRIEF',
                   '任务书', 'V18', 'SPEC', 'DESIGN_RECORD', 'CHANGELOG', 'DATAFLOW', '源 ', '源']

HEAD_RE = re.compile(r'^(#{1,6})\s+(.*)$')
SECNUM_RE = re.compile(r'^§?\s*(\d+(?:\.\d+)*[a-z]?)(?=[\s　]|$)')
REGHEAD_RE = re.compile(r'^(REG-\d+)')

def parse_headings(text):
    secs = {}
    regs = {}
    in_code = False
    for ln, line in enumerate(text.split('\n'), 1):
        if line.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = HEAD_RE.match(line)
        if not m:
            continue
        title = m.group(2).strip()
        m2 = SECNUM_RE.match(title)
        if m2:
            secs[m2.group(1)] = (ln, title)
        m3 = REGHEAD_RE.match(title)
        if m3:
            regs[m3.group(1)] = (ln, title)
    return secs, regs

texts = {d: open(os.path.join(ROOT, d), encoding='utf-8').read() for d in DOCS}
HEADS = {}
REGDEF = {}
for d, t in texts.items():
    s, r = parse_headings(t)
    HEADS[d] = s
    if r:
        REGDEF.update({k: (d,) + v for k, v in r.items()})

# PORT 定义：架构篇 §7 中 "- **PORT-nn" 或 "PORT-nn" 作条目首
PORTDEF = {}
for ln, line in enumerate(texts['ONCHIP_DATAPATH_ARCH.md'].split('\n'), 1):
    m = re.match(r'^\s*[-*]\s*\*\*(PORT-\d+)\s*([^*]*)\*\*', line)
    if m:
        PORTDEF[m.group(1)] = (ln, m.group(2).strip())
    m = re.match(r'^#{1,6}\s+(PORT-\d+)\s*(.*)', line)
    if m:
        PORTDEF[m.group(1)] = (ln, m.group(2).strip())

# 图
FIGS = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(ROOT, 'figs', '*.svg'))}
RETIRED = {}
for p in glob.glob(os.path.join(ROOT, 'figs', '_retired_*', '*.svg')):
    RETIRED.setdefault(os.path.splitext(os.path.basename(p))[0], []).append(os.path.basename(os.path.dirname(p)))

NAMES = sorted(list(ALIAS.keys()) + list(UNWRITTEN), key=len, reverse=True)
NAME_ALT = '|'.join(re.escape(n) for n in NAMES)
SEC = r'(\d+(?:\.\d+)*[a-z]?)'
# 篇名 + 可选"篇"/".md"/反引号/括注 + §
BOUND_RE = re.compile(r'(?<![A-Za-z0-9_])`?(' + NAME_ALT + r')(?:\.md)?`?\s*(篇)?\s*(?:（[^）\n]{0,24}）)?\s*(?:的)?\s*(?:第\s*\d+\s*层\s*（)?\s*§\s*' + SEC)
SELF_RE = re.compile(r'本篇\s*§\s*' + SEC)
ANY_SEC_RE = re.compile(r'§\s*' + SEC)
CHAIN_RE = re.compile(r'(?:（[^）\n§]{0,30}）)?\s*(?:、|/|，|,|和|与|及|或|以及)\s*§\s*' + SEC)
RANGE_RE = re.compile(r'\s*(?:–|—|~|至|-)\s*§?\s*' + SEC)

def line_of(text, pos):
    return text.count('\n', 0, pos) + 1

def line_text(text, ln):
    return text.split('\n')[ln - 1]

def section_at(heads_by_line, ln):
    cur = None
    for l, sid in heads_by_line:
        if l <= ln:
            cur = sid
        else:
            break
    return cur

def resolve(name, cur_doc, ctx):
    if name in ALIAS:
        tgt = ALIAS[name]
        return tgt
    return None

refs = []
for d, t in texts.items():
    hb = sorted((v[0], k) for k, v in HEADS[d].items())
    consumed = set()
    lines = t.split('\n')
    # 代码块范围
    def emit(kind, start, name, sec, tgt, note=''):
        ln = line_of(t, start)
        refs.append(dict(doc=d, line=ln, in_sec=section_at(hb, ln), kind=kind, name=name, sec=sec,
                         target=tgt, note=note, ctx=line_text(t, ln).strip()[:300]))
    def chain(m_end, name, tgt, kind):
        pos = m_end
        while True:
            m = CHAIN_RE.match(t, pos) or RANGE_RE.match(t, pos)
            if not m:
                break
            # 范围上界若无点号且小于 2 位，当作同篇节号
            consumed.add(m.start(1))
            emit(kind, m.start(1), name, m.group(1), tgt, 'chain')
            pos = m.end()
    for m in BOUND_RE.finditer(t):
        name = m.group(1)
        consumed.add(m.start(3))
        # "集成篇"前缀判定
        if name in UNWRITTEN:
            emit('unwritten', m.start(3), name, m.group(3), None)
            chain(m.end(), name, None, 'unwritten')
            continue
        tgt = ALIAS[name]
        emit('cross' if tgt != d else 'self_named', m.start(3), name, m.group(3), tgt)
        chain(m.end(), name, tgt, 'cross' if tgt != d else 'self_named')
    # 无前缀"集成篇 §"：按所在篇判归属
    for m in re.finditer(r'(?<![A-Za-z_ ])(?<!MAE )(?<!VNU )(?<!计算核)集成篇\s*(?:（[^）\n]{0,24}）)?\s*§\s*' + SEC, t):
        if m.start(1) in consumed:
            continue
        pre = t[max(0, m.start() - 6):m.start()]
        if d.startswith('VNU_'):
            tgt = 'VNU_INTEGRATION.md'
        elif d.startswith('MAE_'):
            tgt = 'MAE_INTEGRATION.md'
        else:
            tgt = None
        consumed.add(m.start(1))
        emit('cross_ambig' if tgt else 'ambiguous', m.start(1), '集成篇', m.group(1), tgt, 'pre=' + pre)
        chain(m.end(), '集成篇', tgt, 'cross_ambig')
    for m in re.finditer(r'计算核集成篇\s*§\s*' + SEC, t):
        if m.start(1) in consumed: continue
        consumed.add(m.start(1))
        emit('unwritten', m.start(1), '计算核集成', m.group(1), None)
    for m in SELF_RE.finditer(t):
        if m.start(1) in consumed: continue
        consumed.add(m.start(1))
        emit('self', m.start(1), '本篇', m.group(1), d)
        chain(m.end(), '本篇', d, 'self')
    for m in ANY_SEC_RE.finditer(t):
        if m.start(1) in consumed: continue
        pre = t[max(0, m.start() - 14):m.start()]
        ext = any(p in pre[-10:] for p in EXTERNAL_PREFIX)
        consumed.add(m.start(1))
        emit('bare_external' if ext else 'bare', m.start(1), '', m.group(1), None if ext else d, 'pre=' + pre.replace('\n', ' '))

# 裸 § 紧跟在同一分句的跨篇引用之后：可能实指那一篇
by_line = defaultdict(list)
for r in refs:
    by_line[(r['doc'], r['line'])].append(r)
for d, t in texts.items():
    lines = t.split('\n')
    for (dd, ln), rs in by_line.items():
        if dd != d: continue
        crosses = [r for r in rs if r['kind'] in ('cross', 'cross_ambig') and r['target'] != d]
        if not crosses: continue
        line = lines[ln - 1]
        for r in rs:
            if r['kind'] != 'bare': continue
            # 找该裸引用在行内的位置（按出现次序近似）
            pass
# 精确版：按字符位置
for d, t in texts.items():
    pos_refs = []
    for m in BOUND_RE.finditer(t):
        if m.group(1) in ALIAS and ALIAS[m.group(1)] != d:
            pos_refs.append((m.end(), ALIAS[m.group(1)], m.group(1)))
    for r in refs:
        if r['doc'] != d or r['kind'] != 'bare': continue
        r.setdefault('maybe_cross', None)
    # 用 ANY_SEC 位置重扫
    bare_pos = {}
    for m in ANY_SEC_RE.finditer(t):
        bare_pos.setdefault(line_of(t, m.start(1)), []).append(m.start(1))
    for pe, tgt, nm in pos_refs:
        # 向后到分句边界
        j = pe
        seg_end = len(t)
        for b in ('。', '；', '\n', '|'):
            k = t.find(b, pe)
            if k != -1: seg_end = min(seg_end, k)
        for m in ANY_SEC_RE.finditer(t, pe, seg_end):
            ln = line_of(t, m.start(1))
            for r in by_line.get((d, ln), []):
                if r['kind'] == 'bare' and r['sec'] == m.group(1) and r.get('maybe_cross') is None:
                    r['maybe_cross'] = tgt
                    r['maybe_cross_name'] = nm
                    break

# 存在性
problems = []
for r in refs:
    if r['kind'] in ('cross', 'self', 'self_named', 'bare', 'cross_ambig'):
        tgt = r['target']
        r['exists'] = r['sec'] in HEADS.get(tgt, {})
        if r['exists']:
            r['target_title'] = HEADS[tgt][r['sec']][1]
        else:
            # 允许 §n 指向含 n.* 的顶层但顶层标题非数字的情形
            pref = [k for k in HEADS.get(tgt, {}) if k.startswith(r['sec'] + '.')]
            r['note'] += (' | 有子节无本节标题' if pref else '')
            problems.append(r)

# PORT / REG / FIG
other = []
for d, t in texts.items():
    for m in re.finditer(r'PORT-(\d+)', t):
        k = 'PORT-' + m.group(1)
        ln = line_of(t, m.start())
        ok = k in PORTDEF
        other.append(dict(doc=d, line=ln, kind='PORT', id=k, exists=ok, title=PORTDEF.get(k, (0, ''))[1], ctx=line_text(t, ln).strip()[:300]))
    for m in re.finditer(r'REG-(\d+)', t):
        k = 'REG-' + m.group(1)
        ln = line_of(t, m.start())
        ok = k in REGDEF
        other.append(dict(doc=d, line=ln, kind='REG', id=k, exists=ok, title=REGDEF.get(k, ('', 0, ''))[2] if ok else '', ctx=line_text(t, ln).strip()[:300]))
    for m in re.finditer(r'FIG-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*', t):
        k = m.group(0)
        if k.endswith('-'): k = k[:-1]
        ln = line_of(t, m.start())
        ok = k in FIGS
        other.append(dict(doc=d, line=ln, kind='FIG', id=k, exists=ok, retired=RETIRED.get(k), embed=('figs/' + k + '.svg') in t[m.start()-200:m.end()+40],
                          ctx=line_text(t, ln).strip()[:300]))

json.dump(dict(docs=DOCS, heads={d: {k: v[1] for k, v in h.items()} for d, h in HEADS.items()},
               ports={k: v[1] for k, v in PORTDEF.items()}, regs={k: v[2] for k, v in REGDEF.items()},
               refs=refs, other=other), open(os.path.join(OUT, 'xref_raw.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

with open(os.path.join(OUT, 'xref_problems.txt'), 'w', encoding='utf-8') as f:
    f.write('== 统计\n')
    kinds = defaultdict(int)
    for r in refs: kinds[r['kind']] += 1
    f.write(json.dumps(kinds, ensure_ascii=False) + '\n')
    f.write('PORT 定义 %d 个: %s\n' % (len(PORTDEF), sorted(PORTDEF)))
    f.write('REG 定义 %d 个\n' % len(REGDEF))
    f.write('\n== 节号不存在\n')
    for r in problems:
        f.write('%s:%d [%s] %s §%s -> %s %s\n    %s\n' % (r['doc'], r['line'], r['kind'], r['name'], r['sec'], r['target'], r['note'], r['ctx']))
    f.write('\n== 裸 § 跟在同分句跨篇引用后（自篇解释 | 跨篇解释）\n')
    for r in refs:
        if r.get('maybe_cross'):
            tg = r['maybe_cross']
            selft = HEADS[r['doc']].get(r['sec'], (0, '—不存在—'))[1]
            crt = HEADS[tg].get(r['sec'], (0, '—不存在—'))[1]
            f.write('%s:%d §%s  self=[%s]  %s=[%s]\n    %s\n' % (r['doc'], r['line'], r['sec'], selft[:40], r['maybe_cross_name'], crt[:40], r['ctx'][:260]))
    f.write('\n== 未成文篇引用\n')
    for r in refs:
        if r['kind'] == 'unwritten':
            f.write('%s:%d %s §%s\n    %s\n' % (r['doc'], r['line'], r['name'], r['sec'], r['ctx']))
    f.write('\n== 集成篇归属不明\n')
    for r in refs:
        if r['kind'] == 'ambiguous':
            f.write('%s:%d 集成篇 §%s %s\n    %s\n' % (r['doc'], r['line'], r['sec'], r['note'], r['ctx']))
    f.write('\n== PORT / REG 不存在\n')
    for o in other:
        if o['kind'] in ('PORT', 'REG') and not o['exists']:
            f.write('%s:%d %s\n    %s\n' % (o['doc'], o['line'], o['id'], o['ctx']))
    f.write('\n== FIG 不存在\n')
    seen = set()
    for o in other:
        if o['kind'] == 'FIG' and not o['exists']:
            f.write('%s:%d %s retired=%s embed=%s\n    %s\n' % (o['doc'], o['line'], o['id'], o['retired'], o['embed'], o['ctx'][:200]))
print('refs', len(refs), 'problems', len(problems))
