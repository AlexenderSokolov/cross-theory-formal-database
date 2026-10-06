# 九道新题的可恢复检查点

此包只备份已经逐题通过、在Yupeng合入1024并通过当前全库编译和整包门禁的9道净新增材料；尚未完成20题试点，也未作为新主库发布。主库远端可恢复计数仍1015；622被difficulty hold排除，不在此包。原40题不在这9题中。

完整作者TeX、source0/原出版PDF、必要局部核心、引用、逐件许可证、来源版本和编辑记录、9行全文SQLite与实际编译日志/回执都在CAS中。原网页与私密数据不在此包。

从仓库根目录运行（使用一个新的绝对输出目录）：

```sh
python3 handoff/materials/restore_pending.py --transport handoff/yupeng/net-new-pilot9/pilot9.transport.json --expected-transport-sha256 ffd8827c2052e577f8ab3fa6ca48f3a84c0df9ab07793e89cdbe433eb282babb --destination /absolute/new/pilot9
python3 corpus-work/scripts/validate_corpus.py --mode editable-delivery --package /absolute/new/pilot9/package --evidence /absolute/new/pilot9/package/delivery-evidence.json --build-root /absolute/new/pilot9/build --receipt-root /absolute/new/pilot9/receipts --report /absolute/independent/pilot9-check.json
```

工具先核有序分片及整个CAS字节，再精确恢复hash/大小/mode。实际本地离线恢复及整包门禁已通过9；远端读回核验会另存报告。当前1024包的校验采用实际重新编译全部1024，未把旧不同launcher程序称身份匹配。技术校验不独立认证数学正确性。
