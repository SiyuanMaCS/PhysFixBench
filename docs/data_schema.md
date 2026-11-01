# 数据字段与修复指令格式

每条 JSONL 一行一个 JSON 对象，共 18 个字段（顺序固定）。CSV 为同内容表格（UTF-8 BOM），并额外附带三个人工审核空列。

## 字段定义

| 字段 | 含义 |
|---|---|
| `dir_name` | 视频扁平文件名（不含扩展名）。HF 仓库中对应 `videos/<dir_name>.mp4`，来源前缀防碰撞（如 `robojudge__...`） |
| `record_id` | `<source>::<split>::<id>` 形式的全局唯一 id |
| `slot` | 来源内部槽位号 |
| `generator` | 生成模型（如 Veo 3.1 Fast / Wan 2.2 / cogvideo 等） |
| `error_family` | 问题大类：时序 / 因果、物体永存 / 同一、力与运动、材质 / 状态、接触 / 交互、几何 / 碰撞、智能体结构等 |
| `glitch_category_official` | 来源原始分类（Physion 官方类别；RoboJudge 为 `RoboJudge PA=<分数>` 溯源用） |
| `scenario_domain` | 场景域：刚体、可变形材料、流体 / 热 / 光、人 / 动物肢体、机器人操作等（RoboJudge 统一为 `embodied_robot_manipulation`） |
| `interaction_primitive` | 视频内容 / 动作原语：开合操作、倾倒 / 流动、拿取转移、形变 / 状态变化、肢体运动、多步操作、碰撞冲击、抛射等 |
| `review_error_category` | 复核后的细分错误类别 |
| `obviousness` | 缺陷明显度：`obvious`（最显著问题 ≥4 分）/ `subtle`；1–5 分制见各来源协议 |
| `confidence` | 复核置信度（0–1） |
| `needs_human_frame_step_confirmation` | 是否建议人工逐帧确认（低分辨率 / 近单帧歧义 / 细微 cue 时为 true） |
| `all_claimed_errors_visible` | 所声称的错误是否都能在视频中直接看到 |
| `annotation` | 来源原始标注（Physion 为官方英文原文；RoboJudge 为任务指令；PhyGround / VideoPhy2 为协作者摘要） |
| `fix_problems` | **结构化修复标注·问题**：「第X.Xs–Y.Ys：问题描述」逐条，中文 |
| `fix_expected` | **结构化修复标注·正确表现**：与 problems 逐条一一对应 |
| `fix_keep` | 修复时需保持不变的内容（物体、场景、动作主体等） |
| `fixing_prompt_zh` | 由上述三段拼成的完整中文修复指令，可直接发给视频生成 / 编辑模型 |

## `fixing_prompt_zh` 格式

```
【存在的问题】
1. 第X.Xs–Y.Ys：<问题描述>
2. ……
【应修改为】
1. <与问题 1 对应的正确表现>
2. ……
请在保持<fix_keep>的前提下，修正上述物理问题并重新生成视频。
```

设计要点：

- 时间区间精确到 0.1s，依据抽帧 / 原生帧核对；
- 「问题」与「应修改为」严格一一对应，便于审核与自动评测对齐；
- 只描述物理缺陷与应然物理行为，不涉及语义 / 指令层面的修改；
- `fix_keep` 保护与缺陷无关的内容，降低修复时的次生改动。

## CSV 额外列（供人工审核）

| 列名 | 填写方式 |
|---|---|
| `审核结论(pass/edit/reject)` | pass = 标注正确可用；edit = 需修改（在旁边列给出改后内容）；reject = 误报 / 视频不可修 |
| `修改后内容` | edit 时填写修正后的 fixing prompt 或字段 |
| `备注` | 任何补充说明 |

---

## PhysicsIQ-154（独立 release `physicsiq154-v1.0.0`，未并入 batch1）

本来源**不沿用**上方 18 字段，使用独立 slim canonical schema。发布状态见 `data/physicsiq154/PUBLISH_STATUS.json`（当前 `publication_in_progress` / `media_uploaded=false`）。

| 字段路径 | 含义 |
|---|---|
| `record_id` | 全局唯一键，形如 `0034_v2`；等于 `{id}_{version}`。 |
| `id` / `version` | 同一物理演示的两个**并行 I2V 生成版本**：`v1`（70 条）/ `v2`（84 条）。v1 与 v2 是用户基于 Physics-IQ switch frames + bpp_base prompts 自行生成的候选，不是对同一段视频的两次独立复核。 |
| `scenario` | 场景 slug（如 `block-domino`、`ball-and-block-fall`）。 |
| `original_prompt` | 生成时使用的英文 prompt（来自 Physics-IQ switch frames + bpp_base prompts）。 |
| `duration_s` | 时长（秒）。 |
| `video.path` / `video.sha256` / `video.bytes` | 相对路径 `videos/physicsiq154/{record_id}.mp4`、SHA-256、字节数。**当前媒体尚未上传。** |
| `source.dataset` / `source.release` | 固定 `Physics-IQ` / `physicsiq154-v1.0.0`。源：Google DeepMind Physics-IQ（代码 Apache 2.0，其他材料 CC BY 4.0）。 |
| `machine_review.status` / `machine_review.decision` | 当前全部 `candidate` / `accept`；`observed_summary` 为中文观察摘要。 |
| `machine_review.issues[]` | 每条记录固定 1 个 issue：`time_start_s` / `time_end_s` / `issue_description` / `fix_expected`（修复指令）/ `evidence` / `ambiguity`。`superseded_by_human_review=true` 时机器 issue 仅留作透明参考。 |
| `human_review.status` | `independent_confirmed`（仅 `0034_v2`）/ `pending_human_review`（其余 153 条）。 |
| `human_review.authoritative` | 仅 `0034_v2` 为 `true`；此时以 `human_review.independent_review.issue_description` 与 `.fix_expected` 为权威修复指令，机器 issue 折叠保留。 |

**人工复核事实**：在完整 394 条机器标注里，只有 2 条经过独立人工复核——`0034_v2`（已确认 issue，纳入本 release）和 `0092_v2`（复核后判 `reject_no_clear_issue`，**未纳入**）。本 release 不对外宣称任何额外的人工验证；其余 153 条均为机器预标注，待人工抽审。154 条视频为用户自行 I2V 生成的派生样本，**非 Physics-IQ 官方 reference clip**。
