"""wikimind entry point: ``python3 -m wikimind <command> [args...]``.

Thin wrapper — all dispatch lives in ``wikimind.cli`` (one
dispatcher for the whole pipeline, including ``build``), so this file
only forwards argv to ``cli.main``.
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
