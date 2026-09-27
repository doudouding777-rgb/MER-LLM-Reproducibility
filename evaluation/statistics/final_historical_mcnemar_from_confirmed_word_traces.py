#!/usr/bin/env python3
"""Compute final historical McNemar from confirmed human-marked Word traces.

Inputs:
- Base answers: structured historical PDF-text traces that already reproduced
  the Excel Base total.
- MER answers: author-confirmed historical Word scoring traces:
  red/green/yellow marks denote wrong answers; unmarked objective items are
  treated as correct.

No free-text semantic answer parsing is used.
"""

from __future__ import annotations

import csv
import json
import math
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TXT = ROOT / "02_question_audit/intermediate/pdf_text"
OUT = ROOT / "03_statistics/results"
REP = ROOT / "03_statistics/reports"
STANDARD_JSON = ROOT / "00_original_evidence/07_evaluation_question_banks/Set 1+Set 2/standard_answers.json"

BASE_SET1 = TXT / "assessment_question_bank_zip_Assessment_Question_Bank_Qwen2.5-1.5B-Instruct_30k_samples_4_epochs_Qwen2.5-1.5B-Instruct_30k_samples_4_epochs_Answers_for_the_Set_1_of_Questions_Before_Fine-tung.pdf.txt"
BASE_SET2 = TXT / "assessment_question_bank_zip_Assessment_Question_Bank_Qwen2.5-1.5B-Instruct_30k_samples_4_epochs_Qwen2.5-1.5B-Instruct_30k_samples_4_epochs_Answers_for_the_Set_2_of_Questions_Before_Fine-tung.pdf.txt"

MER_SET1_DOCX = ROOT / "00_original_evidence/07_evaluation_question_banks/6、处理完的数据/测试题的答案/Qwen2.5-1.5B-Instruct - 2万条数据---跑了4轮/Qwen2.5-1.5B-Instruct-2万条数据微调后模型选择题.docx"
MER_SET2_DOCX = ROOT / "00_original_evidence/07_evaluation_question_banks/6、处理完的数据/测试题的答案/Qwen2.5-1.5B-Instruct - 2万条数据---跑了4轮/2万条跑了4轮   新题微调后模型结果(1).docx"

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").replace("\f", "\n")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize_tf(s: str) -> str:
    s = s.strip().lower()
    if s in {"true", "correct", "t", "yes", "正确", "对", "√"}:
        return "T"
    if s in {"false", "incorrect", "f", "no", "错误", "错", "×"}:
        return "F"
    return s.upper()


def references() -> tuple[list[set[str]], list[set[str]], list[set[str]]]:
    data = json.loads(STANDARD_JSON.read_text(encoding="utf-8"))
    choices = [x for x in data if x["type"] == "choice"]
    judges = [x for x in data if x["type"] == "judge"]
    set1 = [{str(x["answer"]).strip().upper()} for x in choices[:550]]
    set2_choice = [{str(x["answer"]).strip().upper()} for x in choices[550:850]]
    set2_judge = [{normalize_tf(str(x["answer"]).strip())} for x in judges[:250]]
    assert len(set1) == 550 and len(set2_choice) == 300 and len(set2_judge) == 250
    return set1, set2_choice, set2_judge


def parse_numbered_choice_answers(text: str, expected: int) -> list[str]:
    answers: list[str] = []
    for line in text.splitlines():
        raw_line = line
        line = line.strip()
        m = re.match(r"^\d+\.\s*(?:\*\*Answer\*\*:|Answer:)\s*([A-D])(?:\b|[.．、:：*\-])", line, flags=re.I)
        if m:
            answers.append(m.group(1).upper())
            continue
        m = re.match(r"^\d+\.\s*(?:\*\*)?\s*([A-D])(?:\b|[.．、:：*\-])", line, flags=re.I)
        if m:
            answers.append(m.group(1).upper())
            continue
        m = re.match(r"^\s{2,}([A-D])\.\s+", raw_line, flags=re.I)
        if m:
            answers.append(m.group(1).upper())
            continue
        m = re.match(r"^\d+\s*-\s*\d+\s*:?\s*([A-D（）()\s]+)", line, flags=re.I)
        if m:
            lhs = re.split(r"[（(]", m.group(1))[0]
            answers.extend([x.upper() for x in re.findall(r"[A-D]", lhs, flags=re.I)])
    return answers[:expected]


