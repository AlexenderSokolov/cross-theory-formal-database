# LL-0002 与 CCC2022.18 的定向范围比较

## 结论

固定作者原文的定向比较支持：GPDOT261014-LL-0002 的完整“弱关系推出全 graded 关系”主张，与已收 CP01A1332F-GA-072 的主定理及其完整源内支撑不同。共享的是 Chevalley 根系、根高度、graded unipotent 子群和 commutator 技术；区别是当前必须在只由受限弱关系呈现的抽象商群中建立全部缺失关系，而 CCC 的生成、normal form 和谱分析在已经满足完整 Steinberg 关系的群中进行。

本结论依据具体数学义务，未以改用 Lean 证明为新增理由。三个当前情形继续合计一题；这里只排除该指定近邻的同一/等价主结果，不作全局净新增或最终无重复声明，不认证作者数学或形式化正确性。

## 固定来源与旧登记

- 旧登记：CP01A1332F-GA-072-Chevalley-high-dimensional-expanders，r001，DOI10.4230/LIPIcs.CCC.2022.18，arXiv2203.03705v1（2022-03-07）
- 作者原题名为 High-Dimensional Expanders from Chevalley Groups，Ryan O'Donnell、Kevin Pratt。旧任务标题 Strongly explicit high-dimensional expanders from Chevalley groups 是描述性标题
- 固定原文：[arXiv v1](https://arxiv.org/abs/2203.03705v1)、[原作者 TeX](https://arxiv.org/src/2203.03705v1)、[官方文章](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2022.18)
- 从作者固定 v1 直接取回的 chevalley_hdx.tex 共1390行，旧登记的主声明678–688与支持块63–677、689–1388吻合。旧 task 与 job-state 两条快照是同一题身份，未算作两项
- 旧成品题包未取得；不需要通过另一成品的转换文本才能识别这里的作者实际范围

## 旧题完整主声明

原 thm:main，TeX678–688，arXiv v1 Theorem3.6、p13，对应官方 Theorem42、18:13。不能把官方42当作v1定理编号。最终作者证明1362–1376，对应v1 pp22–23、官方18:22

背景648及650–676固定有限域F大小p^m、p>3、不可约根系Φ且rank≥2、简单根基及有界次数根元素生成的子群，构造其 coset complex。作者主声明包含全部五项：纯d维且顶点数p^{Θ(m)}的强显式族、独立于m的最大面度界、低维面links连通、(d−2)-face link的p²-regular二部图及λ₂≤√(2/p)、最大面上的简单传递作用。Φ≠G2只出现在谱界项，未被擅自扩大为整条main的共同假设；没有补入作者未显式列出的m下界

## 支撑中最接近的义务

| CCC 作者结果 | 固定v1 TeX位置；版本对应 | 与当前义务的差别 |
| --- | --- | --- |
| 全 Steinberg 呈现、全 commutator formula |492–503 / Def2.23→官方Def24；549–557 / Thm2.27→官方Thm28；566–586 / Prop2.30→官方Prop31| 输入已经施加全部群关系，并未删除为当前Rweak集合 |
| 根生成 |703–705，证明929–937 / Thm3.8→官方Thm44| degree≤1根子群在完整Chevalley群中生成该群；未证明受限弱商向完整群的kernel受控 |
| rank-two degree生成 |767–772，证明773–873 / Lem3.13→官方Lem49| 使用已知全commutator证明完整群内的subgroup membership；不是在弱商内证明缺关系 |
| graded normal form，实质最近邻 |944–946，证明947–976 / Prop3.14，pp17–18→官方Prop50，18:17| 对线性无关Ψ的实际子群XΨ，得degree≤height的有序根元素展开存在且唯一；整理使用全commutator，唯一性援引Prop32/Steinberg Lem17（608–612） |
| 子群交与link结构 |986–993 / Prop3.16→官方Prop52；999–1009 / Thm3.18→官方Thm54| 分析已经定义的实际子群和coset links；未对当前weak presentation给出injectivity/kernel结论 |
| link谱界 |1045–1048，证明1073–1173 / Thm3.23→官方Thm59，18:19–21| 控制图的特征值，不控制弱关系商中全部full relation words的消失 |

完整v1活跃正文63–1388及旧登记全部支持块已纳入此比较。未把“graded”同词当作不同，也未仅凭没有某个关键词判定。最接近的Prop50也没有提供当前特定weak集合的关系删除义务；把其normal form另行扩展成某种呈现证明，属于额外推导，不能当成 CCC 作者已有的这条主张

## 当前精确主张与来源定位

当前固定代码commit e02f0aaba4b045f5c1eadfe9078a3027a3b52d68 的三个 full_relations_implied_by_weak_relations 目标都要求：每个 r∈full*.allRelations 在 weak*.project 下为1。完整full集合含每根linearity、各distinct-root commutator及mixed-degree；weak集合限定codimension-1、lifted和固定definition表达式

- Steinberg.A3：Thm.lean384–444；Ring R；weak定义Defs.lean118，full定义158
- Steinberg.B3Small：Thm.lean518–588；Field F且2≠0；weak定义Defs.lean130，full定义174
- Steinberg.B3Large：Thm.lean572–691；Field F、2≠0且每个元素为两平方和；weak定义Defs.lean298，full定义345

正式 ITP 作者原文亦区分了结果来源：[§2 #S2.p7](https://drops.dagstuhl.de/storage/00lipics/lipics-vol352-itp2025/html/LIPIcs.ITP.2025.9/LIPIcs.ITP.2025.9.html#S2.p7)（9:3）将 CCC[34] 谱扩展与KO[25]/OS[35]呈现/拓扑分析区分；[§3.3](https://drops.dagstuhl.de/storage/00lipics/lipics-vol352-itp2025/html/LIPIcs.ITP.2025.9/LIPIcs.ITP.2025.9.html#S3.SS3)（9:8–9）给出三种弱集合和完整主张；§4给出project(r)=1目标；§5（9:13起）描述逐一建立缺关系的证明义务

全部26个本地当前核心模块、8,276行完整作者代码仍在proof_spans，未删去共享技术或将当前核心改称先修。origin_class仍为human_authored_proof_assistant_transcription。Lean/Lake/kernel均未运行

## 交付边界

整体任务仍为candidate_pending_inflight_dedup，最终全身份范围的无重复结论与计数由主代理填写，并由主代理统一编译。全部邻居原始源、PDF、图片及未知样式许可留.work，不自动进入选定附件

取源辅助缓存自发生成了4个SHA256字段，已向主代理披露；未作准入或复审依据、不入选定交付、不继续该步骤。正文比较及计数判断不依赖哈希
