# 1035主库之后两题备份

2322和2324原题证、必要局部核心、来源许可、H2/H3粗筛、真实编译和全页QA已通过，合并后本地库1037。此备份含61个已审必要文件，排除可重建fontcache；不会增加远端主库1035。

```sh
python3 handoff/materials/restore_history.py --manifest handoff/yupeng/postpilot2/manifest.json --expected-manifest-sha256 afeb2c21a336c6849360954e4c06b022031fa5666d3f17e7a612f9466d9a1fd6 --destination /absolute/new/postpilot2
```

恢复后每题路径 `<destination>/<id>/package`、`<destination>/<id>/build`、`<destination>/<id>/receipts`。显式editable-delivery/evidence/item/report执行；全文SQL与恢复门禁回执见ACTUAL_RESTORATION。该包与公开1035基线组成1037可恢复链，下一合并者核原版ROOT决定和全文件身份后复用合并脚本。没有生成证明或独立数学认证；不要把1037与两题备份再次相加。
