# 高级数学问题与完整人类证明：可编辑题证库

## 当前实际交付

本目录实际交付 **20 题**，不是 3195 题完成。每题均为独立可编辑 `.tex`，包含完整作者原命题、完整作者证明、必要背景、保留的原始宏和可追溯出处。整理说明明确标为非作者正文。数学证明来自可追溯的人类作者，不由助手补造。

- [打开可读总目录](INDEX.md)
- [下载实际全文 SQLite 数据库](corpus.sqlite)：20 条完整题证，TeX 全文存于 `problems.tex_content`；含来源表、稳定编号、难度与依据、版本和原文定位
- [查看机器可读清单](manifest.json)
- [查看当前已恢复的 3000 个旧记录及格式状态](pending-inventory.csv)

历史 3195 是旧证据门禁数量，原先包含 373 个原生 TeX 和 2822 个 PDF 页面封装。页面封装尚需完整可编辑转录；尚未核对的原生 TeX 同样不能凭字段计为完成。这里只统计实际交付的完整题证。

## 阅读和编译

`items/` 每个文件都独立包含作者题面和证明，无需下载整书或约 15 GB 原件。外部链接用于明确标准先修结果及文献定位，不替代本题证明正文。必要上下文与核心支撑证明放在同一 TeX；背景块不另计题数。

已有常用宏包的 TeX Live 下，在 `items` 目录对某题运行两遍：

    xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error 001_stacks_01XF.tex

各题已实际编译两遍，且没有未解析的引用。`receipts/` 保存对应输入 SHA256、编译时间、实际 PDF 页数与结果。编译通过只证明文件能排版，不等于独立数学审稿。

## 来源、归属、许可与修改

本批作者：The Stacks Project Authors；作品：The Stacks Project。使用版本：`a04446e57ec1fbc252a871afcec7752fb2807b14`。每题的 `sources/<编号>/provenance.json` 给出原文件 SHA256、行范围、原命题网页、保留的上下文、精确摘录 SHA256、访问日期和许可证。

`primary.excerpt.tex` 与 `context-*.tex` 保留作者源文本。题文件仅改动引用展示、标题/来源说明，保留原语言、数学内容和证明顺序。037 增补作者 Tag 03GY 的完整因子分解证明，251 增补 Tag 0E9P 的完整下界证明，来源记录给出边界。241 中初等 essential-extension 性质在作者原文写为 Omitted；它是非核心背景，本題分类与单射包络构造的完整作者证明均保留。

Copyright (C) 2005--2025 Johan de Jong and The Stacks Project Authors。作者数学文本及改编 TeX 按 GNU FDL 1.2 或后续版本发布，无不变章节或封面文本；[许可全文](licenses/COPYING)、[贡献者名单](sources/STACKS-CONTRIBUTORS)。其他来源后续加入时各自保留具体许可。

## 数据库复现

`schema.sql` 只定义 `sources` 与 `problems`，不建立研究标签。`origin_class` 区分作者原生 TeX 和保留人类证明的助手忠实转录。只装入已验证条目，待处理清单另列。

    python3 rebuild_database.py
    python3 test_database.py

数据库由同一清单和题文件确定生成。重建核对输入哈希与实际两遍编译回执。测试检查完整 TeX 全文、唯一编号、来源外键、已验证状态、条目数、SQLite 完整性和重复重建的字节一致性。

原始用户 ZIP SHA256：`6ad9d9277ecc8fe39bfe678d4e8ad7cef23e8698217477305b7be6e6bec1b71b`；原始计划 SHA256：`4a1250f52aeb8efff5eb77564150f5e5b1c266fb9e3b2986f21dae3ac876ccca`。旧证据门禁数量不能作为完整可编辑题证完成数。
