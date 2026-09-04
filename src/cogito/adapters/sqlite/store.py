from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from cogito.adapters.sqlite.mappers import (
    episode_from_record,
    episode_to_record,
    event_from_record,
    event_to_record,
    goal_from_record,
    goal_to_record,
    object_from_record,
    object_to_record,
    relation_from_record,
    relation_to_record,
)
from cogito.adapters.sqlite.orm import (
    Base,
    CognitiveEventRecord,
    CognitiveObjectRecord,
    CognitiveRelationRecord,
    EpisodeRecord,
    GoalContractRecord,
)
from cogito.domain.enums import ChangeKind, CognitiveObjectType, GapStatus
from cogito.domain.ids import EpisodeId
from cogito.domain.models.action import ActionDecision
from cogito.domain.models.episode import Episode, EpisodeState
from cogito.domain.models.event import CognitiveEvent, CognitiveTransaction
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.goal import GoalContract
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import Observation
from cogito.ports.cognitive_store import (
    CognitiveStoreError,
    CognitiveVersionConflict,
    EpisodeNotFound,
    ObjectAlreadyExists,
)


class SQLiteCognitiveStore:
    """SQLAlchemy-backed port adapter that returns domain objects only."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(
            f"sqlite:///{self.path.as_posix()}", poolclass=NullPool
        )
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def close(self) -> None:
        self.engine.dispose()

    async def create_episode(self, episode: Episode) -> Episode:
        try:
            with self._sessions.begin() as session:
                session.add(episode_to_record(episode))
        except IntegrityError as error:
            raise CognitiveStoreError(f"episode already exists: {episode.id}") from error
        return episode

    async def append_goal_contract_version(
        self, episode_id: EpisodeId, goal_contract: GoalContract
    ) -> None:
        try:
            with self._sessions.begin() as session:
                episode = self._episode_record(session, episode_id)
                expected_version = episode.goal_contract_version + 1
                if goal_contract.version != expected_version:
                    raise CognitiveStoreError(
                        f"goal contract version must be {expected_version}, got {goal_contract.version}"
                    )
                session.add(goal_to_record(episode_id, goal_contract, datetime.now(UTC)))
                episode.goal_contract_version = goal_contract.version
                episode.updated_at = datetime.now(UTC)
        except IntegrityError as error:
            raise CognitiveStoreError("goal contract version already exists") from error

    async def load_episode_state(self, episode_id: EpisodeId) -> EpisodeState:
        with self._sessions() as session:
            record = self._episode_record(session, episode_id)
            episode = episode_from_record(record)
            goal = None
            if record.goal_contract_version:
                goal_record = session.get(
                    GoalContractRecord,
                    {"episode_id": str(episode_id), "version": record.goal_contract_version},
                )
                if goal_record is not None:
                    goal = goal_from_record(goal_record)
            records = session.scalars(
                select(CognitiveObjectRecord)
                .where(CognitiveObjectRecord.episode_id == str(episode_id))
                .order_by(CognitiveObjectRecord.created_at, CognitiveObjectRecord.id)
            ).all()
            objects = tuple(object_from_record(item) for item in records)

        facts = tuple(item for item in objects if isinstance(item, Fact))
        hypotheses = tuple(item for item in objects if isinstance(item, Hypothesis))
        gaps = tuple(item for item in objects if isinstance(item, InformationGap))
        focused = next((item.id for item in gaps if item.status is GapStatus.FOCUSED), None)
        observations = tuple(item for item in objects if isinstance(item, Observation))
        actions = tuple(item for item in objects if isinstance(item, ActionDecision))
        return EpisodeState(
            episode=episode,
            goal_contract=goal,
            facts=facts,
            hypotheses=hypotheses,
            gaps=gaps,
            focused_gap_id=focused,
            recent_observations=observations,
            recent_actions=actions,
        )

    async def commit_transaction(self, transaction: CognitiveTransaction) -> Episode:
        try:
            with self._sessions.begin() as session:
                episode = self._episode_record(session, transaction.episode_id)
                if episode.cognitive_version != transaction.base_version:
                    raise CognitiveVersionConflict(
                        f"base version {transaction.base_version} does not match "
                        f"current version {episode.cognitive_version}"
                    )
                self._append_events(session, transaction)
                self._apply_object_changes(session, transaction)
                self._apply_relation_changes(session, transaction)
                episode.cognitive_version += 1
                episode.updated_at = datetime.now(UTC)
                session.flush()
                committed = episode_from_record(episode)
        except IntegrityError as error:
            raise CognitiveStoreError("transaction violates persistence constraints") from error
        return committed

    async def list_goal_contract_versions(
        self, episode_id: EpisodeId
    ) -> tuple[GoalContract, ...]:
        with self._sessions() as session:
            records = session.scalars(
                select(GoalContractRecord)
                .where(GoalContractRecord.episode_id == str(episode_id))
                .order_by(GoalContractRecord.version)
            ).all()
            return tuple(goal_from_record(item) for item in records)

    async def list_events(self, episode_id: EpisodeId) -> tuple[CognitiveEvent, ...]:
        with self._sessions() as session:
            records = session.scalars(
                select(CognitiveEventRecord)
                .where(CognitiveEventRecord.episode_id == str(episode_id))
                .order_by(CognitiveEventRecord.sequence)
            ).all()
            return tuple(event_from_record(item) for item in records)

    async def list_relations(self, episode_id: EpisodeId) -> tuple[EvidenceLink, ...]:
        with self._sessions() as session:
            records = session.scalars(
                select(CognitiveRelationRecord)
                .where(CognitiveRelationRecord.episode_id == str(episode_id))
                .order_by(CognitiveRelationRecord.created_at, CognitiveRelationRecord.id)
            ).all()
            return tuple(relation_from_record(item) for item in records)

    @staticmethod
    def _episode_record(session: Session, episode_id: EpisodeId) -> EpisodeRecord:
        record = session.get(EpisodeRecord, str(episode_id))
        if record is None:
            raise EpisodeNotFound(str(episode_id))
        return record

    @staticmethod
    def _append_events(session: Session, transaction: CognitiveTransaction) -> None:
        last_sequence = session.scalar(
            select(func.max(CognitiveEventRecord.sequence)).where(
                CognitiveEventRecord.episode_id == str(transaction.episode_id)
            )
        ) or 0
        expected = list(range(last_sequence + 1, last_sequence + len(transaction.events) + 1))
        actual = [event.sequence for event in transaction.events]
        if actual != expected:
            raise CognitiveStoreError(
                f"event sequences must append contiguously after {last_sequence}: {actual}"
            )
        session.add_all(event_to_record(event) for event in transaction.events)

    @staticmethod
    def _apply_object_changes(session: Session, transaction: CognitiveTransaction) -> None:
        for change in transaction.object_changes:
            current = session.get(CognitiveObjectRecord, change.object_id)
            if change.kind is ChangeKind.CREATE:
                if current is not None:
                    raise ObjectAlreadyExists(change.object_id)
                session.add(object_to_record(change.object_type, change.value, version=1))
                continue
            if current is None:
                raise CognitiveStoreError(f"cannot update missing object: {change.object_id}")
            if current.episode_id != str(transaction.episode_id):
                raise CognitiveStoreError("cannot update an object from another episode")
            replacement = object_to_record(
                CognitiveObjectType(current.object_type), change.value, version=current.version + 1
            )
            current.status = replacement.status
            current.version = replacement.version
            current.payload_json = replacement.payload_json
            current.updated_at = replacement.updated_at

    @staticmethod
    def _apply_relation_changes(session: Session, transaction: CognitiveTransaction) -> None:
        for change in transaction.relation_changes:
            relation_id = str(change.value.id)
            current = session.get(CognitiveRelationRecord, relation_id)
            if change.kind is ChangeKind.CREATE:
                if current is not None:
                    raise ObjectAlreadyExists(relation_id)
                session.add(relation_to_record(change.value))
                continue
            if current is None:
                raise CognitiveStoreError(f"cannot update missing relation: {relation_id}")
            replacement = relation_to_record(change.value)
            current.source_id = replacement.source_id
            current.target_id = replacement.target_id
            current.relation_type = replacement.relation_type
            current.payload_json = replacement.payload_json
