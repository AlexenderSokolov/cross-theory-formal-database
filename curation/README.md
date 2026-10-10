# 返修记录怎么用

[REPAIRS.md](REPAIRS.md)面向阅读；[reviews.jsonl](reviews.jsonl)保存具体依据；[SUMMARY.json](SUMMARY.json)和[review-queue.jsonl](review-queue.jsonl)由目录脚本生成。

同一题的`title`与`content`是不同审查范围：改了题名不等于证明或难度通过。`published_H`仍是历史评级，`confirmed_H`只有实际内容确认后才填写。H3二审需明确独立、同级结论和可定位证据。暂无结论的题不自动降级、不补漂亮模板、不删除原件。

`pairing-review.jsonl`是源码区间检查发现的候选：所选题面与proof之间出现另一命题，必须回原文核对，不能把所有非相邻proof都当错。`authorship-review.jsonl`只检查明确模型解答的proof标题，论文研究AI本身不会被排除。没有命中不代表已通过全库审查。

原作者正文、来源、旧manifest和数据库分片保留。本轮修改通过当前catalog对使用者生效；实际正文修订单独保存到`revisions/`并记录来源区段、编译和交付检查。

研究线对64个已有主命题的新阅读证据已按稳定ID补入当前catalog的`research_reviews`，不增加题数，也不自动改变主库等级。当前完整目录按500条一页供阅读，原始交付INDEX仍保留用于重放。
