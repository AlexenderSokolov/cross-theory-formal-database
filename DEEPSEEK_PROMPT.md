# DeepSeek Harness 接管提示词

你接管高级数学人类证明题库。目标是累计 **30,000 道合格、唯一、可追溯的题目，并完成公开可恢复交付**。请直接执行本提示词，不停留在计划或能力说明。

先读取本目录 `CORPUS_HANDOFF.md`，只读取与当前任务有关的文件。它提供带时间的状态、路径、现有材料、hold 和恢复入口。不要根据根目录历史任务、旧 OpenResearch 会话或 DS Lite 看板恢复旧实验。

## 授权与当前阶段

用户已授权本任务内取材、必要修改、编译、验证、Git 提交、推送及既有仓库发布，无需逐题逐批再次询问。保留已有改动和原始材料；禁止批量删除。不要启动旧聊天、旧心跳、旧实验，也不要新建调度框架。

原 Codex 已停止主动推进；这不等于远端全部进程已停止。用户把本提示词交给你执行即接管生产，先确认现有进程，避免重复运行同一材料。只做交接文件的 Codex 回合不能据此自行恢复生产。

2026-10-06 00:12:51 北京时间核实：主库与公开可恢复交付各 1,115 道，队列 7 道，下一批 1,140 道，还需 18 道新准入。10 份技术 READY 文件存在，尚不能直接算作新增合格题。后续以现场真实状态为准。

## 执行方法：三路生产，一次检查，按批发布

1. 先消化交接中列出的 READY，再处理 v4 已缓存输入。需要补充供给时再扩源，优先已有合法全文及原生 TeX 的来源，不重复下载已有资料。
2. 有并行能力就用三路，每路负责不重叠的来源或题目；同一来源的规范信息先确定一次再共享。没有并行能力就立即串行处理，不先开发调度器。沿用已有控制器，不另开重复服务。
3. 生产端完成来源、完整题面及原作者证明、必要自足内容、难度、许可、同题重复判断，留下简短且可定位的结论。已有有效结论直接复用；缺哪项补哪项。
4. 控制器只核对现有结论、产物身份、全局 hold、重复和机器验证结果，然后准入。**取消根端逐篇全文复审、额外独立审核角色和反复难度评审。** 不开展独立数学纠错或寻找反例研究。
5. 已通过的编译、页面核对和单题结果复用。修改 TeX 后才更新受影响的构建；只改元数据时，只更新相关投影和单题检查。不要因为换模型、换会话重新验证全部历史题库。
6. 单题缺完整证明、许可不清、原文实质歧义或难度不足，记录具体 hold 后立即处理下一题。hold 不阻塞其他题，也不能为凑数直接放行。不得 AI 补证明、偷偷改固定命题或拆普通引理凑数。
7. 使用现有 FIFO 队列，每 25 道合并发布；发布时其他生产路继续准备下一批。达到目标前只取剩余所需数量。断线先核对上次操作结果，未知不等于失败，不盲目重跑。

沿用既定 H1/H2/H3 标准，以实际数学机制判断，严格高于普通博士资格考试；来源名气、长篇证明或技术词汇不能代替难度。完整的人类原证明、精确版本和许可、语义唯一等准入标准保持。

## 接管和命令

本地目录是 `D:\Study_Works2\Lean_grokking`，它不是 Git 根目录。实际生产仓库在 Yupeng，不能拿本地旧 checkout 的 180 题状态覆盖它。

从本地 PowerShell 登录：

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 -o ProxyCommand=none -o ProxyJump=none -o ClearAllForwardings=yes Yupeng-orx
```

远端 Bash 中：

```bash
B=/disks/sata1/yupeng/human-proof-corpus
PY="$B/runtime/python/bin/python"
CTL="$B/repo/corpus-work/corpusctl"
"$CTL" status --json
systemctl --user show corpusctl.service -p ActiveState -p SubState -p MainPID
OWNER=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["owner"])' "$B/operations/corpusctl/owner.json")
GENERATION=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["generation"])' "$B/operations/corpusctl/owner.json")
```

服务是 user service；不要因系统级查询显示 inactive 就重启。沿用真实 owner/generation；更换模型不要求更换逻辑控制器。不得并发手改状态、删除锁、重启健康服务或重放已完成的作业。若确需转移身份，使用现有 `owner` 接口，不手改 owner 文件；身份转移不等于自动停止全部旧进程。

准入时，读取实际 READY 所指向的冻结产物，复用已有 admission 文件格式。**READY 文件本身不是 admission decision。** decision 必须有以下非空字符串字段：

`problem_id`、`package`、`build_root`、`receipt_root`、`accepted_report`、`owner_final_ready`、`accepted_H`、`difficulty_reason`、`material_basis`、`semantic_basis`、`rights_basis`、`admitted_by`，以及 `decision: "admit"`。`accepted_H` 只能为 `H1`、`H2`、`H3`；题号为字符串。READY 中可能使用 `final_package`、`item_report` 等别名，要映射到实际存在且通过的文件。不要伪造任何依据。

```bash
# DECISION_FILE 指向该题实际写好的 admission JSON，不能用 READY 替代。
"$CTL" --controller-id "$OWNER" --generation "$GENERATION" admit --decision "$DECISION_FILE"
# 满 25 道后，通过现有唯一控制流程冻结并合并；先核对是否已有 active_batch。
"$CTL" --controller-id "$OWNER" --generation "$GENERATION" batch
```

读取 `batch` 实际返回的批次目录，然后在本地项目目录执行：

```powershell
python -X utf8 -B ".work\human-proof-corpus-control\corpusctl-implementation\controller_publish_pipeline.py" publish-batch --host Yupeng-orx --batch "<实际远端批次目录>" --owner "<当前OWNER>" --generation <当前GENERATION> --relay ".work\human-proof-corpus-control\relay.git" --cache ".work\human-proof-corpus-control\publication-cache"
```

尖括号值必须替换为现场值。发布脚本自动读取前次公开证明并复用已有步骤；不要猜批次名、previous/base 或提交号。正常发布保留既有精确提交恢复验证，不额外重做历史验证。

已有辅助脚本 `operations/local-controller-01a10a85/admit_native_frozen.py` 硬编码旧身份且按 DOI 处理；接手后不能盲用。优先复用上述 CLI，不另造入库协议。910 已完成 finalizer，不得再次执行。

## 第一阶段成果与报告

按现场状态补足下一批实际公开交付；若仍是 1,115 + 队列 7，则完成 18 道新准入，公开推进到 1,140。之后沿同一流程继续到 30,000。不要把提交交接文档当作题库数量增长。

每批报告北京时间统计区间、新增准入、新增公开交付、累计本地合并、累计公开可恢复、排队数、具体 hold，以及新增公开交付数除以实际耗时得到的吞吐。没有新增报 0，未核实报未知。候选、下载、技术 READY、进程启动和工程测试均不算交付。

交付 Git 提交后确认远端分支 SHA；公开题库交付后保留精确提交恢复证明。不要在回复中承诺未经实测的速度或把服务运行状态当作生产进展。
