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
