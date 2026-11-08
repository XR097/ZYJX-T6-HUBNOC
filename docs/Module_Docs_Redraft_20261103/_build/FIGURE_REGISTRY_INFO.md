# 外部输入信息篇图件登记表（图 ↔ 生图函数 ↔ 正文位置）

> Owner: WangYizhao｜2026-11-06｜正文 `L3PU_EXTERNAL_INFORMATION.md`。

## 再生成

```bash
python -X utf8 -I _build/draw_info.py
```

```bash
& "F:\QQ_Agent\vendor\napcat-shell\node.exe" _build\render.cjs figs _build\preview
```

## 图

| 图文件 | 脚本 / 函数 | 正文位置 | 画什么 | 约定 |
|---|---|---|---|---|
| `figs/FIG-INFO-FOUR-KINDS.svg` | `draw_info.py` / `fig_four_kinds()` | 篇首 | 共享内存 / DDR 里的五样全部经 MAE 搬运引擎（M0 / M1 主口）进芯片，搬运引擎按目的口送 LIC 专用小 SRAM、L2；核产的列表经 C2H 进 L2，通道从 L2 取列表；外部主方经 PIN 从口直写 L2，是唯一不经搬运引擎的路（用户 11-06） | 左列五块只标 "M1 读" 与 "M0 读写" 各一条；文件名沿用 FOUR-KINDS（第二版起为五类）；交叉 0 |
