from __future__ import annotations

from datetime import datetime

from pydantic import Field

from cogito.domain.base import DomainModel
from cogito.domain.enums import EpisodeStatus, TurnResolutionKind
from cogito.domain.ids import EpisodeId, GapId
from cogito.domain.models.action import ActionDecision
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.goal import GoalContract
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import Observation


class Episode(DomainModel):
    id: EpisodeId
    status: EpisodeStatus
    cognitive_version: int = Field(ge=0)
    goal_contract_version: int = Field(ge=0)
    created_at: datetime
    updated_at: datetime


class EpisodeState(DomainModel):
    """Rebuildable read model; committed objects and events remain the truth sources."""

    episode: Episode
    goal_contract: GoalContract | None = None
    facts: tuple[Fact, ...] = ()
    hypotheses: tuple[Hypothesis, ...] = ()
    gaps: tuple[InformationGap, ...] = ()
    focused_gap_id: GapId | None = None
    recent_observations: tuple[Observation, ...] = ()
    recent_actions: tuple[ActionDecision, ...] = ()


class TurnResolution(DomainModel):
    kind: TurnResolutionKind
    why_stop: str
    focused_gap_id: GapId | None = None
    action: ActionDecision | None = None
    message: str | None = None
