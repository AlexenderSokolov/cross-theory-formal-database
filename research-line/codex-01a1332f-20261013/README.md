# 第三条Codex主机收题产线

## 当前交付与接续入口

[第八批完整成品：25道](delivery/batch-008/INDEX.md)，已上传并核实提交`10da27bf3fa902086f064bda624ae0a26c4c9263`。本线累计199道净新增可用材料已上传。第九批已在Yupeng编译并入库25道，待上传；正式生产主库增量仍为0。上传确认读取各批UPLOADED.json，现场进度读取STATUS.json。

第九批接续范围：通信CCC2020.12/arxiv1910.01251/ECCC TR19-140（CC078/079起）；几何CCC2020.11/ECCC TR20-014（GA099起，旧TR19-147撤回novelty claim只作版本历史，不用旧稿代当前正式proof）；数论CCC2020.8/arxiv2003.05152/期刊10.1017/fms.2022.100（NT068，按原声明配齐完整结构续证并逐项保留两许可）。当前21题SQLite有效条目、ITEMS与SELECTION一致，与199道上传清单无任务重叠。GA098的原打印参数疑点保留在task.source_rendering_notes，未自行数学修订；GA097保留作者density/padding说明。Goal active，三个GPT-6.1 Sol / medium代理只写各自lane，根负责jobs/编译/数据库/上传；全Yupeng生产、完整30000目标不变。

几何组完成CCC2021.22后下一独占CCC2021.23/arxiv2105.07517/doi10.48550/arXiv.2105.07517（coloring SoS lower bound，GA090起）。完整旧库、准备记录及两线实际身份零命中；保留原multiple-color-class模型，主下界与承重归约合题，不把unique-color-class开放问题补成结论。

数论组完成CCC2021.27后下一独占CCC2021.28/arxiv2011.09823/doi10.48550/arXiv.2011.09823（quantum minimum cut，NT063起）。完整旧库、准备记录及两线实际身份零命中；保留matrix/array与权重参数模型，上界同主题合题，独立下界仅按实际完整H2主证选取。

通信组CC065/066完成后下一独占CCC2021.24/arxiv2106.00287/doi10.48550/arXiv.2106.00287/ECCC TR21-004（junta-distance tolerant testing，CC067起）。完整旧库、准备记录及两线实际身份零命中；保留relaxed/nonrelaxed模型和参数，同主题与承重证明合题，不拆算法支撑与参数变体。

几何组GA090完成后下一独占CCC2021.29/arxiv2002.11594/doi10.48550/arXiv.2002.11594（highest-weight-vector evaluation，GA091起）。完整旧库、准备记录及两线实际身份零命中；保留编码、field与条件性假设，算法同主题合题，只有独立完整主证明的硬度或结构结果另取，不拆参数/支撑。

通信组CC067完成后下一独占CCC2021.30/arxiv2012.03415/doi10.48550/arXiv.2012.03415（adversary-bound query-to-communication lifting，CC068起）。完整旧库、准备记录及两线实际身份零命中；保留constant gadget/partial function/round/条件性隐私假设，只按实际独立完整主机制选题。

数论组NT063/064完成后下一独占CCC2021.31/ECCC TR21-030（constant-round communication hardness，NT065起）。完整旧库、准备记录及两线实际身份零命中；保留totalBoolean矩阵输入和round/approximation模型，同主题完整证明与承重round elimination合题，不拆支撑。

下方为来源分配和交付的历史记录，旧阶段计数不代表当前进度。

用户明确硬约束（2026-10-13）：禁止在本机编译。所有正文编译、最小文档测试、装配、提取和SQLite生产均只在Yupeng主机执行；本机仅SSH控制、GitHub认证中转及查看主机已生成成品。

统一准则见../../PROJECT.md。作者承担数学责任；执行者只负责完整取材、配对、必要上下文、用途难度、针对性去重、编译和交付。禁止重证、补证明、加假设、审稿、强制双审、内容哈希、逐字节核对、会话日志工程或跨机器重放。

全部生产在Yupeng。根代理独占jobs、SQLite、索引和上传；三个GPT-6.1 Sol / medium材料代理只写各自lane。

| lane | task prefix | 首轮独占来源 |
|---|---|---|
|communication-complexity|CP01A1332F-CC-|doi:10.4230/LIPIcs.CCC.2024.13|
|geometry-algorithms|CP01A1332F-GA-|doi:10.4230/LIPIcs.CCC.2024.14|
|number-theory|CP01A1332F-NT-|doi:10.4230/LIPIcs.CCC.2024.25|

不拆直接推论或支撑小引理凑数。具体新来源由根代理按DOI分配。约25道净新增交付后继续。准备分支上传不计为生产主库增量。保留原件和既有成品，不批量删除。

## 后续来源分工

