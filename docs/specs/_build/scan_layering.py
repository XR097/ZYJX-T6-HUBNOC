# -*- coding: utf-8 -*-
"""V1.8 分层扫描：列出各篇第 2–6 章里出现的内部做法字样，逐条交人判定。Owner: WangYizhao · 2026-11-11
用法（在 docs/specs 目录下）：python -X utf8 -I _build/scan_layering.py [篇名.md ...]
输出：_build/scan_layering_report.md（按篇、按章列出命中行）；另查：统一八章是否齐全、文件头、"缺省"、
      并发条件交设计者的说法、改名旧词残留、容错残留。
"""
import re, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
INTERNAL = re.compile(r'bank|交织|FIFO|轮流|门数|性能计数|停顿计数|busy|将满阈值|入口缓冲|skid 深度')
GIVE_DESIGNER = re.compile(r'(由|交)\s*(L1|L2|SRAM|接收桥)\s*(的)?\s*设计者\s*(给出|定)')
OLD_NAMES = ['变长列表', '封顶', '码块占位', '补算列表', '写入项', '写项', '搬运单位', '发送侧', '已取位', '待回数',
             'LSC', '在用列表缓存', '模式 1', '模式 2', '读时合并', '外设输入区', '返回车道', '写客户', '攒字寄存器',
             'RW-LANES', 'MAE_DSU-REGROUP']
FAULT = re.compile(r'SLVERR|DECERR|致命错误|越界检查|区间检查|错误检测|错误上报')
CH = ['1 概述', '2 接口需求', '3 功能描述', '4 性能指标', '5 约束与由使用者保证的事项', '6 验收', '7 参考实现', '8 为什么']
SKIP = {'CHANGELOG_V1.8.md', 'README.md'}


def main():
    files = sys.argv[1:] or sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, '*.md')))
    files = [f for f in files if f not in SKIP and not f.endswith('_STAGING.md')]
    out = ['# 分层扫描报告（第 2–6 章内部做法字样）', '']
    tot = 0
    for f in files:
        t = open(os.path.join(ROOT, f), encoding='utf-8').read()
        lines = t.split('\n')
        probs = []
        nonempty = [l.strip() for l in lines[1:6] if l.strip()]
        if not nonempty or nonempty[0] != '> Owner: WangYizhao｜2026-11-11':
            probs.append('文件头第二行不是"> Owner: WangYizhao｜2026-11-11"')
        heads = [l[3:].strip() for l in lines if l.startswith('## ')]
        for i, c in enumerate(CH):
            num = c.split()[0]
            if not any(h.startswith(num + ' ') for h in heads):
                probs.append(f'缺第 {num} 章')
        if '缺省' in t:
            probs.append('出现"缺省"')
        chap = None
        hits = []
        in_code = False
        for ln, l in enumerate(lines, 1):
            if l.startswith('```'):
                in_code = not in_code
            m = re.match(r'^## (\d+) ', l)
            if m:
                chap = int(m.group(1))
            if chap is None:
                continue
            if 2 <= chap <= 6 and INTERNAL.search(l):
                hits.append((ln, chap, 'INT', l.strip()[:220]))
            if chap != 8 and GIVE_DESIGNER.search(l):
                hits.append((ln, chap, 'GIVE', l.strip()[:220]))
            if FAULT.search(l) and chap != 8:
                hits.append((ln, chap, 'FAULT', l.strip()[:220]))
            for w in OLD_NAMES:
                if w in l and not (chap == 1 and '对照' in t[:200]):
                    hits.append((ln, chap, 'OLD:' + w, l.strip()[:220]))
        tot += len(hits)
        out.append(f'## {f}（命中 {len(hits)}）')
        for p in probs:
            out.append(f'- **结构问题**：{p}')
        for ln, ch, k, s in hits:
            out.append(f'- L{ln} 第{ch}章 [{k}] {s}')
        out.append('')
    open(os.path.join(HERE, 'scan_layering_report.md'), 'w', encoding='utf-8').write('\n'.join(out))
    print('hits', tot)


if __name__ == '__main__':
    main()
