# 验证产物增量恢复链

restore_validation_chain.py 只恢复并组装已存在的真实编译产物。它不编译、不建 SQLite、不判断来源或难度、不合并题库，也不增加合格数或远端交付数。原 editable-corpus/restore_validation_artifacts.py 和 schema1 完全保留。

输入是一个外部审定 SHA256 绑定的 schema2 JSON。format 固定为 ordered schema1 validation archives with explicit final filemap；archives 按原顺序排列，每条含 index（从0连续）、id、delivery_sha256 及完整原 schema1 delivery 对象。id 到本地下载目录的关系通过重复 --archive-root ID=LOCAL_DIRECTORY 显式提供，每个目录含原 validation-artifact-delivery.json 和全部原分段。descriptor 原字节的 SHA、inline 对象、分段顺序/路径/大小/SHA、完整 ZIP 与内部 ARTIFACT_FILEMAP.json 必须一致。

final_filemap 是当前最终相对路径到 {archive_id, sha256, bytes} 的完整映射；final_file_count 等于其实际长度。仅接受 build/ID/文件.pdf、.log、.fls、.aux、.out 和 receipts/ID.json。最终每个 ID 需要一个 PDF、同名 log/fls/aux、compiler.log 及对应 receipt；out 若存在须为同名文件。当前来源选择由审定映射明确指定，不自动取最新记录。

同一路径存在不同历史字节时，选中条目增加 overrides 列表，按 archives 顺序逐项列全其他不同字节的 {archive_id, sha256, bytes}。未声明或身份错误的冲突直接拒绝。只有字节和大小完全一致的重复可直接明确选择其中一条。新版本改变文件名时，旧路径必须在 stage_only_paths 中按同样顺序列全原身份；这些文件只留在历史 stage。纯新增无须这两个字段。

恢复者从可信发布入口取得 chain 和 helper 的审定 SHA，通过 --expected-chain-sha256 与 --expected-helper-sha256 单独传入。archive 不能选择执行哪个 helper。工具验证后只执行匹配外部 pin 的已捕获 helper 字节并调用其原 restore(root, destination) 接口。更新 helper 版本需要可信入口更新 pin；工具没有永恒版本常量。

所有 archive 的 JSON/路径/普通文件/ZIP文件图和最终对账都先校验，随后才创建全新 output。每个 schema1 archive 恢复到 output/stages/00000-ID 等新目录，再仅按 final_filemap 复制已核字节到 output/build 与 output/receipts。复制不用硬链接，当前产物与历史 stage 独立。输入及历史字节不会覆盖或删除；失败保留部分输出与失败回执。既有输出和悬空符号链接均拒绝。

实际小样本的可直接检查输入是 real-trial-r001/validation-chain.json，包含1497和1501两个真实 archive、共14个实际编译产物，各2个256KiB分段。ACTUAL_REAL_TRIAL.json 记录 CLI 恢复、最终/历史字节对账、旧源产物身份不变及两题使用恢复产物的现行逐题门禁通过。它不代表1035的66段完整 archive或1040全库链已经恢复。

下面是该小样本的实际参数。重复运行需另选一个不存在的 output；不能覆盖已完成的 actual-chain-restore。生产使用时替换为对应可信入口审定的两个 SHA，不能从未审定 archive 自取 pin 当作批准。

~~~bash
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python -B \
  restore_validation_chain.py \
  --chain real-trial-r001/validation-chain.json \
  --expected-chain-sha256 089f45ea105fd0ce18a7bafc37f54e3ed4798eda220d36f2e48e465fd861408c \
  --archive-root base1497=real-trial-r001/base1497 \
  --archive-root delta1501=real-trial-r001/delta1501 \
  --schema1-helper ../../repo/editable-corpus/restore_validation_artifacts.py \
  --expected-helper-sha256 33548dad0cfb3a268346d896ba2ca4340c1171df8f00d3c08bb18a95723c3594 \
  --output /absolute/new/artifact-chain-trial
~~~

测试命令：项目 runtime/python/bin/python -B test_restore_validation_chain.py。21项实际测试覆盖纯新增、同ID显式版本选择/旧字节保存、旧文件名stage_only以及缺段、错序、篡改、重复JSON/ZIP路径、逃逸、符号链接、既有输出、外部helper pin不匹配。所有测试目录保留，无删除清理；测试中的字符串是明确的传输夹具，不能当题证或编译结果。当前源码SHA58f417fc6bf403a45b8497bbb4f628a90f3a9fe2063e7294feec35a93ef214b4，原helper SHA33548dad0cfb3a268346d896ba2ca4340c1171df8f00d3c08bb18a95723c3594。

最终回执 CHAIN_RESTORE_RECEIPT.json 提供 build_root、receipt_root、每个 archive 的原恢复回执及最终文件图。接续流程仍须将这两个根显式交给现行 editable-delivery 门禁，与最终主库 TeX/SQLite/来源身份对账；实际远端下载恢复与门禁成功前不增加远端计数。