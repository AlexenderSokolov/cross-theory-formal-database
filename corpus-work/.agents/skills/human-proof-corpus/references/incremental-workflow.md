# 增量题证交付：可复用流程

适用于本仓库的人类高级数学题证采集、规范化、并行处理和交付。用户已授权的服务器、分支和公开范围继续有效；本流程不扩大授权，也不要求对同范围正常操作重复确认。先读仓库根 `PROJECT.md` 和 `handoff/yupeng/CONTINUATION_CURRENT.json` 的相关部分。

## 工作者的最小交接

领取不重叠的作品／版本块；先下载原 PDF、原生 TeX／网页与必要资产到服务器缓存，再提取。原件按 URL、作品版本和 SHA256 共用，`source0` 保持原字节。工作者只写自己的候选及报告目录；一个合并者独占编号、主库清单、INDEX、SQLite 和 Git。

每题交接实际题证 TeX、原始命题／证明／新局部核心的精确定位、来源与逐组件许可、H1/H2/H3 的 2—4 句具体残余证明义务、实际编译回执及最终日志、全页 QA、全文 SQLite、逐题与整包门禁、可恢复包和 READY。READY 必须列出实际完成范围及待办；存在文件、渲染了图片或返回 PID 都不是通过证据。

只处理题目、完整人类证明及必要数学背景／图。无关插画、品牌页和其他非数学素材直接不进入交付；必要数学图的公式和关键文字必须可编辑，资产仍须具备再分发依据。许可不明而证明又必需的资产才隔离本题；不要为无关美术开展调查。

缺少新题包、数据库、编译产物是需要生成的工作，不是“来源缺失”。普通 wrapper、字段、宏、字体和排号问题要修复；不得安装／执行未知上游类文件、构建脚本，或用假字体／空宏掩盖失败。真实缺证、核心条件无法辨明、版本冲突、低难、语义重复或必要组件许可不明，记录具体 hold，继续其他来源。

## 把原文事实与格式模板分开

模板只复用键名、目录布局、标准排版和程序接口。作者、题名、DOI、版本、页码、命题号、难度理由、source_check 和许可必须逐题生成。先比较实际出版版；旧候选把 Proposition 写成 Theorem 只需记录并校正类型／定位，不能因此换一个结论或自动判为版本冲突。

原证明、假设、量词、常数和公式不修补。不增加 a/c、桥梁、距离等研究标签，也不进行独立数学审稿、投票或反例研究。原文普通漏词／括号／索引瑕疵保留并单独注明；只有完整原证明与实际调用已明确所需条件时可按该原主张继续。主要证明义务仍不清楚则 hold，不猜作者本意。

参考文献必须从该版本原生 `.bib`／`.bbl` 或出版 PDF 忠实转录。不要从记忆填作者／作品，也不要由 `S99`、`HKN` 或年份猜引用。原 PDF 字母标签与原生 citekey 排序不一定一致，须记录实际对应；保留原版本、出版信息、页码和 arXiv／DOI。只转录本题保留正文实际使用的引用及必需先修；完整无关书目不应扩大成任务。新局部核心不能改成指向外部 PDF 的链接。

## 编译与门禁

先查当前程序 `--help`。在项目既有隔离环境以真正 TeX Live、禁用 shell escape 编译；包只读，构建和回执在包外，不暴露网络和凭据。Yupeng 的 wrapper 需要显式传包与输出根目录；查询编译参数时运行原编译脚本的 `--help`，不要裸调用需要这些参数的 wrapper。

```sh
"$PYTHON" "$REPO/corpus-work/scripts/compile_editable_delivery.py" --help
"$COMPILE_ISOLATED" --package "$PACKAGE" --build-root "$BUILD" \
  --receipt-root "$RECEIPTS" --item "$ID" --engine xelatex
"$PYTHON" "$REPO/corpus-work/scripts/validate_corpus.py" --mode editable-delivery \
  --package "$PACKAGE" --evidence "$PACKAGE/delivery-evidence.json" \
  --build-root "$BUILD" --receipt-root "$RECEIPTS" --item "$ID" --report "$ITEM_REPORT"
"$PYTHON" "$REPO/corpus-work/scripts/validate_corpus.py" --mode editable-delivery \
  --package "$PACKAGE" --evidence "$PACKAGE/delivery-evidence.json" \
  --build-root "$BUILD" --receipt-root "$RECEIPTS" --report "$AGGREGATE_REPORT"
```

