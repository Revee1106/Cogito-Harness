from __future__ import annotations

from datetime import datetime

from cogito.domain.enums import (
    AdmissionDecision,
    AdmissionReasonCode,
    CognitiveTargetType,
    EvidenceRelation,
    FactBasis,
    FactStatus,
    PropositionStatus,
    SemanticEntailment,
)
from cogito.domain.ids import EpisodeId, EvidenceLinkId, FactId
from cogito.domain.models.admission import AdmissionResult, AdmittedFactBundle
from cogito.domain.models.draft import DraftCognitiveTarget
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.observation import Observation, ObservedProposition
from cogito.domain.proposals.fact import FactProposal


SOURCE_MARKERS: dict[FactBasis, tuple[str, ...]] = {
    FactBasis.SOURCE_REPORT: ("user", "report", "source-report"),
    FactBasis.ARTIFACT_CONTENT: ("artifact", "file", "config"),
    FactBasis.DIRECT_MEASUREMENT: (
        "tool",
        "shell",
        "runtime",
        "measurement",
        "sensor",
        "action-result",
    ),
    FactBasis.DETERMINISTIC_DERIVATION: ("deterministic", "rule"),
}

EXPLANATORY_PREDICATES = {
    "cause",
    "causes",
    "caused_by",
    "contributes_to",
    "explains",
    "because",
    "leads_to",
}


