# Engineering Benchmark Report

This benchmark compares the original Base model and the final MER LoRA model on the same GPU, precision, prompt set, decoding settings, and max_new_tokens.

No model training, full evaluation rerun, RAG execution, or historical score modification was performed.

## Configuration
- GPU: NVIDIA GeForce RTX 4090 D
- Base model: `<LOCAL_QWEN2_5_1_5B_INSTRUCT_PATH>`
- MER adapter: `<LOCAL_MER_LORA_ADAPTER_PATH>`
- Precision: float16
- Prompts: 40
- Repeats: 3
- Warmup: 1
- max_new_tokens: 128
- Decoding: greedy (`do_sample=False`)

## Summary

### Base
- Mean first-token latency: 0.0464 ± 0.0028 s
- Mean end-to-end latency: 1.7159 ± 1.3376 s
- Mean tokens/s: 34.4539 ± 4.2989
- Mean GPU memory after load: 3862.00 MiB
- Mean peak allocated memory during generation: 2960.93 MiB

### MER
- Mean first-token latency: 0.0762 ± 0.0148 s
- Mean end-to-end latency: 4.9435 ± 1.6628 s
- Mean tokens/s: 18.9107 ± 1.5765
- Mean GPU memory after load: 3934.00 MiB
- Mean peak allocated memory during generation: 3000.59 MiB
