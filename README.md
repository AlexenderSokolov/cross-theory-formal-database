# 高级数学题目与完整人类证明数据库

## 当前可阅读成果

最新规范化题证在 [工作分支的 editable-corpus](https://github.com/AlexenderSokolov/cross-theory-formal-database/tree/corpus-progress-20261001/editable-corpus)。目前已交付 **862 题独立可编辑 TeX 完整题证**，本轮106条新逐题CLI通过，756条保留逐字节同一的历史逐题通过记录；本轮整包862条全部通过完整交付门禁，每题包含完整作者原命题、完整人类证明和可追溯来源，附实际编译回执与全文 SQLite 数据库。

- [直接打开题目总目录](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/corpus-progress-20261001/editable-corpus/INDEX.md)
- [下载全文SQLite数据库全部有序分段](https://github.com/AlexenderSokolov/cross-theory-formal-database/tree/corpus-progress-20261001/editable-corpus/database-parts)
- [阅读范围、许可及编译方法](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/corpus-progress-20261001/editable-corpus/README.md)
- [最新完整交付提交](https://github.com/AlexenderSokolov/cross-theory-formal-database/commit/a40bf9bf862afb8f2560ab5d7d013ba2d54649c3)
- [首批已核实提交](https://github.com/AlexenderSokolov/cross-theory-formal-database/commit/93012acd777d84b190e9cfcf26409e59d03385ee)

历史 3195 是旧证据门禁数量，包含 2822 个 PDF 页面封装，不能视为已交付完整可编辑题证的完成数。原有文件保留供历史参考和继续整理。

当前862条同时具有完整可编辑正文、人类原证明、来源/正文绑定、稳定编译回执、目录和SQLite全文。下载后可按说明重建实际编译文件并逐题运行失败关闭的门禁；机械核对不代替独立数学审稿。

当前完整SQLite以四个有序的无损gzip字节分段交付。请下载全部分段及 [顺序/哈希清单](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/corpus-progress-20261001/editable-corpus/database-delivery.json)，保持目录结构后运行 `python3 editable-corpus/restore_database.py` 一次恢复；脚本核对所有分段顺序、长度和哈希、完整压缩流与SQLite哈希、完整性、外键、862条记录及完整题证正文，并拒绝覆盖不同内容的现有文件。旧377条原SQLite保存在 [历史数据库](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/corpus-progress-20261001/historical-database/corpus-377.sqlite)。

旧684条单gzip原样保存在 [历史压缩数据库](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/corpus-progress-20261001/historical-database/corpus-684.sqlite.gz)，不作为当前数据库。
