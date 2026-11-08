"""把各正式稿里指向数据组织篇底稿的旧节号（§9.x，来自协议篇旧 §9）换成正文版的新节号，并追加 CL 条目。Owner: WangYizhao · 2026-11-08
用法：python -X utf8 -I _build/renumber_dorg_refs_20261108.py
对照：9.1 → 1.2（对齐 / 紧挨）；9.2 → 1.1（三种打包方式）；9.3 → 2.2（长度表）；9.4 → 2.4（定位）；9.5 → 5.2（按 T 切分 / 散写）；
      9.7 → 2.5（窗口容量句）或 5.7（产出次序 / 聚集 / 行统计量）；9.8 → 3（定长项）；9.9 → 5.3（四区域 / 按 m 切分句）或 5.6（衔接 / 并存）；
      裸"数据组织篇 §9" → "数据组织篇"。幂等。
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from add_changelog_mae35_20261108 import CL, ROOT, section_at, sec_key  # noqa: E402

DOCS = {
    'HUB_NOC.md': 'NOC', 'L2_SRAM.md': 'L2', 'MAE_ENG.md': 'ENG', 'VNU_LOSS.md': 'LOSS', 'L1_SRAM.md': 'L1',
    'VNU_QNT.md': 'QNT', 'VNU_SEL.md': 'SEL', 'DATA_TRANSFER_PROTOCOL.md': 'TP', 'VNU_NLU.md': 'NLU',
}
FIXED = {'1': '1.2', '2': '1.1', '3': '2.2', '4': '2.4', '5': '5.2', '8': '3'}
# HUB_NOC.md 的唯一一处（§2.2，§9.9 → §5.3）在第一次运行（键名错误前）已换好，这里只补它的 CL 条目
PRE_DONE = {'HUB_NOC.md': (1, ['§2.2'])}
PAT = re.compile(r'数据组织篇 §9(?:\.(\d))?(?!\d)')


def new_num(old, line):
    if old is None:
        return None                      # 裸 §9
    if old in FIXED:
        return FIXED[old]
    if old == '7':
        return '2.5' if ('窗口容量' in line or '窗口 = ' in line or '上限 ×' in line) else '5.7'
    if old == '9':
        return '5.3' if ('区域' in line or '错开' in line) else '5.6'
    raise SystemExit(f'unmapped §9.{old}: {line[:60]}')


def main():
    cl = CL.read_text(encoding='utf-8')
    for fname, code in DOCS.items():
        p = ROOT / fname
        text = p.read_text(encoding='utf-8')
        if '数据组织篇 §9' not in text and fname not in PRE_DONE:
            continue
        lines = text.split('\n')
        changed_secs, n = set(), 0
        if fname in PRE_DONE:
            n, pre = PRE_DONE[fname]
            changed_secs.update(pre)
        for i, line in enumerate(lines):
            if '数据组织篇 §9' not in line:
                continue
            def rep(m):
                nonlocal n
                n += 1
                nn = new_num(m.group(1), line)
                return '数据组织篇' if nn is None else f'数据组织篇 §{nn}'
            new = PAT.sub(rep, line)
            if new != line:
                lines[i] = new
                changed_secs.add(section_at(text, line))
        text_new = '\n'.join(lines)
        p.write_text(text_new, encoding='utf-8')
        secs = sorted(changed_secs, key=sec_key)
        print(f'{fname}: {n} refs -> {"、".join(secs)}')
        # CL 条目
        m = re.search(r'^## [^\n]*`' + re.escape(fname) + r'`[)）]\s*$', cl, re.M)
        start = m.start()
        nxt = re.search(r'^## ', cl[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(cl)
        chap = cl[start:end]
        if '数据组织篇节号换成正文版' in chap:
            continue
        nn = max(int(x) for x in re.findall(r'\*\*CL-' + code + r'-(\d+)｜', chap)) + 1
        cid = f'CL-{code}-{nn:02d}'
        entry = (f'**{cid}｜11-08 下午（数据组织篇正文产出）**：数据组织篇节号换成正文版（旧 §9.1 → §1.2、§9.2 → §1.1、§9.3 → §2.2、§9.4 → §2.4、'
                 f'§9.5 → §5.2、§9.7 → §2.5 / §5.7、§9.8 → §3、§9.9 → §5.3 / §5.6，裸 §9 → 篇名），共 {n} 处；只换节号，不改内容（{"、".join(secs)}）')
        chap_new = chap.rstrip('\n') + '\n\n' + entry + '\n\n'
        idx_m = re.search(r'### 按节索引\n\n((?:- \*\*[^\n]*\n)+)', chap_new)
        table = {}
        for ln in idx_m.group(1).splitlines():
            mm = re.match(r'- \*\*(.+?)\*\*：(.*)', ln)
            table[mm.group(1)] = [x for x in mm.group(2).split('、') if x]
        for s in secs:
            table.setdefault(s, []).append(cid)
        new_idx = ''.join(f'- **{k}**：{"、".join(table[k])}\n' for k in sorted(table, key=sec_key))
        chap_new = chap_new[:idx_m.start(1)] + new_idx + chap_new[idx_m.end(1):]
        cl = cl[:start] + chap_new + cl[end:]
    CL.write_text(cl, encoding='utf-8')


if __name__ == '__main__':
    main()
