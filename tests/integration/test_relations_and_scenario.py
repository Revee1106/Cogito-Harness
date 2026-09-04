from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from cogito.adapters.sqlite.store import SQLiteCognitiveStore
from cogito.adapters.tools.fake import FakeToolExecutor
from cogito.application.runtime import action_result_to_observation
from cogito.domain.enums import (
    ActionKind,
    ActionRisk,
    ChangeKind,
    CognitiveObjectType,
    CognitiveTargetType,
    EpisodeStatus,
    EvidenceRelation,
    EventType,
    HypothesisStatus,
)
from cogito.domain.ids import (
    ActionId,
    EpisodeId,
    EvidenceLinkId,
    EventId,
    HypothesisId,
    ObservationId,
    PropositionId,
    TransactionId,
)
from cogito.domain.models.action import ActionDecision
from cogito.domain.models.episode import Episode
from cogito.domain.models.event import CognitiveEvent, CognitiveTransaction, ObjectChange, RelationChange
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.goal import AcceptanceCriterion, GoalContract
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import ObservedProposition


NOW = datetime(2026, 1, 1, tzinfo=UTC)


def test_relation_direction_is_source_relation_target(tmp_path) -> None:
    store = SQLiteCognitiveStore(tmp_path / "relations.db")
    store.create_schema()
    episode = Episode(
        id=EpisodeId("ep-rel"), status=EpisodeStatus.ACTIVE, cognitive_version=0,
        goal_contract_version=0, created_at=NOW, updated_at=NOW,
    )
    relation = EvidenceLink(
        id=EvidenceLinkId("el1"), episode_id=episode.id,
        proposition_id=PropositionId("p1"), target_type=CognitiveTargetType.HYPOTHESIS,
        target_id=str(HypothesisId("h1")), relation=EvidenceRelation.SUPPORTS,
        reason="fixture", created_at=NOW,
    )
    proposition = ObservedProposition(
        id=PropositionId("p1"), episode_id=episode.id,
        observation_id=ObservationId("o1"), statement="observed listener mismatch",
        observed_at=NOW, created_at=NOW,
    )
    hypothesis = Hypothesis(
        id=HypothesisId("h1"), episode_id=episode.id,
        statement="endpoint mismatch contributes to failure",
        target_problem="DB connectivity", evidence_refs=(relation.id,),
        prediction="using the listener endpoint removes refusal",
        status=HypothesisStatus.PLAUSIBLE, created_at=NOW, updated_at=NOW,
    )
    tx_id = TransactionId("tx-rel")
    tx = CognitiveTransaction(
        id=tx_id, episode_id=episode.id, base_version=0,
        events=(CognitiveEvent(
            id=EventId("ev-rel"), episode_id=episode.id, transaction_id=tx_id,
            sequence=1, event_type=EventType.EVIDENCE_LINK_ADMITTED,
            payload={"relation_id": "el1"}, created_at=NOW,
        ),),
        object_changes=(
            ObjectChange(
                kind=ChangeKind.CREATE, object_type=CognitiveObjectType.PROPOSITION,
                object_id=str(proposition.id), value=proposition,
            ),
            ObjectChange(
                kind=ChangeKind.CREATE, object_type=CognitiveObjectType.HYPOTHESIS,
                object_id=str(hypothesis.id), value=hypothesis,
            ),
        ),
        relation_changes=(RelationChange(kind=ChangeKind.CREATE, value=relation),),
    )
    asyncio.run(store.create_episode(episode))
    asyncio.run(store.commit_transaction(tx))

    rows = asyncio.run(store.list_relations(episode.id))

    assert rows == (relation,)
    assert rows[0].proposition_id == PropositionId("p1")
    assert rows[0].target_id == "h1"


def test_fake_runtime_action_result_becomes_observation_then_persists(tmp_path) -> None:
    store = SQLiteCognitiveStore(tmp_path / "scenario.db")
    store.create_schema()
    episode = Episode(
        id=EpisodeId("ep-scenario"), status=EpisodeStatus.ACTIVE,
        cognitive_version=0, goal_contract_version=0, created_at=NOW, updated_at=NOW,
    )
    goal = GoalContract(
        objective="diagnose DB connectivity problem",
        hard_constraints=("read only",),
        acceptance_criteria=(AcceptanceCriterion(id="c1", statement="identify port mismatch"),),
        version=1,
    )
    action = ActionDecision(
        id=ActionId("a-inspect"), episode_id=episode.id, kind=ActionKind.TOOL,
        purpose="inspect listener", expected_observation="listener port",
        tool_name="inspect_listener", arguments={}, risk=ActionRisk.READ_ONLY,
        created_at=NOW,
    )
    executor = FakeToolExecutor.success(
        responses={"inspect_listener": "DB listens on 3307"}, clock=lambda: NOW
    )
    asyncio.run(store.create_episode(episode))
    asyncio.run(store.append_goal_contract_version(episode.id, goal))

    result = asyncio.run(executor.execute(action))
    observation = action_result_to_observation(result, episode.id, observed_at=NOW, created_at=NOW)
    tx_id = TransactionId("tx-scenario")
    transaction = CognitiveTransaction(
        id=tx_id, episode_id=episode.id, base_version=0,
        events=(CognitiveEvent(
            id=EventId("ev-scenario"), episode_id=episode.id, transaction_id=tx_id,
            sequence=1, event_type=EventType.OBSERVATION_ADDED,
            cause_id=str(action.id), payload={"object_id": str(observation.id)}, created_at=NOW,
        ),),
        object_changes=(ObjectChange(
            kind=ChangeKind.CREATE, object_type=CognitiveObjectType.OBSERVATION,
            object_id=str(observation.id), value=observation,
        ),),
        relation_changes=(),
    )
    asyncio.run(store.commit_transaction(transaction))
    state = asyncio.run(store.load_episode_state(episode.id))

    assert result.raw_output == "DB listens on 3307"
    assert state.recent_observations[0].raw_content == "DB listens on 3307"
    assert state.recent_observations[0].source == "action-result:a-inspect"

