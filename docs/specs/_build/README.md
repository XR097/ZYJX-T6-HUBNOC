# 文档构建与检查工具

`docs/specs/` 是当前 V1.8 正式需求基线；`figs/` 只保留正文引用的现行 SVG。历史版本、重整报告、源稿快照、暂存副本和退役图通过 Git 追溯，不放在交付树中。

当前保留的检查：

```text
python -X utf8 -I docs/specs/_build/check_registry.py
python -X utf8 -I docs/specs/_build/build_figure_registry.py docs/specs
python -X utf8 -I docs/specs/_build/xref_check.py
python -X utf8 -I docs/specs/_build/scan_layering.py
```

`scan_layering.py` 输出审阅清单，不把第 7 章参考实现命中误判为合同失败。
