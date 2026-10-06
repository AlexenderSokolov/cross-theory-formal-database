# 发布候选与实际本地恢复

这一步复用既有完整题证和已通过的实际编译证据，不转录新证明，不赋予许可、难度或语义准入，不操作Git，也不增加远端交付数。先用当前项目规范完成材料审查、逐题/整包门禁和必要页面检查；变体恢复代码先在新目录规范化为固定Repo helper/schema，保留原包。

`corpus-work/scripts/prepare_editable_release.py` 接收完整包、实际build/receipts、实际aggregate及其外部SHA、明确已完成审查的公共文件清单及其外部SHA、全新输出目录。先查看真实`--help`。使用项目Python和`-B`；禁止把glob当成公共许可批准。

```sh
PYTHON=/absolute/project/runtime/python/bin/python
REPO=/absolute/project/repo
"$PYTHON" -B "$REPO/corpus-work/scripts/prepare_editable_release.py" --help
CORPUS_PYTHON="$PYTHON" bash "$REPO/corpus-work/run_prepare_release.sh" \
  --package "$PACKAGE" --build-root "$BUILD" --receipt-root "$RECEIPTS" \
  --aggregate-report "$AGGREGATE_REPORT" --aggregate-report-sha256 "$AGGREGATE_SHA" \
  --public-filelist "$PUBLIC_REVIEW" --public-filelist-sha256 "$PUBLIC_REVIEW_SHA" \
  --output "$NEW_OUTPUT"
```

变量必须来自该批次实际记录，不是已执行回执。shell入口沿用这8个参数；默认读取同项目`runtime/python/bin/python`，也可用`CORPUS_PYTHON`明确指定实际项目环境。错误返回真实非零code，原文件和部分输出保留；不要删文件或复用失败输出目录。

公共输入清单schema为：

```json
{
  "schema_version": 1,
  "status": "public_filelist_review_complete",
  "package_manifest_sha256": "<actual SHA256>",
  "aggregate_report_sha256": "<actual SHA256>",
  "reviewed_package_filemap": {"<every original relative file>": "<actual SHA256>"},
  "master_helper_sha256": {"<each fixed helper below>": "<actual SHA256>"},
  "files": [{"root": "package|build|receipts|master_helpers", "path": "<canonical relative path in that root>", "sha256": "<actual SHA256>"}]
}
```

固定helper是现Repo的`schema.sql`、`rebuild_database.py`、`restore_database.py`、`test_database.py`、`test_restore_database.py`、`restore_validation_artifacts.py`。完整包filemap只核身份；公共`files`才决定哪些原件字节可以进入候选。包内路径原样保留，build/receipts进入实际证据ZIP，master_helpers只能指向这6个可信文件。同一个公共目的路径只能列一次；不要同时重复列包内helper和master helper。

必须包含当前门禁依赖：完整TeX、manifest/evidence/INDEX、逐题provenance、许可、声明资产、源见证/摘录和字符串路径形式的fidelity receipt。原`inline_text`见证已经位于evidence内，只核原UTF8字节及哈希并完整保留；不能为inline补新数学。真实PDF/log/FLS/aux/out和每题receipt须逐条审查，不能用存在的PDF替代题证。rawHTML、privateevents、凭据和未核组件不进入公共列表。无关插画直接排除，不开启额外审批。

准备器输出`NEW_OUTPUT/package/`为公共候选；`NEW_OUTPUT/work/`为私有gzip/ZIP暂存。只按外层`PUBLIC_FILELIST.json`列出的公共路径发布，不能对整个输出目录`git add`。SQLite采用既有v2固定4MiB有序gzip分段，编译证据沿用既有有序ZIP分段格式；描述记录顺序、大小、SHA和实际manifest数量。原SQLite/旧运输分段不直接发布。

shell入口在`NEW_OUTPUT/verification/`创建新副本，实际执行标准数据库恢复、证据恢复、`test_database.py`和`test_restore_database.py`、完整显式editable-delivery aggregate，并再次核全问题/来源SQL投影。成功记录在`verification/LOCAL_RESTORE_VERIFICATION.json`及各阶段真实日志。只调用已核固定项目程序；不执行TeX、作者class或上游构建脚本。复制/恢复既有实际编译证据不意味着重新编译。

同FS准备可能硬链接复用不可变原件；不要改/chmod这些共享文件，也不要用既有build/receipt根重编。源码、许可、资产、body或运行程序变化时，使用新目录并重跑受影响范围。准备和本地恢复通过仍不代表远端交付；单一授权发布者比较远端分支、提交明确文件清单、从确切公共commit取回完整分段，实际恢复并跑全文SQL及门禁，之后才增加远端主库计数。

这条发布路线接在[增量流程](incremental-workflow.md)和批次合并实际输出之后；来源块、难度粗筛、语义去重与唯一合并者边界沿用现行规范。不得用本工具替代30,000题目标或增加未来a/c、桥梁、距离标签。
