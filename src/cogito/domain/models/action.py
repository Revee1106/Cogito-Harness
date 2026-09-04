from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from pydantic import Field, model_validator

from cogito.domain.base import DomainModel
from cogito.domain.enums import ActionKind, ActionResultStatus, ActionRisk
from cogito.domain.ids import ActionId, EpisodeId, GapId


NonEmpty = Annotated[str, Field(min_length=1)]


class ActionDecision(DomainModel):
    id: ActionId
    episode_id: EpisodeId
    kind: ActionKind
    target_gap_id: GapId | None = None
    purpose: NonEmpty
    expected_observation: str | None = None
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    risk: ActionRisk
    created_at: datetime

    @model_validator(mode="after")
    def tool_actions_name_a_tool(self) -> "ActionDecision":
        if self.kind is ActionKind.TOOL and not self.tool_name:
            raise ValueError("tool actions require tool_name")
        if self.kind is not ActionKind.TOOL and self.tool_name is not None:
            raise ValueError("non-tool actions cannot name a tool")
        return self


class ActionResult(DomainModel):
    action_id: ActionId
    status: ActionResultStatus
    raw_output: str | None = None
    error: str | None = None
    started_at: datetime
    finished_at: datetime

    @model_validator(mode="after")
    def result_is_consistent(self) -> "ActionResult":
        if self.finished_at < self.started_at:
            raise ValueError("finished_at cannot precede started_at")
        if self.status is ActionResultStatus.FAILURE and not self.error:
            raise ValueError("failed actions require error")
        if self.status is ActionResultStatus.SUCCESS and self.error is not None:
            raise ValueError("successful actions cannot carry an error")
        return self

