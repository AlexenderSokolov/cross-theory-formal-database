# dot 独立作者题证产线

依据用户 2026-10-14 交接规范和 2026-10-15 持续生产指令，开展完整作者题证取材、定向去重、可编辑 TeX 编译和 SQLite 交付。项目总目标为 30,000 道，不表示本线已生产或准入该数量。

本线工作根为 `research-line/gptdot-20261014`，准备分支为 `gptdot/corpus-20261014`。本阶段是 `author_material_collection`；不认证作者数学，不分配正式 problem_id，不修改其他生产线或控制服务，准备分支交付不等于正式资格认定或生产主库新增。

## 当前进度

2026-10-15 01:01 UTC 快照：14 个作品形成 17 个候选主张，其中 4 道可用作者题证已实际编译、完成可读性检查并写入含完整题面的 SQLite。其余 8 道待最终在途范围整合及装配，2 道暂缓，3 道排除（2 道来源先被他线收集，1 道与既有计数主张重复）。已上传题目为 0，生产主库公开增量为 0。候选、已编译、已入库和已上传分别计数，同一任务的修订不重复计数。

首批 [INDEX](delivery/batch-001/INDEX.md)、[ITEMS](delivery/batch-001/ITEMS.jsonl)、[SELECTION](delivery/batch-001/SELECTION.json) 和 [完整 SQLite](delivery/batch-001/corpus.sqlite3) 在本地准备完成；公开上传及远端核验尚未发生。现有启动文档提交不计题目上传数。

- MD-0001 r001：Reducing Stochastic Games to Semidefinite Programming，Corollary 10 整体证明链；11 页
- LL-0002 r002：Weak Steinberg relations imply the full graded A3, B3-small and B3-large relation sets；112 页，完整作者 Lean 代码已收录并排版，未执行 Lean，不声称形式化验证通过
- MD-0003 r001：Possible Sizes of Sumsets，Theorem 1.4 及完整当前核心；16 页
- PM-0004 r002：Composite Ramsey Theorems via Trees，独立几何-family 提升 Proposition 4.1；9 页

四道均有实际编译成功回执和 `readable` 呈现检查记录。LL-0002 的检查为选页视读及全页文本边界检查；这不是逐页语义阅读。旧 r001 排版修订记录保留，不作为第二道题或本次公开成品。

## 查重范围与继续位置

五条生产线在途身份快照已取得，完整工作清单身份均解析；2026-10-14 15:24:39 UTC 的增量检查未发现文件变化。公开主库增量最近复核至 `d6606aed2c59c18b3beb393b6488c8a0a8396a76`（20,588 条材料）：较 20,464 条快照新增 124 条，没有旧行变动，也没有四道成品当前来源或定向主张关键词命中；检查时间为 2026-10-14 15:47:17 UTC，见 [批次增量记录](delivery/batch-001/DEDUP_REFRESH.json)。材料总数不能转换为正式合格题数。

这些是有时间边界的已完成检查，不冒充 2026-10-15 的实时在途状态。上传前仍须刷新公开分支与全部在途变动。查重按具体计数主张及完整主证明义务判断，不以来源别名零命中替代语义比较。

8 道待处理：LL-0003、LL-0004、MD-0004、MD-0005、PM-0005、PM-0006、PM-0007、PM-0008。它们尚未进入本批成品或 SQLite，不计可用或已编译题。继续完成最终范围整合后逐题装配、实际编译、视读及入库，积累约 25 道净新增可用作者题证一批；上传核验后继续下一批。数量是快照，不能用此文件中的继续指令宣称存在后台运行服务。

## 当前作品分工与别名

本节供其他产线识别已开展的取材，避免并行重复；不是正式预约或准入。

### 已编译入库的四道

- MD-0001：Reducing Stochastic Games to Semidefinite Programming；DOI 10.4230/LIPIcs.ICALP.2025.145；arXiv 2411.09646；HAL hal-04902257、hal-05388185。只用固定正式会议版的 Corollary 10 整体证明链，不将其他版本许可混入
- LL-0002：ITP2025.9，steinberg-formalization，作者代码固定提交 `e02f0aaba4b045f5c1eadfe9078a3027a3b52d68`；原结果 arXiv 2411.05916、ICALP2021.84。已与 CCC2022.18 的既有全关系群内 normal form 作定向区分；未运行 Lean
- MD-0003：Possible Sizes of Sumsets；arXiv 2510.23022v3，DOI 10.19086/da.165102；Theorem 1.4 及完整当前核心整体一题，作者后续披露的模型生成直径界不收
- PM-0004：Composite Ramsey Theorems via Trees；arXiv 2210.14311v3，DOI 10.19086/da.165253；只计独立完整几何-family 提升 Proposition 4.1。迭代主定理 1.2 缺作者当前扩展正文而不收，不把该同作品未选目标另加为候选题数

