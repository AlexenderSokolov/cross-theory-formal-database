# 本地接收与执行命令

本页区分已实现接口和本地待做任务。命令行参数已对照当前程序的`--help`；具体提交、分段哈希与材料数量以本次交接状态和材料清单为准。不要执行旧目录中临时修补脚本来盲目生成新题。

## 1 获取仓库

在已有Git身份配置的本地终端中新建接收目录，不覆盖旧工作区：

```bash
git clone --depth 1 --branch corpus-progress-20261001 --single-branch \
  https://github.com/AlexenderSokolov/cross-theory-formal-database.git \
  cross-theory-formal-database-local
cd cross-theory-formal-database-local
git rev-parse HEAD
git status --short
```

浅克隆只减少首次下载历史，不删除远端历史；当前完整文件仍会取得。后续确需旧提交时再显式fetch。

如仓库访问需要登录，使用本地现有Git凭据或Git Credential Manager等正常登录方式，不把token写进URL、脚本、日志或聊天。交接链接中的确切提交是复核起点。若分支后来有新提交，记录自己实际取得的提交，必要时在干净接收区切换到指定交接提交；不要重置有未保存修改的旧目录。

Windows建议在现有WSL/Linux环境运行这些Bash命令；纯Windows部署需要自行调整工具与路径，不能声称已按本环境测试。当前实测环境为Python3.12、XeLaTeX/TeX Live、Poppler和pypdf，具体版本看随附运行快照。

## 2 环境检查与安装边界

```bash
python3 --version
xelatex --version
pdftotext -v
pdftoppm -v
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r corpus-work/requirements-core.txt
python -c 'import sqlite3,pypdf; print(sqlite3.sqlite_version, pypdf.__version__)'
kpsewhich amsmath.sty
kpsewhich mathrsfs.sty
kpsewhich tikz.sty
fc-match 'Noto Serif CJK SC'
fc-match 'Latin Modern Math'
```

这些是本地接续命令，不表示本次已在你的电脑执行。当前`requirements-core.txt`固定pypdf版本；额外采集脚本的依赖应按实际脚本声明安装，不装未知“全家桶”。如缺TeX/Poppler/字体，使用操作系统或官方TeX发行版的可信安装渠道；典型Linux需要XeTeX、常用LaTeX扩展／科学宏包、Latin Modern、AMS和Noto CJK。个别题还需要Xy、DejaVu Serif、physics、tensor、faktor等；按真实缺失逐项补齐。

不要执行作者压缩包内的类文件或安装脚本。最好使用不含个人凭据的独立编译环境，固定输入、只开放构建目录写入、禁用shell escape。`fc-match`可能返回替代字体，因此还需在实际样本中核对字体与缺字，不只看命令退出成功。

## 3 恢复真正已交付的全文数据库

```bash
python3 editable-corpus/restore_database.py
python3 editable-corpus/test_restore_database.py
python3 editable-corpus/test_database.py
python3 - <<'PY'
import json, sqlite3
from pathlib import Path
p=Path('editable-corpus')
m=json.loads((p/'manifest.json').read_text())
c=sqlite3.connect(p/'corpus.sqlite')
print('manifest items:',len(m['items']))
print('database rows:',c.execute('select count(*) from problems').fetchone()[0])
print('integrity:',c.execute('pragma integrity_check').fetchone()[0])
print('foreign-key errors:',c.execute('pragma foreign_key_check').fetchall())
assert len(m['items'])==c.execute('select count(*) from problems').fetchone()[0]
assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
assert c.execute('pragma foreign_key_check').fetchall()==[]
PY
```

必须保留`database-parts/`的全部顺序分段和`database-delivery.json`。恢复程序检查每段、整个gzip流、SQLite及记录数，不覆盖不同的现有数据库。不要把“分段文件上传成功”称为数据库已完整恢复。

`handoff/catalog/work_queue.sqlite`若随包提供，只是候选/状态检索队列；它不是已交付全文数据库，不能把它的行数当作合格题数。

可选的程序测试及最小合法来源夹具见 [运行测试说明](../runtime/README.md)。其跳过条件和实际执行范围须如实记录。

## 4 在当前电脑生成真实编译回执

仓库中的既往回执记录了当时的实际运行，不等于在新电脑运行过。先做单题烟测：

```bash
mkdir -p .editable-build .editable-receipts .reports
python3 corpus-work/scripts/compile_editable_delivery.py \
  --package editable-corpus --build-root .editable-build \
  --receipt-root .editable-receipts --item 001
python3 corpus-work/scripts/validate_corpus.py \
  --mode editable-delivery --package editable-corpus \
  --evidence editable-corpus/delivery-evidence.json \
  --build-root .editable-build --receipt-root .editable-receipts \
  --item 001 --report .reports/item-001.json
```

完整接收检查可在环境稳定后运行：

