from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from pydantic import Field

from cogito.domain.base import DomainModel
from cogito.domain.enums import PropositionStatus
from cogito.domain.ids import EpisodeId, ObservationId, PropositionId


NonEmpty = Annotated[str, Field(min_length=1)]


class Observation(DomainModel):
    id: ObservationId
    episode_id: EpisodeId
    source: NonEmpty
    raw_content: NonEmpty
    scope: str | None = None
    source_ref: str | None = None
    observed_at: datetime
    created_at: datetime


class ObservedProposition(DomainModel):
    id: PropositionId
    episode_id: EpisodeId
    observation_id: ObservationId
    statement: NonEmpty
    subject: str | None = None
    predicate: str | None = None
    value: Any | None = None
    scope: str | None = None
    observed_at: datetime | None = None
    status: PropositionStatus = PropositionStatus.ACTIVE
    created_at: datetime

