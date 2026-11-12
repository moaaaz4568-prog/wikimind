"""index: pure-Python BM25 index over chunks — standard library only.

Scoring: BM25, k1=1.5, b=0.75 (documented defaults; stored in the
index file so ask/eval reuse the exact parameters that built it).
Indexed text per chunk = section breadcrumb + " " + chunk text, so a
verbatim section-title query still matches.

Generic-term guard (documented rule): a query term that occurs in
more than half of all chunks carries no evidence — it is ignored, so
a query made only of generic words scores 0 and triggers "لا أعرف".

On-disk state: <data>/index.json
  {params, N, avgdl, doc_len[], idf{term: float},
   postings{term: {doc_idx: tf}}}
<data>/chunks.jsonl remains the store of full chunk text + metadata.

Usage:
  python3 -m wikimind index --data DIR
"""

import argparse
import json
import math
import os
import sys

from .tokenize import tokenize

K1 = 1.5
B = 0.75


def index_text(chunk: dict) -> str:
    return f"{chunk.get('section', '')} {chunk.get('text', '')}"


def build_index(chunks: list) -> dict:
    n = len(chunks)
    doc_len = []
    postings = {}
    for doc_idx, chunk in enumerate(chunks):
        toks = tokenize(index_text(chunk))
        doc_len.append(len(toks))
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        for term, cnt in tf.items():
            postings.setdefault(term, {})[str(doc_idx)] = cnt
    avgdl = sum(doc_len) / n if n else 0.0
    idf = {}
    for term, docs in postings.items():
        df = len(docs)
        idf[term] = math.log(1 + (n - df + 0.5) / (df + 0.5))
    return {
        "params": {"k1": K1, "b": B, "model": "BM25 (pure Python, no external libs)",
                   "tokenizer": "arabic-normalized word tokens, stopwords removed"},
        "N": n,
        "avgdl": avgdl,
        "doc_len": doc_len,
        "idf": idf,
        "postings": postings,
    }


def save_index(index: dict, data_dir: str) -> str:
    path = os.path.join(data_dir, "index.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False)
    return path


def load_index(data_dir: str) -> dict:
    with open(os.path.join(data_dir, "index.json"), encoding="utf-8") as fh:
        return json.load(fh)


def load_chunks(data_dir: str) -> list:
    chunks = []
    with open(os.path.join(data_dir, "chunks.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            chunks.append(json.loads(line))
    return chunks


def bm25_search(index: dict, query_tokens: list, top_k: int,
                persona: str = None, chunks: list = None) -> list:
    """Return [(doc_idx, score), ...] ranked best-first.

    If ``persona`` is given, only chunks whose persona matches are
    returned (persona is an optional metadata filter).
    """
    k1 = index["params"]["k1"]
    b = index["params"]["b"]
    avgdl = index["avgdl"]
    doc_len = index["doc_len"]
    idf = index["idf"]
    postings = index["postings"]
    n = index["N"]
    scores = {}
    for term in set(query_tokens):
        if term not in postings:
            continue
        if len(postings[term]) > 0.5 * n:
            continue  # generic-term guard
        term_idf = idf[term]
        for doc_idx_s, tf in postings[term].items():
            doc_idx = int(doc_idx_s)
            if persona is not None and chunks is not None:
                if chunks[doc_idx].get("persona", "default") != persona:
                    continue
            dl = doc_len[doc_idx]
            denom = tf + k1 * (1 - b + b * dl / avgdl)
            scores[doc_idx] = scores.get(doc_idx, 0.0) + term_idf * tf * (k1 + 1) / denom
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    return ranked[:top_k]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build BM25 index (pure Python).")
    ap.add_argument("--data", required=True, help="data directory (chunks live here)")
    args = ap.parse_args(argv)
    chunks = load_chunks(args.data)
    index = build_index(chunks)
    path = save_index(index, args.data)
    print(f"N={index['N']} terms={len(index['idf'])} avgdl={index['avgdl']:.1f} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
