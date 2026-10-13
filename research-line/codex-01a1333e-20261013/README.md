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
