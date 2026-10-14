# 第四条Codex主机收题与上传

统一准则见../../PROJECT.md。作者承担数学责任；执行者收完整作者题证及必要上下文、用途难度、定向近邻比较、编译建库和交付，不重证不补证不加假设不找反例不审稿，不哈希/逐字节/日志工程。

根代理独占jobs、数据库、索引和上传；材料代理只写分配lane，模型统一gpt-6.1-sol / medium。

|lane|prefix|独占作品及别名|
|---|---|---|
|metric-decompositions|CP01A1333E-MD-|doi:10.4230/LIPIcs.SoCG.2025.66；arxiv:2502.01120|
|persistence-modules|CP01A1333E-PM-|doi:10.4230/LIPIcs.SoCG.2025.41；arxiv:2504.08119v2（完整版CC BY-SA4.0）|
|local-coloring-linear-logic|CP01A1333E-LL-|doi:10.4230/LIPIcs.FSCD.2025.16|

约25道净新增一批，不设领域配额，不拆小引理、直接推论或替代证明凑数。准备分支上传不计生产主库公开增量。新来源由根代理按精确身份分配。

从本task_root运行：
```bash
bash operations/run_assemble.sh --task LANE/TASK/task.json
bash operations/run_compile.sh --job jobs/TASK/r001 --resume
bash operations/run_export.sh --batch batch-001 --limit 25
python operations/source_neighbors.py doi:10.4230/LIPIcs.SoCG.2025.66
python operations/prepare_upload.py batch-001
```

失败包装修正后run_assemble.sh --refresh --assemble-only，再run_compile.sh --resume；成功成品直接复用。prepare_upload.py会实际暂存明确依赖，不提交或推送。上传由根代理在主机提交生成bundle，通过本地独立corpus-relay-01a1333e.git普通推送。本地不生产材料、不共享其他线relay引用。

## 后续精确来源分配

- MD：doi:10.4230/LIPIcs.SoCG.2025.2；doi:10.4230/LIPIcs.SoCG.2025.3。
- PM：doi:10.4230/LIPIcs.SoCG.2025.16（arxiv:2411.19208v2，CC BY-SA4.0）；doi:10.4230/LIPIcs.SoCG.2025.43。
- LL：doi:10.4230/LIPIcs.FSCD.2025.25（含作者正式证明附件）；doi:10.4230/LIPIcs.FSCD.2025.28。

上述分配作品连同不同版本归同一lane，不跨组重复计数。

## 当前接续分配

- MD：SIGMA2025.072（arxiv2411.03882）、SIGMA2025.075；SoCG2025.53（arxiv2504.02190v2，CCBY4）主PTAS；SoCG2025.3/.13目前材料缺口不计数。
- PM：SIGMA2025.070（arxiv2410.05846）、.071（arxiv2504.15597）、.073（arxiv2304.00699）；SoCG2025.43对应arxiv2410.21204v3；SoCG2025.52完整证明许可缺口不计数。
- LL：FSCD2025.8、.12、.13、.15；.9/.10/.28候选未完成不计数。

工具工程针对性检查：operations/check_export.py复用实际成品于自有.work隔离fixture，覆盖前缀隔离、批次参数透传、旧批保留、已上传不重复、排除行退出有效集合、续跑稳定。源码/数学不复审。已修run_export.sh参数透传缺口。

## 后续批次独占来源

- PM：SIGMA2025.078（arxiv2412.05224）、.080（arxiv2504.08293）、.079（arxiv2405.03259，旧158691仅X-asymptotics，需按具体主结论避让）。
- MD：SIGMA2025.075（arxiv2404.15767，旧158092仅lemma01，已定向避让）、.081（arxiv2409.11306，旧806已计Theorem5.6，必须避让）。
- LL：FSCD2025.12（固定arxiv2505.06193v2，CCBY4）、.13、.15。

作者形式证明附件以原始源文件交付，并将完整文本纳入SQLite proof_text；不重跑形式验证。

## 第二批接续来源

- PM：SIGMA2025.083（arxiv2410.14068）；.088（arxiv2408.16696，旧164471仅graphest Lemma3.8，有限比较后避让）。
- MD：SIGMA2025.089（arxiv2509.17976）；.084与旧177319 trop-dist同题不计新增。
- LL：FSCD2025.17（作者固定正式证明commit70dfc56f33a6e4835281044e68aa68279989047e，代码MPL2单列）、.18、.19、.20。

## 第三批预分配（具体作品独占）

