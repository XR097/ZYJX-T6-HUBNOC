# 当前文档工具

本目录保留当前正文配图的生成工具和本地校验工具。正文基线在 `docs/specs/`，图件在 `figs/`；历史版本通过 Git 追溯。生图脚本用相对自身位置定位目录，可从仓库根目录运行。除自动图件登记表外，不保留旧任务书、旧报告或缓存。

## 校验与登记

在仓库根目录执行：

```powershell
python -X utf8 -I docs/specs/_build/check_registry.py
python -X utf8 -I docs/specs/_build/build_figure_registry.py
```

`check_registry.py` 默认执行本地 R1/R2/R3/R5/R6/R7：登记项连续性、字段、架构端口号、部分正文节号、反向登记引用及打包用词。R4 的 V18 裁定引用来自外部文件，默认明确报告未执行；需要时显式传入 `--revisions <文件路径>`。退出码 0 只表示本次启用的检查通过，不表示外部裁定或硬件语义已审查；条目问题返回 1，输入文件/参数错误返回 2。

`build_figure_registry.py` 默认扫描本脚本所在的正文目录，也可传入目录。它覆盖生成 `_build/FIGURE_REGISTRY.md`，列出 SVG 引用、函数与脚本，并列出缺图、未引用图及未找到函数的图。函数对应关系通过源码字面量扫描推导，动态文件名或间接调用可能无法识别；结果需要结合正文核对。运行登记生成器不重画 SVG，也不做视觉审查。

## 配图生成与预览

`draw_*.py` 按对应正文生成 SVG；`draw_vnu_conn.py` 统一生成五个 VNU 外框连接图，`draw_mae_arch.py` 和 `draw_tp_arch.py` 也提供部分公共图元。`fig_f5_post.py`、`figkit3.py`、`svgkit_num.py`、`geometry.py`、`router.py` 是公共依赖；`mcast_fork_sim.py` 提供多播示例的周期计算。生图会覆盖对应 SVG，运行前先核对正文与目标范围。

Python 工具使用 Python 3；部分生图脚本还需 Pillow，以及 Windows 字体文件（字体路径见 `figkit3.py`）。PNG 预览使用 Node.js 和 `sharp`：

```powershell
npm install --no-save sharp
node docs/specs/_build/render.cjs docs/specs/figs docs/specs/_build/preview
```

也可通过 `SHARP_MODULE` 环境变量指定已安装的 sharp 模块路径。渲染器不依赖特定用户目录；缺少模块时返回非零退出码并说明依赖。预览 PNG 与 Python 缓存是本地产物，不作为正文基线提交。