class FactAdmissionPolicy:
    """Admit only descriptive Facts supported by one qualified proposition."""

    def evaluate(
        self,
        *,
        episode_id: EpisodeId,
        proposal: FactProposal,
        proposition: ObservedProposition | None,
        observation: Observation | None,
        draft_target: DraftCognitiveTarget,
        evidence_id: EvidenceLinkId,
        created_at: datetime,
        existing_facts: tuple[Fact, ...] = (),
    ) -> AdmissionResult[AdmittedFactBundle]:
        if proposition is None or proposition.id != proposal.proposition_id:
            return self._reject(
                AdmissionReasonCode.SOURCE_NOT_FOUND,
                "source proposition does not exist",
            )
        if observation is None or observation.id != proposition.observation_id:
            return self._reject(
                AdmissionReasonCode.SOURCE_NOT_FOUND,
                "source observation does not exist",
            )
        if (
            proposition.episode_id != episode_id
            or observation.episode_id != episode_id
            or draft_target.episode_id != episode_id
        ):
            return self._reject(
                AdmissionReasonCode.EPISODE_MISMATCH,
                "proposal sources and reserved Fact must belong to one episode",
            )
        if draft_target.target_type is not CognitiveTargetType.FACT:
            return self._reject(
                AdmissionReasonCode.TARGET_TYPE_MISMATCH,
                "reserved target is not a Fact",
            )
        if proposition.status is not PropositionStatus.ACTIVE:
            return self._reject(
                AdmissionReasonCode.PROPOSITION_INACTIVE,
                "only active propositions may support new Facts",
            )
        if proposal.semantic_entailment is SemanticEntailment.STRONGER_THAN_SOURCE:
            return self._reject(
                AdmissionReasonCode.CLAIM_TOO_STRONG,
                "candidate assertion is stronger than its source proposition",
            )
        if proposal.semantic_entailment is SemanticEntailment.AMBIGUOUS:
            return AdmissionResult[AdmittedFactBundle](
                decision=AdmissionDecision.DEFER,
                reason_codes=(AdmissionReasonCode.SEMANTIC_AMBIGUITY,),
                public_reasons=(
                    "semantic support is ambiguous, so no Fact is committed",
                ),
            )
        if not self._scope_is_contained(proposition.scope, proposal.scope):
            return self._reject(
                AdmissionReasonCode.SCOPE_EXPANDED,
                "candidate Fact expands or invents the proposition scope",
            )
        if not self._temporal_scope_is_contained(proposition, proposal):
            return self._reject(
                AdmissionReasonCode.TEMPORAL_SCOPE_INVALID,
                "candidate Fact extends beyond the proposition's observed time",
            )
        normalized_source = observation.source.casefold()
        if not any(
            marker in normalized_source for marker in SOURCE_MARKERS[proposal.basis]
        ):
            return self._reject(
                AdmissionReasonCode.SOURCE_FITNESS_INSUFFICIENT,
                f"source context does not support {proposal.basis.value}",
            )
        candidate_predicate = (proposal.predicate or "").casefold()
        proposition_predicate = (proposition.predicate or "").casefold()
        if (
            candidate_predicate in EXPLANATORY_PREDICATES
            and candidate_predicate != proposition_predicate
        ):
            return self._reject(
                AdmissionReasonCode.NON_EXPLANATORY_BOUNDARY,
                "Fact admission cannot add a new causal explanation",
            )

        valid_from = proposal.valid_from or proposition.observed_at
        valid_to = proposal.valid_to or proposition.observed_at
        candidate = Fact(
            id=FactId(draft_target.target_id),
            episode_id=episode_id,
            statement=proposal.statement,
            subject=proposal.subject,
            predicate=proposal.predicate,
            value=proposal.value,
            scope=proposal.scope,
            valid_from=valid_from,
            valid_to=valid_to,
            basis=proposal.basis,
            evidence_refs=(evidence_id,),
            status=FactStatus.ACTIVE,
            created_at=created_at,
        )
        if any(self.facts_conflict(item, candidate) for item in existing_facts):
            return self._reject(
                AdmissionReasonCode.FACT_CONFLICT,
                "an active Fact already has an incompatible value in overlapping scope and time",
            )
        evidence = EvidenceLink(
            id=evidence_id,
            episode_id=episode_id,
            proposition_id=proposition.id,
            target_type=CognitiveTargetType.FACT,
            target_id=str(candidate.id),
            relation=EvidenceRelation.SUPPORTS,
            reason="source proposition directly supports admitted Fact",
            created_at=created_at,
        )
        return AdmissionResult[AdmittedFactBundle](
            decision=AdmissionDecision.ADMIT,
            value=AdmittedFactBundle(fact=candidate, evidence_link=evidence),
        )

    @staticmethod
    def _scope_is_contained(source_scope: str | None, candidate_scope: str | None) -> bool:
        if source_scope == candidate_scope:
            return True
        if source_scope is None or candidate_scope is None:
            return False
        return candidate_scope.startswith(f"{source_scope}/") or candidate_scope.startswith(
            f"{source_scope}:"
        )

    @staticmethod
    def _temporal_scope_is_contained(
        proposition: ObservedProposition, proposal: FactProposal
    ) -> bool:
        observed_at = proposition.observed_at
        if observed_at is None:
            return proposal.valid_from is None and proposal.valid_to is None
        if proposal.valid_from is not None and proposal.valid_from != observed_at:
            return False
        if proposal.valid_to is not None and proposal.valid_to != observed_at:
            return False
        return True

    @staticmethod
    def facts_conflict(existing: Fact, candidate: Fact) -> bool:
        if existing.status is not FactStatus.ACTIVE:
            return False
        if existing.episode_id != candidate.episode_id:
            return False
        if existing.subject is None or existing.predicate is None:
            return False
        if existing.subject != candidate.subject or existing.predicate != candidate.predicate:
            return False
        if existing.scope != candidate.scope or existing.value == candidate.value:
            return False
        return FactAdmissionPolicy._intervals_overlap(existing, candidate)

    @staticmethod
    def _intervals_overlap(left: Fact, right: Fact) -> bool:
        if left.valid_to is not None and right.valid_from is not None:
            if left.valid_to < right.valid_from:
                return False
        if right.valid_to is not None and left.valid_from is not None:
            if right.valid_to < left.valid_from:
                return False
        return True

    @staticmethod
    def _reject(
        code: AdmissionReasonCode, reason: str
    ) -> AdmissionResult[AdmittedFactBundle]:
        return AdmissionResult[AdmittedFactBundle](
            decision=AdmissionDecision.REJECT,
            reason_codes=(code,),
            public_reasons=(reason,),
        )