这些变量由实际项目环境填写，不是已执行回执。先同步 manifest、逐题 provenance、INDEX、来源与完整 SQLite，再运行逐题门禁；整包通过才能作为可合并包。报告必须放在独立路径。来源工作者直接调用可信 Python validator，可写自己候选目录内的 reports；该验证器不执行 TeX。主代理通过 operations/env-isolated.sh 验证时才要求报告位于项目 ROOT/reports 下，按工作单分独占子目录。隔离编译仍必须走真实 compile-isolated，不受这条报告路径区别影响。

成功需要实际 exit 0、正确 qualified count、全局及每个 item 的 errors 都空、没有 failed item。`errors: []` 的顶层值不能遮盖嵌套 item 失败。可用 `corpus_delivery_tools.py check-report` 汇总，但它不替代真实门禁。

编译至少 2、最多 4 遍，最终真实日志必须稳定。实际查看新输出各页和关键原文页，尤其公式号、Lemma／Theorem 引用类型、图中数学标签、证明末段与文献。修 bibliography、字体、counter 或 TeX 后要真实重编；只改非编译元数据可在全部编译输入／资产／运行程序身份一致时复用回执，同时重跑受影响 SQL／门禁，说明复用范围。

## 固定恢复程序与合并

不要为每题重新写 SQLite 恢复代码。采用固定主库 `rebuild_database.py` 和相同 `schema.sql`，记录程序 SHA。发现单题包带了变体，在新目录调用 `corpus_delivery_tools.py normalize-recovery`，保留原包，检查题证／清单身份未变，真实重建全文 SQL 并重新跑该题门禁。它只准备材料，不自动授予合格或发表状态。

同一作品／版本的 `sources` 记录共用同一许可见证；逐题 proof locator 与 provenance 独立。许可路径不同而文件字节和其他来源字段完全相同，可以在新包显式规范化并对账；其他字段冲突不能靠换 source_id 绕过。

单一合并者使用 [批次合并 CLI 与已验证实例](batch-merge.md)，复用 `merge_editable_packages.py`／`merge_editable_batch.py` 的当前接口：固定 base 和 incoming 的清单身份，输入明确 root 材料／语义去重决定和完整文件表，输出全新包。根据实际清单计算数量，不写死 975→1002 或某题号。复用当前实际编译产物时核 input／资产／helper 身份；合并后执行实际全文投影和整包门禁。失败保留部分输出与日志，不改基库，不覆盖旧目录。

## CAS 和公开恢复

`corpus_delivery_tools.py pack-cas` 只接受明确审查的文件列表：`status=public_filelist_review_complete`，每项含 `source`、包内相对 `path`、实际 `sha256`。列表代表已完成的内容／权利审查；程序不会做或伪造该审查。不要按工作目录全量 glob 发布，不包含 private events、原始 HTML、凭据、未核许可原件或未知类文件。

Zip blob 必须携带 Unix 普通文件类型 `S_IFREG`；只写权限位会被严格恢复程序拒绝。manifest 记录每条路径、SHA、大小、mode 和 archive 身份。用 `verify-cas` 固定外部 manifest 与可信恢复 helper 的 SHA，在新目录实际恢复全部文件、核 hash／size／mode，然后运行全文 SQLite 投影和恢复后的完整门禁。程序返回“恢复字节已核”不代表题目已合格。

公开提交使用显式文件清单、正常 push，先读远端分支，保留并发成果。没有服务器凭据时沿用已授权的轻量 bundle 中转；实际核 bundle 后再推送。提交后从公开远端取回该 commit 的清单与分段／CAS，在服务器新目录实际恢复、全文 SQL／门禁通过后才能增加对应远端交付数。主库发布数和独立待合并备份数分开记，不能把它们重复相加。

