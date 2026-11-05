# PhyFixBench

<p align="center">
<b>物理视频修复（Physics Video Correction）基准</b><br/>
带物理缺陷的文生视频 × 结构化中文修复指令（fixing prompts）
</p>

<p align="center">
<a href="https://huggingface.co/datasets/HuggingFriends/PhysFixBench"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-Dataset-orange"></a>
<img src="https://img.shields.io/badge/videos-606-blue">
<img src="https://img.shields.io/badge/annotations-606-green">
<img src="https://img.shields.io/badge/sources-4-purple">
<img src="https://img.shields.io/badge/language-zh-red">
</p>

每条样本是一段由视频生成模型产生、且存在**可修复物理缺陷**的视频，配以结构化中文修复指令：第几秒出现了什么物理问题、正确表现应是什么、修复时需保持哪些内容不变。标注只针对**物理问题**，不包含语义对齐 / instruction following / control 类问题。

## 📦 batch1 一览

| 来源 | 条数 | 内容域 | 标注状态 |
|---|---:|---|---|
| **Physion-Eval**（severity 4–5 抽选） | 300 | 通用 / 受控物理 | 6fps + 原生帧率逐帧复核确认 |
| **RoboJudge**（仅 test split） | 115 | embodied 机器人操作 | 400 条全量逐帧**重新标注**（TP 115 / CLEAN 285） |
| **PhyGround** | 91 | 通用物理 | 协作者 agent 标注，待人工复核 |
| **VideoPhy2** | 100 | 通用物理 | 协作者 agent 标注，待人工复核 |

视频与标注托管在 Hugging Face（公开、无需登录）：
**<https://huggingface.co/datasets/HuggingFriends/PhysFixBench>**

> ⚠️ 除 Physion-300 已经逐帧复核确认外，其余三个来源均为 **agent draft**，保留了 `confidence` / `needs_human_frame_step_confirmation` 字段供人工抽审（pass / edit / reject）。

## ✅ Benchmark Eval · 172

**[打开 172 个 fixing task 的三 prompt 可视化页](fixing_tasks.html)**：最终确认通过的 batch1 评测子集，包含 172 个异常视频输入和三种提示条件：

1. `self_fixing`：不给问题描述，也不给正确表现；
2. `problem_only`：只给第几秒出现什么问题；
3. `problem_expected`：给问题和应修改为的正确表现。

