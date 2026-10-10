# 20 条离线候选试做：最终交接

2026-10-10，基底公开 main `5c133eb3cb70ada8bd3ca187089fe69378e5bc52`。

**20 条均已处理：17 条形成独立小包并通过本地真实编译和既有 item gate，3 条明确 HOLD。** 成品入口见 [INDEX.md](INDEX.md)；逐题内容、上下文、源定位、去重范围和实际结果见 [CANDIDATES.json](CANDIDATES.json)；运行记录见 [ASSEMBLY_REPORT.json](ASSEMBLY_REPORT.json)。

这 17 条是本次本地 pilot 的交付结果，使用 `97000001`—`97000020` 中对应的临时编号；没有生产准入、主库计数增加、远端写入或公开发布。每个临时编号均已与本地 main manifest 和可用 queue 快照检查冲突；未来正式准入仍须总控核验生产 ID。

## 已实际完成

- 逐条读取候选题面与完整作者证明，20 条原文均在完整本机章节中逐字命中。理由独立写为每题 2—4 句，保留背景输入和本题证明义务的差别。
- 17 个可行条目已经实际附入必要定义、节首背景和特定新局部核心。其余标准先修使用准确的 Stacks tag / bibliography 链接，没有递归重证全部依赖，也没有生成新证明。
- 17 包均含完整独立 TeX、逐字源摘录、许可、相对路径 manifest / provenance / INDEX、完整 TeX 的 SQLite、保真 evidence、成功 receipt、gate-result 和 PDF。每包的现有 item gate 实际返回 `editable_qualified_count=1`、`errors=[]`。
- 使用项目已有 `compile_editable_delivery.compile_item` 和 `latexmk_xelatex.cmd`，后者以 `latexmk -xelatex -g` 强制真实引擎运行。每题成功调用两次，`shell_escape=false`；最终无未解决引用、缺字、重复标签或重跑要求。没有安装依赖。
- 全部包装已固定为 A4，左右边距24mm，默认上下24mm；P08为避免孤尾页仅将上下边距调为20mm、隐藏链接边框、清楚的 Counting scope 和 Primary problem tag。支持条目的编号不计为额外题目。
- P12 的上下文修为 `homology.tex:5957–5972` 完整定义与段落；新版 3 页由独立复核者逐页检查，半句、蓝框及孤尾页问题已消除。报告在仓库 `curation/visual-review-pilot-97000012-r002.json`。没有声称全部 17 份最终 PDF 均已逐页人工检查。

## 档位与 HOLD

17 包中为 15 个 H2、2 个 H3。本次 H3 为 P01 弱 Chow 覆盖与 P02 Keel–Mori 整体模空间装配，已有总控独立的限定内容复核，见 [ROOT_REVIEW.json](ROOT_REVIEW.json)。该复核完整阅读主证明并检查直接引用及上下文边界，不声称穷尽全部传递依赖或全库数学等价搜索；Keel–Mori 的局部存在性仍明确记为被引输入。

三条 HOLD 不提供“成功”回执：

1. **P03 / `lemma-brown-bis`**：`derived.tex:11554` 把任意分解得到的 beta_n 都称为被下一步杀掉，而 `11505–11519` 的构造只杀自然变换的核。独立复核确认这不是补前置定义即可解决的原文缺步；保留源文，不补证。
2. **P13 / `lemma-lowering-the-level`**：混合特征 level 证明的估值公式及 K/L、w/w^p 记号存在未解决源文疑点；不静默改成模型判断的公式。
3. **P15 / `lemma-cd-1-canonical`**：收尾 `M'` 未在本条证明中定义。同章其他 `M'` 出现属于此前不同引理/证明的局部变量，不能直接借用；不凭猜测补成逆极限。

P20 的题面与证明之间存在作者对“未来可加强版本”的短说明，完整原段为 `models.tex:5549–5555`，其后 `5556–5649` 明确证明当前引理，未出现另一条命题。装配只对此完全匹配的短间隔作显式配对核查，保留说明原文，不把“下一个 proof”作为普遍猜测规则。

## 来源、许可与文本边界

全部成品来自既有 GNU FDL 1.2-or-later 的 Stacks 来源，跨 15 个章节；这不等于 15 个独立文献来源。许可沿用现有 Stacks 家族与真实 `COPYING`，未修改许可政策；HoTT、Lurie、NUMDAM、MSP 没有混入本批。

来源版本统一如实写为：

> local cached snapshot; exact chapter hashes; revision unknown

