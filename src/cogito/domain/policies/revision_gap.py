from datetime import datetime

from cogito.domain.enums import (
    CognitiveTargetType, EvidenceRelation, EventType, GapStatus, RevisionReasonCode as Code,
)
from cogito.domain.ids import EvidenceLinkId
from cogito.domain.models.episode import EpisodeState
from cogito.domain.policies.revision_common import (
    PolicyEffect, already_applied, defer, evidence_for, material, target_check,
)


class GapResolutionPolicy:
    def evaluate(self, state: EpisodeState, evidence_id: EvidenceLinkId,
                 *, now: datetime) -> PolicyEffect:
        link = next((e for e in state.evidence_links if e.id == evidence_id), None)
        if link is None:
            return defer(Code.EVIDENCE_NOT_FOUND)
        gap = next((g for g in state.gaps if str(g.id) == link.target_id), None)
        if problem := target_check(state, gap):
            return problem
        links = evidence_for(state, (evidence_id,), str(gap.id),
                             CognitiveTargetType.GAP, EvidenceRelation.RESOLVES)
        if isinstance(links, PolicyEffect):
            return links
        if gap.status is GapStatus.RESOLVED:
            return already_applied()
        if gap.status not in (GapStatus.OPEN, GapStatus.FOCUSED):
            return defer(Code.TARGET_STATUS_INVALID)
        updated = gap.model_copy(update={"status":GapStatus.RESOLVED, "resolved_at":now})
        return material(gap, updated, EventType.GAP_RESOLVED, EvidenceRelation.RESOLVES.value,
                        (str(link.id),), link.reason)
