# 自动续接

入口是PROJECT.md、CONTINUATION_CURRENT.json、CURRENT_DELIVERY.json及实际HEAD。Goal保持active；无需用户重复批准。用户最新要求下载优先，未完成的来源批次不得边发现边转录。当前新批次只有预下载，无新增提取。

服务器工作根 `/disks/sata1/yupeng/human-proof-corpus`。首先读取 `source-cache/catalog-r001/PROGRESS.json`、`RUN.json`及进程/每URL真实receipt；已运行PID不能当完成。下载器 `run_download_sources.sh` 按2390个exact来源URL续跑，恢复保留所有失败及partial，不删除。每页最多6显式资产不等于完整作品；提取前核原PDF/native/所有所需资产，rawHTML只私有缓存。临时访问失败按真实原因hold并继续其他来源。

8个服务器模型任务位于 `candidates/server-workers/network-repair-r001`，读取各launch/FINAL/文件receipt及private事件用于审查，绝不把private事件/rawHTML/credentials上传。6个source只扩展43入口下载（N024跳过），2个cacheQA。已经强制direct：urllib ProxyHandler({})或curl -q --noproxy '*'；不修改全局网络。完成一块再领取互斥下一块，不启动未授权MCP或重复审批。

公开主库仍1015；本地1024已经当前程序实际全部编译和aggregate通过，新增9作为可恢复检查点公开并实际读回。另3412独立fullgate/CAS通过，故20题试点ready10，不重复加9或原40。下一步核远端3412备份，然后20题闭环发布主库；不重跑已经身份完全相同的检查。编译launcher任何身份变化都按受影响范围真重跑，不冒称历史程序相同。

每次发布前重读远端，保留并发成果；服务器做增量bundle，Windowsbare relay使用本机既有Git身份正常push，不复制token到服务器。只stage明确文件，禁止整个工作树add、force push、回滚或删除。较大快照用同仓库Release，有序sha恢复链未实际往返前保留完整分段。只有主库公开实际恢复成功才加remote_delivered。
