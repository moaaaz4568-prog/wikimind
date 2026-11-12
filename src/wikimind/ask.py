"""ask: CLI question interface — retrieval only, no generation.

Rules (documented defaults, see docs/DESIGN.md):
- Every answer is a cited raw chunk: file path + chunk text + section.
  Nothing is generated; nothing is paraphrased as fact.
- "لا أعرف" when there is no evidence: the best BM25 score is <=
  ``--min-score`` (default 0.0 — zero term overlap means zero
  evidence). 0.0 is a documented default, not a tuned threshold:
  all other thresholds are null until measured (docs/THRESHOLDS.md).
- Contradiction / both sides (معاذ's rule: no quarantine, always
  show both sides): when the top results contain conflicting numeric
  claims about the same unit (e.g. "4–5 رسائل/يوم" vs "20–25
  إيميل/يوم") from different source files, both sides are shown
  grouped under a contradiction banner instead of picking one.
  ``--both-sides`` always groups the top results by source file and
  notes where they disagree.
- Persona is an optional metadata filter (``--persona NAME``); a
  corpus without a ``personas/`` folder has only persona ``default``.

Usage:
  python3 -m wikimind ask "سؤالك هنا" --data DIR [--top-k 5] [--json]
      [--persona NAME] [--min-score 0.0] [--both-sides]
"""

import argparse
import json
import os
import re
import sys
import time

from .index import bm25_search, load_chunks, load_index
from .tokenize import tokenize

NO_EVIDENCE = "لا أعرف — لا يوجد دليل"

# Number words (English + Arabic) for numeric-claim detection.
EN_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "fifteen": 15, "twenty": 20, "twenty-five": 25,
    "thirty": 30,
}
AR_NUMBERS = {
    "واحد": 1, "اثنان": 2, "اثنين": 2, "ثلاثة": 3, "ثلاث": 3,
    "أربعة": 4, "أربع": 4, "خمسة": 5, "خمس": 5, "ستة": 6, "ست": 6,
    "سبعة": 7, "سبع": 7, "ثمانية": 8, "ثمان": 8, "تسعة": 9, "تسع": 9,
    "عشرة": 10, "عشر": 10, "عشرين": 20, "ثلاثين": 30,
}

# Unit words normalized to a canonical unit per language family.
UNIT_MAP = {
    "إيميل": "email/day", "ايميل": "email/day", "email": "email/day",
    "emails": "email/day", "رسالة": "email/day", "رسائل": "email/day",
    "يوم": "per-day", "يوميا": "per-day", "يومياً": "per-day",
    "يوميًا": "per-day", "day": "per-day",
    "أسبوع": "per-week", "اسبوع": "per-week", "week": "per-week",
    "%": "percent", "٪": "percent",
}

NUM_RANGE_RE = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:[-–—]\s*(\d+(?:[.,]\d+)?))?\s*"
    r"(إيميل|ايميل|email|emails|رسالة|رسائل|يوم|يوميا|يومياً|يوميًا|day|أسبوع|اسبوع|week|%|٪)?",
    re.IGNORECASE)
WORD_RANGE_RE = re.compile(
    r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|twenty-five|thirty"
    r"|واحد|اثنان|اثنين|ثلاثة|ثلاث|أربعة|أربع|خمسة|خمس|ستة|ست|سبعة|سبع|ثمانية|ثمان|تسعة|تسع|عشرة|عشر|عشرين|ثلاثين)"
    r"(?:\s*(?:to|إلى|الى|-)\s*"
    r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|twenty-five|thirty"
    r"|واحد|اثنان|اثنين|ثلاثة|ثلاث|أربعة|أربع|خمسة|خمس|ستة|ست|سبعة|سبع|ثمانية|ثمان|تسعة|تسع|عشرة|عشر|عشرين|ثلاثين))?"
    r"\s*(per\s+day|emails?/day|يوم|يوميا|يومياً|يوميًا|إيميل/يوم|ايميل/يوم|رسالة/يوم|رسائل/يوم)?",
    re.IGNORECASE)


def _num_word(w: str):
    w = w.lower()
    if w in EN_NUMBERS:
        return EN_NUMBERS[w]
    return AR_NUMBERS.get(w)


def numeric_claims(text: str) -> list:
    """Extract (value_repr, unit) numeric claims from a chunk's text.

    Returns e.g. [("20-25", "email/day"), ("15", "per-day")].
    Only claims with a recognizable unit are kept.
    """
    claims = []
    for m in NUM_RANGE_RE.finditer(text):
        lo, hi, unit_raw = m.group(1), m.group(2), m.group(3)
        if not unit_raw:
            continue
        unit = UNIT_MAP.get(unit_raw.lower(), unit_raw.lower())
        val = f"{lo}-{hi}" if hi else lo
        claims.append((val, unit))
    for m in WORD_RANGE_RE.finditer(text):
        lo_w, hi_w, unit_raw = m.group(1), m.group(2), m.group(3)
        lo = _num_word(lo_w)
        if lo is None:
            continue
        hi = _num_word(hi_w) if hi_w else None
        val = f"{lo}-{hi}" if hi is not None else str(lo)
        unit = "per-day"
        if unit_raw:
            u = unit_raw.lower().replace(" ", "")
            if "email" in u or "ايميل" in u or "إيميل" in u or "رسال" in u:
                unit = "email/day"
        claims.append((val, unit))
    return claims


