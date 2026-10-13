# 全量材料阅读索引

来源快照：`d9f80e6fd908cee72ef6f4a09e4a00efea8525b2`（已核对 manifest 内容，仅允许 Git checkout 换行差异）。材料共 **18722** 条：legacy **14875**，prepared **3847**。

展示序号仅为此快照的阅读顺序；稳定 problem_id、来源、许可和审阅身份不变。材料状态、历史 H 标签、prepared 或 status 字段均不自动证明现行科学资格，序号也不是新增/交付计数。

本视图由 `corpus-work/tools/render_material_index.py` 从 manifest 全部材料重新生成，不供五列 INDEX 门禁解析器使用。旧交付 [INDEX](INDEX.md) 与历史 [CORPUS_INDEX/catalog](CORPUS_INDEX.md) 保持各自覆盖范围。

从仓库根重新生成（先取得匹配来源快照的 manifest）：

```sh
python3 corpus-work/tools/render_material_index.py --package editable-corpus --snapshot d9f80e6fd908cee72ef6f4a09e4a00efea8525b2
# 只检查过期/缺失/多余行，不覆盖文件
python3 corpus-work/tools/render_material_index.py --package editable-corpus --snapshot d9f80e6fd908cee72ef6f4a09e4a00efea8525b2 --check
```

每页最多 200 条，各页序号延续全局顺序；每条仅出现在一页。

