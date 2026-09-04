from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


# CPython 3.14 applies mode=0o700 ACLs on Windows. On the managed workspace
# volume used by the test harness, that ACL makes the directory unreadable to
# the creating process. Pytest requests exactly 0o700 for its base temp folder,
# so translate only that test-process call; production code is unaffected.
if sys.platform == "win32" and sys.version_info >= (3, 14):
    _path_mkdir = Path.mkdir

    def _windows_test_mkdir(
        self: Path,
        mode: int = 0o777,
        parents: bool = False,
        exist_ok: bool = False,
    ) -> None:
        safe_mode = 0o777 if mode == 0o700 else mode
        _path_mkdir(self, mode=safe_mode, parents=parents, exist_ok=exist_ok)

    Path.mkdir = _windows_test_mkdir

