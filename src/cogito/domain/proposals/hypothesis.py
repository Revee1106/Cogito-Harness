from typing import Annotated

from pydantic import Field

from cogito.domain.base import ProposalModel
from cogito.domain.ids import PropositionId


NonEmpty = Annotated[str, Field(min_length=1)]


class HypothesisProposal(ProposalModel):
    statement: NonEmpty
    target_problem: NonEmpty
    supporting_proposition_ids: tuple[PropositionId, ...]
    prediction: str | None = None
    disconfirming_condition: str | None = None

