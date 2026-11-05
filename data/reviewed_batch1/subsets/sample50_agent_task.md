# PhyFixBench sample50 generation task

You need to generate corrected videos for the 50-video PhyFixBench subset.

## Input file

Use this file:

`data/reviewed_batch1/subsets/sample50_fixing_prompts_3way_en.jsonl`

HF link:

`https://huggingface.co/datasets/HuggingFriends/PhysFixBench/blob/main/data/reviewed_batch1/subsets/sample50_fixing_prompts_3way_en.jsonl`

Each row has:

- `record_id`
- `dir_name`
- `video_url`
- `self_fixing_prompt_en`
- `problem_only_prompt_en`
- `problem_expected_prompt_en`

## What to run

For each row, run three video-editing generations using the same input video:

1. `self_fixing`: use `self_fixing_prompt_en`
2. `problem_only`: use `problem_only_prompt_en`
3. `problem_expected`: use `problem_expected_prompt_en`

Do not rewrite or enrich the prompts. Use the text exactly as provided.

## Output directory

Use this layout:

```text
outputs/<model_slug>/
├── self_fixing/
│   └── <safe_record_id>.mp4
├── problem_only/
│   └── <safe_record_id>.mp4
├── problem_expected/
│   └── <safe_record_id>.mp4
└── generation_metadata.jsonl
```

For Seedance, use:

```text
outputs/seedance/
```

For another model, replace `seedance` with a stable lowercase model name, for example:

```text
outputs/wan_i2v_edit/
outputs/kling_video_edit/
outputs/veo_video_edit/
```

`safe_record_id` means replace every character outside `[A-Za-z0-9._-]` with `_`.

## Metadata

Write one line per generation to:

`outputs/<model_slug>/generation_metadata.jsonl`

Each line should be:

```json
{
  "record_id": "...",
  "dir_name": "...",
  "model_slug": "seedance",
  "prompt_variant": "self_fixing | problem_only | problem_expected",
  "input_video_url": "...",
  "prompt_en": "...",
  "output_video": "outputs/<model_slug>/<prompt_variant>/<safe_record_id>.mp4",
  "status": "success | failed | unsupported",
  "error": "",
  "generation_params": {}
}
```

## Expected count

For one model:

`50 videos × 3 prompt variants = 150 generation attempts`

The metadata file must contain exactly 150 rows unless the model is unsupported for video editing.

## Important

- Output should be a corrected video, not a text answer.
- Preserve the original scene, subjects, intended action, camera, duration, and visual style.
- Only correct the physical issue allowed by the prompt condition.
- Do not add captions, text overlays, watermarks, or explanation screens.
- If the model cannot edit an input video, set `status="unsupported"` for all rows.
