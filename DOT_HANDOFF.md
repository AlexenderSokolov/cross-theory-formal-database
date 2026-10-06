<!-- Historical dot handoff; superseded by LOCAL_CONTROLLER_HANDOFF.md. -->

> 历史停止快照。dot方案已放弃，现行入口为 [LOCAL_CONTROLLER_HANDOFF.md](LOCAL_CONTROLLER_HANDOFF.md)。下文不作为当前派工指令。

# Your dot 接管：高级数学人类证明题库

## 先接管控制，再继续生产

用户已要求原Codex会话停止生产，改由 **Your dot自己的云电脑通过SSH控制Yupeng**，并在dot一侧定时汇报。原会话目标已暂停；旧桌面心跳20-1000为PAUSED；服务器corpusctl.service已停止并禁用自动启动；旧来源CLI已停止。所有材料保留。

本文件是唯一交接入口。**交接材料已准备，dot尚未实际接收，云端SSH和GitHub身份尚未验证，定时汇报尚未在dot创建。** 接管者先完成连接实测，然后取得唯一owner并恢复服务，避免原会话和dot同时派工或发布。

## 目标、位置与真实起点

- 最终目标：30,000道合格唯一题，完整可编辑人类题证、真实编译、全文SQLite、公开远端可恢复。
- 仓库：<https://github.com/AlexenderSokolov/cross-theory-formal-database>，分支`corpus-progress-20261001`。
- `B=/disks/sata1/yupeng/human-proof-corpus`，仓库`$B/repo`，Python`$B/runtime/python/bin/python`。
- 实际公开主库 **1065题**；本地已合并 **1065题**。
- 数据提交`347369e58e67feffcd520e56bf0f5ae6b95f7129`已从公开远端实际恢复；[恢复记录](handoff/yupeng/main1065/PUBLIC_RESTORE_VERIFIED.json)证明1065行、完整性ok、外键无错误、全文与来源完整投影、整包门禁通过。
- 最新主库合并一次处理17个小包：1048→1065；相对上次公开1040净增25。rebuild/aggregate各一次，用时74.6秒。复用了17份未改变的逐题成功结果。
- 另有 **8题已准入、未合并**：1819、1820、1379、1477、2252、2283、2246、2383。[PRODUCTION_QUEUE](handoff/yupeng/PRODUCTION_QUEUE.json)保存精确包、构建、回执、报告与准入理由。1065＋8＝1073只是合并前准入总量；远端交付仍为1065。
- 975＋40遗产已经完成接收；LOCAL1002与其中27题重叠。七份旧独立备份也与主库重叠，不再次计数。1907仍不计数。

实时状态以`corpusctl status --json`、queue及实际文件为准。历史CURRENT、旧1000目标、旧PID、旧launcher、候选行数均不作为当前入口。

## 第一轮应做什么

1. 从dot云电脑实际测试SSH和控制端GitHub登录。连接信息放私有SSH配置；个人电脑的现有私网连接不能假定云电脑也具备。不得复制个人GitHub凭据到Yupeng，不擅自新增公网端口或网络隧道。
2. 阅读本文件、[PROJECT.md](PROJECT.md)和[human-proof-corpus skill](corpus-work/.agents/skills/human-proof-corpus/SKILL.md)。查看[停止快照](handoff/yupeng/DOT_TRANSFER_STATE.json)。
3. 读取status与三个停止交接文件，接续精确未完成阶段。8个已准入包可直接消费；不要重编、重转录或重验未改变的材料。
4. 优先核对1793、2286的技术READY；2415已完成编译、全页QA和最终item，仅缺READY收尾与root材料准入。它们目前都不计入已准入数。1791因原文关键记号与书目问题保持hold。
5. 继续互不重叠的来源块。达到下一批25个净新增准入项后自动组批至1090，再1115、1140；随后按实测吞吐继续至30,000。
6. 接管成功后在 **dot一侧创建每2小时一次、时区Asia/Shanghai的进度汇报**；记录实际创建的任务/日程ID。不要在原Codex会话重建心跳。重大阻塞立即报告。

## 来源块和完成位置

以下路径都位于`$B/candidates/`。完整待续接命令、版本和回执在各`HANDOFF_STOPPED.json`，三份也已复制到仓库的[停止记录目录](handoff/yupeng/dot-stop/)。

| 来源块 | 停止时状态 |
|---|---|
| native-source-continuous-r003 | 1379、1477、2246已READY并已root准入。2244、2282因严格难度依据不足hold。2325仅完成来源调查；2326、2368、2375、2378仅缓存。 |
| native-source-continuous-r004 | 1820、2252、2283已READY并准入；2286已技术READY待准入。2316、2374、2385、2509、2540仅缓存。 |
| native-source-continuous-r005 | 2383已READY并准入；2415的package-r002已2遍17页编译、全部页面QA、SQL及最终item成功，仅待READY/准入。2510、2512、2524仅缓存。 |
| native-source-continuous-r002 | 1793有技术READY（package-r007），root尚未核准；1794检查保留的实际产物后续接。1797未开始，原生TikZ并非来源缺失，不因长文自动hold。1791为明确source-clarity hold，其技术绿不能晋级。其他已合并或已在queue。 |

旧executor-2-r001的实际终止记录为`TERMINAL.json`，exit1，2026-10-05 04:54:28 UTC，是用户停止后的退出。不要将其当来源失败或重新启动整个旧块。

来源先下载再加工。优先复用`$B/source-cache/catalog-r001`和各块的`cached-originals`。旧候选库仅是查询队列，不是全文主库。附属来源预下载记录在`$B/source-cache/declared-assets-r001/ACQUISITION.json`，只是获取记录，不代表组件已获公开准入；无关品牌图和插画可按既定规则省略。

