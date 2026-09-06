"""Pure local revision builder. Persistence belongs to the CognitiveStore caller."""
from datetime import UTC, datetime

from cogito.domain.enums import ChangeKind, RevisionReasonCode as Code, RevisionStatus as Status
from cogito.domain.ids import EventId, TransactionId, new_id
from cogito.domain.models.episode import EpisodeState
from cogito.domain.models.event import CognitiveEvent, CognitiveTransaction, ObjectChange
from cogito.domain.models.revision import RevisionBatch, RevisionResult
from cogito.domain.policies.revision_fact import FactSupersedePolicy
from cogito.domain.policies.revision_gap import GapResolutionPolicy
from cogito.domain.policies.revision_hypothesis import HypothesisRejectPolicy, HypothesisStrengthenPolicy
from cogito.domain.policies.transaction import OBJECT_TYPES


class LocalRevisionEngine:
    def revise(self, episode_state: EpisodeState, revision_batch: RevisionBatch,
               base_version: int, *, now: datetime | None = None) -> RevisionResult:
        state, batch = episode_state, revision_batch
        if base_version != state.episode.cognitive_version:
            return RevisionResult(status=Status.DEFERRED, reason_codes=(Code.BASE_VERSION_CONFLICT,),
                                  public_reasons=("revision snapshot version does not match base_version",))
        instant = now or datetime.now(UTC)
        effects = []
        for policy, inputs in (
            (HypothesisStrengthenPolicy(), batch.hypothesis_strengthen_proposals),
            (HypothesisRejectPolicy(), batch.hypothesis_reject_proposals),
            (GapResolutionPolicy(), batch.gap_resolution_evidence_ids),
            (FactSupersedePolicy(), batch.fact_supersede_proposals),
        ):
            effects.extend(policy.evaluate(state, item, now=instant) for item in inputs)
        codes = tuple(dict.fromkeys(code for e in effects for code in e.reason_codes))
        reasons = tuple(dict.fromkeys(reason for e in effects for reason in e.public_reasons))
        if any(e.status is Status.DEFERRED for e in effects):
            return RevisionResult(status=Status.DEFERRED, reason_codes=codes, public_reasons=reasons)
        by_target = {}
        for effect in effects:
            if effect.status is not Status.MATERIAL_CHANGE:
                continue
            identity = str(effect.value.id)
            if identity in by_target and by_target[identity] != effect:
                return RevisionResult(status=Status.DEFERRED, reason_codes=(Code.CONFLICTING_REVISIONS,),
                                      public_reasons=("conflicting explicit revisions target the same object",))
            by_target[identity] = effect
        if any(e.payload.get("replacement_fact_id") in by_target for e in by_target.values()):
            return RevisionResult(status=Status.DEFERRED, reason_codes=(Code.CONFLICTING_REVISIONS,),
                                  public_reasons=("a replacement Fact must remain ACTIVE after the batch",))
        if not by_target:
            return RevisionResult(status=Status.NO_MATERIAL_CHANGE, reason_codes=codes, public_reasons=reasons)
        tx_id = new_id(TransactionId)
        last_sequence = max((e.sequence for e in state.cognitive_events), default=0)
        events = tuple(CognitiveEvent(
            id=new_id(EventId), episode_id=state.episode.id, transaction_id=tx_id,
            sequence=last_sequence + i, event_type=effect.event_type,
            cause_id=batch.cause_id, payload=effect.payload, created_at=instant,
        ) for i, effect in enumerate(by_target.values(), start=1))
        changes = tuple(ObjectChange(kind=ChangeKind.UPDATE,
            object_type=OBJECT_TYPES[type(effect.value)], object_id=identity, value=effect.value)
            for identity, effect in by_target.items())
        tx = CognitiveTransaction(id=tx_id, episode_id=state.episode.id, base_version=base_version,
                                  events=events, object_changes=changes)
        return RevisionResult(status=Status.MATERIAL_CHANGE, transaction=tx,
                              reason_codes=codes, public_reasons=reasons,
                              affected_object_ids=tuple(by_target))
