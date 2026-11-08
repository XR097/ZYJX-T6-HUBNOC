# -*- coding: utf-8 -*-
"""协议篇切分（目录稿第三版，11-08）：重排章节、切出旧 §9 为数据组织篇底稿、换全部正式稿的交叉引用节号。
Owner: WangYizhao · 2026-11-08。一次性脚本；跑前已备份 _backup_20261108b_idn32_Module_Docs_Redraft/。
用法（在 Module_Docs_Redraft_20261103 下）：python -X utf8 -I _build/split_protocol_20261108.py
做什么：
  1. DATA_TRANSFER_PROTOCOL.md 按新章序重排：§1、§2 不动；旧 §5 → §3、旧 §7 → §4、旧 §3 → §5、旧 §4 → §6、旧 §6 → §7、
     §8 内 8.4 并入 8.1（8.5–8.7 → 8.4–8.6）、旧 §9 切出、旧 §10 / §11 / §12 → §9 / §10 / §11；
     正文里的自引用 §x.y 按新号换（头注里 11-08 之前的节号保留旧号，另注明）。
  2. 旧 §9 整章 + §10 / §12 中属于摆放的行 / 条 → DATA_ORGANIZATION.md（底稿，标题号暂保留 9.x，待按目录稿第二版重写）；
     §12 中与架构篇 §9 重复的口宽条目删除（架构篇已有）。
  3. 其他正式稿与图脚本里 "（传输）协议篇 §x.y（/ §a、§b …）" 按新号换；旧 §9.x → "数据组织篇 §9.x"。
     不换：ONCHIP_DATAPATH_ARCH.md、HUB_IDN.md（已按新号写）、_build 下的历史报告 / 任务书、Claude_Design_Spec。
  4. 产出 _build/TP_SECTION_MAP_20261108.md（新旧对照 + 每文件替换计数）。
"""
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'DATA_TRANSFER_PROTOCOL.md'
DORG = ROOT / 'DATA_ORGANIZATION.md'
MAP_MD = ROOT / '_build' / 'TP_SECTION_MAP_20261108.md'

TOP = {1: 1, 2: 2, 3: 5, 4: 6, 5: 3, 6: 7, 7: 4, 8: 8, 10: 9, 11: 10, 12: 11}   # 9 → 数据组织篇
SUB8 = {'4': '1', '5': '4', '6': '5', '7': '6'}                                   # 旧 8.4 并入 8.1；8.5–8.7 → 8.4–8.6


def remap_num(top, rest):
    """top: int, rest: '.3.4' 或 ''。返回 (新 top 字符串, 新 rest, 是否去数据组织篇)。"""
    if top == 9:
        return '9', rest, True
    parts = rest.split('.')[1:] if rest else []
    if top == 8 and parts and parts[0] in SUB8:
        parts[0] = SUB8[parts[0]]
    new_rest = ''.join('.' + p for p in parts)
    return str(TOP[top]), new_rest, False


TOKEN = re.compile(r'§(\d+)((?:\.\d+)*)([a-z]?)')


def remap_bare(text, cross_doc=False):
    """协议篇正文内的自引用：换号；旧 §9.x 写成 '数据组织篇 §9.x'。cross_doc=True 用于切出到数据组织篇的文字：
    自引用要改成 '协议篇 §新号'，而 §9.x 保持裸写。"""
    out, n = [], 0
    pos = 0
    for m in TOKEN.finditer(text):
        pre = text[max(0, m.start() - 2):m.start()]
        if pre.endswith('篇 ') or pre.endswith('篇§'):
            continue                       # 别的篇的节号
        top = int(m.group(1))
        if top not in TOP and top != 9:
            continue
        new_top, new_rest, to_dorg = remap_num(top, m.group(2))
        if cross_doc:
            rep = f'§{new_top}{new_rest}{m.group(3)}' if to_dorg else f'协议篇 §{new_top}{new_rest}{m.group(3)}'
        else:
            rep = f'数据组织篇 §{new_top}{new_rest}{m.group(3)}' if to_dorg else f'§{new_top}{new_rest}{m.group(3)}'
        if rep != m.group(0):
            n += 1
        out.append(text[pos:m.start()])
        out.append(rep)
        pos = m.end()
    out.append(text[pos:])
    return ''.join(out), n


