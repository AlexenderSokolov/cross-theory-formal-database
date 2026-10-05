# 高级数学人类证明题库：DeepSeek 接管交接

本文件与 `DEEPSEEK_PROMPT.md` 是当前接管入口。根目录 `PROJECT.md` 中的旧 OpenResearch、旧实验、100/1,000/10,000 题方案属于历史，不覆盖当前任务。

## 1. 当前事实、目标与暂停边界

**现场核对时间：2026-10-06 00:12:51，北京时间。** 读取了 Yupeng 的真实状态、Git HEAD、队列、全局 hold、公开恢复记录及 GitHub 生产分支。以下是该时刻快照，不代表永久实时状态。

目标：30,000 道合格唯一的人类高级数学证明题，完成可恢复的公开交付。原定来源完整性、许可、H1/H2/H3 难度和语义去重标准保持；本轮简化的是重复审核与重复工程处理。

| 项目 | 核实结果 |
|---|---|
| Yupeng 本地主库已合并 | 1,115 道 |
| 公开精确提交可恢复 | 1,115 道 |
| 已准入未合并 | 7 道 |
| FIFO 队列 | 816、2380、919、817、818、819、915 |
| 下一批目标 | 1,140；还需 18 道新准入 |
| 当前生产状态 | waiting_for_admissions |
| 已合并但尚未公开的数量 | 0 |
| 当前待发布批次 | 无；上一批 publication 记录为 delivered |
| 控制服务 | corpusctl.service，active/running，PID 309274 |
| runtime 登记的存活作业 | 0；不能据此断言机器上没有其他未登记进程 |
| controller / generation | local-controller-01a10a85 / 1 |

用户之前要求原 Codex 停止推进，之后要求完成交接和 GitHub 快照；本次交接不恢复生产。服务仍在运行，不能写“所有进程已停止”。用户向 DeepSeek Harness 提交执行提示词后，由 Harness 核对既有进程并接续生产。旧 Codex/旧心跳不得自行恢复。

本轮仅更新交接文档和保存指定状态文件。新增准入、公开题库交付均为 0。先前生产耗时未在本轮完整采样，不编造吞吐。

## 2. 哪个目录才是当前项目

| 用途 | 位置 |
|---|---|
| 本地交接目录 | `D:\Study_Works2\Lean_grokking`，不是 Git 根目录 |
| 本地控制工具 | `.work/human-proof-corpus-control/corpusctl-implementation` |
| 本地 Git 发布中继 | `.work/human-proof-corpus-control/relay.git`；bare 仓库，默认 main 无提交不代表没有发布对象 |
| 本地发布缓存 | `.work/human-proof-corpus-control/publication-cache` |
| SSH 别名 | `Yupeng-orx` |
| 远端根目录 B | `/disks/sata1/yupeng/human-proof-corpus` |
| 当前生产 Git 仓库 | `B/repo` |
| Python | `B/runtime/python/bin/python` |
| 控制器 | `B/repo/corpus-work/corpusctl` |
| 控制器状态 S | `B/operations/corpusctl` |
| 已有辅助操作目录 | `B/operations/local-controller-01a10a85` |
| 公开仓库 | `https://github.com/AlexenderSokolov/cross-theory-formal-database.git` |
| 正式生产分支 | `corpus-progress-20261001` |
| 本次交接快照分支 | `corpus-handoff-20261006`；分支是否已推送以交付回执为准 |

本地 `Cross_Theory_Research/Cross_theory_database_formal` 是旧 checkout：最近提交为 2026-09-30 的 `f04850a3`（180 题），并有旧未提交改动。保留它，不从这里向当前生产分支推送或重建当前队列。

重型源码、TeX 编译、SQL 和单题产物在 Yupeng；本地用于控制、有限页面核对和发布中继。不要恢复旧 OpenResearch 会话、旧 DS Lite 实验，或再搭建一套服务器模型 worker。原 FLOW 中关闭的 source dispatch 不要批量开启，它用于防止重复生产。

## 3. GitHub 已交付与尚未提交的区别

2026-10-05 20:54:08 北京时间提交并公开的生产 HEAD 为：

`e538b983d4cbde0eac14ad1fdcb4a7ba9605e9c4` — `corpus: publish batch-1090-1115-r002`。

2026-10-06 00:12 的 `git ls-remote` 确认 GitHub 生产分支仍指向该 SHA；Yupeng HEAD 相同。前一公开批次为 `317f84612597f17fdb90f5631f537e9f834cd60a`（1,090 道），不能再当作下一批的前次计数。

1,115 道交付证明：

`B/operations/corpusctl/batches/batch-1090-1115-r002/verify-public/result.json`

本次读取状态为 `public_exact_commit_full1115_restored_verified`，commit 为上述 SHA，verified_count 为 1115，public_files_verified 为 20321。本轮读取既有证明，没有重新执行全库恢复检查。

