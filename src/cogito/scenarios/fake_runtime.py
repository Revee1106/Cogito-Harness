from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path

from cogito.adapters.sqlite.store import SQLiteCognitiveStore
from cogito.adapters.tools.fake import FakeToolExecutor
from cogito.application.runtime import action_result_to_observation
from cogito.domain.enums import (
    ActionKind,
    ActionRisk,
    ChangeKind,
    CognitiveObjectType,
    EpisodeStatus,
    EventType,
)
from cogito.domain.ids import (
    ActionId,
    EpisodeId,
    EventId,
    TransactionId,
    new_id,
)
from cogito.domain.models.action import ActionDecision
from cogito.domain.models.episode import EpisodeState, Episode
from cogito.domain.models.event import CognitiveEvent, CognitiveTransaction, ObjectChange
from cogito.domain.models.goal import AcceptanceCriterion, GoalContract


async def run_fake_runtime_scenario(database_path: str | Path) -> EpisodeState:
    """Run ActionResult -> Observation -> Persist with no external calls."""

    now = datetime.now(UTC)
    store = SQLiteCognitiveStore(database_path)
    store.create_schema()
    episode = Episode(
        id=new_id(EpisodeId),
        status=EpisodeStatus.ACTIVE,
        cognitive_version=0,
        goal_contract_version=0,
        created_at=now,
        updated_at=now,
    )
    goal = GoalContract(
        objective="diagnose DB connectivity problem",
        hard_constraints=("read only",),
        acceptance_criteria=(
            AcceptanceCriterion(id="listener-port", statement="identify the listener port"),
        ),
        version=1,
    )
    action = ActionDecision(
        id=new_id(ActionId),
        episode_id=episode.id,
        kind=ActionKind.TOOL,
        purpose="inspect listener",
        expected_observation="DB listener port",
        tool_name="inspect_listener",
        arguments={},
        risk=ActionRisk.READ_ONLY,
        created_at=now,
    )
    executor = FakeToolExecutor.success(
        responses={"inspect_listener": "DB listens on 3307"}
    )

    try:
        await store.create_episode(episode)
        await store.append_goal_contract_version(episode.id, goal)
        result = await executor.execute(action)
        observation = action_result_to_observation(result, episode.id)
        transaction_id = new_id(TransactionId)
        transaction = CognitiveTransaction(
            id=transaction_id,
            episode_id=episode.id,
            base_version=0,
            events=(
                CognitiveEvent(
                    id=new_id(EventId),
                    episode_id=episode.id,
                    transaction_id=transaction_id,
                    sequence=1,
                    event_type=EventType.OBSERVATION_ADDED,
                    cause_id=str(action.id),
                    payload={"object_id": str(observation.id)},
                    created_at=now,
                ),
            ),
            object_changes=(
                ObjectChange(
                    kind=ChangeKind.CREATE,
                    object_type=CognitiveObjectType.OBSERVATION,
                    object_id=str(observation.id),
                    value=observation,
                ),
            ),
            relation_changes=(),
        )
        await store.commit_transaction(transaction)
        return await store.load_episode_state(episode.id)
    finally:
        store.close()


def main() -> None:
    state = asyncio.run(run_fake_runtime_scenario(Path(".cogito/scenario.db")))
    print(state.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
