"""terms: extract terms and concepts from ingested files — stdlib only.

Pipeline step 2.

Method (documented): manual TF-IDF over the corpus.
  - Tokenize every document with the shared tokenizer.
  - df(term) = number of documents containing the term.
  - idf(term) = log(1 + (N - df + 0.5) / (df + 0.5))  (same as the BM25 idf)
  - score(term, doc) = tf(term, doc) * idf(term)
  - Per document: the top-N scored terms are that document's terms.
  - Global: terms ranked by their best document score.
Concepts: H1/H2 headings of each document are recorded as concept
candidates (a heading is the author's own label for the idea).

No external keyword library is used (``rank_bm25`` and ``yake`` are
not installed in this environment — see docs/DESIGN.md). TF-IDF by
hand is the zero-dependency alternative the research recommended.

Output:
  <data>/terms.json — {"per_doc": {raw_path: [{term, score, tf}, ...]},
                      "global": [{term, score}, ...],
                      "concepts": [{raw_path, heading, level}, ...]}
  <data>/terms.md   — the same, human-readable.

Usage:
  python3 -m wikimind terms --data DIR [--top-n 15]
"""

import argparse
import json
import math
import os
import re
import sys

from .tokenize import tokenize

HEADING_RE = re.compile(r"^(#{1,2})\s+(.*?)\s*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def extract_terms(manifest_records: list, top_n: int = 15) -> dict:
    docs = []  # (record, tokens, tf)
    df = {}
    for record in manifest_records:
        with open(record["abs_path"], encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        m = FRONTMATTER_RE.match(text)
        if m:
            text = text[m.end():]
        toks = tokenize(text)
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        for t in tf:
            df[t] = df.get(t, 0) + 1
        docs.append((record, toks, tf))

    n = len(docs)
    idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    per_doc = {}
    global_best = {}
    concepts = []
    for record, toks, tf in docs:
        scored = sorted(
            ((t, c * idf[t]) for t, c in tf.items()),
            key=lambda kv: -kv[1])[:top_n]
        per_doc[record["raw_path"]] = [
            {"term": t, "score": round(s, 3), "tf": tf[t]} for t, s in scored
        ]
        for t, s in scored:
            if t not in global_best or s > global_best[t]:
                global_best[t] = s
        with open(record["abs_path"], encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        m = FRONTMATTER_RE.match(text)
        if m:
            text = text[m.end():]
        for line in text.splitlines():
            hm = HEADING_RE.match(line)
            if hm:
                concepts.append({
                    "raw_path": record["raw_path"],
                    "heading": hm.group(2).strip(),
                    "level": len(hm.group(1)),
                })

    global_terms = sorted(
        ({"term": t, "score": round(s, 3)} for t, s in global_best.items()),
        key=lambda d: -d["score"])[:top_n * 4]
    return {"per_doc": per_doc, "global": global_terms, "concepts": concepts}


def render_md(terms: dict) -> str:
    lines = ["# Terms & Concepts (TF-IDF, stdlib only)", ""]
    lines.append("## Global top terms")
    lines.append("")
    for item in terms["global"]:
        lines.append(f"- **{item['term']}** — {item['score']}")
    lines.append("")
    lines.append("## Per-document top terms")
    lines.append("")
    for path, items in sorted(terms["per_doc"].items()):
        tops = ", ".join(f"{i['term']} ({i['score']})" for i in items[:8])
        lines.append(f"- `{path}`: {tops}")
    lines.append("")
    lines.append("## Concept headings (H1/H2)")
    lines.append("")
    for c in terms["concepts"]:
        lines.append(f"- {'#' * c['level']} {c['heading']} — `{c['raw_path']}`")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Extract terms (TF-IDF) + concepts (headings).")
    ap.add_argument("--data", required=True, help="data directory (manifest lives here)")
    ap.add_argument("--top-n", type=int, default=15)
    args = ap.parse_args(argv)
    with open(os.path.join(args.data, "manifest.jsonl"), encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh]
    terms = extract_terms(records, args.top_n)
    with open(os.path.join(args.data, "terms.json"), "w", encoding="utf-8") as fh:
        json.dump(terms, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(args.data, "terms.md"), "w", encoding="utf-8") as fh:
        fh.write(render_md(terms))
    print(f"docs={len(records)} global_terms={len(terms['global'])} "
          f"concepts={len(terms['concepts'])} -> {args.data}/terms.json + terms.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
