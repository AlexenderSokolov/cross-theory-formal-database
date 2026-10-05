# 1090题主库恢复

正文、INDEX与全文SQLite的当前版本以本目录manifest及database-delivery.json为准。
历史文件保留；只恢复当前描述中列出的分段，不把旧备份再次计数。

```sh
python3 restore_database.py
python3 restore_validation_chain.py --chain validation-chain.json --expected-chain-sha256 f3cdef5d61b2e31c17a0e33636b6969a8f42a6e9c8d914062cb17dfb8e43e80e --archive-root based5c97b8febfed495=. --archive-root delta02099617a5431ad0=validation-artifact-deltas/delta02099617a5431ad0 --schema1-helper restore_validation_artifacts.py --expected-helper-sha256 33548dad0cfb3a268346d896ba2ca4340c1171df8f00d3c08bb18a95723c3594 --output /absolute/new/artifacts
```

然后执行corpus-work/scripts/validate_corpus.py --mode editable-delivery，传入实际package、delivery-evidence、恢复后的build和receipts及独立report。公开完整恢复成功后才更新交付数。当前组批复用未变题证编译及合并aggregate；公开恢复仍执行必要完整gate。
