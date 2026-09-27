# RAG Sensitivity Report

This experiment evaluates whether modestly stronger RAG retrieval settings change the original RAG baseline conclusion.

No model training, manuscript editing, McNemar recalculation, or short-answer expert scoring was performed.

## Fixed Components

- Embedding model: `<LOCAL_BGE_LARGE_ZH_PATH>`
- Chunking: chunk_size=500, overlap=50
- Generator: Qwen2.5-1.5B-Instruct
- Temperature: 0.3
- Knowledge base, prompts, decoding settings, and evaluation questions were held constant across tested RAG configurations.
- Question mode: `objective`
- Pilot size: `full selected set`

## Reranker

- Reranker status: `not_configured`

## Summary

| config | top-k | reranker | n objective | parse rate | parseable accuracy | lower-bound accuracy |
|---|---:|---|---:|---:|---:|---:|
| RAG-A_top3_no_reranker | 3 | none | 1100 | 0.9527 | 0.8187 | 0.7800 |
| RAG-B_top5_no_reranker | 5 | none | 1100 | 0.9700 | 0.8201 | 0.7955 |

## Interpretation Guardrails

- Automatic scoring is used only for clearly parsed choice/judge responses.
- Ambiguous objective responses are marked for manual review rather than forced into an answer.
- Short-answer responses are generated and retained when included, but are not automatically expert-scored.
- Because no gold source-document labels are available, Recall@k/Hit@k is not reported.
- `RAG_RETRIEVAL_SAMPLE.csv` provides a fixed sample for later human relevance labeling.

## Reviewer Questions

1. top3 vs top5 results are provided in `RAG_SENSITIVITY_SUMMARY.csv`.
2. Reranker completion status is stated above.
3. Whether stronger RAG changes the original conclusion should be judged from the summary accuracy and manual-review burden.
4. Claims should be phrased as MER outperforming the tested RAG configurations only if the tested RAG results remain below MER.
5. Retrieval noise evidence should rely on retrieved chunks and manual-review flags, not invented source-label recall.
6. The RAG baseline criticism is empirically strengthened to the extent that top-k sensitivity and reranker feasibility are documented.