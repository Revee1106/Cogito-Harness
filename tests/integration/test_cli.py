from __future__ import annotations

from typer.testing import CliRunner

from cogito.interfaces.cli.app import app


runner = CliRunner()


def test_cli_init_create_and_show_episode(tmp_path, monkeypatch) -> None:
    database = tmp_path / "cli.db"
    monkeypatch.setenv("COGITO_SQLITE_PATH", str(database))

    initialized = runner.invoke(app, ["init"])
    created = runner.invoke(
        app,
        [
            "episode", "create", "--goal", "diagnose DB connectivity",
            "--constraint", "read only", "--criterion", "identify root cause",
        ],
    )

    assert initialized.exit_code == 0
    assert created.exit_code == 0
    episode_id = created.stdout.strip().split()[-1]
    shown = runner.invoke(app, ["episode", "show", episode_id])
    assert shown.exit_code == 0
    assert "diagnose DB connectivity" in shown.stdout
    assert "Cognitive Version" in shown.stdout

