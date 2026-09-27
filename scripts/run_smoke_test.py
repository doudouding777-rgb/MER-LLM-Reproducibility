#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data/dataset_16k/train/train.json").read_text(encoding="utf-8"))
sample = data[:10]
assert len(sample) == 10
assert all("instruction" in row and "output" in row for row in sample)
print("PASS smoke test: loaded 10 Dataset-16k training examples")
print("Tokenizer/LoRA forward-pass smoke test intentionally not run by default to avoid model download or long GPU jobs.")
