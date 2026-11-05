# PhyFixBench reviewed batch1 sample50

A deterministic 50-video subset sampled from `data/reviewed_batch1/annotations.jsonl`.

Selection rule: source-proportional stratification from the 194 accepted tasks, then round-robin diversity over `error_family`, `generator`, and single-vs-multi issue count.

| Source | Count |
|---|---:|
| physion_eval | 25 |
| robojudge | 10 |
| phyground | 9 |
| videophy2 | 6 |


Files:

- `sample50_annotations.jsonl`: final benchmark records for the 50 videos.
- `sample50_fixing_prompts_3way.jsonl`: self-fixing / problem-only / problem+expected prompt variants.
- `sample50.csv`: compact table for spreadsheets.
- `sample50_manifest.jsonl`: video URLs and SHA256.
- `sample50.json`: same records in a JSON envelope with selection metadata.

All videos are referenced by the public `video_url` field; no videos are duplicated in this subset folder.
