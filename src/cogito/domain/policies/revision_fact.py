from datetime import datetime

from cogito.domain.enums import (
    CognitiveTargetType, EvidenceRelation, EventType, FactBasis, FactStatus,
    RevisionReasonCode as Code, SemanticDirectness, TemporalSuccessionBasis as Basis,
)
from cogito.domain.models.episode import EpisodeState
from cogito.domain.proposals.revision import FactSupersedeProposal
from cogito.domain.policies.revision_common import (
    PolicyEffect, already_applied, defer, evidence_for, is_direct_observation,
    material, observation_for, target_check,
)


class FactSupersedePolicy:
    def evaluate(self, state: EpisodeState, proposal: FactSupersedeProposal,
                 *, now: datetime) -> PolicyEffect:
        old = next((f for f in state.facts if f.id == proposal.fact_id), None)
        replacement = next((f for f in state.facts if f.id == proposal.replacement_fact_id), None)
        for target in (old, replacement):
            if problem := target_check(state, target):
                return problem
        if old.id == replacement.id:
            return defer(Code.INSUFFICIENT_REVISION_BASIS)
        if old.status is FactStatus.SUPERSEDED and any(
            e.episode_id == state.episode.id and e.event_type is EventType.FACT_SUPERSEDED
            and e.payload.get("object_id") == str(old.id)
            and e.payload.get("replacement_fact_id") == str(replacement.id)
            for e in state.cognitive_events
        ):
            return already_applied()
        if old.status is not FactStatus.ACTIVE or replacement.status is not FactStatus.ACTIVE:
            return defer(Code.TARGET_STATUS_INVALID)
        if (not old.subject or not old.predicate or not old.scope
                or (old.subject, old.predicate, old.scope, old.basis)
                != (replacement.subject, replacement.predicate, replacement.scope, replacement.basis)):
            return defer(Code.INSUFFICIENT_REVISION_BASIS)
        links = evidence_for(state, proposal.basis_evidence_ids, str(replacement.id),
                             CognitiveTargetType.FACT, EvidenceRelation.SUPPORTS)
        if isinstance(links, PolicyEffect):
            return links
        if not set(proposal.basis_evidence_ids) <= set(replacement.evidence_refs):
            return defer(Code.INSUFFICIENT_REVISION_BASIS)
        basis = proposal.temporal_basis
        if basis is Basis.LATER_DIRECT_OBSERVATION:
            if replacement.basis is not FactBasis.DIRECT_MEASUREMENT or not all(
                is_direct_observation(state, e) for e in links
            ):
                return defer(Code.INSUFFICIENT_REVISION_BASIS)
            old_end = self._world_boundary(state, old, end=True)
            new_start = self._world_boundary(state, replacement, end=False)
            if (old_end is None or new_start is None or old_end.utcoffset() is None
                    or new_start.utcoffset() is None or new_start <= old_end):
                return defer(Code.TEMPORAL_BASIS_INSUFFICIENT)
        elif basis is Basis.EXPLICIT_STATE_TRANSITION:
            if proposal.transition_match is not SemanticDirectness.DIRECT:
                return defer(Code.TEMPORAL_BASIS_INSUFFICIENT)
        elif basis is Basis.VERSIONED_ARTIFACT_SUCCESSION:
            # The current Domain has no admitted artifact-version/ordering
            # provenance contract. Proposal ordinals and a shared source_ref
            # cannot establish these world facts. Retain the input shape, but
            # defer until such provenance is explicitly supported.
            return defer(Code.VERSION_PROVENANCE_INSUFFICIENT)
        updated = old.model_copy(update={"status":FactStatus.SUPERSEDED})
        effect = material(old, updated, EventType.FACT_SUPERSEDED, basis.value,
                          tuple(str(e.id) for e in links), proposal.reason, proposal)
        return effect.model_copy(update={"payload":{**effect.payload,
                                                    "replacement_fact_id":str(replacement.id)}})

    @staticmethod
    def _world_boundary(state, fact, *, end):
        # Cognitive created_at is intentionally never a fallback for world time.
        if fact.valid_from is not None or fact.valid_to is not None:
            return (fact.valid_to or fact.valid_from) if end else fact.valid_from
        links = evidence_for(state, fact.evidence_refs, str(fact.id),
                             CognitiveTargetType.FACT, EvidenceRelation.SUPPORTS)
        if isinstance(links, PolicyEffect) or not links:
            return None
        times = []
        for link in links:
            proposition = next(p for p in state.observed_propositions if p.id == link.proposition_id)
            observation = observation_for(state, link)
            instant = proposition.observed_at or (observation.observed_at if observation else None)
            if instant is None or instant.utcoffset() is None:
                return None
            times.append(instant)
        return max(times) if end else min(times)
