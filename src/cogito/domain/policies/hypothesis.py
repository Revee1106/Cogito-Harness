from __future__ import annotations

from datetime import datetime

from cogito.domain.enums import (
    AdmissionDecision,
    AdmissionReasonCode,
    CognitiveTargetType,
    EvidenceRelation,
    HypothesisStatus,
    PropositionStatus,
)
from cogito.domain.ids import EpisodeId, HypothesisId
from cogito.domain.models.admission import AdmissionResult
from cogito.domain.models.draft import DraftCognitiveTarget
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import ObservedProposition
from cogito.domain.proposals.hypothesis import HypothesisProposal


class HypothesisAdmissionPolicy:
    """Create only evidence-backed, testable, PLAUSIBLE hypotheses."""

    def evaluate(
        self,
        *,
        episode_id: EpisodeId,
        proposal: HypothesisProposal,
        draft_target: DraftCognitiveTarget,
        propositions: tuple[ObservedProposition, ...],
        admitted_relations: tuple[EvidenceLink, ...],
        created_at: datetime,
    ) -> AdmissionResult[Hypothesis]:
        if not proposal.supporting_proposition_ids:
            return self._reject(
                AdmissionReasonCode.NO_SUPPORTING_PROPOSITION,
                "a Hypothesis requires at least one candidate proposition",
            )
        if (
            draft_target.episode_id != episode_id
            or draft_target.target_type is not CognitiveTargetType.HYPOTHESIS
        ):
            code = (
                AdmissionReasonCode.EPISODE_MISMATCH
                if draft_target.episode_id != episode_id
                else AdmissionReasonCode.TARGET_TYPE_MISMATCH
            )
            return self._reject(code, "reserved Hypothesis target is invalid")

        proposition_by_id = {item.id: item for item in propositions}
        supporting = tuple(
            proposition_by_id.get(item)
            for item in proposal.supporting_proposition_ids
        )
        if any(item is None for item in supporting):
            return self._reject(
                AdmissionReasonCode.SOURCE_NOT_FOUND,
                "a candidate supporting proposition does not exist",
            )
        if any(item.episode_id != episode_id for item in supporting if item is not None):
            return self._reject(
                AdmissionReasonCode.EPISODE_MISMATCH,
                "all candidate propositions must belong to the current episode",
            )
        if any(
            item.status is not PropositionStatus.ACTIVE
            for item in supporting
            if item is not None
        ):
            return self._reject(
                AdmissionReasonCode.PROPOSITION_INACTIVE,
                "all supporting propositions must be active to create a Hypothesis",
            )

        relevant_relations = tuple(
            item
            for item in admitted_relations
            if item.target_id == draft_target.target_id
            and item.proposition_id in proposal.supporting_proposition_ids
        )
        if any(item.episode_id != episode_id for item in relevant_relations):
            return self._reject(
                AdmissionReasonCode.EPISODE_MISMATCH,
                "supporting Evidence must belong to the current episode",
            )
        supporting_relations = tuple(
            item
            for item in relevant_relations
            if item.target_type is CognitiveTargetType.HYPOTHESIS
            and item.relation is EvidenceRelation.SUPPORTS
        )
        if not supporting_relations:
            return self._reject(
                AdmissionReasonCode.NO_SUPPORTING_EVIDENCE,
                "candidate propositions do not automatically become admitted Evidence",
            )
        if not self._present(proposal.prediction) and not self._present(
            proposal.disconfirming_condition
        ):
            return self._reject(
                AdmissionReasonCode.MISSING_TESTABLE_EXPECTATION,
                "a new Hypothesis needs a prediction or disconfirming condition",
            )

        value = Hypothesis(
            id=HypothesisId(draft_target.target_id),
            episode_id=episode_id,
            statement=proposal.statement,
            target_problem=proposal.target_problem,
            evidence_refs=tuple(item.id for item in supporting_relations),
            prediction=proposal.prediction,
            disconfirming_condition=proposal.disconfirming_condition,
            status=HypothesisStatus.PLAUSIBLE,
            created_at=created_at,
            updated_at=created_at,
        )
        return AdmissionResult[Hypothesis](
            decision=AdmissionDecision.ADMIT,
            value=value,
        )

    @staticmethod
    def _present(value: str | None) -> bool:
        return bool(value and value.strip())

    @staticmethod
    def _reject(
        code: AdmissionReasonCode, reason: str
    ) -> AdmissionResult[Hypothesis]:
        return AdmissionResult[Hypothesis](
            decision=AdmissionDecision.REJECT,
            reason_codes=(code,),
            public_reasons=(reason,),
        )