本机 `D:/tmp/r2work/repo/` 没有 `.git`，没有将旧固定 PIN 冒充本次快照版本。每个原章节的实际内容哈希与精确摘录定位保存在元数据中，日期是本次本地缓存读取时间。`stacks_extract.py` 新增显式 `source_version` 透传，未提供时保留旧默认值以兼容旧调用。

作者正文除已记录的 ref / label / cite 呈现适配外保持原文。明确的排印问题在独立 editorial reading note 中说明，未混入或替换作者正文。多个短 routine 省略只有逐项给出唯一原句、源行、范围及非核心理由才可通过：旧单条 dict 行为保留，新 list 中任一未覆盖省略或错误 locator 仍被拒绝。逐条实际判断已随候选与 manifest 记录。

## 去重覆盖的实际限度

- 排除了 64 条已知同源主命题标签重叠。
- 本次检索有 432 份可用主摘录；其余 14,434 个主库条目只作标题/claim 元数据比较。
- 另检查 4,016 份已交付上下文。原候选 `proposition-finite-type-flat-at-point` 已随主库十个题包交付，因此替换为 `lemma-nonuniqueness`；最终 20 条没有同标签定义的 context 命中。
- 标签、词面相似和未命中都不是数学等价判定器。本轮只报告上述实查范围，没有将 17 个本地小包直接加入公开唯一题计数。

## 复现

编译原始工作目录与日志在工作树外：

- `C:/Users/20600/Documents/Codex/corpus-repair-20261010-work/pilot-build/`
- `C:/Users/20600/Documents/Codex/corpus-repair-20261010-work/pilot-receipts/`

最终成功 receipt JSON 与 PDF 的副本已随各小包保留。未来正式发布仍应按项目原流程归档对应的编译证据并进行公开恢复，不能把本次本地 gate 当远端恢复。

Windows PowerShell 实测命令：

```powershell
$env:PYTHONUTF8='1'
python corpus-work/scripts/build_research_pilot.py --source D:/tmp/r2work/repo --work C:/Users/20600/Documents/Codex/corpus-repair-20261010-work
```

可以用 `--only 10 11 12` 限定必要的重做条目。源及最终输入没有变化时，不为惯例重编译已经通过的小包。

Bash 入口为 [run_compile.sh](run_compile.sh)，须明确设置 `STACKS_SOURCE`、`PILOT_WORK`，可选 `PYTHON_EXE`。它调用同一脚本和已有 latexmk driver，没有另造编译器或调度器。

针对性测试：

```powershell
python -m unittest discover -s corpus-work/scripts/tests -p test_build_research_pilot.py
```

12 项测试覆盖来源版本透传/旧默认值、明确未知版本、不覆盖所有省略时拒绝、错误源定位拒绝、旧 dict 兼容、LF 字节保真、重叠背景去重与非相邻核心拒绝；也覆盖失败后资格/SQLite/证据投影归零、源码重定位、未审或改变的上下文省略拒绝。实际 PDF 编译和 item gate 属于另外已经执行的证据，不由这些测试替代。

## 独立复核后的必要补正

- 交付目录初始为 pending/0；真实编译后，仅在树外新 gate stage 中准备终态用于现有门禁，通过后才复制绑定元数据和SQLite回交付目录。失败保留旧输入/回执诊断，并将manifest、INDEX、evidence和SQLite的合格投影归零，不留下假绿。
- 素材根据当前仓库的相对archive路径定位，不依赖CANDIDATES中历史C盘路径。默认engine按平台选择cmd/sh，亦可显式--engine；F盘和Windows字体设置只在Windows使用。本轮实际验证的是Windows；非Windows驱动和Fandol字体分支尚未在本轮运行。
- [CONTEXT_REVIEW.json](CONTEXT_REVIEW.json)记录6份随附作者核心中7处短省略的实际审读、源行和非核心理由。构建脚本核对被审摘录的字节与所有已审短句；新出现或改变的省略会被拒绝。没有将评审解释补入作者正文。
- P14补入了原作者delta_Z定义式并仅对该包重编译和重验门禁；P08仅改wrapper纵向留白并重编译、重验门禁。其他已固定PDF没有再动。

## 最终页面与本地交付核验

总控已将最终PDF哈希逐一对应到实际逐页视觉记录：17份全部79页通过；P08与P14的旧版报告保留，并由新版记录明确取代。实际结果见[LOCAL_DELIVERY_CHECK](../../curation/LOCAL_DELIVERY_CHECK.json)。2条H3候选的限定独立内容确认在[ROOT_REVIEW.json](ROOT_REVIEW.json)，其余15条沿本轮具体H2理由。没有正式准入或公开增量。