def parse_base_set2(path: Path) -> tuple[list[str], list[str]]:
    text = read(path)
    lower = text.lower()
    cut_candidates = [i for i in [lower.find("true/false"), lower.find("true or false")] if i >= 0]
    cut = min(cut_candidates) if cut_candidates else len(text)
    choice = parse_numbered_choice_answers(text[:cut], 300)
    judge: list[str] = []
    for line in text[cut:].splitlines():
        line = line.strip()
        m = re.match(r"^\d+\.\s*(?:\*\*)?\s*(True|False|Correct|Incorrect)", line, flags=re.I)
        if m:
            judge.append(normalize_tf(m.group(1)))
            continue
        m = re.match(r"^\d+\.\s*([√×])", line)
        if m:
            judge.append(normalize_tf(m.group(1)))
    return choice[:300], judge[:250]


def docx_paragraphs(path: Path) -> list[tuple[int, str, list[tuple[str, bool]]]]:
    root = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    rows = []
    for pi, para in enumerate(root.findall(".//w:p", NS)):
        pieces = []
        for run in para.findall(".//w:r", NS):
            text = "".join(t.text or "" for t in run.findall(".//w:t", NS))
            if not text:
                continue
            marked = False
            rpr = run.find("w:rPr", NS)
            if rpr is not None:
                for tag, attr in [("highlight", "val"), ("color", "val"), ("shd", "fill")]:
                    el = rpr.find("w:" + tag, NS)
                    if el is not None:
                        val = el.attrib.get(f"{{{NS['w']}}}{attr}", "") or el.attrib.get(f"{{{NS['w']}}}val", "")
                        if val and val not in {"auto", "none"}:
                            marked = True
            pieces.append((text, marked))
        full = "".join(x[0] for x in pieces).strip()
        if full:
            rows.append((pi, full, pieces))
    return rows


def mer_set1_from_docx() -> tuple[list[str], list[int]]:
    answers: list[str] = []
    correct: list[int] = []
    for _pi, text, pieces in docx_paragraphs(MER_SET1_DOCX):
        m = re.match(r"^(\d+)\s*-\s*(\d+)\s*:\s*([^（(]+)", text)
        if not m:
            continue
        ans = re.findall(r"[A-D]", m.group(3).upper())
        marked_letters = []
        for run_text, marked in pieces:
            for ch in run_text:
                if ch in "（(":
                    break
                if ch.upper() in "ABCD":
                    marked_letters.append(marked)
        marked_letters = marked_letters[-len(ans):]
        for a, is_wrong in zip(ans, marked_letters):
            answers.append(a)
            correct.append(0 if is_wrong else 1)
    assert len(answers) == 550
    return answers, correct


def mer_set2_from_docx() -> tuple[list[str], list[int], list[str], list[int]]:
    section = ""
    choice_answers: list[str] = []
    choice_correct: list[int] = []
    judge_answers: list[str] = []
    judge_correct: list[int] = []
    for _pi, text, pieces in docx_paragraphs(MER_SET2_DOCX):
        if text == "单选题":
            section = "choice"
            continue
        if text == "多选题":
            section = "multi"
            continue
        if text == "判断题":
            section = "judge"
            continue
        if text == "简答题":
            section = "short"
            continue
        is_wrong = any(marked for _txt, marked in pieces)
        if section == "choice":
            m = re.match(r"^\d+\.\s*(?:\*\*)?\s*([A-D])", text, flags=re.I)
            if m:
                choice_answers.append(m.group(1).upper())
                choice_correct.append(0 if is_wrong else 1)
        elif section == "judge":
            if re.match(r"^\d+\.\s*", text) and re.search(r"(正确|错误|对|错|√|×|Correct|Incorrect|True|False)", text, re.I):
                m = re.search(r"(正确|错误|对|错|√|×|Correct|Incorrect|True|False)", text, re.I)
                judge_answers.append(normalize_tf(m.group(1)))
                judge_correct.append(0 if is_wrong else 1)
    assert len(choice_answers) == 300
    assert len(judge_answers) == 250
    return choice_answers, choice_correct, judge_answers, judge_correct


def exact_binomial_two_sided(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) * (0.5 ** n) for i in range(k + 1))
    return min(1.0, 2 * p)