## 唯一控制者与固定命令

```sh
B=/disks/sata1/yupeng/human-proof-corpus
CTL="$B/repo/corpus-work/corpusctl"
"$CTL" status --json
"$CTL" owner --expected-owner handoff_pending_dot --set-owner dot
bash "$B/repo/corpus-work/run_corpusctl_service.sh" install
```

只有dot实际连接并接收任务后，才执行owner交接和恢复服务。`Linger=yes`已设置。服务承担已登记任务的续接、真实退出收取和满批合并；dot承担来源块选择、材料准入、语义去重与发布。不能把服务active当作已有来源产出。

```sh
# 每个来源块必须有固定JOB_ID和互斥作品/ID；stages.json保存准确argv、stdin及当前阶段。
"$CTL" claim --job-id JOB_ID --work-key id:ID --work-key doi:DOI \
  --workspace "$B/candidates/OWN_BLOCK" --stages "$B/candidates/OWN_BLOCK/stages.json"
"$CTL" run --job-id JOB_ID
"$CTL" resume --job-id JOB_ID
"$CTL" collect
"$CTL" admit --decision "$B/operations/corpusctl/admission-ID.json"
"$CTL" batch
```

重复JOB_ID不另启一份；PID须同时核启动时间和工作目录。失败与未知阶段不盲目重放，活子进程不能转移claim。已完成编译则接QA/投影/门禁，不重新下载。模型限流退避、减少新启动，不杀健康任务。

准入决定必须明确材料、H理由、语义和许可；READY、退出0、编译成功都不是准入。root专有字段由dot填写，不能让来源worker自晋级。开始用三个有效来源工作槽，每块10—20候选；按实际产出与配额增加至最多八路。工作者只写自己的目录，主库与Git只有一个写者。

## 每题标准与工程闭环

- 高于常规博士资格考试，H1/H2/H3须有2—4句具体理由。
- 原命题、假设、量词、常数和结论完整；完整人类证明及必要新局部核心保留。标准先修可以精确引用，主要困难不能略去。
- 记录作者、作品、版本、DOI/URL、定理/页码和原文定位。原文关键不清、版本冲突、缺证明、许可不明或难度不够，具体hold并继续其它来源。
- 使用可编辑TeX正文；无关插画不处理，证明必需的图/资产须满足材料和许可要求。不得用PDF嵌入、图片或链接冒充正文。
- 原文引用、宏和必要资产先在小包收尾；隔离禁shell-escape真实编译，必要全页QA，canonical全文SQL投影，然后最终一次`--item`。输入不变的成功结果复用。
- 先用`compile-isolated --package ABS --build-root ABS --receipt-root ABS --item ID --engine xelatex`，再显式运行当前`validate_corpus.py --mode editable-delivery`，包括真实evidence、build、receipt、item和独立report。不要裸用旧默认validator。
- 沿用`sync_editable_projections.py`及canonical `rebuild(root, output)`，不要套用旧固定数量临时脚本。冻结final后不原地修改；必要修订保留旧版。
- 不生成补证、不改作者数学、不独立数学审稿、不拆routine引理凑数、不重复计不同语言/版本/Lean表示、不增加a/c等研究标签。

## 一次组批、发布与恢复

每25个净新增合格项组装一次、重建一次主库SQLite、aggregate一次。稳定100题后可按100题发布，每500新增完整对账。保留既有一次合并器，不逐题合并主库、不重复单包aggregate/CAS。

```sh
"$CTL" publish --batch-dir ABS_BATCH
# 显式准备文件清单进入Git；不git add整个工作目录。
"$B/runtime/python/bin/python" -B "$B/repo/corpus-work/scripts/stage_corpus_release.py" ABS_BATCH
# 正常commit，服务器制作 LAST_REMOTE..HEAD 增量bundle；控制端取回后执行：
python corpus-work/scripts/publish_corpus_bundle.py \
  --bundle ABS_BUNDLE --relay ABS_RELAY --expected-base LAST_REMOTE --receipt ABS_RECEIPT
# 精确公开提交实际恢复后才增加远端计数：
"$CTL" verify-public --batch-dir ABS_BATCH --commit PUBLIC_COMMIT \
  --previous "$B/operations/corpusctl/batches/batch-1048-1065-r002/verify-public/result.json"
```

GitHub认证留在dot云电脑。发布前读取远端，远端前进则保留并整合，不能强推。出包或push不等于公开可恢复；恢复SQLite及真实编译资产后确认完整投影与gate。下一轮previous直接使用上一轮成功的verify-public/result.json。恢复包的内部格式字段由现有工具处理，不追加SHA专项、目录散列、多层pins或额外审计平台。

## 定时汇报内容与授权

每2小时汇报：本期新增准入数、本期新增公开交付数、累计本地合并数、累计远端交付数、待准入/待合并数量、具体hold和实际吞吐；下一检查点及真实阻塞。无产出时写0，不以启动进程、文件、候选、工具测试代替成果。首次汇报还需说明SSH、GitHub登录及日程创建是否真正成功。

用户已授权本项目正常范围的下载、题证整理、校验、建库、commit/push及同仓库Release，无需重复确认。禁止MCP生产操作路径、批量删除、强推、覆盖其它会话成果、泄露凭据/私有会话/隐藏HTML字段、上传未经许可原件、执行未知上游脚本。仓库为公开，逐组件核验再分发依据。

持续使用项目skill和Stop That Shit：只做交付所需工作，不重复已绿检查，不另建网站或DS Lite/ORX框架。遇网络临时故障保留断点并退避；确需人处理的连接或身份阻塞及时报告。原Codex会话保持暂停，dot负责后续总控。
