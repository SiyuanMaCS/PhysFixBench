#!/usr/bin/env python3
"""Build three aligned prompt variants for reviewed_batch1 annotations."""
import csv
import json
import subprocess
from pathlib import Path

from huggingface_hub import hf_hub_download

REPO = "HuggingFriends/PhysFixBench"


def hf_token() -> str:
    result = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=huggingface.co\n\n",
        text=True,
        capture_output=True,
        check=True,
    )
    return dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)["password"]


def rows_from_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def norm(text: str) -> str:
    return str(text).strip().rstrip("。")


def self_fixing_prompt() -> str:
    return (
        "【任务】\n"
        "请观察输入视频，自行识别并修正其中不符合物理规律的内容，重新生成视频。\n"
        "【保持不变】\n"
        "除需要修正的物理问题外，请保持视频其余内容不变。"
    )


def problem_only_prompt(record: dict) -> str:
    lines = ["【存在的问题】"]
    for i, issue in enumerate(record["issues"], 1):
        lines.append(f'{i}. 第{issue["timestamp"]}秒：{norm(issue["problem"])}')
    lines += [
        "【任务】",
        "请修正上述物理问题并重新生成视频。",
        "【保持不变】",
        "除上述物理问题外，请保持视频其余内容不变。",
    ]
    return "\n".join(lines)


def problem_expected_prompt(record: dict) -> str:
    lines = ["【存在的问题】"]
    for i, issue in enumerate(record["issues"], 1):
        lines.append(f'{i}. 第{issue["timestamp"]}秒：{norm(issue["problem"])}')
    lines.append("【应修改为】")
    for i, issue in enumerate(record["issues"], 1):
        lines.append(f'{i}. {norm(issue["expected"])}')
    lines += [
        "【保持不变】",
        "除上述物理问题外，请保持视频其余内容不变。",
    ]
    return "\n".join(lines)


def main():
    token = hf_token()
    annotations_path = Path(
        hf_hub_download(
            repo_id=REPO,
            repo_type="dataset",
            filename="data/reviewed_batch1/annotations.jsonl",
            revision="main",
            token=token,
            force_download=True,
        )
    )
    records = rows_from_jsonl(annotations_path)
    out_rows = []
    for record in records:
        out_rows.append(
            {
                "record_id": record["record_id"],
                "dir_name": record["dir_name"],
                "source": record["source"],
                "generator": record["generator"],
                "video_path": record["video_path"],
                "video_url": record["video_url"],
                "issue_count": len(record["issues"]),
                "self_fixing_prompt_zh": self_fixing_prompt(),
                "problem_only_prompt_zh": problem_only_prompt(record),
                "problem_expected_prompt_zh": problem_expected_prompt(record),
            }
        )
    out_dir = Path("/mnt/bn/embodied-lf3/masiyuan/PhysFix-workspace/batch1/PhysFixBench-gh/data/reviewed_batch1")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "fixing_prompts_3way.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in out_rows),
        encoding="utf-8",
    )
    (out_dir / "fixing_prompts_3way.json").write_text(
        json.dumps({"schema": "phyfixbench-fixing-prompts-3way-v2", "count": len(out_rows), "records": out_rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (out_dir / "fixing_prompts_3way.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    (out_dir / "fixing_prompts_3way.README.md").write_text(
        """# Three fixing prompt variants

This file defines three aligned prompt conditions for the reviewed batch1 benchmark videos.

1. `self_fixing_prompt_zh`: no localized issue description and no expected behavior. The model must inspect the video and self-identify the physical inconsistency.
2. `problem_only_prompt_zh`: gives only the time-localized problem description. It does not state the correct target behavior.
3. `problem_expected_prompt_zh`: gives both the time-localized problem description and the expected physically correct behavior.

All three variants use the same ending policy: keep the rest of the video unchanged instead of enumerating protected objects. The benchmark record itself remains `annotations.jsonl`.
""",
        encoding="utf-8",
    )
    assert len(out_rows) == len(records)
    assert len({row["self_fixing_prompt_zh"] for row in out_rows}) == 1
    assert all("【应修改为】" not in row["problem_only_prompt_zh"] for row in out_rows)
    assert all("【应修改为】" in row["problem_expected_prompt_zh"] for row in out_rows)
    print(f"wrote {len(out_rows)} prompt rows to {out_dir}")


if __name__ == "__main__":
    main()
