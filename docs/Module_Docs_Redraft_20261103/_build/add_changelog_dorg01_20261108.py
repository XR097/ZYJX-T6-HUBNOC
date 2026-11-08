"""V18-DORG-01（权重 E8M0 与 bias 独立紧密对象）的 CL 条目追加。Owner: WangYizhao · 2026-11-08
用法：python -X utf8 -I _build/add_changelog_dorg01_20261108.py   （复用 add_changelog_mae35_20261108.py 的函数，幂等）
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from add_changelog_mae35_20261108 import CL, ROOT, section_at, sec_key  # noqa: E402

USER = ('用户 11-08："我希望 E8M0 可以单独紧密存放，偏置可以是一个存放逻辑"；'
        '"E8M0 和 Bias 本来就是存在 L1 SRAM 的 S 专项里的，MAE 仍然可以做到无数据感知的读取"；'
        '"Bias 和 E8M0 同样可以按照两种布局存储，为了不同的模式"；"对于小向量等，无需现在定，仍然是 VNU 的任务"。')

ENTRIES = [
    ('DSU', 'MAE_DSU.md',
     '**转置两种输入布局的块尺度都来自独立的尺度对象（标准布局 1 KB 单元不再带 64 B 前缀，hi / lo 等长），DSU 不解析单元头；'
     '§5.1 / §7 第 1 条同步**（V18-DORG-01）。',
     ['| 标准布局 | 1 KB 单元 = 一个平面同一 K 组的 32 个 $k$ 行', 'E8M0 的来源与转置的输入布局无关', '1. **块尺度先于数字**（转置，两种输入布局相同）', '| 转置 | 把前向形式的 $W$']),
    ('L1', 'L1_SRAM.md',
     '**§5.1 关闭"尺度行在 DDR 怎样存放"【待确认】：权重 E8M0 与 bias 在 DDR 各为独立紧密对象、由普通搬运指令整字落 S 类（K 组主序每 32 B 一个尺度行；32 列段主序按跨距取）**（V18-DORG-01）。',
     ['权重的尺度在 DDR 里是独立的紧密对象']),
]


def main():
    cl = CL.read_text(encoding='utf-8')
    for code, fname, body, anchors in ENTRIES:
        doc = (ROOT / fname).read_text(encoding='utf-8')
        secs = sorted({section_at(doc, a) for a in anchors}, key=sec_key)
        m = re.search(r'^## [^\n]*`' + re.escape(fname) + r'`[)）]\s*$', cl, re.M)
        start = m.start()
        nxt = re.search(r'^## ', cl[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(cl)
        chap = cl[start:end]
        nn = max(int(n) for n in re.findall(r'\*\*CL-' + code + r'-(\d+)｜', chap)) + 1
        cid = f'CL-{code}-{nn:02d}'
        if 'V18-DORG-01' in chap:
            print('skip', code)
            continue
        entry = f'**{cid}｜11-08 下午（V18-DORG-01）**：{body}{USER}（{"、".join(secs)}）'
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
        print('added', cid, '->', '、'.join(secs))
    CL.write_text(cl, encoding='utf-8')


if __name__ == '__main__':
    main()