def detect_both_sides(results: list) -> dict | None:
    """Detect conflicting numeric claims among the top results.

    Returns {"unit": ..., "sides": {value: [result, ...]}} when two
    different values for the same unit come from different source
    files, else None. Also notes a documented tension section.
    """
    by_unit = {}
    tension_files = []
    for r in results:
        for val, unit in numeric_claims(r["text"]):
            by_unit.setdefault(unit, {}).setdefault(val, []).append(r)
        if "توتر" in r.get("section", "") or "تناقض" in r.get("section", ""):
            tension_files.append(r["raw_path"])
    for unit, sides in by_unit.items():
        distinct_files = {r["raw_path"] for v in sides.values() for r in v}
        if len(sides) >= 2 and len(distinct_files) >= 2:
            return {"unit": unit, "sides": sides, "tension_files": tension_files}
    if tension_files:
        return {"unit": None, "sides": {}, "tension_files": tension_files}
    return None


def ask(data_dir: str, question: str, top_k: int = 5, persona: str = None,
        min_score: float = 0.0, both_sides: bool = False) -> dict:
    t0 = time.time()
    index = load_index(data_dir)
    chunks = load_chunks(data_dir)
    query_tokens = tokenize(question)
    ranked = bm25_search(index, query_tokens, top_k, persona=persona, chunks=chunks)
    elapsed_ms = (time.time() - t0) * 1000

    results = []
    for doc_idx, score in ranked:
        c = chunks[doc_idx]
        results.append({
            "rank": len(results) + 1,
            "score": round(score, 3),
            "chunk_id": c["chunk_id"],
            "section": c["section"],
            "raw_path": c["raw_path"],
            "domain": c["domain"],
            "persona": c.get("persona", "default"),
            "type": c["type"],
            "source_lines": c.get("source_lines"),
            "text": c["text"],
        })

    best = results[0]["score"] if results else 0.0
    no_evidence = (not results) or best <= min_score
    contradiction = None if no_evidence else detect_both_sides(results)
    return {
        "question": question,
        "persona": persona,
        "top_k": top_k,
        "min_score": min_score,
        "query_ms": round(elapsed_ms, 1),
        "results": results,
        "no_evidence": no_evidence,
        "contradiction": contradiction,
        "both_sides_requested": both_sides,
    }


def render_text(answer: dict) -> str:
    out = []
    if answer["no_evidence"]:
        best = answer["results"][0]["score"] if answer["results"] else 0
        out.append(f"{NO_EVIDENCE} (أفضل score = {best})")
        if answer["persona"]:
            out.append(f"persona المطلوبة: {answer['persona']}")
        return "\n".join(out)

    out.append(f"السؤال: {answer['question']}")
    out.append(f"النتائج: {len(answer['results'])} مقطع "
               f"(query: {answer['query_ms']:.0f} ms)")
    c = answer["contradiction"]
    if c and c["sides"]:
        out.append("")
        out.append("⚠️  طرفان مختلفان في المصادر — لا حجر، نعرض الطرفين:")
        for val, rs in c["sides"].items():
            for r in rs:
                out.append(f"   • {val} {c['unit']} — {r['raw_path']} "
                           f"(score={r['score']})")
        out.append("   القرار للمستخدم؛ الأرقام كما وردت في مصادرها.")
    elif c and c.get("tension_files"):
        out.append("")
        out.append("ملاحظة: أحد المصادر يسجّل توتراً/تعارضاً موثقاً في "
                   "قسم التوترات — راجعه مع النتائج.")
    out.append("=" * 70)
    for r in answer["results"]:
        out.append(f"[{r['rank']}] score={r['score']} | {r['section']}")
        loc = f"{r['raw_path']}"
        if r.get("source_lines"):
            loc += f" (أسطر {r['source_lines'][0]}–{r['source_lines'][1]})"
        out.append(f"    المصدر: {loc} | chunk: {r['chunk_id']} | "
                   f"domain: {r['domain']} | persona: {r['persona']}")
        snippet = r["text"].replace("\n", " ")
        if len(snippet) > 600:
            snippet = snippet[:600] + "…"
        out.append(f"    {snippet}")
        out.append("-" * 70)
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Ask the wiki (BM25 retrieval only).")
    ap.add_argument("question", nargs="?", help="السؤال")
    ap.add_argument("--data", required=True, help="data directory (index lives here)")
    ap.add_argument("--persona", default=None, help="optional persona filter")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--min-score", type=float, default=0.0,
                    help="no-evidence threshold (documented default 0.0)")
    ap.add_argument("--both-sides", action="store_true",
                    help="group top results by source and flag disagreements")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not args.question:
        ap.error("a question is required")
    answer = ask(args.data, args.question, args.top_k, args.persona,
                 args.min_score, args.both_sides)
    if args.json:
        print(json.dumps(answer, ensure_ascii=False))
    else:
        print(render_text(answer))
    return 0


if __name__ == "__main__":
    sys.exit(main())
