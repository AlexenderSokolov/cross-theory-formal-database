# 已下载来源的接续流程

适用于Yupeng当前环境，2026-10-04实测。

1. 下载先完成。2390个exactURL的4951文件约2.43GB是来源接收，不是题目合格数；落地页、policyPDF、论文PDF和完整原生源分别判断，asset未齐不能假称完整。
2. 交worker前明确SOURCE_PATHS.json绝对原件路径和sha/bytes，将已缓存原件复制到其独有cached-originals；旧catalog artifact_refs不存在不是源缺失。复用原件，不重复网络下载。
3. cache的not_yet_admitted_for_publication只是下载阶段初始许可状态，worker必须实际读articlePDFfront/native/作者版本及组件许可并保存事实，不能以初始状态直接泛hold。article授权不能自动覆盖publisherclass/第三方图/字体；原HTML和privateevents不进公开包。
4. 尚未生成TeX/evidence/compile/DB/CAS是明确工作项，而非来源缺证明。先完整人类statement/proof/必要新局部core与具体H1/H2/H3材料筛选；继而整理实际正文/出处/权利/版本/定位、真实禁shellescape编译、逐题与smallaggregate、全页QA、SQL完整投影和独立恢复。真实源关键不清/主困难略证/许可不明/难度不足才sourcehold。不AI补证、不数学审稿/投票。
5. 只复用结构模板，例如candidates/published-pilot/package-938-r017与candidates/native-pilot/packet-1492-r002/package；作者、DOI、许可、标题、修改说明按本源重写匹配。manifest行与sources/ID/provenance.json必须一致，实际全文SQLite依据最终包重建；main/ID/Git仅root。
6. CLI0.160 feature名先用features list核；不存在browser/mcp_elicitation会让任务在启动前退出，不能仅凭PID宣称开工。正确版本支持browser_use/browser_use_external/in_app_browser/tool_call_mcp_elicitation。-a never、禁MCP/提问、非login、显式最小PATH和projectruntimePython保持；清环境不能丢标准PATH。
7. sourceAPI实见Concurrencylimit，对project并发排队，queued不算active，不能反复8泛任务空跑。启动需要thread.started+真实成功工具/原件读取，资格需要全闭环；observe2额外请求成功不是声称provider永久max2。
8. SSH认证前随机closed和源缺失/数学hold分开；同获授权endpoint短退避，必要root持续TTY单写代跑，不改全局SSH/服务/代理，不复制credentials。所有失败和唯一未发布材料保留，不删除。
9. 编译/验证显式package/evidence/build-root/receipt-root/item/report；build与receipt都在只读包外。历史CAS若receipt在package内，按sha同字节复制到包外external-receipts再明确验证，不能伪造receipt或声称新编译。证明正文不变但program/asset身份改变须重跑受影响范围。
10. 每个角色给具体首件/claim/core和确切包路径，不能以复杂泛指令代替行动；source-admission和math/core/difficulty准入分别记录。停止无实质产物的泛任务，继续明确缓存单元。每次接续读CURRENT、actualreports及真实HEAD，主库已远端1015，独立公开备份ready10不重复相加，20净新增试点未完成。
