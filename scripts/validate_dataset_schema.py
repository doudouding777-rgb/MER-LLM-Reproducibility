#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "data/dataset_16k/full/restoration_final_cleaned.json",
    ROOT / "data/dataset_16k/train/train.json",
    ROOT / "data/dataset_16k/validation/val.json",
]
REQUIRED = {"instruction", "input", "output", "system"}

for path in FILES:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected list")
    for i, row in enumerate(data[:100]):
        missing = REQUIRED - set(row)
        if missing:
            raise SystemExit(f"{path}: row {i} missing {sorted(missing)}")
    print(f"PASS {path.relative_to(ROOT)} records={len(data)}")
