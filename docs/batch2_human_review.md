# PhysFixBench batch2 · 人工审核包

共 217 条带 fixing prompt 的候选；另保留 89 条 agent 未推荐样本供人工补捞，合计 306 段视频。所有记录均为预标注，待人工确认。

| 来源 | 推荐候选 | 可复核视频（含补捞） |
|---|---:|---:|
| Physion-Eval 新增 | 124 | 124 |
| Physics-IQ | 82 | 154 |
| MME-COF | 8 | 23 |
| VideoPhy2 · Seedance | 3 | 5 |

Physion-Eval 新增指尚未进入已发布 Physion-300、且已经有完整 fixing 预标注的候选，包含此前审核但未发布的样本。Physics-IQ、MME-COF 和新增 VideoPhy2 的 Seedance 视频由 Siyuan 生成；不推断机器预标注执行者。重复提交包只记一次，VideoPhy2 原始视频候选池不计入 batch2。

- 在线入口：https://siyuanmacs.github.io/PhysFixBench/batch2.html
- 默认显示推荐候选。可切换“全部视频”或“未推荐／补捞”。
- 播放原视频，对照“问题”和“应修改为”，必要时慢放并点击时间区间。
- 选择通过、修改或驳回；可以直接修改问题、正确表现与保持内容。结果暂存于当前浏览器。
- 完成后点击“导出审核结果”，将 JSON 交回维护方。跨设备协作请用导出／导入结果；未填写结论不会被计为通过。
- 也可填写 data/人工审核表.csv 后回传。data/physfixbench_batch2.jsonl 使用与 Physion-300 相同的 18 个字段。
- data/media_manifest.jsonl 保存每段视频的来源、文件名和 SHA256；audit/ 为本地溯源备份，不作为公开标注上传。
