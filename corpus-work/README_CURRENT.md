# 862题已核验历史快照

以下内容记录2026-10-02 16:29 UTC已发布862题时的状态。当前包以仓库根README及editable-corpus/gate-status.json为准；本次包为885题。历史提交与核验事实保留。

# 当前题库状态与使用说明

更新时间：2026-10-02 16:30 UTC

## 当前计数

- GitHub已发布并核验：862道合格、唯一、完整可编辑人类题证包
- 当前提交：a40bf9bf862afb8f2560ab5d7d013ba2d54649c3；已完成首个500题检查点
- 106条新逐题CLI通过、756条完全同一材料的历史逐题记录保留；本轮恢复后整包862条重新通过。190项项目测试、27项SQLite恢复测试、1项全文重建测试和20项执行证据测试通过
- 远端14438个预期文件Git哈希全部匹配，14655个文件对象由逐层哈希关联、未截断的分目录树读回核验；整树接口返回过传输错误，未绕过任何权限限制
- 完整SQLite为54,624,256字节，SHA256 c46d362f0d4aed6e156cb83d37238f2b25dcb7f6b1b5b89008eb3e9d40ff9a44；其14,389,124字节gzip无损分为4个有序文件。下载整个editable-corpus后运行python3 restore_database.py，会校验每段、总gzip、完整SQLite及清单再恢复数据库。原始题证全文未删减
- 远端对象身份与本地完整性、外键、全文、862行和逐字节恢复结果一致；不宣称在远端执行SQL或下载读回整个二进制数据库
- 旧377题SQLite及684题gzip保留于historical-database。历史3000/3195是PDF材料证据数，不是当前完整可编辑交付数
- 目标：先完整交付3000题，继续至5000题；每500题整体检查与汇报，逐题准入门禁持续执行

仓库：https://github.com/AlexenderSokolov/cross-theory-formal-database

当前材料：https://github.com/AlexenderSokolov/cross-theory-formal-database/tree/corpus-progress-20261001/editable-corpus

当前不可变快照为frozen-862-v2。题面、完整人类证明、必要新核心、实际稳定编译、INDEX和SQLite逐项绑定。历史草稿、失败版本和恢复记录保留；不将候选或单纯编译成功计入交付数。下一批JEP、ALCO、SIGMA与ToC材料继续规范化和核验，尚未完成远端发布核验的材料单独记录。

## 合格交付要求

每题必须包含独立可编译的完整TeX文档：原作者题面、完整人类证明、必要的新核心支撑和上下文、准确来源及版本/定位、H1/H2/H3及2—4句具体难度理由。一般外部基础结果保留准确引用；缺失新核心证明或未解决的题证对应问题保持待处理。

PDF来源页、图片、链接、摘要和可编译的页面封装不能代替可编辑题面和证明。原始图形可以作为明确归属的图形资产；图形不能承载被省略的证明正文。原始TeX优先；PDF转录必须绑定原页核对记录，并明确转录身份。

每个独立问题只计一次；配套引理、不同格式或同一结果的参数重述不额外计数。保留原编号与原始材料。最高编号、TeX文件数、编译成功数及历史active状态均不能单独作为合格数。只做材料、来源、完整性、粗难度和交付一致性检查，不宣称独立数学审稿或形式化正确性认证。

## 当前入口与历史入口

当前交付包位于publication/tex-remediation-20261002/。其中editable-corpus是发布准备目录，frozen-*是对应不可变材料快照。包内INDEX.md、manifest.json、sources/、receipts/和完整文本SQLite必须一致。不要在发布过程中手改冻结包。

corpus/INDEX.md、corpus/item_status.json、旧PDF封装、旧检查点名称及原执行记录作为历史恢复材料保留。它们不再决定当前完整TeX计数。原始计划保留在参考计划和资源/计划.md；最新用户要求增加GitHub、SQLite及完整可编辑正文交付。

## 校验与复现

使用scripts/validate_corpus.py的editable-delivery模式，逐题以及整包校验。实际命令、便携证据文件、编译依赖、外部构建/回执目录说明见docs/editable-gate/README.md。

    python3 scripts/validate_corpus.py --mode editable-delivery --package PACKAGE --evidence DELIVERY_EVIDENCE.json --build-root BUILD --item ID --report ITEM_REPORT.json
    python3 scripts/validate_corpus.py --mode editable-delivery --package PACKAGE --evidence DELIVERY_EVIDENCE.json --build-root BUILD --report DELIVERY_REPORT.json
    python3 -m unittest discover -s tests -v

当前集成版本已通过190项项目测试，另有27项SQLite恢复测试。当前862完成全新整包校验；106条新逐题CLI和756条完全同一材料的历史成功记录分别保存，862-v2恢复检出再次通过整包校验。历史执行不冒称本轮新执行；材料/运行规则改变、证据缺失或跨过500题检查点时重新逐题运行，实际最终编译日志无重跑请求或重复标签。校验直接读取哈希绑定日志的最后一次编译，不能仅相信回执中为空或缺失的警告字段。新GitHub快照须分别核对，不能沿用旧快照报告。

历史检查必须显式使用--mode historical-evidence；该结果不代表可编辑题证交付。裸用旧--item命令将失败，避免再次混淆标准。

GitHub检出后，先在editable-corpus内运行python3 restore_database.py，无下载地核验并恢复完整SQLite；存在不同数据库时脚本拒绝覆盖。若没有原入库PDF/日志，应使用compile_editable_delivery.py在包外重新编译，并用--receipt-root明确选择新回执。脚本不安装或下载软件，不改写原入库回执；需要已安装XeLaTeX、相应宏包和声明字体。当前工作区的.tex-cache不是可移植性保证。未经检查不得执行外部源包的Makefile或安装脚本。

## 恢复与保留

已完整恢复q3000r1历史材料备份：38份ZIP、111693个文件，逐份及逐文件哈希核对完成。它仅代表可恢复的历史材料。新编辑题证持续保存到GitHub，另有明确标注为待发布材料的安全副本。不得以安全备份替代GitHub交付，也不得把待发布或待处理题目计入目标。

整个任务尚未完成。完整TeX达到3000及5000时分别进行整体验收、打包和交付。
