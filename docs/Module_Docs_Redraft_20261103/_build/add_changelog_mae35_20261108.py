"""把 V18-MAE-35（MAE_DSU 按字重排）这一轮的修订条目追加到 CHANGELOG_FORMAL_DOCS.md。Owner: WangYizhao · 2026-11-08
用法：python -X utf8 -I _build/add_changelog_mae35_20261108.py
每篇一条 CL-<篇>-nn：节号由正文里给定的锚句所在标题算出；按节索引自动增补；幂等（已存在同号条目则跳过）。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CL = ROOT / 'CHANGELOG_FORMAL_DOCS.md'

USER = ('用户 11-08："我无法接收统一列字布局，因为这会使得输入维度稀疏完全无法减少 EMA"；'
        '"我希望这个任务仍然是 MAE 的"；"MAE 的 DSU，无需规定中间该怎么实现，只需要说明他在转置的时候，输入是怎样的，输出是怎样的，'
        '以及转置需要支持两个 DDR 布局的转置"；"我认为这个攒 4 行 + ping-pong 是最合理的设计……是否能统一逐 Clock 了"；'
        '"我建议放 MAE DSU，作为一个整形模式，并且复用 DSU 所需的寄存器，MAE DSU 的控制命令，一定要来自 MAE ENG"。')

# (篇代号, 章标题里的文件名, 正文文件, 新条目正文, 锚句列表（用于算节号）, 额外节号)
ENTRIES = [
    ('DSU', 'MAE_DSU.md',
     '**半字合并改为按字重排：攒 $n$ 行（标准布局 4 个 $k$ 行 / LSC 2 行）把一拍里分属几个核或几个存储字的粒子重排成各核的整字，'
     '2 × 128 B ping-pong 持续 32 B/拍，核集合与地址由搬运引擎逐字给出；转置只规定输入（标准布局 / 列深度优先两种都必须支持）与输出'
     '（$W^{\\mathsf T}$ 列字块 544 B），撤子段暂存组织、22 KB / 30 k 门、首块 427 拍与"只改落地地址"；暂存一份由两模式共用；'
     'DSU 的全部控制只来自 MAE_ENG 的搬运引擎**（V18-MAE-35）。新图 FIG-MAE_DSU-REGROUP（§4.1）；FIG-MAE_DSU-SPLICE 改为转置的标准布局输入例（§4.2）；'
     'FIG-MAE_DSU-TRANSPOSE / -ARCH 文字同步。',
     ['MAE_DSU 是 MAE 组五个单元之一', '| 四种整形模式：按字重排', '- **粒子**', 'MAE_DSU 有两个入口', '| 整形模式与参数 | MAE_ENG',
      '| 整形输出 → L1 |', '| 按字重排 | 把连续', '### 4.1 按字重排', '### 4.2 转置', 'E8M0 的来源随转置的输入布局', '本节只适用于转置',
      '| 按字重排 | DDR 或 L2 的标准布局单元', '| 前向核 L1 | IDN 出口', '3a. **按字重排的 $n$ 行连续到达', '- **控制只来自 MAE_ENG',
      '| 按字重排吞吐 |', '| 按字重排不降速 |', '- **按字重排是 DSU 的一种模式']),
    ('ENG', 'MAE_ENG.md',
     '**DSU 接口行与运算字段改为按字重排 / 转置 / 两平面合并及其几何（重排粒子字节数与攒行数、转置输入布局与子段长），DSU 的全部控制只由本单元给出；'
     '§9.1 加"前向读标准布局权重与 LSC 必须选按字重排"及核集合规则；IDN 一节的理由改为"链路上只发整字的前提是 MAE_DSU 先按字重排"**（V18-MAE-35）。',
     ['| 整形模式与参数、两侧地址 | MAE_DSU |', '| 运算字段 | 直通 / 经 MAE_DSU', '- 整形模式三选一：按字重排', '链路上只发整字，前提是分属几个核']),
    ('MINT', 'MAE_INTEGRATION.md',
     '**单元表 MAE_DSU 行改四模式（按字重排）并注明控制只来自 MAE_ENG；D6 加"分属几核的粒子先经 MAE_DSU 按字重排"；'
     '§9 V18-HUB-04 条的理由改为按字重排前提与用户原话**（V18-MAE-35）。',
     ['| MAE_DSU | 数据整形：按字重排', '| D6 | IDN 出口 |', '链路上只发整字的前提是 MAE 先把一拍里']),
    ('NII', 'MAE_NI_INT.md',
     '**IDN 出口一条理由改为"分属几核的粒子由 MAE_DSU 按字重排成整字后才进 IDN 出口，本单元不拆拍、不攒字"**（V18-MAE-35）。',
     ['本单元只出一路 32 B，核集合随字']),
    ('TP', 'DATA_TRANSFER_PROTOCOL.md',
     '**§3.5 加"链路上只发整字的前提是 MAE 先按字重排"一段（标准布局 / LSC 一拍的粒子分属几核或几个存储字，由 MAE_DSU 攒行重排；本篇不设拆字分发、L1 写口不接一拍多地址）；'
     '"单核吃满 / 四核均分"改为"单核 / 四核按 $m$ 切分"**（V18-MAE-35）。',
     ['链路上只发整字的前提是 MAE 先按字重排']),
    ('L1', 'L1_SRAM.md',
     '**§7.6 加"标准布局一拍落本核 4 个存储字的情形不在 NWB 处理，由 MAE_DSU 先攒 4 行按字重排"；§15 IDN 验收项加标准布局前向读用例；'
     '§16 V18-HUB-04 条的理由改为按字重排前提（列深度优先一拍本来就是整字；标准布局 / LSC 由 DSU 重排）**（V18-MAE-35）。',
     ['DDR 标准布局一拍（同一 $k$ 行 4 个列组各 8 B）落到本核行字区', '标准布局前向读（经 MAE_DSU 按字重排）单核时', '链路上只发整字的前提是 MAE_DSU 先攒行']),
    ('IDN', 'HUB_IDN.md',
     '**§4.2 首段改为"进入本单元的每个字都是一个核的整存储字：列深度优先本来就是，标准布局 / LSC 由 MAE_DSU 按字重排"，表首行注明单核含重排后 4 字同核；'
     '§10 "不拆 8 B"条的理由改为标准布局交织不能改、重排归 MAE_DSU**（V18-MAE-35）。',
     ['进入本单元的每个字都是一个核的整存储字', '| 单核（含标准布局经 MAE_DSU 重排后', 'DDR 标准布局一拍确实交织 4 个列组']),
    ('ARCH', 'ONCHIP_DATAPATH_ARCH.md',
     '**§4.1 IDN 行、PORT-16 与 §9 V18-HUB-04 条加"每拍一个整字一个地址，分属几核的粒子先由 MAE_DSU 按字重排"，理由改为标准布局交织不能改、重排归 MAE**（V18-MAE-35）。',
     ['分属几个核或几个存储字的粒子先由 MAE_DSU 按字重排', '分属几核的粒子先经 MAE_DSU 按字重排', '链路上只发整字的前提是 MAE_DSU 先攒行']),
    ('INFO', 'L3PU_EXTERNAL_INFORMATION.md',
     '**MAE 指令内容里的整形模式改为"按字重排 / 转置 / 两平面合并及其几何"**（V18-MAE-35）。',
     ['经 MAE_DSU 整形——按字重排']),
]

HEAD = re.compile(r'^(#{1,4})\s+(\d+(?:\.\d+)*[a-z]?)\b')


def section_at(text, anchor):
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit(f'anchor not found: {anchor[:40]}')
    sec = None
    for line in text[:pos].splitlines():
        m = HEAD.match(line)
        if m:
            sec = m.group(2)
    return f'§{sec}' if sec else '全篇 / 未注明节'


def sec_key(s):
    if s.startswith('全篇'):
        return (0,)
    body = s[1:]
    parts = re.findall(r'\d+|[a-z]', body)
    return (1,) + tuple(int(p) if p.isdigit() else ord(p) for p in parts)


def main():
    cl = CL.read_text(encoding='utf-8')
    for code, fname, body, anchors, *extra in ENTRIES:
        doc = (ROOT / fname).read_text(encoding='utf-8')
        secs = sorted({section_at(doc, a) for a in anchors}, key=sec_key)
        # 章范围
        m = re.search(r'^## [^\n]*`' + re.escape(fname) + r'`[)）]\s*$', cl, re.M)
        if not m:
            raise SystemExit(f'chapter not found for {fname}')
        start = m.start()
        nxt = re.search(r'^## ', cl[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(cl)
        chap = cl[start:end]
        nums = [int(n) for n in re.findall(r'\*\*CL-' + code + r'-(\d+)｜', chap)]
        nn = max(nums) + 1
        cid = f'CL-{code}-{nn:02d}'
        if cid in chap:
            print('skip', cid)
            continue
        entry = f'**{cid}｜11-08 下午（V18-MAE-35）**：{body}{USER}（{"、".join(secs)}）'
        # 条目追加到章末
        chap_new = chap.rstrip('\n') + '\n\n' + entry + '\n\n'
        # 索引
        idx_m = re.search(r'### 按节索引\n\n((?:- \*\*[^\n]*\n)+)', chap_new)
        lines = idx_m.group(1).splitlines()
        table = {}
        for ln in lines:
            mm = re.match(r'- \*\*(.+?)\*\*：(.*)', ln)
            table[mm.group(1)] = [x for x in mm.group(2).split('、') if x]
        for s in secs:
            table.setdefault(s, []).append(cid)
        keys = sorted(table, key=sec_key)
        new_idx = ''.join(f'- **{k}**：{"、".join(table[k])}\n' for k in keys)
        chap_new = chap_new[:idx_m.start(1)] + new_idx + chap_new[idx_m.end(1):]
        cl = cl[:start] + chap_new + cl[end:]
        print('added', cid, '->', '、'.join(secs))
    CL.write_text(cl, encoding='utf-8')


if __name__ == '__main__':
    main()