- MD：SoCG2025.54、.55（Fréchet近似、knot factorisation）。
- PM：FSCD2025.26（Functorial Models of Differential Linear Logic）。
- LL：FSCD2025.27（Conversion Checker作者材料，只收作者证明，不执行认证）。

## 当前第三批接续

- MD：SoCG2025.58（arxiv2412.15419v2，CCBY4）、.59；.57无独立H2主结果，已保留来源不计。
- PM：FSCD2025.29、.31；.29 HAL长版hal-05067259v1已取CCBY4原PDF，待5页证明可编辑TeX转录，candidate不计数。
- LL：FSCD2025.30；.27（arxiv2502.15500，paper CCBY4，固定作者项目源码MIT）。

首两批各25已上传：batch001内容98bed985b6c86de05892cbbaf224681876e2fae8；batch002内容d468e1a0ea4a4480eb30a5d0a067f28370a1491b。各批UPLOADED.json保存对应材料集合，后续批次不重复计数。

## 当前明确独占队列更新

- MD：SoCG2025.60、.61（3D knapsack、fat convex transversals）；SoCG58 alias arxiv2412.15419v2、SoCG59 alias arxiv2504.07366v1。
- PM：FSCD2025.32、.33（interpolation/cut-introduction、ordinal presheaf guarded equations）。
- LL：FSCD2025.30（coherent Tietze transformations）。

工作树/分支/任务前缀及单根写jobs/SQLite/索引/上传的范围保持不变。所有已编译成品复用，不重编；缺口仅影响该题，其他继续。

## 后续小组分工

- MD：SoCG2025.62（arxiv2412.03332v2）、.63、.64。
- PM：FSCD2025.34。
- LL：FSCD2024.5（arxiv2402.15174）、FSCD2024.6。2024会议HTML实际404，须取得合法完整可编辑路线后计数。

均已由根对完整旧库、准备表及三条在途产线做定向来源查询；实际固定版本别名由材料组补查，上传前刷新。

用户已明确要求持久执行，当前Codex持久目标为active；沿用项目30000总目标，约25道上传节点后继续，不另设后台服务/调度器。当前后续独占：MD SoCG2025.65/.67；PM FSCD2024.7/.8；LL FSCD2024.5/.6。

第三批25道净新增已上传：[batch-003成品索引](delivery/batch-003/INDEX.md)，内容提交`1e4fec0a820e84b28ccd11a337f6fffed7de8c65`，累计75。远端分支及HTTP200入口已核对，生产主库公开增量仍为0；持久目标active，继续第四批。

第四批后续独占：MD SoCG2025.68/.69；PM FSCD2024.7（arxiv2402.14485v4、CCBY4）/.8；LL FSCD2024.9/.10。SoCG2025.67完整版本arxiv2412.03372v3归MD；FSCD2024.6固定CCBY版本arxiv2405.03264v1归LL。未明确授权的外部代码缓存不纳入资产，论文自身完整作者证明可独立交付。

PM后续独占FSCD2024.11（Optimizing a Non-Deterministic Abstract Machine with Environments）、.12（A Linear Type System for L^p-Metric Sensitivity Analysis），根完整旧库/准备表/三线定向DOI标题查询无命中；固定作者版本别名由材料组补查。MD027已实际编译成功，第四批当前4道净新增入本线库；容量错误接续原GPT6.1Sol medium，不更换模型。

MD后续独占SoCG2025.70与.72，根全旧库/准备5229/三线372,289,110定向DOI标题查重0。SoCG69的实际完整版arxiv2410.22242v3为nonexclusive且官方版缺Appendix续证，原件保留不计。FSCD2024.9的HAL04568289归同作品别名，根补查0；选用许可仍为官方CCBY论文。当前第四批8道已编译入库，累计83、已上传75，持久目标active继续。

当前精确后续分配：LL完成FSCD2024.10后独占FSCD2025.4（Substructural Parametricity）；PM保留FSCD2024.11/.12合法完整PDF待editable转录，继续独占FSCD2025.5（The Cost of Skeletal Call-By-Need, Smoothly）。根已对完整旧14875、准备5229及三线377,295,119定向DOI/标题查询0，具体版本别名由材料组补查。

后续精确分工：MD SoCG2025.73/.74；LL FSCD2025.4/.7；PM FSCD2025.14/.11。FSCD2025.6会议版全部证明指向nonexclusive全文，已保留缺口不计。旧HTML转换器依赖BeautifulSoup；项目Python可append现有/disks/sata1/yupeng/anaconda3/lib/python3.13/site-packages读取bs4 4.13.5与soupsieve（已实测），不新增依赖。来源转换脚本自己的运行说明保留该路径，装配/编译/SQLite仍用项目Python。

