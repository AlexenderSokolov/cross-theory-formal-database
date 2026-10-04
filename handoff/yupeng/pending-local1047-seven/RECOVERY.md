# 七题公开待处理备份的恢复说明

本目录复用七份既有、逐项公开清单已核对的 one-item CAS，归档与 manifest 均保持原字节。IDs 为 1475、1479、1661、1579、1625、1584、1585；这七题全部已经包含在固定的 local1047 中。

**与 local1047 重叠 7 题，main 晋级数量为 0。** 这是待发布的独立恢复备份；本次没有发布、合并主库或创建新的数据库分段／恢复链。不能把这七份备份再加到 main 总数。

`PINS.json` 绑定原 CAS、恢复布局、逐题许可、旧公开清单／root 材料准入／已通过门禁身份及固定 local1047 身份。`PUBLIC_PAYLOAD_AUDIT.json` 列出每个 CAS 内声明文件的 SHA、大小与必要角色。只保留完整可编辑题证、来源／许可／保真见证、单题全文 SQLite、固定可信 helper 和真实 PDF／log／receipt 等证据；未包含旧全库分段、未知 class／字体、fontcache、private HTML、events 或凭据。

先用交接时外部固定的 SHA 核对 `PUBLIC_FILES.json`，再核对该清单列出的文件。恢复必须使用全新目录：

```sh
CORPUS_PYTHON=/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python CORPUS_VALIDATOR=/disks/sata1/yupeng/human-proof-corpus/repo/corpus-work/scripts/validate_corpus.py bash /absolute/path/to/this/public/run_restore.sh /absolute/path/to/FRESH_RESTORE
```

脚本串行调用固定、hash-bound 的 `restore_history.py`，从这里的七份复制归档真正恢复各自完整文件；随后使用明确的项目 validator 对每个 one-item 包执行 item 和 aggregate editable-delivery 门禁。1475／1479／1584 的 package、build、receipts 是三个目录；其他四题为根 package 加 `validation-artifacts`，脚本已经使用各自实际布局。

脚本不执行 TeX，也不重建主库。既有编译证据在恢复后的每题包中保持原字节；检查真实 PDF、最终日志、输入／资产及 receipt 身份。单题 SQL 可以直接只读核对，无需生成新的运输分段。准备阶段已经记录各题 SQL 完整字段／原 TeX／provenance 与 local1047 正文 SHA 的对账。

`RESTORATION_VERIFICATION.json` 记录这份复制备份的实际 fresh restore、原／恢复全文 SQL、已有门禁身份和新 one-item gates。该技术恢复结果不表示新增 main 题数、独立数学认证或已经公开发布。root 独占后续 Git／公开流程。

CAS 字节恢复只依赖自带固定 restore_history.py 和 Python 标准库。完整 editable-delivery gate 另依赖既有项目 validate_corpus.py、editable_delivery.py、editable_exclusions.json 及其原见证文件；这些依赖已逐件 SHA 固定在 PINS.json，运行前实际核对。可用 CORPUS_VALIDATOR 指定相同身份的项目 checkout；没有这套项目依赖时，只能完成 CAS 字节恢复，不能声称 gate 通过。这份小包不携带其他题目的全局审查材料。
