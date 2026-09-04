from __future__ import annotations

from sqlalchemy import create_engine, inspect, text
from typer.testing import CliRunner

from cogito.interfaces.cli.app import app


runner = CliRunner()


def test_cli_init_create_and_show_episode(tmp_path, monkeypatch) -> None:
    database = tmp_path / "cli.db"
    monkeypatch.setenv("COGITO_SQLITE_PATH", str(database))

    initialized = runner.invoke(app, ["init"])
    initialized_again = runner.invoke(app, ["init"])

    engine = create_engine(f"sqlite:///{database.as_posix()}")
    try:
        tables = set(inspect(engine).get_table_names())
        with engine.connect() as connection:
            migration_version = connection.scalar(
                text("SELECT version_num FROM alembic_version")
            )
    finally:
        engine.dispose()

    created = runner.invoke(
        app,
        [
            "episode", "create", "--goal", "diagnose DB connectivity",
            "--constraint", "read only", "--criterion", "identify root cause",
        ],
    )

    assert initialized.exit_code == 0
    assert initialized_again.exit_code == 0
    assert "alembic_version" in tables
    assert migration_version == "0001_story0"
    assert created.exit_code == 0
    episode_id = created.stdout.strip().split()[-1]
    shown = runner.invoke(app, ["episode", "show", episode_id])
    assert shown.exit_code == 0
    assert "diagnose DB connectivity" in shown.stdout
    assert "Cognitive Version" in shown.stdout
