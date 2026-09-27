# Historical Dataset Split Clarification

Verified exported splits:

- Dataset-30k: 27,801 train + 3,089 validation = 30,890
- Dataset-46k: 41,591 train + 4,622 validation = 46,213
- Dataset-16k: 14,967 train + 1,664 validation = 16,631

MER-LLM framework logs indicate:

- Train examples: 25,020
- Eval examples: 2,781
- Total loaded train-file examples: 27,801

Likely explanation: the training framework read a 27,801-record train file and internally split it again with `val_size=0.1`.

This is a historical clarification, not a rewritten result. The preserved training arguments include `val_size: 0.1`.
