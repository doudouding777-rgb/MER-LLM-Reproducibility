# Reproducibility Audit

## 1. Project Summary

This repository is a cleaned public reproducibility package for MER-LLM.

## 2. Files Discovered

The source project was previously inventoried in `MER-LLM-Reproducibility_AUDIT_STAGE/INVENTORY_BEFORE_REORGANIZATION.csv`. This public package contains a curated subset with provenance and SHA256 hashes in `checksums/file_manifest.csv` and `checksums/sha256_manifest.csv`.

## 3. Dataset Status

- Dataset-16k: public record-level data included.
- Dataset-30k: metadata/config/log/results only; record-level contents excluded.
- Dataset-46k: metadata/config/log/results only; record-level contents excluded.

## 4. Dataset-16k Public Status

Dataset-16k is included as the complete public data example:

- full: 16,631 records
- train: 14,967 records
- validation: 1,664 records
- schema: Alpaca-style `instruction`, `input`, `output`, `system`

## 5. Dataset-30k Private Status

Dataset-30k has 30,890 records with a historical 27,801/3,089 split. Record-level contents are excluded due to project data-release restrictions. Metadata and config-only notes are public.

## 6. Dataset-46k Private Status

Dataset-46k has 46,213 records with a historical 41,591/4,622 split. Record-level contents are excluded due to project data-release restrictions. Metadata and config-only notes are public.

## 7. Preprocessing Reproducibility

Historical scripts are preserved as sanitized copies under `preprocessing/original_scripts/`.

## 8. Training Reproducibility

MER LoRA configuration and sanitized logs are included. Full training is partially reproducible because Dataset-30k is restricted and the exact historical software environment is only partially preserved.

The learning rate is `4.0e-05`.

## 9. Evaluation Reproducibility

The 1,100-item paired objective matrix and McNemar test script are public. Question-bank release requires author confirmation.

## 10. RAG Reproducibility

RAG configs, runner, and sensitivity results are public. Knowledge-base contents are not redistributed unless author confirms release permissions.

## 11. Engineering Benchmark Reproducibility

Raw and summary benchmark files are public. Re-running requires similar hardware and local model/adaptor availability.

## 12. Seeds

Training framework seed 42 is preserved. Historical dataset splitting script did not explicitly set the shuffle seed.

## 13. Environment

The environment is partially reconstructed in `requirements.txt`, `environment.yml`, and `docs/environment_uncertainty.md`. Exact historical versions still require author/environment confirmation.

## 14. Historical Inconsistencies

The learning rate is `4.0e-05`.

The final training framework log indicates a framework-level internal split: 25,020 train examples and 2,781 eval examples from a 27,801-record train file. This is documented in `docs/historical_split_note.md`.

## 15. Missing Files

- No record-level source-document provenance is preserved for final training JSON records.
- Exact historical package versions are only partially preserved.
- Public-release permission for Set1+Set2 question/answer JSON still requires author confirmation.

## 16. Copyright Issues

Raw source documents, standards, books, papers, converted full-text corpora, and potentially third-party question-bank materials are not redistributed by default.

## 17. Sensitive Files

Local absolute paths were sanitized in public text copies. No concrete API keys, passwords, private keys, bearer tokens, or cookies were intentionally copied. See `SECURITY_REDACTION_REPORT.md`.

## 18. Large Files

See `checksums/large_files_report.csv`.

## 19. Independently Reproducible From Public Repository

- Dataset-16k schema/count validation
- Dataset-16k small loading smoke test
- McNemar calculation from included paired correctness matrix
- inspection of final LoRA configuration
- inspection of RAG sensitivity and engineering benchmark outputs

## 20. Not Fully Independently Reproducible Because 30k/46k Are Restricted

- final Dataset-30k-based full training
- Dataset-46k historical training/evaluation runs
- any RAG knowledge-base build that depends on restricted corpus contents

## 21. Actions Still Needed From Author

1. Confirm final code and data licenses.
2. Confirm whether Set1+Set2 question/answer JSON can be public.
3. Confirm expert scoring release permission.
4. Confirm Data and Code Availability wording.
