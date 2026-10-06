# 高级数学人类证明题库执行规范

版本：2026-10-04。适用于 Yupeng 上的接收、采集、整理、验证、建库和公开交付。用户后续明确要求优先；本规范不放宽原有收录标准。历史文件保留，旧数量、私有仓库说法和旧默认验证模式不作为当前执行条件。

## 1. 目标与交付物

在现有成果上累计交付 **30,000 道合格、唯一、可追溯的高级数学证明题**。不重建已完成正文。每题交付完整可编辑 TeX、作者原证明及必要局部核心、来源和权利记录、实际编译证据、索引和全文 SQLite。

初始建库只做难度粗筛与必要材料管理。a/c、跨理论关系、桥梁、距离等研究标注后置。来源轮换可以为取得合法完整材料服务，不能按未来希望观察的跨理论现象定向选题。

“合格”同时满足下列条件：

| 条件 | 工作者必须交付的证据 |
|---|---|
| 明确高于通常博士资格考试 | H1/H2/H3，以及2—4句具体难度依据；说明在标准背景之后仍需完成的非例行证明义务 |
| 题目与人类证明对应 | 原命题全部假设、量词、常数、结论；完整原证明；必要的新局部核心及其出处 |
| 可追溯 | 作者、作品、实际版本、DOI/URL、定理编号或页码、精确位置、原文件哈希和获取记录 |
| 可编辑和可编译 | TeX含实际题目与证明全文，真实成功编译和稳定引用，保存PDF及真实日志/回执 |
| 唯一和一致 | 语义去重；manifest、provenance、INDEX、全文SQLite一致；完整性、外键、唯一ID及逐行正文投影通过 |
| 可公开再分发 | 对实际使用的TeX、PDF、图片、宏和其他资产分别记录依据；满足各自许可条件 |
| 已交付 | 明确远端提交与文件清单，公开读回后在新目录实际恢复验证 |

链接、题名、摘要、PDF嵌入、证明截图和只有元数据的数据库不能替代完整题证。必要示意图可以作为资产；正文证明不能由图片替代，图中的关键数学文字和公式依现行标准保留可编辑内容。

同一命题的语言、版本、重印、参数换写、TeX/Lean表示只计一道。同一论文可有多个独立结果，但每个结果必须有不同的实质结论和证明义务。常规辅助引理、简单特例和已在其他题中承担的必要核心不另计。

## 2. 工作位置与当前状态

服务器根目录记为 `ROOT`：`/disks/sata1/yupeng/human-proof-corpus`。仓库为 `ROOT/repo`，分支为 `corpus-progress-20261001`，SSH别名为 `Yupeng-orx`。来源下载、PDF查看、TeX编译和SQLite处理都在服务器。本机只做轻量控制与已有Git身份的发布中转。

| 目录 | 用途 |
|---|---|
| `ROOT/source-cache/` | 已下载原件和接收清单；原网页只作私有缓存 |
| `ROOT/candidates/<owner>/` | 工作者独有目录；候选正文、来源、构建、回执及报告放在自己的子目录 |
| `ROOT/runtime/` | 项目Python、TeX和隔离入口 |
| `ROOT/builds/`、`receipts/`、`reports/` | 主代理的构建与检查证据；不属于只读题证包 |
| `ROOT/snapshots/` | 接收、合并及恢复后的固定材料包 |
| `ROOT/operations/` | 执行脚本、领取台账和恢复工具 |

当前计数以 `handoff/yupeng/CURRENT_DELIVERY.json`、`CONTINUATION_CURRENT.json`、实际manifest/SQLite和远端提交为准。固定交接提交为 `2a654a974767ad64d0a4da0767adaa41d2dafae9`；975题基线为 `5bb58ff2b57284a3ab2f2a76e50f588f4a8e629f`。

接收关系是975＋40＝1015；LOCAL1002中的27个新增题属于这40题，不能再次相加。1907是未完成题目的编号，不是数量。候选目录3255行、3197个稳定ID、58个候选键、2344个作品分组，以及下载URL/文件/字节数都不是合格题数。

## 3. 必读材料与可用来源

新接手者按以下顺序读仓库文件。已读且版本相同的资料不必反复整篇读取。

