# 研究线材料与返修视图

此目录保存 DeepSeek Harness 研究线的本地证据与可复算索引。它不是新增公开交付，不并入 `editable-corpus/manifest.json`。索引通过表示元数据一致且存在题证文件，不代表已编译、原文保真、数学达标或获准再分发。

## 读取与复现

- `index.jsonl`：材料视图；`records.jsonl`：包含 HOLD 与待核项的全部判级记录。
- `holds.jsonl`、`pending.jsonl`：保留原标签和证据，说明暂不计入的原因。
- `main-overlap.jsonl`：研究 ID → 主库 ID；只匹配源文件名和主库 primary 原文的首个命题标签，不使用 context 标签。未匹配不代表新命题。
- `summary.json`：所有计数由输入数据计算；`source-license-audit.json`：完整来源登记表的许可元数据审阅结果。
- `archive/2026-10-10/`：原始快照与复核记录，保留原文件，不就地改写。

在仓库根目录运行：

```bash
bash research-line/run_reconcile.sh
```

Windows PowerShell 可执行同样的两条命令：

```powershell
python -m unittest discover -s corpus-work/scripts/tests -p test_reconcile_research_line.py
python corpus-work/scripts/reconcile_research_line.py
```

脚本仅依赖 Python 标准库，使用相对路径；通过 `--snapshot`、`--reviews`、`--registry` 可指定另一个已归档快照。不会连接远端、编译题证、改写原始文件或主库。

## 这次实际修正的计数

旧控制端镜像记录 234 条、7 个 H3；10 月 10 日只读取得的远端快照记录 235 条、6 个 H3。远端已应用旧 H3 降档及 Noether normalization 最终复核，不能用旧镜像倒盖新决定。

多出来的 `S046-thm:settopos` 同时出现在 `counted` 与 `dropped`，没有对应题证文件；原理由明确指出题面无附带证明，所抽取的是下一条命题的证明。归档保留其 H2 源标签，在当前视图中列为待核。当前材料视图为 **234 条（H2 228、H3 6）**；另有 **4 条 H1 HOLD、1 条待核**。与主库主命题的确定重叠是 **64 条**，其余170条尚未完成语义去重。历史复盘的来源表把 AIF 混在 S047 NUMDAM 中；当前输出分开文献键。

判级次序：保留最新快照中已应用的决定；已应用的 `final_review` 高于较早 `recheck`；外部最终复核优先于外部重判，但与当前快照不一致时只打开待核项，不自动覆写。`previous_levels` 与 `source_record` 保留旧档位和证据位置。H3 是原工作流的当前判级，不是本次重新数学审稿的结论。`review_flags` 另列最终复核报告过的引文问题；例如 Chow Noetherian 的文字修订仍需核对，不能将材料存在等同质量通过。

## 来源许可与证据界限

完整60项来源登记表没有逐来源许可字段。Stacks 可以关联既有主库中的 GNU FDL 1.2 or later 记录及 `editable-corpus/licenses/COPYING`，这是既有来源家族的许可证据；不能据此默认其他来源、不同文献和图形也获准再分发。其余来源保留 `not_established_by_registry` 状态；公开可读、arXiv 收录和题证文件存在均不等于许可审核通过。归档仅供这次授权的本地核查，发布前按实际交付文件另行核验。

历史“90+份复核”“约85%忠实”“最终一致100%”没有统一抽样与分母台账，因此不重写成全库质量指标。归档中的旧模板相似度文件仅是历史材料，新脚本不运行、不汇报该指标。没有做全库数学再审、删题、远端写入或公开发布。
