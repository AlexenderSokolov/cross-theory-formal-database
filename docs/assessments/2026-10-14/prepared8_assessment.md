# Prepared 8题辅助评估

固定仓库：AlexenderSokolov/cross-theory-formal-database
固定commit：41b4ab870b5b24d235c74e7123bccba6d9b9b042

## 范围与证据限制

已实际读取8题作者包的数学命题与连续证明；Poitou–Tate长包已分段读完。只评价难度、重合风险与来源多样性，未修改仓库、生产H、资格或计数；不补作者证明、不认证全部数学正确性，也不外推总体合格率。难度判断依据实际推理义务，不按proof_spans长度、高级术语、论文出处或原H定级。明确给定的前提与必须建立的局部核心分别计算；附有作者解答本身不算给了提示。

统一重合声明：本次深读对象为这8个prepared作者包，未重新读取所有近邻的完整题干及证明，尤其142659和822。涉及近邻的核心复用叙述仅由包内编辑声明及既往审查记录支持，属于需进一步核对的风险，不是本次独立证明的语义重复结论。直接推论、共用支撑引理、换演算而共用证明模板均不自动等同题。行区间不交或标签不同也不足以证明数学信息独立。

## 比较尺度

普通博士qual通常考察第一年研究生基础及重要定理的具体应用；题材超纲本身不构成严格更难。Harvard强调识别、应用重要定理而非高度巧思；UCLA area exams对应研究生核心课程；Wisconsin列出基础课程与逻辑、拓扑等分科范围。这些只是共同尺度的外部锚点，并未用最强学校作为唯一门槛，也没有为每题找到一份等难的实际qual考题。

