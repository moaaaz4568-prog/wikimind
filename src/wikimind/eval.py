"""eval: measure BM25 retrieval on a known-answer question set — stdlib only.

What this measures (and only this): retrieval. For each question, run
it through the same retrieval path as ``ask`` (``bm25_search`` over the
index in ``--data``) and check where the expected file lands:
rank-1 and top-3. Nothing else is scored here — no generation, no
citation wording, no "both sides" judgement. Those are NOT_RUN in
this module; citation quality is checked by reading ``ask`` output,
not by a number here.

Rules (documented defaults, binding decisions):
- The measurement is the only gate. There are no G0–G8 gates.
- Retrieval only: rank-1 rate and top-3 rate over the question set.
- A rank is counted only inside the searched window: the search runs
  with ``max(top_k, 3)`` results, so a file ranked deeper than that
  window is reported as absent ("غائب", rank null) — not as a deep
  rank. The window is part of the reported result (``top_k``).
- Expected file matching is by file basename: a chunk counts when
  ``basename(chunk["raw_path"]) == basename(expected_file)``. This
  makes the question set robust to the corpus being mounted under a
  different root directory.
- Per-type breakdowns (title / paragraph / paraphrase) are computed
  only when the question carries a ``type`` field; questions without
  it are counted in the totals but in no type bucket.
- Malformed entries (not an object, or missing ``question`` /
  ``expected_file``) are skipped and counted in ``skipped`` — they
  never silently become a zero or a pass.
- The old BM25 numbers (12/15 rank-1, 14/15 top-3 on Haitham's 210
  pages) are REPORTED from the original machine; the 15 question
  texts themselves were never saved (UNKNOWN), so this question set
  is new, saved in ``examples/eval-questions.json``, and must not be
  presented as a rerun of the old set.

Question file format (JSON): a list of objects, or an object with a
``"questions"`` key holding that list. Each question:
  {"question": "...", "expected_file": "CPT_...md",
   "type": "title" | "paragraph" | "paraphrase"}

Usage:
  python3 -m wikimind eval --data DIR --questions FILE [--top-k 5] [--out FILE]
      [--persona NAME] [--min-score 0.0]
  python3 -m wikimind.eval --data DIR --questions FILE [--top-k 5] [--out FILE]
      [--persona NAME] [--min-score 0.0]
Without --out the JSON report goes to stdout; with --out it is
written to the file and a one-line summary goes to stdout.
``--persona`` is the same optional metadata filter as in ``ask``:
only chunks of that persona are retrieved. ``--min-score`` is the
same no-evidence threshold as in ``ask`` (default 0.0): a chunk only
counts toward the rank when its score is above it, so a best score
at or below the threshold makes the question absent — the same
"لا أعرف" basis ask uses.
"""

import argparse
import json
import os
import sys

from .index import bm25_search, load_chunks, load_index
from .tokenize import tokenize


