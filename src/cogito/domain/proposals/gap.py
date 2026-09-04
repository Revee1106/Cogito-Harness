from typing import Annotated

from pydantic import Field

from cogito.domain.base import ProposalModel
from cogito.domain.ids import HypothesisId


NonEmpty = Annotated[str, Field(min_length=1)]


class GapProposal(ProposalModel):
    question: NonEmpty
    why_it_matters: NonEmpty
    target_hypothesis_id: HypothesisId | None = None
    source_hint: str | None = None

