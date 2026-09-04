from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest

from cogito.adapters.sqlite.store import SQLiteCognitiveStore
from cogito.domain.enums import (
    AdmissionDecision,
    AdmissionReasonCode,
    ChangeKind,
    CognitiveObjectType,
    CognitiveTargetType,
    EpisodeStatus,
    EvidenceRelation,
    FactBasis,
    FactStatus,
    HypothesisStatus,
    SemanticEntailment,
)
from cogito.domain.ids import (
    EpisodeId,
    EvidenceLinkId,
    FactId,
    HypothesisId,
    ObservationId,
    PropositionId,
    TransactionId,
)
from cogito.domain.models.draft import DraftTargetFactory
from cogito.domain.models.episode import Episode
from cogito.domain.models.event import CognitiveTransaction, ObjectChange, RelationChange
from cogito.domain.models.fact import Fact
from cogito.domain.models.observation import Observation, ObservedProposition
from cogito.domain.policies.evidence import EvidenceAdmissionPolicy
from cogito.domain.policies.fact import FactAdmissionPolicy
from cogito.domain.policies.hypothesis import HypothesisAdmissionPolicy
from cogito.domain.proposals.evidence import EvidenceLinkProposal
from cogito.domain.proposals.fact import FactProposal
from cogito.domain.proposals.hypothesis import HypothesisProposal


NOW = datetime(2026, 1, 1, tzinfo=UTC)
EPISODE_ID = EpisodeId("story-1a-episode")


def episode() -> Episode:
    return Episode(
        id=EPISODE_ID,
        status=EpisodeStatus.ACTIVE,
        cognitive_version=0,
        goal_contract_version=0,
        created_at=NOW,
        updated_at=NOW,
    )


def object_change(value, object_type: CognitiveObjectType) -> ObjectChange:
    return ObjectChange(
        kind=ChangeKind.CREATE,
        object_type=object_type,
        object_id=str(value.id),
        value=value,
    )


@pytest.mark.scenario
def test_scenario_a_direct_measurement_to_atomic_fact_admission(tmp_path) -> None:
    store = SQLiteCognitiveStore(tmp_path / "scenario-a.db")
    store.create_schema()
    current_episode = episode()
    observed = Observation(
        id=ObservationId("o-a"),
        episode_id=EPISODE_ID,
        source="shell:netstat",
        raw_content="mysqld LISTEN 0.0.0.0:3307",
        scope="host-A",
        observed_at=NOW,
        created_at=NOW,
    )
    proposition = ObservedProposition(
        id=PropositionId("p-a"),
        episode_id=EPISODE_ID,
        observation_id=observed.id,
        statement="mysqld listens on 3307 on host-A at T1",
        subject="mysqld",
        predicate="runtime_port",
        value=3307,
        scope="host-A",
        observed_at=NOW,
        created_at=NOW,
    )
    draft = DraftTargetFactory.reserve_fact(
        EPISODE_ID, target_id=FactId("f-a")
    )
    admission = FactAdmissionPolicy().evaluate(
        episode_id=EPISODE_ID,
        proposal=FactProposal(
            proposition_id=proposition.id,
            statement="mysqld runtime listener port is 3307",
            subject="mysqld",
            predicate="runtime_port",
            value=3307,
            scope="host-A",
            basis=FactBasis.DIRECT_MEASUREMENT,
            semantic_entailment=SemanticEntailment.EQUIVALENT_OR_NARROWER,
        ),
        proposition=proposition,
        observation=observed,
        draft_target=draft,
        evidence_id=EvidenceLinkId("e-a"),
        created_at=NOW,
    )
    assert admission.value is not None
    transaction = CognitiveTransaction(
        id=TransactionId("tx-a"),
        episode_id=EPISODE_ID,
        base_version=0,
        object_changes=(
            object_change(observed, CognitiveObjectType.OBSERVATION),
            object_change(proposition, CognitiveObjectType.PROPOSITION),
            object_change(admission.value.fact, CognitiveObjectType.FACT),
        ),
        relation_changes=(
            RelationChange(
                kind=ChangeKind.CREATE,
                value=admission.value.evidence_link,
            ),
        ),
    )

    asyncio.run(store.create_episode(current_episode))
    committed = asyncio.run(store.commit_transaction(transaction))
    state = asyncio.run(store.load_episode_state(EPISODE_ID))

    assert admission.decision is AdmissionDecision.ADMIT
    assert committed.cognitive_version == 1
    assert state.facts[0].status is FactStatus.ACTIVE
    assert state.facts[0].evidence_refs == (EvidenceLinkId("e-a"),)
    assert asyncio.run(store.list_relations(EPISODE_ID))[0].target_id == "f-a"


