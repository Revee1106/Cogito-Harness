from typing import Annotated, Any

from pydantic import Field, model_validator

from cogito.domain.base import ProposalModel
from cogito.domain.enums import ActionKind, ActionRisk
from cogito.domain.ids import GapId


class ActionProposal(ProposalModel):
    kind: ActionKind
    target_gap_id: GapId | None = None
    purpose: Annotated[str, Field(min_length=1)]
    expected_observation: str | None = None
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    risk: ActionRisk

    @model_validator(mode="after")
    def tool_actions_name_a_tool(self) -> "ActionProposal":
        if self.kind is ActionKind.TOOL and not self.tool_name:
            raise ValueError("tool action proposals require tool_name")
        return self

