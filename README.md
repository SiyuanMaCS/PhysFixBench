# PhysFixBench

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
PhysFixBench/
├── README.md                  # 本文件
├── index.html                 # Physion-300 人工审核页（视频走 HF 公开 URL）
├── data/
│   ├── physfixbench_physion300.{jsonl,csv}   # 300
│   ├── physfixbench_robojudge115.{jsonl,csv} # 115
│   ├── physfixbench_videophy2.{jsonl,csv}    # 100
│   └── physfixbench_phyground.{jsonl,csv}    # 91
└── docs/
    ├── annotation_protocol.md  # 四来源构造流程与逐帧复核协议
    ├── data_schema.md          # 18 个字段定义与修复指令格式
    └── human_review.md         # 人工审核操作说明
```

JSONL 为权威格式；CSV（UTF-8 BOM，Excel 可直接打开）额外附带 `审核结论(pass/edit/reject)`、`修改后内容`、`备注` 三个空列供审核填写。

## 📖 文档

- [标注构造流程与逐帧复核协议](docs/annotation_protocol.md) — 各来源数据如何产生、误报如何剔除、分布统计
- [数据字段与修复指令格式](docs/data_schema.md) — 18 个字段逐一说明
- [人工审核说明](docs/human_review.md) — 审核页面使用与结论回收

## License

仅限非商业研究与评测用途；视频版权遵循各来源数据集许可（Physion-Eval Custom Research Use、RoboJudge / PhyGround / VideoPhy2 各自许可），结构化中文标注为 PhysFixBench 项目所有。详见 [标注协议文档](docs/annotation_protocol.md#license--使用限制)。
