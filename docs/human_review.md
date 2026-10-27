# 人工审核说明

batch1 中只有 Physion-300 已完成逐帧复核；RoboJudge-115 / PhyGround-91 / VideoPhy2-100 均为 agent draft，需要人工给出 pass / edit / reject 结论。Physion-300 中细微 cue 样本（`needs_human_frame_step_confirmation=true`）也建议抽查。

## 审核页面

| 来源 | 页面 |
|---|---|
| Physion-300 | 仓库根目录 `index.html`（也在 HF 仓库根目录） |
| RoboJudge / PhyGround / VideoPhy2 | 字段与 CSV 审核列完全一致，可直接用数据文件审核；专用页面随后发布 |

打开方式：

1. 克隆或下载本仓库；
2. 浏览器打开 `index.html`（视频通过 HF 公开 resolve URL 加载，仓库公开无需登录）；
3. 或直接访问 <https://huggingface.co/datasets/HuggingFriends/PhysFixBench> 在线浏览。

## 每条审什么

对照 fixing prompt 的三块内容：

1. **问题是否真实**（`fix_problems`）：播放视频，到标注的时间区间逐帧 / 慢放确认。只承认物理缺陷；若声称的问题实际是语义 / 指令、任务完成度、相机、模糊、美学或转场问题，一律 reject。
2. **应然行为是否正确**（`fix_expected`）：与问题是否一一对应、物理上合理。
3. **保持内容是否恰当**（`fix_keep`）：有没有把缺陷本身也列进 keep，或漏掉可能受影响的相关物体。

## 结论与回收

- 每条选择 **通过 / 需修改 / 驳回**，可在框内直接修改文字并填备注；
- 结论自动暂存在浏览器（基于 record_id / dir_name），关页不丢；
- 点右上角「导出审核结果 JSON」回收结果，回传 PhysFixBench 维护方；
- 也可以直接在 CSV 的 `审核结论(pass/edit/reject)`、`修改后内容`、`备注` 三列填写后回传。

## 特殊情况处理

- **多错误样本**：允许有多条 problem / expected。只要其中一个问题不实，建议整体 edit（删掉不成立的条目）而非直接 reject，除非视频整体物理崩坏、不具备修复价值。
- **单帧 / 低清 / 模糊歧义**：参照 `confidence` 与 `needs_human_frame_step_confirmation`；运动模糊帧不能单独作为缺陷判据，必要时用原生帧率慢放。
- RoboJudge 来源注意智能体边界：连续边缘的真实人手入镜（无材质熔接）属 agent 语义，驳回该条；但夹爪断裂 / 熔毁 / 多肢等结构性缺陷成立。
