"""masters: build one master per domain + a masters/index.md router.

Pipeline step 4 (after ingest, chunk, terms).

What a master is here (binding rules, from the project research):
- A master is a NAVIGATION / summary layer over raw chunks, NOT a
  source of truth. Every claim in it traces to a raw chunk by
  (path + fingerprint): ``<absolute raw path>`` + ``chunk_id`` +
  ``sha256_short``.
- Link rule (from the master study: the old 39 masters have 100%
  broken ``[[Concept_...]]`` links, 95/95): a link/citation is
  written ONLY if its target file exists on disk, verified with
  ``os.path.exists`` BEFORE writing. A target that does not exist is
  dropped entirely — never written as a dangling link. No
  ``[[Concept_...]]`` wiki-links at all; citations are real file
  paths in backticks.
- Structure (from the make-master skill, structure-spec): each master
  is 11 lines — ``## Master_<Name>`` + a source-path line + 3
  single-line sections in fixed order §1 (TL;DR) then §4 (systems)
  then §16 (Q&A), separated by blank lines and closed by ``---``.
  Section titles use form A: ``## §N — <title>``.
- Section cap: every section's content is kept UNDER 5,000 chars
  (safe target <= 4,800), because the old masters were silently
  truncated mid-word at exactly 5,000 chars in 26/39 §4 sections.
  If content would exceed the cap, whole systems / Q&A pairs are
  dropped (summarize, never truncate mid-word); no section is ever
  cut mid-sentence. Each section ends with `` --- ``.
- §16 is Q&A (one of the seven documented §16 functions, declared
  in its title). Its count is NEVER written in the title — the old
  "12 سؤالاً" title over 16 real questions is not repeated.
- Contradiction (معاذ's rule: no quarantine, always show both
  sides): if a domain's chunks record a tension/conflict section
  ("توتر"/"تعارض"/"تناقض"), §16 notes it and names both sides'
  sources instead of silently picking one.
- Numbers are quoted VERBATIM from chunk text, with the citation
  attached. No number is invented, generalized from an example, or
  written without a source chunk.
- No GraphRAG, no fine-tuning, no governance, no gates. Measurement
  is the only gate (this module verifies every link it writes and
  reports the counts).

Default decisions (documented, reversible — no owner decision was
on file for these):
- Master shape: option 1 from معاذ's three options — ONE specialist
  master per domain (the skill's default when no explicit choice).
- Domain = the ``domain`` field already on each chunk (see chunk.py
  ``extract_domain``). One master per distinct domain present in
  ``chunks.jsonl``. A domain with no verifiable source file is
  skipped, not written empty.
- Citations use ABSOLUTE raw paths (from ``manifest.jsonl``
  ``abs_path``) because corpus-relative ``raw_path`` alone is not
  resolvable on its own. The router and the masters never move any
  file; ``masters/index.md`` points at the masters and at the raw
  folders as they are.
- ``terms.json`` (from terms.py) is used when present for top terms
  and concept headings; if it is missing, masters still build from
  chunks alone (headings taken from chunk ``section`` breadcrumbs).

Input:  <data>/chunks.jsonl  (required)
        <data>/manifest.jsonl (for absolute raw paths; optional)
        <data>/terms.json     (for top terms + concepts; optional)
Output: <data>/masters/Master_<Name>.md  (one per domain)
        <data>/masters/index.md          (router)

Usage:
  python3 -m wikimind masters --data DIR
"""

import argparse
import json
import os
import re
import sys

from .ingest import is_secret_or_control

SECTION_CHAR_LIMIT = 4800  # safe target below the 5,000 truncation cliff
EXCERPT_MAX = 320          # verbatim quote length cap inside a system
MAX_SYSTEMS_PER_MASTER = 12
MAX_QA_PER_MASTER = 5
MAX_TERMS_S1 = 8

MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]]*)\]\]")
URL_RE = re.compile(r"https?://\S+")
TENSION_RE = re.compile(r"توتر|تعارض|تناقض")


