# PhyFixBench sample50 generation tasks

This document defines the generation job for the 50-video subset of the reviewed PhyFixBench benchmark. The subset is intended for a small controlled run before scaling to the full 194-video evaluation set.

## Input files

Use the files in:

`https://huggingface.co/datasets/HuggingFriends/PhysFixBench/tree/main/data/reviewed_batch1/subsets`

Required files:

- `sample50_manifest.jsonl`: one row per input video, with `record_id`, `video_url`, SHA256, source, and generator metadata.
- `sample50_annotations.jsonl`: final reviewed benchmark annotations for the 50 videos.
- `sample50_fixing_prompts_3way_en.jsonl`: the English three-prompt conditions for each video. The Chinese file `sample50_fixing_prompts_3way.jsonl` is retained for reference.
- `sample50.csv`: spreadsheet-friendly version for manual tracking.

The corresponding input videos are referenced by `video_url` and are not duplicated in this folder.

## Prompt conditions

Each video must be generated under three prompt conditions. Do not add extra information that changes the information available in each condition.

### 1. `self_fixing`

Use `self_fixing_prompt_en`.

This condition gives no localized issue description and no expected behavior. The model must infer the physical problem from the input video.

### 2. `problem_only`

Use `problem_only_prompt_en`.

This condition gives only the time-localized physical problem description. It must not include the target/correct behavior.

### 3. `problem_expected`

Use `problem_expected_prompt_en`.

This condition gives both the time-localized physical problem and the expected physically correct behavior.

## Common generation rule

For every model and every condition:

- Input is the original anomalous video from `video_url`.
- Output should be a corrected video, not a textual answer.
- Preserve the original scene, subject, intended action, camera, duration, and visual style.
- Only correct the physical inconsistency exposed by the prompt condition.
- Do not add text overlays, captions, watermarks, diagnostic markers, or explanation screens.
- Keep aspect ratio and duration as close as the model API allows.
- If the model cannot take a video input, mark the row as `unsupported` instead of converting the task into plain text-to-video.

## Seedance run

Run all 50 videos under all three prompt conditions with Seedance video editing / video-to-video generation.

Total generations for Seedance:

`50 videos × 3 prompt conditions = 150 generated videos`

Recommended output layout:

```text
outputs/
└── seedance/
    ├── self_fixing/
    │   └── <safe_record_id>.mp4
    ├── problem_only/
    │   └── <safe_record_id>.mp4
    └── problem_expected/
        └── <safe_record_id>.mp4
```

Use this filename sanitizer for `safe_record_id`: replace every character outside `[A-Za-z0-9._-]` with `_`.

For each generation, save one metadata row to:

`outputs/seedance/generation_metadata.jsonl`

Required metadata fields:

```json
{
  "record_id": "...",
  "dir_name": "...",
  "source": "...",
  "model": "seedance",
  "prompt_variant": "self_fixing | problem_only | problem_expected",
  "input_video_url": "...",
  "prompt_en": "...",
  "output_video": "outputs/seedance/<prompt_variant>/<safe_record_id>.mp4",
  "status": "success | failed | unsupported",
  "error": "",
  "generation_params": {}
}
```

## Other model runs

Run the same 50×3 task grid for every other video editing model being compared.

Use this layout:

```text
outputs/
└── <model_slug>/
    ├── self_fixing/
    ├── problem_only/
    ├── problem_expected/
    └── generation_metadata.jsonl
```

`model_slug` should be lowercase and stable, for example:

- `wan_i2v_edit`
- `kling_video_edit`
- `hailuo_video_edit`
- `veo_video_edit`
- `hunyuan_video_edit`

Only compare models that can condition on the input video or a semantically equivalent video-editing input. If a model only supports text-to-video and cannot preserve the input video, record `status="unsupported"` for all rows for that model.

## No leakage between conditions

The three conditions are intentionally different. Do not enrich weaker conditions with information from stronger conditions:

- `self_fixing`: no issue timestamps, no problem text, no expected behavior.
- `problem_only`: problem text is allowed; expected behavior is not allowed.
- `problem_expected`: both problem and expected behavior are allowed.

Use exactly the English prompt text from `sample50_fixing_prompts_3way_en.jsonl` for each condition unless the generation API requires trivial wrapper fields such as JSON escaping.

## Completeness checklist

For each model:

- 150 generation attempts are represented in `generation_metadata.jsonl`.
- Every `record_id` appears exactly once for each prompt condition.
- Every successful row has a readable MP4 file at `output_video`.
- Failed or unsupported rows include a short error string.
- The generation metadata preserves the exact prompt text used.
- Output paths do not overwrite another condition or model.

## Minimal loader example

```python
import json
import re

def safe_id(record_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", record_id)

tasks = []
with open("sample50_fixing_prompts_3way_en.jsonl", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        for variant, key in [
            ("self_fixing", "self_fixing_prompt_en"),
            ("problem_only", "problem_only_prompt_en"),
            ("problem_expected", "problem_expected_prompt_en"),
        ]:
            tasks.append({
                "record_id": row["record_id"],
                "safe_record_id": safe_id(row["record_id"]),
                "variant": variant,
                "input_video_url": row["video_url"],
                "prompt": row[key],
            })

assert len(tasks) == 150
```
