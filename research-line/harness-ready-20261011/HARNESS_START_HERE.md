# DeepSeek持续生产：从这里开始

先读仓库根目录[PROJECT.md](../../PROJECT.md)。它完整约束Codex、DeepSeek及双方子智能体，不因换模型增加审查。唯一任务是找题、整理完整作者题证、建库和已授权发布，持续达到30,000道；原作者对数学工作负责。

## 已经可用的材料

- [150道成品索引](../../materials/INDEX.md)、[SQLite材料库](../../materials/PREPARED_MATERIALS.sqlite3)：100正式、50后备，全部已编译。不要重编或重审。
- [唯一工作表](PREPARATION_WORKLIST.jsonl)：150条prepared_unpublished；3条published为之前演练成果；另外9条旧未完成/暂缓项不阻挡生产。原29卡中4份未收录，不为凑数重开。
- [状态](STATUS.json)：本轮新增70份本地材料，生产主库公开新增0。上传维护分支不是主库发布。
- 去重使用已有[公开身份索引](reference/public-items.jsonl)、[明确淘汰记录](reference/retired-claims.json)和工作表；检索命中的近邻才定点比较，不重扫整库正文。

工作表assembly_job、tex_path、pdf_path相对于仓库根R；task_path相对于本目录P。每次开始都从仓库根执行命令，不把本机C盘或D盘路径当成通用路径。

## 执行环境与权限

用户指定Westlake DeepSeek V4.1 Flash，使用已有配置，不更改账户、模型全局设置或权限，不使用auto/yolo替代正常授权。由用户开启正式会话；Codex没有代为启动或接管。

源码分支：`codex/corpus-repair-20261010`；生产发布分支：`main`。本地准备和生产库分别管理，不将研究分支直接覆盖main。

已有生产主机为SSH别名`Yupeng-orx`，生产范围`/disks/sata1/yupeng/human-proof-corpus`。共享状态目录`operations/corpusctl`，队列`repo/handoff/yupeng/PRODUCTION_QUEUE.json`。生产Python为`runtime/python/bin/python`。150份成品可在该主机取得本维护分支的独立源码目录后直接复用；已有目录先检查状态，不覆盖未提交工作。首次按以下内容读现场，不自行重建管理服务。

历史快照为M=14,878、合格公开Q=12、owner=codex-takeover-01a12558/generation2；仅是2026-10-11快照，不作为现场值。当前主库路径取queue.base.master_database，已公开基线取queue.base.verified_corpus_commit。Q用当前主库对应的实际公开资格记录读取，不把M升级成Q。

如需要转移控制权，使用已有corpusctl接口：先读取owner和队列确认没有正在推进的批次；再以实际旧owner/generation作为期望值，转交给本次DeepSeek主控。冲突就停止相关写入，不删锁或手改身份。示例（变量用现场值）：

```bash
python corpus-work/scripts/corpusctl.py --state-root "$STATE" owner --json
python corpus-work/scripts/corpusctl.py --state-root "$STATE" --controller-id "$NEW_OWNER" --generation "$NEXT_GENERATION" owner --set-owner "$NEW_OWNER" --expected-owner "$OLD_OWNER" --expected-generation "$OLD_GENERATION"
```

这是沿用现有单主控保护，不要求证明会话独立发生，不生成会话证据链。

## 第一条任务：发布首批现成材料

先复用工作表前25条formal成品，不新增选题或重编译作为开工前置。

1. 读取现场owner、queue.base、FLOW和prepared-reservations.json；有未结束的发布批次先续原批次，不新建重复批次。
2. 复制[编号请求模板](operations/first-batch-reserve.template.json)为工作spec，填写实际actor、master_db；复制[发布模板](operations/first-batch-publication.template.json)，填写同一actor、当前公开基线和既有发布Git目录。模板已经列出首批25条准确任务，不需逐题root批准。
3. 两份spec均保留`preparation_basis: author_material_collection`；不要添加whitelist、审阅、抽检、source authorization或会话记录。
4. 用reserve取得或复用正式题号。80个旧保留号以现场reservation账本为准，70个未编号条目正常分配；不直接把L开头的本地文件号当正式题号。缺失的旧reservation先查原编号记录和主库，不凭工作表强塞编号。
5. 对首批工作表assembly_job逐一adopt-material，保留最终TeX/PDF和原作者材料，不重装配或重新编译。
6. prepare本批，再publish；成功后更新原工作表的状态与实际公开提交。失败按现有批次阶段续跑，不重复发布和计数。

从R执行：

```bash
python corpus-work/scripts/prepared_publish.py reserve --spec <已填写的reserve.json>
python corpus-work/scripts/prepared_delivery.py adopt-material --job <工作表assembly_job> --output-root research-line/harness-ready-20261011/jobs/author-material-publication --reservations <现场prepared-reservations.json>
python corpus-work/scripts/prepared_publish.py prepare --spec <已填写的publication.json>
python corpus-work/scripts/prepared_publish.py publish --batch <publication_root>/<batch_id>
```

publish复用既有提交、推送、公开恢复及队列更新。不要把prepare完成或维护分支上传计入Q。网络中断时使用原batch续同一命令；不要重凑一批。确需单独恢复时使用现有restore命令，不添加新的跨机器重放测试。

相同来源的旧著录格式不同，使用普通`source_reconciliations`记录执行者recorded_by、原因及实际task/public两侧author/work/source_url/source_version/license；保留原数据，不要求root签字，不以此重新审论文。

## 库存用完后继续

六条路线：[代数数论](scouting/algebra/README.md)、[几何拓扑](scouting/geometry/README.md)、[分析PDE](scouting/analysis/README.md)、[概率](scouting/probability/README.md)、[组合算法](scouting/combinatorics/README.md)、[数理逻辑](scouting/logic/README.md)。清单标明同源已完成命题；Hartree非线性主定理、统一时间传播混沌、同时Markov–quantile逼近等已完成，不按旧线索重开。

新题先保存原件和必要作者题证、许可及简短难度/近邻理由，复用已有task格式。使用assemble --material-only产生新成品；这个选项不要求审阅记录或正式题号。已有成品直接adopt，不重编。需要发布时经reserve取得正式题号。

```bash
python corpus-work/scripts/prepared_delivery.py assemble --task <task.json> --task-root research-line/harness-ready-20261011 --output-root materials --material-only
```

库存低于25先补至至少50；每批最多25；最多两个材料工作上下文，单主控串行入库发布。没有独立审阅槽。按领域与方法缺口选题，不设机械配额，不拆直接推论凑数。

完成100道、用完150道或结束一次会话均不停止三万题目标。中断后读工作表与原批次接续。单题问题留具体缺口并继续其它材料。只有达到Q=30,000、批准来源耗尽、环境/权限实际阻断或确需用户决定的新范围问题，才停止相关工作并回报。

汇报新增可用题、实际公开增量、当前Q和具体阻碍；来源线索、工作次数、模型输出量均不算题数。旧compiled_pending_qa名称不触发审阅；作者材料新入口输出material_ready，不补造旧审核证据。
