# 1015道完整可编辑人类证明题库

由固定975题及40题规范增量组成。LOCAL1002的27题属于这40题，1907不计。
本版本已在Yupeng实际完成1015题fresh编译、40新增与5wrapper改动的45逐题CLI、1015整包CLI、全文SQLite及独立恢复回放。5题仅修前导区数学数组排版，所有author statement/proof/core spans与原native字节相同。

从新克隆目录恢复数据库：`python3 editable-corpus/restore_database.py`。
在外部新目录恢复真实编译产物：`python3 editable-corpus/restore_validation_artifacts.py --destination /absolute/new/artifacts`。
再执行仓库corpus-work/scripts/validate_corpus.py --mode editable-delivery，显式package/evidence、build-root=/absolute/new/artifacts/build、receipt-root=/absolute/new/artifacts/receipts、report=独立位置。

database-delivery.json与5个有序分段固定完整SQLite字节；validation-artifact-delivery.json及65个分段固定1015实际编译的7103个PDF/log/FLS/aux/receipts。原历史收据保留，fresh override明确选择本次产物。须取得完整分段、核对哈希并实际恢复，不用候选SQLite计题。

作者原题、假设、完整人类证明、新局部核心、来源版本及逐组件许可证都保留。技术门禁不独立认证数学正确性。当前远端交付核验见handoff/yupeng/CURRENT_DELIVERY.json；未经远端恢复确认不能把提交或上传当作完成。
