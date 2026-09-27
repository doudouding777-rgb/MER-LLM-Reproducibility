#!/usr/bin/env python3
"""
Run the MER-LLM RAG sensitivity experiment.

This script reuses the historical RAG design:
- BAAI/bge-large-zh-v1.5 embeddings
- chunk_size=500, overlap=50
- Qwen2.5-1.5B-Instruct generator
- temperature=0.3

It compares top-k=3 and top-k=5 retrieval. A reranker configuration is run
only when an explicit reranker model/path is supplied.
"""

import argparse
import csv
import json
import os
import platform
import random
import re
import statistics
import subprocess
import time
from pathlib import Path

import torch
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer


HISTORICAL_EMBEDDING = "BAAI/bge-large-zh-v1.5"
DEFAULT_GENERATOR = "<LOCAL_QWEN2_5_1_5B_INSTRUCT_PATH>"
SEED = 20260926


def run_cmd(args):
    try:
        return subprocess.check_output(args, text=True).strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def write_csv(path, rows, fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_question_text(text):
    first = text.split("\n")[0].strip()
    return re.sub(r"^\s*\d+\s*[\.\、]\s*", "", first)


def load_questions(path, mode, pilot_n):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = []
    for idx, item in enumerate(data, 1):
        if isinstance(item, str):
            qtype = "unknown"
            question = item
            qid = idx
            answer = ""
        else:
            qtype = item.get("type", "unknown")
            question = item.get("question_full_text") or item.get("question") or ""
            qid = item.get("id", idx)
            answer = item.get("answer", "")
        if mode == "objective" and qtype not in {"choice", "judge"}:
            continue
        if mode == "all" and qtype not in {"choice", "judge", "short"}:
            continue
        items.append({"question_id": qid, "question_type": qtype, "question": question, "standard_answer": answer})

    if pilot_n and pilot_n < len(items):
        rng = random.Random(SEED)
        by_type = {}
        for item in items:
            by_type.setdefault(item["question_type"], []).append(item)
        if mode == "objective":
            targets = {"choice": int(round(pilot_n * 850 / 1100)), "judge": pilot_n - int(round(pilot_n * 850 / 1100))}
        else:
            targets = {}
            total = len(items)
            used = 0
            for qtype, arr in sorted(by_type.items()):
                n = int(round(pilot_n * len(arr) / total))
                targets[qtype] = n
                used += n
            if used != pilot_n:
                first_key = sorted(targets)[0]
                targets[first_key] += pilot_n - used
        sampled = []
        for qtype, arr in sorted(by_type.items()):
            n = min(targets.get(qtype, 0), len(arr))
            sampled.extend(rng.sample(arr, n))
        items = sorted(sampled, key=lambda x: int(x["question_id"]))
    return items


def build_or_load_db(source_dir, db_dir, force_rebuild, embedding_device):
    embeddings = HuggingFaceEmbeddings(
        model_name=HISTORICAL_EMBEDDING,
        model_kwargs={"device": embedding_device},
        encode_kwargs={"normalize_embeddings": True},
    )
    db_dir = Path(db_dir)
    if force_rebuild or not (db_dir / "chroma.sqlite3").exists():
        if db_dir.exists():
            import shutil
            shutil.rmtree(db_dir)
        loader = DirectoryLoader(
            str(source_dir),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"autodetect_encoding": True},
            show_progress=True,
        )
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = splitter.split_documents(documents)
        for i, doc in enumerate(split_docs):
            doc.metadata["chunk_id"] = f"chunk_{i:06d}"
            doc.metadata["source"] = str(doc.metadata.get("source", ""))
        db = Chroma.from_documents(split_docs, embedding=embeddings, persist_directory=str(db_dir))
        return db, len(documents), len(split_docs)
    db = Chroma(persist_directory=str(db_dir), embedding_function=embeddings)
    return db, None, None


def load_reranker(model_name_or_path):
    if not model_name_or_path:
        return None, "not_configured"
    try:
        from sentence_transformers import CrossEncoder
    except Exception as exc:
        return None, f"sentence_transformers_missing: {exc}"
    try:
        return CrossEncoder(model_name_or_path), "loaded"
    except Exception as exc:
        return None, f"load_failed: {exc}"