远端未提交的已跟踪文件恰为：

- `handoff/yupeng/CONTINUATION_CURRENT.json`
- `handoff/yupeng/PRODUCTION_QUEUE.json`

本次交接分支以真实生产 SHA 为父提交，仅保存上述两份文件的现场字节与根目录两份交接文档。`PROJECT.md` 仅在本地更新。生产工作树和生产分支不切换，队列 7 道不计为公开交付。交接分支是工作快照，不能用于覆盖未来更新的运行状态。

本地原始读取记录位于 `.work/human-proof-corpus-control/handoff-20261006/snapshot.json`；完成提交推送后，同目录的 `delivery.json` 记录交接 commit、文件清单和验证结果。

## 4. 现场状态的权威入口

| 需要知道什么 | 路径/命令 |
|---|---|
| 当前队列、合并数、下一批 | `B/repo/handoff/yupeng/PRODUCTION_QUEUE.json` |
| 续接说明 | `B/repo/handoff/yupeng/CONTINUATION_CURRENT.json`；其中旧过程说明需结合本交接和真实队列 |
| controller 身份 | `S/owner.json` |
| 队列与登记作业综合状态 | `B/repo/corpus-work/corpusctl status --json` |
| 运行记录 | `S/runtime.sqlite` |
| 来源调度配置 | `S/FLOW.json` |
| 全局禁止准入项 | `S/source-holds.json` |
| 服务状态 | `systemctl --user show corpusctl.service -p ActiveState -p SubState -p MainPID` |

以真实结果为准，不拿旧 `running`、退出码 0、READY 或工程测试代表数学材料完成。旧失败作业可能仍有保留记录；只恢复当前确有必要的材料，不把历史失败全重跑。

已发现两处旧字段：`CONTINUATION_CURRENT.json.new_pending_main_ids` 仅列 5 道，缺少后来准入的 819、915；真实队列是 `PRODUCTION_QUEUE.json.queued_new_root_admitted` 中的 7 道。队列中的 `first_release_target: 1065` 也是历史字段，当前目标由 `corpusctl status` 计算为 1140。本次保存 JSON 原始现场字节，不为美化快照改写运行数据；接手时不得使用这两个旧字段覆盖真实队列或目标。

## 5. 先处理这十份已有产物

以下 READY 文件在本次现场读取时**均存在**；这只确认可接续入口，不代表材料最终准入。路径前缀为 `B/candidates/source-pipeline-`，产物路径以 READY 内容为准。

| 题号 | READY 相对后缀 | 先前已知未决内容 / 禁止重复事项 |
|---|---|---|
| 624 | `v3/r003/624/READY-root-r002.json` | 技术完成；只补固定 Thm5.5 的实际剩余机制难度结论，不能借后续应用抬高难度 |
| 2414 | `v3/r003/2414/READY-root-r001.json` | 技术完成；补完整材料结论。借用 Figure1 已核对为示意，不能声称拥有第三方图片许可；正文保留必要内容和准确指针 |
| 2515 | `v3/r003/2515/READY-root-r001.json` | 技术完成；待生产端补来源材料准入结论，不重新编译 |
| 820 | `v3/r004/820/READY-root-r005.json` | 技术完成；待补固定端点引理的材料/难度结论 |
| 822 | `v3/r004/822/READY.json` | 固定渐近命题；821 的 t=0 问题不自动扩大成 822 hold，按其实际范围判断 |
| 909 | `v3/r004/909/READY.json` | 技术完成；外部 eikonal phase 是明确前提，不冒充本题自证内容 |
| 910 | `v3/r004/910/READY.json` | finalizer 已完成且非幂等，禁止重复运行；直接读取现成最终结果 |
| 916 | `v3/r005/916/READY.json` | 已有大部分来源判断；与 917 同篇，核对共享来源字段并补语义区别后准入 |
| 917 | `v3/r005/917/READY.json` | 先前材料记录尚缺原生行 866–960 的必要核对；只补缺口，不重读整篇。原文常数印刷问题按固定结论范围记录，不改证明 |
| 925 | `v4/r003/925/READY-root-r003.json` | 技术完成，参考文献修订已完成；待补材料结论，不重新编译 |

表中未决说明来自生产交接记录，本轮没有重新审阅数学原文。先读取已有来源结论、BODY_LOCATORS、source_map 和具体 READY 指向的产物，只补缺失部分，不设第二道全文复审。

同一来源共用 `source_id` 与 `author/work/source_url/source_version/retrieved_at/license/license_path`，许可正文一致。第二个同源题明确记录与已有题的数学内容差别。已有队列中的 818/819 共享来源的对齐已处理，不回滚。

## 6. 后续现成输入与目录修复

v4 各路已有 `SOURCE_PACKET.json` 和 cached-originals，无需重新下载：

