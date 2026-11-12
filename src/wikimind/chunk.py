"""chunk: structural chunking of ingested files.

Pipeline step 3 (after ingest; terms extraction is step 2 and is
independent of chunking).

Rules (from the project research, phase 2 — chunking policy R-2):
- A heading (#, ##, ###, ...) starts a new section. The section's
  heading breadcrumb (file title › section heading) travels with
  every chunk, so a verbatim section-title query still matches.
- Inside a section, text is split into blocks: paragraph / table
  (consecutive lines starting with ``|``) / list (consecutive lines
  starting with ``-``, ``*``, ``+`` or ``1.``). A table or a list is
  ONE chunk unit and is never torn apart mid-row/item unless it alone
  exceeds the word limit.
- Blocks accumulate into a chunk until ~MAX_WORDS (default 800). A
  single block longer than the limit is split on sentence boundaries
  (``.`` ``!`` ``?`` Arabic ``؟``), never across a heading, never
  blindly by characters.
- No overlap in v0.1 (documented default).
- YAML front matter (``--- ... ---``) at the top of a file is parsed
  for ``title``/``concept_id`` and dropped from chunk text.
- Compressed one-line sections of the form
  ``**§N:** ## § N: Title ...body...`` (as in NEXUS_BRAIN.md) are
  expanded: the § title becomes a real ``##`` heading and the rest
  becomes body text.

Chunk metadata (per the metadata schema, pilot subset):
  chunk_id, persona, domain, raw_path, sha256_short, section
  (breadcrumb), type (paragraph/table/list/heading/mixed), offset
  (char offset of the chunk's first char in the source file),
  words, bytes, source_lines ([first, last] 1-based line numbers).

Usage:
  python3 -m wikimind chunk --data DIR [--max-words 800]
Reads <data>/manifest.jsonl, writes <data>/chunks.jsonl.
"""

import argparse
import json
import os
import re
import sys

MAX_WORDS = 800

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BRAIN_SECTION_RE = re.compile(r"^\*\*§\s*(\d+)\s*:?\*\*\s*(#{1,6}\s+.*?)\s*$")
COMPRESSED_SECTION_RE = re.compile(r"^\*\*§\s*(\d+)\s*:?\*\*\s*(.*)$")
TABLE_LINE_RE = re.compile(r"^\s*\|")
LIST_LINE_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
SENT_SPLIT_RE = re.compile(r"(?<=[.!؟。])\s+")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def count_words(text: str) -> int:
    return len(text.split())


def split_long_paragraph(text: str, max_words: int) -> list:
    """Split a long paragraph on sentence boundaries, ~max_words each."""
    sentences = SENT_SPLIT_RE.split(text)
    parts, cur = [], ""
    for sent in sentences:
        if not sent.strip():
            continue
        if count_words(cur + " " + sent) > max_words and cur:
            parts.append(cur.strip())
            cur = sent
        else:
            cur = (cur + " " + sent).strip() if cur else sent
        # One pathological sentence longer than the limit: word-split it.
        while count_words(cur) > max_words:
            words = cur.split()
            parts.append(" ".join(words[:max_words]))
            cur = " ".join(words[max_words:])
    if cur.strip():
        parts.append(cur.strip())
    return parts or [text]


def extract_domain(raw_path: str) -> str:
    """Domain from the path or the concept filename.

    Examples:
      CPT_CURATED_OUTBOUND_WARMUP  -> outbound
      CPT_NEW_OFFER_SALES_...      -> sales (second token after NEW_)
      .../01_outreach/C_...        -> outreach
      .../16_business_models/...   -> business_models
    Falls back to 'general'.
    """
    base = os.path.basename(raw_path)
    m = re.match(r"CPT_(?:CURATED_)?(?:NEW_)?([A-Za-z]+)", base)
    if m:
        return m.group(1).lower()
    m = re.search(r"/(\d{2})_([a-z0-9_]+)/", raw_path)
    if m:
        return m.group(2)
    m = re.search(r"/(\d{2})_([a-z0-9_]+)$", os.path.dirname(raw_path))
    if m:
        return m.group(2)
    return "general"


