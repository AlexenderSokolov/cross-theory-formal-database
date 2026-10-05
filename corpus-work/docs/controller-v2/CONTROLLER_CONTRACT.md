# 题库本地总控执行契约 v2

状态：设计会话交付的实施规格；不代表代码已部署或生产已恢复。
执行会话：`01a10a85-17a8-78a3-aee8-eccff57a9d47`，`gpt-6.1-sol / medium`。
本契约与配套schema、验收场景共同实施；用户最新指令优先。现行题证标准仍由仓库human-proof-corpus skill负责。

## 1. 责任与起点

本会话只设计和审查本契约，执行会话负责代码、测试、部署、采集、准入与发布。设计文件放独立目录；设计会话不修改执行会话的核心程序、运行台账或主库。执行者将这三份文件随明确文件清单提交，更新唯一现行本地控制交接入口，旧dot入口标为历史。

Yupeng根目录`/disks/sata1/yupeng/human-proof-corpus`下保存repo、cache、TeX、编译产物和SQLite。本地只保留控制脚本、GitHub身份和现有Git relay。原会话及旧心跳20-1000保持暂停；新会话的每2小时汇报已创建，automationId=`2`，不得重复创建。

已核实起点：主库本地=公开=1065，8题已准入待合并（1819、1820、1379、1477、2252、2283、2246、2383）；1793/2286技术READY未准入，2415技术闭环完成但缺READY/准入。1065公开恢复数据提交为`347369e58e67feffcd520e56bf0f5ae6b95f7129`；实施前重读实际HEAD，保留并发修改。

首个生产验收为1090公开恢复，然后连续1115、1140并推进30,000。1065基线不重新接收、编译或审计。技术校验不作独立数学正确性认证。

## 2. 权威数据：每种事实只设一个来源

| 对象 | 权威位置 | 职责及边界 |
|---|---|---|
| 主库题证 | 当前queue指向的冻结package、manifest、INDEX、全文SQLite | 保留现有schema与完整tex_content；运行台账不能代替主库 |
| 已准入、当前基库及计数 | `PRODUCTION_QUEUE.json` | 只有总控明确admit才能增加待合并记录；merge/公开验证分别更新本地/远端 |
| 作业、claim、尝试与进程 | 现有`runtime.sqlite` | 执行事实；不保存第二套合格计数，不凭退出码推导准入 |
| 来源块计划 | `operations/corpusctl/FLOW.json` | 已批准的互斥block、候选范围、缓存输入和明确后继 |
| 工作者结果 | 各attempt的`JOB_RESULT.json` | 对全部本次负责ID逐一交代ready/unfinished/hold及现有证据引用 |
| 活跃批次 | queue新增可空的`active_batch`引用 | 同时最多一个从冻结到公开验证未结束的批次；批内状态取自身回执 |
| 最新公开版本 | queue新增`last_publication`引用 | 绑定已有完整公开恢复result、commit、count、batch_id |
| 控制者 | 现有`owner.json`，增加generation | 防止旧控制会话继续派工或共享写入；不是新增凭据系统 |

`pending-publication.json`可以保留为派生兼容显示，不能成为另一处可单独覆盖的权威。旧`first_release_target`只标历史；当前目标由公开数+25计算。统计时间统一UTC存储，用户汇报显示Asia/Shanghai。

主库和queue既有字段兼容保留；新增运行协议使用schema_version=2及record_type，不要求把旧题库schema改成2。配套schema的queue_extension定义只验证新增控制字段，不创建第二份queue文件。不把a/c、跨理论等研究标签加入任何题目记录。

JSON Schema是接口规格，不强制安装新的运行依赖；可用现有依赖或标准库实现等价校验，并用配套正反示例证明一致。schema不负责跨文件身份、实际证据、语义唯一性或状态副作用，这些按正文和验收场景实现。

## 3. 粗粒度派工，逐题记录

一个worker连续处理一个来源块，通常10—20个候选。**不改成每题一个模型会话，更不按下载、转录、编译逐阶段拆会话。** 已继承的短块按现状续接。

每个block固定`block_id、enabled、units、next_block_id`。每个unit固定字符串`problem_id、work_key、source_packet、workspace`。ID原样保留前导零，不转成整数；未分配候选键不能冒充稳定ID。source_packet只引用真实缓存/目录记录，不能由worker猜URL、编号或版本。

登记FLOW时检查block_id唯一、后继存在且无循环、跨块unit ID及作品范围互斥。同一块可包含同作品的多个已明确候选，不能由调度程序把它们自动认定为不同合格题。

作业输入固定`job_id、attempt_id、block_id、unit_ids、work_keys、workspace、stages、result_path`，启动前持久化。同JOB_ID和相同输入重发只返回原任务；输入不同拒绝，不重置原任务。实际进程同时核PID、启动时间、cwd/明确工作目录argv，保留子进程身份。

