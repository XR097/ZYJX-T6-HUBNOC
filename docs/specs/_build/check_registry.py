"""登记篇 TRANSFER_DATA_REGISTRY.md 的校验脚本。Owner: WangYizhao · 2026-11-08
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/check_registry.py
规则（用户 11-08：校验规则不进正文，只在脚本头注）：
  R1 条目编号 REG-nn 唯一、从 01 起连续（编号只增不重排，缺号要在本脚本的 RETIRED 登记）。
  R2 每个条目含全部固定字段：是什么 / 产出方 → 消费方 / 路径 / 发令方 / 落点 / 打包方式 / 元素格式 / 应写量 / 完成 / 为什么这样走
     （§4 核内条目允许"路径 / 发令方""应写量 / 完成"合并写法；§5 多播条目允许缺"是什么"以外的合并）。
  R3 条目里引用的 PORT-nn 都在架构篇 ONCHIP_DATAPATH_ARCH.md §7 定义。
 R4 条目里引用的 V18-xx 都在当前 V1.8 文档集出现；外部设计会话台账不随交付树发布。
  R5 条目里引用的"数据组织篇 §x.y""协议篇 §x.y""MAE_DSU 篇 §x.y""MAE_CRU 篇 §x.y"节号在对应正文里有标题。
  R6 其他正式稿里引用的"登记篇 REG-nn"都存在。
  R7 打包方式字段只用 定长 / 定长项 / 变长 / 紧密 / 设计者定 这几个词之一（含"随原数据"）。
  R8 已撤销的条目编号（RETIRED）与已撤销的架构篇口号（RETIRED_PORTS）不得再被登记篇引用；
     撤销的口号即使架构篇仍留有加粗字样，也不算 R3 的已定义口。
退出码 0 = 全部通过；否则打印问题清单。
11-09（R45 D 组）：REG-35 撤销并入 REG-13 / 22（V18-L1-20 撤元数据类）；PORT-33 / 34 撤销（同一裁定）。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / 'TRANSFER_DATA_REGISTRY.md'
ARCH = ROOT / 'ONCHIP_DATAPATH_ARCH.md'
DOCS = {'数据组织篇': ROOT / 'DATA_ORGANIZATION.md', '协议篇': ROOT / 'DATA_TRANSFER_PROTOCOL.md',
        'MAE_DSU 篇': ROOT / 'MAE_DSU.md', 'MAE_CRU 篇': ROOT / 'MAE_CRU.md', 'L1 篇': ROOT / 'L1_SRAM.md'}
RETIRED = {'REG-35'}     # 退役编号登记在这里，编号不复用（11-09 REG-35 并入 REG-13 / 22）
RETIRED_PORTS = {'PORT-33', 'PORT-34',   # 架构篇已撤销的口号（11-09，V18-L1-20），不复用
                 'PORT-31', 'PORT-32',   # 11-10 第六轮：S 类读口并入 PORT-02（V18-L1-28 / 29）
                 'PORT-25'}              # 11-11 第六轮：撤 NI 控制道（补充任务书二 R6-C5）
FIELDS = ['是什么', '产出方 → 消费方', '路径', '发令方', '落点', '打包方式', '元素格式', '应写量', '完成', '为什么这样走']
PACK_WORDS = ('定长项', '定长', '变长', '紧密', '设计者定', '随原数据')


def headings(text):
    return {m.group(1) for m in re.finditer(r'^#{2,4}\s+(\d+(?:\.\d+)*[a-z]?)\b', text, re.M)}


def main():
    issues = []
    text = REG.read_text(encoding='utf-8')
    entries = re.split(r'^### (REG-\d{2}) ', text, flags=re.M)
    ids = entries[1::2]
    bodies = entries[2::2]
    # R1
    nums = [int(i[4:]) for i in ids]
    if len(set(ids)) != len(ids):
        issues.append('R1 重复编号')
    top = max(nums + [int(r[4:]) for r in RETIRED])      # 退役号也占号，新条目从最大号之后起
    expected = [n for n in range(1, top + 1) if f'REG-{n:02d}' not in RETIRED]
    if sorted(nums) != expected:
        issues.append(f'R1 编号不连续：{sorted(nums)}')
    arch_ports = set(re.findall(r'\*\*(PORT-\d{2})', ARCH.read_text(encoding='utf-8'))) - RETIRED_PORTS
    # R8
    for r in sorted(RETIRED | RETIRED_PORTS):
        if re.search(rf'\b{r}\b', text):
            issues.append(f'R8 登记篇仍引用已撤销的 {r}')
    v18 = '\n'.join(p.read_text(encoding='utf-8') for p in ROOT.glob('*.md'))
    heads = {k: headings(p.read_text(encoding='utf-8')) for k, p in DOCS.items()}
    for rid, body in zip(ids, bodies):
        sec = body.split('\n')[0]
        body_main = body.split('\n## ')[0]           # 条目到下一个章标题为止
        # R2
        mcast = rid == 'REG-33'
        labels = ' '.join(re.findall(r'^- \*\*([^*]+)\*\*', body_main, re.M))   # 合并写法如"路径 / 发令方""应写量来源 / 完成方式"也算
        for f in FIELDS:
            if f in labels:
                continue
            if mcast and f in ('产出方 → 消费方', '打包方式', '元素格式'):
                continue
            issues.append(f'R2 {rid} 缺字段「{f}」')
        # R3
        for p in set(re.findall(r'PORT-\d{2}', body_main)):
            if p not in arch_ports:
                issues.append(f'R3 {rid} 引用了架构篇没有的 {p}')
        # R4
        for v in set(re.findall(r'V18-[A-Z]+-\d{2}', body_main)):
            if v not in v18:
                issues.append(f'R4 {rid} 引用了 V1.8 里没有的 {v}')
        # R5
        for doc, secs in re.findall(r'(数据组织篇|协议篇|MAE_DSU 篇|MAE_CRU 篇|L1 篇) §([\d\.a/ §–]+)', body_main):
            for s in re.findall(r'\d+(?:\.\d+)*[a-z]?', secs):
                if s not in heads[doc]:
                    issues.append(f'R5 {rid} 引用了{doc}没有的 §{s}')
        # R7
        m = re.search(r'\*\*打包方式\*\*：([^\n]*)', body_main)
        if m and not any(w in m.group(1) for w in PACK_WORDS):
            issues.append(f'R7 {rid} 打包方式用词不在允许集合：{m.group(1)[:40]}')
    # R6
    for p in ROOT.glob('*.md'):
        if p.name in (REG.name, 'CHANGELOG_FORMAL_DOCS.md'):
            continue
        for r in set(re.findall(r'登记篇 (REG-\d{2})', p.read_text(encoding='utf-8'))):
            if r not in ids:
                issues.append(f'R6 {p.name} 引用了不存在的 {r}')
    print(f'{len(ids)} entries, {len(arch_ports)} ports in architecture doc')
    if issues:
        print('\n'.join(issues))
        sys.exit(1)
    print('PASS')


if __name__ == '__main__':
    main()
