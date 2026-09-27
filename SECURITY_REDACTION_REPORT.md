# Security Redaction Report

Sanitized public copies were generated for text files containing local absolute paths such as private workstation paths, AutoDL server paths, and Windows drive paths.

No concrete API keys, passwords, private keys, bearer tokens, or cookies were intentionally copied into the public package.

Known benign flag:

- `training/configs/final_mer_llm/llamaboard_config.yaml` contains an empty key field `train.swanlab_api_key: ''`. The value is empty; no secret was present.

Sensitive value patterns are not reproduced in this report.
