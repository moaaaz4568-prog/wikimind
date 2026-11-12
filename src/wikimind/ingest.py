"""ingest: read a user's own files (md/txt) into a manifest.

Pipeline step 1.

Input:  a corpus directory given by the user (any domain, any language).
Output: <data>/manifest.jsonl — one JSON record per accepted file:
        raw_path (corpus-relative), abs_path, sha256, sha256_short,
        size_bytes, words, persona
        <data>/skipped.jsonl — every rejected file + the reason.

Rules (documented defaults, see docs/DESIGN.md):
- Accepted extensions: .md and .txt only.
- Dedupe by content sha256: identical content is recorded once; the
  later copy is skipped as ``duplicate_content``.
- Pointer/tiny files are skipped: < 100 bytes of text, or a file whose
  whole content is 1-2 bare filesystem paths (e.g. ``/root/...``).
- NEVER touched, whatever the corpus contains (hard exclusion):
  any path component matching ``07_control`` or ``control``,
  any hidden directory (starts with ``.``), any ``__pycache__``,
  and any file whose name looks like a secret/credential
  (``*secret*``, ``*credential*``, ``*token*``, ``*.pem``, ``*.key``,
  ``*.p12``, ``id_rsa*``). These are skipped with reason
  ``excluded_control_or_secret`` and are never read.
- Persona: explicit only. A corpus may contain a ``personas/`` folder
  at its root, with one subdirectory per persona dataset
  (``personas/haitham/*.md``, ``personas/business/*.md``). Files under
  ``personas/<name>/`` get persona ``<name>``; every other file gets
  persona ``default``. A plain user's files have no ``personas/``
  folder, so no persona is ever imposed. The persona filter is
  optional everywhere else (``ask --persona NAME``).

Usage:
  python3 -m wikimind ingest --corpus DIR --data DIR
"""

import argparse
import hashlib
import json
import os
import re
import sys

ACCEPTED_EXTS = (".md", ".txt")
MIN_TEXT_BYTES = 100

# Hard exclusion: control/credential material is never read, never indexed.
EXCLUDED_DIR_PARTS = frozenset({"07_control", "control", "__pycache__"})
SECRET_NAME_RES = (
    re.compile(r"secret", re.I),
    re.compile(r"credential", re.I),
    re.compile(r"token", re.I),
    re.compile(r"\.(pem|key|p12)$", re.I),
    re.compile(r"^id_rsa", re.I),
)
POINTER_RE = re.compile(r"^\s*(/root/|/sdcard/|/home/|C:\\|~/)\S*\s*$")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_secret_or_control(rel_path: str) -> bool:
    """True if the path must never be read (control dir or secret-like)."""
    parts = rel_path.replace("\\", "/").split("/")
    for part in parts:
        low = part.lower()
        if low in EXCLUDED_DIR_PARTS or low.startswith("."):
            return True
    name = parts[-1]
    return any(rx.search(name) for rx in SECRET_NAME_RES)


def is_pointer_or_tiny(text: str) -> bool:
    stripped = text.strip()
    if len(stripped.encode("utf-8")) < MIN_TEXT_BYTES:
        return True
    lines = [ln for ln in stripped.splitlines() if ln.strip()]
    if len(lines) <= 2 and all(POINTER_RE.match(ln) for ln in lines):
        return True
    return False


def persona_for(rel_path: str, corpus_root: str) -> str:
    """Persona is explicit only: ``personas/<name>/...`` -> ``<name>``,
    anything else -> ``default``."""
    parts = rel_path.replace("\\", "/").split("/")
    if len(parts) > 2 and parts[0] == "personas":
        return parts[1]
    return "default"


def collect_files(corpus: str):
    """Yield (corpus-relative path, absolute path) for .md/.txt files."""
    for root, dirs, files in os.walk(corpus):
        dirs.sort()
        # Never descend into excluded/hidden directories at all.
        dirs[:] = [d for d in dirs
                   if d.lower() not in EXCLUDED_DIR_PARTS
                   and not d.startswith(".")]
        for name in sorted(files):
            if not name.lower().endswith(ACCEPTED_EXTS):
                continue
            full = os.path.join(root, name)
            yield os.path.relpath(full, corpus), full


def ingest(corpus: str, out_dir: str) -> dict:
    """Run ingest; return counters. Writes manifest.jsonl + skipped.jsonl."""
    os.makedirs(out_dir, exist_ok=True)
    manifest_path = os.path.join(out_dir, "manifest.jsonl")
    skipped_path = os.path.join(out_dir, "skipped.jsonl")

    seen_hashes = {}
    n_found = n_kept = n_dup = n_skip = n_excluded = 0
    total_bytes = 0
    with open(manifest_path, "w", encoding="utf-8") as mf, \
            open(skipped_path, "w", encoding="utf-8") as sf:
        for rel, abs_path in collect_files(corpus):
            n_found += 1
            if is_secret_or_control(rel):
                sf.write(json.dumps(
                    {"raw_path": rel, "reason": "excluded_control_or_secret"},
                    ensure_ascii=False) + "\n")
                n_excluded += 1
                continue
            try:
                with open(abs_path, "rb") as fh:
                    data = fh.read()
            except OSError as exc:
                sf.write(json.dumps({"raw_path": rel,
                                     "reason": f"unreadable: {exc}"},
                                    ensure_ascii=False) + "\n")
                n_skip += 1
                continue
            digest = sha256_hex(data)
            if digest in seen_hashes:
                sf.write(json.dumps(
                    {"raw_path": rel, "reason": "duplicate_content",
                     "duplicate_of": seen_hashes[digest]},
                    ensure_ascii=False) + "\n")
                n_dup += 1
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("utf-8", errors="replace")
            if is_pointer_or_tiny(text):
                sf.write(json.dumps({"raw_path": rel,
                                     "reason": "pointer_or_too_small"},
                                    ensure_ascii=False) + "\n")
                n_skip += 1
                continue
            seen_hashes[digest] = rel
            total_bytes += len(data)
            mf.write(json.dumps({
                "raw_path": rel,
                "abs_path": abs_path,
                "sha256": digest,
                "sha256_short": digest[:12],
                "size_bytes": len(data),
                "words": len(text.split()),
                "persona": persona_for(rel, corpus),
            }, ensure_ascii=False) + "\n")
            n_kept += 1

    return {
        "found": n_found, "kept": n_kept, "duplicates_skipped": n_dup,
        "pointer_or_too_small_skipped": n_skip,
        "control_or_secret_excluded": n_excluded,
        "total_bytes": total_bytes,
        "manifest": manifest_path, "skipped": skipped_path,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Ingest .md/.txt files into a manifest.")
    ap.add_argument("--corpus", required=True, help="user's corpus directory")
    ap.add_argument("--data", required=True, help="output data directory")
    args = ap.parse_args(argv)
    stats = ingest(args.corpus, args.data)
    print(f"found={stats['found']} kept={stats['kept']} "
          f"duplicates_skipped={stats['duplicates_skipped']} "
          f"pointer_or_too_small_skipped={stats['pointer_or_too_small_skipped']} "
          f"control_or_secret_excluded={stats['control_or_secret_excluded']} "
          f"total_bytes={stats['total_bytes']}")
    print(f"manifest: {stats['manifest']}")
    print(f"skipped:  {stats['skipped']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
