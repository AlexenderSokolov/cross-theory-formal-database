# 高级数学人类证明题库

## 统一执行规范与并发工单

新工作者先读[执行规范](handoff/yupeng/EXECUTION_SPEC.zh-CN.md)，主代理按[任务单模板](handoff/yupeng/WORKER_TASK_TEMPLATE.zh-CN.md)填写明确原件、负责人、阶段职责和完成条件后派发。规范统一建库标准、来源资源、先下载后整理、真实门禁、计数及并发权限；当前进度以实际CURRENT/manifest/SQLite/远端为准。原件已存在不等于准入，尚未生成的工作成果不是来源hold。

## 当前目标与边界

在既有成果上推进到30,000道合格唯一题。每题严格高于常规博士资格考试，记录H1/H2/H3及2—4句具体依据；包含作者原命题、完整人类证明及必要的新局部核心，保留实际假设、量词、常数和版本。初始建库仅做难度粗筛和材料管理，不做a/c、跨理论、桥梁、距离或学科研究标签，不作独立数学审稿，不生成补证。

现行规范以用户2026-10-03接手要求、handoff/plan/01_SCOPE_AND_STANDARDS.zh-CN.md及仓库human-proof-corpus skill为准。旧私有仓库、旧数量及旧默认校验路线是历史信息，不是当前条件。仓库已获用户明确授权公开发布；逐作品/文件许可仍分别核对。

## 当前生产状态与固定节奏（2026-10-05 root 交接）

当前为1048道local已合并、1040道main远端已交付。七题公开CAS已实际恢复，证据为 `reports/pending7-public-restoration-r001.json`；它们与local主库重叠，不能再加到main计数。1662、1663、1665已完成root准入，冻结在PRODUCTION_QUEUE待批次；1581仍有残余工程hold。后续状态以对应实际产物更新，不把启动、缓存、报告或工程READY当作净新增。

固定使用root加3个来源workers，每个worker领取互不重叠的10—20候选来源块并连续处理。沿用项目Python3.13（`runtime/python/bin/python`）及已有源缓存，不重下已有原件。按真实模型配额排队；旧8次启动不等于8个有效worker，不爆发重试、不换账号规避配额。

每题先在小包完成原文引用映射、必要资产与最终排版，再对固定final输入调用一次真实编译流程（helper内部仍为2—4遍稳定TeX passes），完成必要page QA与兼容投影，最后执行一次 `--item` 验收。已绿且输入未变时直接复用；不重复同一个single aggregate、不逐题CAS恢复或逐题main合并。提交root的final revision随后冻结，发现实际问题才保留旧版并进入新revision。

root负责准入、H理由、必要core覆盖、semantic去重和发布，按交接的原文定位及已有索引读必要范围；不重新转录全文、不反复扫描全库。每25个净新增准入项形成一次真正multi-pack主库合并：汇总输入后只做一次主库rebuild、aggregate和公开恢复，再推进main远端计数。节奏稳定后扩至100项checkpoint；每500个净新增做完整对账。原件、已绿产物与旧历史保留。

持续使用Stop That Shit及其Stop Ladder：是否用户要求、是否完成当前结果所必需、哪条实际数据／接口／验收要求证明必要、略去是否会让本次任务失败。不能给出必要依据就停止扩展。Production只按实际题证交付、验收和计数推进衡量；重复思考、重复报告及额外散列／pins／专门hash测试不算产出。底层原compile／restore的兼容字段仍由现有helper自动完成，不另建审计平台、调度平台、网站或技能大框架。

## 唯一执行位置与接收起点

服务器SSH别名为 `Yupeng-orx`，工作根目录为 `/disks/sata1/yupeng/human-proof-corpus`，仓库在其 `repo/`。本机旧工作区不改动。计算、来源、PDF页面检查、SQLite和构建都在服务器；本机仅运行轻量控制和GitHub认证发布通道。

工作分支 `corpus-progress-20261001`；固定交接提交 `2a654a974767ad64d0a4da0767adaa41d2dafae9`；固定975基线提交 `5bb58ff2b57284a3ab2f2a76e50f588f4a8e629f`。接手实际克隆HEAD与交接提交相同。每次发布前重新读取远端并保留后来新增提交。

接收已完成：975题与40个互不重复增量已合并为1015题，全部在Yupeng真实编译；公开远端正文、数据库分段和7103个编译证据文件已在新目录实际恢复，整包门禁通过。可恢复正文提交为 `b05abb227bab0a39425b17a0e76f4e6dab12d80a`，交付计数核验提交为 `f291b3f7ca4aea6aab27caef1a8fd4c61868addd`。LOCAL1002的27题属于这40题，不能再加；1907计零。候选3255行和作品分组2344不是合格题数。持续阶段与领取位置见 `handoff/yupeng/CONTINUATION_CURRENT.json`；新增候选不因技术ready或来源记录自动计入远端完成数。

## 目录与协作

`runtime/` 为项目独立Python、TeX和隔离入口；`builds/`、`receipts/`、`reports/`位于包外。`snapshots/`保存不可变恢复/合并包。`candidates/<worker>/`为互不重叠的工作目录；`operations/`为执行命令、领取台账及恢复程序。它们都相对于服务器工作根，不是要求复原旧云端绝对路径。

主代理独占稳定ID、主库manifest、INDEX、SQLite及Git。子代理只写自己的候选目录。来源按作品/版本缓存一次，编号从全部历史稳定ID及预留台账分配，不能用完成数+1或重用空洞。失败按具体hold记录并继续独立来源。

## 实际运行方法

