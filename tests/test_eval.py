"""Unit tests for wikimind.eval — stdlib unittest only.

Run from the repo root:
  PYTHONPATH=src python3 -m unittest discover -s tests -v

The tests build a tiny 3-file corpus in a temp dir and run the real
pipeline (ingest -> chunk -> index) on it, so ``evaluate`` is tested
against the same retrieval path ``ask`` uses.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wikimind import eval as eval_mod  # noqa: E402
from wikimind.ask import ask  # noqa: E402
from wikimind.chunk import chunk_all  # noqa: E402
from wikimind.index import build_index, save_index  # noqa: E402
from wikimind.ingest import ingest  # noqa: E402

CORPUS = {
    "alpha.md": "# التفاح الأحمر\n\nالتفاح فاكهة حمراء تنمو على الأشجار في البساتين.\n",
    "beta.md": "# البرتقال الحمضي\n\nالبرتقال فاكهة حمضية غنية بفيتامين سي.\n",
    "gamma.md": "# الموز الأصفر\n\nالموز فاكهة صفراء طويلة غنية بالبوتاسيوم.\n",
}


def build_data_dir(tmp):
    """Ingest + chunk + index the 3-file corpus; return the data dir."""
    corpus_dir = os.path.join(tmp, "corpus")
    os.makedirs(corpus_dir)
    for name, text in CORPUS.items():
        with open(os.path.join(corpus_dir, name), "w", encoding="utf-8") as fh:
            fh.write(text)
    data_dir = os.path.join(tmp, "data")
    ingest(corpus_dir, data_dir)
    chunk_all(data_dir)
    from wikimind.index import load_chunks
    save_index(build_index(load_chunks(data_dir)), data_dir)
    return data_dir


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = build_data_dir(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_title_question_ranks_first(self):
        """A question matching a section title retrieves that file rank 1."""
        report = eval_mod.evaluate(self.data_dir, [
            {"question": "التفاح الأحمر", "expected_file": "alpha.md",
             "type": "title"},
        ])
        self.assertEqual(report["n_questions"], 1)
        self.assertEqual(report["rank_1"]["count"], 1)
        self.assertEqual(report["rank_1"]["rate"], 1.0)
        self.assertEqual(report["results"][0]["rank"], 1)
        self.assertEqual(report["results"][0]["top_1_file"], "alpha.md")

    def test_no_term_overlap_returns_nothing(self):
        """A question sharing no term with any chunk scores nothing.

        This is the retrieval basis of ask's "لا أعرف": zero overlap
        means zero evidence.
        """
        report = eval_mod.evaluate(self.data_dir, [
            {"question": "حوسبة سحابية خوادم معالجات", "expected_file": "alpha.md",
             "type": "paragraph"},
        ])
        self.assertIsNone(report["results"][0]["rank"])
        self.assertFalse(report["results"][0]["in_top_3"])
        self.assertEqual(report["results"][0]["top_3_files"], [])
        self.assertEqual(report["absent"], 1)

        answer = ask(self.data_dir, "حوسبة سحابية خوادم معالجات")
        self.assertTrue(answer["no_evidence"])
        self.assertEqual(answer["results"], [])

    def test_counts_and_rates_on_known_set(self):
        """rank-1 / top-3 counts, rates and per-type split on a known set."""
        questions = [
            {"question": "التفاح الأحمر", "expected_file": "alpha.md",
             "type": "title"},
            {"question": "البرتقال الحمضي", "expected_file": "beta.md",
             "type": "title"},
            {"question": "فاكهة صفراء طويلة غنية بالبوتاسيوم",
             "expected_file": "gamma.md", "type": "paragraph"},
            {"question": "حوسبة سحابية خوادم معالجات", "expected_file": "alpha.md",
             "type": "paragraph"},
        ]
        report = eval_mod.evaluate(self.data_dir, questions, top_k=5)
        self.assertEqual(report["n_questions"], 4)
        self.assertEqual(report["rank_1"]["count"], 3)
        self.assertEqual(report["rank_1"]["rate"], 0.75)
        self.assertEqual(report["top_3"]["count"], 3)
        self.assertEqual(report["top_3"]["rate"], 0.75)
        self.assertEqual(report["absent"], 1)
        self.assertEqual(report["skipped"], 0)
        by_type = report["by_type"]
        self.assertEqual(by_type["title"]["n"], 2)
        self.assertEqual(by_type["title"]["rank_1"], 2)
        self.assertEqual(by_type["title"]["rank_1_rate"], 1.0)
        self.assertEqual(by_type["paragraph"]["n"], 2)
        self.assertEqual(by_type["paragraph"]["rank_1"], 1)
        self.assertEqual(by_type["paragraph"]["rank_1_rate"], 0.5)
        self.assertEqual(by_type["paragraph"]["top_3"], 1)

    def test_malformed_entries_are_skipped_not_scored(self):
        report = eval_mod.evaluate(self.data_dir, [
            {"question": "التفاح الأحمر", "expected_file": "alpha.md"},
            {"question": "بلا ملف متوقع"},
            {"expected_file": "beta.md"},
            "not a dict",
        ])
        self.assertEqual(report["n_questions"], 1)
        self.assertEqual(report["skipped"], 3)
        self.assertEqual(report["rank_1"]["count"], 1)

    def test_persona_filter_and_min_score(self):
        """persona narrows retrieval; a high min-score makes all absent."""
        q = [{"question": "التفاح الأحمر", "expected_file": "alpha.md",
              "type": "title"}]
        # All temp-corpus chunks carry persona "default".
        self.assertEqual(
            eval_mod.evaluate(self.data_dir, q, persona="default")
            ["rank_1"]["count"], 1)
        self.assertEqual(
            eval_mod.evaluate(self.data_dir, q, persona="other")
            ["absent"], 1)
        self.assertEqual(
            eval_mod.evaluate(self.data_dir, q, min_score=999.0)
            ["absent"], 1)
        self.assertEqual(
            eval_mod.evaluate(self.data_dir, q, min_score=0.0)
            ["rank_1"]["count"], 1)

    def test_report_to_json_round_trips(self):
        report = eval_mod.evaluate(self.data_dir, [
            {"question": "التفاح الأحمر", "expected_file": "alpha.md",
             "type": "title"},
        ])
        text = eval_mod.report_to_json(report)
        parsed = json.loads(text)
        self.assertEqual(parsed["n_questions"], 1)
        self.assertEqual(parsed["results"][0]["expected_file"], "alpha.md")
        # Arabic is kept as-is, not \u-escaped.
        self.assertIn("التفاح", text)


class TestEvalCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = build_data_dir(self.tmp.name)
        self.qpath = os.path.join(self.tmp.name, "questions.json")
        with open(self.qpath, "w", encoding="utf-8") as fh:
            json.dump([
                {"question": "التفاح الأحمر", "expected_file": "alpha.md",
                 "type": "title"},
            ], fh, ensure_ascii=False)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_writes_json_to_stdout(self):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = eval_mod.main(["--data", self.data_dir,
                                "--questions", self.qpath])
        self.assertEqual(rc, 0)
        report = json.loads(buf.getvalue())
        self.assertEqual(report["n_questions"], 1)
        self.assertEqual(report["rank_1"]["count"], 1)

    def test_cli_out_file_and_summary(self):
        out_path = os.path.join(self.tmp.name, "report.json")
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = eval_mod.main(["--data", self.data_dir,
                                "--questions", self.qpath,
                                "--out", out_path])
        self.assertEqual(rc, 0)
        self.assertIn("rank-1=1", buf.getvalue())
        with open(out_path, encoding="utf-8") as fh:
            report = json.load(fh)
        self.assertEqual(report["n_questions"], 1)

    def test_cli_missing_data_dir_returns_2(self):
        rc = eval_mod.main(["--data", os.path.join(self.tmp.name, "nope"),
                            "--questions", self.qpath])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
