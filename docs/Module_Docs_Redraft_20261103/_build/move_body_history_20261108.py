# -*- coding: utf-8 -*-
"""把正式稿正文里的历史句（"11-06 版的……撤""11-08 起……""不再……"）改成只写现行设计，原句记进修改日志（用户 11-08："一并移走"）。
Owner: WangYizhao · 2026-11-08。一次性脚本；跑前已整目录备份 _backup_20261108e_bodyhist_Module_Docs_Redraft/。
"为什么"一节里带日期的用户原话与被否方案是设计依据，不动。
每处替换要求原文恰好出现一次；日志里每篇加一条 CL 条目（按节列"原句 → 现句"），并把条目号补进该篇的按节索引。
"""
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / 'CHANGELOG_FORMAL_DOCS.md'

R = [
    ('DATA_ORGANIZATION.md', '**有效个数由指令给出**（11-05 对象头里的计数撤）', '**有效个数由指令给出**'),
    ('DATA_ORGANIZATION.md', '数据里只剩段头（§9.1）；撤 11-05 的对象头', '数据里只有段头（§9.1），不设对象头'),

    ('DATA_TRANSFER_PROTOCOL.md', '（供数 → 阵列（AEB）→ VNU；出口级 11-08 起是 NLU 的子模块，V18-NLU-06）', '（供数 → 阵列（AEB）→ VNU；出口级是 NLU 的子模块，V18-NLU-06）'),
    ('DATA_TRANSFER_PROTOCOL.md', '（用户 11-05 要求不再叫"行"，以免与矩阵的行、token 行混）', '（不叫"行"，以免与矩阵的行、token 行混，用户 11-05）'),
    ('DATA_TRANSFER_PROTOCOL.md', '（用户 11-05 夜 V18-TP-27，11-06 改 V18-TP-35）', '（V18-TP-27 / 35）'),
    ('DATA_TRANSFER_PROTOCOL.md', '为看清按字的累加，图按 11-05 的"记录补到整字"画（11-07 起记录紧挨，CCU 累加的是字节、攒满 32 B 写一字，规则见 数据组织篇 §9.1）',
     '为看清按字的累加，图把每条记录画成补到整字（实际记录紧挨，CCU 累加的是字节、攒满 32 B 写一字，规则见数据组织篇 §9.1）'),
    ('DATA_TRANSFER_PROTOCOL.md', '**送进 MXU 的激活记录不再要求对齐**', '**送进 MXU 的激活记录不要求对齐**'),
    ('DATA_TRANSFER_PROTOCOL.md', '（din 一律 32 B、be 32 位，11-08 起 IDN 也是，V18-HUB-04）', '（din 一律 32 B、be 32 位，IDN 也是，V18-HUB-04）'),
    ('DATA_TRANSFER_PROTOCOL.md', 'NI 写口不再有独有的象限掩码旁带（并入 `seg` 的段掩码）。', 'NI 写口的同址广播由 `seg` 的段掩码表达，没有独有的旁带。'),
    ('DATA_TRANSFER_PROTOCOL.md', '11-06 版的"C2H 去 MAE_CRU 的分支"与"MAE_CRU 作 H2C 道第二源"撤。', ''),
    ('DATA_TRANSFER_PROTOCOL.md', '（数满 L1 回来的握手），不再是"发送完成"；', '（数满 L1 回来的握手）；'),
    ('DATA_TRANSFER_PROTOCOL.md', '；11-06 的两源 MUX（V18-TP-52）撤。', '。'),
    ('DATA_TRANSFER_PROTOCOL.md', 'V18-L2-04 撤 MAE 装的 5 来源静态表）', 'V18-L2-04）'),
    ('DATA_TRANSFER_PROTOCOL.md', '长度转发因此覆盖全部变长对象，不再限于列表 gather 与外部对象；', '长度转发覆盖全部变长对象、列表 gather 与外部对象；'),
    ('DATA_TRANSFER_PROTOCOL.md', '（§3.8、§4.4.4，V18-TP-50；目的核 L1 原"发送完成即执行完"撤）', '（§3.8、§4.4.4，V18-TP-50）'),
    ('DATA_TRANSFER_PROTOCOL.md', '；"添加指令标号没有问题，ME6 撤回没问题，V18-TP-22 改没问题，CRU 交给 MAE 通知也没问题"；V18-MAE-13）：\n', '；V18-MAE-13）：\n'),
    ('DATA_TRANSFER_PROTOCOL.md', '（多播 $k$ 核按 $k$ 倍计，V18-TP-50；原"发送完成"撤）', '（多播 $k$ 核按 $k$ 倍计，V18-TP-50）'),
    ('DATA_TRANSFER_PROTOCOL.md', '（出口级 11-08 起是 NLU 的子模块，阵列的 AEB 条目直接交 VNU，V18-NLU-06）', '（出口级是 NLU 的子模块，阵列的 AEB 条目直接交 VNU，V18-NLU-06）'),
    ('DATA_TRANSFER_PROTOCOL.md', '11-06 版的"L1 发送侧 + AEB 直达口两个核间主口在 C2H 口前合并、直达口优先"撤；11-07 版的"MXU 输出"一路 11-08 并入 VNU 输出（出口级归 NLU，V18-NLU-06），AEB 部分和经出口级透传上 C2H。',
     'AEB 部分和经 NLU 的出口级子模块透传，算作 VNU 输出上 C2H（V18-NLU-06 / TP-59）。'),
    ('DATA_TRANSFER_PROTOCOL.md', '（§3.8、§4.4.1；11-06 深夜起不再是"数满发出拍数"即发）', '（§3.8、§4.4.1）'),
    ('DATA_TRANSFER_PROTOCOL.md', '11-06 版的"标量"消息与 MAE_CRU 端点撤（V18-TP-55）：', '本网没有标量消息，MAE_CRU 也不是本网端点（V18-TP-55）：'),
    ('DATA_TRANSFER_PROTOCOL.md', '**不设独立的 CRU 配置操作（撤 MAE 操作 18）**', '**不设独立的 CRU 配置操作**'),

    ('HUB_IDN.md', '没有源顺序接口（V18-HUB-02 的"源顺序"已撤）。', '没有源顺序接口。'),
    ('HUB_IDN.md', '| 一拍整字（原 4 拍 × 8 B 撤） |', '| 一拍整字 |'),

    ('HUB_NOC.md', '名称来自 V1.0（10-14）的"以中央 L2 为中心的两级星形 hub"，10-21 第 42 号裁定撤"星形"、改为本篇标题的说法；HUB_IDN 归入后中心端不只 L2，定义按上句。', ''),
    ('HUB_NOC.md', '**C2H 原有的"分流"（去 L2 / 去 MAE_CRU）随 V18-CRU-07 只剩去 L2 一个去向，不再分路**；用户 11-07 要求分流这类随布局调级数的通路留在 HUB，C2H 通路的级数仍由后端定（§3.5）。',
     '**C2H 只有去 L2 一个去向，不分路**（V18-CRU-07）；C2H 通路留在 HUB，级数由后端定（§3.5）。'),
    ('HUB_NOC.md', 'CRU 已并入 MAE 组（MAE_CRU，V18-MAE-11），11-07 晚起只经 L2 进出、不连 HUB（V18-CRU-07）；IDN 11-07 由 MAE 组归入 HUB 组（V18-HUB-01）。',
     'MAE_CRU 属 MAE 组（V18-MAE-11），只经 L2 进出、不连 HUB（V18-CRU-07）；HUB_IDN 属 HUB 组（V18-HUB-01）。'),
    ('HUB_NOC.md', '（11-07 晚撤 D3 MAE_CRU → MUX、D6 C2H → MAE_CRU，编号不重排。）', '（D3、D6 空号。）'),
    ('HUB_NOC.md', '（11-07 晚撤 C2 源顺序、C3 C2H 通路选择、C6 CRU 写入握手，编号不重排。）', '（C2、C3、C6 空号。）'),
    ('HUB_NOC.md', '11-06 的二选一 MUX 与源顺序接口（V18-TP-52）撤。', ''),
    ('HUB_NOC.md', '（V18-CRU-07 撤去 MAE_CRU 的分支）', '（V18-CRU-07）'),

    ('L1_SRAM.md', '（11-05 夜定为兼容能力"可以不用，但不能没有"，11-07 起是默认用法，V18-TP-25 / TP-58 / L1-13）', '（V18-TP-25 / TP-58 / L1-13）'),
    ('L1_SRAM.md', '（11-05 的"送进 MXU 的记录必须对齐"撤，V18-L1-13）', '（V18-L1-13）'),
    ('L1_SRAM.md', 'W1 的 bank 不再出 W 类数据', 'W1 的 bank 不出 W 类数据'),
    ('L1_SRAM.md', '- 没人要的列不读：与旧布局不同，不再有"同一个存储字里没人要的另一列"随字读出。', '- 没人要的列不读：一个存储字只装一列，读出的字里没有没人要的列。'),
    ('L1_SRAM.md', '- W1 不再出 lane，', '- W1 不出 lane，'),
    ('L1_SRAM.md', '**原"重放流直交 pod 激活入口"撤**（用户 11-05）：H2C 激活一律先按 addr 落 A 类', '**H2C 激活一律先按 addr 落 A 类**（用户 11-05）'),
    ('L1_SRAM.md', 'VNU 从 L1 读合并值（V18-TP-55），不再有 CCU 写进"合并值寄存器"的通路。', 'VNU 从 L1 读合并值（V18-TP-55）。'),
    ('L1_SRAM.md', 'MAE 不再向核发 C2H 发送指令。', 'MAE 不向核发 C2H 发送指令。'),
    ('L1_SRAM.md', '11-06 版的"核内上行一律先写 L1""C2H 口前 L1 发送侧与 AEB 直达口两源合并、直达口优先"撤。', ''),

    ('L2_SRAM.md', '；11-06 版的"象限位必须 = $n$，否则致命错误"随之撤', ''),
    ('L2_SRAM.md', '（11-05 夜定为兼容能力"可以不用，但不能没有"，11-07 起是默认用法，V18-TP-25 / L2-02 / L2-05 / TP-58）', '（V18-TP-25 / L2-02 / L2-05 / TP-58）'),
    ('L2_SRAM.md', 'V18-L2-04 撤 MAE 装的 5 来源静态优先级表）', 'V18-L2-04）'),
    ('L2_SRAM.md', '**为什么不再由 L2 维护写计数**', '**为什么 L2 不维护写计数**'),

    ('L3PU_EXTERNAL_INFORMATION.md', '**调用完成状态不再作为状态字写进共享内存，而由 CIF 的状态寄存器承载**', '**调用完成状态不作为状态字写进共享内存，由 CIF 的状态寄存器承载**'),
    ('L3PU_EXTERNAL_INFORMATION.md', '（V18-MAE-15，撤"列表到齐计数"消息；', '（V18-MAE-15；'),

    ('MAE_CRU.md', '（§3.5，V18-CRU-08；撤 11-06 "只保留 BF16 直出"）', '（§3.5，V18-CRU-08）'),
    ('MAE_CRU.md', '第一版的入口 FIFO 与 CRU 存储已撤；V1.7_3 的 ≤ 164 k 门 + 约 4.6 KB RF 不再适用；11-08 加解码器、MXFP6 编码器与压紧',
     '现结构含加法 lane、输入解码器、MXFP6 编码器与压紧，未估；V1.7_3 的 ≤ 164 k 门 + 约 4.6 KB RF 对应另一结构，不作参考'),

    ('MAE_DSU.md', '给出，不再由来源布局码派生（V18-MAE-03）', '给出（V18-MAE-03）'),
    ('MAE_DSU.md', '；IDN 11-07 归 HUB 组，改名 HUB_IDN，V18-HUB-01', '；入站分发网 HUB_IDN 属 HUB 组，V18-HUB-01'),

    ('MAE_ENG.md', '；IDN 11-07 归 HUB 组，改名 HUB_IDN，V18-HUB-01', '；入站分发网 HUB_IDN 属 HUB 组，V18-HUB-01'),
    ('MAE_ENG.md', '（撤原 MAE 操作 18 的独立配置，V18-MAE-12 / 21；V18-CRU-07）', '（V18-MAE-12 / 21；V18-CRU-07）'),
    ('MAE_ENG.md', '（用户 11-06："ME6 撤回没问题"）', '（V18-MAE-13）'),
    ('MAE_ENG.md', '这与"撤流式转发"（V18-TP-46）不冲突', '这与"对象写完才能发"（V18-TP-46）不冲突'),
    ('MAE_ENG.md', '；协议篇原先的"列表到齐计数"消息撤（用户 11-06 ME9："我认为应该选 A"，V18-MAE-15）', '（V18-MAE-15）'),
    ('MAE_ENG.md', '**撤 SRE / IGE / WKE / KCE 四类引擎与按数据类别的发射队列；只有一种搬运引擎，每个引擎都支持全部口对、两种地址生成器与三种运算**',
     '**只有一种搬运引擎，每个引擎都支持全部口对、两种地址生成器与三种运算，不按数据类别分引擎与发射队列**'),
    ('MAE_ENG.md', 'H2C 道只有 L2 一个源（V18-CRU-07），11-06 的 H2C 两源先后与源顺序队列（V18-TP-52）撤。', 'H2C 道只有 L2 一个源（V18-CRU-07）。'),
    ('MAE_ENG.md', '11-06 白天的"5 来源静态优先级表由一条搬运指令写进 L2 的配置口"撤。', ''),
    ('MAE_ENG.md', '；CRU 自己不计数（第一版的"按 CRU 内地址计到达份数"V18-MAE-30 撤）。', '；CRU 自己不计数。'),
    ('MAE_ENG.md', '撤 11-06 "输出只有 BF16 直出"。', ''),
    ('MAE_ENG.md', '11-06 白天的"L2 按（入链路, 象限）维护写计数、MAE 按累计目标值比对"（V18-MAE-20）撤。', ''),

    ('MAE_INTEGRATION.md', '**到四核的入站分发网 IDN 11-07 归 HUB 组，改名 HUB_IDN**', '**到四核的入站分发网 HUB_IDN 属 HUB 组**'),
    ('MAE_INTEGRATION.md', '编号 D1–D7（11-07 晚撤 D8 / D9 / D10）', '编号 D1–D7'),
    ('MAE_INTEGRATION.md', '；11-07 晚撤 C4 CRU 端点、C11 CRU 入口握手）', '；C4、C11 空号）'),

    ('MAE_NI_EXT.md', '入站分发网 IDN 11-07 归 HUB 组，改名 HUB_IDN，V18-HUB-01', '入站分发网 HUB_IDN 属 HUB 组，V18-HUB-01'),
    ('MAE_NI_EXT.md', '**CIF 不再向 NI_EXT 装窗口表**', '**CIF 不向 NI_EXT 装窗口表**'),
    ('MAE_NI_EXT.md', '结果记录里不再有状态字', '结果记录里没有状态字'),
    ('MAE_NI_EXT.md', '；11-06 白天的"L2 按象限写计数、仲裁器记各象限项数、四象限到齐才回 B"（V18-TP-43）撤。', '。'),

    ('MAE_NI_INT.md', '入站分发网 IDN 11-07 归 HUB 组，改名 HUB_IDN（V18-HUB-01）', '入站分发网 HUB_IDN 属 HUB 组（V18-HUB-01）'),
    ('MAE_NI_INT.md', 'V 与权重 MXINT4 不再展开（V18-NII-02）', 'V 与权重 MXINT4 不展开（V18-NII-02）'),
    ('MAE_NI_INT.md', '读返回分路不再有去 CRU 的一路', '读返回分路没有去 CRU 的一路'),
    ('MAE_NI_INT.md', '11-06 版放在本单元、11-07 晚移到 HUB_IDN 的 4 × 32 B 拆拍寄存器 11-08 晚撤销。', ''),
    ('MAE_NI_INT.md', 'NI-L2C 不再需要"按单位、按象限"的记账表，L2 也不再维护写计数', 'NI-L2C 不需要"按单位、按象限"的记账表，L2 也不维护写计数'),
    ('MAE_NI_INT.md', '11-06 白天的"仲裁器为每笔 PIN 事务记各象限项数、四象限写计数到齐才回 B"（V18-TP-43、V18-MAE-L0）撤。', ''),

    ('ONCHIP_DATAPATH_ARCH.md', '不再各自给数字', '不各自给数字'),

    ('VNU_LOSS.md', 'AEB 条目经出口级分发，11-08 起是组内链路，', 'AEB 条目经出口级分发，是组内链路，'),
    ('VNU_LOSS.md', 'MXU 不再重排', 'MXU 不重排'),

    ('VNU_NLU.md', '它原先是 MXU 组的第三部分（V1.7_3 `MXU_ARR` §4.7–§4.8），11-08 起归 NLU：MXU 的 AEB 之后不再有 MXU 自己的运算，**MXU 组的边界到 AEB 为止**（V18-MXU-06）。',
     'MXU 的 AEB 之后没有 MXU 自己的运算，**MXU 组的边界到 AEB 为止**（V18-MXU-06）；本子模块的各动作对应 V1.7_3 `MXU_ARR` §4.7–§4.8。'),
    ('VNU_NLU.md', '；不做 dX 两侧部分和合并（dX 两侧分工 11-08 撤，V18-MXU-05）', ''),
    ('VNU_NLU.md', '（11-08 起 MXU 组到 AEB 为止，V18-MXU-06）', '（MXU 组到 AEB 为止，V18-MXU-06）'),
    ('VNU_NLU.md', '- dX 两侧部分和合并（原 ARR-R-780）随 dX 两侧分工撤（V18-MXU-05），不在本表。\n', ''),

    ('VNU_QNT.md', '——11-08 起出口级是 NLU 的强制子模块（用户 11-04 / 11-08，V18-NLU-06）', '——出口级是 NLU 的强制子模块（V18-NLU-06）'),
    ('VNU_QNT.md', '（11-08 起是组内链路，图中画为来自 NLU，AEB 画灰）', '（组内链路，图中画为来自 NLU，AEB 画灰）'),
    ('VNU_QNT.md', '（11-05 版"经 CCU 中转、结果寄存器 / 合并值寄存器"撤）', ''),
    ('VNU_QNT.md', '（用户 11-04；11-06 撤 PRE / POST 名称，由指令配置', '（用户 11-04；由指令配置'),
    ('VNU_QNT.md', 'token 序号撤（落位校验留给 debug 架构）', '不记 token 序号（落位校验留给 debug 架构）'),
    ('VNU_QNT.md', '（V18-QNT-11；11-05 的"每个在写 token 槽一个未满字、约 $T \\times 32$ B"撤）', '（V18-QNT-11）'),
    ('VNU_QNT.md', '不再经 QNT 解码与重量化', '不经 QNT 解码与重量化'),
]

