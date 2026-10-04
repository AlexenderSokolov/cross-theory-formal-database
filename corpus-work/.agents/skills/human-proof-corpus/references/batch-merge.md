# 可复用可编辑题证批次合并 CLI

合并者复用已测试的旧merge核心与现行editable-delivery门禁，将已准入小包并入真实基线。所有输出进入新目录；原数学正文、来源、资产、旧包和旧构建不改。本文只说明现行契约，不增加审批层或调度平台。

## 输入

spec JSON提供base与按序incoming数组，每项含package、manifest_sha256、build_root、receipt_root；再提供固定master_helpers目录与真实compile_launcher绝对路径。

外部合并者的semantic-review必须绑定原base与全部incoming manifest/ID，含status=material_review_complete、空holds/duplicates、真实非空basis及compile_reuse_basis。reviewed_filemaps覆盖全部原package文件，reviewed_artifact_filemaps覆盖每项实际build/receipts；programme_sha256绑定两合并脚本、delivery工具、validator/adapter、compile helper及launcher；master_helper_sha256固定schema、rebuild/restore与两测试文件。

ROOT-REVIEW-SKELETON-1497-r001.json只供复制字段结构；其external_root_review_required及空basis不能直接通过。程序不生成材料准入。扩批时重新绑定实际完整输入，不给旧review只改数量。

## 命令

~~~sh
"$PYTHON" -B "$REPO/corpus-work/scripts/merge_editable_batch.py" \
  --spec /absolute/spec.json \
  --semantic-review /absolute/root-review.json \
  --semantic-review-sha256 <机器读取的64位SHA256> \
  --output /absolute/fresh-output
~~~

应由机器计算review文件SHA，并直接通过subprocess argv传入，不手抄。CLI拒绝既有输出、dangling symlink、全层重复JSON键、未绑定review、重复ID/claim/已有alias、来源冲突和缺资产。同DOI source/许可路径差异不会自动同义化，先由合并者明确规范化并重新绑定，或者保留具体拒绝。

## 执行与续接

程序只把中性恢复代码规范化为固定master版本并重建完整SQLite；TeX/manifest不变。每个incoming真实过门禁，逐步union保留每步身份及外部review来源。顶层旧merge-preparation.json作为派生全局数据重新生成，其他数学/来源/资产冲突继续拒绝。

最终用明确的merged build/receipts真实执行aggregate。查看batch-result.json、reports/aggregate.json与incoming-N.json；PID、目录存在不是通过。失败partial保留，按stdout/stderr定位后另用新输出目录，不能覆盖旧输入。

同FS不可变实际PDF/log/receipt用硬链接，跨FS用copy2。**reuse build/receipt目录不得chmod、编辑或用作重编输出**。输入、资产、programme或依赖身份变化时，用全新build/receipt roots重检受影响范围。当前gate核对实际input/dependency/PDF/log/receipt；历史helper身份来自外部真实执行及版本对照，不能虚构为旧receipt自带字段。合并不做fresh编译，不声明远端交付。

## 实测记录

25项工程测试实际通过：repo/corpus-work/tests/test_merge_editable_batch.py。覆盖dupID/claim、source冲突、缺asset、既有输出、deep duplicateJSON、single/batch dangling输出和复合包派生prep差异；不是数学认证。

外部Root review固定1032及1497、2311、1578三包，得到1033→1034→1035；三个incoming和全1035aggregate真实通过，主代理另核全文投影/integrity/FK/uniqueID。这完成本地20净新增试点。该记录当时remote主库1015、公开主库恢复待进行；后续计数须查最新CURRENT。

- 真实spec/review：operations/pilot20-reviewed-batch-r003/
- 真实结果：snapshots/pilot20-batch-r001/batch-result.json
- 最终package：snapshots/pilot20-batch-r001/steps/step-3
- immutable编译复用：snapshots/pilot20-batch-r001/build与receipts
- 实际aggregate：snapshots/pilot20-batch-r001/reports/aggregate.json
- 全文核验摘要：reports/union1035-summary-r001.json

实测manifest SHA256：e423634308912ed0c60b78b8eecf6a778e095a6e73a6ca64805d7adcdd9bcd2f

实测SQLite SHA256：84de2eb0fe09a1bca0e1965b4aec28e8db0b61e9d318e474c73d3e5d1c0715ee

实测aggregate SHA256：f01b2ccab51ff650fec11ed6660bc7888c83b58dbf6436f3fe65f44f3869aec2

发布候选和真实本地恢复按 [release-preparation.md](release-preparation.md) 执行；复用 `corpus-work/run_prepare_release.sh`，明确签审文件清单与实际aggregate身份；远端精确恢复成功才计交付。
