from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import Field

from cogito.domain.base import DomainModel
from cogito.domain.enums import HypothesisStatus
from cogito.domain.ids import EpisodeId, EvidenceLinkId, HypothesisId


NonEmpty = Annotated[str, Field(min_length=1)]


class Hypothesis(DomainModel):
    """Committed hypothesis with at least one evidence reference.

    Story 1 admission will additionally verify that referenced evidence belongs
    to the current episode; keeping the reference mandatory prevents an
    evidence-free committed shape in Story 0.
    """

    id: HypothesisId
    episode_id: EpisodeId
    statement: NonEmpty
    target_problem: NonEmpty
    evidence_refs: Annotated[tuple[EvidenceLinkId, ...], Field(min_length=1)]
    prediction: str | None = None
    disconfirming_condition: str | None = None
    status: HypothesisStatus
    created_at: datetime
    updated_at: datetime
