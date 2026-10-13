# 人类数学证明题库 · Human-Proof Mathematics Corpus

> **这是可编辑数学题证与来源证据的材料库。** 历史标签和 prepared 材料不自动成为符合当前 H2/H3 标准的题。
> 14,866 条历史公开材料与本轮实质审核、修复并公开恢复的 9 条分别计数；全库新标准资格总数尚未完成重核，详见[根 README](../README.md)。
>
> `manifest.json` 的 `items` 是材料范围；`INDEX.md`、旧交付 evidence 和数据库分段描述有各自的快照覆盖范围，不保证与后续 prepared 材料等量。`verified_count` 字段或技术检查通过不能单独证明科学资格。

---

## 1. 题库本体（先看这里）

| 你要的东西 | 位置 | 说明 |
|---|---|---|
| **交付清单** | **[`INDEX.md`](INDEX.md)** | 已有交付范围的题号、题名、历史难度标签、TeX 与来源定位；不覆盖全部后续 prepared 材料，不作资格计数 |
| **数据库恢复** | **[恢复范围说明](#数据库恢复范围)** | 恢复后生成 `corpus.sqlite`；`problems` 保存题证全文及元数据，`sources` 保存来源与定位 |
| **题目 + 证明的 TeX** | **[`items/`](items/)** | 每题一个 `.tex`：可直接 xelatex 编译；文件名为 `<题号>_<来源简写>.tex` |
| **来源原文与定位** | **[`sources/<题号>/`](sources/)** | `primary.excerpt.tex`（保留跨度的原文片段）、`provenance.json`（URL、版本、定位信息） |
| **许可证证据** | **[`licenses/`](licenses/)** | 每题的许可证 notice（许可类型、作者、再分发范围、未包含的发行商类文件） |
| **编译回执** | **[`receipts/`](receipts/)** | 每题 `ok / passes / shell_escape / 输入输出哈希`，可用于复现编译 |
| **旧交付证据** | **[`delivery-evidence.json`](delivery-evidence.json)** | 对应交付范围的字节哈希、独立题元、保真回执（哪些行被省略、为什么）；不覆盖全部后续 prepared 材料 |
| **材料清单** | **[`manifest.json`](manifest.json)** | 材料范围与元数据；旧交付含字节哈希，revision-v2 使用任务/版本/审阅身份，不能强补内容指纹 |

### 📑 文档导航（全部为本包内的相对链接，点开即达）

| 文档 | 内容 | 适合谁 |
|---|---|---|
| [`INDEX.md`](INDEX.md) | **已有交付清单**（题号·题名·历史难度标签·TeX 链接·作者原文·原文定位）；后续 prepared 材料另见 manifest | 所有人 |
| [`CORPUS_INDEX.md`](CORPUS_INDEX.md) | 增强版清单：附 arXiv id/版本、计数命题、难度、许可证、交付哈希 | 需要核验来源的人 |
| [`catalog.csv`](catalog.csv) · [`catalog.json`](catalog.json) | 同上，机器可读（表格/程序直接消费） | 做数据分析的人 |
| [`SOURCES.md`](SOURCES.md) | 来源与许可说明：候选池、过滤表达式、许可政策、撤回处理 | 关心合规的人 |
| [`DELIVERIES.md`](DELIVERIES.md) | 历史交付台账：6021–6759 的八个检查点；后续恢复入口见下文 | 审计交付历史的人 |
| [`manifest.json`](manifest.json) · [`delivery-evidence.json`](delivery-evidence.json) | 材料清单 / 对应旧交付范围的哈希与保真回执；先确认覆盖范围 | 核验材料的人 |

### 30 秒上手

```bash
# 1) 看清单（人读）
less INDEX.md

# 2) 按下文恢复范围取得匹配快照的数据库后，再查询
sqlite3 corpus.sqlite "select problem_id, title, difficulty_level from problems limit 10;"
sqlite3 corpus.sqlite "select * from problems where problem_id='127363';"

# 3) 编译某一题的证明
cd items && xelatex 127363_arXiv2206.12041.tex     # 文件名见 INDEX.md 链接
```

---

### 数据库恢复范围

- [RECOVERY_CURRENT.md](RECOVERY_CURRENT.md) 与 [database-delivery.json](database-delivery.json) 保留 14,875 条交付的分段恢复说明。旧 `restore_database.py` 要求 manifest 与描述中的身份一致；不能把旧分段与后续扩展的 manifest 混用。
- revision-v2 材料使用 [prepared-database.json](prepared-database.json) 的基础分段、delta 和资格审阅记录，以及 [prepared_publish.py](prepared_publish.py) 的精确提交恢复入口。先查看 `python3 prepared_publish.py restore --help`，选择同一提交的材料及独立输出目录；旧 `schema.sql`/`rebuild_database.py` 不适用于整个 revision-v2 库。
- 已有同一提交的数据库快照时，可用 `prepared_delivery.py verify-db --database PATH --manifest MANIFEST` 检查结构和元数据。该检查不比较全文与交付 TeX 的逐字节一致性；其按 basis 分组的统计也不能直接当作全库新标准合格数。

---

## 2. 这批题是怎么来的（可核验）

1. **来源**：arXiv 上以 **CC BY 4.0** 许可发布的数学论文（数学分类），以及既有开放获取来源（EJDE、Stacks 等历史家族）；
   许可过滤与逐题证据见 `licenses/`、`sources/<题号>/provenance.json`。
2. **当前资格标准**：要求完整作者题证、必要新局部核心、准确来源与许可、语义唯一性及具体 H2/H3 难度理由；标准先修可保留准确引用。材料收集、历史标签或 prepared 状态不能代替这项审核，详见[项目 skill](../corpus-work/.agents/skills/human-proof-corpus/SKILL.md)。
3. **保真**：交付的 TeX 是原文的**逐行保留**（跨度精确到定理/证明环境）；若有省略（图形包含命令等），逐条记入
   `delivery-evidence.json` 的保真回执，并保证"声明数量 = 实际差异行数"。
4. **作者原文与披露**：整理者不得生成或补写数学证明；原文印刷错误保留并单独说明。作者披露 AI 辅助起草且经作者实质修改的材料按逐项审阅保留披露，不统称为 AI-free；题号 191078 的披露与审阅依据见[根 README](../README.md)。

---

## 3. 辅助材料（次要，按需查看）

| 位置 | 用途 |
|---|---|
| `validation-artifact-parts/` · `validation-artifact-deltas/` · `validation-artifact-delivery.json` · `validation-chain.json` | 交付校验链（逐级哈希），供审计复现 |
| `rebuild_database.py` · `restore_database.py` · `test_database.py` · `schema.sql` | 旧交付范围的全文 SQLite 重建、分段恢复与校验；输入必须匹配该范围 |
| `prepared-database.json` · `prepared_publish.py` · `prepared_delivery.py` | revision-v2 恢复描述、精确提交恢复及结构/元数据检查 |
| `restore_validation_artifacts.py` · `restore_validation_chain.py` · `test_restore_database.py` | 校验链恢复与自测 |
| `SOURCE_PATHS.json` · `provenance.json` | 来源路径索引与包级来源说明 |
| `assets/` | 来源家族层面的辅助材料（如书目文件） |

> 这些是**工具与审计材料**，不是题库内容。只想读题的人可以完全忽略这一节。

---

## 4. 许可与再分发

- 仅收录**允许直接再分发**的许可（arXiv 的 CC BY 系列为主）；**不含** CC BY-SA / NC / ND 语料，**不含**形式化证明库。
- 作者署名与出处**逐题保留**在 `licenses/` 与 `sources/<题号>/provenance.json` 中。
- 发行商排版类文件（IEEEtran / imsart / sn-jnl / informs3 / ejpecm / lmcs / acmart 等）**一律不随包转发**；
  交付 TeX 使用中性的 amsart 包装并复述论文自己的宏与定理环境声明。
- 若发现任何条目与上述声明不符，请开 issue 指出题号，我们会更正或撤下该条。

---

*本页说明阅读入口与覆盖范围；生成型 INDEX、manifest、delivery evidence 和恢复描述以各自发布流程为准，不由本页更新材料或资格计数。*

