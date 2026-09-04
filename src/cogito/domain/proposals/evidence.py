from typing import Annotated

from pydantic import Field

from cogito.domain.base import ProposalModel
from cogito.domain.enums import CognitiveTargetType, EvidenceRelation
from cogito.domain.ids import PropositionId


class EvidenceLinkProposal(ProposalModel):
    proposition_id: PropositionId
    target_type: CognitiveTargetType
    target_id: Annotated[str, Field(min_length=1)]
    relation: EvidenceRelation
    reason: Annotated[str, Field(min_length=1)]

