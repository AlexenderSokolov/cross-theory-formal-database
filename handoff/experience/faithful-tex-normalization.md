# 忠实、可编辑数学语料的本地规范化流程与经验

本文供本地扩展到 30,000 条时复用。目标是交付有明确人类作者、完整题陈与证明、许可明确、可编辑且能复核的独立成果。数量目标不改变准入标准。下列路径均为仓库相对路径；命令从包含 `scripts/` 的工具工作根目录执行，不依赖本次云端临时目录。

## 1. 先固定一个独立成果，再处理排版

- 每条记录固定原始作者、作品、DOI、确切版本、原 PDF 哈希、原定理编号、假设、结论和所选范围。物理页码、印刷页码、源文件行号分别记录。
- 一个稳定 ID 对应一个独立原始成果。证明内的引理、定义、参数代入、维数特例及必要上下文不增加计数。同一论文可包含真正不同的成果，但必须先做结论和证明机制的去重。
- 按已有 H1/H2/H3 标尺保守定级，并写出超出普通博士资格考试的具体剩余难点。篇幅、符号密度、声称使用高级定理，本身不构成难度证据。
- 明确区分精确命名的已知先决结果与本文新核心。先决结果可按原文引用并保留所需假设；作者本篇新引理、构造、分类、归纳与最后收束必须完整交付。不能用一个引用代替尚未提供的新核心。
- 检查材料完整性、假设、范围、转录和可读性，不作独立数学审稿或重新证明。原文疑点逐字保留并披露；不能自行修正公式、补桥接证明，或把更强命题算作成果。

## 2. 版本和许可先于下载后的加工

优先使用确切版本的官方 native TeX。只有 PDF 可合法复用时，采用严格的已发表 PDF 校对转录，并使用 `human_authored_checked_published_transcription`。非独占、NC-ND 或其他受限 native 源即使可读取，也不能自动成为公开 native 复用依据；可留作私有辅助，但不能公开其源码、类文件、前导区、注释或未发表差异，也不能声称 native 字节相等。

许可检查必须把当前作者、题名、DOI、native 版本与哈希、PDF 哈希、许可链接对应到同一份来源。native 与 PDF 的许可可能不同；混合组件须分别注明。一个 notice 的哈希正确，只能证明字节没变，不能证明它属于这篇论文。加入“换成另一篇文章的 notice 应当失败”的负例检查。

公开见证应是最小事实文本或 JSON：作者、题名、版本、DOI、来源 URL、观测到的许可声明和链接、原 PDF/采集文档哈希。不要直接公开抓取的 HTML；`.txt` 后缀也可能存着整页 HTML。递归检查公开清单中的文本和 JSON 字符串，排除脚本、无关表单、隐藏字段、CSRF/session 类值、认证头和 cookie 值。报告字段名和类别，不输出值。发现 `csrfmiddlewaretoken` 不等于已证实用户凭据；原抓取认证状态缺乏证据时，明确写“未记录”，不推断。

保留原采集响应为私有证据，单独冻结安全见证修订及新哈希；原敏感 HTML 不能作为公开“历史版本”进入 Git 或公开恢复包。遇到访问或审批拒绝，保留失败记录，停止该动作，不改 URL、重编码或换上传接口绕过。

## 3. 可搬运的正文与精确绑定

1. 在新目录中准备一组已准入 ID，固定输入清单、正向公开清单与哈希。工作组互不写入；旧修订、失败尝试和已冻结输出保持原状。
2. 生成完整的独立 TeX，并把题陈、完整证明、所有所需新核心、必要定义和完整参考文献内联。原编号、假设、上下文和结尾不能截断；尤其检查跨行脚注、环境闭合和正文之后的收束。
3. 保存可搬运的 source carrier。所有主题陈、主证明及新核心绑定到 `source_index: 0` 的公开 carrier；不得依靠私有目录或执行时临时文件才能通过验证。
4. 逐块校验来源行范围、交付行范围和片段哈希。行号为 1-based、闭区间。明确区分“片段内容哈希”和“片段末尾带一个 LF 的哈希”，不能混用。
5. 为 `contexts` 同时提供精确 body span 与 `source_excerpt_path`；仅保存摘录文件而未把它关联到 evidence，门禁仍会失败。一个 spans 列表须有序且互不重叠；嵌套的新核心可用分开的 context 记录表达。
6. 若排除不印刷的注释，按反斜杠奇偶性判断 `%`，保留真正的换行/连接 guard。只对原作者明确定义的分支作机械选择，例如 `conf=0`；保留物理换行并重放验证。不能把参考文献中的普通条件排版误删为另一版本分支。
7. 图中文字、公式与标签必须保持可编辑。确有必要的原图组件单独声明许可、文件和哈希；完整证明不能用截图或 PDF 页替代。混合转录不得冒充纯 native。

