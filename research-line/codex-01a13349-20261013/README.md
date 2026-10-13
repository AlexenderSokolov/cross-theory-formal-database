# 第五条Codex主机收题与上传

统一准则见../../PROJECT.md。作者承担原始数学责任。收完整作者题证、续证与必要上下文，H2/H3用途，定向去重，编译建库和上传。不重证、不补证、不加假设、不审稿、不双审、不哈希/逐字节核对、不做日志工程。

模型统一gpt-6.1-sol / medium。材料代理只写各自lane；根代理独占jobs、数据库、索引和Git。

|lane|prefix|独占来源|
|---|---|---|
|hyperlogic-complexity|CP01A13349-HC-|arxiv:2311.15675v9；doi:10.4230/LIPIcs.CSL.2025.10|
|modal-fixed-points|CP01A13349-MF-|doi:10.4230/LIPIcs.CSL.2025.25|
|optical-diagrammatic-algebra|CP01A13349-OA-|doi:10.4230/LIPIcs.CSL.2025.38；arxiv:2402.17693v2仅身份别名，使用CC BY出版版|

约25道净新增一批，上传后继续，不设领域配额，不拆小引理或直接推论凑数。准备分支上传不计生产主库公开增量。

从本task_root运行：
```bash
bash operations/run_assemble.sh --task LANE/TASK/task.json
bash operations/run_compile.sh --job jobs/TASK/r001 --resume
bash operations/run_export.sh --batch batch-001 --limit 25
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python operations/prepare_upload.py batch-001
```

修正失败包装后使用run_assemble.sh --refresh --assemble-only，再run_compile.sh --resume；成功成品直接复用。上传用本线独立corpus-relay-01a13349.git，不共享其他线引用。

## 实际成品与当前来源

本线批次入口[batch-001索引](delivery/batch-001/INDEX.md)及[SQLite](delivery/batch-001/corpus.sqlite3)。实际采用来源及同作别名见[来源分工](reference/SOURCE_ALLOCATION.json)。CSL2025.25与.38目前仅保留来源，不计题；SIGMA与后续LMCS原生源按独占分工继续补充。

批量装配使用`bash operations/run_pending.sh`，只处理尚未装配的新任务；已成功题直接跳过。实际修正失败任务后，把其完整任务号作为参数传给同一脚本才重试，不重复编译成功题。
