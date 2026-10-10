# 既有题目返修：第一轮内容审查

基准：公开提交 `5c133eb3cb70ada8bd3ca187089fe69378e5bc52`，2026-10-10审查。原始 manifest、交付证据、题目TeX、来源和数据库分片均保留；本目录记录编辑判断及实际修订，由当前目录消费。

## 本轮实际完成

- 37条审查记录，涉及36个不同题号：18条内容记录、19条题名记录。题号193008同时有题名修订和内容hold。
- 19条题名修订已按原始TeX实际标题核对；其中11条误抓注释中的`full title`模板，8条误抓未被用于排印的`This is the title`宏，正文center块才是真实标题。
- 14条原先以证明长度支持H3的题目，已逐条阅读声明及完整保留证明，并核对28个statement/proof区段与bundled source0.tex对应行完全一致。每条都有具体机制、剩余义务或不足；这不是14条数学正确性认证。
- 一审曾为3条hold、15条needs_review；9条H3建议的独立二审全部留下具体材料缺口。随后211538实际补齐作者上下文，真实编译和单题门禁、2页视觉检查均通过，本轮判为H2。本轮当前状态为1条本地修订confirmed、3条hold、14条needs_review。没有核准旧题H3。
- 未解决的内容记录保留空确认档位及原标签；211538的H2结论绑定实际修订稿，一审原记录仍保存在`original_review`，二审原意见没有覆盖。未按批次自动降H2。

## 暂停准入的三条

| 题号 | 有据可核的问题 | 原文与交付定位 | 处理 |
|---|---|---|---|
| 100008 | 周期积分公式与下一节的上下界证明错配；该证明直接假定待证公式 | item 26–59；source0 207–247及255–296；已另核arXiv原文第2–3节 | hold。恢复同一计数命题的作者推导后另审难度，不把上下界题替换为修复 |
| 193008 | 所选证明明确标注Solution (GPT-4)，来自本科期末考试示例；作者后续Comment指出第二问错误 | item 25–55；source0 456–490、717；已另核公开arXiv v5附录B | hold。与人类证明来源准入不符；保留原件，不拿同文其他模型答案替代 |
| 211627 | 三维稳定性论证写(1-k)/k大于正数，却声称因此k>4；另需核清一般k到k=5及局部时间范围 | item 283–320，尤其312–314；source0 522–560，尤其551–553 | hold。记录原文问题，不代作者改符号或补证 |

