#!/usr/bin/env python3
import importlib.util

packages = ["torch", "transformers", "peft", "datasets", "accelerate", "chromadb", "sentence_transformers", "numpy", "pandas", "scipy", "sklearn"]
for pkg in packages:
    print(f"{pkg}: {'available' if importlib.util.find_spec(pkg) else 'missing'}")
