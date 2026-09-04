from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import create_engine, inspect, text

from cogito.scenarios.fake_runtime import run_fake_runtime_scenario


@pytest.mark.scenario
def test_story_zero_fake_runtime_scenario(tmp_path) -> None:
    database = tmp_path / "scenario.db"
    state = asyncio.run(run_fake_runtime_scenario(database))

    assert state.goal_contract is not None
    assert state.goal_contract.objective == "diagnose DB connectivity problem"
    assert state.episode.cognitive_version == 1
    assert tuple(item.raw_content for item in state.recent_observations) == (
        "DB listens on 3307",
    )

    engine = create_engine(f"sqlite:///{database.as_posix()}")
    try:
        assert "alembic_version" in inspect(engine).get_table_names()
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
                "0001_story0"
            )
    finally:
        engine.dispose()
