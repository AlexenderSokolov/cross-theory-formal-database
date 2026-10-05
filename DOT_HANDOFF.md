# Your dot 接管入口

## 目标与执行位置

在既有成果上持续生产至 **30,000 道合格、唯一题目**。每题包含作者完整题目、完整人类证明与必要新局部核心，可编辑 TeX、实际隔离编译、具体 H1/H2/H3 难度理由、可追溯来源与再分发依据，并进入 INDEX 和全文 SQLite。只有公开远端实际恢复成功才增加交付数。

**控制端是 Your dot 自己的云电脑，计算端是 Yupeng。** 不需要另找一台常驻个人电脑。dot 的新任务先读本文件，再执行 `corpusctl status --json`。SSH 地址、密钥和 GitHub 登录保存在云电脑私有配置，不能写进公开仓库。当前个人电脑可连接 Yupeng，不证明 dot 云电脑已可连接；尚未从 dot 实测连接前，控制 owner 保持现任，不能宣称已接管。

- 仓库：<https://github.com/AlexenderSokolov/cross-theory-formal-database>
- 分支：`corpus-progress-20261001`
- `B=/disks/sata1/yupeng/human-proof-corpus`
- 仓库：`$B/repo`；Python：`$B/runtime/python/bin/python`
- 命令入口：`$B/repo/corpus-work/corpusctl`
- 执行准则：[项目 skill](corpus-work/.agents/skills/human-proof-corpus/SKILL.md)、[PROJECT.md](PROJECT.md)
- 最新计数与冻结准入包：[PRODUCTION_QUEUE.json](handoff/yupeng/PRODUCTION_QUEUE.json)。运行台账位于服务器 `$B/operations/corpusctl/`，不是题库全文 SQLite。

## 当前接续点

**最新已核验：公开主库与本地主库均为1065题，数据提交 `347369e58e67feffcd520e56bf0f5ae6b95f7129` 已实际公开恢复；下一检查点1090。** 当前待合并准入与READY分别读取queue和CONTINUATION_CURRENT，不沿用下段实施起点。下一公开恢复的`--previous`使用`$B/operations/corpusctl/batches/batch-1048-1065-r002/verify-public/result.json`。

已接续来源块r003、r004、r005，各自OWNER给出互斥范围；1791原文关键记号/书目hold，不能从技术READY晋级。

2026-10-05 实施起点：公开主库 **1040**，本地已合并 **1048**，另有 **11** 题已准入待合并，累计准入1059；1065检查点还需6题。以实际 status、queue、manifest 和公开恢复报告更新这些值。七份独立公开备份与主库重叠，不能再次相加。975＋40遗产接收已完成，不重复接收；1907和hold不计数。

本地基库是 queue 的 `base.package`，不是仓库中历史未跟踪的 `editable-corpus/corpus.sqlite`。冻结题1662、1663、1665、1706、1707、1708、1710、1712、1714、1740、1741的包、最终编译、逐题报告和准入理由全部在queue中，复用这些成功结果。

真实待处理来源块：`$B/candidates/native-source-continuous-r002`，IDs为1788、1789、1790、1791、1793、1794、1795、1796、1797、1819。1788已有两遍16页编译，接QA/投影/最终门禁，不重复下载。executor目录保存当前任务与真实退出日志；通过status识别是否仍在途，不根据旧PID文件重启。

1581现已修复并冻结在`$B/candidates/native-source-resume-r006/1581/READY.json`，页码805–830及13条书目已对应原刊，真实2passes/23页QA/最终item通过且已准入。旧r004保留，不再从旧错误版续接。1709、1713、2314、1480等来源hold不能自动重试或数学补写。更详细的已完成材料路径见queue和对应READY。

## 固定生产循环

1. `status --json` 对账任务、活进程、阶段、准入队列和下一动作；服务重启先收取旧任务。
2. 按已缓存作品领取10—20候选来源块，排除主库、准入项、hold和在途owner。固定JOB_ID，同请求重复发送不启动第二份。
3. 工作者仅写自己的目录：忠实转录、完整引用、许可、难度理由、实际编译、页面QA、必要小包投影及最终一次`--item`门禁。遇具体hold继续独立候选。
4. `collect`只进入待准入。dot核对关键假设、题证匹配、新局部核心、难度、许可和语义重复，保存明确准入决定后调用`admit`。
5. `batch`消费已准入项。相对上次公开主库满25个净新增时，一次组装、一次主库rebuild、一次aggregate。未满继续采集；不逐题合并。
6. `publish`准备明确文件、数据库与恢复材料及增量Git bundle；dot云电脑用自己的已授权GitHub身份正常推送。`verify-public`实际从确切公开提交恢复，再更新交付数。
7. 1065交付后自动接1090、1115、1140。完成100题实测后按吞吐决定扩大至最多8个有效工作槽、100题发布；每500题完整对账。