1. `PROJECT.md`，再读 `handoff/README.md` 和 `handoff/STATUS_SNAPSHOT.json`，核对当前HEAD与工作区。
2. `handoff/plan/01_SCOPE_AND_STANDARDS.zh-CN.md`、`02_EXECUTION_PLAN_30000.zh-CN.md`、`03_LOCAL_AGENT_PROMPT.zh-CN.md`、`04_COMMANDS_AND_RECOVERY.zh-CN.md`。
3. `handoff/experience/faithful-tex-normalization.md` 和 `cached-source-admission-and-worker-stages.zh-CN.md`。
4. `handoff/catalog/README.md`、`SOURCE_MAP_ZH.md`、候选CSV/JSONL、`source_works.jsonl`。候选查询库是 `handoff/catalog/work_queue.sqlite.gz`；它不是主库全文数据库。
5. `handoff/new-sources/扩展题源手册.md` 和 `expanded-sources.jsonl`。44个入口是发现线索，不等于44道题或44个独立新题库。
6. 需要恢复时读取 `handoff/materials/RESTORE_PENDING.md`、`handoff/pending/PENDING_INDEX.md`、`handoff/local1002/README.md`、`handoff/runtime/README.md`。
7. 执行收录时读取 `corpus-work/.agents/skills/human-proof-corpus/SKILL.md` 及其 `references/project-workflow.md`。

优先复用已有候选、已缓存的合法原生TeX和已完成包，再轮换扩展来源。当前主来源接收清单位于 `ROOT/source-cache/catalog-r001/acquisition-queue.json`、`url-records/*/receipt.json` 和 `PROGRESS.json`。下载的论文PDF、原生TeX、期刊政策PDF和落地页必须分开识别。

处理前先取得原件。工单必须给出明确的 `SOURCE_PATHS.json`：每个原件的绝对路径、角色、URL、SHA256、字节数、版本和实际取得时间。可把已校验原件复制到工作者自己的 `cached-originals/`；复制须核对哈希。旧catalog中的历史路径不存在，不能据此忽略当前已经下载的原件。

## 4. 难度、证明和许可怎么判断

### 难度

H1表示明确超出通常资格考试；H2表示高阶博士专题中仍有实质证明任务；H3表示已有完整人类论证的研究级结果。三个等级都必须指出具体非例行义务。期刊、作者、篇幅、术语和“研究级”称呼不能单独证明难度。

先写清可以引用的标准背景，再说明剩下什么。可以明确引用原文中可定位的标准先修；不能把主结论、等价结论、新关键构造或主要常数推导当作已知。若剩下的只是定义核查、常规群运算或直接套用大定理，记录难度不足并继续其他候选。

### 人类原证明

保留作者语言、证明顺序、假设、量词、符号、常数和条件性。逐段读取主证明及其调用的作者新局部论证，跨页、附录和非相邻续证也要包含。助手只写题名、难度依据、排版与异常说明，不能补造证明。

检查范围是来源取得、题证匹配、核心完整性、忠实转录、版本、许可、难度粗筛、语义去重和工程一致性。不开独立数学审稿、多模型投票、反例研究或替代证明竞赛。技术通过不等于独立认证数学正确性。

只有权威出版PDF明确显示原生文件的技术乱码时，才可做限定转录：保存原source0，给出具体小段、原PDF位置、真实对照和替换记录。关键公式、版本或证明含义不清时隔离该题，不猜修、不缩小原假设来过门禁。

### 权利

公开可读不等于允许再分发。核对实际文章/版本的作者、题名、DOI和许可，再分别核对原生TeX、出版PDF、数学图、第三方照片、宏包、字体及整理说明。同站托管或另一题的许可证不能代替本题证据。arXiv nonexclusive不能作为公开复用授权。

来源缓存中的 `not_yet_admitted_for_publication` 表示下载时还没完成许可检查。它不是已经核实的拒绝，也不是自动授权。工作者应读取原文许可，生成事实记录，再按工单中的审查职责提出准入或具体hold。

未知许可原件、原HTML表单/隐藏字段、私密会话、凭据和未核验的第三方资产不进入公开包。若数学正文不需要某照片或数值图，可以明确排除其使用；不能顺带宣称整份原PDF中的所有资产都已获准。

## 5. 每题处理顺序和完成条件

