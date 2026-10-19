# 作者题证库：公开阅读目录复用

2026-10-19。本轮基于公开d4077e447681a460ce95ddf2ef4da24b08d10a06隔离实现，未接管原生产写入者。

入口：[阅读目录](../editable-corpus/browse/README.md)、[结构与运行](../PROJECT.md)、[复现脚本](../run_reader_catalog.sh)。

实现：reader_catalog以现有manifest为活动身份、catalog为既有判断、work-registry为固定作品定位，输出小型Markdown与JSON分页；原作者题证、稳定ID和数据库链不改。write_active_indexes统一生成，prepare及失败续作使用实际分页白名单，consumer helpers携带同一reader代码。

已验证：14项针对性回归通过；原复现脚本经Git Bash实跑test/check通过。22,790个活动ID恰好分区覆盖一次（TeX 22,755／Lean 35），236对分页最大63,543字节，小INDEX 480字节。23,598个不同仓库内目标无缺失；四类实际原件入口／证明片段读取通过。独立审阅指出的新helper旧批次恢复及work-registry暂存缺项已修正；精确白名单回归通过。没有运行Lean内核、重新编译全库、开展数学正确性认证、部署生产或更新公开main。

注意：catalog内容已是当前22,790条，旧的是继承的generated_at；README和CORPUS_INDEX才实质过期。当前版本按Git定位，旧生成时间单独保留。Windows写文件需固定LF；动态嵌套页必须同时进入prepare与resume的暂存和备份，否则正常生成不代表失败恢复可用。

提示词来源：用户2026-10-19要求“那得麻烦你先系统性的把仓库重构更新一下”；背景是网页GPT选题所需链接可读性。六题选题方案为前序讨论，本轮没有替用户选题或执行数学标注。

当前交付为隔离副本与已验收补丁，公开和运行副本仍待原单写者接入；接入时用最新manifest/catalog重新生成，不能把本次固定快照的数量覆盖到更新的产线。目录校验仅检查Git保留路径及生成导航，不等于所有远程来源可访问。
