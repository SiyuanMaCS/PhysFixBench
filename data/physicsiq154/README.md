# PhysicsIQ-154 Release Card

- **Release tag:** `physicsiq154-v1.0.0`
- **Record count:** 154 (selected from 394 machine-pre-annotated records by `review_bucket = candidate`)
- **Video count:** 154 (one MP4 per record, byte-preserved from source)
- **Status:** Standalone dataset under `data/physicsiq154/`. **Metadata published; videos not yet uploaded.** See `../PUBLISH_STATUS.json`.

## Layout (relative to repo root)

```
data/physicsiq154/
  README.md                      # this card
  NOTICE.md                      # upstream attribution and rights separation
  MANIFEST.json                  # release metadata, counts, source receipt hashes
  PUBLISH_STATUS.json            # publication_in_progress / media_uploaded=false
  records/
    index.json                   # 5-shard manifest (154 records total)
    shard_00.jsonl               # 31 records
    shard_01.jsonl               # 31 records
    shard_02.jsonl               # 31 records
    shard_03.jsonl               # 31 records
    shard_04.jsonl               # 30 records
videos/physicsiq154/
  {record_id}.mp4                # pending upload; e.g. 0002_v2.mp4, 0059_v1.mp4
```

The slim canonical 154-record JSONL is sharded under `records/` (see `index.json` for the
shard manifest). The single-file `physicsiq154.jsonl` and `media_map.json` are kept locally
for reproducibility but are not published to this repo; shards are the authoritative on-disk
form here.

## Record primary key

Unique key is `record_id` (e.g. `0034_v2`). The trailing `_v1` / `_v2` suffix is part of
the opaque unique key and distinguishes generated variants per source scene; it is **not**
a display grouping — the browsing page renders them as `Sample 001..154` with the original
`record_id` kept as the key only.

## Per-record fields (slim canonical)

```
record_id, id, version, scenario, original_prompt, duration_s,
video:  {path, sha256, bytes},
source: {dataset, release, original_sha256, preview_sha256, has_preview},
machine_review: {
  status, decision, observed_summary, reject_reason,
  issues: [{time_start_s, time_end_s, issue_description,
            fix_expected, evidence, ambiguity}],
  quality_notes: [{flag, note}],
  superseded_by_human_review, normalization_note
},
human_review: {status, authoritative, independent_review}
```

- `machine_review.issues[].fix_expected` is the repair instruction.
- `source.original_sha256 == video.sha256` and matches `SHA256SUMS.txt` (pending).
- `quality_notes` are downstream-facing neutral notes; internal raw-QC wording is removed.

## Human review status

Across the full 394-record machine annotation, exactly **2** records carry an independent
human review:

- `0034_v2` — inside this release, `human_review.status = "independent_confirmed"`,
  `human_review.authoritative = true`.
- `0092_v2` — independently reviewed but rejected as `reject_no_clear_issue`, therefore
  **NOT included** in this 154 release.

The remaining **153** records are machine pre-annotations with
`human_review.status = "pending_human_review"`.

### 0034_v2 disambiguation (important)

For `0034_v2`, the machine issue and the human-confirmed issue describe **different**
events:

- `machine_review.issues` (retained as raw model output,
  `superseded_by_human_review = true`): block spacing too small, domino chain triggered
  without contact, t≈1.0–4.0 s.
- `human_review.independent_review` (authoritative): green block falls left without contact
  from the pink block or stick, t≈2.5–2.92 s; subsequent blue/purple blocks also fall
  without contact.

**Treat `human_review.independent_review.issue_description` and `.fix_expected` as the
authoritative repair instruction for 0034_v2.** The machine issue is kept only for
transparency and was NOT human-confirmed.

## Provenance

The underlying benchmark is **Physics-IQ / Physics-IQ Verified** by Google DeepMind:

- Code repository: https://github.com/google-deepmind/physics-iq-benchmark
- Project website: https://physics-iq.github.io/
- Input dataset (gated HuggingFace): https://huggingface.co/datasets/Anates-Labs-Research/Physics-IQ-Verified
- Upstream LICENSE: Apache License 2.0 for software; Creative Commons Attribution 4.0
  International (CC-BY-4.0) for other materials. Copyright 2025 Google LLC.
  ("This is not an official Google product.")

The 154 MP4s in this release are **generated I2V videos produced by Seedance 2.5**, conditioned
on Physics-IQ Verified switch frames and bpp_base prompts. They are NOT the official real-camera
Physics-IQ reference footage. No official PhysicsIQ metric score is computed or claimed here.

## License and redistribution

Two distinct right layers apply — do not conflate them:

1. **Upstream Physics-IQ materials** (code, prompts, switch frames, website content) are
   governed by the upstream LICENSE: Apache-2.0 (code) / CC-BY-4.0 (other materials),
   Copyright 2025 Google LLC. Our use of them is conditioned on those terms.
2. **This release's generated videos and annotations** are derivative outputs. Their
   redistribution terms are **to be confirmed** before public upload:
   - Annotation text (`records/*.jsonl`, `MANIFEST.json`, docs): license not yet chosen;
     do not treat as public domain or any specific license until explicitly confirmed.
   - Generated videos (`videos/physicsiq154/*.mp4`): redistribution status pending
     confirmation; this package does NOT attach a MIT/Apache/CC license to them.
   - A `LICENSE` file will be added only after the annotation license and video
     redistribution terms are actually confirmed.

## Verification

Videos are byte-copied: no re-encode, no crop, no speed change. Verify with:

```
sha256sum -c videos/physicsiq154/SHA256SUMS.txt
```