公开数据包使用正向清单，只选择已授权的正文、carrier、原 PDF、必要资产、许可与核查记录。草稿、私有辅助、未使用的类和宏包、原始 HTML、可再生的非输入 QA 图不成为正文依赖。

## 4. 本地运行时与实际编译

需要 Python 3、SQLite、XeLaTeX/TeX Live、Poppler，以及项目使用的 `pypdf`、PyMuPDF (`fitz`)、Pillow、NumPy。常见正版运行时包括 `fontspec`、AMS 系列、`hyperref`、`enumitem`、`mathrsfs`，Latin Modern、Computer Modern、RSFS、Euler 字体；按实际 FLS 与嵌入字体清单补充。先检查安装状态，再处理材料。

```bash
python3 --version
xelatex --version
kpsewhich fontspec.sty
kpsewhich mathrsfs.sty
pdffonts -v
```

必要的第三方运行时只能使用有出处、版本、哈希与许可的真实包。需要随包携带时附原许可和署名；例如 `IEEEtrantools.sty` 应使用真实官方包，并把其目录放入包的 `TEXINPUTS`，末尾保留冒号以继续查找标准运行时。不要模拟缺少的 `.sty`，也不为未选正文中一个未使用的宏包反复下载。

下面的目录是可替换的本地工作目录示例。先准备已核准的 `manifest.json`、`delivery-evidence.json`、正文和 assets。

```bash
CORPUS_PACKAGE="$PWD/work/packet-001/editable-corpus"
PROOF_BUILDS="$PWD/work/packet-001-build"
PROOF_RECEIPTS="$PWD/work/packet-001-receipts"
PROOF_REPORTS="$PWD/work/packet-001-reports"
mkdir -p "$PROOF_REPORTS"

python3 scripts/compile_editable_delivery.py \
  --package "$CORPUS_PACKAGE" \
  --build-root "$PROOF_BUILDS" \
  --receipt-root "$PROOF_RECEIPTS"
```

编译实际使用：

```bash
xelatex -no-shell-escape -interaction=nonstopmode \
  -halt-on-error -file-line-error -recorder \
  -output-directory=实际构建目录 实际入口.tex
```

记录真实的 2–4 次成功调用、退出码、输入、依赖、PDF、最终 TeX 日志和 compiler stdout 哈希。标准 helper 在第 2 次后无 rerun 请求时可能停止；`compile_passes_requested` 不是已执行次数。若需要第 3 次稳定性证据，应先保存实际第 2 次 aux/log/FLS，再真正执行第 3 次并追加 stdout，不能手填 passes。source 收据与 fresh 收据的字段可能不同，须保留原语义，不能补造不存在的字段或 `.out` 文件。

最终引用、文献、标签、缺字和 rerun 诊断须清空。比较 aux/FLS；日志时间头可能改变，不能因此声称整个日志字节相同。PDF 的日期或对象元数据改变也不代表页面数学改变。已有 Underfull/Overfull 逐项保留，通过实际整页检查确认可读性；`Warning:` 为零不代表排版诊断为零。页面裁切必须修正独立 wrapper 排版修订并重编译，不能降低边缘检查阈值或改作者正文。

## 5. 页面、字体、门禁和全文数据库

实际查看每一页新输出，以及所选来源页、身份/许可页、完整证明结尾和文献页。检查 MediaBox、公式重叠、脚注、图标签、页脚和缺字。与已核准输出逐页在内存中比较，再保存小型 contact sheet；不必同时保存大量全页 raster。字体相似不能替代符号一致，尤其应核查字母大小写、上下标、闭包横线、矩阵括号、箭头、有限脚本字母和希腊字母。嵌入 subset 名、FLS 真正输入与安装字体 design 的哈希是不同事实，不能混称字节相等。

检查真实编译收据后，把对应收据纳入候选包；准备包自己的 `INDEX.md`、受约束的 `schema.sql` 与完整 `corpus.sqlite`。保持数据库中的全文 TeX 与文件逐字相等，不存 PDF 包装器或外部文件占位。

