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

- batch-002：25道；提交`cd4b1327eb02aa8d5daa742bebc57da737791e77`。[索引](delivery/batch-002/INDEX.md)、[SQLite](delivery/batch-002/corpus.sqlite3)。累计上传50道，生产主库公开增量0。

- batch-003：25道；提交`e6cac81533a2892691c2d46dad028d4a4d4f3167`。[索引](delivery/batch-003/INDEX.md)、[SQLite](delivery/batch-003/corpus.sqlite3)。累计上传75道，生产主库公开增量0。

- batch-004：25道；提交`6a62ad21ee2df4868d8f16b400ff76a19681e317`。[索引](delivery/batch-004/INDEX.md)、[SQLite](delivery/batch-004/corpus.sqlite3)。累计上传100道，生产主库公开增量0。

- batch-005：25道；提交`edf5db2583635e315a47e20b669afdd8ec9fa3e2`。[索引](delivery/batch-005/INDEX.md)、[SQLite](delivery/batch-005/corpus.sqlite3)。累计上传125道，生产主库公开增量0。

- batch-006：25道；提交`c13dd56e7f0e55fbd973b9750c272a176fce5bfb`。[索引](delivery/batch-006/INDEX.md)、[SQLite](delivery/batch-006/corpus.sqlite3)。累计上传150道，生产主库公开增量0。

## 作者原件入口

[所选作者原件清单](delivery/ORIGINAL_SOURCES.json)按来源列出未修改源码包、native源码或官方HTML/PDF的仓库相对路径。各lane在新源task就绪时记录原件，上传按实际交付来源过滤；弃用候选和暂缓来源不混入公开清单。原件补充不增加题目计数，也不触发已有PDF重编。

- batch-007：25道；提交`e50813ebfd2b208bf0f5bc592f2f478046bd08c1`。[索引](delivery/batch-007/INDEX.md)、[SQLite](delivery/batch-007/corpus.sqlite3)。累计上传175道，生产主库公开增量0。

- batch-008：25道；提交`3a807e6327be4771f5e0e8685c4121800de9399b`。[索引](delivery/batch-008/INDEX.md)、[SQLite](delivery/batch-008/corpus.sqlite3)。累计上传200道，生产主库公开增量0。

- batch-009：25道；提交`26fb06728fa4c3fc13fa34c7d49bb3d9a0388d71`。[索引](delivery/batch-009/INDEX.md)、[SQLite](delivery/batch-009/corpus.sqlite3)。累计上传225道，生产主库公开增量0。

- batch-010：23道净新增（原25条材料，2条跨线重复保留不计）；提交`2e58ea33609d144aa4e28d8891f12da4a29dcf2a`。[索引](delivery/batch-010/INDEX.md)、[SQLite](delivery/batch-010/corpus.sqlite3)。累计净上传248道，生产主库公开增量0。

- batch-011：24道净新增（原25条材料，1条跨线重复保留不计）；提交`7b685d4296dbe363ad323b681b35a56e32ea9955`。[索引](delivery/batch-011/INDEX.md)、[SQLite](delivery/batch-011/corpus.sqlite3)。累计净上传272道，生产主库公开增量0。

跨线去重修正：第三线已交付的CCC2025.6两条采样器结论和CCC2025.12 weighted adversary结论与本线原条目相同。本线保留原始题证、成品和历史提交，仅撤销3条净新增计数；累计净交付由275修正为272。后续同时只读比较第三线真实三个lane、交付和排除记录。

包装说明修正：15条已整理题目及1条新候选移除了模板误加的sampler/extractor先修段，作者正文、原文位置与图形不变；旧修订保留，新修订已编译。已上传批次中14条成品链接/SQLite同步指向新修订，其余正常进入新批次，不增加旧题净新增数。

- batch-012：25道；提交`fd548deb094e11c77b78db0a500d33b9c8b36ba2`。[索引](delivery/batch-012/INDEX.md)、[SQLite](delivery/batch-012/corpus.sqlite3)。累计上传297道，生产主库公开增量0。

- batch-013：25道；提交`25cda279b04a386e4d199393a358855d10237654`。[索引](delivery/batch-013/INDEX.md)、[SQLite](delivery/batch-013/corpus.sqlite3)。累计净上传322道，生产主库公开增量0。