本版本中job_spec包含的一次attempt整体不可变。网络回应丢失、重复run/resume沿用同job_id/attempt_id。只有前次已确认终止、需要新尝试时，才预先持久化新的确定性job_id/attempt_id并通过previous_job_id链接原作业，原子转移本次承接的claims；同块计数器用于命名，不在每次重发请求时生成新ID。配额重试也遵守这条规则。它是块尝试，不是每题或每阶段新建模型任务。

`work_keys`在claim/adopt/revise等入口统一规范化并事务检查：数字ID统一为`id:<原字符串>`；作品键取目录中的稳定work_key，DOI只做明确的前缀/大小写标准化。未知别名必须查目录，不猜作不同作品。同一作品只能有一个活跃写者。同作品多个明确候选由同块处理；不因支持引理存在而自动增加题号。

每个阶段产生可复用产物时更新该题的简短检查点，引用原compile/QA/SQL/item回执，不复制一层新报告或散列清单。可恢复阶段固定为：

`cached → source_review → normalized → compiled → page_qa → projected → item_passed`

其中source_review包含精确命题、必要core、难度、版本和组件许可初筛；数学不清或难度不足在构包前hold。引用与纯格式宏在编译前就绪。compile helper内部真实稳定passes沿用原协议。原件只读，冻结final不可原地修改。

## 4. JOB_RESULT：进程、材料、准入必须分开

JOB_RESULT绑定`job_id+attempt_id+block_id+精确(problem_id,work_key)集合`。每题只能有一条结果；遗漏、重复、额外ID、作品错配或旧attempt结果拒绝。

| disposition | 必需内容 | 控制器动作 |
|---|---|---|
| ready_for_review | 固定revision/package/READY/item报告/build/receipts/QA/来源定位/许可/H理由引用；last_completed_stage=item_passed | 核实已有最终证据与当前修订对应，进入待材料准入；不重跑绿门禁 |
| unfinished | 最后已完成阶段、现存产物、明确next_stage/next_action | 同块下一attempt只承接未完成ID，从该阶段继续 |
| source_hold | 具体reason_code和原文/许可/难度/重复疑点证据 | 隔离该题，继续其它候选；不算工程失败或合格 |
| engineering_hold | 具体错误、失败日志、已有安全检查点及修复动作 | 总控安排有限修复；不把缺输出或模板错误写成来源hold |

stage名是检查点，不是每阶段新模型任务。工作者在结束前写一个覆盖本attempt全部ID的结果；未处理的ID必须列unfinished，不能遗漏。结果经临时文件原子替换发布。

退出0但缺结果、结果不合法或只有自然语言FINAL：执行状态为`needs_recovery`，原因`result_missing/result_invalid`；不成为READY。有效结果被收取后执行状态可为`collected`，另记result_status=`complete`或`partial`。partial必须续接，不能假装整个block完成。

一个块所有unit都有ready/source_hold/明确engineering_hold去向，且没有活进程或未知执行结果，才可标accounted并幂等登记next_block。仍有unfinished时优先续同块。worker不得越界自领新作品。后继缺失则总控从已缓存候选池准备新块，不能让服务编造任务。

初始3个有效工作槽；不盲目启动旧launcher。待材料审核积压达到25时暂停领取新块，先清理准入/发布；健康在途任务继续。1090后按实际吞吐和限流情况试增服务器工作槽，上限8，失败回退到最后稳定档。

## 5. 仅总控准入，复用既有检查

admit继续使用现有字段：problem_id、package、build_root、receipt_root、accepted_report、owner_final_ready、accepted_H、difficulty_reason、material_basis、semantic_basis、rights_basis、admitted_by和decision=admit。

准入前核对：原命题假设/量词/常数、完整对应的人类证明、新局部核心覆盖、2—4句具体H理由、逐组件许可、语义重复、正确引用映射及真实最终技术证据。技术证据检查复用已有函数，不再重新编译或运行同一个item gate。缺少合并器要求的兼容投影字段时，在候选范围解决，不能拖到满批后才发现；不新增独立SHA工程。

引用映射须来自原版BibTeX/原刊参考条目，禁止按字母序猜BibKey。原文关键不清即hold，不能替作者修证明。完整人类证明、H门槛、许可、唯一性标准不因模型档位或配额降低。schema通过只说明结构合法。

导入现有8个已准入条目只登记运行引用，不能重复admit。1793/2286/2415仍需明确材料决定。已有hold不能因新worker得到技术绿而自动解除；解除必须记录新的来源依据和明确总控决定。

## 6. owner与进程恢复

owner记录固定`owner、generation、previous_owner、updated_at`。旧文件缺generation按0读取，仅迁移一次。共享写命令必须带调用者owner与generation；不能默认读取最新owner并替调用者充当它。

