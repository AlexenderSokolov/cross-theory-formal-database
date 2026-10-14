# dot 独立作者题证产线

依据用户 2026-10-14 交接规范开展完整作者题证取材、定向去重、可编辑 TeX 编译和 SQLite 交付。项目总目标为 30,000 道，不表示本线已生产或准入该数量。

本线工作根为 `research-line/gptdot-20261014`，准备分支为 `gptdot/corpus-20261014`。不分配正式 problem_id，不修改其他生产线或控制服务。

## 当前进度

2026-10-14 15:55 UTC：8 个作品形成 9 个候选主张。2 道已实际编译、检查排版并写入含完整题证的 SQLite；另 1 道编译成功待视读，1 道正在编译。2 道暂缓（版本材料、难度），2 道来源先被他线收集，1 道与既有主张实质重复。已上传题目及正式公开新增仍为 0。另有 3 个新作品正在取材，未计候选。

五条生产线在途身份快照已取得，完整工作清单身份均解析；15:24 UTC 增量检查未发现文件变化。查重仍按具体主张与完整主证明义务判断，不以来源别名零命中替代语义检查。

首批成品在本线本地积累，待批次上传后提供 INDEX、TeX、PDF 与 SQLite；未经上传验证前不计已交付。

## 交付

约 25 道完整、去重、实际编译且可读的作者题证一批；SQLite 保存完整题面、证明、上下文和 TeX，准备分支上传不等同正式准入。

## 资源管理

只清理本线可恢复缓存；公开上传验证前保留来源和成品。未变成功材料不重复编译。使用系统 Python 3、XeLaTeX 和 latexmk，无 shell escape。

## 当前作品分工与别名

本节用于其他产线识别本线已开展的工作，不表示最终唯一性或正式准入。

- MD：Reducing Stochastic Games to Semidefinite Programming；DOI 10.4230/LIPIcs.ICALP.2025.145；arXiv 2411.09646；HAL hal-04902257、hal-05388185。固定正式会议版，Corollary 10 整体证明链一题，已定向查重、实际编译并入本线 SQLite，尚未上传
- PM：Symmetric Proofs in the Ideal Proof System；DOI 10.4230/LIPIcs.MFCS.2025.40；arXiv 2504.16820v1。固定完整作者 v1，Theorems 15 和 20 两个候选已因第二线先行收集排除（该线提交 cd4b1327eb02aa8d5daa742bebc57da737791e77）；不编译、不计新增
- LL：Right-Linear Lattices；DOI 10.4230/LIPIcs.MFCS.2025.39；arXiv 2505.10303v1，作者版标题 An algebraic theory of ω-regular languages, via μν-expressions。整体完备性主结果暂缓：正式版支撑无完整展开；作者版定义文字与同版说明冲突。保留原文，不跨版本补证或自行修订

源文件固定版本与许可逐题记录。首批已开始积累；本分支启动文档上传不计题目上传数。

- PM ITP2025.4（arXiv 2507.05327，divided_powers_journal）的两理想相容PD结构延拓主张与既有 S9-dpa-two-ideals / Stacks Tag07GQ 重复，保留材料但不编译计数
- LL ITP2025.9（steinberg-formalization，原结果 arXiv 2411.05916、ICALP2021.84）：完整作者 Lean 代码，未运行 Lean；与 CCC2022.18 的既有全关系群内 normal form 区分，已完成定向近邻核对，实际排版为112页，入本线SQLite；未运行Lean
- MD SoCG2025.45（arXiv 2409.00682）：完整材料保留，因符号传播及奇偶论证尚不足以支持严格 H2 门槛暂缓
- 新取材：Composite Ramsey theorems via trees（arXiv2210.14311、DOI10.19086/da.165253）；Possible Sizes of Sumsets（arXiv2510.23022、DOI10.19086/da.165102）


## 当前新作品占用提示

这是本线取材身份提示，避免并行重复；不表示正式预约或准入。

- PM：Composite Ramsey theorems via trees，arXiv2210.14311v3，DOI10.19086/da.165253；计数目标仅独立完整几何-family提升 Proposition4.1。迭代主定理1.2缺作者当前扩展正文而不收
- MD：Possible Sizes of Sumsets，arXiv2510.23022v3，DOI10.19086/da.165102；整体Theorem1.4及完整当前核心一题。作者后续披露的模型生成直径界不收
- LL：G3-Criteria and Applications，Mihai Halic，arXiv2401.16196v4，DOI10.46298/epiga.2026.12974；正在取材主Theorem3.1
- MD：Uniform unlikely intersections for unicritical polynomials，Hang Fu，arXiv2009.12251v4，DOI10.46298/epiga.2026.10958；正在取材主Theorem1.1
- PM：Chow quotients of C*-actions on convex varieties，arXiv2503.19663，DOI10.46298/epiga.2026.15529；刚开始版本、完整主证明及旧作语义近邻检查，尚无冻结候选

最近公开主库增量范围已复核到 d6606aed2c59c18b3beb393b6488c8a0a8396a76（20,588 条材料）；较20,464快照新增124条，没有旧行变动，也没有本线当前来源/定向主张关键词命中。该材料总数不能转换为合格题数。
