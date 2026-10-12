# publication 批目录清理台账（2026-10-13）

**授权**：Lead（Chief）2026-10-13 明确授权，规则见 `CONTROL.md` §2.3；
**执行人**：发布官（DeepSeek Harness 会话）；
**规则**：保留最近 **5** 个批目录原样 + **全部回执类文件**；对更早的批目录只删**派生副本**
（`base-restore/`、`public-consumer-*/`、`worktree/`、`tmp/`，以及 `public-restore-*/` 内**除 `RESTORE_RESULT.json` 外**的内容）；
**不碰** `jobs/`、`sources/`、`withdrawn/`、别人的卡与文件、失败现场 `publication/failed-attempts/`。

> 说明：规则原话是「删 `public-restore-*/`」，但该目录内含**回执** `RESTORE_RESULT.json`（规则 1 要求保留回执）
> ⇒ 实际执行取两者的交集：**保留该文件，删同目录其余内容**。这一处已在本台账显式记录。

## 一、时间与结果

| 项 | 删前 | 删后 |
|---|---|---|
| 主机 `/disks/sata1` 可用空间 | **364G** | **494G** |
| `publication/` 占用 | **144G** | **15G** |
| `publication/` 批目录数（含 `failed-attempts/`） | 138 | 138 |
| 真正的批目录数（含 `publication.json`） | 137 | 137 |
| **本次释放合计** | — | **约 130G**（随后清残余再释放约 3.2G，累计 **约 133G**） |

- 涉及清理的旧批：**133 个**（首轮）+ 132 个（清残余，主要是首轮遗留的零星派生目录）。
- 单批清理后占用：**1.2–2.9M**（只余回执与元数据；清理前约 1.9–2.0G）。

## 二、删后核验（逐项实测）

- **最近 5 批原样保留**（按 `publication.json` 的发布时间排序）：`author-material-new-137…141`，仍各约 **1.9–2.0G**，派生物未被删；
- **旧批回执存活**：抽查 113 / 120 / 130，`publication.json`、`stage-paths.txt`、`completion-marker-history/`、`relay/`、`public-restore-001/RESTORE_RESULT.json` **全部在**；
- **失败现场未动**：`publication/failed-attempts/` **2.5G 完好**（三个 attempt 目录及其 `base-restore/`、`worktree/` 均在）；
- `jobs/`、`sources/`、`withdrawn/` **未触碰**。

## 三、清理器与两处自行发现的缺陷（已在工具里修掉）

工具：`~/.dsh/bot/workspace/cleanup_publication.sh`（**默认 dry-run**，`--apply` 才真删；`--keep N` 指定保留批数）。

1. **排序用目录 mtime 是错的**：清理会刷新被清理目录的 mtime，「最近 N 批」会漂移到刚清过的旧批
   ⇒ 改为按 **`publication.json` 的 mtime（发布时刻）** 排序。
2. **未排除非批目录**：`publication/` 下还有 `failed-attempts/`（失败现场，规则禁止触碰）
   ⇒ 改为**只认含 `publication.json` 的真批目录**，非批目录一律跳过。
   （首轮因 `failed-attempts/` 内部多一层嵌套、删除路径恰好未命中，未造成误删；仍按规则显式跳过。）

## 四、后续

- **每 5 批自动清一次**，规则同上（保留最近 5 批 + 全部回执）；
- 可用空间 **< 250G** ⇒ 收紧到保留 **3** 批；**< 200G** ⇒ **停批并报 Lead**；
- 每批在 `status/publisher.json` 的 `disk_per_batch` 记 `df` 与保留批数，便于判断清理是否掉队。
