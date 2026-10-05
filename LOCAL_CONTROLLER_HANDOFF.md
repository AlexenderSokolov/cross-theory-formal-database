# 高级数学人类证明题库：本地总控入口

现行目标为30,000道合格唯一题。总控会话为01a10a85-17a8-78a3-aee8-eccff57a9d47，模型gpt-6.1-sol / medium。本机只控制SSH和GitHub relay；题证、缓存、编译、SQLite和公开恢复均在Yupeng。

正文、schema与场景规格位于[controller-v2](corpus-work/docs/controller-v2/CONTROLLER_CONTRACT.md)。schema成功不代表连续生产验收；真实公开恢复成功才增加交付数。

## 当前边界

实施起点本地合并1065、远端可恢复1065；8份已准入冻结包1819、1820、1379、1477、2252、2283、2246、2383待合并。1793、2286技术READY待材料准入；2415已有绿色材料但缺READY及准入。这些均不能自动增计。1791、2244、2282、2254、1907维持原具体hold。

本入口初版处于整改验证阶段。owner接管、服务恢复、真实1090/1115/1140及100题性能窗口状态以CONTINUATION_CURRENT、queue、runtime与公开恢复回执为准，不能从此文件或服务active推断已产出。

## 固定位置与身份

- SSH：Yupeng-orx，使用本地现有身份，BatchMode=yes、ConnectTimeout=10、ProxyCommand=none、ProxyJump=none、ClearAllForwardings=yes。
- B=/disks/sata1/yupeng/human-proof-corpus，repo=$B/repo，PY=$B/runtime/python/bin/python，CTL=$B/repo/corpus-work/corpusctl。
- 主分支corpus-progress-20261001，GitHub仓库AlexenderSokolov/cross-theory-formal-database。发布前读取最新远端，保留并发成果，不强推。
- 总控actor为owner=local-controller-01a10a85，首次接管generation=1；调用者显式提供，不能把当前owner读出来冒充它。
- GitHub认证只在本地；relay位于本地轻量控制目录relay.git。服务器网络请求按命令直连绕过失效loopback代理，不改变全局配置。

## 执行闭环

FLOW.json保存互斥来源块、真实缓存与明确后继。初始3个有效worker，每块连续10—20候选，继承短块按原断点续接；不用每题或每阶段模型任务。JOB_RESULT绑定job/attempt/block及精确ID+work_key，逐题区分ready_for_review、unfinished、source_hold、engineering_hold。缺结果或自然语言FINAL不能晋级。

总控材料准入后，queue按FIFO取25个净新增，额外已准入项留给下一批；active_batch冻结意图先原子写queue。未公开对账的active批次期间来源加工和准入可继续，但禁止第二次合并。最终批截到30000，剩余材料保留。

固定publish-batch入口从publication记录读parent/tree/target/previous，完成服务器prepare与staging、commit/bundle、本地push和服务器精确公开恢复。跨本地push持SSH publication flock guard，锁顺序publication→controller。中断只恢复受影响阶段，成功输出复用；未知外部写先确认终态及远端。

每题复用原compile-isolated、canonical投影、最终item及必要全页QA，保持原题证与局部新core、具体H理由、逐组件许可与语义唯一性。已有绿色且未改变的材料不重编或重复item。引用映射源于原刊实际参考条目，不能猜编号或BibKey。不能补写证明或改作者假设结论。

1090真实交付后自动续1115、1140。只有实际合格吞吐提高且无持续限流才试增工作槽，上限8；满100题性能窗口前保持25题批次。新题来源加工、返工、准入等待、合并和发布分开计时，继承成果单列。

## 统计、接续与历史

PRODUCTION_QUEUE.json是准入/合并/公开计数权威；runtime.sqlite只记执行。last_publication指向上一实际公开恢复result；下一轮初始previous为$B/operations/corpusctl/batches/batch-1048-1065-r002/verify-public/result.json。

每2小时汇报日程已经创建：automationId=2，目标为本总控会话，Asia/Shanghai显示；不重复创建，不另起worker，不恢复旧会话/旧Goal/旧心跳20-1000。重大阻塞及时报告；无新增准确写0，本地离线期间不猜进度。

DOT_HANDOFF.md及DOT_TRANSFER_STATE.json只作历史停止快照。dot方案已经放弃，不重建dot任务。旧本机题库、已有材料和失败现场保留，不批量删除。只有实际公开恢复30,000题并完成全目标验收，才结束持续目标。
