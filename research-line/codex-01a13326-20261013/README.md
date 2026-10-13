# 本对话在Yupeng独立收题与上传

全部生产子智能体使用GPT-6.1 Sol / medium。遵循仓库根PROJECT.md的统一准则：完整作者题证与必要上下文、H2/H3用途、定点近邻比较；不替作者证明，不补假设，不做论文式审查、哈希或逐字节核对。

本目录为task_root，任务前缀CP01A13326-，三个独立lane为algebra-geometry、combinatorics-logic、analysis-probability。根代理装配、编译、SQLite建库、每约25道提交上传，完成一批继续下一批。

只写本目录和本工作树PROJECT.md，不操作其他会话或DeepSeek目录、主库、queue、owner、模型配置。reference/existing-claims.jsonl为只读来源快照，不是生产工作表。来源身份、原文命题位置和结论用于定点去重，任务号不代表独立题目。

成品批次位于delivery/batch-NNN，包含INDEX.md、ITEMS.jsonl、corpus.sqlite3以及相对路径指向的完整可编辑TeX、PDF和必要来源。上传准备分支不计生产主库公开增量。

## 主机复现命令

```bash
bash operations/run_assemble.sh --task combinatorics-logic/TASK/task.json
bash operations/run_export.sh --batch batch-001 --limit 25
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python operations/prepare_upload.py batch-001
```

任务参数从本task_root执行时可用相对路径。修正失败包装后使用run_assemble.sh的`--refresh --assemble-only`，再`bash operations/run_compile.sh --job jobs/TASK/r001 --resume`；不删除失败构建，也不重编成功题目。

## 已上传批次

- batch-001：25道；提交`dc51f6d6b54495b3df33dec4ba11d233a45eb8b4`。成品入口[索引](delivery/batch-001/INDEX.md)、[SQLite](delivery/batch-001/corpus.sqlite3)。生产主库公开增量0。
