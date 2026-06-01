#!/usr/bin/env python3
"""Download a small HumanEval-X sample for IST smoke tests."""

import argparse
import json
from pathlib import Path

from huggingface_hub import hf_hub_download


DATASET_REPO = "zai-org/humaneval-x"
LANGUAGE_FILES = {
    "cpp": "data/cpp/data/humaneval.jsonl",
    "go": "data/go/data/humaneval.jsonl",
    "java": "data/java/data/humaneval.jsonl",
    "js": "data/js/data/humaneval.jsonl",
    "python": "data/python/data/humaneval.jsonl",
}


def build_code(record: dict) -> str:
    return f"{record.get('prompt', '')}{record.get('canonical_solution', '')}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a small JSONL sample from zai-org/humaneval-x."
    )
    parser.add_argument(
        "--language",
        choices=sorted(LANGUAGE_FILES),
        default="java",
        help="HumanEval-X language split to sample.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of records to write.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSONL path. Defaults to dataset/humanevalx_<language>_sample.jsonl.",
    )
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")

    output = args.output or Path("dataset") / f"humanevalx_{args.language}_sample.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)

    source_path = hf_hub_download(
        DATASET_REPO,
        filename=LANGUAGE_FILES[args.language],
        repo_type="dataset",
    )

    count = 0
    with open(source_path, "r", encoding="utf-8") as src, open(
        output, "w", encoding="utf-8"
    ) as dst:
        for line in src:
            if count >= args.limit:
                break
            record = json.loads(line)
            sample = {
                "task_id": record["task_id"],
                "language": args.language,
                "source": DATASET_REPO,
                "func": build_code(record),
                "prompt": record.get("prompt", ""),
                "canonical_solution": record.get("canonical_solution", ""),
                "test": record.get("test", ""),
            }
            dst.write(json.dumps(sample, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} records to {output}")


if __name__ == "__main__":
    main()