用户明确执行边界：禁止在本机编译；所有取材、装配、TeX编译、SQLite建库及提交仅在Yupeng主机执行。本机仅SSH控制、Git认证中转及查看成品。

当前独占接续：MD SoCG2025.75/.76；LL FSCD2025.24（arxiv2505.09960v1 CCBY4）和FSCD2026.4；PM FSCD2025.11（arxiv2505.13495v1完整论文版本，原封面作者/导师角色与arxiv作者列差异均保留）与2025.14。材料/编译/建库继续仅Yupeng，本机禁止编译。

MD后续明确独占SoCG2025.77/.78，根全旧14875/准备6704/三线418,446,186定向DOI标题查询0。SoCG2025.75两个固定完整版本2504.07752v1/2504.07770v1归同组，缺失作者公式上下文已从其自身CCBY companion原文收齐，不猜测改数学；2025.76固定2412.02866v1主结果一题。

第四批25道净新增已上传：[batch-004成品索引](delivery/batch-004/INDEX.md)，内容提交`88e83b5768e6c857416399ce61db7afbf6d76d8f`，累计100。远端分支及HTTP200入口已核对，生产主库公开增量仍为0；持久目标active，继续第五批。所有编译仅Yupeng，禁止本机编译。

第五批后续独占：MD SoCG2026.4/.5；LL FSCD2026.7/.9；PM FSCD2025.11/.14。根对完整旧库及准备6704/三线446,457,196的精确DOI/标题查询0。SoCG2025.79/.80为CG Challenge条目，当前未分配，不默认计为H2。后续固定版本与别名由材料组实际补查。

原生BibLaTeX任务的私有Biber依赖：主机项目Python执行operations/prepare_biber.py，从官方SourceForge固定2.21下载至本线.work/biber-2.21并验证版本。run_assemble.sh/run_compile.sh自动使用私有binary，PAR/TMP缓存也在该目录；不改共享TeX Live，不在本机安装或编译。主机biblatex3.21/BCF3.11/BBL3.3已核对。

本线分离装配与编译时使用 run_assemble.sh --assemble-only，再run_compile.sh。后者通过compile_material.py仅向当前job材料包目录前置BSTINPUTS，供作者自带plainurl.bst等样式使用；原prepared_delivery接口及共享TeX不变。量子线路LL030已在主机编译62页、置换树LL032已编译6页。

当前精确独占：MD SoCG2026.8/.9（.6/.7/.8完整版许可与作者续证明缺口保留不计；.8别名2601.16468）；LL FSCD2026.10/.11；PM FSCD2025.11/.14。PM2025.11固定2505.13495v1原封面明确Master thesis，保留硕士论文作者/导师角色与arxiv作者列原貌，不称博士论文。新四DOI定向查重旧14875/准备6894/三线498,457,202无近邻；上传前刷新。

MD接续独占SoCG2026.10（2512.08652）/.11，MD045–047来自SoCG2026.9固定CCBY版本2601.02920v2；root已对全旧14875/准备7083/三线502,457,202查询.10/.11无邻居。FSCD2025.14实际同作品别名2506.09453归PM，未授权作者代码缓存不列交付。

PM下一独占FSCD2026.12/.13（量子程序资源界、概率计算证据带语义）；2025.14非标准核心Prop7完整证明许可缺口保留不计，不把它当标准先修略去。LL继续FSCD2026.11（固定2601.05199v4 CCBY4）。

当前后续独占：MD SoCG2026.12（2602.16306）/.13；LL FSCD2026.14/.15；PM FSCD2026.12（2510.20452v2、HAL05518918v1）/.13（2605.07259v1）。root已刷新全旧14875/prep7088/三线518,457,202的精确来源查询，暂无邻居；实际别名继续补查，上传前刷新。第五批已主机编译入库19，累计119、上传100。所有编译仅Yupeng，本机禁止编译。

本线多修订导出按job路径排序，后来的r002替换同task旧r001有效呈现，旧job保留且不增加题数。LL033页眉修正已生成r002、实际编译5页并在真实第五批导出确认只计一题。原作者重复anchors仅在呈现副本机械唯一化早期label，保留最后原label/所有原引用语义；原件及说明均保留。

第五批25道完成主机编译与SQLite入本线库，准备上传；本批17个独立作品/版本组对完整旧14875、准备7179、最新三线525,457,202定向刷新，无同来源近邻。SQLite有效集合、选择清单、ITEMS与原100道已上传集合核对一致且不重计；LL033仅新r002有效。