参考：[Harvard syllabus](https://www.math.harvard.edu/graduate/study-the-qualifying-exam/the-qualifying-exam-syllabus/)、[UCLA handbook](https://ww3.math.ucla.edu/graduate-handbook/)、[Wisconsin](https://www.math.wisc.edu/graduate/current-phd/qualifying-exams/study-strategies/)

描述性汇总：3项明显低于，2项边界，3项有证据高于；最后一组中HoTT的把握较弱。仅针对这8个定向样本。

## 1. 900000403

判断：明显低于；置信度：高

主张：有限个区间平均核的复合保持随机序、保持相对于Lebesgue测度的递减密度，并将原测度向随机序的较大方向移动。

关键难点/常规性与理由：真正论证是单个平均核的保序性、有限复合，以及“递减密度的分布函数为凹函数，凹图像位于弦上方”。题干没有直接把凹性论证给成提示，不能因此说“答案已经给了”；但独立找出并运用这一点仍是标准分析/概率练习，没有可辨识的超qual难点。原始定义还明确说明核在各原子水平区间上平均密度，这降低了所需的构造负担。

证据：[作者包](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/LIT-prob-markov-quantile-monotonicity/r003/package-root-r003/items/L714_author_proof.tex#L177-L189)；[固定原始TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/LIT-prob-markov-quantile-monotonicity/r003/package-root-r003/sources/L714/source-01.tex#L1440-L1533)。作者包177–189为命题及完整证明；固定原始TeX1440–1533含核定义、复合及证明。

重合风险：中等。包内既往审查记载本题与同论文主要Markov化定理主张不同，但它属于该论证中的辅助单调性链；未重新深读该近邻，不能证明解法信息独立或语义重复。

补充限制/异常：来源异常：provenance把作者、作品、网址及许可串成HoTT书。实际TeX及DOI指向Charles Boubel、Nicolas Juillet的JEP论文，官方页与包内licenses/evidence.json均支持CC BY 4.0。作者包TeX第159行author同样写成The Univalent Foundations Program，第160行date许可也写成CC BY-SA 3.0，错配已进入展示页眉，而非仅provenance。应保留正文/DOI、错误页眉、provenance及licenses/evidence.json之间的冲突证据；统计可按已核对实际作品身份归类，但不能悄悄重归类并抹掉冲突。来源统计不能将其并入HoTT书。官方核对：https://jep.centre-mersenne.org/articles/10.5802/jep.177/

## 2. 900000016

判断：有证据高于；置信度：高

主张：建立正特征全局域上二项环面复形的全局、局部限制积与对偶超上同调长正合序列，并明确两处必须使用完成化局部限制积。

关键难点/常规性与理由：即使允许单群有限平坦对偶性、局部环面对偶性和标准同调代数，仍须建立复形的严格拓扑、正特征下可能无限的Kummer项、Tate模控制的可除核、有限D群在缩小开集下的稳定，以及限制积上对偶和极限的正合性。特别是ℓ=p时不能机械套用“全部有限”或交换极限，作者为低次数项另用拓扑群类及完成化处理。额外难点是这些步骤必须彼此兼容，最终确定恰好两处完成化例外，不只是高级术语或长篇幅。

证据：[作者包](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/A-1933-poitou-tate-I/r002/package-root-r002/items/900000016_author_proof.tex#L2440-L2542)；[固定原始TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/A-1933-poitou-tate-I/r002/package-root-r002/sources/900000016/source-01.tex#L2515-L2617)。作者包2440–2462为主命题、2464–2542为收束证明；1545–1671为ℓ-primary对偶与ℓ=p例外，1782–1866为低次完成化配对，2106–2438为稳定、离散像及极限正合性。原始TeX2515–2537为主命题、2539–2617为证明。

重合风险：中等。包内既往审查记载1933的紧支撑对偶作为已证明支撑进入本包；全局限制积、稳定化及完成化连接项是额外结论与工作。未重新读取1933完整题证，不能独立认证两题语义关系。

补充限制/异常：包内有明确适用范围及原文符号读法说明。本次分段读完包内数学文本，但没有重新认证这些修正的数学正确性。

## 3. 900000178

判断：边界，偏常规qual应用侧；置信度：高

主张：用两组Chern类给出六维流形上两种相容正交几乎复结构对应twistor截面的交数公式。

关键难点/常规性与理由：包内明确将twistor上同调环表示、典范截面的Poincaré对偶和x′=x+(c₁−c₁′)/2作为上下文/前提提供。剩余工作是把两个三次类放入同一个商环、相乘并用四次关系及维数约束约化，再配对基本类；有运算和符号控制负担，但没有需要另外发现或建立的spin-c比较构造。因此不能把前提中已经给出的高级几何计入本题独立难度，现有内容不足以支持“严格高于普通qual”。

证据：[作者包](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/DSH-geom-twistor-intersection/r002/package-root-r002/items/L401_author_proof.tex#L99-L176)；[固定原始TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/DSH-geom-twistor-intersection/r002/package-root-r002/sources/L401/source-00.tex#L995-L999)。作者包99–170为前提及上下文，172–173为命题，175–176为完整证明。原始TeX995–999为命题与证明。

重合风险：低至中。既往记录称同源1307计算几乎复结构空间分支的有理最小模型，而本题计算交数；本8题内无近重复。该近邻没有重新深读，因此只报告记录支持的低重合风险，不认证全库唯一。

## 4. 900000163

判断：边界；置信度：中高

主张：假设此前各层是matroid，下一层可加边族不依赖所选最大稀疏集，并满足非空性结论。

关键难点/常规性与理由：不能只读最后一串不等式：包内surplus独立性是须理解/建立的局部核心，其证明先递归分层，再用基交换化到单边替换，找包含新边端点的最小紧集，最后扩张极小化集合使新旧边计数相同。这一交换与极小化集合协调有真实巧思；但两个关键紧集计数引理已作为陈述给定后，整体可与较难组合学研究生习题作推理结构上的类比，尚无很强证据认定稳定地超出普通qual范围。此类比不是已找到实际可比qual试题，也不能用一所学校或某个高阶组合专题的门槛代替普通qual。

证据：[作者包](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-combinatorics-matroid-layer-independence/r001/package-root-r001/items/L304_author_proof.tex#L117-L206)；[固定原始TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-combinatorics-matroid-layer-independence/r001/package-root-r001/sources/L304/source-00.tex#L676-L764)。作者包117–121为目标命题，123–173为surplus局部核心，175–206为目标完整证明；原始TeX676–764覆盖这些块。

重合风险：高优先核对风险。包内编辑说明及既往审查明确记载，局部最有分量的surplus独立性是既有142659的计数主张，本包重用其完整证明；新目标主要由该结果和稀疏性判据推出。这只支持核心复用风险：本次未重新读取142659全题证，不能给出独立语义重复已证结论，也不能把支持引理重用自动判成同题。

补充限制/异常：标题声称“form a matroid”，实际计数命题Matroid_1证明的是选择无关性和非空性，没有在该命题中证明本层augmentation/circuit公理。难度按实际命题，不按标题扩大。

## 5. 900004363

判断：明显低于；置信度：很高

主张：(F⊗O O′)ₓ与Fₓ⊗Oₓ O′ₓ自然相同，作为O′ₓ模。

关键难点/常规性与理由：两个允许前提恰好提供预层张量积的茎计算，以及取茎与层化交换。以“层张量积是预层张量积的层化”连接它们就得到结论，没有额外局部构造或非例行论证。这里不是因作者证明短而判低，而是任务在声明前提下只剩两条标准事实的直接合成。

证据：[作者包](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S7-sh-stalk-tensor-sheaf-modules/r001/package-root-r001/items/L22271_author_proof.tex#L232-L256)；[固定原始TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S7-sh-stalk-tensor-sheaf-modules/r001/package-root-r001/sources/L22271/source-01.tex#L2164-L2182)。作者包232–235为前提，238–251为命题，253–256为完整证明；原始TeX2164–2182为命题与证明。

重合风险：中高核对风险。预层版本加标准层化事实已几乎提供全部解题内容；已有记录主要用区间无交支持身份独立，无法充分评估直接推论型重合。但直接推论不自动等于同题，且本次没有重新读取对应预层近邻全题证，不能作已证重复判定。

## 6. 900000120

判断：有证据高于，保留边界性；置信度：中

主张：在HoTT中构造S²上的纤维化，基点纤维为S¹，总空间等价于S³。

关键难点/常规性与理由：不能只把最后S¹*S¹≃S³的等式链当全题；局部核心包括用univalence在pushout上胶合纤维族、识别总空间为pushout、构造圆的H-space结构并检查loop相容性，以及join结合律的依赖路径一致性。这些是实际保留的解题义务，不能因为附有作者解答就当作免费提示。相对普通qual，连贯完成这些构造有额外非例行负担；但不少步骤在熟悉HoTT基础后属于标准构造，故高于判断不如Poitou–Tate稳固。

证据：[作者包](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/AGP-hott-hopf-fibration/r001/package-root-r001/items/L128_author_proof.tex#L889-L1223)；[固定原始TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/AGP-hott-hopf-fibration/r001/package-root-r001/sources/L128/source-03.tex#L1235-L1555)。作者包889–892为主命题，903–982为pushout构造，998–1072为H-space的Hopf构造，1083–1123为圆乘法及loop相容，1129–1223为join结合律和总空间识别；原始TeX1235–1555为局部构造与证明。

重合风险：中等。与其他HoTT题共享flattening、pushout等基础工具，当前8题内没有同目标；既往dedup记录列举的部分远邻不是最强近邻证据，不能据此排除经典Hopf构造的其他呈现。

补充限制/异常：作者对join逆映射检查及悬挂—join等价留有“直接计算/练习”的压缩说明。本次没有替作者补证明，也不把本报告当证明完整性认证。

## 7. 900003110

判断：明显低于；置信度：很高

主张：对tableau可证性，Γ⊆Δ且Γ⊢A，则Δ⊢A。

关键难点/常规性与理由：允许前提已包含有限前提形式的tableau可证性。原先证明所用有限子集仍然是Δ的有限子集，直接复用同一个tableau即可；没有新归纳、构造或语义完备性步骤。它是定义级练习，不能由“逻辑演算”题材提升难度。

证据：[作者包](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/X2-logic-tableaux-monotonicity/r001/package-root-r001/items/L48044_author_proof.tex#L409-L425)；[固定原始TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/X2-logic-tableaux-monotonicity/r001/package-root-r001/sources/L48044/source-01.tex#L684-L692)。作者包409–412为前提，413–417为命题，419–425为证明；原始TeX684–692为命题与证明。

重合风险：高优先核对风险。有限前提证明系统中的此类弱化往往共享同一个有限子集包含论证，按演算名或章节名区分可能掩盖模板型重合。但换演算并不自动构成同题：本次未逐一读取自然演绎、相继式演算等近邻全题证，不能认证语义重复。

补充限制/异常：作者包419–421与423–425重复装入同一证明；这不是第二个数学结果。

## 8. 900000083

判断：有证据高于；置信度：中高

主张：令Φ(q)=∫₀qφ(s)ds，并用Φ⁻¹对应subordinator的Lévy测度L，得到逆积分时间ρ下ξρ(t)的精确Laplace积分公式。

关键难点/常规性与理由：允许的涨落理论已经提供Φ⁻¹及L，不能把这一现成结果充作新增难点；真正核心是选取变换后的f(t,q)，借随机时钟换元和强Markov性质得到积分恒等式，再建立混合PDE及连续性。还须区分有限活动无漂移时t=0的首跳情形，正确扣除逆指数的漂移项，最后用时间Laplace变换解ODE并反演。每件工具常规，但这一套变换的选择、初值分支和正则性相互制约，构成超出普通qual例行应用的实际证据。

证据：[作者包](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/EXT-822-exact-laplace-inverse-integral/r001/package-root-r001/items/900000083_author_proof.tex#L106-L328)；[固定原始TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/EXT-822-exact-laplace-inverse-integral/r001/package-root-r001/sources/900000083/source-01.tex#L634-L785)。作者包106–112为命题，187–207为时钟换元及强Markov积分，210–280为混合PDE、正则性与两种初值，284–328为ODE、反演及结论；原始TeX634–785为核心证明。

重合风险：中高核对风险。既往包内记录称822计数大时间精细渐近，本题计数更宽条件下的有限时间精确变换，且本精确公式已在822中作为支撑使用。这支持上游核心复用风险；本次没有重新读取822全题证，不能独立认证实际复用比例、语义重复或完全独立。

## 来源多样性

- 按实际作品身份，这8题来自8个不同作品/项目单元：两篇不同JEP论文、SIGMA论文、arXiv论文、Stacks、HoTT书、Open Logic、AHL论文
- 按较粗来源系列，是7类，其中JEP占2项；这仅是样本描述
- 来源多样不等于任务独立：142659→900000163、822→900000083是包内记录支持的核心重用风险；层张量茎和演算单调性有直接推论/模板型重合风险，但均未在本次完成近邻全题证重读，因此不能下独立语义重复已证结论
- 900000403的元数据串源必须单独标出，否则作者、作品和许可三个维度都会错误归并。其官方来源是Boubel–Juillet的JEP.177，与HoTT书不同
- 本报告没有重新做全库语义去重，不把既往dedup结论当作本次独立验证


[评估目录](README.md) · [概览](difficulty_assessment_overview.md) · [历史层](historical8_assessment.md) · [作者材料层](prepared8_assessment.md) · [既有审阅层](reviewed8_assessment.md) · [来源与重合统计](source_diversity_overlap.md)
