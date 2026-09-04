from typing import Annotated

from pydantic import Field

from cogito.domain.base import DomainModel


NonEmpty = Annotated[str, Field(min_length=1)]


class AcceptanceCriterion(DomainModel):
    id: NonEmpty
    statement: NonEmpty


class GoalContract(DomainModel):
    objective: NonEmpty
    hard_constraints: tuple[NonEmpty, ...] = ()
    acceptance_criteria: tuple[AcceptanceCriterion, ...] = ()
    version: int = Field(ge=1)

