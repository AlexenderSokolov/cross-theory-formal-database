# 现存题源与候选目录（本地扩充到 30,000 的交接快照）

快照开始：2026-10-03T07:06:20.049770+00:00；完成：2026-10-03T07:06:34.232629+00:00。此目录只导出元数据，不复制原文、PDF、原始 HTML、认证或会话数据。

## 数字口径

- 原始上传包有 225 个分题 TeX，原 INDEX 有 220 个不同编号；不是本轮合格题数
- 恢复后的 corpus/metadata 有 3005 个记录：374 原生 TeX 材料记录、2,631 PDF 页证据记录
- 历史 item_status 有 3194 个 ID：3,000 旧 active、194 旧 quarantined。历史 active/PDF 包装不等于完整可编辑证明
- 历史记载 3,195 个证据候选，但不能从现存恢复清单重建为完整的 3,195 个已核验记录；本次不补造缺项
- 当前目录保留 3197 个实际出现过的稳定 ID，以及 58 个尚未分配稳定 ID 的候选身份键。共 3255 行；最高 ID 不代表完成数
- 来源/作品有 2,344 个可复现身份分组键：2,079 DOI、262 字面URL、3 明确集体作品/仓库；这不是独立合格题数，也不是全部镜像与版本的语义书目认证
- 来源材料已准入：1015，准入快照时间 2026-10-03T06:39:35.203940+00:00
- GitHub 已核验：975，提交 5bb58ff2b57284a3ab2f2a76e50f588f4a8e629f，树 669d8b47233a11ae40e8a7f4508f5b67df5274fb
- safe975-r004：975 个本地清单条目；local1002：1,002 个本地整包门禁通过条目；LOCAL1002的safe975历史材料检查已完成精确保留，且最终fresh27/fresh1002实际门禁通过
- 1,015 来源准入中 40 尚未计入上述 GitHub 975；其中13位于固定local1002之后，现也已完成规范化/逐题及整包门禁，全部40后续题已封存在可恢复独立包中

原有 frozen975 pending-inventory.csv 仅标记974条 verified，但 manifest 实际975条；具体旧CSV漏标ID1936。主目录按 manifest 对齐，不用旧CSV或旧active标记抬高/降低完成数。

3,195 是历史证据声称，3,197 是现存稳定编号目录条目；二者均不是已接收完整证明题数。58 个未分配键与2,344个来源分组也不计为完成。

最终交付状态对齐：2026-10-03T09:45:37Z。safe975已完成提交及远端精确commit/tree核验，远端corpus-progress-20261001分支交付975，main导航另行更新。仓库在09:45独立读取为公开，用户09:43明确同意公开发布；先前私有判断只作有日期的历史事实。LOCAL1002基线精确保留及fresh27/1002实际门禁已通过；后续40完整规范化材料与40逐题、恢复后整包门禁已通过，40题对应39来源，仍独立封存等待本地合并及发布。1907另列未合格。当前证据见final_status_evidence_975.json；原final_status_evidence_911.json仅作历史快照。保留字段github_verified911表示当前快照的核验布尔值，其实际真值数现为975

## 文件

