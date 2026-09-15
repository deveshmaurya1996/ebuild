# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project

"""Recreate a static archive for Ninja's ar_rule.

``ar rcs $out $in`` updates an existing archive: it replaces or adds the
members named in ``$in``, but keeps any other members already present. After a
source is removed from a static_library target, an incremental rebuild can
therefore leave the old ``.o`` inside ``$out``.

Ninja invokes this script by absolute path as::

    python /path/to/recreate_archive.py $out $ar rcs $out $in

so the archive is deleted first and then rebuilt from the current object list.
A Python helper is used instead of ``rm`` so the same rule works on Windows.
The script is run by path (not ``python -m``) so a source checkout that only
puts ebuild on ``PYTHONPATH`` still builds static libraries.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _resolve_archiver(archiver: str) -> str | None:
    """Return a runnable archiver path, or None if it cannot be executed."""
    if os.path.isfile(archiver) and os.access(archiver, os.X_OK):
        return archiver
    return shutil.which(archiver)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 4:
        print(
            "ebuild: recreate_archive: expected $out $ar rcs $out …members",
            file=sys.stderr,
        )
        return 2

    archive = Path(args[0])
    archiver = args[1]
    # Refuse to destroy a good archive when the archiver cannot run.
    if _resolve_archiver(archiver) is None:
        print(f"ebuild: cannot run archiver {archiver}: not found", file=sys.stderr)
        return 1

    try:
        archive.unlink(missing_ok=True)
    except OSError as exc:
        print(f"ebuild: cannot remove archive {archive}: {exc}", file=sys.stderr)
        return 1

    try:
        return subprocess.call(args[1:])
    except OSError as exc:
        print(f"ebuild: cannot run archiver {archiver}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
