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

系统 TeX 源完整，但格式库与文件名索引的系统符号链接目标缺失。首次编译因找不到 xelatex.fmt 失败；仅在本线 `.work/texmf/web2c/xetex` 构建格式后原作业续跑成功。没有安装软件或修改全局配置。复现：在该目录运行 `TEXMF='{/usr/share/texmf,/usr/share/texlive/texmf-dist}' xetex -ini -etex -jobname=xelatex -progname=xelatex -interaction=nonstopmode -halt-on-error xelatex.ini`。包装脚本仅当本地格式存在时设置 TEXMF/TEXFORMATS，避开失效的系统 ls-R 索引；缓存不上传。

`format_source_pointers.py` 仅对编辑性 Source reference 行里的来源路径斜杠添加可断行点，保持换行数及作者数学正文不变，拒绝已开始编译的作业。实际发现截断后才修复并编译新排版版本；不重编译未变成功题证。
