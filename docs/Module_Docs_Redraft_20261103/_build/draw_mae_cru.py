"""MAE_CRU 篇的数值小例（第二版：经 L2 合并，V18-CRU-07）。Owner: WangYizhao · 2026-11-07
用法（在 Module_Docs_Redraft_20261103 目录下）：python -X utf8 -I _build/draw_mae_cru.py
输出（figs/）：
  FIG-MAE_CRU-SUM       部分和归约：核 0、1、2 各把部分和写进本核象限的同一象限内地址 A；MAE 经 NI 读口一拍读出四个象限，
                        按象限掩码 0111 取三份，按象限次序 (q0 + q1) + q2 相加，写回 L2
  FIG-MAE_CRU-READSET   读集合并：两条合并指令（象限掩码 0111、0101）各读一拍、按位取并、写回 L2
  FIG-MAE_CRU-RESID     残差加（11-08，V18-CRU-08）：指令 1 归约写 BF16，指令 2 读归约结果 + 残差 MXFP6（码 × 2^-1）相加、
                        按 QNT 规则编码成 MXFP6（尺度 2^1，4.75 → 5 RNE）写回 L2 残差流；末行按 keep 1011 压缩
架构图 FIG-MAE_CRU-ARCH 在 draw_mae_arch.py（MAE 组统一外圈）。数值由脚本算出并断言。
11-07 晚：第一版的"按 CRU 内地址计到达份数"三张图退役——SUM / READSET 改画四象限同址读出，PINGPONG 退役（ping-pong 改在 L2 地址里，
不再有 CRU 存储）；旧函数加 _retired_ 前缀。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit_num import Svg, C_HI, C_LO, C_KEEP, C_OFF, C_SIDE, C_LEFT, C_ACC  # noqa: E402

DATE = '2026-11-08'
A_SRC = 4096                     # 四个象限里同一象限内字节地址（示例）
A_DST = 8192                     # 结果写回的 L2 地址（示例，象限 0）

# =====================================================================
# SUM：部分和归约（四象限同址读出）
# =====================================================================
S_PART = {0: [1.5, -2.0, 0.25, 3.0], 1: [0.5, 1.0, -0.75, 2.0], 2: [-1.0, 0.5, 0.5, 4.0],
          3: [7.0, 7.0, 7.0, 7.0]}                    # 象限 3 的同址字属别的对象（核 3 不参与），不计入
S_MASK = [1, 1, 1, 0]                                 # 象限掩码 0111（象限 0、1、2 参与）
S_SUM = [(S_PART[0][i] + S_PART[1][i]) + S_PART[2][i] for i in range(4)]   # 按象限次序相加
assert S_SUM == [1.0, -0.5, 0.0, 9.0]
assert all(S_SUM[i] != S_SUM[i] + S_PART[3][i] for i in range(4))           # 掩码外的份若被计入，结果会不同


def fig_sum():
    s = Svg(1340, 420)
    s.rich(30, 34, f'部分和归约：核 0、1、2 各把部分和写进本核象限的同一象限内地址 {A_SRC}；MAE 一拍读四个象限，按掩码 0111 取三份', 17)
    s.note(30, 66, '一个存储字 32 B = 16 个 BF16（图中只画 4 个）；加法次序按象限固定 (象限 0 + 象限 1) + 象限 2，与各核写进 L2 的先后无关', 15)
    cols = [('NI 读口这一拍', 200), ('写入方', 110), ('掩码', 80), ('元素 0', 120), ('元素 1', 120), ('元素 2', 120), ('元素 3', 120), ('处理', 300)]
    x0, y0, rh = 30, 92, 42
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    rows = []
    for q in range(4):
        rows.append([f'象限 {q} · 字节 {A_SRC}', f'核 {q}', str(S_MASK[q])] + [f'{v:g}' for v in S_PART[q]] +
                    ['参与合并' if S_MASK[q] else '不参与（同址是别的对象）'])
    rows.append([f'写回 L2 · 字节 {A_DST}', 'MAE_CRU', '—'] + [f'{v:g}' for v in S_SUM] + ['BF16 直出，经 NI-L2C → NI 写口'])
    for i, vals in enumerate(rows):
        y = y0 + (i + 1) * rh
        last = i == len(rows) - 1
        for j, (xx, (_, w), v) in enumerate(zip(xs, cols, vals)):
            f = 'white'
            if last and 3 <= j <= 6:
                f = C_KEEP
            elif not last and 3 <= j <= 6:
                f = C_LO if S_MASK[i] else C_OFF
            elif j == 2 and not last:
                f = C_LEFT if S_MASK[i] else 'white'
            s.cell(xx, y, w - 6, rh - 4, v, fill=f, size=13)
    yb = y0 + (len(rows) + 1) * rh + 24
    s.red(30, yb, '一拍读四份，一拍出一个字', 15)
    s.note(250, yb, '：四个象限同址同拍读出（NI 读口 4 × 32 B），相加后写回 32 B；启动前 MAE 已收齐核 0、1、2 的发出报告', 15)
    s.save('FIG-MAE_CRU-SUM.svg', DATE)


# =====================================================================
# READSET：读集合并（两条指令，象限掩码不同）
# =====================================================================
R_BITS = {(0, 0): '10010000', (1, 0): '00010010', (2, 0): '01000000', (3, 0): '11111111',
          (0, 1): '00100001', (1, 1): '11110000', (2, 1): '00000101', (3, 1): '00001111'}   # (象限, 指令)
R_MASK = {0: [1, 1, 1, 0], 1: [1, 0, 1, 0]}        # 指令 0：掩码 0111；指令 1：掩码 0101
R_SRC = {0: 1024, 1: 1056}                           # 两条指令各读的象限内地址


def _or(bits):
    v = 0
    for b in bits:
        v |= int(b, 2)
    return format(v, '08b')


R_RES = {k: _or([R_BITS[(q, k)] for q in range(4) if R_MASK[k][q]]) for k in (0, 1)}
assert R_RES == {0: '11010010', 1: '00100101'}
assert _or([R_BITS[(q, 0)] for q in range(4)]) != R_RES[0]          # 掩码外的份不能并进来


def fig_readset():
    s = Svg(1340, 470)
    s.rich(30, 34, '读集合并：指令 0（掩码 0111，共享前缀段）与指令 1（掩码 0101，某行私有段）各读一拍四个象限，按位取并', 17)
    s.note(30, 66, '1 位 = 一个 key（或区块、列）要不要读；图中 8 bit，实际一个存储字 256 bit，更长的读集占连续几个字；结果写回 L2，由 MAE 当列表读用', 15)
    cols = [('指令', 90), ('读的地址', 150), ('象限 0', 140), ('象限 1', 140), ('象限 2', 140), ('象限 3', 140), ('掩码', 90), ('并集（写回 L2）', 200)]
    x0, y0, rh = 30, 92, 42
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    for i, k in enumerate((0, 1)):
        y = y0 + (i + 1) * rh
        mask = ''.join(str(b) for b in reversed(R_MASK[k]))
        vals = [f'指令 {k}', f'字节 {R_SRC[k]}'] + [R_BITS[(q, k)] for q in range(4)] + [mask, R_RES[k]]
        fills = ['white', 'white'] + [(C_HI if k == 0 else C_LO) if R_MASK[k][q] else C_OFF for q in range(4)] + ['white', C_KEEP]
        for xx, (_, w), v, f in zip(xs, cols, vals, fills):
            s.cell(xx, y, w - 6, rh - 4, v, fill=f, size=13)
    yb = y0 + 3 * rh + 24
    s.red(30, yb, '掩码外的象限不并入', 15)
    s.note(210, yb, f'：指令 0 并集 {R_RES[0]}、指令 1 并集 {R_RES[1]}；灰格是同址上别的对象。掩码写为象限 3→0', 15)
    s.note(30, yb + 34, '参与核不同的两组用两条指令、两个地址；两条指令可先后执行，ping-pong 由编译链在 L2 地址里安排', 15)
    s.save('FIG-MAE_CRU-READSET.svg', DATE)


# =====================================================================
# RESID：残差加（11-08，V18-CRU-08）——指令 1 归约（BF16 写 L2），指令 2 读归约结果 + 残差（MXFP6）相加、一次编码
# =====================================================================
A_RES = 20480                    # 残差流对象里这 4 个通道的 L2 地址（示例）
A_OUT = 12288                    # 残差加结果写回 L2 残差流的地址（示例）
RES_SCALE_EXP = -1               # 残差这一组的 E8M0 尺度指数：2^-1
RES_CODE = [1.5, -3.0, 4.0, 1.0] # 残差的 E2M3 码（都能精确表示）
RES_VAL = [c * 2.0 ** RES_SCALE_EXP for c in RES_CODE]
assert RES_VAL == [0.75, -1.5, 2.0, 0.5]
X2 = [S_SUM[i] + RES_VAL[i] for i in range(4)]      # x'' = Y + x'（宽格式里相加）
assert X2 == [1.75, -2.0, 2.0, 9.5]
KEEP = [1, 0, 1, 1]                                 # 按列表压缩时的 keep 位图（通道 1 丢）


def e2m3_round(v):
    """E2M3（偏置 1，最大 7.5，次正规步长 0.125）RNE 量化；返回可表示的值。"""
    import math
    a = abs(v)
    if a >= 7.5:
        return math.copysign(7.5, v)
    e = 0 if a < 1.0 else min(2, int(math.floor(math.log2(a))))
    step = 2.0 ** (e - 3)                            # 该二进制区间的码步长：[1,2) 0.125、[2,4) 0.25、[4,8) 0.5；次正规 0.125
    q = a / step
    lo = math.floor(q)
    frac = q - lo
    if frac > 0.5 or (frac == 0.5 and lo % 2 == 1):
        lo += 1
    return math.copysign(lo * step, v)


import math as _m
OUT_SCALE_EXP = int(_m.floor(_m.log2(max(abs(v) for v in X2)))) - 2       # 组尺度：floor(log2 amax) − E2M3 的最大指数 2
assert OUT_SCALE_EXP == 1
OUT_CODE_RAW = [v / 2.0 ** OUT_SCALE_EXP for v in X2]                     # 0.875, −1, 1, 4.75
OUT_CODE = [e2m3_round(c) for c in OUT_CODE_RAW]
assert OUT_CODE_RAW == [0.875, -1.0, 1.0, 4.75] and OUT_CODE == [0.875, -1.0, 1.0, 5.0]   # 4.75 在 [4,8) 步长 0.5，RNE 舍到 5
OUT_VAL = [c * 2.0 ** OUT_SCALE_EXP for c in OUT_CODE]
assert OUT_VAL == [1.75, -2.0, 2.0, 10.0]
COMPACT = [OUT_CODE[i] for i in range(4) if KEEP[i]]
assert len(COMPACT) == 3


def fig_resid():
    s = Svg(1340, 560)
    s.rich(30, 34, '残差加：指令 1 归约（BF16 写 L2），指令 2 读归约结果与残差（MXFP6）相加、一次编码写回 L2 残差流', 17)
    s.note(30, 66, f'一段实际 32 个通道、一行 d_hidden 个通道，图中只画 4 个；残差尺度 2^{RES_SCALE_EXP}，输出尺度 2^{OUT_SCALE_EXP}（组内最大幅值 9.5 ≥ E2M3 最大 7.5，尺度取 2 的幂 floor）', 15)
    cols = [('指令 · 步骤', 230), ('编码 · 地址', 230), ('元素 0', 120), ('元素 1', 120), ('元素 2', 120), ('元素 3', 120), ('说明', 370)]
    x0, y0, rh = 30, 92, 42
    xs, x = [], x0
    for name, w in cols:
        xs.append(x)
        s.cell(x, y0, w - 6, rh - 4, name, fill=C_SIDE, size=14)
        x += w
    rows = [
        ('指令 1 · 归约', f'BF16 · 写 L2 字节 {A_DST}', [f'{v:g}' for v in S_SUM], C_KEEP, '三份同址相加（同 FIG-MAE_CRU-SUM）'),
        ('指令 2 · 读归约结果', f'BF16 · 读 L2 字节 {A_DST}', [f'{v:g}' for v in S_SUM], C_LO, 'MAE 引擎给地址，NI 读口读一个象限'),
        ('指令 2 · 读残差码', f'E2M3 码 · 读 L2 字节 {A_RES}', [f'{v:g}' for v in RES_CODE], C_HI, f'同一 token 同 4 个通道；组尺度 E8M0 = 2^{RES_SCALE_EXP}'),
        ('指令 2 · 残差还原', '码 × 尺度（精确）', [f'{v:g}' for v in RES_VAL], C_HI, '解码在宽格式里无损'),
        ('指令 2 · 相加', 'x″ = Y + x′', [f'{v:g}' for v in X2], C_ACC, '宽格式相加，这里 4 个和都精确'),
        ('指令 2 · 编码', f'E2M3 码 · 尺度 2^{OUT_SCALE_EXP}', [f'{v:g}' for v in OUT_CODE], C_KEEP, '4.75 → 5（[4, 8) 步长 0.5，RNE）；其余精确'),
        ('指令 2 · 写回', f'MXFP6 稠密 · 写 L2 字节 {A_OUT}', [f'{v:g}' for v in OUT_VAL], C_KEEP, '还原值；只在这一步舍入一次'),
        ('（可选）按列表压缩', f'keep {"".join(map(str, KEEP))} · 同址', [f'{OUT_CODE[i]:g}' if KEEP[i] else '—' for i in range(4)], C_LEFT,
         '只写保留通道的码 + 位图 + 尺度；字节数交引擎写长度表'),
    ]
    for i, (a, b, vals, fill, c) in enumerate(rows):
        y = y0 + (i + 1) * rh
        cells = [a, b] + vals + [c]
        for j, (xx, (_, w), v) in enumerate(zip(xs, cols, cells)):
            f = fill if 2 <= j <= 5 else 'white'
            if 2 <= j <= 5 and v == '—':
                f = C_OFF
            s.cell(xx, y, w - 6, rh - 4, v, fill=f, size=13)
    yb = y0 + (len(rows) + 1) * rh + 24
    s.red(30, yb, '残差只加一次，编码只在末了一次', 15)
    s.note(350, yb, '：各核部分和不含残差；归约结果 BF16 是允许的中间暂存；两条指令由 LIC 先后下发，分块时放在一个 Fusion-L3PU 段里循环', 15)
    s.save('FIG-MAE_CRU-RESID.svg', DATE)


if __name__ == '__main__':
    fig_sum()
    fig_readset()
    fig_resid()
