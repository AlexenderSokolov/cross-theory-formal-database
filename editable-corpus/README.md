# 正式交付材料与当前目录

本目录的原始交付清单是 [manifest.json](manifest.json)，数据库分片说明是 [database-delivery.json](database-delivery.json)。

- **现在看题**：[CORPUS_INDEX.md](CORPUS_INDEX.md)。它展示当前题名、历史评级、复核状态和许可。
- **程序使用**：[catalog.json](catalog.json) / [catalog.csv](catalog.csv)。题号集合与manifest一致。
- **历史交付核验**：[INDEX.md](INDEX.md)、`receipts/`、`delivery-evidence.json` 和数据库分片。历史“verified”主要指当时的材料与工程门禁。
- **内容返修**：[逐题记录](../curation/reviews.jsonl) / [返修说明](../curation/REPAIRS.md)。有明确问题的题暂不作为合格人类证明使用，原文件仍可追溯。
- **恢复数据库**：在本目录执行 `python restore_database.py`，随后 `python test_database.py`。
- **恢复编译证据**：按 [RECOVERY_CURRENT.md](RECOVERY_CURRENT.md)；本轮目录整理没有重编译全部旧题。
- **研究材料及20候选**：[research-line](../research-line/README.md)，不自动增加本目录交付数。

原数据库保留历史正文与标签；当前修订按`problem_id`从catalog关联。不要从已发布总数推断已完成当前标准的内容审查。返回[仓库首页](../README.md)。

旧`SHA256SUMS`实际对应较早快照，已归入[历史资料](../docs/history/README.md)。当前数据库按`database-delivery.json`逐片校验；完整题证和编译证据按现有恢复脚本及manifest/delivery-evidence检查，不使用旧校验表替代。
