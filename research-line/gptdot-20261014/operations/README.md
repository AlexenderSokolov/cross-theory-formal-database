# 本线工具

复用 `corpus-work/scripts/prepared_delivery.py`，仅把调用路径和本线前缀适配到云端环境。共享生产脚本和 schema 未修改。

单题实际顺序（TASK、JOB 为具体本线路径）：

1. 完成完整身份范围和在途查重，原任务如实写结论及依据；pending 不装配
2. `bash operations/run_assemble.sh --task "$TASK" --assemble-only`
3. `python3 operations/material_origin.py --job "$JOB"`，若有长编辑来源路径再运行 `python3 operations/format_source_pointers.py --job "$JOB"`
4. `bash operations/run_compile.sh --job "$JOB"`
5. 检查实际 PDF 可读性，只有完成后的材料进入批次 SQLite 和选择清单

`material_origin.py` 只在装配后、编译前把任务明确声明的既有 origin_class 写入 manifest 和 provenance，以免上游装配器的固定 native_tex 值误标作者证明助手代码或正式出版转录。它不改变题面、证明、资格、ID、审核或作业状态。局部测试 `python3 operations/test_material_origin.py` 覆盖两份元数据同步及其他字段不变；没有重跑未变题证或宣称全库测试通过。

上传使用现有授权 GitHub 连接创建 blob/tree/commit，再普通快进更新本分支；shell 未配置写认证，不读取、复制或新建凭据。每次更新前复核远端分支头，冲突时停止，不 force push。源码与许可证遵循逐题明确白名单，`.work` 和未许可素材不上传。

## 当前云端 TeX 运行时

系统 TeX 源完整，但格式库与文件名索引的系统符号链接目标缺失。首次编译因找不到 xelatex.fmt 失败；仅在本线 `.work/texmf/web2c/xetex` 构建格式后原作业续跑成功。该首次格式修复没有修改全局配置；后续缺失依赖只安装在本线私有缓存，见下方版本说明。复现：在该目录运行 `TEXMF='{/usr/share/texmf,/usr/share/texlive/texmf-dist}' xetex -ini -etex -jobname=xelatex -progname=xelatex -interaction=nonstopmode -halt-on-error xelatex.ini`。包装脚本仅当本地格式存在时设置 TEXMF/TEXFORMATS，避开失效的系统 ls-R 索引；缓存不上传。

`format_source_pointers.py` 仅对编辑性 Source reference 行里的来源路径斜杠添加可断行点，保持换行数及作者数学正文不变，拒绝已开始编译的作业。实际发现截断后才修复并编译新排版版本；不重编译未变成功题证。

## 后续标准依赖与复现

2026-10-15 的实际任务还使用官方发行的 `faktor 0.1b`、`mathdots 0.9`、`biblatex 3.21`、`logreq 1.0`、`ytableau 1.4`、`mathabx` 字体及 `Biber 2.21`。它们来自 CTAN 或项目官方发行源，原许可证保留；没有用替代数学符号来绕过字体缺项。安装只在本线 `.work/texmf` 与 `.work/biber-2.21`，系统目录、网络和安全设置未改。

一般完整 TeX Live 环境可由标准包管理器提供这些依赖。当前特殊云镜像需本地 `xelatex.fmt` 与 `mf.base`，私有字体映射仅补充 mathabx，未替换作者正文。`run_compile.sh` 会检测本线 Biber 路径，所有缓存均不进入公开题证包。

`compile_material.py` 将包根加入 `BIBINPUTS`，保留原搜索路径，解决作者 `items/*.bib` 引用在独立构建目录中不可见的问题。它仍保留已有 `BSTINPUTS` 行为。回归测试见 `test_compile_material.py`；四项通过，整套本线工具测试二十五项通过。这不是整库测试或数学认证。

## 准备分支与最终准入

保存快照范围内的定向查重、材料及可读性检查与最终当前在途确认分开记录。最新在途身份未确认时，准备包附 `PUBLICATION_LIMITS.md`，不得作为现行全局唯一资格或生产主库新增计数。已知重复、缺少完整作者主证明或许可不明的条目不因上传而转为合格。

## 后续运行时复用记录（2026-10-15）

新增私有官方依赖 listofitems 1.65、stmaryrd 2.02a-tmp-CAR 和 accents 1.4。stmaryrd 原始 TFM/官方 Type1 与映射均保留；私有 dvipdfmx 配置同时保留既有 mathabx，补充官方 stmaryrd、txfonts 与 txr3 映射，以解决缺失系统 pdftex.map 造成的 rtxptmri 物理字体映射。后者已通过先失败后成功的独立单符号测试；没有用不同符号替代原文。

失败引擎中断后若 aux/out/toc 不完整，先在本线私有缓存保存失败中间件，再仅对失败作业续跑；不重新编译未变成功材料。统计当前候选时，递归扫描三个来源组的 task.json，但排除 revisions/.work/private.work，并要求 task_id 唯一；源目录有单题和多题两种层级，不能用固定一层路径遗漏多题来源。
