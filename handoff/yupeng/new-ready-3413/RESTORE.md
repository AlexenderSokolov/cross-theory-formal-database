# 已通过题证3413的可恢复备份

保存完整可编辑人类题证、原版本来源/逐组件许可、全文SQLite及实际编译/恢复证据。实际QA范围见随附报告；未声称数学正确性独立认证。未作为新主库发布，不增加远端主库1015计数。

```sh
python3 handoff/materials/restore_history.py --manifest handoff/yupeng/new-ready-3413/ready-3413-r003.cas.manifest.json --expected-manifest-sha256 0449192574d09db210985ad6389e73f9e41906dd6fb66589a17db54731379764 --destination /absolute/new/3413
mkdir /absolute/new/3413/external-receipts
cp /absolute/new/3413/package/receipts/3413.json /absolute/new/3413/external-receipts/3413.json
python3 corpus-work/scripts/validate_corpus.py --mode editable-delivery --package /absolute/new/3413/package --evidence /absolute/new/3413/package/delivery-evidence.json --build-root /absolute/new/3413/build --receipt-root /absolute/new/3413/external-receipts --report /absolute/independent/3413-gate.json
```

须核所有SHA/大小/mode和实际完整门禁；历史回执复用身份与真实pass已明确，复制恢复不称新编译。20净新增试点未达到，继续候选，原40不再计算。
