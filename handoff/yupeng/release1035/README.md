# 1035题整包

975+40题接收后新增20道唯一题，合计1035。完整原数学TeX、题目INDEX、来源及许可、全文SQLite分段和真实编译证据已组成可恢复整包。此提交时服务器新目录恢复及完整门禁已通过；远端主库计数仍为1015，待公开精确提交重新下载恢复后更新。

从 editable-corpus 执行 `python3 restore_database.py`，然后 `python3 test_restore_database.py`、`python3 test_database.py`。编译证据用 `python3 restore_validation_artifacts.py --destination /absolute/fresh/artifacts` 恢复。用仓库validate_corpus.py显式editable-delivery、package/evidence/build-root/receipt-root进行完整门禁。见固定公开清单PUBLIC_FILELIST.json、PREPARATION.json及LOCAL_RESTORATION.json。未重跑所有题编译；仅当材料、程序和真实证据身份相符时复用本次服务器已通过证据。
