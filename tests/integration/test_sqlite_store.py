from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest

from cogito.adapters.sqlite.store import SQLiteCognitiveStore
from cogito.domain.enums import (
    ChangeKind,
    CognitiveObjectType,
    EpisodeStatus,
    EventType,
)
from cogito.domain.ids import (
    EpisodeId,
    EventId,
    ObservationId,
    TransactionId,
)
from cogito.domain.models.episode import Episode
from cogito.domain.models.event import CognitiveEvent, CognitiveTransaction, ObjectChange
from cogito.domain.models.goal import AcceptanceCriterion, GoalContract
from cogito.domain.models.observation import Observation
from cogito.ports.cognitive_store import CognitiveVersionConflict, ObjectAlreadyExists


NOW = datetime(2026, 1, 1, tzinfo=UTC)


def make_store(tmp_path) -> SQLiteCognitiveStore:
    store = SQLiteCognitiveStore(tmp_path / "cogito.db")
    store.create_schema()
    return store


def make_episode() -> Episode:
    return Episode(
        id=EpisodeId("00000000-0000-0000-0000-000000000001"),
        status=EpisodeStatus.ACTIVE,
        cognitive_version=0,
        goal_contract_version=0,
        created_at=NOW,
        updated_at=NOW,
    )


def make_goal(version: int, objective: str = "diagnose DB connectivity") -> GoalContract:
    return GoalContract(
        objective=objective,
        hard_constraints=("read only",),
        acceptance_criteria=(AcceptanceCriterion(id="c1", statement="identify cause"),),
        version=version,
    )


def make_observation_tx(episode: Episode, observation: Observation, *, base_version: int = 0) -> CognitiveTransaction:
    tx_id = TransactionId(f"00000000-0000-0000-0000-00000000001{base_version}")
    event = CognitiveEvent(
        id=EventId(f"00000000-0000-0000-0000-00000000002{base_version}"),
        episode_id=episode.id,
        transaction_id=tx_id,
        sequence=base_version + 1,
        event_type=EventType.OBSERVATION_ADDED,
        payload={"object_id": str(observation.id)},
        created_at=NOW,
    )
    return CognitiveTransaction(
        id=tx_id,
        episode_id=episode.id,
        base_version=base_version,
        events=(event,),
        object_changes=(ObjectChange(
            kind=ChangeKind.CREATE,
            object_type=CognitiveObjectType.OBSERVATION,
            object_id=str(observation.id),
            value=observation,
        ),),
        relation_changes=(),
    )


def test_create_persist_commit_and_reload_episode_state(tmp_path) -> None:
    store = make_store(tmp_path)
    episode = make_episode()
    observation = Observation(
        id=ObservationId("00000000-0000-0000-0000-000000000002"),
        episode_id=episode.id,
        source="fixture", raw_content="DB listens on 3307",
        observed_at=NOW, created_at=NOW,
    )

    asyncio.run(store.create_episode(episode))
    asyncio.run(store.append_goal_contract_version(episode.id, make_goal(1)))
    committed = asyncio.run(store.commit_transaction(make_observation_tx(episode, observation)))
    state = asyncio.run(store.load_episode_state(episode.id))

    assert committed.cognitive_version == 1
    assert state.episode.cognitive_version == 1
    assert state.goal_contract == make_goal(1)
    assert state.recent_observations == (observation,)
    assert type(state.recent_observations[0]) is Observation


def test_goal_contract_version_history_is_retained(tmp_path) -> None:
    store = make_store(tmp_path)
    episode = make_episode()
    asyncio.run(store.create_episode(episode))
    asyncio.run(store.append_goal_contract_version(episode.id, make_goal(1)))
    asyncio.run(store.append_goal_contract_version(episode.id, make_goal(2, "diagnose safely")))

    history = asyncio.run(store.list_goal_contract_versions(episode.id))
    state = asyncio.run(store.load_episode_state(episode.id))

    assert [goal.version for goal in history] == [1, 2]
    assert state.goal_contract.objective == "diagnose safely"
    assert state.episode.goal_contract_version == 2


def test_version_conflict_rejects_transaction(tmp_path) -> None:
    store = make_store(tmp_path)
    episode = make_episode()
    observation = Observation(
        id=ObservationId("o-conflict"), episode_id=episode.id, source="fixture",
        raw_content="data", observed_at=NOW, created_at=NOW,
    )
    asyncio.run(store.create_episode(episode))
    asyncio.run(store.commit_transaction(make_observation_tx(episode, observation)))

    second = observation.model_copy(update={"id": ObservationId("o-second")})
    with pytest.raises(CognitiveVersionConflict):
        asyncio.run(store.commit_transaction(make_observation_tx(episode, second, base_version=0)))

    assert asyncio.run(store.load_episode_state(episode.id)).episode.cognitive_version == 1


def test_failed_transaction_rolls_back_events_objects_and_version(tmp_path) -> None:
    store = make_store(tmp_path)
    episode = make_episode()
    observation = Observation(
        id=ObservationId("duplicate"), episode_id=episode.id, source="fixture",
        raw_content="first", observed_at=NOW, created_at=NOW,
    )
    asyncio.run(store.create_episode(episode))
    asyncio.run(store.commit_transaction(make_observation_tx(episode, observation)))
    duplicate = observation.model_copy(update={"raw_content": "duplicate"})

    with pytest.raises(ObjectAlreadyExists):
        asyncio.run(store.commit_transaction(make_observation_tx(episode, duplicate, base_version=1)))

    state = asyncio.run(store.load_episode_state(episode.id))
    events = asyncio.run(store.list_events(episode.id))
    assert state.episode.cognitive_version == 1
    assert [item.raw_content for item in state.recent_observations] == ["first"]
    assert len(events) == 1


def test_event_order_is_traceable_and_append_only(tmp_path) -> None:
    store = make_store(tmp_path)
    episode = make_episode()
    asyncio.run(store.create_episode(episode))
    first = Observation(
        id=ObservationId("o1"), episode_id=episode.id, source="fixture",
        raw_content="first", observed_at=NOW, created_at=NOW,
    )
    second = first.model_copy(update={"id": ObservationId("o2"), "raw_content": "second"})
    asyncio.run(store.commit_transaction(make_observation_tx(episode, first, base_version=0)))
    asyncio.run(store.commit_transaction(make_observation_tx(episode, second, base_version=1)))

    events = asyncio.run(store.list_events(episode.id))

    assert [event.sequence for event in events] == [1, 2]
    assert [event.payload["object_id"] for event in events] == ["o1", "o2"]
    assert not hasattr(store, "delete_event")

