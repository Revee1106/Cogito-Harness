from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import Field

from cogito.domain.base import DomainModel
from cogito.domain.enums import CognitiveTargetType, EvidenceRelation
from cogito.domain.ids import EpisodeId, EvidenceLinkId, PropositionId


class EvidenceLink(DomainModel):
    id: EvidenceLinkId
    episode_id: EpisodeId
    proposition_id: PropositionId
    target_type: CognitiveTargetType
    target_id: Annotated[str, Field(min_length=1)]
    relation: EvidenceRelation
    reason: Annotated[str, Field(min_length=1)]
    created_at: datetime