def load_questions(path: str) -> list:
    """Load a question file: a JSON list, or {"questions": [...]}."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        data = data.get("questions", [])
    if not isinstance(data, list):
        raise ValueError("questions file must be a JSON list "
                         "or an object with a 'questions' list")
    return data


def _rate(count: int, total: int) -> float:
    return round(count / total, 3) if total else 0.0


def evaluate(data_dir: str, questions: list, top_k: int = 5,
             persona: str = None, min_score: float = 0.0) -> dict:
    """Run every question through bm25_search and score rank-1 / top-3.

    Returns a report dict:
      {data_dir, top_k, persona, min_score, n_questions, skipped,
       rank_1: {count, rate}, top_3: {count, rate}, absent: count,
       by_type: {type: {n, rank_1, rank_1_rate, top_3, top_3_rate}},
       results: [{question, expected_file, type, rank (int or None),
                  in_top_3, top_1_file, top_3_files}]}
    ``rank`` is None (absent) when no chunk of the expected file is
    inside the searched window, or when its best score is at or below
    ``min_score`` (the no-evidence rule ask uses for "لا أعرف").
    ``top_3_files`` still lists what BM25 returned, for diagnosis.
    """
    index = load_index(data_dir)
    chunks = load_chunks(data_dir)
    search_k = max(top_k, 3)

    results = []
    rank1_count = top3_count = skipped = 0
    by_type = {}
    for entry in questions:
        if not isinstance(entry, dict) or not entry.get("question") \
                or not entry.get("expected_file"):
            skipped += 1
            continue
        text = entry["question"]
        expected = os.path.basename(entry["expected_file"])
        qtype = entry.get("type")
        ranked = bm25_search(index, tokenize(text), search_k,
                             persona=persona, chunks=chunks)
        top_3_files = [os.path.basename(chunks[i]["raw_path"])
                       for i, _ in ranked[:3]]
        rank = None
        for pos, (doc_idx, score) in enumerate(ranked, start=1):
            if score <= min_score:
                continue
            if os.path.basename(chunks[doc_idx]["raw_path"]) == expected:
                rank = pos
                break
        is_rank1 = rank == 1
        is_top3 = rank is not None and rank <= 3
        rank1_count += 1 if is_rank1 else 0
        top3_count += 1 if is_top3 else 0
        if qtype:
            bucket = by_type.setdefault(qtype, {"n": 0, "rank_1": 0, "top_3": 0})
            bucket["n"] += 1
            bucket["rank_1"] += 1 if is_rank1 else 0
            bucket["top_3"] += 1 if is_top3 else 0
        results.append({
            "question": text,
            "expected_file": entry["expected_file"],
            "type": qtype,
            "rank": rank,
            "in_top_3": is_top3,
            "top_1_file": top_3_files[0] if top_3_files else None,
            "top_3_files": top_3_files,
        })

    n = len(results)
    by_type_out = {}
    for qtype, b in sorted(by_type.items()):
        by_type_out[qtype] = {
            "n": b["n"],
            "rank_1": b["rank_1"],
            "rank_1_rate": _rate(b["rank_1"], b["n"]),
            "top_3": b["top_3"],
            "top_3_rate": _rate(b["top_3"], b["n"]),
        }
    return {
        "data_dir": data_dir,
        "top_k": top_k,
        "persona": persona,
        "min_score": min_score,
        "n_questions": n,
        "skipped": skipped,
        "rank_1": {"count": rank1_count, "rate": _rate(rank1_count, n)},
        "top_3": {"count": top3_count, "rate": _rate(top3_count, n)},
        "absent": n - top3_count,
        "by_type": by_type_out,
        "results": results,
    }


def report_to_json(report: dict) -> str:
    """Serialize a report dict to indented JSON (UTF-8, Arabic kept)."""
    return json.dumps(report, ensure_ascii=False, indent=2)


def format_summary(report: dict) -> str:
    r1 = report["rank_1"]
    t3 = report["top_3"]
    return (f"n={report['n_questions']} rank-1={r1['count']} ({r1['rate']:.3f}) "
            f"top-3={t3['count']} ({t3['rate']:.3f}) "
            f"absent={report['absent']} skipped={report['skipped']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Evaluate BM25 retrieval on a known-answer question set.")
    ap.add_argument("--data", required=True,
                    help="data directory (index + chunks live here)")
    ap.add_argument("--questions", required=True,
                    help="JSON question file (see module docstring)")
    ap.add_argument("--top-k", type=int, default=5,
                    help="retrieval window; rank is only counted inside it")
    ap.add_argument("--persona", default=None,
                    help="optional persona filter, as in ask")
    ap.add_argument("--min-score", type=float, default=0.0,
                    help="no-evidence threshold, as in ask (default 0.0)")
    ap.add_argument("--out", default=None,
                    help="write the JSON report to this file instead of stdout")
    args = ap.parse_args(argv)
    try:
        questions = load_questions(args.questions)
        report = evaluate(args.data, questions, args.top_k,
                          persona=args.persona, min_score=args.min_score)
    except (OSError, ValueError, KeyError) as exc:
        print(f"eval: error: {exc}", file=sys.stderr)
        return 2
    text = report_to_json(report)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"{format_summary(report)} -> {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
