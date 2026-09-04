from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import Field, model_validator

from cogito.domain.base import DomainModel
from cogito.domain.enums import GapStatus
from cogito.domain.ids import EpisodeId, GapId, HypothesisId


NonEmpty = Annotated[str, Field(min_length=1)]


class InformationGap(DomainModel):
    id: GapId
    episode_id: EpisodeId
    question: NonEmpty
    why_it_matters: NonEmpty
    target_hypothesis_id: HypothesisId | None = None
    source_hint: str | None = None
    status: GapStatus = GapStatus.OPEN
    created_at: datetime
    resolved_at: datetime | None = None

    @model_validator(mode="after")
    def resolved_time_matches_status(self) -> "InformationGap":
        if self.status is GapStatus.RESOLVED and self.resolved_at is None:
            raise ValueError("resolved gaps require resolved_at")
        if self.status is not GapStatus.RESOLVED and self.resolved_at is not None:
            raise ValueError("only resolved gaps may have resolved_at")
        return self

