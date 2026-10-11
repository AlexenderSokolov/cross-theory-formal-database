# 当前持续建库入口

统一规则：[PROJECT.md](PROJECT.md)，对Codex、DeepSeek及全部子智能体同等生效。

启动说明：[HARNESS_START_HERE.md](research-line/harness-ready-20261011/HARNESS_START_HERE.md)。直接使用[完整执行提示词](research-line/harness-ready-20261011/DEEPSEEK_HARNESS_PROMPT.md)。唯一工作表在同目录PREPARATION_WORKLIST.jsonl。

## 历史内容，不作为当前执行指令

下文旧“只做机械装配”“等待Codex逐题审批”“完成后停止”“固定双审”等安排不再执行。

# 建库与维护：唯一执行入口

> **当前入口（2026-10-11）**：先读[本项目统一工作准则](D:/Study_Works2/Lean_grokking/PROJECT.md)。本阶段只做找题与建库，取消旧交接、固定数学复审及会话证据要求。下方旧执行安排和数量为历史参考；来源、材料和命令按当前任务需要复用，不据旧文字恢复DeepSeek工作或额外核验。


先看[首页](README.md)和[当前状态](curation/SUMMARY.json)。本页给命令和边界，具体题目问题见[返修说明](curation/REPAIRS.md)。

2026-10-10新增[文献前置准备](research-line/preparation-20261010/README.md)：六份已有文献的实质候选、题证定位、来源边界和续做位置；[Harness提示词](docs/corpus-preparation/DEEPSEEK_HARNESS_PROMPT.md)。先读各块当前验证状态，再复用已验证办法。此包不改变现场队列、生产编号或发布授权。

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
