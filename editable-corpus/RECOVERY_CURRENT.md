# 1115题主库恢复

正文、INDEX与全文SQLite的当前版本以本目录manifest及database-delivery.json为准。
历史文件保留；只恢复当前描述中列出的分段，不把旧备份再次计数。

```sh
python3 restore_database.py
python3 restore_validation_chain.py --chain validation-chain.json --expected-chain-sha256 572a6c8a0ff20e053c10d83ea0c18f774a8ca52b311748f1bbb8a9d4df0f8471 --archive-root based5c97b8febfed495=. --archive-root delta02099617a5431ad0=validation-artifact-deltas/delta02099617a5431ad0 --archive-root deltaaedcd63da893bd42=validation-artifact-deltas/deltaaedcd63da893bd42 --schema1-helper restore_validation_artifacts.py --expected-helper-sha256 33548dad0cfb3a268346d896ba2ca4340c1171df8f00d3c08bb18a95723c3594 --output /absolute/new/artifacts
```

然后执行corpus-work/scripts/validate_corpus.py --mode editable-delivery，传入实际package、delivery-evidence、恢复后的build和receipts及独立report。公开完整恢复成功后才更新交付数。当前组批复用未变题证编译及合并aggregate；公开恢复仍执行必要完整gate。