def parse_blocks(lines):
    """Yield (kind, text, start_line) blocks from section body lines."""
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if TABLE_LINE_RE.match(line):
            j = i
            buf = []
            while j < n and (TABLE_LINE_RE.match(lines[j]) or not lines[j].strip()):
                if lines[j].strip():
                    buf.append(lines[j].rstrip())
                j += 1
            yield "table", "\n".join(buf), i
            i = j
            continue
        if LIST_LINE_RE.match(line):
            j = i
            buf = []
            while j < n and (LIST_LINE_RE.match(lines[j]) or
                             (lines[j].startswith((" ", "\t")) and lines[j].strip())):
                buf.append(lines[j].rstrip())
                j += 1
            yield "list", "\n".join(buf), i
            i = j
            continue
        # Paragraph: consecutive non-blank, non-table, non-list lines.
        j = i
        buf = []
        while j < n and lines[j].strip() and not TABLE_LINE_RE.match(lines[j]) \
                and not LIST_LINE_RE.match(lines[j]):
            buf.append(lines[j].strip())
            j += 1
        yield "paragraph", " ".join(buf), i
        i = j


def split_long_block(kind: str, text: str, max_words: int) -> list:
    """Split an over-long table/list block into ~max_words sub-blocks.

    Tables keep their header (first two lines: header + separator) on
    each sub-block. Lists are grouped item by item.
    """
    lines = text.split("\n")
    if kind == "table" and len(lines) >= 2 and re.match(r"^\s*\|[\s:-]+\|", lines[1]):
        header, rows = lines[:2], lines[2:]
    else:
        header, rows = [], lines
    parts, cur = [], []
    cur_words = sum(count_words(h) for h in header)
    for ln in rows:
        w = count_words(ln)
        if cur and cur_words + w > max_words:
            parts.append("\n".join(header + cur))
            cur, cur_words = [], sum(count_words(h) for h in header)
        if w > max_words:  # pathological single row/item: word-split it
            words = ln.split()
            for i in range(0, len(words), max_words):
                parts.append("\n".join(header + [" ".join(words[i:i + max_words])]))
            continue
        cur.append(ln)
        cur_words += w
    if cur:
        parts.append("\n".join(header + cur))
    return parts or [text]


def expand_compressed_lines(text: str) -> str:
    """Flatten compressed single-line § sections (NEXUS_BRAIN.md style).

    Each ``**§N:** ## § N: Title ...body...`` physical line packs a
    whole section: the § title (up to the first inline ``###`` or
    numbered item) becomes a real ``##`` heading line, and the rest
    becomes body text. Inline ``###`` sub-headings inside the body are
    flattened into the text (their words stay indexed).
    """
    out = []
    for line in text.split("\n"):
        m = COMPRESSED_SECTION_RE.match(line)
        if not m:
            out.append(line)
            continue
        rest = m.group(2).strip()
        if rest.startswith("#"):
            hm = re.match(r"(#{1,6})\s+(.*)$", rest)
            if hm:
                body = hm.group(2)
                cuts = [len(body)]
                mm = re.search(r"\s#{2,6}\s", body)
                if mm:
                    cuts.append(mm.start())
                mm = re.search(r"\s\d+[.)]\s", body)
                if mm:
                    cuts.append(mm.start())
                cut = min(cuts)
                heading, tail = body[:cut].strip(), body[cut:].strip()
                out.append(f"## {heading}")
                if tail:
                    tail = re.sub(r"(?:^|\s)#{2,6}\s", " — ", tail)
                    out.append(tail)
                continue
        out.append(f"## §{m.group(1)}")
        if rest:
            out.append(re.sub(r"(?:^|\s)#{2,6}\s", " — ", rest))
    return "\n".join(out)


def make_chunk(record, seq, ctype, text, section, domain, offset, src_lines):
    return {
        "chunk_id": f"{record['sha256_short']}-{seq:04d}",
        "persona": record.get("persona", "default"),
        "domain": domain,
        "raw_path": record["raw_path"],
        "sha256_short": record["sha256_short"],
        "section": section,
        "type": ctype,
        "offset": offset,
        "words": count_words(text),
        "bytes": len(text.encode("utf-8")),
        "source_lines": src_lines,
        "text": text,
    }