def retrieve(db, query, top_k, reranker=None):
    candidates = db.similarity_search_with_score(query, k=top_k if reranker is None else max(top_k * 4, 20))
    rows = []
    for rank, (doc, score) in enumerate(candidates, 1):
        rows.append({
            "rank_pre": rank,
            "chunk_id": doc.metadata.get("chunk_id", ""),
            "source": doc.metadata.get("source", ""),
            "retrieval_score": score,
            "text": doc.page_content,
            "rerank_score": "",
        })
    if reranker is not None:
        pairs = [(query, row["text"]) for row in rows]
        scores = reranker.predict(pairs)
        for row, score in zip(rows, scores):
            row["rerank_score"] = float(score)
        rows.sort(key=lambda x: x["rerank_score"], reverse=True)
    return rows[:top_k]


def make_prompt(question, retrieved):
    context = "\n".join([f"[资料{i+1}]: {row['text']}" for i, row in enumerate(retrieved)])
    return f"""你是一个海洋生态修复领域的专家。请基于参考资料回答题目。

【作答要求】：
1. 如果是选择题：请直接给出正确选项（如 "A"），并简要解释原因。
2. 如果是判断题：请回答 "正确" 或 "错误"，并简要说明理由。
3. 如果是简答题：请根据资料归纳总结，条理清晰地回答。

【参考资料】：
{context}

【题目】：
{question}
"""


def parse_answer(qtype, response):
    text = response.strip()
    if not text:
        return "", "manual_review_empty"
    tail = text[-120:]
    if qtype == "choice":
        patterns = [
            r"(?:答案|正确选项|最终答案|应选|选择)\s*(?:是|为|：|:)?\s*([ABCD])",
            r"^\s*([ABCD])[\.\、\s]",
            r"因此\s*(?:答案|应选|选择)?\s*([ABCD])",
        ]
        hits = []
        for pat in patterns:
            hits.extend(re.findall(pat, text, flags=re.I))
        tail_hits = re.findall(r"\b([ABCD])\b", tail, flags=re.I)
        if hits:
            ans = hits[-1].upper()
            if len(set(h.upper() for h in hits[-3:])) == 1:
                return ans, "parsed"
            return ans, "manual_review_multiple_options"
        if tail_hits and len(set(h.upper() for h in tail_hits)) == 1:
            return tail_hits[-1].upper(), "parsed"
        return "", "manual_review_unparsed"
    if qtype == "judge":
        correct_terms = ["正确", "对", "是正确的"]
        wrong_terms = ["错误", "不正确", "错", "是错误的"]
        has_correct = any(x in tail for x in correct_terms)
        has_wrong = any(x in tail for x in wrong_terms)
        if has_correct and not has_wrong:
            return "正确", "parsed"
        if has_wrong and not has_correct:
            return "错误", "parsed"
        full_correct = any(x in text for x in correct_terms)
        full_wrong = any(x in text for x in wrong_terms)
        if full_correct and not full_wrong:
            return "正确", "parsed"
        if full_wrong and not full_correct:
            return "错误", "parsed"
        return "", "manual_review_unparsed"
    return "", "not_scored_short_answer"


def load_generator(model_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=dtype, trust_remote_code=True).to(device)
    model.eval()
    return tokenizer, model, device


@torch.inference_mode()
def generate(tokenizer, model, device, prompt, max_new_tokens, temperature):
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(device)
    start = time.perf_counter()
    output_ids = model.generate(
        inputs.input_ids,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=temperature,
        pad_token_id=tokenizer.eos_token_id,
    )
    if device == "cuda":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    generated = output_ids[0][inputs.input_ids.shape[-1]:]
    response = tokenizer.decode(generated, skip_special_tokens=True)
    return response, int(generated.shape[-1]), elapsed


def summarize(raw_rows, configs):
    rows = []
    for cfg in configs:
        name = cfg["name"]
        subset = [r for r in raw_rows if r["retrieval_configuration"] == name]
        objective = [r for r in subset if r["question_type"] in {"choice", "judge"}]
        parseable = [r for r in objective if r["ambiguity_flag"] == "parsed"]
        correct = [r for r in parseable if r["is_correct"] == "1"]
        gen_times = [float(r["generation_time_sec"]) for r in subset]
        rows.append({
            "retrieval_configuration": name,
            "top_k": cfg["top_k"],
            "reranker": cfg.get("reranker_name", ""),
            "n_total": len(subset),
            "n_objective": len(objective),
            "n_parseable_objective": len(parseable),
            "n_manual_review_objective": len(objective) - len(parseable),
            "parse_rate_objective": len(parseable) / len(objective) if objective else "",
            "correct_parseable_objective": len(correct),
            "accuracy_parseable_objective": len(correct) / len(parseable) if parseable else "",
            "accuracy_lower_bound_manual_review_wrong": len(correct) / len(objective) if objective else "",
            "mean_generation_time_sec": statistics.mean(gen_times) if gen_times else "",
            "sd_generation_time_sec": statistics.stdev(gen_times) if len(gen_times) > 1 else 0,
        })
    return rows