- work_queue.sqlite：METADATA WORK QUEUE，材料管理查询副本；不是合格完整题证全文数据库。schema、重建脚本、integrity/FK/行数检查与查询示例分别见work_queue_schema.sql、build_work_queue.py、work_queue_validation.json、METADATA_WORK_QUEUE.md
- candidate_catalog.csv / .jsonl：稳定ID与未分配候选、题名、作者、作品、来源URL/DOI、版本、命题与题证位置、已有粗难度及其核验状态、许可、文件路径与哈希、状态、下一步
- candidate_record_history.jsonl.gz：所有匹配元数据记录的原路径、SHA256、身份匹配依据及变化字段。复制/版本/同ID修订不增加题数
- legacy_seed_bibliography_claims.jsonl：179个缺失结构化来源元数据的旧隔离条目，全部仍有现存TeX作者/书目/版本/范围声明与原URL、行号、文件哈希；另列字面URL汇总见legacy_bibliography_source_registry.json；这些只是未核验旧声明，不增加准入、作品分组或完成数
- source_works.jsonl：按 DOI、明确集体作品/仓库、其余字面来源URL分组；这些是可复现身份组，不伪称完成了所有镜像与书目语义去重
- source_domains.json：实际采用来源域的聚合；source_navigation_registry_60.json 保留原60入口，来源导航分组不是题目学科标签
- materials_inventory.jsonl：现存必要来源、许可、TeX与证据材料的位置、存在性、实际与声明哈希、导出分类
- identifier_alias_map.json：原字段与原数字字符串到稳定ID的明确映射；source/draft局部编号不能冒充全局题号
- duplicate_identity_groups.json：跨编号的同去重键/别名待核对组；不能仅依相似标题删除或合并
- release_packet_file_inventory.jsonl.gz：已保留911/safe975/local1002完整包全部文件的位置、大小、SHA256与Git blob身份；只登记元数据，包内重复/编译产物不计题数。快照数量见release_packet_inventory_summary.json
- private_raw_aid_inventory.jsonl.gz：原始HTML/headers及显式私有原件辅助的路径和SHA256；只输出元数据，内容禁止随本目录公开
- counts_and_reconciliation.json：精确口径、差集、错误数和已知旧清单问题
- input_snapshot_pins.json：统计依据与原计划、原始上传包、门禁和关键快照的哈希

历史采集脚本仅保留在history/HISTORICAL_NONPORTABLE_cloud_capture_20261003.py作来源追溯，依赖已过期云端/临时路径，不能作为本地接续命令。用户无需重建该云端文件系统；直接读取本目录冻结CSV/JSONL，或用build_work_queue.py派生元数据查询库。

## 状态与继续顺序

1. github_verified_complete_editable：复用同一不可变完整题证及许可；原编号保留
2. safe975的64个新增条目已转为github_verified_complete_editable；原local_safe975_qualified_not_committed_or_Git_verified现无当前条目，仅保留历史状态
3. canonical_qualified_sealed_pending_merge_and_publication：40题已实际逐题与恢复后整包通过（27题来自LOCAL1002、13题已另行规范化）。40份完整TeX与40题/39来源SQLite已对应，使用materials中的封存恢复包作本地合并；这些仍与corpus-progress-20261001的975交付分开
4. historical_evidence_only / quarantined / unassigned：候选。补全完整可编辑作者正文、来源/许可、实际残余难度、去重与编译；不得当作完成数
5. in_progress_unqualified_not_counted：1907另存未完成材料，不随封存40题计数
6. blocked_or_non_counting：按具体当前hold处理；不生成作者缺失证明，不自行修正未解决的数学对应，不绕过依赖/许可拒绝

H1/H2/H3为既有粗筛标签。已准入条目的复核仅是材料/来源/完整性与有限难度判断，不是独立数学审稿；未准入历史和候选标签明确为未核验。

## 来源与许可安全

许可保留逐份原文实际证据及限制，GNU FDL、CC BY-SA、CC BY-NC-SA 等不能统一改写成项目许可证。公开可读/原生源可下载不等于允许再分发。明确public allowlist材料仍须保留署名、版本、改变说明及具体许可。所有原始HTML和headers保持私有，不能直接进入Git；用最小安全署名/许可事实见证替代。非独占arXiv原生转录辅助与无核验许可宏不能作为公开载荷。

文件存在性仅为本地快照检查；本次没有重新联网确认来源可达性。不存在的路径照实标记缺失。execution-snapshots/和temporary-execution/是原临时执行路径的可读映射，不表示这些大载荷已经装入本目录或Git。请结合交接包中的恢复说明取得实际原件。

SQLite以 `work_queue.sqlite.gz` 无损交付，解压及逐字节原库哈希见 [恢复说明](METADATA_WORK_QUEUE.md#恢复随附sqlite) 与 [传输清单](SQLITE-TRANSPORT.json)。不要将压缩格式变化误认为数据库内容变化。
