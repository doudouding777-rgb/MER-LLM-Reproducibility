#!/usr/bin/env python3
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "checksums/sha256_manifest.csv"
out.parent.mkdir(exist_ok=True)

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["relative_path", "sha256", "size"])
    writer.writeheader()
    for path in sorted(p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts):
        if path == out:
            continue
        writer.writerow({"relative_path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size": path.stat().st_size})
print(f"Wrote {out}")