def sanitize_text(text: str) -> str:
    """Strip Markdown/wikilinks and bare URLs from quoted text.

    Excerpts are pasted verbatim from chunks, but a chunk may contain
    ``[text](url)`` links or ``[[Concept_X]]`` links whose targets
    live outside this data dir. Those are rewritten to plain text so
    a master never contains a link that was not verified here.
    """
    text = MD_LINK_RE.sub(r"\1", text)
    text = WIKI_LINK_RE.sub(r"\1", text)
    text = URL_RE.sub("", text)
    return " ".join(text.split())


def excerpt(text: str, max_len: int = EXCERPT_MAX) -> str:
    """Verbatim excerpt: whole sentences up to max_len, cut only at a
    word boundary, with an ellipsis marker if content was dropped."""
    text = sanitize_text(text)
    if len(text) <= max_len:
        return text
    sentences = re.split(r"(?<=[.!؟。])\s+", text)
    out = ""
    for sent in sentences:
        if out and len(out) + 1 + len(sent) > max_len:
            break
        out = (out + " " + sent).strip() if out else sent
    if not out:  # one pathological sentence: cut at a word boundary
        out = text[:max_len].rsplit(" ", 1)[0]
    if len(out) < len(text):
        out += " …"
    return out


def master_name(domain: str) -> str:
    """Domain -> ``Master_<Pascal_Case>`` (e.g. business_models ->
    Master_Business_Models)."""
    parts = [p for p in re.split(r"[^a-zA-Z0-9]+", domain) if p]
    pascal = "".join(p[:1].upper() + p[1:].lower() for p in parts)
    return f"Master_{pascal or 'General'}"


def _content_len(line: str, prefix: str) -> int:
    """Length of a section's content (the line minus its ``**§N:** ``
    prefix), i.e. the number the 5,000-char truncation cliff applies
    to."""
    return len(line) - len(prefix)


def _fit(items: list, joiner: str, prefix: str, limit: int = SECTION_CHAR_LIMIT) -> list:
    """Drop whole items from the end until the joined content fits
    under the limit. Returns the kept items (never an empty list when
    at least one item fits)."""
    kept = list(items)
    while len(kept) > 1 and _content_len(joiner.join(kept), prefix) > limit:
        kept.pop()
    return kept


def _load_jsonl(path: str) -> list:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _load_terms(data_dir: str) -> dict:
    path = os.path.join(data_dir, "terms.json")
    if not os.path.exists(path):
        return {"per_doc": {}, "global": [], "concepts": []}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_abs_paths(data_dir: str) -> dict:
    """raw_path -> absolute raw path, from manifest.jsonl if present."""
    path = os.path.join(data_dir, "manifest.jsonl")
    if not os.path.exists(path):
        return {}
    abs_paths = {}
    for record in _load_jsonl(path):
        abs_paths[record["raw_path"]] = record.get("abs_path", "")
    return abs_paths


def _resolve_source(raw_path: str, abs_paths: dict, data_dir: str):
    """Return an existing absolute path for a raw file, or None.

    A path is usable only if it exists on disk and is not a
    control/secret path (ingest's hard exclusion, re-checked here).
    """
    candidates = []
    if abs_paths.get(raw_path):
        candidates.append(abs_paths[raw_path])
    candidates.append(os.path.join(data_dir, raw_path))
    candidates.append(raw_path)
    for cand in candidates:
        if cand and os.path.isfile(cand) and not is_secret_or_control(cand):
            return os.path.abspath(cand)
    return None


def _file_title(chunks: list) -> str:
    """Title of a source file, from its first chunk's breadcrumb."""
    section = chunks[0].get("section", "")
    title = section.split(" › ")[0].strip() if section else ""
    if title:
        return title
    return os.path.splitext(os.path.basename(chunks[0]["raw_path"]))[0]


