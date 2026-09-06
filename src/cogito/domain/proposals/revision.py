from typing import Annotated

from pydantic import Field, StringConstraints

from cogito.domain.base import ProposalModel
from cogito.domain.enums import HypothesisSupportBasis, RejectionBasis, SemanticDirectness, TemporalSuccessionBasis
from cogito.domain.ids import EvidenceLinkId, HypothesisId, FactId

Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
EvidenceIds = Annotated[tuple[EvidenceLinkId, ...], Field(min_length=1)]


class HypothesisStrengthenProposal(ProposalModel):
    hypothesis_id: HypothesisId
    evidence_link_ids: EvidenceIds
    support_basis: HypothesisSupportBasis
    reason: Reason


class HypothesisRejectProposal(ProposalModel):
    hypothesis_id: HypothesisId
    evidence_link_ids: EvidenceIds
    rejection_basis: RejectionBasis
    reason: Reason
    semantic_directness: SemanticDirectness | None = SemanticDirectness.AMBIGUOUS


class FactSupersedeProposal(ProposalModel):
    fact_id: FactId
    replacement_fact_id: FactId
    temporal_basis: TemporalSuccessionBasis
    basis_evidence_ids: EvidenceIds
    reason: Reason
    transition_match: SemanticDirectness = SemanticDirectness.AMBIGUOUS
    artifact_identity: Reason | None = None
    old_version: Annotated[int, Field(strict=True, ge=0)] | None = None
    replacement_version: Annotated[int, Field(strict=True, ge=0)] | None = None