@pytest.mark.scenario
def test_scenario_b_connection_refused_cannot_become_database_down(tmp_path) -> None:
    store = SQLiteCognitiveStore(tmp_path / "scenario-b.db")
    store.create_schema()
    current_episode = episode()
    observed = Observation(
        id=ObservationId("o-b"),
        episode_id=EPISODE_ID,
        source="shell:tcp-connect",
        raw_content="connection to db:3306 returned connection refused",
        scope="db:3306",
        observed_at=NOW,
        created_at=NOW,
    )
    proposition = ObservedProposition(
        id=PropositionId("p-b"),
        episode_id=EPISODE_ID,
        observation_id=observed.id,
        statement="connection to db:3306 was refused",
        scope="db:3306",
        observed_at=NOW,
        created_at=NOW,
    )
    initial = CognitiveTransaction(
        id=TransactionId("tx-b-source"),
        episode_id=EPISODE_ID,
        base_version=0,
        object_changes=(
            object_change(observed, CognitiveObjectType.OBSERVATION),
            object_change(proposition, CognitiveObjectType.PROPOSITION),
        ),
    )
    asyncio.run(store.create_episode(current_episode))
    asyncio.run(store.commit_transaction(initial))

    rejection = FactAdmissionPolicy().evaluate(
        episode_id=EPISODE_ID,
        proposal=FactProposal(
            proposition_id=proposition.id,
            statement="database is down",
            scope="db:3306",
            basis=FactBasis.DIRECT_MEASUREMENT,
            semantic_entailment=SemanticEntailment.STRONGER_THAN_SOURCE,
        ),
        proposition=proposition,
        observation=observed,
        draft_target=DraftTargetFactory.reserve_fact(EPISODE_ID),
        evidence_id=EvidenceLinkId("e-b-rejected"),
        created_at=NOW,
    )
    state = asyncio.run(store.load_episode_state(EPISODE_ID))

    assert rejection.decision is AdmissionDecision.REJECT
    assert rejection.reason_codes == (AdmissionReasonCode.CLAIM_TOO_STRONG,)
    assert state.episode.cognitive_version == 1
    assert state.facts == ()
    assert asyncio.run(store.list_relations(EPISODE_ID)) == ()


