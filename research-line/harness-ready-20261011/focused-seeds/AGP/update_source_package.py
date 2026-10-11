import pathlib,json,collections,datetime
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf8'))
rows=load(O/'READY_TASKS.json');ts=[load(P/x['task_path']) for x in rows];routes=collections.Counter(t['route'] for t in ts);numbered=[t for t in ts if t['problem_id'] is not None];sources=collections.defaultdict(list)
for t in ts:sources[t['source_id']].append(t['task_id'])
report={'prepared_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ready_count':len(ts),'route_counts':dict(routes),'numbered_by_root':len(numbered),'source_identity_count':len(sources),'task_ids':[t['task_id'] for t in ts],'pending_tasks':load(O/'PENDING_TASKS.json'),'pending_readings':['canonical-kac-reading.json'],'validation':'MATERIAL_VALIDATION.json','claim_boundary':'Ready mathematical source/configuration preparation only. No new published count, compilation or E2E claim by this agent. Root owns IDs, integration, sample review and publication.'}
(O/'PREPARATION_STATUS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
text=f'''# AGP 来源级准备包

当前 {len(ts)} 张数学材料/装配配置 ready：代数 {routes['algebra']}、几何 {routes['geometry']}、概率 {routes['probability']}；其中 {len(numbered)} 张已由 root 写入真实正式编号，其余保留 null。不是编译、公开或端到端交付数。既有25与3published不在此重复计数。

## 使用入口

- `READY_TASKS.json`：实际可整合题卡路径；各卡有完整作者题证区间、先修、1–3项义务、难度理由、语义近邻和 focused review。
- `SOURCE_RECORDS.json`：每张卡的固定版本、允许区间、已计排除、宏/书目/资产、许可及来源授权候选记录。root统一审批路线。
- `MATERIAL_VALIDATION.json`：review/config binding、范围边界、文件存在和装配角色一致性结果；没有以这些检查声称数学逐步认证。
- `PENDING_TASKS.json`、`HOLDS_AND_PENDING.json`、`canonical-kac-reading.json`：有具体疑点者独立保存，不进ready计数。

## 原件、许可和范围

1. SIGMA/JEP/AHL固定作者TeX与既有逐文许可，只读复用或定点缓存。旧公开2007/2039/2870/1912/1065/2088/1651的原主张只作为近邻或不计数支持；新卡按source+claim分别比较。
2. Stacks位于`sources/stacks-snapshot-20261011`。原始路径D:/tmp/r2work/repo；固定为本地2026-10-11快照，上游commit未记录，绝不冒用a044或当前HEAD。原preamble、my.bib、COPYING、tags均保留。许可GNU FDL1.2或更高；只选定卡内范围，不把完整缓存当整章已审。
3. HoTT位于`sources/hott-book-578b85cc`，完整官方archive与解包均保留。固定HoTT/book commit578b85cc8d586b1677ec4335148adeb443057d24；集体作者The Univalent Foundations Program；实际README/front版权页明确CC BY-SA3.0Unported。保留macros.tex、references.bib、原编号表和单独署名/同许可声明，不混成CC BY4。

## 先修和复用边界

常规 focused 检查题证配对、关键假设、具体剩余义务、许可与语义近邻；接受可信作者完整proof作为参考。此前完整阅读/实质review逐卡引用，不重做整篇、逐式验算或标准先修递归。承重本地作者构造保留为proof spans；不以标签指针替换核心。普通格式或唯一读法笔误保留可见说明。

Freudenthal旧提取错配已纠正：新卡保留真proof1747–1791和完整code/wedge链，旧1676–1707只是不计数辅助构造。未将Eckmann–Hilton、球面短推论或作者明确outline/exercise当新题。

0F2B的Ext长度/image解释仍为needs_codex，等待定点独立确认。等特征Epp末支的Galois条件、canonical静态Kac子结论的取材边界也没有计为成熟；已有反例/HOLD不重开。

## 后续具体来源

优先同一固定HoTT的独立完整构造，以及既有Stacks深读记录中未与公开库重合的独立命题。暂避原037 Stein、272 affine reconstruction、297 henselian-local finite-etale、310 Faltings、389 resolution-property等近邻过强的机械推广；不按旧H2标签自动收。

本包未删除、计算内容hash/逐字节比较、提交推送或远端占号。正式编号与公开由root执行。
'''
(O/'SOURCE_PACKAGE.md').write_text(text,encoding='utf8');print(report['ready_count'],dict(routes),len(numbered))