- r003：924、925、926、927、928、929、930、931、932、933。
- r004：939、941、944、947、948、951、994、1001、1002、1055。
- r005：1056、1057、1058、1059、1060、1061、1062、1063、1064、1065。

v4 输入曾误落到 v3，现已修正实际 30 个未来路径并保留旧输入；修复记录为 `S/following-cache-r002-workspace-correction-r001/result.json`。不要再次搬运、删除或重置。925 已产生上表 READY；其他输入不按候选数量算完成。

已有扩源缓存 `B/source-cache/new-source-intake/arxiv-math-oai-r001/`：先前元数据记录包含 434 个未分配来源候选，另有 `native-relay-r002` 下两篇精确版本原生包 `1907.01091v3`、`2102.07928v4`。它们没有题号和最终选定证明，贡献合格计数 0。用完当前储备后再接续扩源，先看既有记录，不重抓同一包。

## 7. 具体 hold：保留原因，逐题跳过

本次全局 `S/source-holds.json` 共 21 项，以下为简要翻译，完整原始理由以该文件为准：

| 题号 | 当前原因 |
|---|---|
| 1709、1713 | 既有来源歧义；全局记录未提供更细解释，不臆造原因 |
| 2314 | 原始伴随关系符号冲突 |
| 1480 | 逆指标含义不清 |
| 1443、2244、2282 | 未达到既定难度准入标准 |
| 1907 | 原材料不完整，未合格 |
| 1791 | critical T_k 原文不清，另有 symc1 文献对应问题 |
| 2254 | 勘误和版本关系未解决 |
| 2325 | 必需 Lemma16 参数/尺度与 Lemma18 行列式表达不一致 |
| 2378 | 固定 Thm3.2 为已给 Prop3.1 后的直接系数比较，剩余难度不足 |
| 1476 | 必要构造中的扩展 netflow 坐标、符号与边约定不明确 |
| 1623 | 新代换引理端点 p+/p- 在陈述、证明及调用中不一致 |
| 622 | 固定 Thm3.4 的已给前提之后，仅剩普通群作用/阶数机制 |
| 814 | 固定 Lemma3.6 的已给前提之后，仅剩一阶矩、尾界与截断 |
| 815 | 固定 Lemma2.10 的剩余相对对偶及杯积机制不足以证明更高难度 |
| 914 | 固定曲面构造引理在已给曲线族之后，剩余标准 cobordism/handle 计算难度不足 |
| 920 | 固定 Prop2.4 的 trace、base change 等已给前提后剩余机制难度不足 |
| 921 | 固定 Prop3.2 的单项式分组、除法及计数机制难度不足 |
| 821 | 固定 all-t>=0 命题的 inverse clock 在 >= 与 > 约定下 t=0 对象不同，不能偷偷删除 0 或改定义 |

另有尚未提升为全局结论的生产端 hold：813（剩余难度）、912（闭集基/常数类与有限 ends 计数歧义）、913（固定 Thm6.1 剩余难度）、918（固定 1.9(2) 剩余难度）。读取各候选目录已有 HOLD 记录；本轮未重新核验或解除这些项。不要把它们写成已通过。

旧的绿编译、QA 和证明原件仍保留。工程通过不能覆盖上述来源或难度 hold；不同命题要另按真实题目处理，不能偷换被 hold 的固定题意。

## 8. 接手顺序、已知陷阱与验收

1. 读取现场 status、owner、服务和必要作业状态；只复用当前任务，不重启全套服务。
2. 三路补上述 READY 缺项，控制器复用现有检查直接准入；同步处理 v4 输入。
3. 队列满 25 后走 `corpusctl batch`，读取真实批次返回值，再用本地 `controller_publish_pipeline.py publish-batch` 发布。完整命令在 `DEEPSEEK_PROMPT.md`。
4. SSH 失败先看实际状态和回执再续跑；服务查询必须 `--user`。远端 `rg` 可能不可用，可用 grep/find；无须安装工具。GitHub 本地代理失效时可仅对当前 Git 命令指定 `-c http.proxy= -c https.proxy=`，不改全局代理。
5. `admit_native_frozen.py` 有旧 actor 硬编码且按 DOI 工作；不要对新身份或无 DOI 的 arXiv 包盲用。现有 `corpusctl admit` 需要 admission decision，不能直接传 READY。
6. 不重复执行 910 finalizer、不重复修 v4 目录、不按旧 runtime 失败记录重放已有产物、不删除锁、不修改公开计数来“对账”。

第一阶段是下一批真正公开交付，若状态不变即 1,140；后续持续至 30,000。主库合并、公开恢复、待处理候选各自计数。每批用北京时间报告实际新增和吞吐，没有新增报 0，无法核实报未知。取材与工程成功均不冒充数学准入或公开交付。
