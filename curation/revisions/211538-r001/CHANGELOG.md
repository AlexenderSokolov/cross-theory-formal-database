# 211538-r001：补齐作者原文上下文

此目录是独立本地修订包，原公开题证、主库 manifest、数据库保留；一审/二审历史亦保留。

本次把原单元孤立保留的 `q_n theta-p_n -> 0` 扩展为作者原文 `source0.tex:1028–1059`：明确 `p_n/q_n` 是 theta 的连分数渐近分数，保留无理旋转遍历性、Denjoy–Koksma 的有界变差条件和不等式，并恢复作者所引的四条参考文献。原题面1067–1076、原证明1078–1177逐字不变，原先已经编译的preamble逐字复用。没有补写任何数学推导。

`changes.json` 逐块列出原文行号、新 TeX 行号、原/新文件和文字/字节比对结果。`package-root` 含新 TeX、原source副本、许可记录、五列INDEX、同步manifest/provenance及逐块delivery-evidence。原item和原metadata另存于 `original/`，便于直接比较。

**难度建议由H3改为H2。** 原H3记录只使用论文来源与100行证明长度。独立读证明后，可明确给定的先修是无理旋转遍历性、沿渐近分母的Denjoy–Koksma界、L2平移连续性和绕数的周期相位提升；本证明完成单位相位归一化、迭代、相位导数下界和分部积分矛盾，具备博士专题难度，但当前证据不支持H3。此建议只进入新修订metadata，不覆盖已发布标签。

本次静态检查核对全部标签、交叉引用、四个引用键及对应作者bibliography，未发现遗漏；没有添加自定义宏。新增的作者文献条目来自同一捆绑source，不宣称重新验证这些外部图书的内容。原题、source和许可notice均按锁定Git提交的原字节保存，未把Windows checkout的CRLF转换计为上游内容；原许可notice逐字保留，`licenses/REVISION-NOTE.txt`另述本修订包的实际范围。许可记录继承原主库元数据；原始abstract网页不在本包，未伪造新的许可抓取证据。

**当前状态：本地返修完成，尚未合入正式主库。** 新TeX以latexmk完成两次真实成功编译，无未解析引用、缺字或重跑请求；既有单题交付检查返回1条通过、errors为空；独立查看全部2页PDF通过。本轮内容判断为H2，原公开H3标签保留在历史数据中。当前目录已链接本修订稿。详见`gate-result.json`、`changes.json`和`../../visual-review-211538.json`。

复现准备过程：在本目录执行 `bash run_prepare.sh` 或 `python prepare_revision.py`。再次运行会重新生成未编译状态的候选包，因此主控确认通过后不要把此准备脚本当验证命令重跑。

完整编译/数据库/门检入口：设置包外`REVISION_WORK`后运行`bash run_compile.sh`。如重编译导致PDF字节改变，应重新记录对应版本的页面检查，不能沿用旧PDF哈希的视觉记录。