固定沿用项目Python3.13（`runtime/python/bin/python`）及已选TeX环境。compile／restore所需兼容身份字段由既有helper自动记录，不追加全目录散列、多层pins或专门hash报告测试；环境回执不代替题证验收。网络直连使用命令级代理覆盖，不修改服务器全局代理。编译禁用shell escape，不运行论文上游构建脚本；bwrap包住完整可信compile helper，禁网、包只读、个人凭据不可见。

接收历史由`run_reception.sh`保留；仅在实际接收／恢复需要时追溯，不在日常production重复执行已完成的975基线恢复测试。40题和LOCAL1002按固定交接手册恢复到新目录；基线和LOCAL1002输出必须在同一文件系统，不改硬链接输入。原clone POSIX模式若与CAS严格要求不同，使用精确新副本，不放宽恢复器。

`run_compile.sh --package ABS --build-root ABS --receipt-root ABS --item ID --engine xelatex`调用项目要求的真实回执helper。该入口保留helper的实际2—4遍XeLaTeX协议，不以其他编译输出冒充回执。验证使用 `corpus-work/scripts/validate_corpus.py --mode editable-delivery`，显式指定真实package、delivery-evidence、build-root、receipt-root、item和独立report。单题仍检查所属小包的数据库一致性，因此先在小包做好必要兼容投影，最终--item只执行一次。single aggregate与逐题CAS恢复不是默认交付步骤。

合并器只准备新目录，不自动晋级或发布。保持sources/problems schema和完整tex_content；按最终manifest重建数据库，再验证全文投影。缺项、关键疑点、版本/许可冲突和语义重复不得计数；技术门禁不独立认证数学正确性。

## 验收、发布与续接

975、40和LOCAL1002的接收、环境编译基线及20题试点属于已保留历史，不在日常生产反复执行。现在按25项checkpoint起步，稳定后100项、每500项完整对账，继续累计3000、5000、10000、20000、30000；来源记录、技术READY和重叠备份不算净新增。

每25个净新增准入项真正汇总multi-pack后，仅一次主库rebuild、aggregate、发布与公开恢复；稳定后扩至100项。每新增500项才做完整主库和证据对账，实际冲突按受影响范围处理。Git保存可比较正文、索引及恢复清单，较大SQLite快照使用同仓库Release；增量恢复链未实际往返通过前用既有完整分段。准确数据库字节恢复保留对应分段，不声称跨SQLite版本重建字节相等。

发布先审查明确文件清单，服务器制作增量Git bundle，本机验证其基准并通过已有身份正常推送；不把token放服务器。不强推、不回滚、不覆盖并发成果，不批量删除。远端交付数量仅在commit/tree/ref及公开下载后实际恢复检查通过后增加。

中断前提交当前commit、各阶段真实计数、领取来源块、完成位置、hold、必要文件/哈希、依赖版本和下一条完整命令。磁盘按实际分配量测量；下一批空间不足时报告并申请可写空间，不删唯一材料、不降低标准、不承诺未测完成时间。

## 全自动续跑

用户明确授权离开后持续推进。当前任务Goal为30000且保持active；桌面heartbeat `20-1000` 已更新为固定流程，当前保留PAUSED状态；当前Goal及生产队列继续工作，不把自动化配置存在当作进程正在生产。固定root与3个来源workers，各worker连续处理10—20候选块；实际提供方配额决定排队。历史8个启动请求不等于8个有效采集槽，遇Concurrency limit exceeded正常排队，不爆发重试，不换账号或规避。返回后由主代理检查结果并续派。启动回执不等于采集完成；普通网络或题目hold不停止其他来源，不等待重复确认。只有30000题公开远端可恢复并通过既定门禁后才完成Goal。

## 来源下载优先

用户2026-10-04明确要求先下载来源，再提取处理。已缓存来源的PDF、公开网页与可取得原生TeX保存于服务器source-cache/catalog-r001；默认直接复用，不重新下载已存在原件。下载器operations/download_catalog_sources.py为16路I/O、每主机2路，显式直连代理隔离，保存URL、实际HTTP结果、完整文件hash/bytes及失败记录；原网页只作私有缓存，不公开隐藏字段。下载文件数和字节数不计合格题，许可在公开准入时逐件核验。完整缓存的既有ready材料可以完成闭环，新来源必须先完成其领取下载批次再转录。用户已充分授权全自动，不请求重复审批；运行优先已授权SSH与命令通道，不调用会反复要求平台审批的MCP接口。

## 可复用题证流程与工具

当前流程入口：corpus-work/.agents/skills/human-proof-corpus/SKILL.md；增量经验：其 references/incremental-workflow.md。corpus-work/scripts/corpus_delivery_tools.py 提供严格报告检查、固定恢复程序规范化、显式文件表CAS封包及真实恢复核验；合并复用 merge_editable_packages.py / merge_editable_batch.py。仅在对应工具发生实际修改或真实失败时运行其针对性检查；run_delivery_reuse_checks.sh不是每题／每块的重复production步骤。既有临时目录和旧材料保留。程序准备／恢复成功不自动授予数学、来源许可、难度或远端主库完成状态。实际计数与恢复入口看 handoff/yupeng/CONTINUATION_CURRENT.json。

公开恢复数据传输复用 `corpus-work/run_public_transport.sh`，方法与证据边界见 skill 的 references/public-transport.md。按固定 commit/filelist 复用真正旧公开恢复缓存，变化文件精确下载；材料准备后仍实际恢复 SQLite/编译资产并验证，不能从 transport 回执增加完成数。各候选流程报告放 sources/ID 或带完整manifest身份的批次目录，避免同名根报告阻塞合并；旧文件只在新输出中重新安放并保留原件。