def write_report(path, summary_rows, reranker_status, mode, pilot_n, configs):
    lines = [
        "# RAG Sensitivity Report",
        "",
        "This experiment evaluates whether modestly stronger RAG retrieval settings change the original RAG baseline conclusion.",
        "",
        "No model training, manuscript editing, McNemar recalculation, or short-answer expert scoring was performed.",
        "",
        "## Fixed Components",
        "",
        f"- Embedding model: `{HISTORICAL_EMBEDDING}`",
        "- Chunking: chunk_size=500, overlap=50",
        "- Generator: Qwen2.5-1.5B-Instruct",
        "- Temperature: 0.3",
        "- Knowledge base, prompts, decoding settings, and evaluation questions were held constant across tested RAG configurations.",
        f"- Question mode: `{mode}`",
        f"- Pilot size: `{pilot_n if pilot_n else 'full selected set'}`",
        "",
        "## Reranker",
        "",
        f"- Reranker status: `{reranker_status}`",
        "",
        "## Summary",
        "",
        "| config | top-k | reranker | n objective | parse rate | parseable accuracy | lower-bound accuracy |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        def fmt(x):
            if x == "":
                return ""
            if isinstance(x, float):
                return f"{x:.4f}"
            try:
                return f"{float(x):.4f}"
            except Exception:
                return str(x)
        lines.append(
            f"| {row['retrieval_configuration']} | {row['top_k']} | {row['reranker']} | {row['n_objective']} | "
            f"{fmt(row['parse_rate_objective'])} | {fmt(row['accuracy_parseable_objective'])} | "
            f"{fmt(row['accuracy_lower_bound_manual_review_wrong'])} |"
        )
    lines.extend([
        "",
        "## Interpretation Guardrails",
        "",
        "- Automatic scoring is used only for clearly parsed choice/judge responses.",
        "- Ambiguous objective responses are marked for manual review rather than forced into an answer.",
        "- Short-answer responses are generated and retained when included, but are not automatically expert-scored.",
        "- Because no gold source-document labels are available, Recall@k/Hit@k is not reported.",
        "- `RAG_RETRIEVAL_SAMPLE.csv` provides a fixed sample for later human relevance labeling.",
        "",
        "## Reviewer Questions",
        "",
        "1. top3 vs top5 results are provided in `RAG_SENSITIVITY_SUMMARY.csv`.",
        "2. Reranker completion status is stated above.",
        "3. Whether stronger RAG changes the original conclusion should be judged from the summary accuracy and manual-review burden.",
        "4. Claims should be phrased as MER outperforming the tested RAG configurations only if the tested RAG results remain below MER.",
        "5. Retrieval noise evidence should rely on retrieved chunks and manual-review flags, not invented source-label recall.",
        "6. The RAG baseline criticism is empirically strengthened to the extent that top-k sensitivity and reranker feasibility are documented.",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--questions-json", required=True)
    parser.add_argument("--output-dir", default="04_rag_experiment")
    parser.add_argument("--db-dir", default="04_rag_experiment/chroma_db")
    parser.add_argument("--generator", default=DEFAULT_GENERATOR)
    parser.add_argument("--mode", choices=["objective", "all"], default="objective")
    parser.add_argument("--pilot-n", type=int, default=0)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--embedding-device", default="cpu")
    parser.add_argument("--force-rebuild-db", action="store_true")
    parser.add_argument("--reranker", default="")
    args = parser.parse_args()

    random.seed(SEED)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    db, n_docs, n_chunks = build_or_load_db(args.source_dir, args.db_dir, args.force_rebuild_db, args.embedding_device)
    questions = load_questions(args.questions_json, args.mode, args.pilot_n)
    tokenizer, model, device = load_generator(args.generator)
    reranker, reranker_status = load_reranker(args.reranker)

    configs = [
        {"name": "RAG-A_top3_no_reranker", "top_k": 3, "reranker": None, "reranker_name": "none"},
        {"name": "RAG-B_top5_no_reranker", "top_k": 5, "reranker": None, "reranker_name": "none"},
    ]
    if reranker is not None:
        configs.append({"name": "RAG-C_top5_reranker", "top_k": 5, "reranker": reranker, "reranker_name": args.reranker})

    config_payload = {
        "seed": SEED,
        "source_dir": str(args.source_dir),
        "questions_json": str(args.questions_json),
        "db_dir": str(args.db_dir),
        "generator": args.generator,
        "embedding_model": HISTORICAL_EMBEDDING,
        "chunk_size": 500,
        "chunk_overlap": 50,
        "temperature": args.temperature,
        "max_new_tokens": args.max_new_tokens,
        "mode": args.mode,
        "pilot_n": args.pilot_n,
        "n_questions": len(questions),
        "n_loaded_docs_when_rebuilt": n_docs,
        "n_chunks_when_rebuilt": n_chunks,
        "device": device,
        "torch_version": torch.__version__,
        "platform": platform.platform(),
        "nvidia_smi": run_cmd(["nvidia-smi"]),
        "reranker_status": reranker_status,
        "configs": configs,
    }
    config_payload["configs"] = [
        {k: v for k, v in cfg.items() if k != "reranker"} for cfg in configs
    ]
    (out / "RAG_CONFIGS.json").write_text(json.dumps(config_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    raw_rows = []
    retrieval_rows = []
    sample_candidates = []
    for cfg in configs:
        for idx, item in enumerate(questions, 1):
            query = normalize_question_text(item["question"])
            retrieved = retrieve(db, query, cfg["top_k"], cfg["reranker"])
            prompt = make_prompt(item["question"], retrieved)
            response, generated_tokens, gen_time = generate(
                tokenizer, model, device, prompt, args.max_new_tokens, args.temperature
            )
            parsed, flag = parse_answer(item["question_type"], response)
            is_correct = ""
            if flag == "parsed" and item["question_type"] in {"choice", "judge"}:
                is_correct = "1" if parsed == str(item["standard_answer"]).strip() else "0"

            row = {
                "question_id": item["question_id"],
                "question_type": item["question_type"],
                "retrieval_configuration": cfg["name"],
                "top_k": cfg["top_k"],
                "reranker": cfg["reranker_name"],
                "question": item["question"],
                "standard_answer": item["standard_answer"],
                "search_query": query,
                "retrieved_chunk_ids": " || ".join(r["chunk_id"] for r in retrieved),
                "retrieval_scores": " || ".join(str(r["retrieval_score"]) for r in retrieved),
                "rerank_scores": " || ".join(str(r["rerank_score"]) for r in retrieved),
                "retrieved_texts": "\n---CHUNK---\n".join(r["text"] for r in retrieved),
                "generated_response": response,
                "final_parsed_answer": parsed,
                "ambiguity_flag": flag,
                "is_correct": is_correct,
                "generated_tokens": generated_tokens,
                "generation_time_sec": gen_time,
            }
            raw_rows.append(row)
            for r in retrieved:
                retrieval_rows.append({
                    "question_id": item["question_id"],
                    "question_type": item["question_type"],
                    "retrieval_configuration": cfg["name"],
                    "rank_pre": r["rank_pre"],
                    "chunk_id": r["chunk_id"],
                    "source": r["source"],
                    "retrieval_score": r["retrieval_score"],
                    "rerank_score": r["rerank_score"],
                    "chunk_text": r["text"],
                })
            if cfg["name"] == configs[0]["name"]:
                sample_candidates.append((item, retrieved))
            if idx % 25 == 0:
                print(f"{cfg['name']}: {idx}/{len(questions)} done", flush=True)

    write_csv(out / "RAG_SENSITIVITY_RAW.csv", raw_rows)
    write_csv(out / "RAG_RETRIEVAL_ALL.csv", retrieval_rows)
    summary_rows = summarize(raw_rows, configs)
    write_csv(out / "RAG_SENSITIVITY_SUMMARY.csv", summary_rows)

    rng = random.Random(SEED)
    sample = rng.sample(sample_candidates, min(100, len(sample_candidates)))
    sample_rows = []
    for item, retrieved in sample:
        for r in retrieved:
            sample_rows.append({
                "question_id": item["question_id"],
                "question_type": item["question_type"],
                "question": item["question"],
                "chunk_id": r["chunk_id"],
                "source": r["source"],
                "retrieval_score": r["retrieval_score"],
                "chunk_text": r["text"],
                "human_relevance_label": "",
                "notes": "",
            })
    write_csv(out / "RAG_RETRIEVAL_SAMPLE.csv", sample_rows)
    write_report(out / "RAG_SENSITIVITY_REPORT.md", summary_rows, reranker_status, args.mode, args.pilot_n, configs)
    print(f"Done. Outputs written to {out}")


if __name__ == "__main__":
    main()