claim/run/resume/adopt/revise/collect/serve/admit/batch及发布共享写入前，在现有controller lock内检查身份。owner交接用相同锁CAS递增generation。serve启动绑定身份，每轮及派工前重新检查。只读status不初始化/迁移数据库、不改变任何状态。

已启动worker仅可保存自己当前attempt的结果。交接后旧控制器不能派发新阶段、准入、合并、提交、push或更新计数；由新控制者收取合法检查点。

涉及发布与owner交接时，统一锁顺序为publication lock→controller lock。只有controller lock的操作不得在持锁期间再获取publication lock。跨本地push的publication lock由一个持有flock的短小SSH guard进程维持，沿用现有SSH，不引入锁服务；本地驱动在外部写期间保留该guard并监测它。guard/网络丢失后停止发起后续写，记录当前外部写结果为unknown并读取远端协调。

交接不得越过尚在运行或结果未知的外部写：须确认原本地发布进程已终止，或其阶段结果已明确，再获取publication lock进行CAS。只看到远端仍为expected base，不足以证明旧push已结束。若原进程状态无法确认，停在needs_recovery并说明实际缺口。新owner在锁内更新publication.actor，保留started_by和actor_history；batch/parent/tree/commit等内容身份不变，随后接续未完成阶段。它是普通受信控制会话的交接规则，不是防御任意SSH用户绕过程序的安全框架。

| 事件 | 固定处理 |
|---|---|
| 启动请求回应丢失 | 查同JOB_ID与真实进程；不能据超时再开一份 |
| runner死、子进程仍活 | orphan_running，占用claim与容量；不转移、不重启 |
| 父子均死、阶段结果未知 | needs_recovery；读取该阶段已有回执/日志后明确复用或续接，不从头重跑 |
| 已提交阶段之间退出 | 从next_stage继续；已成功阶段不执行第二次 |
| 明确模型限流且命令未执行 | 60/120/240秒退避；不杀健康任务、不换账号绕配额；连续失败进入配额等待，由总控后续检查 |
| 有效partial结果 | 新attempt只处理未完成子集；原attempt和已完成题证保留 |
| 无任何产物 | 工程续接/修复工单；不是来源hold，也不是完成 |

日志和失败材料保留，不批量删除。普通工程修复由总控自主进行，不反复向用户申请同范围批准。

## 7. 批次屏障与事务边界

恢复生产后的新批次只有在`active_batch=null`、local_count=remote_count且待合并准入数达到本批大小时才能冻结。初始batch_size=25，按queue已有顺序取最早25项，额外已准入项原样留给下一批；不是丢弃。下一目标显示remote_count+本批大小。真实100题统计完成后才能把batch_size改为100。

最终批大小为min(batch_size,30000-remote_count)，达到30000即停止新派工/合并并进行最终验收；超过剩余数的已准入材料保留，不加入本次主库也不删除。因此当前下一批精确为1090，随后1115、1140，不随队列同时到达26项而漂移。

冻结首先在同一controller lock下向queue原子写入active_batch意图，包含batch_id、batch_dir、frozen_base（原base对象）、expected_count、incoming_ids和created_at；然后生成同一批次的spec/review，之后才组装。若意图已写而spec未完成，按frozen_base和精确incoming_ids从不可变准入行重建，不能把后来新准入行加入该批。准入行只在merge成功后消费。冻结的base、incoming_ids、spec和材料review不可被新准入改变。新准入继续加入queue，留给下一批。

last_publication固定包含batch_id、commit、count、result_path，引用完整公开恢复result。active_batch与last_publication的更新同queue原子提交；不用另一份可覆盖指针替代它们。

阶段为：

`frozen → merged → release_prepared → git_staged → commit_ready → pushed → publicly_verified → reconciled`

active_batch在reconciled之后才清空。任何未结束阶段都阻止第二次冻结/合并，包括尚未merge的frozen批。状态来自已完成回执与实际结果，failed/interrupted是步骤情况，不是要求重建整个批次。

核心反例：local=1090、remote=1065、queue=1，只能恢复1090的发布，不能合并1091。不得再用local-remote+queue作为下一批阈值。

merge成功只更新local/base并移除本批incoming_ids，保留后来加入的行；公开完整恢复成功才更新remote。重复同批回调幂等；不同/陈旧批次回调明确拒绝，不能静默覆盖更高计数。local>remote却无active指针时，仅从既有merge回执恢复唯一身份；不唯一就报告冲突并保持材料，不能猜测。

controller lock保护短状态写；另用同一批次的发布互斥锁保护发布推进。长下载和恢复不应长期阻塞不相关候选准入，但任何时候不得同时推进两个批次或覆盖发布身份。

## 8. 本地发布总入口与恢复矩阵

