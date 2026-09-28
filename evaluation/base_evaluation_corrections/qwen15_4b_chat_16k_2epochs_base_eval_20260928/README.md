# Qwen1.5-4B-Chat Dataset-16k Base Evaluation Correction

This directory documents a correction for the base-model evaluation associated with:

- model: Qwen1.5-4B-Chat
- dataset configuration: Dataset-16k
- fine-tuning setting used for comparison: 2 epochs
- corrected evaluation date: 2026-09-28

## Rationale

The historical before/base metrics previously associated with this configuration were not used for the corrected comparison because their throughput and runtime imply a different evaluation-set size from the confirmed 1,664-example after-evaluation set.

The corrected base evaluation was therefore run on the same `val` dataset used by the after-evaluation, with 1,664 examples and without loading a LoRA adapter.

## Verification Summary

- `eval_dataset`: `val`
- number of examples: 1,664
- model path: `/root/autodl-tmp/models/Qwen/Qwen1___5-4B-Chat`
- LoRA adapter: not loaded
- cutoff length: 1024
- max new tokens: 512
- evaluation batch size: 8
- temperature: 0.95
- top-p: 0.7
- template: `qwen`
- generation evaluation: enabled

## Corrected Base Results

| Metric | Value |
|---|---:|
| BLEU-4 | 5.668036598557692 |
| ROUGE-1 | 30.653278125 |
| ROUGE-2 | 9.960576141826921 |
| ROUGE-L | 18.106114723557692 |
| Model preparation time | 0.012 |
| Runtime seconds | 1519.7308 |
| Samples/s | 1.095 |
| Steps/s | 0.137 |

The files in this directory are lightweight evaluation evidence only. No model weights, LoRA checkpoint files, optimizer states, or generated record-level private artifacts are included.
