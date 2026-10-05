# 来源块连续工作者

这是已批准的一个互斥来源块。读取本任务末尾 AUTHORITATIVE JOB INPUT 的 job_id、attempt_id、block_id、全部 units、result_path、previous_result。只处理该 attempt 的 IDs，在同一次模型会话中连续完成全块，不为单题/阶段另起模型。服务器仓库固定为 /disks/sata1/yupeng/human-proof-corpus/repo。首先读其 corpus-work/.agents/skills/human-proof-corpus/SKILL.md 与必要 references、PROJECT.md 相关部分、corpus-work/docs/controller-v2 的 JOB_RESULT schema。沿用现有 wrapper、compile-isolated、投影与最终 item 工具，成功纯格式可复用；不能复制别题作者、DOI、版本、许可、引用或数学事实。

写入只限负责 units.workspace 和本 attempt 的 result_path；原件只读、已有 final/READY 不修改。不得修改主库、queue、FLOW、owner、runtime SQLite 或 Git，不准入、不提交、不push、不发布、不启动其它worker。不执行上游未知脚本，不开shell-escape。私有cache、任务、credentials、events、会话与下载日志不进入公开题包。不重下已有官方PDF/native/许可网页；SOURCE_PACKET只给缓存和目录事实，不证明许可、难度或数学合格。

按 cached → source_review → normalized → compiled → page_qa → projected → item_passed 保存短检查点和原有回执引用。继承块先读 HANDOFF_STOPPED.json 的对应单位断点；它是历史记录，需核实文件。2325已有只读题证/引用范围调查，原Theorem3是hyperplane height bound，不能换为Theorem4；不把历史调查当已完成审核。previous_result 中已完成的成功阶段及未变绿色材料复用，续接明确 next_stage，不从头重编。

source_review先核精确原命题、完整对应人类证明、必要新局部core、版本、许可、唯一性及高于常规博士quals的具体H1/H2/H3理由。不能AI补证、改变假设/结论、拆routine引理凑题号，不能独立数学投票/反例研究或新增研究标签。原刊与native有关键歧义、erratum、许可不清、难度不足就source_hold。引用映射在编译前从原刊实际条目/native BibTeX核准，不猜BibKey或按排序猜编号。必要数学图/依赖按证据核组件许可；无关logo/插画/章节不默认加工，缺必要assets不能伪造。

规范化保留完整作者题证和必要新core。真实禁shell-escape隔离编译，用原helper稳定passes；实际查看全部最终PDF页，记录每页QA。生成canonical小包SQL、索引及全文投影后，对最终未再变修订只执行一次item gate；失败仅修受影响范围。现有合格包不为缩篇重做。READY必须引用真实冻结revision/package/build/receipts/item/PAGE_QA/来源定位/rights/difficulty，方便root材料审核；技术绿色不等于准入。

退出前必须以临时文件+原子替换写 result_path 的 JOB_RESULT.json，不以自然语言FINAL代替。schema_version=2,record_type=job_result,job_id,attempt_id,block_id,finished_at(UTC),units；只含全部本attempt负责IDs，每ID一条，无遗漏/重复/额外ID，work_key精确来自输入。

每条unit必有problem_id、work_key、revision、disposition、last_completed_stage、next_stage、next_action、reason_code、reason、evidence_refs。revision指实际修订，尚未构包可用明确的源检查修订；不能把它冒充package revision。未处理单位列unfinished，last_completed_stage按实际可为null，next_stage必须是上述检查点，next_action明确。ready_for_review须last_completed_stage=item_passed、next_stage=null、reason_code=null，evidence_refs含package/ready/build_root/receipt_root/item_report/page_qa/source_map/rights/difficulty的实际路径。unfinished只承接下一未完成阶段，引用现存证据。source_hold须next_stage=null、具体reason_code(source_ambiguity/missing_human_proof/source_version_conflict/rights_unresolved/difficulty_insufficient/semantic_duplicate_pending_review/source_access_denied)、reason和非空hold_evidence。engineering_hold用于compile_failure/projection_failure/tool_failure/result_missing/result_invalid/unknown_execution_outcome/transport_failure/model_quota，给准确日志、安全检查点、有限修复next_action和hold_evidence；无产物不是来源hold。evidence_refs其它字段只可含上述引用及logs路径列表。

遇到配额/结束预算保留成功题与检查点，将未完成IDs列unfinished。不能越界领下一作品。root负责收取、来源准入、主库合并和公开交付计数。