```bash
ITEM_ID="本组实际ID"
python3 scripts/validate_corpus.py --mode editable-delivery \
  --package "$CORPUS_PACKAGE" \
  --evidence "$CORPUS_PACKAGE/delivery-evidence.json" \
  --build-root "$PROOF_BUILDS" --receipt-root "$PROOF_RECEIPTS" --item "$ITEM_ID" \
  --report "$PROOF_REPORTS/item.json"

python3 scripts/validate_corpus.py --mode editable-delivery \
  --package "$CORPUS_PACKAGE" \
  --evidence "$CORPUS_PACKAGE/delivery-evidence.json" \
  --build-root "$PROOF_BUILDS" --receipt-root "$PROOF_RECEIPTS" \
  --report "$PROOF_REPORTS/aggregate.json"
```

两个 CLI 都必须实际执行并返回成功，逐项和聚合报告均无 errors。strict published-transcription 条目还须通过对应的 published evidence 门禁。不得关闭原验证器、修改 schema 限制或把缺项标成 waived 来凑数。

交付包附有 `rebuild_database.py` 时，可从已冻结 manifest/TeX/收据生成一个新的数据库文件：

```bash
python3 "$CORPUS_PACKAGE/rebuild_database.py" \
  --output "$PROOF_REPORTS/rebuilt-corpus.sqlite"
```

对于压缩数据库交付，使用包内 `restore_database.py` 校验有序分片大小、哈希、整库哈希、manifest、行集合、外键和全文；脚本拒绝覆盖不同的现存数据库。重建数据库与按分片恢复原数据库是不同验证，不能只凭行数相等声称字节恢复成功。source 行数可能少于 problem 行数；共享论文须有一致 source 身份。

## 6. 冻结、去重和发布边界

所有门禁通过后，冻结 READY、正向 PUBLISH 清单、HASH manifest、实际 build 和 SQLite 核查收据。发布前再次检查哈希，集成后重新执行受影响逐项与全包门禁。source 已批准、局部已规范化、固定 intake 已核准、Git 已远端读回是不同状态，不互相代替计数。

已冻结 intake 不接受“顺便加上”的新 ID。新增成果另建工作组；不同人只写自己的组，由唯一发布者整合。相同 ID 的修订保持原成果身份，不增加数量；相同结论的不同版本或参数表达先做去重。生成内容相同、已能从冻结来源/Git 准确恢复的临时副本，可以先清点磁盘潜在节省，再经授权处理，不删除原始证据。

更改 attribution、license witness 或 schema 描述时采用独立修订：证明/编译没变就不声称重新编译，当前正向清单却必须绑定新 notice/描述的哈希。恢复清单记录相对路径、mode、blob 哈希和所需原输入；公开恢复包选当前安全见证，不能自动回收被排除的原始 HTML。

## 7. 本次拖慢流程的因素与对应改进

| 因素 | 本地扩展时的处理 |
| --- | --- |
| 不同来源收据与 allowlist 字段略异，复制模板留下旧 ID、scope、页数或字体声明 | 先读取真实 schema；从当前数据生成声明。冻结前自动搜索旧 ID、原文与版次的残留，断言来源身份 |
| 未闭合脚注、遗漏 authored 新核心或文献使候选需回做 | 截取前确定完整结构和正文结束位置；完整块重放先于昂贵编译/逐字 glyph QA |
| context 摘录存在却缺 evidence 关联，或 LF 哈希约定不一致 | 同时生成正文 span、source span、摘录路径和明确 LF 约定；先跑 body gate |
| aux 标签含嵌套花括号，简单正则截断结果 | 用平衡括号解析器读取完整 label/bibcite 值 |
| 每组全页图、副本和大 JSON 累积，云端磁盘频繁接近上限 | 本地预留容量，比较 raster 时逐页用内存，小 contact sheet；按唯一 inode 计算新增分配，硬链接不能重复算存储 |
| 已完成的旧包因字段修订重复编译、重复全量检查 | 明确 metadata-only 与数学/布局变化；只重跑受影响门禁，并保留已有有效 build |
| copied notice 属于另一论文，或 raw HTML 混入 CSRF/form 数据，发布晚期被拒 | 来源身份和安全 witness 检查提前到采集准入；公开清单只选事实见证及需要的源材料 |
| 未固定 intake、多人并发修改共享包，或结果只留在临时目录 | 小组隔离、单一发布、明确冻结计数；尽早作可验证恢复包并将可复用工具和文档纳入仓库 |

扩展时优先选择许可与确切版本清楚、native 可编辑、原证明闭合、核心范围能完整交付的材料。对来源、权利、字形或核心范围不确定的条目保持 pending/HOLD；减少无效回做，比放宽质量标准更能提高有效交付速度。
