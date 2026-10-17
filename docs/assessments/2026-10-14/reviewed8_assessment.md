# 已审层8题：只读辅助内容难度评估

固定仓库提交：41b4ab870b5b24d235c74e7123bccba6d9b9b042。没有修改仓库，也没有变更原H标签、计数或正式review。

## 方法与边界

- 通过GitHub连接器读取8份provenance，按item_path读取实际TeX；8题的完整命题与连续主证明均已读到结束，也读取了相关本地核心支撑。191192的完整穿越强度证明和分离几何证明均读完。未做PDF图像视觉核验，不声称逐字原始source0对校。
- 完成主证明分析后再读取content-review作比较；但是provenance和TeX前言本身含原评级/难度理由，定位时已看到，故不能声称完全盲评。判断理由重新落在实际命题及证明步骤上。
- 题库附有证明不意味着题干已给提示。源内必须建立的关键构造/引理计入完整题证单位；仅对明确当作现成先修的外引定理排除其证明贡献。
- 官方qual仅是比较锚点，不能把某校最大纲作为所有普通qual唯一门槛。[Harvard官方大纲](https://www.math.harvard.edu/graduate/study-the-qualifying-exam/the-qualifying-exam-syllabus/)明确强调具体问题与重要定理的识别应用，且范围含表示论、覆盖/纤维化、同调、Sobolev；[Wisconsin官方大纲](https://www.math.wisc.edu/graduate/current-phd/qualifying-exams/topics/)提供另一范围锚点。课程名、文章日期、证明长度均不单独决定难度。
- 此处“有证据高于”只表示有具体非例行步骤支持辅助判断，并非正式准入或人类审核；“边界”不等于不合格，也不等于明显低于。材料质量与难度分开。
- INDEX因文件较大，GitHub fetch_file返回空内容；manifest约74.9MB未整读。provenance直接给出精确TeX位置，故目录读取边界不构成数学命题/证明读取缺口。父任务另行交叉核对清单与路径。
- 原review提到的全库近邻未在本次重新逐题读取；只能给本8题内的重合观察、各题支撑重复风险及原review的待复查近邻，不声称全库完成语义去重。

## 汇总

- 有证据高于：191192、190548、191078、187527
- 边界：191190、188412、182976、194851
- 没有把任何题判为“明显低于”；8题均取得完整题干与连续主证明，无需因读取失败标“不足以判断”
- 这是本层8个样本的辅助分布，不能外推整库准入率

## 来源多样性与重合

8题来自8个不同arXiv源标识、不同命题，无本样本内同源多拆题。数学对象涵盖多胞形、随机几何、magma恒等式、图/关联系统、度量群作用、拓扑不变量、加性密度、统计误差，实际构造机制有差异。共同方法有有限/递增构造、局部条件保持，但不足以认定语义重复。 依赖或支撑相同也不自动等于主张语义重复；是否存在重复计数问题，须核对独立命题、完整题证及各自新增的实质证明义务，只有缺乏独立新增证明任务时才有此风险。

来源渠道却非常集中：全部为arXiv原生作者TeX，7个编号属于2025年8–12月，另1个为2026年2月；“8个不同文章”不等于来源渠道、年代和文献类型已充分多样。作者归属依provenance，未扩大为AI-free判断，亦未做作者网络独立性审计。

最需注意的两处条件：
1. 191190本地FAP继承证明已计入评估；mix定理是明确外引输入。即使计入FAP，其超qual强度仍有边界，不是简单删掉核心后降级
2. 194851下界模型和参数校准已在命题明示；不能将它们的全部发现负担算入解题困难。其上界阈值及同一事件控制仍计入


## 191190 — 边界（置信度：中等）

**实际命题：** 任意给定 d≥3 和 n₃,…,n_d≥5，构造具有指定环面型三维截面、精确2幂群阶及多重FAP性质的有限正则d-多胞形。

**核心困难：** 设计可沿秩继续的共同二维截面拼合，并建立正规闭包的继承等式 N⁻_{k+l+1}=N⁻_k·N̂；仅控制群阶不足以闭合归纳。

**先修与直接套用的区别：** 群的同构定理、正规闭包、半直积及归纳属于常规先修。McMullen–Schulte的mix定理在包内明确作为外引定理（199–217）给出，不应计其整套存在性/交性质证明；133–179的source-local FAP继承证明则必须计入，不能因保留为support就当作提示。

**具体理由：** 计入FAP继承后，完整任务需要选择共同截面、建立相容的正规闭包分解，并保留能沿任意秩继续的归纳不变量。继承论证使用标准同构定理，并不能据此直接决定整体构造的难度；明确外引的mix定理可作先修，但源内FAP机制及完整构造的发现负担仍须计入。目前缺少同型实际资格考题作为难度锚点，故保持中等置信的边界判断；尚未稳断严格高于，不等于已经证明它等同于常规qual。

**原review比对：** 原H2理由识别了正确的继承与构造义务；独立完整重读后保留边界中等置信。标准工具的使用不抹去整体构造负担；因缺同型实考锚点，不将“尚未证明高于”改写为“已经证明常规”。 原H2仅为原记录。

**重合/支撑风险：** 辅助FAP、环面分类与mix与本题存在依赖关系；若另列为题，须核对独立命题、完整题证及各自新增的实质证明义务，只有缺乏独立新增证明任务时才有重复计数风险。与188412同属群作用/组合结构构造，但命题和证明机制不同。review列197572、1474为近邻，我未重读这两个近邻，不能重申全库去重已验证，也不能否定其资格。

**来源：** Gabe Cunningham, Yan-Quan Feng, Dong-Dong Hou, Egon Schulte，Symmetric polytopes whose automorphism groups are 2-groups，[固定版本](https://arxiv.org/abs/2512.15511v1)

**确切TeX：** [命题265–273行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/191190_author_proof.tex#L265-L273)；[连续主证明275–330行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/191190_author_proof.tex#L275-L330)；核心支撑行：117–179；182–249。原源命题354–362；主证明364–419；本地继承156–263及mix/环面上下文至349。数字以当前独立包装TeX为主；source0范围来自包装/provenance记录。

[既有content-review](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/sources/191190/content-review.json)

## 191192 — 有证据高于（置信度：较高）

**实际命题：** 双曲半平面的Poisson长度L棒模型中，对任意p&lt;1，强度λ≥C(p)L⁻²且L充分大时，接于初始棒的无界簇概率大于p；另给显式充分常数。

**核心困难：** 把交点/角度/中心偏移参数的强度与递归分离半平面结合，使自适应探索的两子代始终位于尚未查询且互不相交的区域。

**先修与直接套用的区别：** Poisson映射/限制与不交集合独立性、Galton–Watson存活、双曲正弦/余弦定理是可引用先修。穿越强度推导341–776和分离几何918–995是本地实证核心，不因其在support就排除；分枝过程定理本身不能替代这些构造。

**具体理由：** 难点不是算出2q&gt;1，而是建立每一代条件于历史后仍有同一q的合法探索机制，几何嵌套和分离正用于此。强度坐标推导还需双侧小区间估计，不能靠欧氏直觉直接替代；二者合起来才产生L⁻²尺度并把存活概率推到任意p。这是比常规“识别一个已知定理并应用”更强的构造链，支持严格高于的辅助判断。

**原review比对：** 与原H2指出的核心义务一致，但辅助判断不沿用H编号，也不以99行长度作证据。 原H2仅为原记录。

**重合/支撑风险：** 强度lemma和half-plane lemma在本包中支撑主命题；若另列为独立题，需核对其独立命题、完整证明及新增证明任务，不能仅因支撑关系判重复，只有缺乏独立新增证明任务时才有重复计数风险。源中反向区间、主证明开头倒数常数的已注明问题影响可读性/质量，不作为降低难度的证据；判断以命题与末尾q计算一致的阈值为准。review列191475作近邻，我未复查该题，不据此否定其资格。

**来源：** Erik I. Broman, Johan H. Tykesson，The Poisson stick model in hyperbolic space，[固定版本](https://arxiv.org/abs/2512.15529v1)

**确切TeX：** [命题799–807行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/191192_author_proof.tex#L799-L807)；[连续主证明997–1095行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/191192_author_proof.tex#L997-L1095)；核心支撑行：333–776；809–995。原源命题1411–1419；主证明1614–1712；强度与定义620–1192；分离上下文1425–1611。数字以当前独立包装TeX为主；source0范围来自包装/provenance记录。

[既有content-review](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/sources/191192/content-review.json)

## 190548 — 有证据高于（置信度：中等）

**实际命题：** 构造满足 x=y◇(y◇(x◇y))（E73）却不满足x◇(x◇x)=(x◇x)◇x（E4380）的magma。

**核心困难：** 自己找出可延拓且不崩溃的部分运算不变量：右平移单射，以及额外排除x◇y=y，再用新元素处理被迫定义并保留反例种子。

**先修与直接套用的区别：** 可数枚举、有限部分运算的递增并及基本逻辑足够理解。抽象greedy扩张定理54–68给出标准完成框架，但未替题目选择可兼容的规则集；79–103的规则选择和四种新规则情形必须算完整解题贡献。

**具体理由：** 题干只给两条恒等式，没有给三条扩张不变量或四元种子；不能因为答案短就把寻找这些对象视为已提示。尤其第三条不是E73的逻辑后果，而是为排除延拓碰撞而主动加强的条件，这比通常代入恒等式或调用模型存在定理多出实质设计负担。所有工具很初等，但设计一个能无限完成的反模型有超过常规qual的具体证据；置信度仅中等，因为对熟悉free/greedy构造的专题训练者可能是一道短高阶习题。

**原review比对：** 原H2所述碰撞规避确在实证中，辅助支持来自不变量发现而非论文声望、ATP/Lean使用或源长度。 原H2仅为原记录。

**重合/支撑风险：** 一般greedy定理在本包中为具体E73反例提供框架；若二者另列为题，应核对各自独立命题、完整题证与新增实质证明义务，只有缺乏独立新增证明任务时才有重复计数风险。与187527都属反例构造但结构不同，未见两题之间的同义/包含关系。review列134512、197537、210884、211339；我未重读近邻，故没有全库无重复结论，也不能否定这些近邻的资格。

**来源：** Matthew Bolan, Joachim Breitner, Jose Brox, Nicholas Carlini, Mario Carneiro, Floris van Doorn, Martin Dvorak, Andr\'es Goens, Aaron Hill, Harald Husum, Hern\'an Ibarra Mejia, Zoltan A. Kocsis, Bruno Le Floch, Amir Livne Bar-on, Lorenzo Luccioli, Douglas McNeil, Alex Meiburg, Pietro Monticone, Pace P. Nielsen, Emmanuel Osalotioman Osazuwa, Giovanni Paolini, Marco Petracci, Bernhard Reinke, David Renshaw, Marcus Rossel, Cody Roux, J\'er\'emy Scanvic, Shreyas Srinivas, Anand Rao Tadipatri, Terence Tao, Vlad Tsyrklevich, Fernando Vaquerizo-Villar, Daniel Weber, Fan Zheng，The Equational Theories Project: Advancing Collaborative Mathematical Research at Scale，[固定版本](https://arxiv.org/abs/2512.07087v2)

**确切TeX：** [命题76–77行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/190548_author_proof.tex#L76-L77)；[连续主证明79–103行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/190548_author_proof.tex#L79-L103)；核心支撑行：45–73。原源命题784–785；连续主证明787–811；greedy框架749–772。数字以当前独立包装TeX为主；source0范围来自包装/provenance记录。

[既有content-review](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/sources/190548/content-review.json)

## 188412 — 边界（置信度：中等）

**实际命题：** 把任一有限关联系统改造成所有旗秩≤2、所有元素度≥2的有限系统，同时保持全correlation群及保类型子群这一对群。

**核心困难：** 设计边细分加射线/尾部图装置，通过两种新颜色类的不同且足够大的基数使旧顶点可识别，再证明限制无核、原自同构唯一延拓。

**先修与直接套用的区别：** 有限图、自同构、着色、群同态核是基础先修；没有现成实现定理直接给出结论。装置75–89的设计也没有在题干中给出，必须计入发现负担；图示占行不应计为数学复杂度。

**具体理由：** 本题有真实装置设计：兼顾无三角形、提高小度数并消去多余对称，不能当作纯定理引用。另一方面，装置给出的数学机制集中于颜色类基数可识别与固定根的局部刚性，随后限制/延拓论证都是典型图自同构编码方法；从实际证明尚难稳断严格高于较强资格考的构造题。保留边界并不说构造已被题干提示，而是承认该发现负担与高级组合习题的分界不清。

**原review比对：** 同意原H2定位的刚性与延拓义务；对从这种义务上推“严格超qual”保持保留。 原H2仅为原记录。

**重合/支撑风险：** 装置构造与保持两个群的论证在当前包中服务同一结论；若另列为题，需核对独立命题、完整题证及各自新增实质证明任务，只有缺乏独立新增证明任务才有重复计数风险。注释/TikZ行数本身不构成数学困难。与191190共享自同构群主题但不是同一结论。review列174743、994、198387为近邻；未独立复查，不据此否定其资格。

**来源：** Antonio D\'iaz Ramos, R\'emi Molinier, Antonio Viruel，Every finite group is represented by a finite incidence geometry，[固定版本](https://arxiv.org/abs/2511.02410v2)

**确切TeX：** [命题60–62行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/188412_author_proof.tex#L60-L62)；[连续主证明64–206行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/188412_author_proof.tex#L64-L206)；核心支撑行：73–89；175–194。原源命题440–442；连续主证明443–585（含TikZ与注释）；定义181–203。数字以当前独立包装TeX为主；source0范围来自包装/provenance记录。

[既有content-review](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/sources/188412/content-review.json)

## 191078 — 有证据高于（置信度：中等偏高）

**实际命题：** 剩余有限群在任意度量空间的等距作用，其任意有限点集、有限群元素和给定误差上的轨道距离，可由一个有限度量G-空间一致逼近。

**核心困难：** 有限商会产生新短路，须先加ε离散度量使每条非平凡边有统一正下界，以此预先界定所有潜在短路词长，再选对此词球单射的有限商并把短路提升回原空间。

**先修与直接套用的区别：** 剩余有限性对有限集的分离、路径度量、等距作用和三角不等式是基础。没有引用一个现成有限作用逼近定理完成关键步骤；正文38–190亲自建立扰动—词长界—商单射—无短路这一链条。

**具体理由：** 单纯把有限轨道数据送入有限群商无法控制距离，证明需要一个反向依赖设计：先用ε扰动控制将来商上短路的长度，再据此选商。该选择还要同时覆盖多个起点与轨道、保证权重和等距作用一致，随后才能用提升路径的三角不等式闭合。这是可明确指出的非例行构造，支持严格高于常规qual；不据原H3声称更高强度等级。

**原review比对：** 原H3理由中的无短路机制确实由作者主证明承担；本评估只给辅助超qual证据，不认证H3。 原H3仅为原记录。

**重合/支撑风险：** 证明明确受Doucha工作启发，技术祖先重合需与完全同题分开；原review指Proposition3.9的有限赋范群近似为相关先例，此次未独立读该外文原文。采用同一无短路机制的群特例/推论是否有独立贡献，须核对各自命题、完整题证及新增实质证明任务；只有缺乏独立新增证明任务时才有重复计数风险，不能仅凭方法相同否定资格。与本8项其余命题未见直接重合。

**来源：** Vadim Alekseev, Andreas Thom，On finite local approximations of isometric actions of residually finite groups，[固定版本](https://arxiv.org/abs/2512.14147v1)

**确切TeX：** [命题30–36行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/191078_author_proof.tex#L30-L36)；[连续主证明38–190行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/191078_author_proof.tex#L38-L190)；核心支撑行：53–73；91–177。原源命题66–72；连续主证明96–248；定义/启发来源92–94。数字以当前独立包装TeX为主；source0范围来自包装/provenance记录。

[既有content-review](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/sources/191078/content-review.json)

## 182976 — 边界（置信度：中等）

**实际命题：** 对覆盖p:Y→X，证明分布范畴不等式 dcat(X)≤(dcat₁(X)+1)(dcat(Y)+1)−1。

**核心困难：** 正确区分复合覆盖p∘qY的纤维与qY的纤维，把普遍覆盖上的有限支撑截面投影至p的纤维，再混合Y上的路径分布以获得X上的截面。

**先修与直接套用的区别：** 覆盖/路径提升、普遍覆盖同构、纤维化的截面、自然性在研究生拓扑训练范围内；这里原文为Hurewicz fibration，并不预设局部平凡纤维丛。156–214的源内提升论证计入完整内容，正确选择复合覆盖的分布空间和构造所需截面也计入发现负担；有限支撑分布的自然性是给定背景，主结论并未被引用。

**具体理由：** 完整构造必须先选对复合覆盖p∘qY的分布空间：支撑点可在不同qY纤维中，但须在复合覆盖下同纤维；随后还要组织提升、投影和路径分布混合以得到真正所需的截面。这一空间选择及截面构造不能压缩成事后核对纤维，末尾(n+1)(r+1)支持数虽为直接乘法，也不消除前面发现构造的负担。现缺同型实际资格考题作难度锚点，故保留边界并降为中等置信；尚未稳断严格高于不等于已经证明是常规qual题。

**原review比对：** 与原H2对复合覆盖分布空间和截面构造的观察一致；独立完整重读后，更明确计入这些源内发现负担。边界置信度调整为中等，因为缺同型实考锚点，不能从支持数乘法直接推断整体常规。 原H2仅为原记录。

**重合/支撑风险：** 自然性、pullback和覆盖提升在本包中属于共享先修/支撑；若另列为题，应核对独立命题、完整题证及新增实质证明义务，只有缺乏独立新增证明任务时才有重复计数风险。review列185405作为同类不变量近邻，尚未独立对读，不能否定其资格；本次只能说本8项内未见重复。

**来源：** Ekansh Jauhari, John Oprea，On distributional one-category, \\ diagonal distributional complexity, \\ and related invariants，[固定版本](https://arxiv.org/abs/2508.06973v2)

**确切TeX：** [命题217–222行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/182976_author_proof.tex#L217-L222)；[连续主证明224–275行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/182976_author_proof.tex#L224-L275)；核心支撑行：81–135；156–214。原源命题1827–1832；连续主证明1833–1884；覆盖提升798–861及分布定义409–580。数字以当前独立包装TeX为主；source0范围来自包装/provenance记录。

[既有content-review](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/sources/182976/content-review.json)

## 187527 — 有证据高于（置信度：中等）

**实际命题：** 任意ε&gt;0可构造上Banach密度&gt;1−ε的自然数集A，却排除一切嵌套无限B_i、任意起始长度k_i与平移t_i组成的长度窗口[k_i,k_i+i]有限和配置。

**核心困难：** 选择稀疏素数模的删除族，同时处理任意平移与无界长度窗口；利用早期平移排掉零剩余类，再用后期长窗口扫遍同一个素数模的非零类。

**先修与直接套用的区别：** 素数、鸽巢原理、循环群以及基本密度估计是初等先修；不需要把Hindman定理当工具。删去哪些类、怎样关联早期和后期指标均未由题干给定，整段构造52–76必须计入发现负担。

**具体理由：** 这不是一个固定模数的有限和计算：同一A须击败任意嵌套系统和任意自然数平移，还要保留任意接近1的密度。证明的两尺度选择把未知的早期平移嵌入素数删除宽度，并让较晚窗口覆盖全部模类，嵌套性正是连接两次矛盾的必要环节。工具初等却需要定制的统一反例设计，足以给出超常规qual的中等置信证据；短证明和初等语言均不应自动降级。

**原review比对：** 原H2说的跨尺度障碍在实际证明中成立；本辅助判断靠量词统一性与构造选择，不靠原H2。 原H2仅为原记录。

**重合/支撑风险：** 零类/非零类在当前证明中是同一反例的两种情形；若相关结论另列为题，仍须核对独立命题、完整题证与各自新增实质证明任务，只有缺乏独立新增证明任务时才有重复计数风险。与190548都以强化局部约束建反例，但对象、量词结构和技术没有直接包含。review近邻202246、205630未在本次复查，不据此否定其资格。

**来源：** Felipe Hern\'andez, Ioannis Kousek, Trist\'an Radi\'c，On density analogs of Hindman's finite sums theorem，[固定版本](https://arxiv.org/abs/2510.18788v1)

**确切TeX：** [命题47–50行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/187527_author_proof.tex#L47-L50)；[连续主证明52–76行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/187527_author_proof.tex#L52-L76)；核心支撑行：主证明内。原源命题438–441；连续主证明460–484；自然数约定401–402及密度264–266。数字以当前独立包装TeX为主；source0范围来自包装/provenance记录。

[既有content-review](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/sources/187527/content-review.json)

## 194851 — 边界（置信度：中等）

**实际命题：** 两模型等先验Bayesian averaging的KL误差，以概率≥1−δ有min{10log²(2/δ)/n,5log(2/δ)}上界，并在题干指定的Bernoulli/点质量模型下给出同阶概率δ下界。

**核心困难：** 建立源内平方根似然比矩估计，再按真实Hellinger间隔分近远两支；远支选择后验错误权重阈值，使间隔在KL估计中抵消，并保证同一事件同时控制密度比。

**先修与直接套用的区别：** Markov、独立乘积期望、凸性及指数估计是常规概率工具，但其使用不能代替本题构造。仅KL–Hellinger比较明确作为现成专项先修；源内77–117的平方根似然比矩估计与完整lemma证明，以及主证明的近远分支、阈值和同事件控制，均计入完整题证单位。下界模型与(1−p)^n=δ已在命题给出，不把发现整个反例算作解题者任务；被排除的比较辅助原证明也不算成本题贡献。

**具体理由：** 上界的完整负担包括77–117的平方根似然比矩估计，以及主证明中近远分支、使Hellinger间隔抵消的阈值选择和同一事件控制；它不是在给定整套浓缩结论后仅做代入。下界模型与概率校准关系确已在题干明示，因此这一发现负担较小，但仍须完成指定模型上的事件分析及两尺度估计。独立完整重读后保持边界、置信度降为中等：缺少同型实际资格考题作锚点，尚未稳断严格高于不等于已经证明常规，也不以辅助证明质量问题扣成简单。

**原review比对：** 原H2指出的上界残余有实证支持，平方根似然比矩估计及其源内证明也应计入完整负担；“下界独立设计Bernoulli模型”则会夸大题干未给定的任务。独立完整重读后保留边界中等置信，并明确缺同型实考锚点。 原H2仅为原记录。

**重合/支撑风险：** 本包的上/下界共同构成锐阶断言；若分别列为题，须核对各自独立命题、完整题证与新增实质证明任务，只有缺乏独立新增证明任务时才有重复计数风险，且拆分不增加原始来源数量。review列1568、197148、874，此次未对读，不能否定其资格。KL–Hellinger比较在本题明确作为共享标准输入，其证明不计入本题难度；这不预断它另成独立题时的难度或资格。

**来源：** Spencer Compton; Gábor Lugosi; Jaouad Mourtada; Jian Qian; Nikita Zhivotovskiy，Ratio Covers of Convex Sets and Optimal Mixture Density Estimation，[固定版本](https://arxiv.org/abs/2602.16142v2)

**确切TeX：** [命题120–135行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/194851_author_proof.tex#L120-L135)；[连续主证明137–259行](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/items/194851_author_proof.tex#L137-L259)；核心支撑行：40–75；77–117。原源命题1714–1729；连续主证明1731–1853；似然lemma470–525；比较387–395。数字以当前独立包装TeX为主；source0范围来自包装/provenance记录。

[既有content-review](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/sources/194851/content-review.json)


[评估目录](README.md) · [概览](difficulty_assessment_overview.md) · [历史层](historical8_assessment.md) · [作者材料层](prepared8_assessment.md) · [既有审阅层](reviewed8_assessment.md) · [来源与重合统计](source_diversity_overlap.md)
