# 高级数学题目与完整人类证明数据库

## 本地接续入口：目标30,000道

[打开完整本地交接手册](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/handoff/README.md)。交接含现状、硬性标准、详细执行计划、本地模型指令、实际命令、来源目录、扩展来源、规范化经验和可恢复的待处理材料。

- [状态与计数口径](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/handoff/STATUS_SNAPSHOT.json)
- [3,255条来源材料目录](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/handoff/catalog/README.md)：3,197个稳定ID及58个未分配候选键，不是合格完成数
- [44个核查后的扩展来源入口](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/handoff/new-sources/扩展题源手册.md)
- [本地执行命令与恢复](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/handoff/plan/04_COMMANDS_AND_RECOVERY.zh-CN.md)
- [40份待合并规范题证及1907未完成材料](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/handoff/materials/RESTORE_PENDING.md)
- [可直接阅读的待处理TeX索引](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/handoff/pending/PENDING_INDEX.md)
- [本地1002题整包恢复](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/handoff/local1002/README.md)：975主库加上述40份中的27份，另13份独立封存；1002尚未作为另一主库合并发布，不能重复相加到远端完成数

先按交接手册克隆工作分支并核对 `handoff/SHA256SUMS`，再恢复数据库和固定待合并材料。30,000是本地后续目标，本次没有声称完成三万题。

## 当前主库：975道完整可编辑题证

已交付 **975道独立可编辑TeX完整人类题证**，含作者原命题、原证明、必需新局部核心、可追溯来源、实际编译回执、INDEX和全文SQLite。64道新增题逐题新检查通过；911道既有题仅在正文、来源、构建、运行时等身份精确核对后保留成功检查记录。归属及安全见证修订涉及的题另作新检查；当前恢复整包975/975和230项项目测试通过。机械核对不代替独立数学审稿。

- [直接打开题目总目录](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/editable-corpus/INDEX.md)
- [全文SQLite全部有序分段](https://github.com/AlexenderSokolov/cross-theory-formal-database/tree/2a654a974767ad64d0a4da0767adaa41d2dafae9/editable-corpus/database-parts)
- [题证范围、许可及编译说明](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/editable-corpus/README.md)
- [975主库完整交付提交](https://github.com/AlexenderSokolov/cross-theory-formal-database/commit/5bb58ff2b57284a3ab2f2a76e50f588f4a8e629f)
- [本地交接提交](https://github.com/AlexenderSokolov/cross-theory-formal-database/commit/2a654a974767ad64d0a4da0767adaa41d2dafae9)
- [首批已核实提交](https://github.com/AlexenderSokolov/cross-theory-formal-database/commit/93012acd777d84b190e9cfcf26409e59d03385ee)

当前完整SQLite以五个有序无损gzip字节分段交付。下载全部分段与 [顺序/哈希清单](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/editable-corpus/database-delivery.json)，保持目录结构后运行 `python3 editable-corpus/restore_database.py`；脚本核对分段、压缩流与SQLite身份、完整性、外键及975份全文，拒绝覆盖不同内容的已有文件。交接中的catalog数据库是来源元数据工作队列，不替代这份全文主库。

## 历史材料与许可边界

历史3195是旧证据门禁数量，其中2822个为PDF页面封装，不能当作完整可编辑题证的完成数。原有文件继续保留供历史参考；[旧377条SQLite](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/historical-database/corpus-377.sqlite)及[旧684条压缩数据库](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/2a654a974767ad64d0a4da0767adaa41d2dafae9/historical-database/corpus-684.sqlite.gz)都不是当前主库。

来源许可逐条保留，完整必要正文与可分发的作者数学宏有明确绑定。原始敏感HTML、隐藏请求字段、私有非独占辅助源包及未核验再分发权限的实现不在交接导出中；历史临时路径不是本地恢复依赖。
