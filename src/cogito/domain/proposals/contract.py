from typing import Annotated

from pydantic import Field

from cogito.domain.base import ProposalModel


NonEmpty = Annotated[str, Field(min_length=1)]


class GoalInterpretationProposal(ProposalModel):
    objective: NonEmpty
    hard_constraints: tuple[NonEmpty, ...] = ()
    acceptance_criteria: tuple[NonEmpty, ...] = ()