## 用实测消除返工

- 优先修复已完成正文的 wrapper／元数据，避免工作者遇到普通工程错误就结束。
- 同一源的已完成数学正文和完整必要 core 不重复提取；已验证身份一致的历史证据按受影响范围复用。
- 当前 native agent 槽位、服务器模型进程、排队任务、CPU 编译并行分别记录；接口限流时排队，CPU 多不代表模型请求槽位多。进程真实终止后才接续，观察超时不是终止。
- 每题立即检查；每 25—100 新通过项保存可恢复检查点，每 500 新合格题全库对账。继续 20 净新增试点→100／500→30,000 的原目标，不以工具或文档完成代替题库完成。
- 中断前保存 commit、计数依据、源 owner／位置、hold、必要文件和恢复命令。新的经验只针对已观察的失败，不积累无关审批和复杂平台。

### 可复用工具命令

```sh
"$PYTHON" "$REPO/corpus-work/scripts/corpus_delivery_tools.py" check-report --report "$ITEM_REPORT" --expected-count 1
"$PYTHON" "$REPO/corpus-work/scripts/corpus_delivery_tools.py" normalize-recovery --package "$PACKAGE" --master "$FIXED_MASTER" --output "$NEW_PACKAGE" --helper-sha256 "$REBUILD_SHA256" --schema-sha256 "$SCHEMA_SHA256"
"$PYTHON" "$REPO/corpus-work/scripts/corpus_delivery_tools.py" pack-cas --spec "$REVIEWED_PUBLIC_FILES_JSON" --output "$NEW_CAS_DIR"
"$PYTHON" "$REPO/corpus-work/scripts/corpus_delivery_tools.py" verify-cas --manifest "$CAS_MANIFEST" --expected-manifest-sha256 "$CAS_MANIFEST_SHA256" --restore-helper "$REPO/handoff/materials/restore_history.py" --restore-helper-sha256 "$RESTORE_HELPER_SHA256" --destination "$NEW_RESTORE_DIR"
bash "$REPO/corpus-work/run_delivery_reuse_checks.sh" "$PYTHON"
```

变量必须来自本次实际输入及外部固定身份。check-report只检查既有报告，不能伪造一次门禁执行。normalize-recovery同时携带恢复程序及其测试依赖；CAS输出和恢复目标拒绝现有文件／目录与符号链接。JSON重复键必须拒绝，不能让后写的passed掩盖前写的failed。SHA从机器字段取得并检查64位，避免终端折行手抄。

发布候选和真实本地恢复按 [release-preparation.md](release-preparation.md) 执行；复用 `corpus-work/run_prepare_release.sh`，明确签审文件清单与实际aggregate身份；远端精确恢复成功才计交付。

CAS当前接口使用仓库 `handoff/materials/restore_history.py`（`--manifest`、`--expected-manifest-sha256`、`--destination`）；`restore_pending.py`接收的是40题运输描述及`--expected-transport-sha256`，不可混用。执行前读取真实`--help`并固定对应helper身份。打包只选逐题必要编译输出，排除 `.cache/fontconfig` 等可重建运行缓存；排除不等于删除。

术语宏（例如 `\gls`）必须使用原作者定义的实际符号／展开；不得把key直接打印或用空 `\newglossaryentry`、假字体宏糊过编译。普通页分隔等纯格式宏可据原定义规范化；数学字母／字体和映射须忠实保留，变更后真实重编并全页核对。

已实测的[验证产物恢复链](artifact-chain.md)可复用明确已公开基础archive与新增小archive，原schema1不改，所有源/最终字节显式对账。源码与小包通过不等于整库通过；本项目首次真实1040链恢复及完整门禁见handoff/yupeng/reusable-tools/ARTIFACT_CHAIN_ACTUAL_FULL1040.json。两类SQLite程序CLI/API不同，执行前读help；通用重建入口是固定 `rebuild(root,output)`，原rebuild_database.py CLI仅--output且包根来自保存程序目录，不接受虚构--package。