| 阶段 | 负责人做什么 | 阶段完成证据 |
|---|---|---|
| 领取 | 主代理按作品/版本分配互斥块；确认已有ID或登记候选键 | owner、范围、路径、排除项、下一位置明确 |
| 接收原件 | 来源工作者下载或复用已缓存原件，先补本题所需资产 | 实际文件、URL、格式、哈希、大小、版本和失败记录 |
| 来源审查 | 工作者核作者、版本、定位、许可；主代理处理共享来源身份 | 逐组件事实记录；未知项明确，原件不冒充准入 |
| 材料筛选 | 工作者匹配原命题、完整证明、新局部核心、难度和独立性 | 具体statement/proof/core位置、理由、去重比较和待判项 |
| TeX整理 | 工作者生成独立完整正文、出处、许可、证据映射和索引 | 实际TeX；source0未改；声明的每段可以回放 |
| 编译 | 工作者在隔离环境运行真实helper | 2—4遍实际成功；最终日志稳定，无未解引用、缺字、重名标签或重跑请求 |
| 数据库与逐题门禁 | 工作者同步manifest/provenance/INDEX，按最终包重建全文SQLite并验证 | 唯一ID/claim、integrity/FK、逐行全文及来源投影、实际item和小包aggregate通过 |
| 页面检查 | 工作者真实查看输出每页布局及关键原文页 | 明确看过的页、图像/PDF哈希、复用范围和具体结果；页数或文本提取不等于看过 |
| 可恢复包 | 工作者按明确文件清单封装，再在新目录恢复 | 分段/归档/文件哈希、大小、mode、SQL和恢复后的真实完整门禁通过 |
| 合并发布 | 唯一主代理处理ID/共享来源/去重，合并并发布 | 完整INDEX/SQLite/聚合检查；远端commit、明确文件清单、公开实际恢复 |

尚未生成的TeX、evidence、编译回执、SQLite或恢复包是工作者需要完成的工作，不能作为“来源缺证明”的理由。未满足晋级条件时保持当前阶段；只有具体来源或质量缺陷才进入hold。

复用模板只复用结构和通用宏。作者、DOI、许可、版本、题名、修改说明、难度和证据绑定必须按本题重新匹配。当前可参考服务器已有合格包 `candidates/published-pilot/package-938-r017` 和 `candidates/native-pilot/packet-1492-r002/package`。

## 6. 当前环境中的编译与验证

Python使用 `ROOT/runtime/python/bin/python`。执行前用项目Python读取可信compile_editable_delivery.py/validate_corpus.py --help；compile-isolated裸help会因缺真实绝对路径被拒绝。工作者自己选择一个新的包/构建/回执/报告目录；构建和回执必须位于只读包外。

下面是命令模板，必须填入本工单真实路径和ID，不能把占位符原样执行：

```bash
ROOT=/disks/sata1/yupeng/human-proof-corpus
PKG=/absolute/owned/packet/package
BUILD=/absolute/owned/build
RECEIPTS=/absolute/owned/receipts
REPORT=/absolute/owned/reports/item-ID.json
ID=actual_stable_id

"$ROOT/runtime/bin/compile-isolated" \
  --package "$PKG" --build-root "$BUILD" \
  --receipt-root "$RECEIPTS" --item "$ID" --engine xelatex

"$ROOT/runtime/python/bin/python" "$ROOT/repo/corpus-work/scripts/validate_corpus.py" \
  --mode editable-delivery --package "$PKG" \
  --evidence "$PKG/delivery-evidence.json" \
  --build-root "$BUILD" --receipt-root "$RECEIPTS" \
  --item "$ID" --report "$REPORT"
```

编译一律由可信helper和bwrap隔离：禁网络、禁shell escape、包只读、个人凭据不可见。不运行出版社类文件、Makefile或未知脚本。缺依赖时使用有来源、版本和许可依据的真实运行包，不能造同名stub；失败日志保留。

逐题通过后，用相同包与实际build/receipt执行aggregate：省略 `--item`，报告写到另一独立路径。主代理可用 `operations/env-isolated.sh` 包住验证；该入口限制报告在 `ROOT/reports/`，工作者不能越过自己写入范围，因此可直接运行不执行TeX的可信Python validator，在自己的目录保存报告。

历史CAS若把真实receipt放在package内，按哈希同字节复制到包外的 `external-receipts/`，再显式传入该目录。不能伪造新receipt，不能把复制或复用说成重新编译。

发生正文、资产、许可、来源、运行程序或数据库投影身份变化时，重新执行受影响检查。身份完全相同且已有检查可覆盖当前范围时才复用，报告必须说明复用事实。可靠单题检查即时执行，不等累计500题才补检查。

## 7. 并发分工与排队

| 角色 | 可以写 | 必须交付 | 不拥有的职责 |
|---|---|---|---|
| 来源工作者 | 自己的缓存和接收报告 | 下载原件、格式/版本/许可事实、依赖和失败记录 | 不分配稳定ID、不改主库、不计合格题 |
| 题证工作者 | 自己的候选包/build/receipts/reports | 完整题证及实际闭环材料 | 不写其他worker目录，不改共享INDEX/主库/Git |
| 工程与页面检查者 | 自己的检查目录 | 哈希/来源匹配、实际页面和恢复检查 | 不生成证明，不进行数学审稿或投票 |
| 主代理/唯一合并者 | 主manifest、INDEX、全文SQLite、领取台账和发布 | 去重、ID、来源身份合并、聚合检查、提交与远端核验 | 不覆盖其他会话成果，不放宽门禁 |