通信组独占CCC2024.7、CCC2024.3；几何算法组独占CCC2024.24、CCC2024.4；数论组独占CCC2024.1。CCC2024.29缺完整可编辑作者证明路线，原件保留、不计新增。具体任务标签用于界定计数，支撑上下文不拆数。

## 已上传成果

[batch-001：25道净新增成品](delivery/batch-001/INDEX.md)，提交`170c9993c1b4774037a0273d082bd8336ecaa993`。全部在Yupeng取材、编译和SQLite建库，本地只认证中转。生产主库公开增量0，继续第二批。

## 新来源分工与缺口

通信组独占CCC2024.11与CCC2024.9对应完整期刊DOI10.1007/s00037-025-00276-5；数论组独占CCC2024.31及CCC2024.5；几何算法组独占CCC2024.2。CCC2024.10完整证明许可不足，保留缓存不计新增。

[batch-002：25道净新增成品](delivery/batch-002/INDEX.md)，提交`36b79fd8979690e6c98ae8f6a6da2bea5c76d552`，累计上传50道，继续第三批。

## 沿用现有逐项许可口径

仓库根README第56行明确存量含GNU FDL及非商业许可，不能把整库当统一CC BY语料。本线同样逐题保留实际许可；不新增只能CC BY的限制。BY-SA整理稿保留BY-SA，适用于本项目非商业研究交付的BY-NC-SA材料保留NC/SA条件，不能改标CC BY。ND材料不得把受限改编稿公开；非独占分发授权本身也不当作第三方重排许可。题证/原件/SQLite按各自license记录使用。

[batch-003：25道净新增成品](delivery/batch-003/INDEX.md)，提交`8f5e1c40b6da83df4c014b38bea76825df41dc0d`，累计上传75道净新增。数据库另保留1条与第二线同题的非计数记录，默认ITEMS不包含它。继续第四批。

## 当前跨线避让

第二线已占CCC2025.8、2025.9、2025.16；本线不在这些论文取材。arxiv2402.10351量子Frege/LWE主结论也已有第二线在途，本线保留原材料但不计新增，见delivery/EXCLUDED.json。

第四批刷新：第二线batch-010现已使用CCC2025.10/.11/.19；本线GA043与其Theorem15同题，CC023/GA044/NT025按获批同源争用避让规则退出新增计数，并不声称三个不同主张数学等同。四份完整材料和数据库历史保留，记录见delivery/EXCLUDED.json及batch-004/RETAINED_DUPLICATES.jsonl。新独占块：通信CCC2025.4/.5；几何算法CCC2025.13/.14；数论CCC2025.1/.2，三代理分别只写本lane。

第四批当前18道已实际编译并存入SQLite，尚未上传；4份同题/同源争用记录保留不计新增。NT026–028排版r003重新编译，NT026曾剪裁的第14页公式已实际预览确认完整显示。继续补齐约25道交付节点，累计已核实上传仍75道。

## 避免继续同源争用：CCC2023独占块

最新刷新第二线batch-011/在途还使用CCC2025.12/.13/.18/.20，本线当前未上传的同源11份材料退出新增计数，原件和SQLite历史保留；此前先上传的75份不追溯删改。用户已明确授权一次跨会话来源协调，现已向第一/第二会话各成功发送一次，包含本线75份已上传入口、当前来源分工和争用避让；仅协调，不修改它们的文件/队列/配置。

新独占来源（均已对完整旧库+准备+两线查零同源）：communication-complexity负责CCC2023.4/.5（先完成已在做的CCC2025.4/.5）；geometry-algorithms负责CCC2023.13/.14；number-theory负责CCC2023.25/.26。完整DOI统一为10.4230/LIPIcs.CCC.年份.编号。仍按原规则，不拆直接后果或支撑小引理。

下一精确来源块已查零同源后分配：通信CCC2023.6/.7（CC030起）、几何算法CCC2023.15/.16（GA057起）、数论CCC2023.27/.28（完成2023.26后）。其他产线可读取本记录避免争用。

跨线协调已实际落实：第二线delivery/EXCLUDED.json明确将其sparse-abelian-cayley-expanders与johnson-complex-coboundary-expansion两项（CCC2025.7）让给本线，不计其新增；本线继续交付GA041/042。后续数论独占CCC2023.29/.30（NT037起），已查零同源。

第四批最终别名刷新：CCC2025.4在第二线早期batch-002以arxiv2501.09545身份交付，CCC2025.3在batch-011交付；本线CC024/025和NT021/022因此退出本批新增，保留原件和历史。第四批非计数历史合计19份；实际25份选择清单与SQLite有效状态一致后再提交。

[batch-004：25道净新增成品](delivery/batch-004/INDEX.md)，提交`1b22539899c312d0abefac785641b6ee30f396dd`，远端分支已核实指向该提交，累计上传100道净新增；本批另保留19份不计新增历史。第五批实际编译已启动，继续生产。

