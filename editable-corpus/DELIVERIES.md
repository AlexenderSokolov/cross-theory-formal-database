# 公开交付与本轮维护

## 当前公开基线

- 公开材料数：**14,866**。
- 生产提交：[`7165605d4c3aa091f8f079ca329443806029be31`](https://github.com/AlexenderSokolov/cross-theory-formal-database/commit/7165605d4c3aa091f8f079ca329443806029be31)。
- main对应提交：[`5c133eb3cb70ada8bd3ca187089fe69378e5bc52`](https://github.com/AlexenderSokolov/cross-theory-formal-database/commit/5c133eb3cb70ada8bd3ca187089fe69378e5bc52)。
- 已有恢复回执状态：`public_exact_commit_full14866_restored_verified`，批次`batch-14785-14866-r003`。
- 数据库实际恢复及结构检查：14,866条题目、14,505条来源，完整性通过、外键错误0；本轮没有重新编译14,866道旧题。

具体数据库分片见[database-delivery.json](database-delivery.json)，原始材料名单见[manifest.json](manifest.json)。这组证据不单独认证每条难度、题证配对或数学正确性。

## 2026-10-10维护

本轮修目录、保留逐题返修记录、整理独立研究材料并试做20候选。尚未走正式生产准入和公开恢复的新题不会加进上述数字；实际试做结果见[候选目录](../research-line/pilot-20261010/)。

原来只列到6,759条的表已保存在[历史交付表](../docs/history/2026-10-10/DELIVERIES-through-6759.md)，不能再当作当前规模。生产和维护提交历史均保留在Git中。