def main() -> None:
    set1_ref, set2_choice_ref, set2_judge_ref = references()
    base_set1 = parse_numbered_choice_answers(read(BASE_SET1), 550)
    base_set2_choice, base_set2_judge = parse_base_set2(BASE_SET2)
    mer_set1_ans, mer_set1_correct = mer_set1_from_docx()
    mer_set2_choice_ans, mer_set2_choice_correct, mer_set2_judge_ans, mer_set2_judge_correct = mer_set2_from_docx()

    base_set1_correct = [1 if a in ref else 0 for a, ref in zip(base_set1, set1_ref)]
    base_set2_choice_correct = [1 if a in ref else 0 for a, ref in zip(base_set2_choice, set2_choice_ref)]
    base_set2_judge_correct = [1 if a in ref else 0 for a, ref in zip(base_set2_judge, set2_judge_ref)]

    components = [
        ("Base", "Set1", "choice", sum(base_set1_correct), 550, 428),
        ("Base", "Set2", "choice", sum(base_set2_choice_correct), 300, 186),
        ("Base", "Set2", "judge", sum(base_set2_judge_correct), 250, 206),
        ("MER", "Set1", "choice", sum(mer_set1_correct), 550, 442),
        ("MER", "Set2", "choice", sum(mer_set2_choice_correct), 300, 204),
        ("MER", "Set2", "judge", sum(mer_set2_judge_correct), 250, 219),
    ]
    validation = [{
        "model_state": model,
        "set": set_name,
        "question_type": qtype,
        "expected_correct_from_excel": expected,
        "expected_total": total,
        "recovered_correct": recovered,
        "recovered_total": total,
        "status": "pass" if recovered == expected else "fail",
    } for model, set_name, qtype, recovered, total, expected in components]
    if any(row["status"] != "pass" for row in validation):
        raise RuntimeError(f"Excel validation failed: {validation}")

    rows = []
    specs = [
        ("Set1", "choice", 1, base_set1, base_set1_correct, mer_set1_ans, mer_set1_correct, set1_ref),
        ("Set2", "choice", 551, base_set2_choice, base_set2_choice_correct, mer_set2_choice_ans, mer_set2_choice_correct, set2_choice_ref),
        ("Set2", "judge", 851, base_set2_judge, base_set2_judge_correct, mer_set2_judge_ans, mer_set2_judge_correct, set2_judge_ref),
    ]
    for set_name, qtype, start, b_ans, b_cor, m_ans, m_cor, refs in specs:
        for i in range(len(refs)):
            rows.append({
                "global_id": start + i,
                "set": set_name,
                "question_type": qtype,
                "local_id": i + 1,
                "standard_answer": "/".join(sorted(refs[i])),
                "base_answer": b_ans[i],
                "base_historical_correct": b_cor[i],
                "mer_answer": m_ans[i],
                "mer_historical_correct": m_cor[i],
                "base_source": str((BASE_SET1 if set_name == "Set1" else BASE_SET2).relative_to(ROOT)),
                "mer_source": str((MER_SET1_DOCX if set_name == "Set1" else MER_SET2_DOCX).relative_to(ROOT)),
                "recovery_method": "Base structured answer-vs-key; MER author-confirmed Word wrong-answer color marks",
            })

    b0m1 = sum(1 for r in rows if r["base_historical_correct"] == 0 and r["mer_historical_correct"] == 1)
    b1m0 = sum(1 for r in rows if r["base_historical_correct"] == 1 and r["mer_historical_correct"] == 0)
    both1 = sum(1 for r in rows if r["base_historical_correct"] == 1 and r["mer_historical_correct"] == 1)
    both0 = sum(1 for r in rows if r["base_historical_correct"] == 0 and r["mer_historical_correct"] == 0)
    disc = b0m1 + b1m0
    chi2 = ((abs(b0m1 - b1m0) - 1) ** 2 / disc) if disc else 0.0
    p_exact = exact_binomial_two_sided(b0m1, b1m0)

    write_csv(OUT / "HISTORICAL_OBJECTIVE_ITEM_LEVEL_TRACE.csv", rows, [
        "global_id", "set", "question_type", "local_id", "standard_answer",
        "base_answer", "base_historical_correct", "mer_answer", "mer_historical_correct",
        "base_source", "mer_source", "recovery_method",
    ])
    write_csv(OUT / "HISTORICAL_TRACE_VS_EXCEL_VALIDATION.csv", validation, [
        "model_state", "set", "question_type", "expected_correct_from_excel",
        "expected_total", "recovered_correct", "recovered_total", "status",
    ])
    write_csv(OUT / "FINAL_HISTORICAL_PAIRED_CORRECTNESS.csv", [{
        "global_id": r["global_id"],
        "set": r["set"],
        "question_type": r["question_type"],
        "base_correct": r["base_historical_correct"],
        "mer_correct": r["mer_historical_correct"],
    } for r in rows], ["global_id", "set", "question_type", "base_correct", "mer_correct"])
    write_csv(OUT / "FINAL_HISTORICAL_MCNEMAR.csv", [{
        "comparison": "MER vs Base, all 1100 objective items",
        "both_correct": both1,
        "base_wrong_mer_correct": b0m1,
        "base_correct_mer_wrong": b1m0,
        "both_wrong": both0,
        "discordant_total": disc,
        "mcnemar_chi2_continuity_corrected": chi2,
        "exact_binomial_two_sided_p": p_exact,
        "status": "computed_from_confirmed_historical_human_word_traces",
    }], [
        "comparison", "both_correct", "base_wrong_mer_correct", "base_correct_mer_wrong",
        "both_wrong", "discordant_total", "mcnemar_chi2_continuity_corrected",
        "exact_binomial_two_sided_p", "status",
    ])

    REP.mkdir(parents=True, exist_ok=True)
    report = f"""# Historical McNemar Evidence Closure Report

## Verdict

PASS: true historical item-level objective matrix was recovered and McNemar was computed.

## Source Policy

No model retraining, no rerun inference, and no free-text semantic parser was used.

Base correctness was recovered from the structured historical answer traces that reproduce Excel exactly. MER correctness was recovered from the two author-confirmed Word files whose red/green/yellow marks indicate wrong answers:

- `{MER_SET1_DOCX.relative_to(ROOT)}`
- `{MER_SET2_DOCX.relative_to(ROOT)}`

## Excel Validation

| Model | Set | Type | Excel | Recovered |
|---|---|---|---:|---:|
| Base | Set1 | choice | 428/550 | 428/550 |
| Base | Set2 | choice | 186/300 | 186/300 |
| Base | Set2 | judge | 206/250 | 206/250 |
| MER | Set1 | choice | 442/550 | 442/550 |
| MER | Set2 | choice | 204/300 | 204/300 |
| MER | Set2 | judge | 219/250 | 219/250 |

## McNemar

- Both correct: {both1}
- Base wrong, MER correct: {b0m1}
- Base correct, MER wrong: {b1m0}
- Both wrong: {both0}
- Discordant total: {disc}
- McNemar chi-square with continuity correction: {chi2:.6g}
- Exact binomial two-sided p-value: {p_exact:.6g}

## Outputs

- `03_statistics/results/HISTORICAL_OBJECTIVE_ITEM_LEVEL_TRACE.csv`
- `03_statistics/results/HISTORICAL_TRACE_VS_EXCEL_VALIDATION.csv`
- `03_statistics/results/FINAL_HISTORICAL_PAIRED_CORRECTNESS.csv`
- `03_statistics/results/FINAL_HISTORICAL_MCNEMAR.csv`
"""
    (REP / "HISTORICAL_MCNEMAR_EVIDENCE_CLOSURE_REPORT.md").write_text(report, encoding="utf-8")
    (REP / "OBJECTIVE_STATISTICS_FINAL_DECISION_V2.md").write_text(
        """# Objective Statistics Final Decision V2

The original module-level paired t-test should be removed. Historical item-level objective correctness has now been recovered from preserved human scoring traces and validated against the historical Excel ledger.

The objective-question comparison should report the historical manual accuracy results and the McNemar paired test computed from `FINAL_HISTORICAL_PAIRED_CORRECTNESS.csv`.

No automatic free-text rescoring result is used as model performance evidence.
""",
        encoding="utf-8",
    )
    print({"both_correct": both1, "base_wrong_mer_correct": b0m1, "base_correct_mer_wrong": b1m0, "both_wrong": both0, "p_exact": p_exact, "chi2": chi2})


if __name__ == "__main__":
    main()
