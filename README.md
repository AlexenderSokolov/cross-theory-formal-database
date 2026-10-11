# 人类数学证明题库

## 当前准备成果（2026-10-11）

[150道题证与PDF索引](materials/INDEX.md) · [SQLite材料库](materials/PREPARED_MATERIALS.sqlite3) · [统一项目准则](PROJECT.md)

本维护分支保存100正式加50后备，全部已编译；本轮新增70道本地材料，生产主库公开新增0。后续接续准备仍以30,000道为目标；所有执行者遵守同一准则。

[DeepSeek接续说明](research-line/harness-ready-20261011/HARNESS_START_HERE.md) · [可直接使用的提示词](research-line/harness-ready-20261011/DEEPSEEK_HARNESS_PROMPT.md)

## 历史仓库说明

> **当前入口（2026-10-11）**：先读[本项目统一工作准则](D:/Study_Works2/Lean_grokking/PROJECT.md)。本阶段只做找题与建库，取消旧交接、固定数学复审及会话证据要求。下方旧执行安排和数量为历史参考；来源、材料和命令按当前任务需要复用，不据旧文字恢复DeepSeek工作或额外核验。


这里保存数学文献中的原题与作者证明，以及可编辑 TeX、来源、许可和数据库。

<!-- catalog-summary:start -->
当前公开材料 **14,866 条**。这是已经交付的材料数，不代表每条都已按当前标准重新核准。

当前目录覆盖全部题目，已修正 **19** 个题名；明确待返修 **4** 条。详见[返修说明](curation/REPAIRS.md)。
<!-- catalog-summary:end -->

## 从这里开始

| 想做什么 | 打开这里 |
|---|---|
| 看题目、当前题名、难度与待修状态 | [当前题目目录](editable-corpus/CORPUS_INDEX.md) |
| 用程序读取全部题目元数据 | [catalog.json](editable-corpus/catalog.json) · [catalog.csv](editable-corpus/catalog.csv) |
| 阅读某题的作者证明 | 目录中的“题证”链接，正文在 [items/](editable-corpus/items/) |
| 查看已发现的问题与返修 | [返修说明](curation/REPAIRS.md) · [逐题记录](curation/reviews.jsonl) |
| 查看新增研究材料、重复和待处理项 | [研究线说明](research-line/README.md) |
| 使用已准备的文献、跨方向样例与Harness提示词 | [文献前置包](research-line/preparation-20261010/README.md) · [交接提示词](docs/corpus-preparation/DEEPSEEK_HARNESS_PROMPT.md) |
| 继续建库或维护目录 | [执行入口](LOCAL_CONTROLLER_HANDOFF.md) |
| 查旧计划、旧交接和历史数据 | [历史资料导航](docs/history/README.md) |

**使用难度标签前请看状态。** `H` / `published_H` 是历史标签；只有 `confirmed_H` 表示本轮内容复核已确认的等级。`hold` 表示已发现实质问题，暂不采用；`needs_review` 表示依据尚不足；`not_reassessed` 表示本轮尚未复核。改正题名不会让题目自动变成合格。

## 下载和使用数据库

```bash
git clone https://github.com/AlexenderSokolov/cross-theory-formal-database.git
cd cross-theory-formal-database/editable-corpus
python restore_database.py
python test_database.py
```

恢复后会生成 `editable-corpus/corpus.sqlite`，其中 `problems` 含完整 TeX，`sources` 含来源记录。数据库保留原始交付版本；当前题名修订与待修状态见同目录 `catalog.json`，按 `problem_id` 与数据库关联。原始题名和评级保留以便追溯。完整编译证据恢复按 [恢复说明](editable-corpus/RECOVERY_CURRENT.md) 执行；下载成功不等于重编译或数学复核通过。

## 继续建库

先利用已有缓存，确认题证对应、具体难点和跨库唯一性，再编译并走现有准入与交付流程。研究线材料不会自动计入主库。相关命令与当前限制统一放在[执行入口](LOCAL_CONTROLLER_HANDOFF.md)，长期标准见 [PROJECT.md](PROJECT.md)。

## 来源与许可

逐题查看目录中的许可链接。存量包含不同许可证，包括 GNU FDL 和个别非商业许可，不能把整库当作统一 CC BY 语料使用。新来源先核对实际文件的许可，再决定是否交付；完整说明见 [SOURCES.md](editable-corpus/SOURCES.md)。
