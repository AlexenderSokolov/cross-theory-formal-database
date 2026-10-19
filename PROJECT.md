# 作者题证库：结构与维护

本项目收集高级数学作者的完整命题、证明和必要上下文，供跨理论研究等任务使用。作者负责原数学；本库负责材料配对、来源定位、固定版本、必要上下文、难度依据和针对性去重。不能由模型补写作者证明、修改假设或以编译成功认证数学。

## 当前结构与权威

- `editable-corpus/manifest.json` 的活动 `items` 决定材料成员及稳定字符串 ID；未知字段、前导零、历史判断、退休编号保留。
- `work-registry.jsonl` 关联固定作品版本及共享原件。`tex/works`、`lean/works` 保存作品，`tex/entries`、`lean/entries` 定位每题范围；旧 `items/` 与 `prepared-jobs/` 的原有题证继续可用。
- `catalog.json`／CSV 是元数据投影，保留已有审阅字段；`browse/` 是阅读投影，不能反向修改原始材料或决定准入。
- SQLite、数据库分片及增量描述继续沿既有恢复路径；本轮不迁移或重建作者材料、数据库 schema、编号和运行环境。

## 阅读与选题

入口为 [browse/README.md](editable-corpus/browse/README.md)。TeX 与 Lean 分页，每页最多100条，MD与配套JSON各不超过64 KiB。精简summary列出分页位置，来源目录按原记录的URL主机归组；这不是学科或跨理论标注。

目录先链接真实 `item_path`；存在阅读PDF时链接PDF；已公开共享作品且原记录提供证明行范围时生成精确源码行链接。没有证据的PDF、页数、学科、难度和运行结果不猜测。历史映射待定位与旧题证丢失须区分。

网页端工具可先读小入口和相关分页，入选前再读题证及必要上下文。工具读不到的对应页／文件可以单独补交，无需让用户预先搬运全库。

## 生成路径与接口

[prepared_retirements.write_active_indexes](editable-corpus/prepared_retirements.py) 继续作为活动材料投影入口，按现有manifest和catalog生成机器目录，并调用 [reader_catalog](editable-corpus/reader_catalog.py) 生成阅读页。

- `render_reader_files(corpus, manifest, catalog)`：只读，返回相对路径到UTF-8文本的映射。
- `write_reader_catalog(...)`：只写上述导航文件，固定LF；不改作者原件、manifest或注册表。
- `active_index_files(...)`：列出本次全部生成路径，供现有prepare、失败续作和明确暂存白名单使用。
- `prepared_publish.CONSUMER_HELPERS` 包含reader模块，消费者取得相同实现；嵌套阅读页的恢复备份创建其父目录。

旧 `corpus-work/scripts/sync_editable_projections.py` 服务于历史 verified-editable-TeX 逐题包，不是混合总库的阅读入口；总库导航不能作为它的旧五列表格输入。旧说明保留在Git历史，不沿旧标签、数字或控制提示恢复任务。

## 复现命令

使用现有Python 3.10+，仅依赖标准库；不安装新依赖。

```sh
bash run_reader_catalog.sh generate
bash run_reader_catalog.sh check
bash run_reader_catalog.sh links
bash run_reader_catalog.sh test
```

PowerShell等环境也可直接运行：

```text
python -B editable-corpus/reader_catalog.py
python -B editable-corpus/reader_catalog.py --check --check-links
python -B -m unittest discover -s corpus-work/tests -p test_reader_catalog.py -v
```

`generate`沿现有投影入口同步元数据与阅读目录；`check`核对当前manifest成员、核心元数据及应生成页面；`test`只运行本次相关回归。必要验证通过后不扩大到全库构建或作者数学复审。

## 发布与运行副本

本仓库的代码和生产环境使用的运行副本必须区分。公开helper更新不证明正在运行的副本已替换；部署应由原共享库单写者在安全窗口沿既有流程完成。目录更新不转移正式ID分配、材料采用、共享状态或发布职责，不操控其他会话。

本轮仅改阅读组织及其直接生成／暂存／续作衔接。原有数据库恢复链、来源许可及在途材料继续保留；禁止批量删除、强推、覆盖他人改动、新建调度器或自动化。

[本轮实际验证与复用](notes/PROJECT_REUSE.md)。[此前项目说明的固定历史版本](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/d4077e447681a460ce95ddf2ef4da24b08d10a06/PROJECT.md)用于追溯旧决策，不能覆盖本次明确范围。
