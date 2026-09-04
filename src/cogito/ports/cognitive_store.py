from __future__ import annotations

from typing import Protocol

from cogito.domain.ids import EpisodeId
from cogito.domain.models.episode import Episode, EpisodeState
from cogito.domain.models.event import CognitiveEvent, CognitiveTransaction
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.goal import GoalContract


class CognitiveStoreError(RuntimeError):
    pass


class EpisodeNotFound(CognitiveStoreError):
    pass


class CognitiveVersionConflict(CognitiveStoreError):
    pass


class ObjectAlreadyExists(CognitiveStoreError):
    pass


class CognitiveStore(Protocol):
    async def create_episode(self, episode: Episode) -> Episode: ...

    async def load_episode_state(self, episode_id: EpisodeId) -> EpisodeState: ...

    async def commit_transaction(self, transaction: CognitiveTransaction) -> Episode: ...

    async def append_goal_contract_version(
        self, episode_id: EpisodeId, goal_contract: GoalContract
    ) -> None: ...

    async def list_goal_contract_versions(
        self, episode_id: EpisodeId
    ) -> tuple[GoalContract, ...]: ...

    async def list_events(self, episode_id: EpisodeId) -> tuple[CognitiveEvent, ...]: ...

    async def list_relations(self, episode_id: EpisodeId) -> tuple[EvidenceLink, ...]: ...