第五批25道净新增已上传：[batch-005成品索引](delivery/batch-005/INDEX.md)，内容提交`f20e9dc69d12085111dfea4b38faa5a80c1064c0`，累计125。远端本线分支与HTTP200成品入口已实际核对，生产主库公开增量仍为0；持久目标active，继续第六批。主机累计已编译入库129，其中第六批4道未上传。所有编译仅Yupeng，禁止本机编译。

当前独占接续：MD SoCG2026.16/.17；LL FSCD2026.18/.19；PM FSCD2026.17合法完整PDF正在忠实转录。SoCG2026.14作者于2026-10-08撤回并说明结果错误，保留记录不计；.15完整证明许可缺口保留不计。

第六批继续：PM FSCD2026.20 Relational Dualities and Bisimulation、.21 Constructing (Co)inductive Types via Large Sizes（root全旧14875/prep7179/三线532,457,202查询0邻居）；MD当前2026.17仅选官方完整已发表主证明范围，2026.16整节作者称sketch且full许可缺口，不计；LL 2026.19仅发表CCBY范围与AppendixA，额外NC full附录不混入。

第六批后续独占：MD SoCG2026.18（2603.18997；旧196746仅lem:Gr_clique-levels）/.19（2602.10795；旧194428 thm:beta-gamma）；LL FSCD2026.22/.23（2609.17324；旧210587 prop:Qonmor）；PM FSCD2026.20/.21。根对全旧14875/prep7179/三线538,457,202定向查询，已将三项有限旧邻居及原文位置交各组比较避重，不靠新task号/版本号计新增。

PM后继独占FSCD2026.24/.25，root全旧14875/prep7179/三线549,457,202精确DOI/title查询无邻居。PM041关系Thomason对偶已实际主机编译21页入第六批，135累计已编入库；作者mathpartir依赖按原sty与GPL许可交付，原列表enumerate已恢复。

MD接续独占SoCG2026.20（2603.09048）/.21；PM FSCD2026.24/.25（2512.22930）；LL继续2026.23（2609.17324）避旧210587。root新两MD DOI/title定向查询全旧14875/prep7179/三线551,457,202无邻居；固定作者版本别名持续补查。第六批14道已主机编译入库、累计139，成功成品复用。

LL038原作者Rocq核心sub_trans_size题证已由root仅XeLaTeX编译7页并入库，未运行Rocq；原代码与GPL3许可完整附上，其他未选桥的Admitted披露保留。MD058/059各59页、MD06025页已主机编译入库；旧196746/194428有限比较避让结果随task记录。当前第六批14道、累计139，上传125。

LL后继独占FSCD2026.26/.27（Polymorphism Meets DHOL），MD SoCG2026.22/.23；root全旧14875/prep7179/三线556,457,202精确DOI/title查询均0邻居。LL039事件结构2-density与旧Qonmor计数命题有限比对后独立，已实际主机编译4页入第六批；作者省略的最后验证原句保留，不补写、不声称独立认证。第六批15道、累计140已编入库。

PM044 congruence/equality proof equivalence已实际主机编译10页，MD065原生random Delaunay shifting29页已实际编译，累计149、第六批24道已入库。旧材料代理句柄在本次协作列表已不存在，根按原GPT6.1Sol/medium/forknone接续三名材料代理，先读现场与具体活进程；已成功源复用。下一LL FSCD2026.28/.29，MD拟SoCG2026.26/.27、PM拟FSCD2026.30/.31（根完整旧库查询在途，确认后才取材）。

当前精确后继：MD SoCG2026.28/.29（root全旧14875/prep7273/三线573,457,202 DOI/title查0）；PM FSCD2026.30/.31（2605.00655）；LL FSCD2026.28/.29。旧MD26/27承重续证许可证缺口保留不计。LL041原LIPIcs必要threeparttable/optional依赖按原包与许可局部交付，仍由root主机编译。

MD后继独占SoCG2026.28（2603.21617）/.29（2603.21790），只选官方CCBY完整新core范围，原full不同许可不套标；根DOI/title查全旧14875/prep7273/三线573,457,202为0，实际别名正在补查。当前149道已编译入库、第六批24，上传125。

第六批25道已完成主机编译、SQLite与最终选择/ITEMS核对，准备上传；已上传125集合无交叠。完整旧14875/prep7273/最新三线589,457,206来源刷新仅命中旧196746 level计数、194428 beta-gamma、210587 Qonmor，三项已有有限题面/证明范围比较并避让；其他本批来源无邻居。只选task显式合法依赖，未选private/NC/许可未明rawcache不公开。

