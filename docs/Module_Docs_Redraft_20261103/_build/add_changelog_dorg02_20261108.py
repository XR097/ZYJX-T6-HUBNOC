"""V18-DORG-02（残差流两种存储格式）的 CL 条目追加。Owner: WangYizhao · 2026-11-08
用法：python -X utf8 -I _build/add_changelog_dorg02_20261108.py（复用 add_changelog_mae35_20261108.py 的函数，幂等）
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from add_changelog_mae35_20261108 import CL, ROOT, section_at, sec_key  # noqa: E402

USER = ('用户 11-08："我认为残差流在存储的时候，也应该是压缩存储，只是 CRU 对待它应该是按照稠密去做加法，CRU 完成加法的这一步应该是稠密存储，非稀疏的，'
        '因为还没有过 VNU 的 SEL 模块，过完 SEL 模块后再压缩……最好的方案是这里对 CRU 提出要求，它可以支持两个模式"；'
        '"我认为这里不需要说明默认，只需要在硬件直接标注出来两种支持格式即可"。')

ENTRIES = [
    ('DORG', 'DATA_ORGANIZATION.md',
     '**§4.1 改为"残差流两种存储格式（稠密残差格式 / 紧凑记录），硬件都支持、按位点配置、不设默认"：两格式表 + 残差加两侧（NLU 出口级 / MAE_CRU）输入两种格式、相加按稠密、CRU 输出稠密、'
     '紧凑残差由核侧 QNT 在 SEL 之后写出；算法侧 A 级验证为启用前提【待确认，算法侧】；§1.1 两种打包方式的例子随改；§8 加一条为什么**（V18-DORG-02）。',
     ['### 4.1 残差流与嵌入行', '稠密格式的残差流（一个 token 一项', '紧凑格式的残差流（§4.1）', '- **残差流两种存储格式、残差加两侧按稠密做**']),
    ('CRU', 'MAE_CRU.md',
     '**残差加指令的残差输入可以是稠密残差格式或紧凑记录（按段头 keep 展开、缺位补 0，§3.5 输入编码表加一行，§3.4 "压缩的紧凑记录不作输入"改为残差加例外）；残差加输出一律稠密，"按列表压缩"输出只用于指令已能给 keep 列表的合并**（V18-DORG-02）。',
     ['稠密残差格式 MXFP6 g32，或紧凑记录——按段头 keep 展开', '**残差加的输出一律稠密**', '**唯一的例外是残差加指令的残差输入可以是紧凑记录**', '| 输入 | MXFP6 紧凑记录']),
    ('NLU', 'VNU_NLU.md',
     '**§3.6 残差加与残差 / 特征行还原两行：残差输入支持稠密残差格式与紧凑记录（按段头展开），$x\'$ 按位点配置编码成稠密或等 SEL 判完后编码成紧凑**（V18-DORG-02）。',
     ['**两种存储格式都支持**：稠密残差格式', '| 残差 / 特征行还原 | L1 里的残差对象']),
    ('QNT', 'VNU_QNT.md',
     '**§3.5 记录表残差记录拆成稠密 / 紧凑两行；要点加"残差流两种存储格式都支持、按位点配置，紧凑格式等 SEL 判完后编码"**（V18-DORG-02）。',
     ['| 残差记录（稠密残差格式） |', '**残差流两种存储格式都支持、按位点配置**']),
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
        if 'V18-DORG-02' in chap:
            print('skip', code)
            continue
        nn = max(int(n) for n in re.findall(r'\*\*CL-' + code + r'-(\d+)｜', chap)) + 1
        cid = f'CL-{code}-{nn:02d}'
        entry = f'**{cid}｜11-08 下午（V18-DORG-02）**：{body}{USER}（{"、".join(secs)}）'
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
