from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def upgrade_database(path: str | Path) -> None:
    """Upgrade a runtime SQLite database to the repository's Alembic head."""

    database_path = Path(path).resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")
    command.upgrade(config, "head")
