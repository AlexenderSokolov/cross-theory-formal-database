---
name: human-proof-corpus
description: Use when collecting, admitting, validating, counting, or recovering source-grounded mathematical problems with human-authored proofs, especially when editable delivery or corpus completion is required.
---

# Human-proof corpus

Count unique independent problem units only after the current delivery gate passes. Mechanical checks establish material fidelity/consistency, not mathematical correctness, authorship, difficulty, or semantic uniqueness. Never add an AI-generated proof, mathematical referee, or cross-theory difficulty ranking.

## 固定生产流程与worker交付

持续使用Stop That Shit。固定3个来源workers，每块10—20候选连续处理；root独占准入、H、必要core覆盖、semantic和发布。沿用项目Python3.13与已有源缓存，按真实模型配额排队；8次历史启动不能当作8个有效worker，不爆发重试。

worker只交付一条可接续contract：**题号；固定final包；原命题／完整证明／必要新core的来源定位；H1/H2/H3及2—4句具体理由；逐项许可；真实compile／最终日志／必要page QA；已有最终item gate或具体hold。** 已存在的兼容字段由现有helper自动记录；不追加目录hash、多层pins、专门hash报告测试或框架。

原文引用、必要资产及最终排版在小包前置完成。对固定final输入调用一次真实compile流程，完成page QA和必要兼容投影后仅执行一次最终 `--item`。helper内部2—4个真实成功TeX passes仍保留。已绿且输入未变时复用已有证据；不重复same single aggregate、不逐题CAS恢复、不逐题main合并。已交付final revision不再编辑；真实失败或必要改动才进入新revision，并保留原件及旧历史。

root读取交接定位及已有索引的必要范围，不重转全文、不反复全库扫描。每25个净新增准入项执行一次真正multi-pack主库rebuild、aggregate、发布及公开恢复；稳定后扩至100项checkpoint，每500项完整对账。独立备份与main重叠时计晋级0。

Stop Ladder依次问：用户是否要求；是否完成当前结果所必需；什么实际数据／接口／验收要求证明必要；略去是否会让本次任务失败。无必要依据就停止扩展。只有实际题证、验收和计数推进才是production；重复思考、重复报告不算产出，不另造平台、网站或技能大框架。

## Material contract

- Include the complete original human statement, proof and necessary source-local core in each standalone editable TeX document. Preserve language, hypotheses, organization and mathematical symbols. PDF-page wrappers, proof images, links, summaries and external proof inputs are provenance or context, not editable bodies.
- Read consecutive authored proof/support passages in a pinned revision. Retain exact excerpts, locators, author, version, retrieval date and license, with the existing helper-generated compatibility identity fields. Match editorial titles to essential hypotheses; compare version, DOI and header evidence. Hold ambiguous core formulas or missing new local constructions. Never choose a mathematical repair to meet a quota.
- Distinguish source-local new arguments from ordinary named prerequisites. Include the former; a precise citation with intact hypotheses suffices for the latter. Omit irrelevant artwork and publisher frontmatter within the user’s agreed scope without reopening approval. Record bounded ancillary omissions; they cannot excuse omitted substantive core.
- Check semantic uniqueness across sources, tags and formats. Count one independent claim once; supporting results remain uncounted context. H1/H2/H3 needs 2–4 concrete rationale sentences explaining why the selected result exceeds ordinary PhD quals. Labels or a research venue alone do not establish difficulty.

## Delivery gate

| Evidence | Required decision |
|---|---|
| Historical count or file total | Do not use as editable completion |
| Empty receipt warnings | Inspect the actual hash-bound final log |
| Local gate pass | Report local qualification until remote delivery is verified |

Compile the actual final layout with no shell escape for at least two, up to four actual successful TeX passes. Record the true pass count and bind input, assets, PDF and logs. Require a stable final pass with no unresolved references/citations, missing glyphs, label/bookmark/outlines/PageLabels rerun requests or duplicate labels, even when receipt warning fields are missing or empty. Deduplicate overlapping identical contexts with precise source mapping in a new pinned revision, then rebuild; never relax uniqueness guards.

Require manifest/provenance/INDEX agreement, unique stable IDs/claims, SQLite integrity/foreign keys and exact full delivered TeX in its full-text field. Prepare the required small-package projections once before the final item gate; the main rebuild and aggregate belong to the 25-item multi-pack checkpoint. Hold failures with reasons. Preserve prior receipts, drafts and source bytes; isolate staging and serialize shared-state writes.

Use the current [incremental workflow](references/incremental-workflow.md) for cached acquisition, exact reference transcription, disjoint workers, fixed recovery code, batch merge and actual public restoration. Reuse [corpus delivery tools](../../../scripts/corpus_delivery_tools.py); these deterministic mechanics never grant source, difficulty or semantic admission. The [project workflow](references/project-workflow.md) retains historical examples, which are not current acceptance receipts. Bare historical `--item` cannot admit editable data. Respect explicit source-access denials; alternate accounts, browsers or caches cannot evade them.

Publication belongs to root at the multi-pack checkpoint. Existing compile/restore helpers record and check the required remote commit, manifest, INDEX and TeX identity fields; do not add separate hash-report layers. For this project, download the exact public commit and all declared database parts/CAS, actually restore into a new server directory, and verify complete SQLite projection and delivery gates before increasing the corresponding delivered total. Hash-only remote comparison is diagnostic evidence, not this project’s completed restoration. Quota, deadline, local success and a pending upload do not change this contract.

批次checkpoint的发布候选和真实本地恢复按 [references/release-preparation.md](references/release-preparation.md) 执行；复用 `corpus-work/run_prepare_release.sh`，明确签审文件清单与实际aggregate身份；远端精确恢复成功才计交付。

公开恢复取材可复用 [public transport](references/public-transport.md)：已核验旧公开恢复缓存按固定文件清单复制，变化文件按精确提交下载。`run_public_transport.sh` 只准备材料和逐文件账，SQLite/编译资产恢复及门禁必须另做；prepared receipt 不能冒充已完成公开恢复。


## Durable controller

Read the repository root `DOT_HANDOFF.md` for Your dot takeover. Use `corpus-work/corpusctl status --json` as the current runtime/queue view. The Yupeng user service continues submitted jobs and merges a full admitted batch; root/dot still makes explicit material, difficulty, rights and semantic decisions. A successful worker exit can contain zero admissible packets. Resume its unfinished material stage; never count exit0 as a new problem. A process proven stuck inspecting its own events is an execution failure, not sourcehold. Preserve outputs and terminal evidence before an explicitly reviewed revision.

Use fixed JOB_ID and both `id:ID` and work identity in claims. Current/final package paths come from queue/READY, not historical launcher defaults. GitHub authentication belongs to the controller (Your dot cloud computer after actual connection). Normal Git bundle publishing retains concurrent remote changes; verify-public alone updates delivered count. Service install/status: `corpus-work/run_corpusctl_service.sh`. Engineering checks are for related code changes only, never per-item steps.