| 页面 | 全局展示序号 | 稳定 ID 范围 |
|---|---|---|
| [第 1 页](material-index/page-001.md) | 1–200 | 001–453 |
| [第 2 页](material-index/page-002.md) | 201–400 | 454–806 |
| [第 3 页](material-index/page-003.md) | 401–600 | 807–1322 |
| [第 4 页](material-index/page-004.md) | 601–800 | 1323–1894 |
| [第 5 页](material-index/page-005.md) | 801–1000 | 1895–2373 |
| [第 6 页](material-index/page-006.md) | 1001–1200 | 2374–8025 |
| [第 7 页](material-index/page-007.md) | 1201–1400 | 8026–118787 |
| [第 8 页](material-index/page-008.md) | 1401–1600 | 118826–133544 |
| [第 9 页](material-index/page-009.md) | 1601–1800 | 133748–142038 |
| [第 10 页](material-index/page-010.md) | 1801–2000 | 142091–149370 |
| [第 11 页](material-index/page-011.md) | 2001–2200 | 149543–154879 |
| [第 12 页](material-index/page-012.md) | 2201–2400 | 154910–159000 |
| [第 13 页](material-index/page-013.md) | 2401–2600 | 159029–162432 |
| [第 14 页](material-index/page-014.md) | 2601–2800 | 162448–165472 |
| [第 15 页](material-index/page-015.md) | 2801–3000 | 165480–167968 |
| [第 16 页](material-index/page-016.md) | 3001–3200 | 167970–170507 |
| [第 17 页](material-index/page-017.md) | 3201–3400 | 170538–172887 |
| [第 18 页](material-index/page-018.md) | 3401–3600 | 172890–174865 |
| [第 19 页](material-index/page-019.md) | 3601–3800 | 174866–176838 |
| [第 20 页](material-index/page-020.md) | 3801–4000 | 176848–178482 |
| [第 21 页](material-index/page-021.md) | 4001–4200 | 178483–179238 |
| [第 22 页](material-index/page-022.md) | 4201–4400 | 179241–180005 |
| [第 23 页](material-index/page-023.md) | 4401–4600 | 180006–180734 |
| [第 24 页](material-index/page-024.md) | 4601–4800 | 180735–181447 |
| [第 25 页](material-index/page-025.md) | 4801–5000 | 181454–182132 |
| [第 26 页](material-index/page-026.md) | 5001–5200 | 182133–182896 |
| [第 27 页](material-index/page-027.md) | 5201–5400 | 182899–183637 |
| [第 28 页](material-index/page-028.md) | 5401–5600 | 183638–184534 |
| [第 29 页](material-index/page-029.md) | 5601–5800 | 184536–185259 |
| [第 30 页](material-index/page-030.md) | 5801–6000 | 185261–185957 |
| [第 31 页](material-index/page-031.md) | 6001–6200 | 185959–186675 |
| [第 32 页](material-index/page-032.md) | 6201–6400 | 186678–187517 |
| [第 33 页](material-index/page-033.md) | 6401–6600 | 187523–188390 |
| [第 34 页](material-index/page-034.md) | 6601–6800 | 188394–189128 |
| [第 35 页](material-index/page-035.md) | 6801–7000 | 189129–190591 |
| [第 36 页](material-index/page-036.md) | 7001–7200 | 190625–191571 |
| [第 37 页](material-index/page-037.md) | 7201–7400 | 191573–192193 |
| [第 38 页](material-index/page-038.md) | 7401–7600 | 192194–192794 |
| [第 39 页](material-index/page-039.md) | 7601–7800 | 192800–193370 |
| [第 40 页](material-index/page-040.md) | 7801–8000 | 193371–193951 |
| [第 41 页](material-index/page-041.md) | 8001–8200 | 193952–194484 |
| [第 42 页](material-index/page-042.md) | 8201–8400 | 194487–194986 |
| [第 43 页](material-index/page-043.md) | 8401–8600 | 194990–195518 |
| [第 44 页](material-index/page-044.md) | 8601–8800 | 195525–196051 |
| [第 45 页](material-index/page-045.md) | 8801–9000 | 196056–196591 |
| [第 46 页](material-index/page-046.md) | 9001–9200 | 196596–197093 |
| [第 47 页](material-index/page-047.md) | 9201–9400 | 197100–197628 |
| [第 48 页](material-index/page-048.md) | 9401–9600 | 197630–198125 |
| [第 49 页](material-index/page-049.md) | 9601–9800 | 198126–198613 |
| [第 50 页](material-index/page-050.md) | 9801–10000 | 198619–199163 |
| [第 51 页](material-index/page-051.md) | 10001–10200 | 199165–199662 |
| [第 52 页](material-index/page-052.md) | 10201–10400 | 199664–200163 |
| [第 53 页](material-index/page-053.md) | 10401–10600 | 200166–200626 |
| [第 54 页](material-index/page-054.md) | 10601–10800 | 200628–201099 |
| [第 55 页](material-index/page-055.md) | 10801–11000 | 201100–201579 |
| [第 56 页](material-index/page-056.md) | 11001–11200 | 201584–202018 |
| [第 57 页](material-index/page-057.md) | 11201–11400 | 202019–202556 |
| [第 58 页](material-index/page-058.md) | 11401–11600 | 202564–203084 |
| [第 59 页](material-index/page-059.md) | 11601–11800 | 203087–203612 |
| [第 60 页](material-index/page-060.md) | 11801–12000 | 203616–204147 |
| [第 61 页](material-index/page-061.md) | 12001–12200 | 204150–204694 |
| [第 62 页](material-index/page-062.md) | 12201–12400 | 204695–205594 |
| [第 63 页](material-index/page-063.md) | 12401–12600 | 205595–206123 |
| [第 64 页](material-index/page-064.md) | 12601–12800 | 206124–206570 |
| [第 65 页](material-index/page-065.md) | 12801–13000 | 206572–207120 |
| [第 66 页](material-index/page-066.md) | 13001–13200 | 207122–207538 |
| [第 67 页](material-index/page-067.md) | 13201–13400 | 207539–207977 |
| [第 68 页](material-index/page-068.md) | 13401–13600 | 207979–208422 |
| [第 69 页](material-index/page-069.md) | 13601–13800 | 208428–208814 |
| [第 70 页](material-index/page-070.md) | 13801–14000 | 208823–209304 |
| [第 71 页](material-index/page-071.md) | 14001–14200 | 209306–209710 |
| [第 72 页](material-index/page-072.md) | 14201–14400 | 209712–210111 |
| [第 73 页](material-index/page-073.md) | 14401–14600 | 210112–210688 |
| [第 74 页](material-index/page-074.md) | 14601–14800 | 210689–211548 |
| [第 75 页](material-index/page-075.md) | 14801–15000 | 211551–900000126 |
| [第 76 页](material-index/page-076.md) | 15001–15200 | 900000127–900000326 |
| [第 77 页](material-index/page-077.md) | 15201–15400 | 900000327–900000528 |
| [第 78 页](material-index/page-078.md) | 15401–15600 | 900000529–900000728 |
| [第 79 页](material-index/page-079.md) | 15601–15800 | 900000729–900000928 |
| [第 80 页](material-index/page-080.md) | 15801–16000 | 900000929–900001128 |
| [第 81 页](material-index/page-081.md) | 16001–16200 | 900001129–900001328 |
| [第 82 页](material-index/page-082.md) | 16201–16400 | 900001329–900001528 |
| [第 83 页](material-index/page-083.md) | 16401–16600 | 900001529–900001728 |
| [第 84 页](material-index/page-084.md) | 16601–16800 | 900001729–900001928 |
| [第 85 页](material-index/page-085.md) | 16801–17000 | 900001929–900002128 |
| [第 86 页](material-index/page-086.md) | 17001–17200 | 900002129–900002328 |
| [第 87 页](material-index/page-087.md) | 17201–17400 | 900002329–900002528 |
| [第 88 页](material-index/page-088.md) | 17401–17600 | 900002529–900002728 |
| [第 89 页](material-index/page-089.md) | 17601–17800 | 900002729–900002928 |
| [第 90 页](material-index/page-090.md) | 17801–18000 | 900002929–900003130 |
| [第 91 页](material-index/page-091.md) | 18001–18200 | 900003131–900003330 |
| [第 92 页](material-index/page-092.md) | 18201–18400 | 900003331–900003530 |
| [第 93 页](material-index/page-093.md) | 18401–18600 | 900003531–900003730 |
| [第 94 页](material-index/page-094.md) | 18601–18722 | 900003731–900003852 |
