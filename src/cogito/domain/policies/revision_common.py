"""Shared structural checks for the four explicit Story 1B revision policies."""
from datetime import datetime

from pydantic import Field

from cogito.domain.base import DomainModel, ProposalModel
from cogito.domain.enums import (
    CognitiveTargetType, EvidenceRelation, EventType, FactBasis,
    PropositionStatus, RevisionReasonCode as Code, RevisionStatus,
)
from cogito.domain.models.episode import EpisodeState
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.policies.fact import SOURCE_MARKERS

RevisionTarget = Hypothesis | InformationGap | Fact


class PolicyEffect(DomainModel):
    status: RevisionStatus
    value: RevisionTarget | None = None
    event_type: EventType | None = None
    payload: dict[str, object] = Field(default_factory=dict)
    reason_codes: tuple[Code, ...] = ()
    public_reasons: tuple[str, ...] = ()


def defer(code: Code) -> PolicyEffect:
    return PolicyEffect(status=RevisionStatus.DEFERRED, reason_codes=(code,),
                        public_reasons=(code.value.replace("_", " ").lower(),))


def already_applied() -> PolicyEffect:
    return PolicyEffect(status=RevisionStatus.NO_MATERIAL_CHANGE,
                        reason_codes=(Code.ALREADY_APPLIED,),
                        public_reasons=("revision effect already committed",))


def material(before: RevisionTarget, after: RevisionTarget, event_type: EventType,
             basis: str, evidence_ids: tuple[str, ...], reason: str,
             proposal: ProposalModel | None = None) -> PolicyEffect:
    payload = dict(object_id=str(before.id), previous_status=before.status.value,
                   new_status=after.status.value, basis_evidence_ids=list(dict.fromkeys(evidence_ids)),
                   basis=basis, public_reason=reason)
    if proposal is not None:
        payload["proposal"] = proposal.model_dump(mode="json")
    return PolicyEffect(status=RevisionStatus.MATERIAL_CHANGE, value=after,
                        event_type=event_type, payload=payload)


def target_check(state: EpisodeState, target: RevisionTarget | None) -> PolicyEffect | None:
    if target is None:
        return defer(Code.TARGET_NOT_FOUND)
    if target.episode_id != state.episode.id:
        return defer(Code.EPISODE_MISMATCH)
    return None


def evidence_for(state: EpisodeState, ids: tuple[str, ...], target_id: str,
                 target_type: CognitiveTargetType, relation: EvidenceRelation
                 ) -> tuple[EvidenceLink, ...] | PolicyEffect:
    by_id = {str(e.id): e for e in state.evidence_links}
    propositions = {str(p.id): p for p in state.observed_propositions}
    links = []
    for ref in dict.fromkeys(ids):
        e = by_id.get(ref)
        if e is None:
            return defer(Code.EVIDENCE_NOT_FOUND)
        p = propositions.get(str(e.proposition_id))
        if p is None:
            return defer(Code.EVIDENCE_NOT_FOUND)
        if e.episode_id != state.episode.id or p.episode_id != state.episode.id:
            return defer(Code.EPISODE_MISMATCH)
        if e.target_id != target_id or e.target_type is not target_type:
            return defer(Code.EVIDENCE_TARGET_MISMATCH)
        if e.relation is not relation:
            return defer(Code.EVIDENCE_RELATION_INVALID)
        if p.status is not PropositionStatus.ACTIVE:
            return defer(Code.PROPOSITION_INACTIVE)
        links.append(e)
    return tuple(links) if links else defer(Code.INSUFFICIENT_REVISION_BASIS)


def observation_for(state: EpisodeState, link: EvidenceLink):
    p = next((p for p in state.observed_propositions if p.id == link.proposition_id), None)
    if p is None:
        return None
    return next((o for o in state.recent_observations
                 if o.id == p.observation_id and o.episode_id == state.episode.id), None)


def is_direct_observation(state: EpisodeState, link: EvidenceLink) -> bool:
    observation = observation_for(state, link)
    if observation is None:
        return False
    source = observation.source.casefold()
    excluded = SOURCE_MARKERS[FactBasis.SOURCE_REPORT] + SOURCE_MARKERS[FactBasis.ARTIFACT_CONTENT]
    return (not any(marker in source for marker in excluded)
            and any(marker in source for marker in SOURCE_MARKERS[FactBasis.DIRECT_MEASUREMENT]))