第五批当前13道已实际编译并存入SQLite，尚未上传，与前四批100道无任务重复。其余ready材料继续装配。

## 第五批接续来源

当前已查零同源后分配CCC2022.4/.5给通信组（完成CCC2023.7后），CCC2022.13/.14给几何算法组（完成CCC2023.15的有完整作者证明子项后），CCC2022.25/.26给数论组。各实际arxiv/ECCC/期刊别名先报根做完整身份刷新，再大量整理。所有其他产线可只读本分工，原目录与写权限边界不变。

CCC2022来源实际别名刷新已完成：通信2201.10997/2111.02999、几何ECCC TR22-033/TR22-028（撤销不同作品的2202.08688）、数论两完整题名及旧opus16587/16588均无命中。第五批当前19题已编译入库，仍未上传。禁止本机编译硬约束继续。

下一精确DOI占用：通信CCC2022.8/.9（CC040起），数论CCC2022.27/.28（完成2022.26后）。完整旧库+准备+两线已查DOI零同源，实际arxiv/ECCC/期刊别名仍先刷新后生产。第五批25份均已编译入库，NT044元数据换行r002正在主机收尾。

[batch-005：25道净新增成品](delivery/batch-005/INDEX.md)，提交`3149adf80953019c4cf9b6ab3f2bc29ab466db6a`，远端分支与GitHub入口均已核实，累计上传125道净新增。第五批无跨线同源命中；禁止本机编译规则已随PROJECT/README发布。继续第六批。

第六批当前5题已实际编译入库，未上传，与前五批125份上传清单不重叠。MCSP/NT040/NT044本轮呈现修复均仅在Yupeng；继续当前CCC2022精确来源分工。

持久目标已回读恢复active，继续原30000总目标；第六批当前10份主机编译入库。通信下一独占CCC2022.10/.11（CC044起）已查DOI零同源，实际别名先刷新。所有本机编译仍禁止。

通信后续精确DOI已查零命中后分配CCC2022.12/CCC2021.4，避开几何已占2022.13–16；所有实际作品别名先刷新。第六批当前11份主机编译入库，仍未上传。

下一分工实际别名刷新：几何CCC2022.17=ECCC TR22-023，.18=arxiv2203.03705，均零同源；数论CCC2022.29完整题名零命中且正式页无Related Versions，.30=ECCC TR20-165零命中，正式元数据主机缓存可复用。通信下一CCC2021.5/.6已查DOI零同源。所有生产继续仅Yupeng。

下一几何独占来源CCC2022.19/.20已查DOI零同源，GA073起；通信CCC2021.5/.6等实际别名后生产。共享主Goal由用户/根控制，子源缺口仅汇报。第六批当前23道主机编译入库。

[batch-006：实际24道净新增成品](delivery/batch-006/INDEX.md)，提交`a1f5eca853ad68c817d5649f55e52dab54108c50`，远端分支与固定提交入口已核实，累计149道。所有编译/SQLite均在Yupeng；模型容量不足未更换模型，约25节点按实际24交付，不凑数。进入第七批，GA073已主机编译并入库。

第七批最新独占来源：通信CCC2021.5/arxiv2011.04071及CCC2021.7/arxiv2103.00864/ECCC TR21-037；CCC2021.6的期刊版DOI10.4086/toc.2026.v022a002已命中旧库792，停止本线该源生产，原件保留。几何CCC2022.19/arxiv2205.02374v2与2022.20/arxiv2111.10409v4；数论CCC2022.30/arxiv2011.04295/ECCC TR20-165。上述未占来源实际别名已完整旧库/准备表/两线刷新无命中。Goal记录仍存在，但再次观察为blocked，工具不能resume；用户/system需/goal resume，当前授权生产继续，不标记目标完成。

数论后续精确独占CCC2022.31 Vanishing Spaces of Random Sets and Applications to Reed-Muller Codes，实际arxiv2205.10749及10.48550 DOI/ECCC TR22-075已完整旧库/准备/两线刷新零命中，NT053起；主结论与直接Reed-Muller应用不拆数。NT052当前TeX包装待修复，尚未计入可用或上传。

目标现已回读恢复active，按原30000总目标继续。第七批已新增编译入库11题。下一精确独占来源：几何CCC2022.21/arxiv2103.14134/ECCC TR21-047，数论CCC2022.33/arxiv2202.07761/ECCC TR22-018/期刊DOI10.1137/22M1498346；全部实际身份已完整旧库/准备/两线刷新零命中。CCC2022.32正式刊本主证明defer缺口见MATERIAL-GAP.md，不计新增，保留原件转源。