执行者提供一个本地`publish-batch`入口，参数固定为SSH别名、远端batch路径、actor(owner/generation)及本地relay/cache根。具体实现在现有publish辅助脚本外加薄编排；不要要求操作者每批手工写spec/review/commit/verify命令。

入口按以下顺序调用既有工具：服务器准备release → 显式文件staging → commit/bundle → 本地取bundle并正常push → 服务器精确公开恢复 → queue对账。GitHub身份只在本地。各阶段使用固定batch/publication记录，参数从记录读取。

publication记录包括batch_id、当前actor(owner/generation)、started_by、actor_history、remote/branch、expected_remote_base、server_parent、expected_tree、target_commit、bundle路径、固定previous-public引用、stage和各阶段回执路径。Git tree/commit是原生Git身份；不另建签名/散列系统。

进入git_staged时，必须已持久化server_parent、expected_tree及批次标记，然后才能执行commit；进入commit_ready时必须已有target_commit和固定bundle路径。不能等commit返回后才首次记录用于找回它的parent/tree。每个外部写尝试保存本地进程身份/启动时间和终态，供交接时判断是否仍在途。

| 丢失或失败位置 | 同批次恢复规则 |
|---|---|
| staging | 按既有文件清单核对并补缺失/变化路径；临时文件+原子替换，不改共享hardlink原件；不混入无关已暂存文件 |
| commit回应丢失 | parent/tree/批次标记吻合则认领已有commit；HEAD仍是parent才提交；其它变化先整合，不能再盲提交 |
| bundle回应丢失 | 使用固定target_commit和expected base恢复bundle，不使用移动的HEAD |
| push回应丢失 | remote=target视为已推送；remote=expected base正常重试；其它远端前进保留并整合，禁止force |
| transport部分下载 | 同commit/filelist/previous身份才接续；已有完整文件复用，补缺失/损坏文件，不重新下载全部 |
| 文件完成、ledger未写 | 按已有格式确认文件后补一条记录；计数按唯一path重算，不累加重复数 |
| SQL/资产恢复中断 | 成功逻辑步骤复用；部分恢复保留现场，核对能否复用；旧helper不支持部分目录时新建该阶段attempt，不重传完整来源 |
| 完整verify成功、queue未写 | 认领同一公开恢复result，仅补queue/指针；重复调用不增加计数 |

网络临时错误用有间隔的有限重试。改变commit、文件清单、来源版本或目标身份时，禁止复用旧输出目录冒充同次恢复。每次attempt保留日志。单次HTTP失败不要求从整批开始，也不能忽略损坏文件。

## 9. 增量资产和必要验收

沿用已验证的schema2 validation chain：旧公开验证archive按原路径/原字节复用，新批只打包incoming IDs的build/receipts为delta；如有合法替换，沿用已有显式override规则。主库SQLite暂保留完整gzip分段，不改变全文表结构。

公开文件清单覆盖恢复所需的旧archive与新delta；按已验证清单跳过未改文件staging。`RECOVERY_CURRENT`和public_plan的第四个恢复命令必须同步使用正确schema1或chain helper；原有五个逻辑恢复步骤及公开proof结构保留。旧archive下载字节数应为0，新增下载主要为delta、SQL及变动元数据。

不增加一次多余本地恢复或同一个aggregate。合并aggregate与公开恢复后的完整gate是两个不同必要边界，不能为了宣称“一次检查”省掉后者。

按配套acceptance-cases.json实施针对性测试；合成场景不计数学产出。新代码未涉及的绿色测试不例行重跑。1090真实批次验收后连续1115、1140；用真实100题分开测量来源加工、返工、准入等待、建库和发布，不用74.6秒合并时间外推采集速度或完成工期。性能窗口在本契约生产恢复时开始；启动时已完成的8题及其它继承阶段单列，不能把它们的复用速度当作新题采集吞吐。对没有同口径阶段计时的数据明确标未知。

## 10. 报告、发布文档与实施完成定义

status/report必须分列候选、来源准入、规范化、技术item通过、root准入待合并、本地合并、公开恢复交付及hold；不能把文件、PID、FINAL或工程fixture计为题目。运行台账不能无证据地把停止文件中的旧状态当实时状态。

每2小时日程ID2只向执行会话注入汇报任务，不另启worker。报告本期增量、累计、等待、hold、耗时和下一步；重大阻塞及时说明。本地离线时已启动服务器任务可继续，控制/发布待重连，未知进度不得猜测。用户暂停后必须停生产，日程不得自行恢复。

实施完成须同时证明：有效结果驱动同块续接/后继派工、旧actor被拒、未发布屏障、单阶段恢复、真实1090公开恢复、无新人工派工继续下一批。只通过schema或单元测试不能宣布连续生产已完成。
