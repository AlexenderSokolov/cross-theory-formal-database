# 高级数学人类证明题库

目标：在已有成果上推进到30,000道合格唯一题，交付完整可编辑题证TeX、真实编译结果、INDEX、全文SQLite和公开可恢复材料。

## 入口与位置

- 日常执行：[LOCAL_CONTROLLER_HANDOFF.md](LOCAL_CONTROLLER_HANDOFF.md)。
- 当前主库、待交付包、来源块与历史清理候选：[产物索引](handoff/yupeng/ARTIFACTS_CURRENT.md)。计数以索引指向的queue和公开恢复结果为准，不在本文维护另一套数字。
- 题证标准：[human-proof-corpus skill](corpus-work/.agents/skills/human-proof-corpus/SKILL.md)。
- 本地负责SSH与GitHub认证中转；计算与数据在Yupeng `/disks/sata1/yupeng/human-proof-corpus`。仓库为其`repo/`，Python为`runtime/python/bin/python`，分支`corpus-progress-20261001`。
- GitHub仓库`AlexenderSokolov/cross-theory-formal-database`为公开；用户已授权本项目正常提交发布，逐组件来源许可仍须匹配。

## 收录与生产

严格高于常规博士资格考试，记录H1/H2/H3及具体理由；保留作者完整原命题、证明和必要新局部核心、准确来源定位与引用。不得生成补证、改变作者数学、拆常规引理凑数或重复计版本；不开展独立数学审稿或提前增加研究标签。具体门禁统一按项目skill执行。

固定流程为：**复用或缓存来源 → 完成题证 → 逐题验收 → 满25项合并 → 公开恢复。** 未改变的成功材料直接复用；只修实际失败及其受影响范围。来源缺口、许可或难度问题逐题hold，继续独立候选。

来源worker只写自己的互斥候选目录；唯一总控负责稳定ID、材料准入、语义去重、主库与发布。运行台账不代替题库，技术READY不代替准入或远端交付。

## 工具与维护边界

运行入口为`corpus-work/corpusctl`；编译沿用`compile-isolated`，校验显式使用`validate_corpus.py --mode editable-delivery`。复用canonical投影、现有合并器及发布恢复入口，不执行旧固定数量/旧绝对路径脚本。

[控制器v2契约](corpus-work/docs/controller-v2/CONTROLLER_CONTRACT.md)、schema及35项场景用于修改相关代码时查阅和回归，**不作为日常生产待办或每轮启动检查**。相关测试已通过后不再例行重跑；本次集成完成后优先交付题目，不追加泛化测试、架构审查或新平台。不得以精简为由再重构一轮已可用程序。

题目最终编译与item门禁、批次SQL/aggregate和必要公开恢复保留。每500道新增作完整对账；公开计数仅在实际远端恢复成功后更新。失败回执、唯一未交付材料和在途目录保留，不批量删除，不强推或覆盖其它成果。GitHub凭据留在本地，原始网页缓存不盲目公开。

## 历史与接续

975＋40已接收，LOCAL1002和旧独立备份存在重叠，不能重复计数；1907未完成。历史见`handoff/`和Git历史，日常不重做接收。dot方案已取消，旧会话和旧心跳20-1000保持暂停。

现行总控为“高级数学题库：本地总控续产”，模型gpt-6.1-sol / medium，每2小时汇报日程ID2。中断时只更新当前队列、真实完成阶段和必要下一步，不复制维护多份状态说明。