数论完成2022.33后独占CCC2022.34（Xin Lyu, Improved Pseudorandom Generators for AC0 Circuits），实际arxiv2301.10102/10.48550 DOI/ECCC TR22-021/Berkeley EECS-2024-212与正式DOI已完整身份刷新零命中。按实际版本许可取完整作者题证；支撑switching/partition框架不额外拆数。

通信后续CCC2021.8的期刊身份DOI10.4086/toc.2022.v018a022命中旧库970，避让该源，不创建新题。改独占CCC2021.9 Shadows of Newton Polytopes（Hrubeš/Yehudayoff），实际ECCC TR20-189与正式DOI完整身份刷新零命中，CC051起；发现额外实际版本先刷新后生产。第七批NT054完整编译入库，其原作者复杂TikZ图已在Yupeng渲染并查看，标签/图注完整。

第七批现15份已主机编译入库（其中GA080正式Gaussian PTF PRG）。几何后续独占CCC2022.22（Aggarwal/Alman, Optimal-Degree Polynomial Approximations for Exponentials and Gaussian Kernel Density Estimation），实际arxiv2205.06249及10.48550 DOI/正式DOI已完整旧库/准备/两线刷新零命中；GA081起，实际许可/额外别名先确认，参数区间及正负指数同机制不拆数。工作树/前缀沿用20261013固定身份。

第七批当前16份实际编译入库。数论后续独占CCC2022.35 Characterizing Derandomization Through Hardness of Levin-Kolmogorov Complexity（Liu/Pass），实际ECCC TR22-084与正式DOI已完整旧库/准备/两线刷新零命中，NT056起；两个方向及hitting-set/support合1主等价，保留原promise与量词条件。

通信2021.9补报实际期刊身份DOI10.1007/s11856-023-2510-z（Israel Journal of Mathematics 2023），根完整身份刷新同样零命中，正式CCBY范围不自动扩到期刊额外内容。数论2022.35当前承重参数改造证明defer到长稿，先核对完整版本许可；下一备用独占CCC2022.36 On One-Way Functions from NP-Complete Problems（Liu/Pass），ECCC TR21-059与正式DOI完整身份刷新零命中。先与本线NT047/NT045题面做有限近邻比较，重复NP-hardness/直接SoI后果不额外计数。

第七批现18份主机编译入库。几何下一独占CCC2022.23 Extremely Efficient Constructions of Hash Functions, with Applications to Hardness Magnification and PRFs（Chen/Li/Yang），实际ECCC TR22-086/正式DOI完整旧库/准备/两线刷新零命中，GA082起；support组件与直接PRF替换应用不拆数，额外实际身份先刷新。

第七批当前19份实际编译入库。数论转源CCC2021.25 Arithmetic Circuit Complexity of Division and Truncation（Dutta/Jindal/Pandey/Sinhababu），实际ECCC TR21-072与正式DOI完整身份刷新零命中，NT056起。通信独占CCC2021.10 Fractional Pseudorandom Generators from Any Fourier Level，实际arxiv2008.01316/10.48550 DOI/ECCC TR20-121（旧题名from the kth Fourier Level同源）完整身份刷新零命中，CC053起，保留实际选版5作者。其他新版本先刷新再取材；参数分支/support不拆数。

通信完成2021.10后独占CCC2021.11 Deterministic Identity Testing Paradigms for Bounded Top-Fanin Depth-4 Circuits（Dutta/Dwivedi/Saxena），实际arxiv2304.11325及10.48550 DOI/正式DOI完整身份刷新零命中，CC055起。作者页标ToC2026 to appear，未确认正式期刊DOI不编造；实际额外身份先报根。

第八批用途处理：NT059作者主要结果区明确为独立dense transcendental-series短电路构造，相关38/40/44已合1题；NT060独立PosSLP判定结果保留完整材料作背景，H2用途不足暂不单计，不能称为别题承重引理或重复。来源接续：通信CCC2021.13/arxiv2102.06652（已全身份零命中，修订/许可逐版保留）；几何CCC2021.14/ECCC TR20-054（已全身份零命中），避开下载受阻的2022.24完整长稿。

数论下一独占CCC2021.26 SOS Lower Bound for Exact Planted Clique（Shuo Pang），实际ECCC TR21-070与正式DOI已完整身份刷新零命中，NT061起，完整作者pseudoexpectation/PSD主证链合主题，不拆技术by-product。

第八批接续独占：通信CCC2021.15/arxiv2011.05085（v2实际CC BY-NC-SA4.0按原许可），几何CCC2021.16/期刊10.1145/3625308/共享长稿arxiv1907.00309（另含SIAM10.1137/21M1441110部分），数论CCC2021.26/ECCC TR21-070；所有实际身份已完整旧库/准备/两线刷新零命中，后续另有身份先报。CC059图片依实际TeX目录修复，原图主机渲染查看完整；CC060 r002显式恢复array依赖已实际编译。
