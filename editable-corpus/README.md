# 高级数学问题与完整人类证明：可编辑题证库

## 当前实际交付

本目录实际交付 **151 题**，不是 3195 题完成。每题均为独立可编辑 `.tex`，包含完整作者原命题、完整作者证明、必要背景、保留的原始宏和可追溯出处。整理说明明确标为非作者正文。数学证明来自可追溯的人类作者，不由助手补造。

- [打开可读总目录](INDEX.md)
- [下载实际全文 SQLite 数据库](corpus.sqlite)：151 条完整题证，TeX 全文存于 `problems.tex_content`；含来源表、稳定编号、难度与依据、版本和原文定位
- [查看机器可读清单](manifest.json)
- [查看当前已恢复及新增的 3002 个记录和格式状态](pending-inventory.csv)

历史 3195 是旧证据门禁数量，原先包含 373 个原生 TeX 和 2822 个 PDF 页面封装。页面封装尚需完整可编辑转录；尚未核对的原生 TeX 同样不能凭字段计为完成。这里只统计实际交付的完整题证。

## 可执行门禁状态

材料核对和实际编译回执已保存。当前151条清单的新完整题证门禁正在生成逐题来源/正文绑定与重新执行记录；上传材料数与最终机器门禁通过数分别记录。当前清单不据此宣称151条均已通过新的可执行门禁。历史清单来自已恢复3000条检查点及逐条恢复/新增编号，不能据此宣称3195条历史元数据均已恢复。

## 阅读和编译

`items/` 每个文件都独立包含作者题面和证明，无需下载整书或约 15 GB 原件。外部链接用于明确标准先修结果及文献定位，不替代本题证明正文。必要上下文与核心支撑证明放在同一 TeX；背景块不另计题数。

已有常用宏包的 TeX Live 下，在 `items` 目录对某题运行两遍：

    xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error 001_stacks_01XF.tex

各题已实际成功编译至少两遍；个别条目实际使用三遍，回执如实记录，且没有未解析的引用。`receipts/` 保存对应输入 SHA256、编译时间、实际 PDF 页数与结果。编译通过只证明文件能排版，不等于独立数学审稿。

中文条目293–295及个别中文整理说明依赖 Noto Serif CJK SC 字体，已在本环境实际测试；没有声称未测试的 Fandol/ctex 回退可用。英文正文使用 TeX Live Latin Modern 字体，1919 的指示符需要标准 Latin Modern Math 字体。必要宏和原图随条目保存，无私人绝对字体路径。

## 来源、归属、许可与修改

来源包括 The Stacks Project、Wen-Wei Li《代数学方法》第二卷，以及 SIGMA、JEP、AHL、LMCS、Documenta Mathematica、Algebraic Geometry 等的署名文献。逐题记录准确作者、作品、版本、题证边界及具体许可证，区分原生作者 TeX 与忠实 PDF 转录。Stacks 使用版本：`a04446e57ec1fbc252a871afcec7752fb2807b14`。每题的 `sources/<编号>/provenance.json` 给出原文件 SHA256、行范围、原命题网页、保留的上下文、精确摘录 SHA256、访问日期和许可证。

`primary.excerpt.tex` 与 `context-*.tex` 保留作者源文本。题文件仅改动引用展示、标题/来源说明，保留原语言、数学内容和证明顺序。037 增补作者 Tag 03GY 的完整因子分解证明，251 增补 Tag 0E9P 的完整下界证明，来源记录给出边界。241 中初等 essential-extension 性质在作者原文写为 Omitted；它是非核心背景，本題分类与单射包络构造的完整作者证明均保留。

Copyright (C) 2005--2025 Johan de Jong and The Stacks Project Authors。Stacks 作者数学文本及改编 TeX 按 GNU FDL 1.2 或后续版本发布，无不变章节或封面文本；[许可全文](licenses/COPYING)、[贡献者名单](sources/STACKS-CONTRIBUTORS)。其他作者论文按其 CC BY 4.0 或 CC BY-NC 3.0 许可保存；逐题许可证见来源记录与 licenses/，不把 Stacks 的许可套给其他来源。必要原作者图在 assets/，不替代任何证明正文。

## 忠实 PDF 转录条目

3005 是 Thompson 的二进制群 T 的二次 Dehn 函数结论，完整新核心证明、必要定义和原图已保留；3198 的稳定化定理以存在稳定化双有理态射为前提；3215 是余维至多二的正则化结论。2839 的 NP/coNP 分离明确以 ST 及指定模型扩张假设为条件，不是无条件解决开放问题；3406 只计外型 A2 群无限亏格的一个主结果，构造中的嵌入引理不另计题数。各条目保留具体原题范围，不加入原证明未覆盖的要求。它们的完整数学 TeX 已放在单个题文件中，原 PDF 只用作来源核对。

## 数据库复现

`schema.sql` 只定义 `sources` 与 `problems`，不建立研究标签。`origin_class` 区分作者原生 TeX 和保留人类证明的助手忠实转录。只装入已验证条目，待处理清单另列。

    python3 rebuild_database.py
    python3 test_database.py

数据库由同一清单和题文件确定生成。重建核对输入哈希与实际两遍编译回执。测试检查完整 TeX 全文、唯一编号、来源外键、已验证状态、条目数、SQLite 完整性和重复重建的字节一致性。

原始用户 ZIP SHA256：`6ad9d9277ecc8fe39bfe678d4e8ad7cef23e8698217477305b7be6e6bec1b71b`；原始计划 SHA256：`4a1250f52aeb8efff5eb77564150f5e5b1c266fb9e3b2986f21dae3ac876ccca`。旧证据门禁数量不能作为完整可编辑题证完成数。
