# Known Limitations

- Dataset-30k and Dataset-46k record-level contents are not public.
- Historical data splits are preserved as files, but the original split shuffle seed was not explicitly fixed in preserved scripts.
- Configuration-level expert ICC is preserved; item-level short-answer ICC is not preserved.
- RAG sensitivity does not establish general SFT-over-RAG superiority.
- Engineering benchmark supports local single-GPU feasibility, not edge-device deployment.