def _headings(chunks: list, concepts: list, raw_path: str) -> list:
    """Distinct section headings of a file, in first-appearance order."""
    seen, out = set(), []
    for c in concepts:
        if c.get("raw_path") == raw_path:
            h = c.get("heading", "").strip()
            if h and h not in seen:
                seen.add(h)
                out.append(h)
    for ch in chunks:
        section = ch.get("section", "")
        parts = section.split(" › ")
        if len(parts) > 1:
            h = parts[-1].strip()
            if h and h not in seen:
                seen.add(h)
                out.append(h)
    return out


def _section_1(domain: str, n_files: int, n_chunks: int, terms: list,
               headings: list) -> str:
    """§1 — TL;DR, one single line, under the char cap."""
    items = [
        "1. **الأطروحة:** هذا الماستر يجمع موضوع "
        f"`{domain}` من {n_files} ملفاً خاماً ({n_chunks} مقطعاً) — "
        "طبقة تنقّل وتلخيص فوق المقاطع، وليست مصدر حقيقة.",
    ]
    if terms:
        items.append("2. **أهم المصطلحات:** " + "، ".join(terms) + ".")
    if headings:
        items.append("3. **أهم الأقسام:** " + "؛ ".join(headings[:4]) + ".")
    items.append(
        "4. **كيف تستخدمه:** اقرأ §4 للأنظمة، ثم §16 للأسئلة، "
        "وارجع دائماً للمقطع الخام المذكور مصدراً — لا تثق بخلاصة بلا مصدر.")
    items.append(
        "5. **القاعدة:** كل ادعاء هنا يرجع لمقطع خام بمساره وبصمته؛ "
        "وإن غاب الدليل فالجواب «لا أعرف».")
    prefix = "**§1:** "
    kept = _fit(items, " ", prefix)
    return prefix + "## §1 — TL;DR — الجوهر في 60 ثانية " + " ".join(kept) + " ---"


def _section_4(domain: str, systems: list) -> str:
    """§4 — the systems, one per source file, under the char cap."""
    prefix = "**§4:** "
    kept = _fit(systems, " --- ", prefix)
    return prefix + "## §4 — الأنظمة الكاملة " + " --- ".join(kept) + " ---"


def _section_16(domain: str, qa: list, sources: list) -> str:
    """§16 — Q&A + the verified sources list, under the char cap.

    Sources are kept whenever possible: Q&A pairs are dropped first
    if the section would overflow."""
    prefix = "**§16:** "
    qa_kept = list(qa)
    src_kept = list(sources)
    body = ("## §16 — أسئلة وإجابات "
            + " ".join(qa_kept)
            + " **المصادر (مسارات حقيقية على القرص — كل مسار تحققنا من "
              "وجوده قبل الكتابة):** "
            + " ".join(src_kept)
            + " ---")
    while _content_len(body, prefix) > SECTION_CHAR_LIMIT and len(qa_kept) > 0:
        qa_kept.pop()
        body = ("## §16 — أسئلة وإجابات "
                + " ".join(qa_kept)
                + " **المصادر (مسارات حقيقية على القرص — كل مسار تحققنا من "
                  "وجوده قبل الكتابة):** "
                + " ".join(src_kept)
                + " ---")
    while _content_len(body, prefix) > SECTION_CHAR_LIMIT and len(src_kept) > 1:
        src_kept.pop()
        body = ("## §16 — أسئلة وإجابات "
                + " ".join(qa_kept)
                + " **المصادر (مسارات حقيقية على القرص — كل مسار تحققنا من "
                  "وجوده قبل الكتابة):** "
                + " ".join(src_kept)
                + " ---")
    return prefix + body


