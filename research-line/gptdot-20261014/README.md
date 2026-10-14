# dot 独立作者题证产线

依据用户 2026-10-14 交接规范开展完整作者题证取材、定向去重、可编辑 TeX 编译和 SQLite 交付。项目总目标为 30,000 道，不表示本线已生产或准入该数量。

本线工作根为 `research-line/gptdot-20261014`，准备分支为 `gptdot/corpus-20261014`。不分配正式 problem_id，不修改其他生产线或控制服务。

## 当前进度

2026-10-14：初始取材。3 个作品已完成第一轮取材，共 4 个候选，其中 1 个因作者版本材料缺口暂缓；其中 2 个已发现第二线先行收集而排除；1 个待全部在途身份范围核查。已编译、已入库、已上传及正式公开新增均为 0。候选不计合格成果。

## 交付

约 25 道完整、去重、实际编译且可读的作者题证一批；SQLite 保存完整题面、证明、上下文和 TeX，准备分支上传不等同正式准入。

## 资源管理

只清理本线可恢复缓存；公开上传验证前保留来源和成品。未变成功材料不重复编译。使用系统 Python 3、XeLaTeX 和 latexmk，无 shell escape。

## 当前作品分工与别名

本节用于其他产线识别本线已开展的工作，不表示最终唯一性或正式准入。

- MD：Reducing Stochastic Games to Semidefinite Programming；DOI 10.4230/LIPIcs.ICALP.2025.145；arXiv 2411.09646；HAL hal-04902257、hal-05388185。固定正式会议版，Corollary 10 整体证明链一题，等待在途核对
- PM：Symmetric Proofs in the Ideal Proof System；DOI 10.4230/LIPIcs.MFCS.2025.40；arXiv 2504.16820v1。固定完整作者 v1，Theorems 15 和 20 两个候选已因第二线先行收集排除（该线提交 cd4b1327eb02aa8d5daa742bebc57da737791e77）；不编译、不计新增
- LL：Right-Linear Lattices；DOI 10.4230/LIPIcs.MFCS.2025.39；arXiv 2505.10303v1，作者版标题 An algebraic theory of ω-regular languages, via μν-expressions。整体完备性主结果暂缓：正式版支撑无完整展开；作者版定义文字与同版说明冲突。保留原文，不跨版本补证或自行修订

源文件固定版本与许可逐题记录。当前暂无交付批次；本分支启动文档上传不计题目上传数。

下一组正在初步核查：PM ITP2025.4（arXiv 2507.05327，divided_powers_journal）；LL ITP2025.9（steinberg-formalization，含原结果 arXiv 2411.05916 与 ICALP2021.84 近邻检查）。尚未形成可用题。
