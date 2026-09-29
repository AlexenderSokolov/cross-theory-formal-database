# Claude Code本地工具与参考项目

核对日期：2026-09-28。以下“支持什么”来自官方文档或项目README；“在本项目怎样用”是工作流建议。没有对本地Claude Code做速度基准，以下配置不承诺固定加速倍数。

## 一、先用最少的工具

| 组件 | 本项目用途 | 建议 |
|---|---|---|
| Claude Code项目skill与CLAUDE.md | 固定研究边界，按需加载取材过程 | 本包已经给出目录；不必安装另一个技能管理器 |
| Python 3.10+、Git、curl、ripgrep | 文件保存/版本、原件下载、题名与全文搜索 | 首批直接使用；本包发布脚本只依赖Python标准库 |
| Poppler工具（pdftotext、pdftoppm、pdfinfo） | 定位PDF正文与查看特定公式页 | 不做OCR批量扫描；文本PDF先提取文本 |
| 已有TeX Live / XeLaTeX；latexmk可选 | 每道新TeX的可读性与引用排版 | ctex通常需中文支持；只安装一次，不每题部署；没有编译器先留可读TeX并记录未编译 |

官方入口：[技能](https://code.claude.com/docs/en/skills)、[项目记忆](https://code.claude.com/docs/en/memory)、[Git](https://git-scm.com/docs)、[curl](https://curl.se/docs/)、[ripgrep](https://github.com/BurntSushi/ripgrep)、[Poppler](https://poppler.freedesktop.org/)、[latexmk](https://ctan.org/pkg/latexmk)。

已有工具先检查，不自动修改用户机器：

```bash
python3 --version
git --version
curl --version
rg --version
command -v pdftotext pdftoppm pdfinfo xelatex latexmk
claude --version
```

Windows环境可按Claude Code[官方安装说明](https://code.claude.com/docs/en/setup)选择WSL或原生环境；本包命令例子采用Linux/WSL shell，Python文件工具本身使用标准库。WSL中建议在自己的Linux工作目录执行，不假定能读到网页端历史目录。

## 二、实用取材命令

下面的URL、页码和文件名是待替换示例，不是已经下载的来源。对来源分别命名，失败请求不能覆盖已有原件。

```bash
mkdir -p .work/cache/sourceA
# 先写临时文件，失败就不把它命名为正式原件。
curl --fail --location --retry 2 --connect-timeout 20 --max-time 180 \
  --output .work/cache/sourceA/source.pdf.part '实际作者PDF地址'
# 检查成功后才移动到新的source版本目录；不覆盖旧文件。
pdfinfo .work/cache/sourceA/source.pdf.part
sha256sum .work/cache/sourceA/source.pdf.part

# pdftotext通常使用从1起的PDF物理页码；与书内页码分别记录。
pdftotext -layout -f 15 -l 19 source.pdf excerpt.txt
pdftoppm -f 17 -l 17 -singlefile -r 150 -png source.pdf page17
rg -n -i -- 'theorem|proposition|proof|关键定理名' excerpt.txt
```

`pdftotext`用来定位，不负责可信地还原数学排版。页面图用于核对上下标、括号、换行、图示和跨页续证；不把图片OCR结果直接作为参考证明。必要图可作为原图摘录随题保存，不由AI重绘替换作者图。

新增题的编译资源路径相对 `corpus/tex/`（例如 `../sources/<来源键>/figure.png`）；来源说明中的原件路径则相对corpus根目录。合并时修资源路径，不改作者数学内容。

编译示例（从项目根启动，只对自己整理的独立文件执行，关闭shell escape）：

```bash
PROJECT_ROOT="$(pwd)"
mkdir -p "$PROJECT_ROOT/.work/build/101"
(cd corpus/tex && xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error \
  -output-directory="$PROJECT_ROOT/.work/build/101" '101_实际题名.tex')
# 同一命令再执行一遍，确认引用稳定。
```

`-no-shell-escape`只关闭shell escape，并不等于完整TeX安全沙箱；不编译未经检查的上游入口。latexmk可代替手工控制多遍编译。不要运行来源仓库的任意Makefile/latexmkrc，也不为修排版擅自修改作者公式。PDF、OCR或解析工具的许可证，不自动成为所处理书籍的许可。

## 三、参考项目：按需要增加，不全装

### anthropics/skills：PDF与skill-creator

[仓库](https://github.com/anthropics/skills)；[PDF技能](https://github.com/anthropics/skills/tree/main/skills/pdf)；[skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)。前者适合查PDF处理方法，后者适合迭代skill的触发和行为用例。它们不是数学真伪评判器。按所用子目录的许可证处理，不把整个仓库一概当成同一种许可。

本包的题证取材skill可独立运行。首次扩充不用额外跑一次大规模技能评测，也不用复制整套文档生成工具。

### obra/superpowers：维护流程与脚本时有用

[项目](https://github.com/obra/superpowers)。适合修改发布脚本时做TDD、调试和执行检查；普通取材不按每题启动软件设计、计划审批、审稿循环。已有用户批准的建库规则直接执行。

其当前README给出的Claude Code安装入口之一：

```text
/plugin install superpowers@claude-plugins-official
```

这是用户选择安装的命令，不由本工作包自动执行。使用时以本项目最新任务为准：不让通用软件开发流程把题证收集变成新平台建设。

### Microsoft Playwright：遇到真实浏览器需求时再启用

优先阅读[Playwright CLI](https://github.com/microsoft/playwright-cli)；需要持续浏览器状态和MCP工具时再用[Playwright MCP](https://github.com/microsoft/playwright-mcp)。微软当前MCP README明确区分CLI+skills与MCP两种用法，CLI更适合控制上下文开销；MCP适合需要持续页面交互状态的任务。

对于静态TeX、PDF链接和作者普通网页，curl/现有WebFetch已经够用。只有动态页面或确需浏览器渲染的下载入口才加浏览器。不要拿浏览器无界抓站，更不绕过访问控制。

### NaturalProofs：候选发现而非批量自动入库

[项目](https://github.com/wellecks/naturalproofs)。可查结构化定理、证明及引用关系，帮助定位来源。最终仍读作者正文、查旧题、核对核心证明与许可。不为了建库运行其模型训练或检索评测实验。

## 四、并行配置：主会话负责合并，两个取材窗口负责文件

Claude Code官方支持[自定义子代理](https://code.claude.com/docs/en/sub-agents)。本包在 `.claude/agents/proof-collector.md` 给出一个可选模板；其 `skills` 字段预载本建库skill，不固定模型名称或额外预算。

先完成一题完整流程，再最多同时开两个取材任务。每个任务收到绝对路径、限定来源/主题、已有近邻、待交付文件和独占候选目录。子代理没有主会话全部历史，必须显式传这些信息。

两个执行者均不写corpus、总目录和最终编号；主会话从在途表和成品文件进行合并前排重，再串行入库。子代理写 `candidate.tex` 而非占用101/102，减少空号与撞号。该分工不是AI审核链。独占目录是工作约定，不是操作系统隔离；主会话仍须检查实际输出路径。

[Git worktree](https://git-scm.com/docs/git-worktree)留给多个独立CLI会话需要隔离工作树时使用。当前一主会话加两个候选目录不必为每题创建worktree，更不要提前清理仍含未合并题证的工作树。

## 五、恢复与备份

Claude Code提供 `claude --continue`、`claude --resume` 等[会话续接入口](https://code.claude.com/docs/en/cli-reference)。恢复后仍读BATCH_STATE及真实文件：会话记忆不是题库本体。

官方[checkpointing说明](https://code.claude.com/docs/en/checkpointing)指出，Bash造成的文件修改不由rewind跟踪，许多子代理修改也不能靠主会话rewind恢复。因此Python生成、curl下载和子代理写出的题证，要靠实文件、Git与检查点保存，而不是只依赖聊天回退。

每5题建立一次含正文的本地检查点，每批完成交付一个累计ZIP；发布成功后新建累计主TeX基线，下一批使用该新路径检查全部既有题证。初次使用可在用户确认的工作目录初始化Git并提交基线；后续只提交明确的题证、来源、状态和流程文件，先看 `git status`。本包不自动初始化或推送仓库。

同盘Git与ZIP保护修改历史，不保护整块磁盘损坏。按自己的存储政策将完整发布包另存一份；不要默认推送公开仓库，也不上传API密钥、会话凭据或浏览器profile。

## 六、现在不需要的组件

不装AI数学judge、Lean自动形式化流水线、Dafny/TLA+审稿链、全库向量数据库或复杂代理编排平台。它们对应其它任务，不是这轮“多收可靠题证”的前置条件。也不把Nougat/Marker等批量数学OCR转换作为默认可信入口：先解决原生文本和少量原页对照。

本地效率主要来自原件缓存、连续题源、短主上下文、受控并行和持久保存。换成本地并不意味着可以省去核心证明、来源位置或排重。
