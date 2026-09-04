from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest

from cogito.adapters.llm.fake import FakeModelProvider
from cogito.adapters.tools.fake import FakeToolExecutor
from cogito.domain.enums import ActionKind, ActionRisk, ActionResultStatus
from cogito.domain.ids import ActionId, EpisodeId
from cogito.domain.models.action import ActionDecision
from cogito.domain.proposals.gap import GapProposal
from cogito.ports.model_provider import ModelRequest, UnknownModelResponse


NOW = datetime(2026, 1, 1, tzinfo=UTC)


def test_fake_model_provider_returns_configured_proposal_and_records_request() -> None:
    proposal = GapProposal(question="Which port?", why_it_matters="diagnosis")
    provider = FakeModelProvider({"listener-gap": proposal})
    request = ModelRequest(role="gap_contextualizer", input_key="listener-gap", context={})

    result = asyncio.run(provider.propose(request, GapProposal))

    assert result == proposal
    assert provider.received_requests == [request]


def test_fake_model_provider_rejects_unknown_input() -> None:
    provider = FakeModelProvider({})
    request = ModelRequest(role="test", input_key="missing", context={})

    with pytest.raises(UnknownModelResponse):
        asyncio.run(provider.propose(request, GapProposal))


def test_fake_tool_executor_never_executes_external_command() -> None:
    action = ActionDecision(
        id=ActionId("a1"), episode_id=EpisodeId("ep1"), kind=ActionKind.TOOL,
        purpose="inspect listener", expected_observation="port",
        tool_name="inspect_listener", arguments={"host": "localhost"},
        risk=ActionRisk.READ_ONLY, created_at=NOW,
    )
    executor = FakeToolExecutor.success(
        responses={"inspect_listener": "DB listens on 3307"}, clock=lambda: NOW
    )

    result = asyncio.run(executor.execute(action))

    assert result.status is ActionResultStatus.SUCCESS
    assert result.raw_output == "DB listens on 3307"
    assert executor.received_actions == [action]


def test_fake_tool_executor_can_be_configured_to_fail() -> None:
    action = ActionDecision(
        id=ActionId("a2"), episode_id=EpisodeId("ep1"), kind=ActionKind.TOOL,
        purpose="inspect listener", tool_name="inspect_listener", arguments={},
        risk=ActionRisk.READ_ONLY, created_at=NOW,
    )
    executor = FakeToolExecutor.failure(
        errors={"inspect_listener": "fixture failure"}, clock=lambda: NOW
    )

    result = asyncio.run(executor.execute(action))

    assert result.status is ActionResultStatus.FAILURE
    assert result.error == "fixture failure"

