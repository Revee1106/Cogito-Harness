from typing import Annotated, Any

from pydantic import Field

from cogito.domain.base import ProposalModel
from cogito.domain.ids import ObservationId


class ObservedPropositionProposal(ProposalModel):
    observation_id: ObservationId
    statement: Annotated[str, Field(min_length=1)]
    subject: str | None = None
    predicate: str | None = None
    value: Any | None = None
    scope: str | None = None

