# 1065题主库恢复

正文、INDEX与全文SQLite的当前版本以本目录manifest及database-delivery.json为准。
历史文件保留；只恢复当前描述中列出的分段，不把旧备份再次计数。

```sh
python3 restore_database.py
python3 restore_validation_artifacts.py --destination /absolute/new/artifacts
```

然后显式执行当前仓库corpus-work/scripts/validate_corpus.py --mode editable-delivery，传入实际package、delivery-evidence、恢复后的build和receipts及独立report。公开恢复成功后才更新交付数。当前组批使用一次主库重建和一次aggregate；合格题证的历史真实编译按不变输入复用。
