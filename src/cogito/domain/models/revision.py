from pydantic import model_validator

from cogito.domain.base import DomainModel, ProposalModel
from cogito.domain.enums import RevisionStatus, RevisionReasonCode
from cogito.domain.ids import EvidenceLinkId
from cogito.domain.models.event import CognitiveTransaction
from cogito.domain.proposals.revision import (
    FactSupersedeProposal, HypothesisRejectProposal, HypothesisStrengthenProposal, Reason,
)


class RevisionBatch(ProposalModel):
    """Explicit local revision inputs sharing one cognitive cause."""
    cause_id: Reason
    hypothesis_strengthen_proposals: tuple[HypothesisStrengthenProposal, ...] = ()
    hypothesis_reject_proposals: tuple[HypothesisRejectProposal, ...] = ()
    gap_resolution_evidence_ids: tuple[EvidenceLinkId, ...] = ()
    fact_supersede_proposals: tuple[FactSupersedeProposal, ...] = ()


class RevisionResult(DomainModel):
    status: RevisionStatus
    transaction: CognitiveTransaction | None = None
    reason_codes: tuple[RevisionReasonCode, ...] = ()
    public_reasons: tuple[str, ...] = ()
    affected_object_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def transaction_matches_materiality(self):
        if (self.status is RevisionStatus.MATERIAL_CHANGE) != (self.transaction is not None):
            raise ValueError("exactly MATERIAL_CHANGE requires a transaction")
        expected = tuple(c.object_id for c in self.transaction.object_changes) if self.transaction else ()
        if self.affected_object_ids != expected:
            raise ValueError("affected_object_ids must match the transaction updates")
        if self.transaction is not None and not expected:
            raise ValueError("a revision transaction must update a target")
        return self
