from __future__ import annotations

from datetime import datetime
from typing import TypeAlias

from cogito.domain.enums import (
    AdmissionDecision,
    AdmissionReasonCode,
    CognitiveTargetType,
    EvidenceRelation,
    PropositionStatus,
)
from cogito.domain.ids import EpisodeId, EvidenceLinkId
from cogito.domain.models.admission import AdmissionResult
from cogito.domain.models.draft import DraftCognitiveTarget
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import ObservedProposition
from cogito.domain.proposals.evidence import EvidenceLinkProposal


EvidenceTarget: TypeAlias = Fact | Hypothesis | InformationGap | DraftCognitiveTarget

ALLOWED_RELATIONS: dict[CognitiveTargetType, frozenset[EvidenceRelation]] = {
    CognitiveTargetType.FACT: frozenset(
        {EvidenceRelation.SUPPORTS, EvidenceRelation.CONTRADICTS}
    ),
    CognitiveTargetType.HYPOTHESIS: frozenset(
        {EvidenceRelation.SUPPORTS, EvidenceRelation.CONTRADICTS}
    ),
    CognitiveTargetType.GAP: frozenset({EvidenceRelation.RESOLVES}),
}


def cognitive_target_type(target: EvidenceTarget) -> CognitiveTargetType:
    if isinstance(target, DraftCognitiveTarget):
        return target.target_type
    return {
        Fact: CognitiveTargetType.FACT,
        Hypothesis: CognitiveTargetType.HYPOTHESIS,
        InformationGap: CognitiveTargetType.GAP,
    }[type(target)]


def cognitive_target_id(target: EvidenceTarget) -> str:
    if isinstance(target, DraftCognitiveTarget):
        return target.target_id
    return str(target.id)


class EvidenceAdmissionPolicy:
    """Deterministic admission law for proposition-to-target relations."""

    def evaluate(
        self,
        *,
        episode_id: EpisodeId,
        proposal: EvidenceLinkProposal,
        propositions: tuple[ObservedProposition, ...],
        targets: tuple[EvidenceTarget, ...],
        evidence_id: EvidenceLinkId,
        created_at: datetime,
        existing_relations: tuple[EvidenceLink, ...] = (),
        staged_relations: tuple[EvidenceLink, ...] = (),
    ) -> AdmissionResult[EvidenceLink]:
        source = next(
            (item for item in propositions if item.id == proposal.proposition_id), None
        )
        if source is None:
            return self._reject(
                AdmissionReasonCode.SOURCE_NOT_FOUND,
                "source proposition does not exist",
            )
        target = next(
            (item for item in targets if cognitive_target_id(item) == proposal.target_id),
            None,
        )
        if target is None:
            return self._reject(
                AdmissionReasonCode.TARGET_NOT_FOUND,
                "cognitive target does not exist in current state or transaction draft",
            )
        if source.episode_id != episode_id or target.episode_id != episode_id:
            return self._reject(
                AdmissionReasonCode.EPISODE_MISMATCH,
                "source, target, and transaction must belong to one episode",
            )
        if source.status is not PropositionStatus.ACTIVE:
            return self._reject(
                AdmissionReasonCode.PROPOSITION_INACTIVE,
                "only active propositions may create new EvidenceLinks",
            )
        actual_type = cognitive_target_type(target)
        if proposal.target_type is not actual_type:
            return self._reject(
                AdmissionReasonCode.TARGET_TYPE_MISMATCH,
                "declared target type does not match the domain object",
            )
        if proposal.relation is EvidenceRelation.NEUTRAL:
            return AdmissionResult[EvidenceLink](
                decision=AdmissionDecision.NO_NEW_ADMISSION,
                reason_codes=(AdmissionReasonCode.NEUTRAL_EVIDENCE,),
                public_reasons=("neutral evaluations are not committed",),
            )
        if proposal.relation not in ALLOWED_RELATIONS[actual_type]:
            return self._reject(
                AdmissionReasonCode.RELATION_NOT_ALLOWED,
                f"{proposal.relation.value} cannot target {actual_type.value}",
            )

        material_relations = existing_relations + staged_relations
        matching_pair = tuple(
            item
            for item in material_relations
            if item.proposition_id == proposal.proposition_id
            and item.target_id == proposal.target_id
        )
        if any(item.relation is proposal.relation for item in matching_pair):
            return AdmissionResult[EvidenceLink](
                decision=AdmissionDecision.NO_NEW_ADMISSION,
                reason_codes=(AdmissionReasonCode.DUPLICATE_EVIDENCE,),
                public_reasons=("the same active evidence relation already exists",),
            )
        opposites = {EvidenceRelation.SUPPORTS, EvidenceRelation.CONTRADICTS}
        if proposal.relation in opposites and any(
            item.relation in opposites and item.relation is not proposal.relation
            for item in matching_pair
        ):
            return self._reject(
                AdmissionReasonCode.RELATION_CONFLICT,
                "the same proposition and target already have the opposite active relation",
            )

        value = EvidenceLink(
            id=evidence_id,
            episode_id=episode_id,
            proposition_id=proposal.proposition_id,
            target_type=proposal.target_type,
            target_id=proposal.target_id,
            relation=proposal.relation,
            reason=proposal.reason,
            created_at=created_at,
        )
        return AdmissionResult[EvidenceLink](
            decision=AdmissionDecision.ADMIT,
            value=value,
        )

    @staticmethod
    def _reject(
        code: AdmissionReasonCode, reason: str
    ) -> AdmissionResult[EvidenceLink]:
        return AdmissionResult[EvidenceLink](
            decision=AdmissionDecision.REJECT,
            reason_codes=(code,),
            public_reasons=(reason,),
        )