### 八道待处理候选

- LL-0003：G3-Criteria and Applications，Mihai Halic，arXiv 2401.16196v4，DOI 10.46298/epiga.2026.12974；主 Theorem 3.1
- LL-0004：SIGMA 22 (2026), 091，DOI 10.3842/SIGMA.2026.091；奇异 Helffer–Nourrigat 锥的 dilation-compatible global Pedersen stratification
- MD-0004：Uniform unlikely intersections for unicritical polynomials，Hang Fu，arXiv 2009.12251v4，DOI 10.46298/epiga.2026.10958；主 Theorem 1.1
- MD-0005：arXiv 2407.06155v1；自然单位区间图的 elementary top coefficient 乘积公式，原 Theorem 3.11；后续 DOI 10.5802/alco.468 仅为别名，不混拼版本
- PM-0005、PM-0006：Chow quotients of C*-actions on convex varieties；arXiv 2503.19663v4，DOI 10.46298/epiga.2026.15529；分别为正规化 Chow 商的 SNC 边界与 nef/Mori 锥两个候选主张
- PM-0007、PM-0008：arXiv 2201.11553v4，EpiGA 10 (2026), Article 19；分别为光滑方案的 Zariski Gersten 正合性与保留明确条件的半稳定结点 Gersten 正合性

### 两道暂缓与三道排除

- LL-0001 暂缓：Right-Linear Lattices；DOI 10.4230/LIPIcs.MFCS.2025.39；arXiv 2505.10303v1，作者版标题 An algebraic theory of ω-regular languages, via μν-expressions。正式版支撑无完整展开；作者版定义文字与同版说明冲突。保留原文，不跨版本补证或自行修订
- MD-0002 暂缓：SoCG2025.45，arXiv 2409.00682；完整材料保留，但符号传播及奇偶论证尚不足以支持严格 H2 门槛
- PM-0001、PM-0002 排除：Symmetric Proofs in the Ideal Proof System；DOI 10.4230/LIPIcs.MFCS.2025.40，arXiv 2504.16820v1。Theorems 15 和 20 已被第二线先行收集（提交 `cd4b1327eb02aa8d5daa742bebc57da737791e77`），不编译、不计新增
- PM-0003 排除：ITP2025.4，arXiv 2507.05327，divided_powers_journal；两理想相容 PD 结构延拓主张与既有 S9-dpa-two-ideals / Stacks Tag07GQ 重复，保留材料但不编译计数

## 公开交付范围与许可

以逐题明确白名单和 `operations/prepare_upload_manifest.py` 的实际输出选择文件，不整目录暂存。发布候选清单为 `delivery/batch-001/PUBLIC_UPLOAD_MANIFEST.json`；它记录四道有效修订的成品、完整 SQLite、索引、必要原件和许可，以及本线说明文件。清单不表示已经提交或上传；内容变化后须重新生成。

- ICALP2025.145 仅公开正式会议版 CC BY 4.0 范围；arXiv 2411.09646v1/v2 的 nonexclusive 来源、HAL 材料及未明确许可的第三方样式不列入
- ITP2025.9 会议论文为 CC BY 4.0，固定作者 Lean 代码为 Apache-2.0，分别保留署名与许可。外部标准 Lean/mathlib 依赖只保留固定版本引用，不重新打包
- 两篇 Discrete Analysis 材料固定 v3 的原生作者 TeX/图及元数据按 CC BY 4.0；原 PDF 内 CC BY 3.0 链接另行保留说明，不统一改写原许可。早期 v1/v2、完整源码归档、许可未明确的 daj.cls/tocbase.cls、模板 PNG 和无关照片不公开
- `.work`、私有身份快照、暂缓/排除/待处理任务、失败或旧修订成品、临时传输文件、编译中间文件及 QA 渲染图不上传

## 运行与资源管理

复用本线 [operations 说明](operations/README.md)。使用系统 Python 3、XeLaTeX 和 latexmk，无 shell escape；仅在本线维护所需运行缓存。未变成功材料不重复编译。公开上传验证前保留来源、成品、旧修订和失败记录，只按既有授权处理可恢复缓存。

SQLite 保存完整题面、作者证明、必要上下文和成品 TeX，行状态保持 `prepared_unpublished`。ITEMS 的 `problem_id` 为 null；SQLite 内 `task_json` 沿用装配器生成的本线 GPDOT 任务 ID 作为内部 `problem_id`，不属于正式题号分配。上传使用现有授权连接，仅普通快进更新本线准备分支；核对远端提交、入口和文件可用后再记录上传数。不得 force push、改动生产控制或把上传当成正式准入。