```bash
python3 corpus-work/scripts/compile_editable_delivery.py \
  --package editable-corpus --build-root .editable-build \
  --receipt-root .editable-receipts
python3 corpus-work/scripts/validate_corpus.py \
  --mode editable-delivery --package editable-corpus \
  --evidence editable-corpus/delivery-evidence.json \
  --build-root .editable-build --receipt-root .editable-receipts \
  --report .reports/full-editable-delivery.json
```

输出中须为目标数量、`errors: []`和真实通过状态。不要使用裸`validate_corpus.py --item ID`：默认历史证据模式不能证明完整可编辑交付。辅助程序不安装依赖，也不自动证明数学正确性或难度。

少数包声明了随附的运行宏，例如1505的IEEEtrantools。按该包的`runtime_TEXINPUTS_package_relative`声明，为该次进程设置`TEXINPUTS`，保留末尾冒号以继续使用标准搜索路径；不要猜测云端绝对路径，也不要全局覆盖TeX设置。例如在相应完整包恢复后：

```bash
PKG=/absolute/path/to/restored/package
TEXINPUTS="$PKG/sources/1505/runtime//:" \
python3 corpus-work/scripts/compile_editable_delivery.py \
  --package "$PKG" --build-root .build-1505 \
  --receipt-root .receipts-1505 --item 1505
```

示例中的`PKG`必须替换为实际恢复的包路径。此包特例不代表所有题都需要该设置；不要从某个题复制依赖到其他题。

## 5 接收待合并规范包与未完成材料

按 [待处理材料恢复说明](../materials/RESTORE_PENDING.md)（命令需先从仓库根进入`handoff/`）核对分段和整体哈希，再恢复到新目录。以其便携索引中的包路径运行上述编译/门禁命令。它们的状态包括“单组通过但未合并”“LOCAL1002整包通过但未远端交付”等，均不能直接替换远端已交付计数。

LOCAL1002 的独立增量恢复见 [精确恢复说明](../local1002/README.md)。它需要仓库中确切的safe975基线、待处理CAS及自身overlay；在safe975真正提交之前不得假设旧911能当基线。它已通过完整目录硬链物化、归档逐流哈希、实际1002门禁与SQLite检查，未宣称在云端重新写出了所有归档文件。恢复到新目录，保留基线不变。

原始READY和回执中的旧绝对路径是历史位置，不是本地运行参数。当前恢复清单、仓库相对路径和安全修订覆盖记录才是执行入口。许可安全修订之后，旧抓取HTML的哈希仍可保留作来源历史，但原始隐藏字段不能恢复到公开输出目录。

1907明确是未完成材料：只有清单允许的出版PDF、已直接核对的组件、最小许可见证和继续步骤可用；不能将私有旧版辅助草稿当作合格正文。其他hold同理。

## 6 新批次的实际命令形态

先按标准生成一个隔离的完整候选包，包含其真实`manifest.json`、`delivery-evidence.json`、`items/`、`sources/`、`licenses/`及必要资产。这里不提供“自动生成证明”的命令，也不假装旧PDF封装脚本是通用原生TeX采集器。

```bash
PKG=/absolute/path/to/new-batch-package
BUILD=/absolute/path/to/new-batch-build
RECEIPTS=/absolute/path/to/new-batch-receipts
ID=actual_stable_id
python3 corpus-work/scripts/compile_editable_delivery.py \
  --package "$PKG" --build-root "$BUILD" --receipt-root "$RECEIPTS" --item "$ID"
python3 corpus-work/scripts/validate_corpus.py \
  --mode editable-delivery --package "$PKG" \
  --evidence "$PKG/delivery-evidence.json" \
  --build-root "$BUILD" --receipt-root "$RECEIPTS" \
  --item "$ID" --report ".reports/$ID.json"
```

合并前后核对输入哈希、范围、许可、重复身份、INDEX及数据库。现有临时合并脚本包含旧批次ID/数量/绝对路径，不能原样当成通用命令运行；本次便携手册列出的通用接口与经过固定验证的示例才可直接使用。当前里程碑身份复用适配器须连同测试和说明一起接收，不能篡改计数骗过旧辅助器。

## 7 提交与恢复

```bash
git status --short
git diff --stat
# 仅添加已经核对的本批清单、完整正文、来源、索引、数据库分段和回执
git --literal-pathspecs add --pathspec-from-file=reviewed-paths.txt
git commit -m "corpus: add verified human-proof batch"
git push origin HEAD:corpus-progress-20261001
git rev-parse HEAD
git ls-remote origin refs/heads/corpus-progress-20261001
```

先把审查通过的明确仓库相对路径逐行写入`reviewed-paths.txt`，不要包含私有路径或通配符；不应把含私有原件的整个工作目录盲目`git add .`。不改仓库可见性，不force push；分支推进与清单/数据库哈希确认后再更新已交付数。远端身份核验与完整下载核验分别记录。

磁盘清理只针对已验证可恢复的重复或可重建产物。压缩替代要实际解压比对；删除已上传副本先确认精确提交和恢复路径。未上传唯一材料、未知许可原件和失败原因不能因缺空间被悄悄删掉。不同文件系统不能硬链接；空间预算用实际分配量而非把共享inode重复计算。