按互不重叠的作品块分工。一个作品的多个版本、多个目标命题和共有原件由同一owner协调；共享原件只读。工单先给首个具体题目，确认已实际读取原件、生成成果，再扩展该块，避免多个泛任务同时空跑。

目标可设为8个或更多工作者，实际活跃数受可用模型槽位、API限制、磁盘和真实吞吐约束。来源下载与编译可分别使用已实测的16路；模型并发与CPU线程不是同一数量。观察到服务端限流时排队补位，不能把queued、PID存在或重连次数当作有效并发，更不能改权限/降低标准来凑吞吐。

启动前核CLI版本、实际支持的feature名、项目PATH和原件路径。启动证据是 `thread.started` 加实际成功工具/文件变化；完成证据是完整交付物。每个任务结束后，主代理核结果，再分配下一互斥块。

用户已授权正常同范围的服务器处理、公开同仓库提交和持续推进。不要重复请求确认，不调用会反复审批的MCP工作流；使用已授权命令通道。不可变的平台限制不能绕过，记录具体影响，继续可完成的独立任务。

## 8. 状态、失败和计数

分别记录候选、原件接收、来源准入、规范化、逐题通过、主库合并、远端核验数量。状态词统一：

`source_acquired → source_reviewed → material_reviewed → tex_ready → locally_validated → merged → published_verified`

上述状态词用于进度台账，不替代程序要求的manifest/evidence字段或SQLite schema；待定项不能自行改成已核实。

草稿、原件、技术通过但页面未看、小包已备份但尚未发布主库，分别报告。不能把同一题的这些阶段数量相加。主库远端完成数只看远端已恢复验证的主库。

| 情形 | 处理 |
|---|---|
| 真缺主证明/新核心、原文关键不清 | `hold_missing_proof` 或 `hold_source_core`，保存位置和具体原文 |
| 具体剩余义务不足以超出资格考试 | `hold_difficulty`，说明已引用背景和剩余步骤 |
| 许可/第三方资产/版本身份不明 | `hold_rights` 或 `hold_version`，说明缺少哪份依据 |
| 拒绝访问、不存在或临时失败 | 按真实HTTP/网络原因记录，不绕过访问控制 |
| 当前字体/宏/排版/引用失败 | `hold_build`，保存真正日志、输入和失败点；修复后新报告重跑 |
| 错路径、丢PATH、未知feature、误读阶段 | 调度/环境错误，修复工单；不能冒称数学或许可hold |
| 已有同一语义问题 | `duplicate`，记录对应ID与比较依据，不重复计数 |

失败的题不得晋级，但其他独立题继续。共用来源、程序、许可或清单出问题时，只暂停受影响的范围。保留所有源、草稿、失败和历史回执，不批量删除。

## 9. 发布与持续推进

完成20道净新增试点后继续100、500道批次，继而累计3000、5000、10000、20000、30000。既有40题不是这20道净新增。每25—100道形成可恢复提交；每新增500道做全库聚合与证据对账。必要的早期材料备份可以提前进行，但不自动增加主库计数。

发布前重读远端分支，保留其他会话新增成果。只添加明确审查的文件清单，不 `git add .`，不force push、回滚或覆盖。服务器生成增量Git bundle；本机验证并使用已有Git身份正常推送，不把凭据复制到服务器。

较大数据库使用同仓库Release或已核验的有序压缩分段，保存完整哈希与恢复程序。增量恢复链未实际往返通过前继续保留完整分段。公开读回后在服务器新目录实际恢复，检查真实正文、INDEX、SQL和证据，再更新远端计数。

每次中断前写入真实HEAD、各阶段计数依据、owner/来源块/完成位置、hold、必要路径与哈希、运行版本和下一条命令。30,000目标保持完整；未达到最终要求不声明完成，不因普通题目失败或任务返回而永久停止。

## 10. 给工作者的一页任务单

主代理使用同目录的 `WORKER_TASK_TEMPLATE.zh-CN.md`。派发前必须填写：负责人、唯一写入目录、确切原件路径/哈希、已有ID或候选键、原命题范围、材料与许可检查职责、结构模板、需要生成的成果、完成条件、明确排除项和接续位置。不能只发“看这个期刊，收几题”。

工单中的 `source_cache_status`、`source_reuse_review`、`material_review` 和 `delivery_validation` 是不同字段。原件已经下载不等于可以公开；来源许可明确不等于难度通过；材料审查通过不等于编译/恢复完成。工作者负责完成自己阶段的工作，而不是等待所有阶段的成果预先存在。
