"""Unit tests for wikimind.masters — stdlib unittest only.

Run from the repo root:
  PYTHONPATH=src python3 -m unittest discover -s tests -v

The tests build a tiny 2-file data dir in tmp from
examples/sample-corpus/ (one outbound file, one sales file) and run
the real pipeline (ingest -> chunk -> terms -> masters) on it, so
``build_masters`` is tested against the same chunks/terms the other
modules produce.

Checks:
- masters are built (one per domain) + masters/index.md exists;
- every path link inside a master exists on disk for real (the
  100%-broken-links failure of the old 39 masters must not recur);
- masters count == number of domains;
- index.md points only at masters that actually exist;
- the §1/§4/§16 structure holds (order, single line, under the
  5,000-char truncation cliff, closed with " --- ");
- the CLI (``wikimind.masters.main`` and
  ``python3 -m wikimind masters``) returns 0.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wikimind import masters as masters_mod  # noqa: E402
from wikimind.chunk import chunk_all  # noqa: E402
from wikimind.ingest import ingest  # noqa: E402
from wikimind.terms import main as terms_main  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_CORPUS = os.path.join(REPO_ROOT, "examples", "sample-corpus")

# Two files, two distinct domains (chunk.extract_domain):
#   CPT_CURATED_OUTBOUND_WARMUP.md -> outbound
#   CPT_CURATED_SALES_VALUE_PRICING.md -> sales
SAMPLE_FILES = [
    "CPT_CURATED_OUTBOUND_WARMUP.md",
    "CPT_CURATED_SALES_VALUE_PRICING.md",
]

PATH_IN_BACKTICKS_RE = re.compile(r"`([^`]+)`")
MD_LINK_RE = re.compile(r"\]\((\./[^)]+)\)")


def build_data_dir(tmp):
    """Ingest + chunk + terms the 2-file corpus; return the data dir."""
    corpus_dir = os.path.join(tmp, "corpus")
    os.makedirs(corpus_dir)
    for name in SAMPLE_FILES:
        shutil.copy(os.path.join(SAMPLE_CORPUS, name),
                    os.path.join(corpus_dir, name))
    data_dir = os.path.join(tmp, "data")
    ingest(corpus_dir, data_dir)
    chunk_all(data_dir)
    terms_main(["--data", data_dir])
    return data_dir


def resolve_path_candidate(candidate, data_dir, masters_dir):
    """Resolve a path-shaped string the way a reader would, or None
    when it is not a path at all."""
    if os.path.isabs(candidate):
        return candidate
    if candidate.startswith("./"):
        return os.path.join(masters_dir, candidate[2:])
    if candidate.startswith("masters/"):
        return os.path.join(data_dir, candidate)
    if candidate.endswith((".md", ".txt")):
        return os.path.join(data_dir, candidate)
    return None


def extract_path_candidates(text, data_dir, masters_dir):
    """All path-shaped strings in a file's text, resolved to absolute
    paths (chunk ids like ``a1b2c3-0000`` are not paths and are
    ignored)."""
    found = []
    for cand in PATH_IN_BACKTICKS_RE.findall(text):
        resolved = resolve_path_candidate(cand, data_dir, masters_dir)
        if resolved is not None:
            found.append((cand, resolved))
    for rel in MD_LINK_RE.findall(text):
        found.append((rel, os.path.join(masters_dir, rel[2:])))
    return found


class TestBuildMasters(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = build_data_dir(self.tmp.name)
        self.masters_dir = os.path.join(self.data_dir, "masters")
        self.summary = masters_mod.build_masters(self.data_dir)

    def tearDown(self):
        self.tmp.cleanup()

    def _master_files(self):
        return sorted(f for f in os.listdir(self.masters_dir)
                      if f.startswith("Master_") and f.endswith(".md"))

    def _domains(self):
        with open(os.path.join(self.data_dir, "chunks.jsonl"),
                  encoding="utf-8") as fh:
            return sorted({json.loads(line)["domain"] for line in fh})

    def test_masters_built_and_index_exists(self):
        """One master per domain + masters/index.md."""
        self.assertEqual(self.summary["masters"], 2)
        self.assertEqual(self.summary["domains"], 2)
        self.assertEqual(self._master_files(),
                         ["Master_Outbound.md", "Master_Sales.md"])
        self.assertTrue(os.path.isfile(
            os.path.join(self.masters_dir, "index.md")))
        self.assertEqual(self.summary["index"],
                         os.path.join(self.masters_dir, "index.md"))

    def test_masters_count_equals_domain_count(self):
        """masters == number of distinct domains in chunks.jsonl."""
        domains = self._domains()
        self.assertEqual(domains, ["outbound", "sales"])
        self.assertEqual(len(self._master_files()), len(domains))
        self.assertEqual(self.summary["masters"], len(domains))

    def test_every_path_link_in_masters_exists_on_disk(self):
        """No broken links: every path-shaped string inside a master
        resolves to a real file (absolute raw paths and the masters/
        self-path)."""
        for fname in self._master_files():
            with open(os.path.join(self.masters_dir, fname),
                      encoding="utf-8") as fh:
                text = fh.read()
            found = extract_path_candidates(text, self.data_dir,
                                            self.masters_dir)
            self.assertTrue(found, f"{fname} cites no paths at all")
            for cand, resolved in found:
                self.assertTrue(os.path.isfile(resolved),
                                f"{fname}: {cand!r} -> {resolved} missing")
        self.assertEqual(self.summary["links_dropped"], 0)
        self.assertEqual(self.summary["links_verified"],
                         self.summary["links_total"])
        self.assertGreater(self.summary["links_verified"], 0)

    def test_index_points_to_existing_masters(self):
        """Every master link in masters/index.md resolves to a real
        master file, and the count matches."""
        with open(os.path.join(self.masters_dir, "index.md"),
                  encoding="utf-8") as fh:
            text = fh.read()
        targets = MD_LINK_RE.findall(text)
        self.assertEqual(len(targets), len(self._master_files()))
        for rel in targets:
            self.assertTrue(rel.startswith("./Master_"))
            self.assertTrue(os.path.isfile(
                os.path.join(self.masters_dir, rel[2:])),
                f"index.md -> {rel} missing")
        for fname in self._master_files():
            self.assertIn(f"./{fname}", text)

    def test_section_structure_and_char_cap(self):
        """§1 then §4 then §16, each a single line under 5,000 chars
        of content, each closed with ' --- '; no wiki/markdown links."""
        for fname in self._master_files():
            with open(os.path.join(self.masters_dir, fname),
                      encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            self.assertEqual(len(lines), 12, f"{fname}: not 11 lines + NL")
            self.assertTrue(lines[0].startswith("## Master_"))
            s1 = next(i for i, ln in enumerate(lines)
                      if ln.startswith("**§1:** "))
            s4 = next(i for i, ln in enumerate(lines)
                      if ln.startswith("**§4:** "))
            s16 = next(i for i, ln in enumerate(lines)
                       if ln.startswith("**§16:** "))
            self.assertTrue(s1 < s4 < s16)
            for i, prefix in ((s1, "**§1:** "), (s4, "**§4:** "),
                              (s16, "**§16:** ")):
                content = lines[i][len(prefix):]
                self.assertLess(len(content), 5000,
                                f"{fname} {prefix.strip()}: "
                                f"{len(content)} chars >= 5000")
                self.assertTrue(content.rstrip().endswith(" ---"),
                                f"{fname} {prefix.strip()}: not closed")
            text = "\n".join(lines)
            self.assertNotIn("[[", text)
            self.assertNotIn("]]", text)
            self.assertNotIn("](", text)
            self.assertNotIn("http://", text)
            self.assertNotIn("https://", text)

    def test_masters_cite_raw_chunks_of_their_domain(self):
        """Each master cites at least one chunk id and one absolute
        raw path from its own domain, with the sha fingerprint."""
        with open(os.path.join(self.data_dir, "chunks.jsonl"),
                  encoding="utf-8") as fh:
            chunks = [json.loads(line) for line in fh]
        for fname in self._master_files():
            domain = "outbound" if "Outbound" in fname else "sales"
            domain_chunks = [c for c in chunks if c["domain"] == domain]
            with open(os.path.join(self.masters_dir, fname),
                      encoding="utf-8") as fh:
                text = fh.read()
            self.assertTrue(
                any(c["chunk_id"] in text for c in domain_chunks),
                f"{fname}: no chunk id of domain {domain} cited")
            self.assertIn("sha256:", text)
            self.assertIn("توترات موثقة", text,
                          f"{fname}: tension note missing")

    def test_main_cli_returns_zero_and_is_idempotent(self):
        """masters.main(['--data', DIR]) returns 0 and re-running
        keeps the same masters."""
        rc = masters_mod.main(["--data", self.data_dir])
        self.assertEqual(rc, 0)
        self.assertEqual(self._master_files(),
                         ["Master_Outbound.md", "Master_Sales.md"])

    def test_subprocess_cli(self):
        """python3 -m wikimind masters --data DIR works via the
        package dispatcher."""
        env = dict(os.environ, PYTHONPATH=os.path.join(REPO_ROOT, "src"))
        proc = subprocess.run(
            [sys.executable, "-m", "wikimind", "masters",
             "--data", self.data_dir],
            cwd=REPO_ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("masters=2", proc.stdout)
        self.assertIn("links_verified=", proc.stdout)

    def test_missing_chunks_returns_2(self):
        empty = os.path.join(self.tmp.name, "empty")
        os.makedirs(empty)
        self.assertEqual(masters_mod.main(["--data", empty]), 2)


if __name__ == "__main__":
    unittest.main()
