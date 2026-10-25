# PhysFixBench · batch1（draft，待人工审核）

带**物理缺陷**的文生视频样本 + 结构化中文修复标注（fixing prompts），用于物理视频修复（physics video correction）基准。batch1 由四个并列来源构成，每条标注只针对**物理问题**（不含语义对齐 / instruction following / control 问题）。除 Physion-300 已经过我方 6fps 逐帧复核外，其余三个来源均为 agent draft，等待人工审核（pass / edit / reject）。

| 来源 | 条数 | 内容域 | 标注状态 | 文件 |
|---|---|---|---|---|
| Physion-Eval | 300 | 通用/受控物理（general & controlled physics） | 6fps+原生帧率逐帧复核确认 TP，分层抽选 | `data/physfixbench_physion300.{jsonl,csv}` |
| RoboJudge（**test split only**） | TBD（目标 100+ 可修） | embodied 机器人/人手操作 | agent 6fps+native 逐帧**重新标注**，draft 待审 | `data/physfixbench_robojudge*.{jsonl,csv}` |
| PhyGround | 91 | 通用物理 | 协作者 juyil agent 标注，直接搬运转换，我方未逐帧复核 | `data/physfixbench_phyground.{jsonl,csv}` |
| VideoPhy2 | 100 | 通用物理 | 协作者 juyil agent 标注，直接搬运转换，我方未逐帧复核 | `data/physfixbench_videophy2.{jsonl,csv}` |

视频（扁平文件命名，按来源前缀区分）托管在 Hugging Face dataset：
[https://huggingface.co/datasets/HuggingFriends/PhysFixBench](https://huggingface.co/datasets/HuggingFriends/PhysFixBench)（私有；`videos/` + 同样的 `data/`）。

## 各来源说明

### Physion-Eval · physion300

- 视频来自 Physion-Eval severity-4/5 候选池（seed 20261019 抽样的 1000 条队列），覆盖 5 个生成模型：Veo 3.1 Fast / Wan 2.2 / Hailuo 2.3 / Sora 2 / Kling 2.5（各 59–61 条）。
- 每条经 **6fps 全片抽帧 + 原生帧率（24/30fps）逐帧放大复核**：仅保留官方标注物理缺陷被视觉证据确认存在的样本；误报、语义对齐/control/美学问题一律剔除。
- 选样在确认 TP 池上按 **问题类别 × 视频内容 41 个联合格子分层**，稀有内容（碰撞、抛射、工具操作）均覆盖；保留明显/细微难度梯度（112 条细微 cue，其中 104 条 `needs_human_frame_step_confirmation=true` 建议逐帧复核）。
- 问题类别：时序/因果 92 · 物体永存 54 · 力与运动 48 · 材质/状态 47 · 接触/交互 34 · 几何/碰撞 23 · 其他 2。

### RoboJudge · test split（re-annotation draft）

- 仅使用 RoboJudge **test split**（不使用 train）。从 800 条 test 池中抽选 150 条候选（RoboJudge physical-adherence 分布 PA1=9 / PA2=11 / PA3=45 / PA4=85），覆盖 Robotwin/Agibot/Droid/EpiKitchens 等 embodied corpora 与多个生成模型。
- RoboJudge 原始 judge-model 标注质量低，**不直接搬运**：每条视频按统一协议从像素**重新独立标注**物理缺陷（6fps 全片 + 原生帧率接触/抓取时刻放大），输出中文问题描述、应然行为、证据帧与 confidence；无缺陷的条目不进入发布文件。
- 这些结果是 agent draft，confidence 与 `needs_human_frame_step_confirmation` 字段保留供人工抽检。

### PhyGround (91) / VideoPhy2 (100)

- 由协作者 juyil 用 agent 流程在 PhyGround、VideoPhy2 测试视频上标注（含 gpt 投票与 severity），我方将其**直接搬运并转换**为本仓库统一 schema；未再做逐帧像素复核。
- 视频与文本质量以 juyil 源仓库为准；人工审核时如发现误报直接 reject。

## 统一标注 schema（jsonl）

| 字段 | 含义 |
|---|---|
| `slot` | 来源内部槽位号 |
| `record_id` | `<source>::<split>::<id>` 形式的全局 id |
| `dir_name` | 审核工作目录名 |
| `generator` | 生成模型 |
| `error_family` / `glitch_category_official` | 问题类别（时序/因果、物体永存/同一、力与运动、材质/状态、接触/交互、几何/碰撞等） |
| `interaction_primitive` | 视频内容（开合操作、倾倒/流动、拿取转移、形变/状态变化、肢体运动、多步操作、碰撞冲击、抛射等） |
| `scenario_domain` | 场景域（刚体、可变形材料、流体/热/光、人/动物肢体、机器人操作等） |
| `review_error_category` | 复核后的细分错误类别 |
| `obviousness` / `confidence` / `needs_human_frame_step_confirmation` / `all_claimed_errors_visible` | 复核难度与置信度 |
| `annotation` | 来源原始标注（Physion 为官方英文原文；juyil 来源为其人工/agent 摘要；RoboJudge 该字段为任务指令，物理结论以 fix_* 字段为准） |
| `fix_problems` | **结构化修复标注·问题**：「第X.Xs–Y.Ys：问题」逐条 |
| `fix_expected` | **结构化修复标注·正确表现**：与 problems 一一对应 |
| `fix_keep` | 修复时需保持不变的内容 |
| `fixing_prompt_zh` | 由上述三段拼成的完整中文修复指令（可直接发给 videogen） |

修复指令示例：

```
【存在的问题】
1. 第6.1s–6.2s：搅拌碗突然消失并变成塑料布
【应修改为】
1. 搅拌碗应持续留在台面原位
请在保持棕面团形变、手臂、石台、排插、木勺杯、消毒器、蓝电器、透明塑料布保持不变的前提下，修正上述物理问题并重新生成视频。
```

CSV 为同内容表格（UTF-8 BOM，Excel 可开），并附 `审核结论(pass/edit/reject)`、`修改后内容`、`备注` 三个空列供人工审核填写。

## 人工审核方式

1. Physion-300：打开 `index.html`（与 HF 数据目录同级；视频走 HF resolve URL，需登录有访问权限的 HF 账号）。
2. 播放视频，对照 ❶问题 / ❷正确表现 / ❸保持不变 三块；可直接在框中修改文字。
3. 每条选择 **通过 / 需修改 / 驳回**，可填备注；结果自动暂存在浏览器，点右上角「导出审核结果 JSON」回收。
4. RoboJudge / PhyGround / VideoPhy2 的审核页随后发布（字段与 CSV 审核列完全一致）。

## License / 使用限制

视频版权与使用限制遵循各来源：Physion-Eval 为 **Custom Research Use Only License**（仅限非商业研究与评测用途）；RoboJudge / PhyGround / VideoPhy2 视频遵循各自数据集许可。本仓库仅用于学术研究，不得违反适用法律或第三方权利再分发。结构化中文标注为 PhysFixBench 项目所有（研究用途）。
