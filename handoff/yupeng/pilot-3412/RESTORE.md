# 3412已通过材料备份，未发布为主库增量

原EJDE2026.03/Theorem1.2，全部作者原条件、完整证明和必要新局部核心；标准minimax/抽象乘子明确引述。只有原native乱码£º依权威PDF进行小段忠实转录，source0原hash保持。实际2passes/27pages、逐题与整包门禁、SQLite和CAS独立恢复均通过。3411保持source_support_hold，完全不在此包。

```sh
python3 handoff/materials/restore_history.py --manifest handoff/yupeng/pilot-3412/ready-3412-r006.cas.manifest.json --expected-manifest-sha256 423f79767f4153c880f0209e247e148bb8f97bc954d5d19a1baf13d7d0ef8767 --destination /absolute/new/3412
mkdir /absolute/new/3412/external-receipts
cp /absolute/new/3412/package/receipts/3412.json /absolute/new/3412/external-receipts/3412.json
python3 corpus-work/scripts/validate_corpus.py --mode editable-delivery --package /absolute/new/3412/package --evidence /absolute/new/3412/package/delivery-evidence.json --build-root /absolute/new/3412/build --receipt-root /absolute/new/3412/external-receipts --report /absolute/independent/3412-check.json
```

此备份不增加主库远端计数，当前远端主库1015，9题已公开备份并实际读回，另此1题完成本地闭环。20题试点当前10个独立ready单元，未达到20。下一会话先核当前来源预下载和下列readiness，按真实main manifest/SQL和公开恢复结果计算。
