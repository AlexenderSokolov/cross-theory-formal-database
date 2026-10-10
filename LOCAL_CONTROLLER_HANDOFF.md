# 建库与维护：唯一执行入口

先看[首页](README.md)和[当前状态](curation/SUMMARY.json)。本页给命令和边界，具体题目问题见[返修说明](curation/REPAIRS.md)。

## 本地整理、返修和检查

```bash
bash run_curation.sh
```

对应的PowerShell命令：

```powershell
python -m unittest discover -s corpus-work/scripts/tests -p test_refresh_catalog.py
python -m unittest discover -s corpus-work/scripts/tests -p test_reconcile_research_line.py
python corpus-work/scripts/reconcile_research_line.py
python corpus-work/scripts/refresh_catalog.py
python corpus-work/scripts/refresh_catalog.py --check
```

首次或抽取逻辑改变后，另跑 `python corpus-work/scripts/refresh_catalog.py --scan-pairing`。它检查全库源码跨度间插入的另一命题和明确模型解答标记，只生成需核对的条目，不把启发式命中当作数学不合格。

修改题名或内容结论时，写入 `curation/reviews.jsonl` 并附原文位置。`review_scope=title`只修题名；`content`才影响内容状态。H3的一审建议不能自动核准。原交付的正文、清单与数据库分片保留，目录显示新判断。研究线重叠项映射回原题，不重复计数。

## 20个候选试做

候选和逐题结果在 [research-line/pilot-20261010/](research-line/pilot-20261010/)。按其中README/run脚本复现。确认题证、难度与唯一性后，才能把真实成功编译和材料检查结果交给现有准入器。片段存在、编译成功、候选材料数均不等于正式公开交付。

## 正式产线

主机 `Yupeng-orx`，根目录 `/disks/sata1/yupeng/human-proof-corpus`，控制器入口 `repo/corpus-work/corpusctl`（shell脚本，以bash调用）。先只读检查现场状态、磁盘和当前写入者：

```bash
bash /disks/sata1/yupeng/human-proof-corpus/repo/corpus-work/corpusctl status --json
df -h /disks/sata1
```

准入、冻结、合并、发布沿用已有控制器和发布器；owner/generation、批量大小和active batch取现场值，不使用旧交接中的硬编码值。`PRODUCTION_QUEUE.json`负责准入与计数；runtime只记执行。公开精确提交恢复成功才增加交付数。

2026-10-10 15:16复核时公开与本地主库均14,866、队列58、batch_size250；共享盘只剩约68MB，仍不够运行需要GB级空间的正式恢复发布。本轮本地成果不自动覆盖远端。磁盘不足时保留待交付产物及完整命令，不批量删除，不修改别人的服务。

详细运行对象见[产物索引](handoff/yupeng/ARTIFACTS_CURRENT.md)；控制器代码变更才查[控制器契约](corpus-work/docs/controller-v2/CONTROLLER_CONTRACT.md)。旧交接见[历史导航](docs/history/README.md)，不据旧文档恢复旧任务。
