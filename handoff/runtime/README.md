# 本地运行测试夹具

从仓库根目录运行：

```bash
python3 handoff/runtime/install_test_fixtures.py --project corpus-work
python3 -m unittest discover -s handoff/runtime -p 'test_install_test_fixtures.py' -v
python3 -m unittest discover -s corpus-work/tests -v
```

安装器只复制清单中七份确切的 Stacks 原始数据文件，不执行上游脚本，不替换不同的现有文件。它们是三个真实来源抽取测试所需的最小源码闭包，并非完整 Stacks 仓库，也不增加合格题数。来源版本和 SHA256 见 stacks-test-fixtures-manifest.json；保留 CONTRIBUTORS 和 COPYING 中的 GFDL 条件。

本次隔离复测运行230项测试，结果 OK，跳过3项依赖项目本地 XeTeX format 的历史批次集成测试；不能称为230项全部实际执行。安装器自身的2项测试通过。首次隔离复制漏掉门禁证据子目录及测试用文档，失败日志保留；补入仓库本来已有的原始文件后通过，没有修改或放宽生产门禁。最终日志和输入身份见 SMOKE-final.txt、SMOKE-RECEIPT.json。

本地若显示跳过，先理解测试前提；不要创建假格式文件或删除 skip 条件以冒充通过。题库的实际编译与逐题/全库验收仍按命令手册单独执行。
