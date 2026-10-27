# 标注构造流程与逐帧复核协议

本基准的 batch1 由四个并列来源构成，统一为同一套 [18 字段 schema](data_schema.md)。所有标注**只针对物理问题**：语义 / 指令对齐（instruction following）、任务是否完成、相机运动、模糊、美学、转场（cross-dissolve）一律不标。

多错误样本允许保留多个问题实例；每条结论必须能在**决定性原生帧**上看到证据，运动模糊帧不能单独作为判据。

---

## 1. Physion-Eval · physion300（300 条，已逐帧复核）

### 来源与候选池

- 视频来自 Physion-Eval 的 severity-4/5 候选池（seed 20261019 抽样的 1000 条队列），对应原数据集中质量最高、最接近「整体可用、仅有局部物理缺陷」的视频。
- 覆盖 5 个生成模型：Veo 3.1 Fast / Wan 2.2 / Hailuo 2.3 / Sora 2 / Kling 2.5（各 59–61 条）。

### 复核协议

1. 以 **6fps** 对全片抽帧，定位官方标注声称的物理问题时间区间；
2. 在问题区间用 **原生帧率（24/30fps）逐帧放大**核对，只有视觉证据确认缺陷真实存在才记 TP；
3. 误报（如把转角处两块不同朝向玻璃的反射差异误判为「天空与倒影不一致」）、语义对齐 / control / 美学问题一律剔除；
4. 在确认 TP 池上按 **问题类别 × 视频内容 41 个联合格子分层抽选**，保证稀有内容（碰撞、抛射、工具操作）覆盖，并保留明显 / 细微难度梯度。

### 分布

- 问题类别：时序 / 因果 92 · 物体永存 54 · 力与运动 48 · 材质 / 状态 47 · 接触 / 交互 34 · 几何 / 碰撞 23 · 其他 2。
- 其中 112 条为细微 cue（104 条 `needs_human_frame_step_confirmation=true`，建议人工逐帧复核）。
- 每条 `annotation` 字段保留 Physion-Eval 官方英文原文，结构化中文修复标注见 `fix_*` 字段。

---

## 2. RoboJudge · test split · robojudge115（115 条，全量重新标注）

### 为什么重新标注

RoboJudge 原始结论来自 judge model 的 PA（physical adherence）reasoning，文本质量参差、误报率高，因此**不直接搬运**，也不判定原标注的 TP/FP，而是从像素**重新独立标注**物理问题。严格只使用 RoboJudge **test split**，不使用 train conversations。

### 数据规模与覆盖

- 对 **400 条** test 视频做全量逐帧重标注 → 确认可修物理缺陷 **115 条**（CLEAN 285 条不发布）。
- 覆盖 8 个 embodied corpora：Robotwin / Agibot / Droid / EgoDex / EgoScaler / EpiKitchens / Open-X / GR1；
- 覆盖 20 个生成器变体：cogvideo / cosmos3 / wan22 / wan26 / gigaworld / wow-wan / abot-physworld / veo / kling / happyhorse（prefix / rewrite 等变体）。

### 复核协议

1. 每条视频 6fps 全片抽帧，在接触 / 抓取时刻用原生帧率放大；
2. worker 输出中文问题描述、应然行为、≥4 个证据原生帧与 confidence；
3. 编排者对每条 TP 草案再做一轮**原生帧像素 QC**，误报一律推翻为 CLEAN。典型被推翻案例：
   - 把夹爪前沿正常接触阴影误判为「物体悬空」；
   - 把腕部法兰上刚性随动的衣夹状配件误判为「复制的悬浮方块」；
   - 把真实入镜人手误判为机械臂熔接。

### 智能体类问题的边界

- 连续边缘的真实人手 / 手臂入镜替换或协同机器人、且**没有材质熔接** → 记为 agent 语义问题，**不计**物理缺陷；
- 机械臂本身的结构性缺陷计入：夹爪断裂脱落、多出一条手臂、前臂消失、夹指熔成无关节的一团等。

### 分布

- 115 条共 **150 个问题实例**（25 条多错误）：
  物体 / 场景一致性 93 · 智能体结构完整性 26 · 接触 / 交互 19 · 力与运动 12。
- 明显度：obvious 93 / subtle 22（issue 级 obviousness：2 分 2 个、3 分 27 个、4 分 62 个、5 分 59 个）。
- confidence 中位 0.91（范围 0.66–0.99）；17 条 `needs_human_frame_step_confirmation=true`（低分辨率 / 近单帧歧义）。
- `annotation` 字段为任务指令（非物理结论），物理结论以 `fix_*` 字段为准；`glitch_category_official` 保留原 PA 分数（`RoboJudge PA=<n>`）便于溯源。
- 视频扁平命名为 `robojudge__<dir_name>.mp4` 防止与其他来源文件名碰撞。

该来源为 **agent draft（已过编排者像素 QC）**，confidence 与 needs_human 字段保留供人工抽检。

---

## 3. PhyGround（91 条）/ VideoPhy2（100 条）

- 由协作者 juyil 用 agent 流程在两个数据集的测试视频上标注（含 gpt 投票与 severity），我方**直接搬运并转换**为统一 schema，未再做逐帧像素复核。
- 视频与文本质量以协作者源仓库为准；人工审核发现误报直接 reject。
- 两个来源合计 191 条，定位为覆盖通用物理场景的扩展来源。

---

## License / 使用限制

- 视频版权与使用限制遵循各来源：
  - **Physion-Eval**：Custom Research Use Only License，仅限非商业研究与评测用途；不得违反适用法律或第三方权利再分发；
  - **RoboJudge / PhyGround / VideoPhy2**：遵循各自数据集许可。
- 本仓库不主张视频版权，仅用于学术研究。
- 结构化中文标注（fixing prompts）为 PhysFixBench 项目所有，研究用途。