运行状态为待领取、执行中、待准入、已准入、已合并、待发布、已交付。FINAL存在、退出码0或编译成功都不能直接晋级。工程失败、来源hold、SSH不可达和模型限流分别记录。只续未完成阶段；模型限流退避并减少新启动，不杀健康任务，不爆发重试。

## dot云电脑首次连接

在其私有SSH配置中设置别名`corpus-yupeng`和可达主机、用户、端口、专用密钥。个人电脑的私网地址不能假定云端可达；先验证实际可达通路，不擅自开放服务器端口或复制现有私钥。

```sh
ssh -o BatchMode=yes -o ConnectTimeout=10 corpus-yupeng \
  /disks/sata1/yupeng/human-proof-corpus/repo/corpus-work/corpusctl status --json
gh auth status
```

连接成功后，读取实际运行状态并续接已有JOB_ID。发布身份在云电脑登录，Yupeng不保存个人GitHub凭据。正式切换时使用 `corpusctl owner --expected-owner current-session --set-owner dot` 交接命令，只保留一个总控与发布者；旧桌面心跳保持暂停。云端网络或身份未就绪时，服务器已启动工作继续，发布保留待处理状态。

首次任务：

> 接管高级数学人类证明题库。读取DOT_HANDOFF.md并执行status，接续现有阶段，消费已准入队列。完成1065题真实发布和公开恢复后自动继续到1140，再按目标推进30,000。不得重新接收975＋40遗产，不重验未改变的合格材料。仅在实际阻塞需要人处理时通知。

## 授权、边界和汇报

用户已授权正常范围的来源下载、转录、校验、建库、commit/push和同仓库Release，无需重复审批。先把官方PDF、公开网页与可取得原生TeX缓存到Yupeng，再加工；缓存网页与运行日志保持私有。公开发布逐组件核实许可。

持续执行Stop That Shit：不调用MCP操作路径，不追加SHA专项、目录散列、多层pins、重复整库扫描或新的平台；现有工具内部兼容字段自行处理。禁止批量删除、强推、覆盖他人提交、泄露凭据、运行未知上游脚本、生成补证和拆routine引理凑数。无关插画不进入题证。

只汇报真实新增合格数、主库合并数、远端可恢复数、吞吐及确切阻塞。工具测试、PID、来源文件数、READY数量都不是交付数量。每次中断保存当前提交、运行JOB_ID、阶段和下一条命令，后续仅靠仓库与服务器状态即可继续。


## 固定命令示例

```sh
B=/disks/sata1/yupeng/human-proof-corpus
CTL="$B/repo/corpus-work/corpusctl"
"$CTL" status --json
# stages.json: [{"name":"source-work","argv":["..."],"stdin":"...TASK.md"}]
# TASK只指定已缓存、互不重叠的来源块；所有实际路径由claim/READY提供。
"$CTL" claim --job-id SOURCE_REVISION --work-key id:ID --work-key doi:DOI \
  --workspace "$B/candidates/OWN_BLOCK" --stages "$B/candidates/OWN_BLOCK/stages.json"
"$CTL" run --job-id SOURCE_REVISION
"$CTL" collect
"$CTL" admit --decision "$B/operations/corpusctl/admission-ID.json"
"$CTL" batch
"$CTL" publish --batch-dir BATCH_DIR
# 发布后传入上一轮实际公开恢复描述，不能传技术READY。
"$CTL" verify-public --batch-dir BATCH_DIR --commit PUBLIC_COMMIT --previous PREVIOUS_JSON
```

`admission-ID.json`必须含problem_id、package、build_root、receipt_root、accepted_report、owner_final_ready、accepted_H、difficulty_reason、material_basis、semantic_basis、rights_basis、admitted_by和`decision: admit`。只有当前总控填写语义决定；worker不能自晋级。

云电脑中转命令为`python corpus-work/scripts/publish_corpus_bundle.py --bundle ABS --relay ABS --expected-base COMMIT --receipt ABS`。服务器先提交明确文件，再用`git bundle create ABS LAST_REMOTE..HEAD`出包，云电脑通过scp取得bundle。脚本实际验证Git bundle、远端祖先和正常push结果；若远端前进则停在待整合，不强推。bundle推送回执不增加数学交付数。

真实断连验收见[记录](handoff/yupeng/corpusctl-real-reconnect-r001.json)：控制SSH退出、另一次SSH重连及服务重启后，同一在途来源worker仍为同PID/启动时间；重复resume未启动第二份。首个1065真实发布已通过[公开恢复](handoff/yupeng/main1065/PUBLIC_RESTORE_VERIFIED.json)；下一批已持续生产。dot云端SSH与GitHub身份接通仍未实测。
