# dot 独立作者题证产线

依据用户 2026-10-14 交接规范和 2026-10-15 持续生产指令，开展完整作者题证取材、定向去重、可编辑 TeX 编译和 SQLite 交付。项目总目标为 30,000 道，不表示本线已生产或准入该数量。

本线工作根为 `research-line/gptdot-20261014`，准备分支为 `gptdot/corpus-20261014`。本阶段是 `author_material_collection`；不认证作者数学，不分配正式 problem_id，不修改其他生产线或控制服务，准备分支交付不等于正式资格认定或生产主库新增。

## 当前进度

2026-10-15 11:33 UTC：35 个当前候选任务，来自 31 个原始作品。29 道完整作者题证已实际编译、通过可读性检查、完整保存到本线 SQLite，并全部提交准备分支；3 道暂缓、3 道排除。生产主库本线公开增量 0，最终全局唯一资格仍未确认。子智能体因预览额度耗尽退出，目前没有并行生产后台。

- [第一批 INDEX](delivery/batch-001/INDEX.md)：4 道，已发布提交 `1bc7a42971fb6705cfd04b937c393d569c4683b6`
- [第二批 INDEX](delivery/batch-002/INDEX.md)：11 道，已发布提交 `8f4a372766c903ac7ac967e944f5975ddd5f8a4c`
- [第三批 INDEX](delivery/batch-003/INDEX.md)：11 道，已发布提交 `8efb535cec0cba19b39b61611533201cf50a254b`
- [第四批 INDEX](delivery/batch-004/INDEX.md)：1 道，LL-0009 r002，已发布提交 `2147e1a62e14a7a06b57437e4eb77bd35c7ede2b`
- [第五批 INDEX](delivery/batch-005/INDEX.md)：1 道，LL-0010 r003，已发布提交 `5d666e6d545d1f24365828d4b970213d88d4c59e`
- [第六批 INDEX](delivery/batch-006/INDEX.md)：1 道，MD-0011 r001，已发布提交 `6b3bec4f7db93725bf4fe90e0276e78f1354ae5f`

各批有独立完整 SQLite、ITEMS 与 SELECTION；任务集合不重叠。前两批累计 15 道；第三至第六批增加 14 道，总计 29 道。各批 UPLOADED.json 记录固定内容提交及实核依据。冻结清单中的 prepared_unpublished 是创建时状态，不能代替之后的 UPLOADED 回执或触发重复上传。

## 查重范围与继续位置

完整旧库与保存的在途身份已参与定向检查；最后成功在途快照截至 2026-10-14 17:36:45 UTC。公开 main 已复核至 `652c73d739c2d5f85ef9e56e2b14e93310b2e024`；前次以来的 398 条新增没有已查候选的新精确身份命中。LL-0004 的旧同源条目 190870 已单独比较计数主张，不能把同源或共享引理直接当重复。

此后在途重合情况尚未确认，见 [准备交付限制](delivery/batch-001/PUBLICATION_LIMITS.md)。本分支和备份只提供准备材料，不据此宣称现行全局唯一资格，也不增加生产主库计数。后续接收仍须完成现有准入步骤。

继续在独立云电脑整理新的精确作品、处理实际 TeX/许可/完整性问题并完成提交；不操作服务器或其他产线。ALCO502 已完成并纳入上述候选和成品；ALCO505 仍仅预筛，未形成 task.json，不计题数。

## 当前作品分工与别名

本节供其他产线识别已开展的取材，避免并行重复；不是正式预约或准入。

### 首四道已编译入库材料

- MD-0001：Reducing Stochastic Games to Semidefinite Programming；DOI 10.4230/LIPIcs.ICALP.2025.145；arXiv 2411.09646；HAL hal-04902257、hal-05388185。只用固定正式会议版的 Corollary 10 整体证明链，不将其他版本许可混入
- LL-0002：ITP2025.9，steinberg-formalization，作者代码固定提交 `e02f0aaba4b045f5c1eadfe9078a3027a3b52d68`；原结果 arXiv 2411.05916、ICALP2021.84。已与 CCC2022.18 的既有全关系群内 normal form 作定向区分；未运行 Lean
- MD-0003：Possible Sizes of Sumsets；arXiv 2510.23022v3，DOI 10.19086/da.165102；Theorem 1.4 及完整当前核心整体一题，作者后续披露的模型生成直径界不收
- PM-0004：Composite Ramsey Theorems via Trees；arXiv 2210.14311v3，DOI 10.19086/da.165253；只计独立完整几何-family 提升 Proposition 4.1。迭代主定理 1.2 缺作者当前扩展正文而不收，不把该同作品未选目标另加为候选题数

