# 本地总控：日常执行一页说明

目标30,000道合格唯一题。先看[当前产物索引](handoff/yupeng/ARTIFACTS_CURRENT.md)、queue和实际任务状态；严格标准统一引用[项目skill](corpus-work/.agents/skills/human-proof-corpus/SKILL.md)，不重复展开规范。

## 五步闭环

1. **处理来源**：优先缓存和已有断点。确认精确命题、必要证明/core、难度、版本和许可；具体问题逐题hold。无关插画、品牌图和章节不默认加工。
2. **完成题证**：忠实转录，引用按原刊映射，复用已成功wrapper的纯格式部分。作者、DOI、许可和版本逐题绑定。
3. **逐题验收**：对固定final真实编译，完成必要QA和全文SQL投影，执行最终一次item门禁。未改绿色材料复用；失败仅重做受影响部分。总控作明确材料/语义准入。
4. **满25项合并**：按queue顺序冻结25个净新增，一次主库重建、一次aggregate；余项留下一批。已有待公开批次时，来源加工和准入可继续，合并等待。
5. **公开恢复**：沿用现有固定发布入口和上一轮实际恢复描述；正常push后实际恢复，成功才增加远端交付数。继续下一批，不等待新的人工派工。

## 何时才再验证

只有题目输入改变、出现实际失败或相关程序改变，才重跑对应范围。控制器工程场景及已经通过的测试不列入日常清单，不逐题aggregate/CAS，不为每次状态汇报扫描或重验整库。

当前集成测试自然完成后进入生产；失败只处理关联部分，不再追加泛化测试或新一轮架构审查。来源加工不等待无关发布优化，发布问题只阻塞对应发布步骤。已有程序保留，不为“精简代码”重构一轮；已有合格题包也不为缩篇重新制作。

## 固定位置与协作

`B=/disks/sata1/yupeng/human-proof-corpus`；SSH别名`Yupeng-orx`；`repo=$B/repo`；`PY=$B/runtime/python/bin/python`；`CTL=$repo/corpus-work/corpusctl`。SSH沿用BatchMode、ConnectTimeout=10、ProxyCommand=none、ProxyJump=none、ClearAllForwardings=yes；本地仅保留控制与GitHub relay。

初始3个有效来源worker，每块连续10—20候选，继承短块按断点续接。worker只写自己的目录；总控独占准入、主库和Git。actor/generation读取已登记的总控身份并显式传入，不能冒用其它owner。具体参数及恢复细节只在需要时查已实现入口和[开发契约](corpus-work/docs/controller-v2/CONTROLLER_CONTRACT.md)。

## 记录与汇报

queue是准入和计数权威；runtime只记执行；公开恢复result证明交付。每2小时汇报沿用ID2，报告新增准入/公开交付、累计、等待、hold及下一步；无新增写0。进程启动、技术READY、文件数和工程测试不计题数。

来源/当前主库/未交付材料原路径保留；人工清理候选见产物索引。旧dot与旧会话资料只作历史；不恢复旧心跳、不新增平台、schema、散列专项或重复审计。
