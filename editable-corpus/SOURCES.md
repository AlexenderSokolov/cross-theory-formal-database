# 来源与许可说明 / Sources & licensing

本语料只使用**允许直接再分发**的来源；每题都保留可核验的许可证据。

## 1. 候选池（当前主池）
- 数据集：`{'url': 'https://huggingface.co/datasets/librarian-bots/arxiv-metadata-snapshot', 'readme_url': 'https://huggingface.co/datasets/librarian-bots/arxiv-metadata-snapshot/raw/main/README.md', 'repo_commit': '5071ce89fe1da64b9d51284b44b924412cd044b7', 'mirror_of': 'https://www.kaggle.com/datasets/Cornell-University/arxiv', 'declared_num_examples': 3195172, 'declared_download_size_bytes': 3017519181, 'observed_rows_scanned': 3195172, 'observed_total_shard_bytes': 3017519181, 'size_matches_declared': True, 'fields_in_parquet': ['id', 'submitter', 'authors', 'title', 'comments', 'journal-ref', 'doi', 'report-no', 'categories', 'license', 'abstract', 'versions', 'update_date', 'authors_parsed'], 'readme_field_list': ['id', 'submitter', 'authors', 'title', 'comments', 'journal-ref', 'doi', 'abstract', 'categories', 'versions', 'license']}`
- 过滤表达式：`license.str.contains('creativecommons.org/licenses/by/4.0') & categories.str.contains('math.')`
- 结果：3,195,172 行 → 数学 789,838 → 数学 ∩ CC BY 4.0 **112,673**
- 分片哈希、阶段计数、工具版本：见 `source-cache/new-source-intake/arxiv-snapshot-r002/receipt.json`
- 过滤器经**实测校验**：36/36 抽样（24 个候选 + 12 个负对照：非独占/CC0/by-nc-sa）与实时 `abs.html` 许可字符串一致
- 生产顺序：`worklist-r001.json`（已耗尽）、`worklist-r002.json`（10,000 条，按 update_date 降序）
- 去重：`exclude-arxiv-ids.txt`（已被 master/旧池占用的 arXiv id）

## 2. 历史池
- `arxiv-math-oai-r001`：arXiv OAI-PMH（`set=math`）首批 CC BY 4.0 候选 434 条 → id 段 8001–8099
- EJDE 2026 原生 TeX 候选（`10.58997/ejde.2026.NN`）→ id 段 7001–7099
- 另有既有 OA 家族（alco / jep / ahl / aljabr / documenta）等历史来源

## 3. 许可与权利政策
- **只收录允许直接再分发的许可**：arXiv 的 CC BY 系列（4.0 为主）+ 既有 OA 家族；**不**采用 CC BY-SA/NC/ND 语料，**不**采用形式化库（mathlib/AFP 非人类证明）
- 每题在包内保留**真实许可证 notice**（`package-root-*/licenses/*.txt`），声明必须对"实际交付内容"严格为真（资产、图形包含命令、保真回执、捆绑的 `sources/<id>/source0.tex`、发行商类文件不转发）
- 许可证人：抓取时保存的 `abs.html`（sha256 记录）+ 池元数据 `license_metadata`
- 发行商类文件（IEEEtran/imsart/sn-jnl/informs3/ejpecp/lmcs/acmart 等）**一律不转发**，wrapper 统一为 amsart 并复述论文自己的 `\newtheorem`/宏定义

## 4. 版本与撤回处理
- 一律使用候选指定版本；若该版本 e-print/PDF 404（作者或管理员撤回），回退到**最新完整版本**，并在 `SOURCE_MAPPING.notes`、`STATUS-LEAD.json`、scope 与 notice 四处披露
- PDF-only e-print（无 TeX）→ `FETCH-FAILURE.json` 并 HOLD，不生产

## 5. 每题的来源字段（机器可读）
`catalog.json` 每项含：`problem_id, arxiv_id, version, title, author, claim, H, tex_sha256, license`；
逐题完整证据在 `candidates/native-pilot/<id>/`：`SOURCE_MAPPING.json`（来源映射）、`STRUCTURE-r001.json`（定理结构）、
`package-root-*/delivery-evidence.json`（交付证据与保真回执）、`receipts-root-*/<id>.json`（编译回执）、`licenses/*.txt`（许可 notice）。