def chunk_file(record: dict, max_words: int = MAX_WORDS) -> list:
    with open(record["abs_path"], encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    raw_path = record["raw_path"]
    sha_short = record["sha256_short"]
    is_brain = os.path.basename(raw_path) == "NEXUS_BRAIN.md"

    front = {}
    body = text
    fm_offset = 0
    m = FRONTMATTER_RE.match(text)
    if m:
        for line in m.group(1).splitlines():
            kv = re.match(r"(\w+):\s*(.*)", line.strip())
            if kv:
                front[kv.group(1)] = kv.group(2).strip().strip('"')
        body = text[m.end():]
        fm_offset = m.end()

    if is_brain:
        body = expand_compressed_lines(body)
    lines = body.split("\n")
    line_offsets = []
    pos = fm_offset
    for ln in lines:
        line_offsets.append(pos)
        pos += len(ln) + 1

    # Split into sections by heading.
    sections = []  # (heading_text, level, line_no, [body lines])
    cur_head, cur_level, cur_start = front.get("title", ""), 0, 0
    cur_body = []
    for idx, line in enumerate(lines):
        hm = HEADING_RE.match(line)
        if is_brain:
            bm = BRAIN_SECTION_RE.match(line)
            if bm:
                hm = HEADING_RE.match(bm.group(2))
        if hm:
            if cur_body or cur_head:
                sections.append((cur_head, cur_level, cur_start, cur_body))
            cur_head = hm.group(2).strip()
            cur_level = len(hm.group(1))
            cur_start = idx
            cur_body = []
        else:
            cur_body.append(line)
    if cur_body or cur_head:
        sections.append((cur_head, cur_level, cur_start, cur_body))

    base_domain = extract_domain(raw_path)
    file_title = front.get("title") or os.path.splitext(os.path.basename(raw_path))[0]
    chunks = []
    seq = 0
    for head, level, start_line, body_lines in sections:
        breadcrumb = file_title
        if head and head != breadcrumb:
            breadcrumb = f"{breadcrumb} › {head}"
        blocks = list(parse_blocks(body_lines))
        if not blocks:
            # Heading-only section: keep the heading itself as a chunk so
            # verbatim section-title queries still retrieve it.
            if head:
                off = line_offsets[start_line] if start_line < len(line_offsets) else 0
                chunks.append(make_chunk(record, seq, "heading", head, breadcrumb,
                                         base_domain, off, [start_line + 1, start_line + 1]))
                seq += 1
            continue
        cur_text, cur_type, cur_offset, cur_words = "", "paragraph", None, 0
        cur_first_line = None
        for kind, btext, bline in blocks:
            abs_line = start_line + bline
            offset = line_offsets[abs_line] if abs_line < len(line_offsets) else 0
            if count_words(btext) > max_words and kind in ("paragraph", "table", "list"):
                parts = (split_long_paragraph(btext, max_words) if kind == "paragraph"
                         else split_long_block(kind, btext, max_words))
                for part in parts:
                    if cur_text:
                        chunks.append(make_chunk(record, seq, cur_type, cur_text,
                                                 breadcrumb, base_domain, cur_offset,
                                                 [cur_first_line + 1, abs_line]))
                        seq += 1
                        cur_text, cur_words = "", 0
                    chunks.append(make_chunk(record, seq, kind, part, breadcrumb,
                                             base_domain, offset, [abs_line + 1, abs_line + 1]))
                    seq += 1
                continue
            if cur_text and cur_words + count_words(btext) > max_words:
                chunks.append(make_chunk(record, seq, cur_type, cur_text,
                                         breadcrumb, base_domain, cur_offset,
                                         [cur_first_line + 1, abs_line]))
                seq += 1
                cur_text, cur_words = "", 0
            if not cur_text:
                cur_type, cur_offset, cur_first_line = kind, offset, abs_line
            elif cur_type == "paragraph" and kind != "paragraph":
                cur_type = "mixed"
            cur_text = (cur_text + "\n\n" + btext).strip() if cur_text else btext
            cur_words = count_words(cur_text)
        if cur_text:
            chunks.append(make_chunk(record, seq, cur_type, cur_text,
                                     breadcrumb, base_domain, cur_offset,
                                     [cur_first_line + 1, start_line + len(body_lines)]))
            seq += 1
    return chunks


def chunk_all(data_dir: str, max_words: int = MAX_WORDS) -> dict:
    manifest_path = os.path.join(data_dir, "manifest.jsonl")
    out_path = os.path.join(data_dir, "chunks.jsonl")
    total = 0
    with open(manifest_path, encoding="utf-8") as mf, \
            open(out_path, "w", encoding="utf-8") as out:
        for line in mf:
            record = json.loads(line)
            for chunk in chunk_file(record, max_words):
                out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                total += 1
    return {"chunks": total, "out": out_path}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Structural chunking of ingested files.")
    ap.add_argument("--data", required=True, help="data directory (manifest lives here)")
    ap.add_argument("--max-words", type=int, default=MAX_WORDS)
    args = ap.parse_args(argv)
    stats = chunk_all(args.data, args.max_words)
    print(f"chunks={stats['chunks']} -> {stats['out']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
