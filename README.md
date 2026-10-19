# 人类数学作者题证库

收集数学作者的明确命题、完整证明及必要上下文，保留可编辑 TeX 或原生 Lean、固定作品版本和来源定位，供阅读、选题与研究使用。

**从 [题库阅读入口](editable-corpus/browse/README.md) 开始。** 该页给出当前材料统计、TeX／Lean 小型分页、每页 JSON 与来源导航，适合网页端 GPT 和数学合作者按需读取。

| 要做什么 | 入口 |
|---|---|
| 阅读、搜索候选题 | [TeX 分页](editable-corpus/browse/tex/README.md) · [Lean 分页](editable-corpus/browse/lean/README.md) |
| 按作者来源缩小范围 | [来源目录](editable-corpus/browse/sources.md) |
| 给网页端 GPT 提供材料 | [阅读方法与范围](editable-corpus/browse/README.md#给网页端gpt与合作者) |
| 读取小型机器数据 | [统计与分片位置](editable-corpus/browse/summary.json)，每页配套 JSON |
| 下载全部元数据 | [catalog.json](editable-corpus/catalog.json) · [catalog.csv](editable-corpus/catalog.csv)；文件较大 |
| 按稳定编号定位 | [兼容索引入口](editable-corpus/INDEX.md)，目录行链接既有题证或共享条目 |
| 恢复全文数据库 | [恢复说明](editable-corpus/RECOVERY_CURRENT.md) |
| 维护目录或了解源码 | [PROJECT.md](PROJECT.md) · [运行脚本](run_reader_catalog.sh) |

每道题以稳定字符串 ID 引用。旧逐题 TeX 包与新共享作品、Lean 项目共同保留，分页不复制或改写作者证明。

活动材料总数、已有难度筛选记录、实际运行／编译状态和跨理论标注分别表示不同事情。历史 H2/H3 标签不能单独证明当前难度，Lean 代码存在不能替代内核运行，目录生成不会新增数学判断。作者负责原始数学；本库对材料整理、来源定位及自身修改负责。

跨理论、知识及证明方法分析由具体研究任务开展；这里不自动给全库添加这些标签。选题前应实际阅读对应题面、完整作者证明和必要支撑材料。

各题的实际来源、版本及许可沿用原记录；整库不宣称统一许可证。未公开或访问受限材料不因目录出现就取得再分发许可。

目录由现有活动材料投影入口统一生成。当前数量见阅读入口，避免首页维护第二套数字。[复用说明](notes/PROJECT_REUSE.md)记录本次结构和实际验证边界。
