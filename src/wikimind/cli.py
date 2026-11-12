"""wikimind: one command line for the whole pipeline — stdlib only.

Usage:
  PYTHONPATH=src python3 -m wikimind <command> [options]
  python3 src/wikimind/cli.py <command> [options]

Commands — each one delegates to the matching module's ``main(argv)``,
so every option is exactly the one documented in that module's
docstring (no second copy of the argument definitions lives here):
  ingest   ingest --corpus DIR --data DIR
  chunk    chunk --data DIR [--max-words 800]
  index    index --data DIR
  terms    terms --data DIR [--top-n 15]
  masters  masters --data DIR
  ask      ask "QUESTION" --data DIR [--top-k 5] [--persona NAME]
           [--min-score 0.0] [--both-sides] [--json]
  eval     eval --data DIR --questions FILE [--out FILE]
           [--top-k 5] [--persona NAME] [--min-score 0.0]
  build    build --corpus DIR --data DIR [--max-words 800] [--top-n 15]
           (runs ingest -> chunk -> index -> terms -> masters, in order;
           stops at the first step that fails)

Contract of the two dispatch targets (OBSERVED — verified end-to-end
2026-11-12, re-verified in the measurement pass the same day; see
docs/MEASUREMENTS.md):
  - ``wikimind.masters`` exposes ``build_masters(data_dir)`` (no
    ``out_dir`` parameter) and ``main(argv)`` accepting ``--data DIR``
    only; it writes one master per domain plus ``masters/index.md``
    under ``<data>/masters/``. An earlier draft of this docstring
    assumed ``build_masters(data_dir, out_dir=None)`` and ``--out``;
    that assumption was wrong and is removed — ``build`` calls it
    with ``--data`` only.
  - ``wikimind.eval`` exposes ``evaluate(data_dir, questions,
    top_k=5, persona=None, min_score=0.0)`` — ``questions`` is a
    list, not a path — and ``main(argv)`` accepting exactly
    ``--data DIR --questions FILE [--top-k 5] [--persona NAME]
    [--min-score 0.0] [--out FILE]``.
  The NOT_RUN fallback in ``_dispatch`` stays in place: if either
  file is ever absent again, the command exits 2 with a clear
  message instead of a traceback. ``main()`` returns the exit code.
"""

import argparse
import importlib
import importlib.util
import os
import sys

COMMANDS = ("ingest", "chunk", "index", "terms", "masters", "ask", "eval", "build")

USAGE = """usage: python3 -m wikimind <command> [options]
   or: python3 src/wikimind/cli.py <command> [options]

commands:
  ingest    ingest --corpus DIR --data DIR
  chunk     chunk --data DIR [--max-words 800]
  index     index --data DIR
  terms     terms --data DIR [--top-n 15]
  masters   masters --data DIR
  ask       ask "QUESTION" --data DIR [--top-k 5] [--persona NAME]
            [--min-score 0.0] [--both-sides] [--json]
  eval      eval --data DIR --questions FILE [--out FILE] [--top-k 5]
            [--persona NAME] [--min-score 0.0]
  build     build --corpus DIR --data DIR [--max-words 800] [--top-n 15]

run `python3 -m wikimind <command> --help` for a command's own options.
"""

_NOT_WRITTEN = (
    "{cmd}: wikimind.{mod} does not exist yet (NOT_RUN) — the owning "
    "agent is still writing it. This command dispatches to "
    "{mod}.main(argv) once the file exists; see the assumptions in "
    "cli.py's docstring."
)


def _ensure_importable() -> None:
    """Make ``wikimind.*`` importable when cli.py is run as a script.

    Under ``python3 -m wikimind`` the package is already importable.
    Under ``python3 src/wikimind/cli.py`` it is not (``__package__``
    is empty), so add the ``src/`` directory that contains this
    package to ``sys.path``.
    """
    if __package__:
        return
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def _module_main(module: str):
    """Return ``wikimind.<module>.main``, or None if the module file
    does not exist yet. A module that exists but fails to import
    raises normally, so a real bug is never hidden as NOT_RUN."""
    _ensure_importable()
    fullname = f"wikimind.{module}"
    if importlib.util.find_spec(fullname) is None:
        return None
    mod = importlib.import_module(fullname)
    return mod.main


def _dispatch(module: str, argv) -> int:
    """Run ``wikimind.<module>.main(argv)``; exit 2 if not written."""
    main_fn = _module_main(module)
    if main_fn is None:
        print(_NOT_WRITTEN.format(cmd=module, mod=module), file=sys.stderr)
        return 2
    return main_fn(argv)


def _build(argv=None) -> int:
    """Run ingest -> chunk -> index -> terms -> masters in order."""
    ap = argparse.ArgumentParser(
        description="Build the whole pipeline: ingest, chunk, index, terms, masters.")
    ap.add_argument("--corpus", required=True, help="user's corpus directory")
    ap.add_argument("--data", required=True, help="output data directory")
    ap.add_argument("--max-words", type=int, default=800)
    ap.add_argument("--top-n", type=int, default=15)
    args = ap.parse_args(argv)
    steps = [
        ("ingest", ["--corpus", args.corpus, "--data", args.data]),
        ("chunk", ["--data", args.data, "--max-words", str(args.max_words)]),
        ("index", ["--data", args.data]),
        ("terms", ["--data", args.data, "--top-n", str(args.top_n)]),
        ("masters", ["--data", args.data]),
    ]
    for name, step_argv in steps:
        print(f"[build] {name} {' '.join(step_argv)}")
        code = _dispatch(name, step_argv)
        if code != 0:
            print(f"[build] stopped: {name} exited with code {code}",
                  file=sys.stderr)
            return code
    print(f"[build] done -> {args.data}")
    return 0


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(USAGE)
        return 0 if argv else 2
    command, rest = argv[0], argv[1:]
    if command not in COMMANDS:
        print(f"unknown command: {command}\n{USAGE}", file=sys.stderr)
        return 2
    if command == "build":
        return _build(rest)
    return _dispatch(command, rest)


if __name__ == "__main__":
    sys.exit(main())
