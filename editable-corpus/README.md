# 高级数学问题与完整人类证明：可编辑题证库

## 当前实际交付

本目录实际交付 **911 题**，不是 3195 题完成。每题均为独立可编辑 `.tex`，包含完整作者原命题、完整作者证明、必要背景、保留的原始宏和可追溯出处。整理说明明确标为非作者正文。数学证明来自可追溯的人类作者，不由助手补造。

- [打开可读总目录](INDEX.md)
- [下载全部实际全文SQLite有序分段](database-parts)：911 条完整题证，下载后运行 `python3 restore_database.py` 完成一次无损解压；TeX 全文存于 `problems.tex_content`；含来源表、稳定编号、难度与依据、版本和原文定位
- [查看机器可读清单](manifest.json)
- [查看当前已恢复及新增的 3002 个记录和格式状态](pending-inventory.csv)

历史 3195 是旧证据门禁数量，原先包含 373 个原生 TeX 和 2822 个 PDF 页面封装。页面封装尚需完整可编辑转录；尚未核对的原生 TeX 同样不能凭字段计为完成。这里只统计实际交付的完整题证。

## 可执行门禁状态

当前911题在冻结清单SHA256 `278434a086f8ed1e625b6a7e3a72693910918121eaf54346c3f88b23a298bc2e` 上通过本轮全部逐题CLI及整包完整可编辑交付门禁。[正文/来源证据](delivery-evidence.json)、[门禁记录](gate-status.json) 与 [逐题执行记录](individual-execution-status.json) 已保存。本次在已核验885题上增加26题。

本轮源文类型门禁增加准确的已核对出版全文转写类别，因此911题全部重新执行显式逐题CLI，911题通过，历史执行复用为0；本轮整包门禁也重新核对全部911题。230项项目测试通过。机械门禁不等于独立数学审稿。

2445保留 `human_authored_checked_published_transcription` 身份：完整CC BY3.0出版源PDF、逐行来源及完整人类作者题证随包提供。私人非独占许可原生辅助归档及类文件未公开或执行。收集时待准入状态及旧表示说明作为哈希固定历史保存，当前新准入说明与已复核运行程序绑定，不冒称公开原生归档许可。ToC当前准入由包内哈希固定记录确认。

1100完整保留六个原有换行防护及七处已批准分隔符省略，42页与原批准版逐像素一致。2517页51未选末段/QED的至多3.6pt间距差异经原文核对及复核接受，四题总计139页中138页逐像素一致；所有所选主要证明页一致。798上下文矩阵保留14.55637pt与16.62978pt最终警告；720保留2.09497pt警告；792保留内部TikZ节点盒10.10698pt警告。实际日志均保留，均经视觉安全复核，不压制或称为无警告。

完整SQLite为60,465,152字节，以15,984,486字节无损gzip流分为4个有序文件。下载 [全部分段](database-parts) 及 [顺序/哈希清单](database-delivery.json)，保持目录结构并离线恢复。恢复核对各段、gzip、SQLite哈希、完整性、外键、911条记录和每题完整TeX全文，原子创建 `corpus.sqlite`，拒绝覆盖不同现有文件。旧历史数据库保持原字节。

需已安装XeLaTeX、所需宏包/字体及pypdf；辅助程序不下载或安装依赖。在仓库根目录运行：

    python3 editable-corpus/restore_database.py
    python3 corpus-work/scripts/compile_editable_delivery.py --package editable-corpus --build-root .editable-build --receipt-root .editable-receipts
    python3 corpus-work/scripts/validate_corpus.py --mode editable-delivery --package editable-corpus --evidence editable-corpus/delivery-evidence.json --build-root .editable-build --receipt-root .editable-receipts --report editable-delivery-report.json

逐题验证再加 `--item 编号`。缺少真实匹配编译文件、源文绑定或完整正文会失败关闭。历史3195条元数据不能代替当前完成数。

## 阅读和编译

`items/` 每个文件都独立包含作者题面和证明，无需下载整书或约 15 GB 原件。外部链接用于明确标准先修结果及文献定位，不替代本题证明正文。必要上下文与核心支撑证明放在同一 TeX；背景块不另计题数。

已有常用宏包的 TeX Live 下，在 `items` 目录对某题运行两遍：

    xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error 001_stacks_01XF.tex

各题已实际成功编译至少两遍；个别条目实际使用三遍，回执如实记录，且没有未解析的引用。`receipts/` 保存对应输入 SHA256、编译时间、实际 PDF 页数与结果。编译通过只证明文件能排版，不等于独立数学审稿。