### 后续八道候选及其来源（当前完成状态见上方 INDEX）

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

以逐题明确白名单和 `operations/prepare_upload_manifest.py` 的实际输出选择文件，不整目录暂存。发布候选清单为 `delivery/batch-003/PUBLIC_UPLOAD_MANIFEST.json`；它记录当前选择的有效修订成品、完整 SQLite、索引、必要原件和许可，以及本线说明文件。清单不表示已经提交或上传；内容变化后须重新生成。

- ICALP2025.145 仅公开正式会议版 CC BY 4.0 范围；arXiv 2411.09646v1/v2 的 nonexclusive 来源、HAL 材料及未明确许可的第三方样式不列入
- ITP2025.9 会议论文为 CC BY 4.0，固定作者 Lean 代码为 Apache-2.0，分别保留署名与许可。外部标准 Lean/mathlib 依赖只保留固定版本引用，不重新打包
- 两篇 Discrete Analysis 材料固定 v3 的原生作者 TeX/图及元数据按 CC BY 4.0；原 PDF 内 CC BY 3.0 链接另行保留说明，不统一改写原许可。早期 v1/v2、完整源码归档、许可未明确的 daj.cls/tocbase.cls、模板 PNG 和无关照片不公开
- `.work`、私有身份快照、暂缓/排除/待处理任务、失败或旧修订成品、临时传输文件、编译中间文件及 QA 渲染图不上传

## 运行与资源管理

复用本线 [operations 说明](operations/README.md)。使用系统 Python 3、XeLaTeX 和 latexmk，无 shell escape；仅在本线维护所需运行缓存。未变成功材料不重复编译。公开上传验证前保留来源、成品、旧修订和失败记录，只按既有授权处理可恢复缓存。

SQLite 保存完整题面、作者证明、必要上下文和成品 TeX，行状态保持 `prepared_unpublished`。ITEMS 的 `problem_id` 为 null；SQLite 内 `task_json` 沿用装配器生成的本线 GPDOT 任务 ID 作为内部 `problem_id`，不属于正式题号分配。上传使用现有授权连接，仅普通快进更新本线准备分支；核对远端提交、入口和文件可用后再记录上传数。不得 force push、改动生产控制或把上传当成正式准入。

## 后续已完成的两个原始作品

- LL-0005：Hyperbolic actions of Thompson's group F and generalizations，DOI 10.5802/alco.506；使用正式期刊公开 TeX，Theorem A / 4.4 及完整当前核心整体一题，21 页。
- MD-0006：Representation Stability in the Intrinsic Hyperplane Arrangements Associated to Irreducible Representations of the Symmetric Groups，DOI 10.5802/alco.498；正式 CC BY 4.0 PDF 忠实转录，Theorem 3.7 及完整当前 Proposition 3.5 核心整体一题，6 页。

## 最新已完成作品

- LL-0006：Shuffle Tableaux, Littlewood–Richardson Coefficients, and Schur Log-Concavity，DOI 10.5802/alco.502，正式 CC BY 4.0 TeX。独立 Proposition 2.13 及 Lemmas 2.14–2.17 完整作者证明整体一题，7 页；不收缺少完整当前证明的另一个主定理 1.2。四个图形从同版正式 PDF 精确矢量提取。r003 修正编辑性前提引用为 Corollary 2.7，作者数学正文未改。

## 第三批本地完整材料

PM-0009 至 PM-0014 分别对应 arXiv2307.10461v4（双曲性）、2408.11645v3（K3 型循环核界）、2207.07623v3（perfectoid torsor 拓扑比较）、2302.09412v3（del Pezzo GW 对应）、2502.17236v3（descendant log-GW 与量子 broken lines）、2211.16207v5（norm 延拓判据）。LL-0007 为 DOI10.5802/ahl.276 的 Lemma6.2 完整小扩张构造；MD-0007 为 DOI10.5802/ahl.275 的自由 multi-Novikov 实现；MD-0008 为 DOI10.5802/jep.338 的 Proposition4.5 同时形式延拓。具体题干、完整作者核心、许可和可复现来源见逐题记录与第三批索引；未上传不计公开交付。

ALCO505 只保留未登记的来源暂缓记录：正式作者多项式的两种给定表达有直接数值矛盾，未修改数学或计入候选。DA144978 的主证明所引 notebook 未随已得版本取得，同样不计完整产出。

第三批另含 MD-0009（DOI10.5802/alco.495，Theorem1.1 完整第一证明）与 LL-0008（DOI10.5802/alco.500，校正后正式出版 Theorem4.3 及完整当前构造核心）。ALCO497/MD-0010 已登记为来源暂缓，未装配、编译或计可用；其最终证明中的原文歧义保留，没有自行解释修复。
