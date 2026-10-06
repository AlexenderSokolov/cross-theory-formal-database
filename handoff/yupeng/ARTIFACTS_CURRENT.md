# 当前产物索引

盘点时间：2026-10-05 15:26:28 Asia/Shanghai；读取时HEAD：`157f5e0cf1b0bc602ebd11bc275766330748f0e4`。这是位置与保留索引；后续计数读取[queue](PRODUCTION_QUEUE.json)，不由本文件增加题数。

## 当前成果与待交付

台账快照：本地已合并 **1065**，远端已恢复交付 **1065**，已准入待合并 **11**。

| 用途 | 原位置 |
|---|---|
| 当前主库：TeX、INDEX、全文SQLite与manifest | `/disks/sata1/yupeng/human-proof-corpus/operations/corpusctl/batches/batch-1048-1065-r002/merge/package` |
| 当前编译产物 | `/disks/sata1/yupeng/human-proof-corpus/operations/corpusctl/batches/batch-1048-1065-r002/merge/build` |
| 当前逐题编译回执 | `/disks/sata1/yupeng/human-proof-corpus/operations/corpusctl/batches/batch-1048-1065-r002/merge/receipts` |
| 当前聚合检查 | `/disks/sata1/yupeng/human-proof-corpus/operations/corpusctl/batches/batch-1048-1065-r002/merge/reports/aggregate.json` |
| 最新公开恢复结果与下一次previous入口 | `/disks/sata1/yupeng/human-proof-corpus/operations/corpusctl/batches/batch-1048-1065-r002/verify-public/result.json` |
| 准入与主库计数 | `/disks/sata1/yupeng/human-proof-corpus/repo/handoff/yupeng/PRODUCTION_QUEUE.json` |
| 当前执行阶段与任务 | `/disks/sata1/yupeng/human-proof-corpus/operations/corpusctl/runtime.sqlite`；只记录执行 |

### 已准入待合并包

这些路径直接取自queue，包含已有成功材料。接续时复用对应final，不从历史draft开始。

| ID | 冻结package | 已有最终item报告 |
|---|---|---|
| 1819 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r002/1819/package-final-r004` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r002/1819/final-item-r004.json` |
| 1820 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r004/1820/package-final-r002` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r004/1820/final-item-r002.json` |
| 1379 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r003/1379/package-r002` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r003/1379/item-final.json` |
| 1477 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r003/1477/package-r004` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r003/1477/item-final.json` |
| 2252 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r004/2252/package-final-r004` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r004/2252/final-item-r004.json` |
| 2283 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r004/2283/package-final-r002` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r004/2283/final-item-r002.json` |
| 2246 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r003/2246/package-r001` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r003/2246/item-final.json` |
| 2383 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r005/2383/package-r003` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r005/2383/item-final.json` |
| 1793 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r002/1793/package-r007` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r002/executor-2-r001/reports/final-item-1793.json` |
| 2286 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r004/2286/package-final-r004` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r004/2286/final-item-r004.json` |
| 2415 | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r005/2415/package-r002` | `/disks/sata1/yupeng/human-proof-corpus/candidates/native-source-continuous-r005/2415/item-final.json` |

### 来源块与尚未晋级材料

`candidates/native-source-continuous-r002`至`r005`整体保留。每块当前JOB_RESULT、READY、实际日志和运行台账决定进度；HANDOFF_STOPPED只是历史断点，不能据此认定今天仍停止。

1793、2286、2415若已进入上表，以queue为准；否则沿用原有技术成果完成缺失阶段及材料准入，不重新编译。1791等具体hold以现有hold文件为准，技术绿不能解除。其余来源块及旧候选也暂不清理，以免丢失唯一未交付材料。

## 保留和排除整理的目录

| 目录 | 处理 |
|---|---|
| `/disks/sata1/yupeng/human-proof-corpus/repo` | 主库正文、索引、程序、Git历史保留；本次只改三份说明文件 |
| `/disks/sata1/yupeng/human-proof-corpus/operations` | 当前基库、发布状态、集成及测试现场，整个目录排除移动/清理 |
| `/disks/sata1/yupeng/human-proof-corpus/operations/local-controller-01a10a85`、`/disks/sata1/yupeng/human-proof-corpus/operations/controller-v2-runtime-fixture` | 执行会话使用，不能移动或修改 |
| `/disks/sata1/yupeng/human-proof-corpus/candidates`、`/disks/sata1/yupeng/human-proof-corpus/builds`、`/disks/sata1/yupeng/human-proof-corpus/receipts`、`/disks/sata1/yupeng/human-proof-corpus/reports` | 保留题包、断点、回执和失败现场 |
| `/disks/sata1/yupeng/human-proof-corpus/source-cache`、`/disks/sata1/yupeng/human-proof-corpus/runtime` | 原始来源缓存及可用环境保留，不重新下载/安装 |

## 历史快照：人工清理候选

上次只读盘点总量约64GB，历史快照按du归属约43–45GB。硬链接和统计遍历顺序会影响归属量；下表不是可释放空间承诺。

以下目录在限定的当前入口中未见直接引用，但尚未排除间接引用或唯一材料，**不是删除白名单**。清理前逐项确认；发现任何引用或唯一材料疑点就排除。按现有AGENTS规则，整目录/批量删除由用户手动处理，本次没有执行删除或移动。

| 绝对路径 | 前轮近似归属量GiB |
|---|---|
| `/disks/sata1/yupeng/human-proof-corpus/snapshots/ready4-batch-r003` | 4.27 |
| `/disks/sata1/yupeng/human-proof-corpus/snapshots/next3-batch-r001` | 2.62 |
| `/disks/sata1/yupeng/human-proof-corpus/snapshots/pilot20-batch-r001` | 2.60 |
| `/disks/sata1/yupeng/human-proof-corpus/snapshots/release1035-public-restore-r001` | 2.22 |
| `/disks/sata1/yupeng/human-proof-corpus/snapshots/next2after1044-batch-r002` | 2.14 |
| `/disks/sata1/yupeng/human-proof-corpus/snapshots/next2-batch-r001` | 2.10 |
| `/disks/sata1/yupeng/human-proof-corpus/snapshots/remote1015-b05abb2` | 1.82 |
| `/disks/sata1/yupeng/human-proof-corpus/snapshots/release1035-local-restore-r001` | 1.44 |

`/disks/sata1/yupeng/human-proof-corpus/snapshots/main1040-public-restored-r001`与`/disks/sata1/yupeng/human-proof-corpus/snapshots/main1040-public-r004`仍被旧previous描述明确引用，排除本次清理候选。

## 日常使用

只读[日常一页流程](../../LOCAL_CONTROLLER_HANDOFF.md)即可开工。详细接口/schema/35项场景留作相关代码变更时的开发参考，不是每题、每批或每次汇报的额外检查清单。

本次整理仅生成此索引并精简PROJECT和日常入口；没有复制另一套题库、移动原目录、运行校验、计算散列、改程序、重启服务或更新题目计数。