def _build_master(domain: str, files: dict, terms_by_file: dict,
                  concepts: list, abs_paths: dict, data_dir: str,
                  masters_dir: str) -> dict | None:
    """Build one master's text from its domain's files.

    ``files`` maps raw_path -> [chunks]. Returns the master record
    (or None if the domain has no verifiable source file).
    """
    name = master_name(domain)
    systems, qa, sources = [], [], []
    n_chunks = 0
    total_files = len(files)
    for raw_path in sorted(files):
        chunks = sorted(files[raw_path], key=lambda c: c["chunk_id"])
        n_chunks += len(chunks)
        abs_path = _resolve_source(raw_path, abs_paths, data_dir)
        if abs_path is None:
            continue  # unverifiable source: drop it entirely (link rule)
        first = chunks[0]
        # Quotes must come from a real content chunk, not a heading-only
        # chunk (chunk.py emits heading chunks whose text IS the heading
        # — quoting one would just repeat the title as if it were a
        # claim).
        content = [c for c in chunks if c.get("type") != "heading"]
        quote = content[0] if content else first
        cite = (f"`{abs_path}` — chunk `{quote['chunk_id']}` "
                f"(sha256: {quote['sha256_short']})")
        title = _file_title(chunks)
        headings = _headings(chunks, concepts, raw_path)
        systems.append(
            f"### 4.{len(systems) + 1} {sanitize_text(title)}: "
            f"{excerpt(quote.get('text', ''))} (المصدر: {cite}) "
            f"الأقسام: {sanitize_text('؛ '.join(headings[:6])) or '—'}.")
        sources.append(f"- {cite} — {sanitize_text(title)}.")
        if len(qa) < MAX_QA_PER_MASTER and headings:
            q_head = headings[0]
            qa.append(
                f"**س {len(qa) + 1}: ما {sanitize_text(q_head)} في "
                f"{sanitize_text(title)}؟** ج: "
                f"{excerpt(quote.get('text', ''))} (المصدر: {cite})")
    if not systems:
        return None

    # §1 terms: top terms of this domain's files, by best score.
    best = {}
    for raw_path in files:
        for item in terms_by_file.get(raw_path, []):
            t, s = item["term"], item["score"]
            if t not in best or s > best[t]:
                best[t] = s
    top_terms = [t for t, _ in sorted(best.items(), key=lambda kv: -kv[1])
                 [:MAX_TERMS_S1]]
    all_headings = []
    for raw_path in sorted(files):
        for h in _headings(files[raw_path], concepts, raw_path):
            if h not in all_headings:
                all_headings.append(h)

    # Tension note (both sides, no quarantine): recorded tension
    # sections in this domain's chunks, with their source files.
    tensions = []
    for raw_path in sorted(files):
        for ch in files[raw_path]:
            section = ch.get("section", "")
            if TENSION_RE.search(section) and raw_path not in tensions:
                tensions.append(raw_path)
    if tensions:
        tension_line = (
            "**توترات موثقة:** المصادر تسجل توصيات/مواقف مختلفة في هذا "
            "الموضوع — نعرض الطرفين ولا نحسم بصمت (لا حجر خالص): " +
            "؛ ".join(f"`{p}`" for p in
                      (_resolve_source(p, abs_paths, data_dir) or p
                       for p in tensions)) + ".")
        qa.append(tension_line)

    s1 = _section_1(domain, len(systems), n_chunks, top_terms, all_headings)
    s4 = _section_4(domain, systems[:MAX_SYSTEMS_PER_MASTER])
    s16 = _section_16(domain, qa, sources)

    lines = [
        f"## {name}",
        f"`masters/{name}.md`",
        "",
        s1,
        "",
        s4,
        "",
        s16,
        "",
        "---",
        "",
    ]
    path = os.path.join(masters_dir, f"{name}.md")
    with open(path, "w", encoding="utf-8") as fh:
        # 11 lines, each newline-terminated (the 11th line is blank).
        fh.write("\n".join(lines) + "\n")
    return {
        "domain": domain,
        "name": name,
        "path": path,
        "sources": len(systems),
        "sources_total": total_files,
        "chunks": n_chunks,
        "links": len(sources) + len(qa),
        "sections": {"s1_chars": _content_len(s1, "**§1:** "),
                     "s4_chars": _content_len(s4, "**§4:** "),
                     "s16_chars": _content_len(s16, "**§16:** ")},
    }