当前接续独占：MD SoCG2026.30（2603.21585）/.31（2601.03516）；LL FSCD2026.32/.33（HAL05694098）；PM FSCD2026.34后接CSL2026.20（PHart3/colimits-agda）。FSCD2026.35官方404不分配。作者formal附件仅保留原代码，不运行Isabelle/Agda/Rocq；未选个人/NC/许可未明缓存不公开。第六批上传前fresh查询全旧14875/prep7564/三线597,457,209仅原三有限邻居，无新增同题。

第六批25道净新增已上传，内容提交`adee782657a265911a0be0e6089717f7cea1d548`；本线累计150道，远端分支指向与成品索引HTTP200已实核。生产主库公开增量0。第七批已主机编译入库8道（累计158），MD066只取r002且保留r001，不重计。持久目标active继续；所有编译仅Yupeng，本机禁止编译。当前独占MD SoCG2026.32/.33、LL CSL2026.21/.22、PM CSL2026.23/.24；根全旧14875/prep7564/三线611,457,212定向DOI/title无新来源邻居，实际别名继续补查。

第七批已主机编译入库12道，累计162、上传150。PM046正式作者Agda证明只作Unicode忠实排版未执行，44页缺字已修；PM048主LAPC完整印刷证明24页；MD069完整原生正文/附录47页。LL041页眉实际裁切仅自有新r002缩短原runningtitle，59页成功，旧r001保留同题不重计。LL045 covering/subgroup主分类21页，已有限比较不同于本线旧LL022/23。当前MD后继独占SoCG2026.34/.35（fullold14875/prep7826/三线614,457,213 DOI/title0）；.32仅直接tensor正确性不计H2，.33官方新core缺证明且full2603.28268v1为nonexclusive，保留gap不计。

当前接续独占已更新：MD SoCG2026.36/.37（root全旧14875/prep7826/三线619,457,214 DOI/title无邻居）；LL CSL2026.25/.26（root全旧14875/prep7826/三线616,457,214 DOI/title无邻居）；PM CSL2026.23/.24固定CCBY完整源2506.14538v1、2507.18539v3。MD34/35作者full合法但主机有限官方src请求TCP超时，具体核心续证/数据结构材料gap保留不计，未改网络配置或用本机取材编译。第七批13道已编译入库，累计163、上传150；PM049仍仅实际排版错误待修，不计新增。

第七批14道已编译入库，累计164、已上传150；PM049真实排版问题已修并主机编译48页，成功源freeze。MD授权SoCG2026.34/.35临时TCP下载缺口已在主机通过官方export/arxiv urllib实际取得固定CCBY原tar解除，恢复34→35整理；仅下载不计新增。36/37许可/续证检查保留原件，不套会议许可。所有编译仅Yupeng，持久目标active。

第七批已主机编译入库21道，累计171、已上传150。PM050原作者showkeys调试标签实际遮挡正文，独立r002仅去debug包，重新主机编译33页并视读确认清楚；原r001/source保留，同题不重计。LL0478页、LL04813页、MD07231页、PM05135页均成功且已视读；SQLite有效集合与SELECTION/ITEMS一致，无已上传150交叠。当前接续独占LL CSL2026.29/.30、PM CSL2026.27/.28，MD SoCG2026.37精确HALv1完整CCBY版本正在可编辑转录。全部编译仅Yupeng，禁止本机编译，goal active继续30000总目标。

当前接续精确独占：PM CSL2026.31 Parametric Disjunctive Timed Networks（2512.04991；只选官方完整证明，nonexclusive全文不公开）/.32 Mean-Payoff and Energy Discrete-Bidding Games（2509.00506v1 CCBY4），root全旧14875/prep7826/三线639,457,219 DOI/title查询0，实际别名由PM继续补查；LL CSL2026.29/.30，MD SoCG2026.37固定HAL04816535v1自身CCBY4完整作者PDF可编辑转录，v2不同许可不混。第七批23道已编译入库、累计173，已上传150，所有编译仅Yupeng。

第七批25道已完成主机编译与SQLite最终集合核对，准备上传；累计175已入库、另PM054成功46页待后批，已上传150。LL049全部68原数学电路PNG（76实际引用）保留，完整normal-form证明6页成功并视读；PM053仅官方完整Theorem17全局不可达证明30页，未选Theorem20 sketch；三处r002仅更新呈现同题不重计。上传前root再次刷新完整旧库/准备表/三条线，再按最终明确资产选择提交，所有编译仅Yupeng。
