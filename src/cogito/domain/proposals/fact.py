from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from pydantic import Field, model_validator

from cogito.domain.base import ProposalModel
from cogito.domain.enums import FactBasis, SemanticEntailment
from cogito.domain.ids import PropositionId


NonEmpty = Annotated[str, Field(min_length=1)]


class FactProposal(ProposalModel):
    proposition_id: PropositionId
    statement: NonEmpty
    subject: str | None = None
    predicate: str | None = None
    value: Any | None = None
    scope: str | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    basis: FactBasis
    semantic_entailment: SemanticEntailment

    @model_validator(mode="after")
    def temporal_range_is_ordered(self) -> "FactProposal":
        if (
            self.valid_from is not None
            and self.valid_to is not None
            and self.valid_to < self.valid_from
        ):
            raise ValueError("valid_to must not precede valid_from")
        return self