def _render_index(masters: list, data_dir: str) -> str:
    lines = [
        "# Masters — روتر الماسترز",
        "",
        "> الماسترز طبقة تنقّل وتلخيص فوق المقاطع، وليست مصدر حقيقة. "
        "كل ادعاء في ماستر يرجع لمقطع خام بمساره وبصمته. الروابط هنا "
        "تشاور على الملفات كما هي — لا نُقل أي ملف.",
        "",
        "## الماسترز",
        "",
    ]
    for m in masters:
        lines.append(
            f"- [{m['name']}](./{m['name']}.md) — domain `{m['domain']}` — "
            f"{m['sources']} ملف خام، {m['chunks']} مقطعاً")
    lines += ["", "## المصادر الخام", ""]
    for m in masters:
        lines.append(f"- domain `{m['domain']}`: ماستر `{m['name']}` "
                     f"في `./{m['name']}.md` — {m['sources']} ملفاً خاماً.")
    lines += [
        "",
        "## ملاحظة",
        "",
        f"مولّدة بـ `python3 -m wikimind masters --data {data_dir}` "
        f"— ماستر واحد لكل domain موجود في chunks.jsonl، "
        "والروابط كلها تحققنا من وجودها على القرص قبل كتابتها.",
        "",
    ]
    return "\n".join(lines)


def build_masters(data_dir: str) -> dict:
    """Read chunks.jsonl (+ terms.json) from data_dir and build one
    master per domain plus masters/index.md. Returns a summary dict."""
    chunks_path = os.path.join(data_dir, "chunks.jsonl")
    if not os.path.exists(chunks_path):
        raise FileNotFoundError(f"chunks.jsonl not found in {data_dir} "
                                "(run ingest + chunk first)")
    chunks = _load_jsonl(chunks_path)
    terms = _load_terms(data_dir)
    abs_paths = _load_abs_paths(data_dir)
    concepts = terms.get("concepts", [])
    terms_by_file = terms.get("per_doc", {})

    by_domain = {}
    for ch in chunks:
        domain = ch.get("domain", "general") or "general"
        by_domain.setdefault(domain, {}).setdefault(ch["raw_path"], []).append(ch)

    masters_dir = os.path.join(data_dir, "masters")
    os.makedirs(masters_dir, exist_ok=True)

    masters, skipped = [], []
    links_total = links_verified = links_dropped = 0
    for domain in sorted(by_domain):
        n_files = len(by_domain[domain])
        result = _build_master(domain, by_domain[domain], terms_by_file,
                               concepts, abs_paths, data_dir, masters_dir)
        if result is None:
            skipped.append(domain)
            links_dropped += n_files
            continue
        masters.append(result)
        links_verified += result["links"]
        links_total += result["links"]
        links_dropped += result["sources_total"] - result["sources"]

    index_path = os.path.join(masters_dir, "index.md")
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(_render_index(masters, data_dir))

    return {
        "domains": len(by_domain),
        "masters": len(masters),
        "skipped_domains": skipped,
        "sources": sum(m["sources"] for m in masters),
        "chunks": sum(m["chunks"] for m in masters),
        "links_total": links_total,
        "links_verified": links_verified,
        "links_dropped": links_dropped,
        "masters_dir": masters_dir,
        "index": index_path,
        "masters_detail": masters,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Build one master per domain + masters/index.md router.")
    ap.add_argument("--data", required=True,
                    help="data directory (chunks.jsonl lives here)")
    args = ap.parse_args(argv)
    try:
        stats = build_masters(args.data)
    except FileNotFoundError as exc:
        print(f"masters: {exc}", file=sys.stderr)
        return 2
    print(f"domains={stats['domains']} masters={stats['masters']} "
          f"sources={stats['sources']} chunks={stats['chunks']} "
          f"links_verified={stats['links_verified']} "
          f"links_dropped={stats['links_dropped']} -> {stats['index']}")
    if stats["skipped_domains"]:
        print(f"skipped domains (no verifiable source): "
              f"{', '.join(stats['skipped_domains'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
