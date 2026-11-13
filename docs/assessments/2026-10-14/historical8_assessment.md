## 本组结论与适用边界

已通过 GitHub 连接器读取固定提交 41b4ab870b5b24d235c74e7123bccba6d9b9b042 的8份完整 TeX 与对应 provenance，并读到各计数主张的连续证明和必要支撑块。以下是难度与重合风险的辅助判断，不是数学正确性认证，不改变生产 H 或资格。

本组判断：
- 有证据高于普通博士 qual：432、1309、773、901、887
- 边界：062、947、191407
- 没有将任何题判为“明显低于”；边界不等于确认满足严格超标门槛
- 这8题属于24题分层目的样本，不能据此计算或外推总体合格率

比较锚点已核读：
- [Harvard syllabus](https://www.math.harvard.edu/graduate/study-the-qualifying-exam/the-qualifying-exam-syllabus/)：考察识别、应用重要定理解决具体问题，明确不要求很强的独创巧思
- [UCLA syllabus](https://ww3.math.ucla.edu/qualifying-exam-dates/)：代数 qual 已包括张量积、范畴、平坦/投射/内射模、中心单代数和 Artin–Wedderburn，不能把这些术语本身当作超标证据
- [Wisconsin syllabus](https://www.math.wisc.edu/graduate/current-phd/qualifying-exams/topics/)：以一年级研究生课程及本科先修为基准，平坦/投射模、Hom、局部化等属于标准知识范围

## 062：Skolem–Noether 共轭定理

主张：有限维中心单代数 A 中，简单 k-代数 B 的两个嵌入相差一个内共轭。

关键步骤与先修：
- 标准先修：Artin–Wedderburn、矩阵代数的模、简单模分解、交换子代数
- 局部核心：用最短张量表示与交换子降低长度证明中心除环张量积的单性；把两个 B⊗Lᵒᵖ 模结构的同构转成 A 中的可逆元

辅助判断：边界，偏向普通研究生代数较难题；置信度：高。

理由：主证明不是简单“套定理名”，必须想到在同一简单 A-模上比较两种扩张作用，并利用双交换子将交织算子识别为内共轭。将交付包中保留的支撑证明一起计入后，最实质的额外技巧仍是最小张量长度的交换子论证；它巧妙，但与标准中心单代数课程的证明技巧连续，UCLA 明确覆盖相应先修。因此没有足够证据仅凭当前完整单元确认它严格高于普通 qual，而不能因为附有这些证明就将原题缩成末尾几行。

证据：
- [固定 TeX：主张与证明 L213–238](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/062_stacks_074Q.tex#L213-L238)
- 同文件 L105–143：简单模与交换子；L145–211：张量单性与最小长度核心
- [原来源 Stacks 074Q](https://stacks.math.columbia.edu/tag/074Q)

重合风险：应与任何单独计数的 Stacks 074E、074F、074C、074B 比对；它们在本题中作为支撑整体保留，若另计为独立题，会形成“主定理—支撑命题”嵌套。与本组另两道 Stacks 题未见相同主张或相同决定性证明。

## 432：Smooth base change

主张：光滑态射与拟紧拟分离基态射构成的笛卡尔方块中，素于特征的 torsion étale sheaf 高阶直接像满足光滑基变换。

关键步骤与先修：
- 可引用背景：光滑态射的局部结构、滤过余极限相容性、有限映射高阶直接像消失、Leray 谱序列、泛纤维覆盖的延拓等
- 必须完成的主证明核心：在逆像不保持内射性的情况下构造 effacement；相对曲线约化、有限型下降、有限正规化与分裂嵌入，最终结合上同调次数归纳和支撑维数归纳

辅助判断：有证据高于；置信度：高。

理由：即使允许引用列出的外部工具，证明仍须设计一条保持待消灭上同调类的约化链，特别是在有限覆盖后保留分裂关系并把泛纤维消失推广到稠密开集。末段不是单次五引理：开集部分需要较低上同调次数的消失，闭补部分需要较低维度归纳，两条归纳相互配合完成 effacement。这一具体证明结构明显超出普通 qual 的局部定理应用，判断不依赖“étale”术语或篇幅。

证据：
- [固定 TeX：主张 L105–121，第一连续证明 L123–519](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/432_stacks_0EYU.tex#L105-L519)
- L约230–291：归约到 pulled-back injective 的消失与有限型下降
- L约327–455：有限覆盖、正规化、泛纤维消灭；L457–518：开闭分解与双归纳收尾
- L521–628：第二证明，同一结论的另一组织方式
- [原来源 Stacks 0EYU](https://stacks.math.columbia.edu/tag/0EYU)

重合风险：两个证明只能支持同一个计数单元，不能作为两题。若库中另有 0EYT、0EYJ、0F08 等被引用支撑结果，应核查它们是独立任务还是重复计入同一核心；仅“存在依赖”尚不足以认定重复。

## 1309：可数生成 flat Mittag–Leffler 模是投射模

主张：任意环上的可数生成、平坦、Mittag–Leffler 模为投射模。

关键步骤与先修：
- 可引用背景：Lazard 定理；Hom 对第一个变量余极限转逆极限；有限表示模与纯正合分裂的基本结果
- 本包局部核心：建立 domination/因子分解/逆系统稳定性的等价刻画；构造保留所有必要稳定关系的可数有向子系统；证明 countable Mittag–Leffler 逆极限保持所需满射

辅助判断：有证据高于；置信度：中高。

理由：不能把末尾 L416–447 的短 Hom 论证单独当作全部题目，因为可数子系统的选择与 Mittag–Leffler 刻画是保留的实质工作。关键不只是挑出可数个生成元，而是交替补充稳定因子分解和有向上界，确保缩小索引集后既不丢生成元，也不丢消灭关系。再将非空纤维的 Mittag–Leffler 稳定性转为逆极限满射，整体呈现超出普通平坦/投射模 qual 题的无限模控制要求；但其主体仍是高级教材定理，证据强度低于432。

证据：
- [固定 TeX：可数约化 L130–173](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/1309_stacks_059X.tex#L130-L173)
- 同文件 L176–280：五种刻画与连续证明；L283–362：domination 支撑
- L365–407：逆极限正合核心；L410–447：主张与主证明
- [原来源 Stacks 059X](https://stacks.math.columbia.edu/tag/059X)

重合风险：本题的大部分难度集中在已嵌入的 ML 刻画、可数约化和逆极限正合支撑；若这些在其他行又作为完整题出现，会有较高的支撑重合风险。不能用多个支撑命题的数量把本题拆成多个独立高难单位。

## 773：Garsia–Procesi 环的 charge 单项式基

主张：对任意分拆 μ，由 insertion tableau 的 catabolizability dominance 条件选出的 charge 单项式组成 Rμ 的基，并与 Carlsson–Chou 的已有基相同。

关键步骤与先修：
- 明确背景工具：RSK 及反转/转置关系、charge/cocharge、Blasiak 的 catabolism insertion 算法及其输出性质、Carlsson–Chou 基定理
- 局部核心：证明算法所得每列子字仍为合法 cocharge word；把 catabolizability dominance 转成分拆列间移盒操作，并证明该过程保留各列合法性

辅助判断：有证据高于；置信度：中高。

理由：已有基定理只提供终点，不给出新构造与旧构造的识别；实际需要建立 insertion 读取次数、行位置与 cocharge 数值之间的控制。随后必须证明一盒 dominance 下降不破坏合法子字，并迭代得到所需 shuffle 分解，最后才可用基数一致完成等同性。这是针对该构造的多层不变量论证，不能归结为套用已知基定理；也没有将全文后半的额外新定理算入本题难度。

证据：
- [固定 TeX：主张 L677–686，识别证明 L739–801](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/773_alco_458.tex#L677-L801)
- 同文件 L341–382：cocharge word 刻画及插入稳定性
- L473–493：引用的 insertion 算法；L523–565：行号关系与列子字的局部证明
- [原来源 ALCO 10.5802/alco.458](https://alco.centre-mersenne.org/articles/10.5802/alco.458/)

重合风险：该文件保留整篇数学正文，L813 以后另有 catabolizability sum theorem、交换性质、antisymmetric 部分，不能把这些一概视为主张 A 必需证明。如果数据库另计同文 Theorem B 或其他主张，文件级大段重复不必然等于题目重复，但共同核心与真正独立的新增步骤必须分开核对。

## 947：周期图的累积增长为 quasi-polynomial

主张：实际计数的是原 Theorem 3.4(1)(2)：α-Ehrhart 条件推出累积增长准多项式；C₁+C₂&lt;1 保证适当 α 的 α-Ehrhart 条件。虽然题干还显示(3)互反律，文件明确排除它。

关键步骤与先修：
- 标准背景：周期图的格作用、增长多面体、rational cone 的整数点生成函数、三角剖分及 fundamental parallelepiped
- 局部核心：轨道分解把图球计数变成有限个平移、带实数偏移的 Ehrhart 计数；Appendix B 保留对这些计数的准多项式证明与适用起点控制

辅助判断：边界；置信度：中。

理由：主张(2)直接来自 C₁、C₂ 定义，(1)在轨道分解后确实依赖 Appendix B，不能把它当成免费引理而只评末尾短证明。把 Appendix B 计入后，需要锥化、三角剖分、半开基本平行体与生成函数分子次数控制，尤其保证从所述起点即准多项式，而非仅最终如此。证明路径主要沿已有 Ehrhart 方法展开，但属于专题教材本身不能证明其等同常规 qual；本次没有实际可比考试题支持这种等同判断。暂留“边界”只表示严格超标的正面证据尚不够确定，排除的互反律也不能用于抬高判断。

证据：
- [固定 TeX：计数主张 L448–464，连续证明 L491–523，排除说明 L525](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/947_author_proof.tex#L448-L525)
- 同文件 L529–564：必须支撑与仅引用结果的界线
- L622–702：Appendix B 定理与准多项式证明；L704–722 的互反部分不作为本题额外难度
- [原来源 ALCO 10.5802/alco.367](https://alco.centre-mersenne.org/articles/10.5802/alco.367/)

重合风险：本题与单独计数的平移 Ehrhart 定理、增长多面体支撑有嵌套风险。尤其不能因为整个印刷定理含(3)，就把本行当作又覆盖一套 reciprocity 结果；当前真正计数范围窄于印刷定理和文件显示范围。

## 901：不可嵌入微分 Zinbiel 代数的 derived Zinbiel 反例

主张：基域特征不为2或3时，存在 D-Zinbiel 代数不能嵌入任何带导子的 Zinbiel 代数。

关键步骤与先修：
- 背景工具：自由非结合代数与商、Zinbiel 正规形、derived operations、微分包络的泛性质
- 局部核心：选择 f=b·b′ 及其导数生成的微分理想 J，找到 h∈J∩D-Zinbiel 但 h∉(f)；将非包含性精确约化为16种导出乘积的正规形和秩障碍

辅助判断：有证据高于；置信度：高。

理由：核心不是对给出的16×16矩阵做消元，而是构造微分包络中必然消失、原商代数中却不消失的元素，并证明它进入每个可能嵌入的核。为证 h∉I，必须利用首字母不变与次数结构说明所列16种乘积穷尽有关分量，再连接到正规形线性独立性。这个反例设计与理想收缩论证有具体的非例行结构，明显强于仅依赖陌生 operad 术语的判断。

证据：
- [固定 TeX：主张与完整证明 L815–1002](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/901_author_proof.tex#L815-L1002)
- L821–891：自由微分代数、J、h 与包络核
- L893–1001：穷尽正规形与秩障碍
- [原来源 SIGMA 2024/017，Theorem 4.5](https://sigma-journal.com/2024/017/)

重合风险：同篇文章还有 derived algebra/Manin product 识别、weight criterion、special embedding 等在文件中保留的结果；若其他题同源，需要区分共用背景与本题特有反例。当前8题中未见相同核心；更大库内是否已单独计数这些支撑未在本子任务中验证。

## 887：固定步长 ideal HMC 的 O(κ) relaxation time

主张：μ-强凸、L-smooth 的势函数下，ideal HMC 取 T=1/(2√L) 时 relaxation time 为 O(κ)，κ=L/μ。

关键步骤与先修：
- 可引用工具：凸光滑函数的梯度 cocoercivity、不等式型 Grönwall、Markov Ricci curvature 到 spectral gap 的已有结果
- 本包局部核心：同初速度 Hamiltonian 耦合；保持时间变化的曲率量 ρ(t)，用 P(t)=∫ρ 的单调性控制速度误差，证明 T≈L⁻¹ᐟ² 下位置距离收缩

辅助判断：有证据高于；置信度：中高。

理由：末尾从 Wasserstein 收缩到 spectral gap 的转换是已知工具，不能把它本身当作本题新难度。真正关键在于不粗暴地把 ρ(t) 全部替换为 L 或 μ，而是保留累积曲率，使速度差带来的正项与位置差的负项在同一尺度下比较，得到 O(κ) 而非较差条件数依赖。这个估计设计比通常给定 Lyapunov 函数后套 Grönwall 的 qual 题有明确额外要求，但使用工具本身均相对基础，因此置信度不列最高。

证据：
- [固定 TeX：主张 L415–421，收缩核心 L484–637](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/887_author_proof.tex#L415-L637)
- L639–651：引用 Ricci curvature/spectral gap 结果收尾
- L654–704：粗界的连续证明
- [原来源 Theory of Computing v018a009](https://theoryofcomputing.org/articles/v018a009/)

重合风险：文件同时包含 matching lower bound 和 discretized HMC convergence，不能全计入当前上界题的难度。如果其他行分别计数下界或离散化结果，应特别检查共同 contraction lemma 的复用程度，而不能单凭共用正文认定整题重复。

## 191407：网络局部信号的自适应检测与定位边界

主张：稀疏 logistic fixed-design 网络模型中，在明确列出的 calibration、线性化、方差估计、packing 与设计条件下，扫描检测/定位在 a²n²ρh²≈log m 的尺度上具有上界与 minimax 下界。

关键步骤与先修：
- 题干已经假设：线性化余项速度、studentizer 一致性、目标偏差界、全局零假设下 multiplier calibration、packing 分离、重叠计数、oracle 到原实验的 Markov kernel 比较
- 本题剩余核心：Bernstein 与 Gaussian 尾界下的信号分离、经验 bootstrap 分位数的 DKW 控制、Bernoulli likelihood ratio 交叉二阶矩、稀疏重叠混合的 χ² 界及定位损失到 Fano 分类误差的转换

辅助判断：边界；置信度：中。

理由：不能把前文证明 calibration 或构造估计器的难度记到本题，因为这些已作为明确假设写入题干，尤其 L553–564 直接假设实际统计量的 uniform calibration。剩余证明有真实工作，包括相反符号交叉项可能为负时使用正部、利用重叠图控制 χ² 混合、把支持集损失转为可测解码误差，并正确串联条件与无条件风险。这些方法虽已有标准形式，完整组合仍是支持超标的正面证据，不能仅据其名称熟悉就降到 qual 水平；本次没有实际常规博士数学 qual 试题可证明该组合与常规考试等同。暂留“边界/中置信度”只反映在强假设下所剩证明工作的超标证据仍不够确定，1578行文件长度也不能单独证明超标。

证据：
- [固定 TeX：完整题干 L27–796](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/191407_author_proof.tex#L27-L796)
- L267–377：信息量、独立影响项、线性化/方差/偏差假设
- L542–568：已假定的 calibration；L636–730：下界实验与设计假设
- L798–1220：上界连续证明
- L1222–1575：下界连续证明，尤其 L1387–1440 的正部/重叠计数、L1490–1574 的 Fano 与定位解码
- [原来源 arXiv:2512.18592v2](https://arxiv.org/abs/2512.18592v2)

重合风险：与同文的 multiplier/bootstrap、线性化定理存在前提依赖，但当前题没有重新证明它们，不宜把它们的难度重复归入本行。检测与定位两种风险共享一套备择族、散度估计与尺度，也不宜据两个结论另算完全独立贡献。另需保留一个上下文提示：L29–30 仍以文字引用 preceding sections 的模型记号，虽然公式交叉引用均落在本包内部，“交叉引用闭合”不等于所有语义背景都独立重建；这不构成数学错误判定。

## 本8题的来源多样性与重合概况

1. 出处层面是五个来源平台/体系：Stacks 3题、ALCO 2题、SIGMA 1题、Theory of Computing 1题、arXiv 1题。不能把不同 Stacks 章节计作三个独立来源平台，也不能把 arXiv 版本号当成新增来源。
2. 作品层面是 Stacks 一个持续编写项目，加五篇不同论文，共六个作品单位。ALCO 两篇的作者与数学内容不同，属于真实的作品多样性，而非同篇拆分。
3. 作者群层面为 Stacks 集体作者，以及 Mitsuki Hanada；Takuya Inoue/Yusuke Nakamura；Pavel Kolesnikov/Farukh Mashurov/Bauyrzhan Sartayev；Zongchen Chen/Santosh S. Vempala；Marios Papamichalis/Regina Ruane，共六个不同作者群。
4. 本8题计数主张之间未见直接等价、改写或同一个证明换题面。主要风险是“完整交付包含有多个后来也可能被单计的支撑/旁支命题”，以及把引用工具、附带全文或明确排除的部分当作该题难度。
5. 以上仅是这8题之间的实读比对和其显式依赖风险识别；未完成对整个生产库的逐对去重，不能将“本组未见直接重复”写成“全库无重复”。

## 统一比较与重合判断限制

比较基准始终是常规博士数学资格考试及其一年级研究生课程背景，不是高年级统计专业资格考试或最难专题考试。947与191407均未获得实际可比考试题的直接证据；“边界”表示尚不足以确定严格超标，并不表示已经证明它们等同常规 qual。

支撑依赖、共享背景和文件级正文重合不自动构成题目重复。上文所列近邻仅是待核查的风险；未实际深读相关近邻之前，不能否定其作为独立题的资格，也不能据此合并或取消任何生产单元。

[评估目录](README.md) · [概览](difficulty_assessment_overview.md) · [历史层](historical8_assessment.md) · [作者材料层](prepared8_assessment.md) · [既有审阅层](reviewed8_assessment.md) · [来源与重合统计](source_diversity_overlap.md)