@pytest.mark.scenario
def test_scenario_c_two_propositions_create_only_plausible_hypothesis(tmp_path) -> None:
    store = SQLiteCognitiveStore(tmp_path / "scenario-c.db")
    store.create_schema()
    current_episode = episode()
    propositions = (
        ObservedProposition(
            id=PropositionId("p-c1"),
            episode_id=EPISODE_ID,
            observation_id=ObservationId("o-c1"),
            statement="application connects to port 3306",
            observed_at=NOW,
            created_at=NOW,
        ),
        ObservedProposition(
            id=PropositionId("p-c2"),
            episode_id=EPISODE_ID,
            observation_id=ObservationId("o-c2"),
            statement="database listens on port 3307",
            observed_at=NOW,
            created_at=NOW,
        ),
    )
    source_tx = CognitiveTransaction(
        id=TransactionId("tx-c-source"),
        episode_id=EPISODE_ID,
        base_version=0,
        object_changes=tuple(
            object_change(item, CognitiveObjectType.PROPOSITION)
            for item in propositions
        ),
    )
    asyncio.run(store.create_episode(current_episode))
    asyncio.run(store.commit_transaction(source_tx))

    draft = DraftTargetFactory.reserve_hypothesis(
        EPISODE_ID, target_id=HypothesisId("h-c")
    )
    evidence_policy = EvidenceAdmissionPolicy()
    admitted_links = []
    for index, source in enumerate(propositions, start=1):
        result = evidence_policy.evaluate(
            episode_id=EPISODE_ID,
            proposal=EvidenceLinkProposal(
                proposition_id=source.id,
                target_type=CognitiveTargetType.HYPOTHESIS,
                target_id=draft.target_id,
                relation=EvidenceRelation.SUPPORTS,
                reason="matches the candidate explanation",
            ),
            propositions=propositions,
            targets=(draft,),
            staged_relations=tuple(admitted_links),
            evidence_id=EvidenceLinkId(f"e-c{index}"),
            created_at=NOW,
        )
        assert result.value is not None
        admitted_links.append(result.value)
    hypothesis_result = HypothesisAdmissionPolicy().evaluate(
        episode_id=EPISODE_ID,
        proposal=HypothesisProposal(
            statement="endpoint mismatch contributes to DB connectivity failure",
            target_problem="DB connectivity",
            supporting_proposition_ids=tuple(item.id for item in propositions),
            prediction="using the actual listener endpoint removes connection refusal",
        ),
        draft_target=draft,
        propositions=propositions,
        admitted_relations=tuple(admitted_links),
        created_at=NOW,
    )
    assert hypothesis_result.value is not None
    admission_tx = CognitiveTransaction(
        id=TransactionId("tx-c-admission"),
        episode_id=EPISODE_ID,
        base_version=1,
        object_changes=(
            object_change(
                hypothesis_result.value,
                CognitiveObjectType.HYPOTHESIS,
            ),
        ),
        relation_changes=tuple(
            RelationChange(kind=ChangeKind.CREATE, value=item)
            for item in admitted_links
        ),
    )

    asyncio.run(store.commit_transaction(admission_tx))
    state = asyncio.run(store.load_episode_state(EPISODE_ID))

    assert hypothesis_result.decision is AdmissionDecision.ADMIT
    assert state.hypotheses[0].status is HypothesisStatus.PLAUSIBLE
    assert state.hypotheses[0].evidence_refs == (
        EvidenceLinkId("e-c1"),
        EvidenceLinkId("e-c2"),
    )


@pytest.mark.scenario
def test_scenario_d_overlapping_active_fact_conflict_never_selects_a_winner() -> None:
    existing = Fact(
        id=FactId("f-d1"),
        episode_id=EPISODE_ID,
        statement="runtime port is 3306",
        subject="mysqld",
        predicate="runtime_port",
        value=3306,
        scope="host-A",
        valid_from=NOW,
        valid_to=NOW,
        basis=FactBasis.DIRECT_MEASUREMENT,
        evidence_refs=(EvidenceLinkId("e-d1"),),
        status=FactStatus.ACTIVE,
        created_at=NOW,
    )
    observed = Observation(
        id=ObservationId("o-d2"),
        episode_id=EPISODE_ID,
        source="shell:netstat",
        raw_content="mysqld listens on 3307",
        scope="host-A",
        observed_at=NOW,
        created_at=NOW,
    )
    proposition = ObservedProposition(
        id=PropositionId("p-d2"),
        episode_id=EPISODE_ID,
        observation_id=observed.id,
        statement="mysqld listens on 3307",
        subject="mysqld",
        predicate="runtime_port",
        value=3307,
        scope="host-A",
        observed_at=NOW,
        created_at=NOW,
    )

    conflict = FactAdmissionPolicy().evaluate(
        episode_id=EPISODE_ID,
        proposal=FactProposal(
            proposition_id=proposition.id,
            statement="runtime port is 3307",
            subject="mysqld",
            predicate="runtime_port",
            value=3307,
            scope="host-A",
            basis=FactBasis.DIRECT_MEASUREMENT,
            semantic_entailment=SemanticEntailment.EQUIVALENT_OR_NARROWER,
        ),
        proposition=proposition,
        observation=observed,
        draft_target=DraftTargetFactory.reserve_fact(
            EPISODE_ID, target_id=FactId("f-d2")
        ),
        evidence_id=EvidenceLinkId("e-d2"),
        created_at=NOW,
        existing_facts=(existing,),
    )

    assert conflict.decision is AdmissionDecision.REJECT
    assert conflict.reason_codes == (AdmissionReasonCode.FACT_CONFLICT,)
    assert conflict.value is None
    assert existing.status is FactStatus.ACTIVE
