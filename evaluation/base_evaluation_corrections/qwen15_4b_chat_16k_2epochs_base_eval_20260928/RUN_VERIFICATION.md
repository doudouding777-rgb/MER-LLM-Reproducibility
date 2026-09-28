# Qwen1.5-4B-Chat Dataset-16k Base Evaluation Verification

Run date: 2026-09-28

Purpose:
Base-model evaluation for Qwen1.5-4B-Chat / Dataset-16k / 2 epochs comparison.

Important:
This is base evaluation only. No LoRA adapter was loaded.

Observed terminal evidence:

- model_name_or_path: `/root/autodl-tmp/models/Qwen/Qwen1___5-4B-Chat`
- Num examples = 1664
- Batch size = 8
- all params: 3,950,369,280
- All model checkpoint weights were used when initializing Qwen2ForCausalLM.
- All weights were initialized from `/root/autodl-tmp/models/Qwen/Qwen1___5-4B-Chat`.
- No `adapter_name_or_path` was present in the evaluation config.

Evaluation protocol:

- eval_dataset: val
- dataset_dir: data
- cutoff_len: 1024
- max_new_tokens: 512
- per_device_eval_batch_size: 8
- predict_with_generate: true
- temperature: 0.95
- top_p: 0.7
- template: qwen

Results:

- BLEU-4 = 5.668036598557692
- ROUGE-1 = 30.653278125
- ROUGE-2 = 9.960576141826921
- ROUGE-L = 18.106114723557692
- model preparation time = 0.012
- runtime = 1519.7308 s
- samples/s = 1.095
- steps/s = 0.137
