# 1040题完整主库候选与恢复

1015接收基线之后累计25道净新增，本地主库1040；本提交时新目录全文SQL/恢复链/完整门禁已通过，远端可恢复主库仍按1035记录，公开精确提交取回实际恢复后再更新。原题证TeX/INDEX/来源/许可和完整SQLite均在editable-corpus。原schema1编译证据描述只标识基础1035 archive；恢复全部1040必须用validation-chain.json，不能把只恢复1035当全库完成。

在editable-corpus中：
```sh
python3 restore_database.py
python3 test_restore_database.py
python3 test_database.py
python3 restore_validation_chain.py --chain validation-chain.json --expected-chain-sha256 5944b02abbe5bd02b9e182414e8f69cd5fa019b8e2edecc1f2ac278d2b4944b0 --archive-root base1035=. --archive-root delta5=validation-artifact-deltas/pilot25-delta5 --schema1-helper restore_validation_artifacts.py --expected-helper-sha256 33548dad0cfb3a268346d896ba2ca4340c1171df8f00d3c08bb18a95723c3594 --output /absolute/fresh/artifact1040
```
随后显式调用corpus-work/scripts/validate_corpus.py --mode editable-delivery，真实package/evidence、恢复的build-root/receipt-root及独立report。完整7278编译文件=基础7243+新35，新增ZIP927151bytes；旧证据身份匹配复用，无新编译声明。下一检查点继续100/500至30000，来源缺证/低难/未明许可保持hold0，不增加研究标签。
