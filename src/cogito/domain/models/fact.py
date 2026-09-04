from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from pydantic import Field

from cogito.domain.base import DomainModel
from cogito.domain.enums import FactStatus
from cogito.domain.ids import EpisodeId, FactId, PropositionId


class Fact(DomainModel):
    id: FactId
    episode_id: EpisodeId
    statement: Annotated[str, Field(min_length=1)]
    subject: str | None = None
    predicate: str | None = None
    value: Any | None = None
    scope: str | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    evidence_refs: tuple[PropositionId, ...] = ()
    status: FactStatus = FactStatus.ACTIVE
    created_at: datetime

