from __future__ import annotations

from datetime import datetime
from typing import Annotated, TypeAlias

from pydantic import Field, model_validator

from cogito.domain.base import DomainModel
from cogito.domain.enums import ChangeKind, CognitiveObjectType, EventType
from cogito.domain.ids import EpisodeId, EventId, TransactionId
from cogito.domain.models.action import ActionDecision
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import Observation, ObservedProposition


CognitiveObject: TypeAlias = (
    Observation | ObservedProposition | Fact | Hypothesis | InformationGap | ActionDecision
)


class CognitiveEvent(DomainModel):
    """Immutable envelope for one ordered entry in an episode's event history."""

    id: EventId
    episode_id: EpisodeId
    transaction_id: TransactionId
    sequence: int = Field(ge=1)
    event_type: EventType
    cause_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class ObjectChange(DomainModel):
    kind: ChangeKind
    object_type: CognitiveObjectType
    object_id: Annotated[str, Field(min_length=1)]
    value: CognitiveObject

    @model_validator(mode="after")
    def identity_matches_value(self) -> "ObjectChange":
        if self.object_id != str(self.value.id):
            raise ValueError("object_id must match value.id")
        expected = {
            Observation: CognitiveObjectType.OBSERVATION,
            ObservedProposition: CognitiveObjectType.PROPOSITION,
            Fact: CognitiveObjectType.FACT,
            Hypothesis: CognitiveObjectType.HYPOTHESIS,
            InformationGap: CognitiveObjectType.INFORMATION_GAP,
            ActionDecision: CognitiveObjectType.ACTION,
        }[type(self.value)]
        if self.object_type is not expected:
            raise ValueError("object_type does not match value")
        return self


class RelationChange(DomainModel):
    kind: ChangeKind
    value: EvidenceLink


class CognitiveTransaction(DomainModel):
    """Validated commit intent guarded by the episode's ``base_version``."""

    id: TransactionId
    episode_id: EpisodeId
    base_version: int = Field(ge=0)
    events: tuple[CognitiveEvent, ...] = ()
    object_changes: tuple[ObjectChange, ...] = ()
    relation_changes: tuple[RelationChange, ...] = ()

    @model_validator(mode="after")
    def envelope_is_consistent(self) -> "CognitiveTransaction":
        if not (self.events or self.object_changes or self.relation_changes):
            raise ValueError("transaction must contain at least one cognitive change")
        for event in self.events:
            if event.episode_id != self.episode_id or event.transaction_id != self.id:
                raise ValueError("event envelope does not match transaction")
        for change in self.object_changes:
            if change.value.episode_id != self.episode_id:
                raise ValueError("object change belongs to another episode")
        for change in self.relation_changes:
            if change.value.episode_id != self.episode_id:
                raise ValueError("relation change belongs to another episode")
        return self