CHAIN = re.compile(r'(传输)?协议篇 §\d+(?:\.\d+)*[a-z]?(?:(?: / |、| 与 | 和 |–|—)§\d+(?:\.\d+)*[a-z]?)*')


def remap_other_doc(text):
    """其他文档里 '协议篇 §a / §b …' 链：逐个换号；§9.x 的那一个改前缀为数据组织篇。"""
    n = 0

    def fix_chain(m):
        nonlocal n
        s = m.group(0)
        prefix_end = s.index('§')
        prefix = s[:prefix_end]            # '协议篇 ' 或 '传输协议篇 '
        toks = list(TOKEN.finditer(s))
        pieces, pos, first = [], 0, True
        for t in toks:
            top = int(t.group(1))
            if top not in TOP and top != 9:
                continue
            new_top, new_rest, to_dorg = remap_num(top, t.group(2))
            new = f'§{new_top}{new_rest}{t.group(3)}'
            if to_dorg:
                new = ('数据组织篇 ' if not first else '') + new
            pieces.append(s[pos:t.start()])
            pieces.append(new)
            if new != t.group(0):
                n += 1
            pos = t.end()
            first = False
        body = ''.join(pieces) + s[pos:]
        # 首个 token 去数据组织篇时，整条链的前缀改名
        first_tok = toks[0]
        if int(first_tok.group(1)) == 9:
            prefix = prefix.replace('协议篇', '数据组织篇')
        return prefix + body[prefix_end:] if body.startswith(prefix) else prefix + body[len(prefix):]

    new = CHAIN.sub(fix_chain, text)
    return new, n


HEAD = re.compile(r'^(#{2,4}) (\d+)((?:\.\d+)*)([a-z]?) (.*)$')


def renumber_heading(line):
    m = HEAD.match(line)
    if not m:
        return line
    top = int(m.group(2))
    new_top, new_rest, _ = remap_num(top, m.group(3))
    return f'{m.group(1)} {new_top}{new_rest}{m.group(4)} {m.group(5)}'


