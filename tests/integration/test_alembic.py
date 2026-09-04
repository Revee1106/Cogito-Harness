from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_creates_exact_story_zero_tables(tmp_path) -> None:
    database = tmp_path / "migration.db"
    root = Path(__file__).resolve().parents[2]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")

    command.upgrade(config, "head")

    tables = set(inspect(create_engine(f"sqlite:///{database.as_posix()}")).get_table_names())
    assert tables == {
        "alembic_version",
        "episodes",
        "goal_contracts",
        "cognitive_events",
        "cognitive_objects",
        "cognitive_relations",
    }