中文条目293–295及个别中文整理说明依赖Noto Serif CJK SC字体，已实际测试；未测试的Fandol/ctex回退不作保证。英文正文使用TeX Live Latin Modern字体，1919的指示符需要Latin Modern Math字体；2590保留已测试的原整理字体，2606出版社姓名字符ȩ另需DejaVu Serif，限用于该字符。806需要标准TeX宏包physics1.3、tensor2.2和faktor0.1b，已使用官方CTAN版本实际测试。必要宏和原图随条目保存，无私人绝对字体路径。编译辅助程序不安装依赖。

## 来源、归属、许可与修改

来源包括 The Stacks Project、Wen-Wei Li《代数学方法》第二卷，以及 SIGMA、JEP、AHL、LMCS、Documenta Mathematica、Algebraic Geometry 等的署名文献。逐题记录准确作者、作品、版本、题证边界及具体许可证，区分原生作者 TeX 与忠实 PDF 转录。Stacks 使用版本：`a04446e57ec1fbc252a871afcec7752fb2807b14`。每题的 `sources/<编号>/provenance.json` 给出原文件 SHA256、行范围、原命题网页、保留的上下文、精确摘录 SHA256、访问日期和许可证。

`primary.excerpt.tex` 与 `context-*.tex` 保留作者源文本。题文件仅改动引用展示、标题/来源说明，保留原语言、数学内容和证明顺序。037 增补作者 Tag 03GY 的完整因子分解证明，377 增补 Tag 0E9P 的完整下界证明，来源记录给出边界。241 中初等 essential-extension 性质在作者原文写为 Omitted；它是非核心背景，本題分类与单射包络构造的完整作者证明均保留。

Copyright (C) 2005--2025 Johan de Jong and The Stacks Project Authors。Stacks 作者数学文本及改编 TeX 按 GNU FDL 1.2 或后续版本发布，无不变章节或封面文本；[许可全文](licenses/COPYING)、[贡献者名单](sources/STACKS-CONTRIBUTORS)。其他作者论文按其 CC BY 4.0 或 CC BY-NC 3.0 许可保存；逐题许可证见来源记录与 licenses/，不把 Stacks 的许可套给其他来源。必要原作者图在 assets/，不替代任何证明正文。

## 忠实 PDF 转录条目

3005 是 Thompson 的二进制群 T 的二次 Dehn 函数结论，完整新核心证明、必要定义和原图已保留；3198 的稳定化定理以存在稳定化双有理态射为前提；3215 是余维至多二的正则化结论。2839 的 NP/coNP 分离明确以 ST 及指定模型扩张假设为条件，不是无条件解决开放问题；3406 只计外型 A2 群无限亏格的一个主结果，构造中的嵌入引理不另计题数。各条目保留具体原题范围，不加入原证明未覆盖的要求。它们的完整数学 TeX 已放在单个题文件中，原 PDF 只用作来源核对。

## 数据库复现

`schema.sql` 只定义 `sources` 与 `problems`，不建立研究标签。`origin_class` 区分作者原生 TeX 和保留人类证明的助手忠实转录。只装入已验证条目，待处理清单另列。

    python3 restore_database.py
    python3 test_restore_database.py
    python3 test_database.py
    python3 rebuild_database.py

数据库由同一清单和题文件确定生成。重建核对输入哈希与实际两遍编译回执。测试检查完整 TeX 全文、唯一编号、来源外键、已验证状态、条目数、SQLite 完整性和重复重建的字节一致性。

原始用户 ZIP SHA256：`6ad9d9277ecc8fe39bfe678d4e8ad7cef23e8698217477305b7be6e6bec1b71b`；原始计划 SHA256：`4a1250f52aeb8efff5eb77564150f5e5b1c266fb9e3b2986f21dae3ac876ccca`。旧证据门禁数量不能作为完整可编辑题证完成数。

## 历史排版中间件的保存范围

本包保留作者源文、正文绑定、实际最终编译回执、必要数学图示与许可。重复的历史QA页图、旧生成PDF及编译中间件只在本地可恢复档案/备份中保留，不冒充GitHub里的当前自含验证文件。逐文件哈希及本地历史位置见 [中间件省略索引](sources/DERIVED_RENDER_ARCHIVE_INDEX.json)。当前实际编译文件需按上述命令在下载后的外部目录重新生成。

806需要标准TeX宏包physics1.3、tensor2.2和faktor0.1b，已使用官方CTAN版本实际测试；源码和回执没有私人绝对字体路径。编译辅助程序不安装依赖。

来源/正文证据JSON仅移除字符串外的排版空白，所有字符串、数字词法和数组顺序均精确保留；原始美化JSON另有哈希固定的历史字节保留。1005使用随包提供的官方listofitems1.65运行文件及LPPL许可，不要求辅助程序下载或安装。