公开复核链接：[100008原论文](https://arxiv.org/html/0801.3487v4)；[193008原论文](https://arxiv.org/html/2601.13209v5)。193008是按作者明确归属判断，不是因为论文研究AI或文字风格像AI而排除。

## 14条长度族逐题处置

| 题号 | 本题具体机制或困难边界 | 第一审处置 |
|---|---|---|
| 211520 | Theta求值矩阵子式、Frobenius行列式微分、非零最高阶系数与互素挠点重排 | H3建议待二审；torsion-jet/Frobenius核心依赖及空间定义待核 |
| 211531 | Catalan比值递推加O(1/r)归纳误差界 | 难度待定；102行不能支持H3 |
| 211533 | 已知Harnack定理的尾项与逆函数单调比较 | 难度待定；不能继承被引用主定理的难度 |
| 211538 | L2回归相位与Denjoy–Koksma导数控制形成矛盾 | 已补齐作者背景；本地修订判H2，[读PDF](revisions/211538-r001/package-root/pdf/211538.pdf) |
| 211543 | 测度弱收敛、边界能量强制性、局部一致收敛与唯一极小点 | 难度待定；存在唯一性已作先修后的剩余义务待校准 |
| 211548 | 振荡Cauchy核近远分解、截止导数与平方分母估计、尺度平衡 | 难度待定；算子、相位和区域定义待核 |
| 211551 | Dirichlet分割交错、Airy外谱计数和内部谱索引控制 | H3建议待二审；奇异算子及边界条件待核 |
| 211560 | 块逆矩阵尾事件夹逼、随机阈值偏移、联合L2误差经条件平均传递 | H3建议待二审；专门尾估计是否承担主要难点待核 |
| 211565 | 速度相关时间分界的振荡积分与多阶加权特征导数bootstrap | H3建议待二审；场范数、权重定义和闭合条件待核 |
| 211577 | 外域Green收缩、加权核迭代、L1算子级极限及多类误差 | H3建议待二审；全局Green等核心依赖及维数范围待核 |
| 211585 | 等型张量分解、展平秩、有限域低次数多项式同时非零 | H3建议待二审；有限底域及矩阵代数分解假设待核 |
| 211589 | Hartree频率/立方体分解、双线性增益与平方和形成可求和尺度 | H3建议待二审；函数空间与专门先修引理待核 |
| 211603 | Lyapunov矩控制、Fisher/熵耗散、降温误差吸收与Gibbs尾速率 | H3建议待二审；矩阵证书和密度逼近核心依赖待核 |
| 211627 | 离散流体/温度能量估计中出现原文符号矛盾 | hold，见上表 |

这些判断按所计命题和剩余证明义务作出；不以题名看起来高深、来自研究论文、证明长或引用闭合作为难度通过条件。二审仍可否决H3建议。

## 正面对照与既有困难例

001（Serre仿射性判据）保留了具体可定位的两段机制：由理想层H1消失构造仿射主开邻域，再以有限覆盖和核层过滤得到全局单位理想。它适合作为“理由必须对应正文机制”的正面对照，本轮没有把旧H2提升为H3。

201599的保留证明只按max更新分两种情形，再用非负权重推出单调性；当前证据不足以维持目标难度承诺。其完整步长假设仍待核，不把这一判断扩展为整篇论文简单或错误。

## 题名修订

下表只确认题名。`review_scope=title`的confirmed不改变内容资格；193008即为“题名确认但内容hold”的明确例子。

| 题号 | 修订题名 | 作者来源标题行 |
|---|---|---|
| 123190 | C*-Algebraic Gauss-Lucas Theorem and C*-Algebraic Sendov's Conjecture | source0.tex 78 |
| 139792 | Functional Donoho-Stark-Elad-Bruckstein-Ricaud-Torrésani Uncertainty Principle | source0.tex 64 |
| 156688 | Nonlinear Heisenberg-Robertson-Schrodinger Uncertainty Principle | source0.tex 64 |
| 169662 | Multi-height analysis of rational points of toric varieties | source0.tex 129 |
| 180374 | p-adic Ghobber-Jaming Uncertainty Principle | source0.tex 65 |
| 186597 | On convergence structures in graphs | source0.tex 109 |
| 187598 | The Nikodym and Grothendieck properties of Boolean algebras and rings related to ideals | source0.tex 243 |
| 187783 | Multi-height distribution of rational points of split toric stacks | source0.tex 159 |
| 191847 | $L^p$ Error Estimates for Numerical Approximation of Convex Hamilton--Jacobi Equations | source0.tex 175 |
| 192281 | Non-Archimedean Brauer Oval (of Cassini) Theorem and Applications | source0.tex 64 |
| 193008 | AI for Mathematics: Progress, Challenges, and Prospects | source0.tex 37 |
| 193491 | Convergence of a two-parameter hyperbolic relaxation system toward the incompressible Navier-Stokes equations | source0.tex 53 |
| 195563 | Non-Archimedean Tarski-Maligranda Inequalities | source0.tex 64 |
| 196360 | The multi-height distribution implies the Batyrev-Manin principle | source0.tex 159 |
| 198525 | Finite Field Tarski-Maligranda Inequalities | source0.tex 64 |
| 201714 | Cohomology of Finite Element Stokes Complexes on Alfeld Splits | source0.tex 154–155 |
| 202426 | $\mathbb{Z}$-Ramsey ultrafilters | source0.tex 51 |
| 203137 | Noncommutative Cauchy Bound and Noncommutative Montel Bound for Roots of Polynomials | source0.tex 64 |
| 209415 | Kähler Einstein manifolds and the Calabi curvature operator | source0.tex 60 |

## 数据使用与验证边界

`reviews.jsonl`以`(problem_id, review_scope)`组合处理，不能用同题最后一行覆盖其他scope。内容资格只由content记录决定；题名修订不晋级。`needs_second_review`表示尚未完成独立第二审，不能作为confirmed输出。

已检查37行JSON均可解析、37个scope键唯一、必需字段与状态合法，124个本地证据路径和行段均实际存在；原发布manifest、delivery-evidence、items、sources和database-parts的Git状态无修改。未重新编译全库，未验证未审题目的数学正确性，未提交或推送。

本轮19条题名和14条难度理由更新是编辑修订成果；100008、193008和211627的hold记录是已定位问题及后续处置边界，不是假称原证明已修复。

## 已完成的实际修订

[211538-r001](revisions/211538-r001/CHANGELOG.md)保留原题面和证明，补作者源1028–1059及四条参考文献。新TeX真实latexmk两遍成功，既有item gate=1/errors=[]；全部2页实际查看通过。主库原件和公开数量不变，当前catalog的`current_item_path`指向本地修订稿，状态明确为待正式合并。

复现新修订的编译与门检：设置包外`REVISION_WORK`后运行`bash curation/revisions/211538-r001/run_compile.sh`。只有要重做源摘录时才用`run_prepare.sh`，不要把准备脚本当只读验证。

## 全库机械定位

本轮扫描了全部14,866条交付记录，发现1,695个区段组合、涉及1,412个题号需要题证配对核对；它们不是1,412个已确认错题。另检出1条明确模型解答标题，已核为193008并hold。清单见[pairing-review.jsonl](pairing-review.jsonl)与[authorship-review.jsonl](authorship-review.jsonl)。