对应 HF 数据位于 [`data/reviewed_batch1/`](https://huggingface.co/datasets/HuggingFriends/PhysFixBench/tree/main/data/reviewed_batch1)。

## batch2 · 人工审核

**[打开 batch2 人工审核页](batch2.html)**：217 条新增预标注候选（Physion-Eval 124、Physics-IQ 82、MME-COF 8、VideoPhy2 Seedance 3），均待人工确认。另外保留 89 条未推荐视频供人工补捞。视频在 HF，支持直接修改问题、正确表现并导出结果。详见 [交付说明](docs/batch2_human_review.md)。

## ⏳ 即将发布（独立数据集，未并入 batch1）

| 数据集 | 条数 | 状态 | 说明 |
|---|---:|---|---|
| **PhysicsIQ-154** | 154 | `publication_in_progress`（媒体待上传） | 数据来源：Google DeepMind Physics-IQ；视频由 Seedance 2.5 基于其 switch frames + bpp_base prompts 自行 I2V 生成，**非官方 reference clip**；issue/fix 为机器初判，仅 1 条已经独立人工复核，其余 153 条待人工抽审。详见 [候选浏览页](physicsiq.html) 与 [发布状态](data/physicsiq154/PUBLISH_STATUS.json)。 |

> 该数据集**不并入**上方 batch1 的 606 计数；媒体上传完成前不对外宣称可播放。

## 🚀 快速使用

```python
import json

rows = [json.loads(l) for l in open("data/physfixbench_physion300.jsonl")]
ex = rows[0]

print(ex["generator"])        # 生成模型
print(ex["fixing_prompt_zh"]) # 可直接发给视频生成/编辑模型的中文修复指令
# 视频位于 HF 仓库：videos/<dir_name>.mp4
video_url = f"https://huggingface.co/datasets/HuggingFriends/PhysFixBench/resolve/main/videos/{ex['dir_name']}.mp4"
```

修复指令示例（来自真实样本）：

```
【存在的问题】
1. 第6.1s–6.2s：搅拌碗突然消失并变成塑料布
【应修改为】
1. 搅拌碗应持续留在台面原位
请在保持棕面团形变、手臂、石台、木勺杯等其余内容不变的前提下，修正上述物理问题并重新生成视频。
```

## 📂 仓库结构

```
PhyFixBench/
├── README.md                  # 本文件
├── datasets.html              # 数据集导航（Physion-300 / PhysicsIQ-154）
├── index.html                 # Physion-300 人工审核页（视频走 HF 公开 URL）
├── physicsiq.html             # PhysicsIQ-154 候选浏览页（媒体待上传）
├── data/
│   ├── physfixbench_physion300.{jsonl,csv}   # 300
│   ├── physfixbench_robojudge115.{jsonl,csv} # 115
│   ├── physfixbench_videophy2.{jsonl,csv}    # 100
│   ├── physfixbench_phyground.{jsonl,csv}    # 91
│   └── physicsiq154/
│       ├── README.md
│       ├── NOTICE.md
│       ├── MANIFEST.json
│       ├── PUBLISH_STATUS.json   # publication_in_progress / media_uploaded=false
│       └── records/
│           ├── index.json        # 5 shard 清单（154 条）
│           ├── shard_00.jsonl    # 31 条
│           ├── shard_01.jsonl    # 31 条
│           ├── shard_02.jsonl    # 31 条
│           ├── shard_03.jsonl    # 31 条
│           └── shard_04.jsonl    # 30 条
└── docs/
    ├── annotation_protocol.md  # 四来源构造流程与逐帧复核协议
    ├── data_schema.md          # 18 个字段定义 + PhysicsIQ-154 字段
    └── human_review.md         # 人工审核操作说明
```

JSONL 为权威格式；CSV（UTF-8 BOM，Excel 可直接打开）额外附带 `审核结论(pass/edit/reject)`、`修改后内容`、`备注` 三个空列供审核填写。

## 📖 文档

- [数据集导航](datasets.html) — Physion-300 人工审核页 ↔ PhysicsIQ-154 候选浏览页
- [172 Fixing Tasks · 三种 Prompt](fixing_tasks.html) — benchmark eval 输入视频与三种 prompt 条件
- [标注构造流程与逐帧复核协议](docs/annotation_protocol.md) — 各来源数据如何产生、误报如何剔除、分布统计
- [数据字段与修复指令格式](docs/data_schema.md) — batch1 的 18 个字段 + PhysicsIQ-154 字段
- [人工审核说明](docs/human_review.md) — 审核页面使用与结论回收

## 🧭 Provenance（来源）

- **batch1**：4 个来源并列——Physion-Eval（severity 4–5 抽选 300）、RoboJudge test split（全量重标注 115）、PhyGround（协作者 agent 标注 91）、VideoPhy2（协作者 agent 标注 100）。
- **PhysicsIQ-154**：源数据集为 Physics-IQ / Physics-IQ Verified by Google DeepMind（代码仓 <https://github.com/google-deepmind/physics-iq-benchmark>，站点 <https://physics-iq.github.io/>；输入 gated <https://huggingface.co/datasets/Anates-Labs-Research/Physics-IQ-Verified>）。本仓库 154 条视频由 **Seedance 2.5** 基于其 switch frames + bpp_base prompts **自行 I2V 生成**，**非官方 reference clip**。
- 完整 394 条机器标注里仅 2 条经独立人工复核：`0034_v2`（确认 issue，纳入）与 `0092_v2`（判 `reject_no_clear_issue`，**未纳入**）。

## ⚖️ License / 使用限制

- 仅限非商业研究与评测用途。
- **batch1 视频版权**遵循各来源数据集许可（Physion-Eval Custom Research Use、RoboJudge / PhyGround / VideoPhy2 各自许可）。
- **PhysicsIQ-154 源材料**遵循 Physics-IQ 上游许可：代码 Apache License 2.0（<https://www.apache.org/licenses/LICENSE-2.0>），其他材料 CC BY 4.0（<https://creativecommons.org/licenses/by/4.0/legalcode>），Copyright 2025 Google LLC（"This is not an official Google product."）。本仓库派生的 I2V 视频与中文修复标注的再分发须同时满足上述源许可与 PhyFixBench 项目约定；**不声明全部内容可自由再分发**，本 release 自身尚未选定 LICENSE。
- **结构化中文修复标注**（fixing prompts）为 PhyFixBench 项目所有，研究用途。
- 详见 [标注协议文档](docs/annotation_protocol.md#license--使用限制)。

## 📝 NOTICE

- 本仓库**未声明** MIT / Apache-2.0 等开源软件许可证；batch1 视频与标注的再分发受上述各来源许可约束。
- `0092_v2` 经独立人工复核判 `reject_no_clear_issue`，**不包含**在 PhysicsIQ-154 内。
- `0034_v2` 是 PhysicsIQ-154 内**唯一**经独立人工复核确认 issue 的记录；其人工 issue（2.5–2.92s 绿色块无接触倾倒）与机器 issue（1–4s 间距过小）不一致，UI 以人工 issue 为准、机器原注释折叠保留。
- PhysicsIQ-154 媒体上传完成前不对外宣称可播放；二进制 base64 适配未启用，媒体以原始 mp4 经授权通道就位。
