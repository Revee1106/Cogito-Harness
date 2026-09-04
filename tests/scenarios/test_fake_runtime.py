from __future__ import annotations

import asyncio

import pytest

from cogito.scenarios.fake_runtime import run_fake_runtime_scenario


@pytest.mark.scenario
def test_story_zero_fake_runtime_scenario(tmp_path) -> None:
    state = asyncio.run(run_fake_runtime_scenario(tmp_path / "scenario.db"))

    assert state.goal_contract is not None
    assert state.goal_contract.objective == "diagnose DB connectivity problem"
    assert state.episode.cognitive_version == 1
    assert tuple(item.raw_content for item in state.recent_observations) == (
        "DB listens on 3307",
    )

