"""Exact Story 1B UPDATE validation, not general event inference."""
from datetime import UTC, datetime

from cogito.domain.enums import ChangeKind, EpisodeStatus, EventType, RevisionStatus
from cogito.domain.models.episode import Episode, EpisodeState
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import Observation, ObservedProposition
from cogito.domain.policies.revision_fact import FactSupersedePolicy
from cogito.domain.policies.revision_gap import GapResolutionPolicy
from cogito.domain.policies.revision_hypothesis import HypothesisRejectPolicy, HypothesisStrengthenPolicy
from cogito.domain.proposals.revision import FactSupersedeProposal, HypothesisRejectProposal, HypothesisStrengthenProposal

REVISION_EVENTS = frozenset((EventType.HYPOTHESIS_STRENGTHENED, EventType.HYPOTHESIS_REJECTED,
                             EventType.GAP_RESOLVED, EventType.FACT_SUPERSEDED))


def revision_issues(transaction, objects, relations, history) -> tuple[str, ...]:
    issues = []
    created = {c.object_id:c.value for c in transaction.object_changes if c.kind is ChangeKind.CREATE}
    # A historical condition/provenance snapshot must describe its actual CREATE.
    snapshots = {
        EventType.HYPOTHESIS_CREATED:Hypothesis,
        EventType.OBSERVATION_ADDED:Observation,
        EventType.PROPOSITION_ADDED:ObservedProposition,
    }
    for event in transaction.events:
        if event.event_type in snapshots and "object_id" in event.payload:
            value = created.get(event.payload["object_id"])
            if not isinstance(value, snapshots[event.event_type]):
                issues.append("creation history must reference its actual CREATE")
            elif (isinstance(value, Hypothesis) and "disconfirming_condition" in event.payload
                  and event.payload["disconfirming_condition"] != value.disconfirming_condition):
                issues.append("condition snapshot must equal the created Hypothesis condition")
    updates = [c for c in transaction.object_changes if c.kind is ChangeKind.UPDATE
               and isinstance(c.value, (Hypothesis, InformationGap, Fact))]
    events = [e for e in transaction.events if e.event_type in REVISION_EVENTS]
    if not updates and not events:
        return tuple(issues)
    if (len(updates) != len(transaction.object_changes) or transaction.relation_changes
            or len(events) != len(transaction.events)):
        issues.append("Story 1B revision batches contain only explicit target UPDATEs and revision events")
    if len(updates) != len(events):
        issues.append("every material UPDATE needs exactly one matching revision event")
    updated_ids = {c.object_id for c in updates}
    if any(isinstance(e.payload.get("replacement_fact_id"), str)
           and e.payload["replacement_fact_id"] in updated_ids for e in events):
        issues.append("a replacement Fact must remain ACTIVE after the batch")
    if len({e.cause_id for e in events}) != 1 or any(not e.cause_id for e in events):
        issues.append("revision events must share one non-empty cognitive cause")
    instant = events[0].created_at if events else datetime(2000,1,1,tzinfo=UTC)
    state = EpisodeState(
        episode=Episode(id=transaction.episode_id,status=EpisodeStatus.ACTIVE,
                        cognitive_version=transaction.base_version,goal_contract_version=0,
                        created_at=instant,updated_at=instant),
        hypotheses=tuple(o for o in objects if isinstance(o,Hypothesis)),
        facts=tuple(o for o in objects if isinstance(o,Fact)),
        gaps=tuple(o for o in objects if isinstance(o,InformationGap)),
        observed_propositions=tuple(o for o in objects if isinstance(o,ObservedProposition)),
        recent_observations=tuple(o for o in objects if isinstance(o,Observation)),
        evidence_links=relations,cognitive_events=history,
    )
    for change in updates:
        matches = [e for e in events if e.payload.get("object_id") == change.object_id]
        if len(matches) != 1:
            issues.append("material UPDATE lacks one unambiguous matching event")
            continue
        event = matches[0]
        try:
            if event.event_type is EventType.GAP_RESOLVED:
                ids = event.payload["basis_evidence_ids"]
                if not isinstance(ids,list) or len(ids) != 1 or not isinstance(ids[0],str):
                    raise ValueError("gap revision needs one explicit RESOLVES link")
                effect = GapResolutionPolicy().evaluate(state,ids[0],now=event.created_at)
            else:
                policy, proposal_type = {
                    EventType.HYPOTHESIS_STRENGTHENED:(HypothesisStrengthenPolicy(),HypothesisStrengthenProposal),
                    EventType.HYPOTHESIS_REJECTED:(HypothesisRejectPolicy(),HypothesisRejectProposal),
                    EventType.FACT_SUPERSEDED:(FactSupersedePolicy(),FactSupersedeProposal),
                }[event.event_type]
                proposal = proposal_type.model_validate(event.payload["proposal"])
                effect = policy.evaluate(state,proposal,now=event.created_at)
            if (effect.status is not RevisionStatus.MATERIAL_CHANGE or effect.value != change.value
                    or effect.event_type != event.event_type or effect.payload != event.payload):
                issues.append("revision UPDATE and event do not match the policy-authorized effect")
        except (ValueError, KeyError, TypeError):
            issues.append("revision event payload is malformed")
    return tuple(issues)
