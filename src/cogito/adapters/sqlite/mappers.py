from __future__ import annotations

from datetime import UTC, datetime
import json

from cogito.adapters.sqlite.orm import (
    CognitiveEventRecord,
    CognitiveObjectRecord,
    CognitiveRelationRecord,
    EpisodeRecord,
    GoalContractRecord,
)
from cogito.domain.enums import CognitiveObjectType
from cogito.domain.ids import EpisodeId, EventId, TransactionId
from cogito.domain.models.action import ActionDecision
from cogito.domain.models.episode import Episode
from cogito.domain.models.event import CognitiveEvent, CognitiveObject
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.goal import GoalContract
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import Observation, ObservedProposition


OBJECT_MODELS = {
    CognitiveObjectType.OBSERVATION: Observation,
    CognitiveObjectType.PROPOSITION: ObservedProposition,
    CognitiveObjectType.FACT: Fact,
    CognitiveObjectType.HYPOTHESIS: Hypothesis,
    CognitiveObjectType.INFORMATION_GAP: InformationGap,
    CognitiveObjectType.ACTION: ActionDecision,
}


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def episode_to_record(episode: Episode) -> EpisodeRecord:
    return EpisodeRecord(
        id=str(episode.id),
        status=episode.status.value,
        cognitive_version=episode.cognitive_version,
        goal_contract_version=episode.goal_contract_version,
        created_at=episode.created_at,
        updated_at=episode.updated_at,
    )


def episode_from_record(record: EpisodeRecord) -> Episode:
    return Episode(
        id=EpisodeId(record.id),
        status=record.status,
        cognitive_version=record.cognitive_version,
        goal_contract_version=record.goal_contract_version,
        created_at=_as_utc(record.created_at),
        updated_at=_as_utc(record.updated_at),
    )


def goal_to_record(episode_id: EpisodeId, goal: GoalContract, created_at: datetime) -> GoalContractRecord:
    return GoalContractRecord(
        episode_id=str(episode_id),
        version=goal.version,
        payload_json=goal.model_dump_json(),
        created_at=created_at,
    )


def goal_from_record(record: GoalContractRecord) -> GoalContract:
    return GoalContract.model_validate_json(record.payload_json)


def event_to_record(event: CognitiveEvent) -> CognitiveEventRecord:
    return CognitiveEventRecord(
        id=str(event.id),
        episode_id=str(event.episode_id),
        transaction_id=str(event.transaction_id),
        sequence=event.sequence,
        event_type=event.event_type.value,
        cause_id=event.cause_id,
        payload_json=event.model_dump_json(include={"payload"}),
        created_at=event.created_at,
    )


def event_from_record(record: CognitiveEventRecord) -> CognitiveEvent:
    return CognitiveEvent(
        id=EventId(record.id),
        episode_id=EpisodeId(record.episode_id),
        transaction_id=TransactionId(record.transaction_id),
        sequence=record.sequence,
        event_type=record.event_type,
        cause_id=record.cause_id,
        payload=json.loads(record.payload_json)["payload"],
        created_at=_as_utc(record.created_at),
    )


def object_to_record(
    object_type: CognitiveObjectType,
    value: CognitiveObject,
    *,
    version: int,
) -> CognitiveObjectRecord:
    status = getattr(value, "status", "ACTIVE")
    status_value = status.value if hasattr(status, "value") else str(status)
    created_at = value.created_at
    updated_at = getattr(value, "updated_at", created_at)
    return CognitiveObjectRecord(
        id=str(value.id),
        episode_id=str(value.episode_id),
        object_type=object_type.value,
        status=status_value,
        version=version,
        payload_json=value.model_dump_json(),
        created_at=created_at,
        updated_at=updated_at,
    )


def object_from_record(record: CognitiveObjectRecord) -> CognitiveObject:
    model = OBJECT_MODELS[CognitiveObjectType(record.object_type)]
    return model.model_validate_json(record.payload_json)


def relation_to_record(value: EvidenceLink) -> CognitiveRelationRecord:
    return CognitiveRelationRecord(
        id=str(value.id),
        episode_id=str(value.episode_id),
        source_id=str(value.proposition_id),
        target_id=value.target_id,
        relation_type=value.relation.value,
        payload_json=value.model_dump_json(),
        created_at=value.created_at,
    )


def relation_from_record(record: CognitiveRelationRecord) -> EvidenceLink:
    return EvidenceLink.model_validate_json(record.payload_json)
