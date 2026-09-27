---
library_name: peft
license: other
base_model: <LOCAL_QWEN2_5_1_5B_INSTRUCT_PATH>
tags:
- llama-factory
- lora
- generated_from_trainer
model-index:
- name: train_2025-07-10-14-16-21
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# train_2025-07-10-14-16-21

This model is a fine-tuned version of [<LOCAL_QWEN2_5_1_5B_INSTRUCT_PATH>](https://huggingface.co/<LOCAL_QWEN2_5_1_5B_INSTRUCT_PATH>) on the train dataset.
It achieves the following results on the evaluation set:
- Loss: 1.2080
- Num Input Tokens Seen: 71545824

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 4e-05
- train_batch_size: 4
- eval_batch_size: 4
- seed: 42
- gradient_accumulation_steps: 8
- total_train_batch_size: 32
- optimizer: Use adamw_torch with betas=(0.9,0.999) and epsilon=1e-08 and optimizer_args=No additional optimizer arguments
- lr_scheduler_type: cosine
- lr_scheduler_warmup_steps: 300
- num_epochs: 4.0

### Training results



### Framework versions

- PEFT 0.15.2
- Transformers 4.52.4
- Pytorch 2.7.1+cu126
- Datasets 3.6.0
- Tokenizers 0.21.1