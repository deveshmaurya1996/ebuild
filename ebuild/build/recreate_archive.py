# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project

"""Recreate a static archive for Ninja's ar_rule.

``ar rcs $out $in`` updates an existing archive: it replaces or adds the
members named in ``$in``, but keeps any other members already present. After a
source is removed from a static_library target, an incremental rebuild can
therefore leave the old ``.o`` inside ``$out``.

Ninja invokes this module as::

    python -m ebuild.build.recreate_archive $out $ar rcs $out $in

so the archive is deleted first and then rebuilt from the current object list.
A Python helper is used instead of ``rm`` so the same rule works on Windows.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 4:
        print(
            "ebuild: recreate_archive: expected $out $ar rcs $out …members",
            file=sys.stderr,
        )
        return 2

    Path(args[0]).unlink(missing_ok=True)
    try:
        return subprocess.call(args[1:])
    except OSError as exc:
        print(f"ebuild: cannot run archiver {args[1]}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
