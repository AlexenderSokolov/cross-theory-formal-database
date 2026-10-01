# 当前题库状态与使用说明

以 corpus/INDEX.md、corpus/item_status.json 与 scripts/validate_corpus.py 的最新验证结果为当前依据。原上传包中的历史目录、旧交付ZIP名称、难度seed、RECOVERY/BATCH_STATE叙述保留为历史记录，不是本次重新核验后的合格认证。

只有状态active且逐题完整门禁通过的唯一问题才计入3000目标。quarantined保留原编号和原件，但不计数；最高编号不等于题目总数。H1/H2/H3仅为粗难度分层。难度理由与原文核对为整理判断，不宣称独立数学审稿或形式化正确性认证。

当前新增自然语言条目两种忠实呈现方式：
- native_tex：固定版本原生TeX，完整作者题证与必要上下文；正文引用改为稳定来源链接，原始摘录另存。
- source_pdf_pages：原作者PDF所选题证与必要背景页原样嵌入可编译TeX；前置页明确唯一计数的命题，附带页中的其他命题不额外计数。

本次执行计划见 EXECUTION_PLAN.md，当前进度见 RUN_STATE.json，门禁和旧材料问题见 audit/。实际编译PDF与日志按 compile_report.json 中路径定位。遇到缺失或哈希变化，请重跑门禁，不信任旧PDF。

命令（工作目录为本目录）：

    python3 scripts/validate_corpus.py
    python3 scripts/validate_corpus.py --item 241
    python3 scripts/compile_all.py --item 241

工作区TeX资源仅安装在 .tex-cache/；编译脚本自动配置，不修改系统安全设置。原作者许可证按来源保留。目录中的外部源码不得未经检查直接运行其Makefile或其他安装脚本。

目标尚未完成时，任何检查点只代表可恢复的中间状态，不能宣称3000题已经完成。

复现环境记录在 ENVIRONMENT_SNAPSHOT.json，核心 Python 依赖锁定在 requirements-core.txt。本次实际运行环境为 Linux、Python 3.12、XeLaTeX；新环境还需要可用的 XeTeX/xdvipdfmx、Noto Serif CJK SC 字体和常用 LaTeX 宏包。根目录 scripts/ 与 tests/ 是当前支持的执行入口；audit/ 中的旧脚本副本、红灯测试和临时实验是历史诊断材料，不替代当前入口。

原生 Stacks 封装从600检查点起使用简短 Tag 页眉，完整题名和原始数学正文不变。批量门禁只在一次调用内复用按路径及 mtime/ctime/大小/inode 校验的文件快照；独立 validate_corpus.py 和每批最终门禁均重新读取，不依赖旧会话缓存。

体积较大的恢复归档可能分成多个独立 ZIP：全部解压到同一父目录即可重建 corpus-work，各分包路径互不重复。检查点记录保留每包的哈希及文件身份；从500到1200题的各百题归档均已做过异路径解压后的完整门禁验证；后续结果见 CHECKPOINTS.json。打包省略的仅是 Git 内部目录、Python缓存、临时锁/临时文件和非材料软链接，已入库的代码、原件、元数据和当前编译产物以恢复验证为准。

来源身份门禁检查 source_version 中明确 DOI 与 locator 的一致性，并对可识别的 ALEA /articles/vN/N-NN.pdf 地址检查目录卷号与文件名卷号一致。它不代替官方URL访问和PDF字节哈希核对；新来源仍须保留实际出版页、头部和许可证据。当前80项回归测试通过，红灯复现与修复证据保留在 audit/。

从1500题批次开始，只接收已宣布完成的完整来源批次；candidates/finalized-blocks.json 记录已完成批次上限。早期五题快照与正在修订的 ready 文件不直接进入入库队列。暂存脚本保留所有未入库身份，并用集合断言排除已在当前 active 集合中的身份；批量入库仍执行独立最终完整门禁。

入库前预检 INDEX 展示字段，拒绝标题、作者等字段中的管道符或换行，保持条目隔离状态；数学条件应在编辑标题中用清晰文字表达，原作者证明正文不受该展示规则影响。

PDF页证据门禁同时检查 statement_pages、proof_pages 和已声明 context_pages 的有效页码、原件页数边界及封装实际覆盖；不得漏掉只承担必要背景的声明页。
