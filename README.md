# 人类数学证明题库 · Human-Proof Mathematics Corpus

> **这是一个"题目 + 完整人类证明"的数据库本体。** 每条记录 = 一道高于博士资格考水平的数学命题，
> 连同作者本人的完整证明、可编译的 LaTeX 源码、来源定位与许可证证据。
>
> 当前规模：**见 `manifest.json` 的 `items` 数量**（与 `corpus.sqlite` 的 `problems` 表行数一致）。

---

## 1. 题库本体（先看这里）

| 你要的东西 | 位置 | 说明 |
|---|---|---|
| **全量题目清单** | **[`INDEX.md`](editable-corpus/INDEX.md)** | 每题一行：题号 · 题名 · 难度(H2/H3) · 可编辑 TeX 链接 · 作者原文链接 · 原文定位 |
| **数据库** | **[`corpus.sqlite`](editable-corpus/corpus.sqlite)** | SQLite；`problems`（题目/证明元数据）、`sources`（来源与定位） |
| **题目 + 证明的 TeX** | **[`items/`](editable-corpus/items/)** | 每题一个 `.tex`：可直接 xelatex 编译；文件名为 `<题号>_<来源简写>.tex` |
| **来源原文与定位** | **[`sources/<题号>/`](editable-corpus/sources/)** | `primary.excerpt.tex`（保留跨度的原文片段）、`provenance.json`（URL、版本、定位信息） |
| **许可证证据** | **[`licenses/`](editable-corpus/licenses/)** | 每题的许可证 notice（许可类型、作者、再分发范围、未包含的发行商类文件） |
| **编译回执** | **[`receipts/`](editable-corpus/receipts/)** | 每题 `ok / passes / shell_escape / 输入输出哈希`，可用于复现编译 |
| **交付证据** | **[`delivery-evidence.json`](editable-corpus/delivery-evidence.json)** | 每题交付字节的哈希、独立题元、保真回执（哪些行被省略、为什么） |
| **包清单与哈希** | **[`manifest.json`](editable-corpus/manifest.json)** | 本包所有文件与每题交付物的 sha256；用于逐字节校验 |

### 📑 文档导航（全部为本包内的相对链接，点开即达）

| 文档 | 内容 | 适合谁 |
|---|---|---|
| [`INDEX.md`](editable-corpus/INDEX.md) | **逐题清单**（题号·题名·难度·TeX 链接·作者原文·原文定位）——题库主入口 | 所有人 |
| [`CORPUS_INDEX.md`](editable-corpus/CORPUS_INDEX.md) | 增强版清单：附 arXiv id/版本、计数命题、难度、许可证、交付哈希 | 需要核验来源的人 |
| [`catalog.csv`](editable-corpus/catalog.csv) · [`catalog.json`](editable-corpus/catalog.json) | 同上，机器可读（表格/程序直接消费） | 做数据分析的人 |
| [`SOURCES.md`](editable-corpus/SOURCES.md) | 来源与许可说明：候选池、过滤表达式、许可政策、撤回处理 | 关心合规的人 |
| [`DELIVERIES.md`](editable-corpus/DELIVERIES.md) | 交付台账：每批条目数与 `public_exact_commit_full<N>_restored_verified` 提交 | 审计交付历史的人 |
| [`manifest.json`](editable-corpus/manifest.json) · [`delivery-evidence.json`](editable-corpus/delivery-evidence.json) | 逐文件哈希 / 逐题交付证据与保真回执 | 校验字节一致性的人 |

### 30 秒上手

```bash
# 1) 看清单（人读）
less INDEX.md

# 2) 查数据库
sqlite3 corpus.sqlite "select problem_id, title, difficulty from problems limit 10;"
sqlite3 corpus.sqlite "select * from problems where problem_id='127363';"

# 3) 编译某一题的证明
cd items && xelatex 127363_arXiv2206.12041.tex     # 文件名见 INDEX.md 链接
```

---

## 2. 这批题是怎么来的（可核验）

1. **来源**：arXiv 上以 **CC BY 4.0** 许可发布的数学论文（数学分类），以及既有开放获取来源（EJDE、Stacks 等历史家族）；
   许可过滤与逐题证据见 `licenses/`、`sources/<题号>/provenance.json`。
2. **选题标准**：每题必须有**作者本人的完整证明**，且难度高于普通博士资格考（H2/H3）；证明不完整、依赖未交付文献、或无定理—证明结构的论文一律不收录。
3. **保真**：交付的 TeX 是原文的**逐行保留**（跨度精确到定理/证明环境）；若有省略（图形包含命令等），逐条记入
   `delivery-evidence.json` 的保真回执，并保证"声明数量 = 实际差异行数"。
4. **不编造**：不含任何 AI 生成或补写的数学内容；原文印刷错误照原样保留。

---

## 3. 辅助材料（次要，按需查看）

| 位置 | 用途 |
|---|---|
| `validation-artifact-parts/` · `validation-artifact-deltas/` · `validation-artifact-delivery.json` · `validation-chain.json` | 交付校验链（逐级哈希），供审计复现 |
| `rebuild_database.py` · `restore_database.py` · `test_database.py` · `schema.sql` | 由 `manifest.json`/`delivery-evidence.json` 重建并校验 `corpus.sqlite` |
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

*本 README 由语料控制流程维护；每次合并发布时刷新，与 `manifest.json` 的规模保持一致。*

