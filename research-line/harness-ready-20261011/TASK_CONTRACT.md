# 当前规则与持续任务

遵循仓库根[PROJECT.md](../../PROJECT.md)。当前从[启动说明](HARNESS_START_HERE.md)接续，[执行提示词](DEEPSEEK_HARNESS_PROMPT.md)适用于DeepSeek及全部子智能体；PREPARATION_WORKLIST.jsonl仍是唯一工作表。

150道已准备，长期目标30,000；取消旧逐题审批、双审、抽检和会话证据要求。既有成品经reserve/adopt-material进入发布，不重编、不重审。

## 此前计划与契约（历史保留）

# 找题与建库：当前入口

执行前先读[本项目统一工作准则](D:/Study_Works2/Lean_grokking/PROJECT.md)。当前只做找题与建库；沿已有工作表复用材料，完成题证整理、针对性去重、装配及入库。

旧字段说明仅供读取既有记录，不要求补录审阅身份、读取事件或会话证据。文档变更不代表旧程序已改造；仅当程序实际阻挡入库时作必要局部调整。

## 历史内容（保留，不再作为当前执行指令）

下文旧审查、抽检、DeepSeek交接和启动要求已被项目准则替代，原数字仅为历史快照。

# 当前任务契约：定点核查与持续生产

2026-10-11用户批准的当前责任与停止条件见PLAN.md。此文件替代旧契约的全量独审和逐题root预批要求；原契约保存在draft-history/before-focused-TASK_CONTRACT.md。旧任务及其意见仍按原规则承接，不自动改标。

## 数据接口与核查方式

工程POLICY保持reviewed-revision-v2。新任务显式review_protocol=focused-source-check-v1；字段和准确JSON形状见operations/FOCUSED_INTERFACE.json。任务仍包含准确task_id/revision/source_id/source_version/claim_key、完整作者、许可、statement/proof/context spans、标准先修、1至3项非例行核心义务、roadmap、具体难度理由、近邻比较、原作者宏/图/书目及装配配置。

每项span相对于本目录P，指定真实源文件、起止行和原始标签。起草problem_id为null；现场reserve成功后才登记正式题号。完成定点核查但尚未编号/通过接口验证的卡只能称待准入，不计成熟总数。

新review保留任务与修订范围绑定、approved_task_config、原因和具体判断，另含同名review_protocol、checks五键authorship/paired_scope/key_hypotheses/core_obligations/semantic_neighbors。每键有pass及具体原文短依据，red_flags为空才可通过。允许同一人选题和核查，不要求H3两审；这不是对作者证明逐步独立重证的声明。

旧task缺review_protocol时仍按旧规则验证。历史applicable_public_qualification_reuse只能承接适用的旧意见，不准通过新标签绕过旧要求。纯工程配置调整按原scope_reuse边界复用；数学范围改变须新修订及相应定点核查。

## 来源路线授权

Codex批准路线的来源/URL边界、许可、学科及排除规则。DeepSeek可在批准范围内自主发现文献、选择命题，无须每文或每题root签字；新站点、新许可或越界内容须先暂缓。

每篇source record固化source_record_id、route_id、source_id/version/url、真实许可信号、允许范围、排除范围和明确整文件资产许可清单。每题source_authorization引用route_id/source_record_id，所有实际正文/先修/宏选段及资产书目须在所授权范围内。来源批准不等于其全部命题自动合格。

同一文献的原件、原宏、记号和已核依赖共享。已公开/在途/淘汰的具体claim均先查，不把支持引理的出现当作主命题已计，也不把同一主命题不同证明算新题。

## 独立抽检

当前主控冻结batch具体任务ID及修订后，用prepared_focused.py select-sample随机抽ceil(n/10)，25道抽3道，尾批至少1道。抽样文件不覆盖重抽。

DeepSeek主控调用原生agent_spawn新上下文，明确allowed_tools只含读取所需材料的工具；不使用fork继承生产历史，不给初审评分理由和先前裁定。输入只含中性原题证、必要本地引理/定义、允许先修及实际原资产。抽检占用现有两个工作槽之一。

记录实际子会话身份、原始请求、真实读取事件及最终结构化结果。适配后的session证据只能引用/提取原始记录，不得从自报通过生成假读取事件。材料截断、核心缺失、承重图形不能解读或实质红旗未决时不得通过。仅更换reviewer_id不构成独立审阅。

数学疑点由生产主控记录精确位置和缺口后HOLD，继续其他题；运行期间无需等Codex为每批签字。Codex交前校准、交回后处置；不在后台假定Codex一直在线。

## 执行、计数与恢复

正式和后备都必须是完整可执行未公开任务。首次100+50由Codex组织astra/low准备；今后由DeepSeek自行补队列。少于25条先补至50，长期目标Q=30000，不在完成100题后停止。

现有run_prepared.sh调度validate-task/assemble/qa/verify-job/reserve/prepare/relay/publish/restore；新增抽检通过prepared_focused.py。使用原XeLaTeX明确分遍链，禁止调用暗含内容摘要的旧默认链。不安装新依赖、不做正文逐字节检查、不删除现场。

一个主控、最多两个工作子上下文；正式ID由现owner/generation在现场master/queue/FLOW/reservations下登记；每批1至25条，发布串行。后续具体whitelist由生产者冻结任务配置形成，不需要root逐题签字，但仍受来源授权、修订、抽检及owner校验。

公开恢复成功后才更新Q；同时显示M、未公开成熟数、HOLD以及按审核依据分组的资格数。读取queue.base与本批真实恢复记录，不把旧顶层计数字段或旧batch_size当新产线规则。旧分片及旧口径保持兼容；本次不重审历史全库。

未知外部写入或中断先接续原batch，不重新凑批、推送或计数；控制权冲突不抢占、不删锁。正式新会话仍由用户开启，先实际完成一题及首批公开恢复，再展开并行。准备、脚本测试、独立读取校准不等于已正式移交。
