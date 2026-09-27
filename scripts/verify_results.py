#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "evaluation/statistics/mcnemar_test.py"
matrix = ROOT / "evaluation/paired_statistics/FINAL_HISTORICAL_PAIRED_CORRECTNESS.csv"
out = subprocess.check_output([sys.executable, str(script), str(matrix)], text=True)
print(out)
if "base_wrong_mer_correct,126" not in out or "base_correct_mer_wrong,81" not in out:
    raise SystemExit("McNemar paired counts did not match expected values")
print("PASS paired statistics")
