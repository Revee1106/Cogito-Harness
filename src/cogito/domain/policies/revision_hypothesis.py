from datetime import datetime

from cogito.domain.enums import (
    CognitiveTargetType, EvidenceRelation, EventType, HypothesisStatus,
    HypothesisSupportBasis as Basis, RevisionReasonCode as Code,
    RejectionBasis, SemanticDirectness,
)
from cogito.domain.models.episode import EpisodeState
from cogito.domain.proposals.revision import HypothesisStrengthenProposal, HypothesisRejectProposal
from cogito.domain.policies.revision_common import (
    PolicyEffect, already_applied, defer, evidence_for, is_direct_observation,
    material, observation_for, target_check,
)


class HypothesisStrengthenPolicy:
    def evaluate(self, state: EpisodeState, proposal: HypothesisStrengthenProposal,
                 *, now: datetime) -> PolicyEffect:
        h = next((h for h in state.hypotheses if h.id == proposal.hypothesis_id), None)
        if problem := target_check(state, h):
            return problem
        if h.status not in (HypothesisStatus.PLAUSIBLE, HypothesisStatus.SUPPORTED):
            return defer(Code.TARGET_STATUS_INVALID)
        links = evidence_for(state, proposal.evidence_link_ids, str(h.id),
                             CognitiveTargetType.HYPOTHESIS, EvidenceRelation.SUPPORTS)
        if isinstance(links, PolicyEffect):
            return links
        basis = proposal.support_basis
        if basis is Basis.DIRECT_OBSERVATION and not all(is_direct_observation(state, e) for e in links):
            return defer(Code.INSUFFICIENT_REVISION_BASIS)
        if basis is Basis.INDEPENDENT_CORROBORATION:
            if len({e.proposition_id for e in links}) < 2:
                return defer(Code.INSUFFICIENT_CORROBORATION)
            observations = [observation_for(state, e) for e in links]
            if any(o is None for o in observations):
                return defer(Code.INSUFFICIENT_CORROBORATION)
            refs = [o.source_ref for o in observations if o.source_ref is not None]
            if len({o.id for o in observations}) != len(links) or len(set(refs)) != len(refs):
                return defer(Code.INSUFFICIENT_CORROBORATION)
        if basis is Basis.PREDICTION_CONSISTENT and not (h.prediction or "").strip():
            return defer(Code.MISSING_PREDICTION)
        consumed = set()
        for event in state.cognitive_events:
            if (event.episode_id == state.episode.id
                    and event.event_type is EventType.HYPOTHESIS_STRENGTHENED
                    and event.payload.get("object_id") == str(h.id)
                    and event.payload.get("basis") == basis.value):
                consumed.update(event.payload.get("basis_evidence_ids", []))
        ids = tuple(str(e.id) for e in links)
        if set(ids) <= consumed:
            return already_applied()
        updated = h.model_copy(update={"status":HypothesisStatus.SUPPORTED, "updated_at":now})
        return material(h, updated, EventType.HYPOTHESIS_STRENGTHENED,
                        basis.value, ids, proposal.reason, proposal)


class HypothesisRejectPolicy:
    def evaluate(self, state: EpisodeState, proposal: HypothesisRejectProposal,
                 *, now: datetime) -> PolicyEffect:
        h = next((h for h in state.hypotheses if h.id == proposal.hypothesis_id), None)
        if problem := target_check(state, h):
            return problem
        links = evidence_for(state, proposal.evidence_link_ids, str(h.id),
                             CognitiveTargetType.HYPOTHESIS, EvidenceRelation.CONTRADICTS)
        if isinstance(links, PolicyEffect):
            return links
        if h.status is HypothesisStatus.REJECTED:
            return already_applied()
        if h.status not in (HypothesisStatus.PLAUSIBLE, HypothesisStatus.SUPPORTED):
            return defer(Code.TARGET_STATUS_INVALID)
        if proposal.rejection_basis is RejectionBasis.DIRECT_CONTRADICTION:
            if proposal.semantic_directness is SemanticDirectness.NOT_DIRECT:
                return defer(Code.INSUFFICIENT_REVISION_BASIS)
            if proposal.semantic_directness is not SemanticDirectness.DIRECT:
                return defer(Code.AMBIGUOUS_DIRECTNESS)
            if not self._comparable_to_prior_support(state, h, links):
                return defer(Code.INSUFFICIENT_REVISION_BASIS)
        else:
            if not (h.disconfirming_condition or "").strip():
                return defer(Code.DISCONFIRMING_CONDITION_MISSING)
            if not self._condition_precedes(state, h, links):
                return defer(Code.DISCONFIRMING_CONDITION_NOT_PRIOR)
        updated = h.model_copy(update={"status":HypothesisStatus.REJECTED, "updated_at":now})
        return material(h, updated, EventType.HYPOTHESIS_REJECTED,
                        proposal.rejection_basis.value, tuple(str(e.id) for e in links),
                        proposal.reason, proposal)

    @staticmethod
    def _comparable_to_prior_support(state, hypothesis, links) -> bool:
        # Hypothesis has no structured entity/time fields yet. Compare the known
        # entity and scope in its retained support; do not infer natural language.
        propositions = {p.id:p for p in state.observed_propositions}
        prior = [propositions[e.proposition_id] for e in state.evidence_links
                 if e.id in hypothesis.evidence_refs and e.target_id == str(hypothesis.id)
                 and e.relation is EvidenceRelation.SUPPORTS and e.proposition_id in propositions]
        for link in links:
            candidate = propositions[link.proposition_id]
            for supporting in prior:
                for field in ("subject", "scope"):
                    a, b = getattr(candidate, field), getattr(supporting, field)
                    if a is not None and b is not None and a != b:
                        return False
        return True

    @staticmethod
    def _condition_precedes(state, hypothesis, links) -> bool:
        history = tuple(e for e in state.cognitive_events if e.episode_id == state.episode.id)
        snapshots = [e for e in history if e.event_type is EventType.HYPOTHESIS_CREATED
                     and e.payload.get("object_id") == str(hypothesis.id)
                     and e.payload.get("disconfirming_condition") == hypothesis.disconfirming_condition]
        if len(snapshots) != 1:
            return False
        snapshot = snapshots[0]
        for link in links:
            observation = observation_for(state, link)
            if observation is None:
                return False
            required = ((EventType.OBSERVATION_ADDED, "object_id", str(observation.id)),
                        (EventType.PROPOSITION_ADDED, "object_id", str(link.proposition_id)),
                        (EventType.EVIDENCE_LINK_ADMITTED, "relation_id", str(link.id)))
            for kind, key, identity in required:
                events = [e for e in history if e.event_type is kind and e.payload.get(key) == identity]
                if not events or any(e.sequence <= snapshot.sequence or
                                     e.transaction_id == snapshot.transaction_id for e in events):
                    return False
        return True