CODE = {'ONCHIP_DATAPATH_ARCH.md': 'ARCH', 'DATA_TRANSFER_PROTOCOL.md': 'TP', 'DATA_ORGANIZATION.md': 'DORG', 'L1_SRAM.md': 'L1',
        'L2_SRAM.md': 'L2', 'HUB_NOC.md': 'NOC', 'HUB_IDN.md': 'IDN', 'MAE_INTEGRATION.md': 'MINT', 'MAE_ENG.md': 'ENG',
        'MAE_NI_EXT.md': 'NIE', 'MAE_NI_INT.md': 'NII', 'MAE_DSU.md': 'DSU', 'MAE_CRU.md': 'CRU', 'VNU_NLU.md': 'NLU',
        'VNU_QNT.md': 'QNT', 'VNU_SEL.md': 'SEL', 'VNU_LOSS.md': 'LOSS', 'VNU_OPT.md': 'OPT', 'L3PU_EXTERNAL_INFORMATION.md': 'INFO'}


def section_at(text, pos):
    best = '正文开头'
    for m in re.finditer(r'^(#{2,4}) (\d+(?:\.\d+)*[a-z]?) ', text, re.M):
        if m.start() > pos:
            break
        best = '§' + m.group(2)
    return best


def main():
    by_file = {}
    for f, old, new in R:
        by_file.setdefault(f, []).append((old, new))
    records = {}
    for f, pairs in by_file.items():
        p = ROOT / f
        t = io.open(p, encoding='utf-8').read()
        for old, new in pairs:
            c = t.count(old)
            assert c == 1, (f, c, old[:40])
            pos = t.index(old)
            sec = section_at(t, pos)
            t = t.replace(old, new)
            records.setdefault(f, []).append((sec, old.strip(), new.strip()))
        io.open(p, 'w', encoding='utf-8', newline='\n').write(t)

    log = io.open(LOG, encoding='utf-8').read().split('\n')
    for f, recs in records.items():
        code = CODE[f]
        start = next(i for i, l in enumerate(log) if l.startswith('## ') and f'（`{f}`）' in l)
        end = next((i for i in range(start + 1, len(log)) if log[i].startswith('## ')), len(log))
        ids = [int(m.group(1)) for l in log[start:end] for m in [re.match(rf'\*\*CL-{code}-(\d+)', l)] if m]
        cid = f'CL-{code}-{max(ids) + 1:02d}'
        parts = []
        for sec, old, new in recs:
            parts.append(f'{sec}：原「{old}」' + (f'→ 现「{new}」' if new else '→ 删去'))
        entry = [f'**{cid}｜11-08 晚 正文里的历史句移出**（用户 11-08："一并移走"）：' + '；'.join(parts) + '。', '']
        # 条目追加在本章末尾
        ins = end
        while ins > start and not log[ins - 1].strip():
            ins -= 1
        log[ins:ins] = [''] + entry[:1]
        # 按节索引
        end = next((i for i in range(start + 1, len(log)) if log[i].startswith('## ')), len(log))
        i0 = next(i for i in range(start, end) if log[i].startswith('### 按节索引'))
        i1 = next(i for i in range(i0 + 1, end) if log[i].startswith('### 条目'))
        idx = [l for l in log[i0 + 1:i1] if l.startswith('- **')]
        keys = {re.match(r'- \*\*(.+?)\*\*：', l).group(1): l for l in idx}
        for sec in dict.fromkeys(s for s, _, _ in recs):
            k = '全篇 / 未注明节' if sec == '正文开头' else sec
            keys[k] = (keys[k] + '、' + cid) if k in keys else f'- **{k}**：{cid}'

        def sk(k):
            if k == '全篇 / 未注明节':
                return (0, [])
            if k.startswith('数据组织篇'):
                return (2, [int(x) for x in re.findall(r'\d+', k)])
            return (1, [int(x) for x in re.findall(r'\d+', k)])
        new_idx = [keys[k] for k in sorted(keys, key=sk)]
        log[i0:i1] = ['### 按节索引', ''] + new_idx + ['']
        print(f, len(recs), cid)
    io.open(LOG, 'w', encoding='utf-8', newline='\n').write('\n'.join(log))
    print('total', sum(len(v) for v in records.values()))


if __name__ == '__main__':
    main()