def main():
    lines = io.open(SRC, encoding='utf-8').read().split('\n')
    # ---- 定位各章起止（按标题行）----
    idx = {}
    for i, ln in enumerate(lines):
        m = re.match(r'^## (\d+) ', ln)
        if m:
            idx[int(m.group(1))] = i
    order_old = sorted(idx)
    assert order_old == list(range(1, 13)), order_old
    end = len(lines)
    rng = {k: (idx[k], idx[order_old[j + 1]] if j + 1 < len(order_old) else end) for j, k in enumerate(order_old)}
    header = lines[:idx[1]]

    def block(k):
        a, b = rng[k]
        return lines[a:b]

    # ---- §8：删 8.4 拓扑（并入 8.1 由协调者手改），8.5–8.7 → 8.4–8.6 ----
    b8 = block(8)
    i84 = next(i for i, ln in enumerate(b8) if ln.startswith('### 8.4 '))
    i85 = next(i for i, ln in enumerate(b8) if ln.startswith('### 8.5 '))
    topo_text = [ln for ln in b8[i84 + 1:i85] if ln.strip()]
    b8 = b8[:i84] + b8[i85:]

    # ---- §11（旧）：三行移数据组织篇 ----
    b11 = block(11)
    MOVE_ROWS = ('| 每道 token 在 A 类里连续分配', '| 跨核合并的定长份同址异象限', '| 紧密对象的写入与读出在同一种 A 类配置下')
    moved_rows = [ln for ln in b11 if ln.startswith(MOVE_ROWS)]
    b11 = [ln for ln in b11 if not ln.startswith(MOVE_ROWS)]
    assert len(moved_rows) == 3, moved_rows

    # ---- §12（旧）：四条移数据组织篇、四条删（架构篇 §9 已有）----
    b12 = block(12)
    MOVE_B = ('- **三档打包**', '- **按 MX 组打包', '- **四核分产的数据同址异象限', '- **MAE 按长度表聚集')
    DROP_B = ('- **L2 写侧每核一条 32 B 写链路', '- **IDN 每核一条 32 B 链路', '- **目的 / 源核按物理链路', '- **IDN 带宽按字数比例')
    moved_b = [ln for ln in b12 if ln.startswith(MOVE_B)]
    dropped_b = [ln for ln in b12 if ln.startswith(DROP_B)]
    assert len(moved_b) == 4 and len(dropped_b) == 4, (len(moved_b), len(dropped_b))
    b12 = [ln for ln in b12 if not ln.startswith(MOVE_B + DROP_B)]

    new_body = block(1) + block(2) + block(5) + block(7) + block(3) + block(4) + block(6) + b8 + block(10) + b11 + b12
    new_body = [renumber_heading(ln) for ln in new_body]
    body_text, n_self = remap_bare('\n'.join(new_body))
    io.open(SRC, 'w', encoding='utf-8', newline='\n').write('\n'.join(header) + '\n' + body_text.rstrip('\n') + '\n')

    # ---- 数据组织篇底稿 ----
    b9 = block(9)
    b9_text, _ = remap_bare('\n'.join(b9), cross_doc=True)
    rows_text, _ = remap_bare('\n'.join(moved_rows), cross_doc=True)
    bul_text, _ = remap_bare('\n'.join(moved_b), cross_doc=True)
    dorg = [
        '# 片上数据组织（底稿）',
        '',
        '> Owner: WangYizhao｜2026-11-08｜**底稿，正文未按目录稿写**：本文件是 11-08 协议篇切分（目录稿第三版）时从 `DATA_TRANSFER_PROTOCOL.md` 切出的旧 §9 全章、旧 §11 的三行"由谁保证"与旧 §12 的四条"为什么"，原文照搬、标题号暂保留 9.x，使现有文档里"数据组织篇 §9.x"的引用仍能找到；正式正文按 `../V17_3_MODULE_TOC_DATA_ORG_20261108.md`（第二版）重写时再统一编号并改引用。切出时把其中指向协议篇的节号改成了协议篇的新号。',
        '',
        '## 0 本底稿与目录稿的对应',
        '',
        '| 目录稿第二版 | 底稿里的来源 |',
        '|---|---|',
        '| §2 三种打包方式（定长 / 定长项 / 变长）、§2.1 元素位宽 | 9.2、9.8 |',
        '| §3 数据块 / token 记录 / 32 通道段，紧挨存放与长度表 | 9.1、9.3、9.4、9.7 |',
        '| §2.3 位图与序号列表 | 9.6 |',
        '| §4 各类数据 | 9.5、9.7 |',
        '| §5 各并行模式的落点 | 9.9 |',
        '| 由谁保证 / 为什么 | 文末两节 |',
        '',
    ] + b9_text.split('\n') + [
        '',
        '## 由谁保证（切自协议篇旧 §11）',
        '',
        '| 事项 | 由谁保证 |',
        '|---|---|',
    ] + rows_text.split('\n') + [
        '',
        '## 为什么（切自协议篇旧 §12）',
        '',
    ] + bul_text.split('\n') + ['']
    io.open(DORG, 'w', encoding='utf-8', newline='\n').write('\n'.join(dorg))

    # ---- 其他正式稿与图脚本 ----
    skip = {'DATA_TRANSFER_PROTOCOL.md', 'ONCHIP_DATAPATH_ARCH.md', 'HUB_IDN.md', 'DATA_ORGANIZATION.md'}
    counts = []
    targets = sorted(ROOT.glob('*.md')) + sorted((ROOT / '_build').glob('draw_*.py'))
    for p in targets:
        if p.name in skip:
            continue
        t = io.open(p, encoding='utf-8').read()
        t2, n = remap_other_doc(t)
        if n:
            io.open(p, 'w', encoding='utf-8', newline='\n').write(t2)
            counts.append((p.name, n))
    # FIGURE_REGISTRY_TP.md：只换 14 张图的表行里的裸节号（"正文位置"列），历史注记不动
    reg = ROOT / '_build' / 'FIGURE_REGISTRY_TP.md'
    rl = io.open(reg, encoding='utf-8').read().split('\n')
    n_reg = 0
    for i, ln in enumerate(rl):
        if ln.startswith('| `figs/FIG-TP-') and '架构篇' not in ln.split('|')[3]:
            new, n = remap_bare(ln)
            rl[i] = new
            n_reg += n
    io.open(reg, 'w', encoding='utf-8', newline='\n').write('\n'.join(rl))

    # ---- 对照表 ----
    rows = ['| 旧 | 新 | 说明 |', '|---|---|---|',
            '| §1 | §1 | 分层与覆盖范围；两张口表移架构篇 §1.2 / §3 / §4，LINKS 图改为指路 |',
            '| §2.1–2.6 | §2.1–2.6 | 共同约定不变 |',
            '| §5.1 | §3.1 | 链路表移架构篇 §4.1，本篇只留两条规则句 |',
            '| §5.2–5.10 | §3.2–3.10 | 核间协议（含 5.3.1–5.3.4 → 3.3.1–3.3.4） |',
            '| §7.1–7.6 | §4.1–4.6 | 发送许可与完成（7.4.1–7.4.4 → 4.4.1–4.4.4） |',
            '| §3.1–3.6 | §5.1–5.6 | 核内 RRAM |',
            '| §4.1–4.5 | §6.1–6.5 | 核内 stall |',
            '| §6.1–6.4 | §7.1–7.4 | 桥 |',
            '| §8.1–8.3 | §8.1–8.3 | 命令网；旧 8.4 拓扑一段并入 8.1 |',
            '| §8.5 / 8.6 / 8.7 | §8.4 / 8.5 / 8.6 | 信号 / 消息骨架 / 顺序与时延 |',
            '| §9（全章） | 数据组织篇 §9.x（底稿，编号暂留） | `DATA_ORGANIZATION.md` |',
            '| §10 | §9 | 错误 |',
            '| §11 | §10 | 由谁保证；三行移数据组织篇 |',
            '| §12 | §11 | 为什么；四条移数据组织篇，四条口宽条目删（架构篇 §9 已有） |']
    cnt = ['| 文件 | 换号处数 |', '|---|---|'] + [f'| `{n}` | {c} |' for n, c in counts] + [f'| `_build/FIGURE_REGISTRY_TP.md`（表行） | {n_reg} |', f'| `DATA_TRANSFER_PROTOCOL.md`（正文自引用） | {n_self} |']
    md = ['# 协议篇切分：新旧节号对照（2026-11-08）', '',
          '> Owner: WangYizhao｜由 `_build/split_protocol_20261108.py` 生成。协议篇头注里 11-08 之前各条注记引用的是旧节号（历史记录，不改）；'
          '`Claude_Design_Spec/V1.8_DESIGN_REVISIONS.md`、`_build/` 下的任务书与报告同样保留旧号。'
          '`ONCHIP_DATAPATH_ARCH.md`、`HUB_IDN.md`（11-08 写）已按新号，不在替换之列。', '',
          '## 新旧对照', ''] + rows + ['', '## 各文件替换计数', ''] + cnt + ['',
          '## 并入 8.1 的旧 8.4 原文（协调者手改时用）', ''] + ['> ' + t for t in topo_text] + ['',
          '## 从旧 §12 删除的四条（架构篇 §9 已有同题条目）', ''] + [f'- {ln[4:60]}…' for ln in dropped_b] + ['']
    io.open(MAP_MD, 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
    print('self refs remapped:', n_self, '| registry rows:', n_reg)
    for n, c in counts:
        print(f'  {n}: {c}')


if __name__ == '__main__':
    main()
