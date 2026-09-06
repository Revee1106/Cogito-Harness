from datetime import UTC, datetime, timedelta

from cogito.domain.enums import (
    EpisodeStatus, EvidenceRelation, CognitiveTargetType, HypothesisStatus,
    FactBasis, EventType,
)
from cogito.domain.models.episode import Episode, EpisodeState
from cogito.domain.models.event import CognitiveEvent
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.observation import Observation, ObservedProposition

NOW = datetime(2026, 1, 10, tzinfo=UTC)


def event(kind, payload, sequence=1, tx="seed", **updates):
    return CognitiveEvent(
        id=f"event-{sequence}", episode_id="ep", transaction_id=tx,
        sequence=sequence, event_type=kind, payload=payload, created_at=NOW,
    ).model_copy(update=updates)


def state():
    observations = tuple(Observation(
        id=f"o{i}", episode_id="ep", source="direct measurement",
        source_ref=f"sensor-{i}", raw_content=f"measurement {i}", scope="host-A",
        observed_at=NOW + timedelta(hours=i), created_at=NOW,
    ) for i in range(1, 7))
    propositions = tuple(ObservedProposition(
        id=f"p{i}", episode_id="ep", observation_id=f"o{i}",
        statement=f"measurement {i}", subject="db", predicate="port",
        value=3306 if i == 5 else 3307, scope="host-A",
        observed_at=observations[i-1].observed_at, created_at=NOW,
    ) for i in range(1, 7))
    links = tuple(EvidenceLink(
        id=f"e{i}", episode_id="ep", proposition_id=f"p{i}",
        target_type=(CognitiveTargetType.HYPOTHESIS if i <= 3 else
                     CognitiveTargetType.GAP if i == 4 else CognitiveTargetType.FACT),
        target_id="h1" if i <= 3 else "g1" if i == 4 else f"f{i-4}",
        relation=EvidenceRelation.CONTRADICTS if i == 3 else
                 EvidenceRelation.RESOLVES if i == 4 else EvidenceRelation.SUPPORTS,
        reason="explicit semantic fixture", created_at=NOW,
    ) for i in range(1, 7))
    h = Hypothesis(id="h1", episode_id="ep", statement="endpoint mismatch",
        target_problem="connectivity", evidence_refs=("e1",), prediction="probe succeeds",
        disconfirming_condition="same endpoint still fails", status=HypothesisStatus.PLAUSIBLE,
        created_at=NOW, updated_at=NOW)
    facts = tuple(Fact(id=f"f{i-4}", episode_id="ep", statement=f"port {p.value}",
        subject=p.subject, predicate=p.predicate, value=p.value, scope=p.scope,
        valid_from=p.observed_at, valid_to=p.observed_at,
        basis=FactBasis.DIRECT_MEASUREMENT, evidence_refs=(f"e{i}",), created_at=NOW)
        for i, p in enumerate(propositions, 1) if i >= 5)
    history = [event(EventType.HYPOTHESIS_CREATED,
                     {"object_id":"h1", "disconfirming_condition":h.disconfirming_condition})]
    for i in range(1, 7):
        for kind, payload in (
            (EventType.OBSERVATION_ADDED, {"object_id":f"o{i}"}),
            (EventType.PROPOSITION_ADDED, {"object_id":f"p{i}"}),
            (EventType.EVIDENCE_LINK_ADMITTED, {"relation_id":f"e{i}"}),
        ):
            history.append(event(kind, payload, len(history)+1, tx="evidence"))
    return EpisodeState(
        episode=Episode(id="ep", status=EpisodeStatus.ACTIVE, cognitive_version=2,
                        goal_contract_version=0, created_at=NOW, updated_at=NOW),
        hypotheses=(h,), facts=facts,
        gaps=(InformationGap(id="g1", episode_id="ep", question="port?",
              why_it_matters="connectivity", created_at=NOW),),
        observed_propositions=propositions, recent_observations=observations,
        evidence_links=links, cognitive_events=tuple(history),
    )


def replace_item(s, field, index, **updates):
    values = list(getattr(s, field))
    values[index] = values[index].model_copy(update=updates)
    return s.model_copy(update={field:tuple(values)})
