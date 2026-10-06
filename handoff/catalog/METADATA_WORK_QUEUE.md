# METADATA WORK QUEUE：候选材料管理查询库

`work_queue.sqlite` 是由本目录的候选/来源/材料元数据派生的查询副本。它不是 `editable-corpus` 中合格完整题证的全文数据库，不包含问题—证明正文，不以数据库行数计算合格题数。

- 3,255 个候选目录条目：3,197 个稳定 ID 与 58 个未分配身份键
- 2,344 个可复现来源/作品分组键；其中按 DOI、明确集体作品/仓库、或字面 URL 分组。没有承诺全部镜像与版本已做语义书目去重
- 15,417 个原始元数据记录引用，保存原路径、哈希、原字段编号及身份匹配依据
- 9,378 个必要材料位置、11,530 个条目—材料关联
- 最终对齐的来源准入1,015；GitHub核验975。原safe975差集64项已远端核验；另40题已规范化、逐题与恢复后整包通过并独立封存，等待本地合并及发布；1907仍未合格。LOCAL1002基线精确保留已完成。JSONL/CSV的github_verified911保留历史字段名，其含义为当前快照Git核验布尔值，现975项为真。上述材料状态与候选行数分别记录

完整性检查、外键检查和全部表的预期/实际行数见 `work_queue_validation.json`。可运行 `python3 build_work_queue.py --output /明确的新位置/work_queue.sqlite` 从本目录冻结元数据重新派生。期望行数和准入/交付数全部从输入快照读取，先校验一致性；新文件经完整性/外键检查后原子落盘。目标若已存在且与本快照字节相同则幂等复用，若不同则拒绝覆盖。脚本只向标准输出给出检查回执，不覆盖原有证据文件。原有JSONL/CSV仍是可读权威交接目录。

执行 `python3 -m unittest discover -s . -p test_build_work_queue.py` 检查错误计数拒绝与既有不同文件保护。历史云端采集脚本只作追溯，不能用于本地继续扩充。

## 恢复随附SQLite

实际库按无损gzip交付：`work_queue.sqlite.gz`。原SQLite完整字节已压缩后实际解压比对；原哈希仍为 `f44669791d7632e68e43827af5b49d73babc3ba42f426644519f6b63c8f18c64`。这只是传输表示变化，表、记录和检查结论不变。完整大小与两层哈希见 `SQLITE-TRANSPORT.json`。从仓库根进入本目录：

```bash
cd handoff/catalog
gzip -dk work_queue.sqlite.gz
echo 'f44669791d7632e68e43827af5b49d73babc3ba42f426644519f6b63c8f18c64  work_queue.sqlite' | sha256sum -c -
```

`gzip -dk`保留压缩包并拒绝覆盖现有输出；如已有数据库，直接检查其哈希，不使用强制覆盖。下面查询均针对恢复后的 `work_queue.sqlite`。

## 示例查询

```sql
-- 所有待补/受阻条目，含已有难度标签的核验状态
SELECT problem_id, candidate_key, title, status,
       difficulty_level, difficulty_verification, hold_reason, next_action
FROM entries
WHERE github_verified_at_catalog_snapshot = 0
ORDER BY status, CAST(problem_id AS INTEGER);

-- 各状态的候选目录行数，不是合格证明数
SELECT status, count(*) AS candidate_entries
FROM entries GROUP BY status;

-- 某个历史稳定ID及其全部元数据版本引用
SELECT e.problem_id, e.title, r.record_path, r.record_sha256,
       r.id_assignment_basis, r.original_identifiers_json
FROM entries e JOIN record_refs r USING(entry_key)
WHERE e.problem_id = '3188';

-- 来源分组与候选条目的关联
SELECT e.work_key, count(*) AS candidate_entries,
       sum(e.source_approved) AS source_approved,
       sum(e.github_verified_at_catalog_snapshot) AS snapshot_git_verified
FROM entries e
WHERE e.work_key IS NOT NULL
GROUP BY e.work_key;

-- 本地缺失材料
SELECT e.problem_id, e.candidate_key, m.path, m.export_classification
FROM entries e JOIN entry_materials em USING(entry_key)
JOIN materials m ON m.path = em.material_path
WHERE m.exists_locally = 0;

PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

私有 raw HTML/header/原生辅助文件仅在压缩元数据清单中登记路径与哈希，内容没有装入数据库。逐份的再分发许可和材料状态始终适用。
