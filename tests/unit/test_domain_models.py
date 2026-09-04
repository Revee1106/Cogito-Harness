from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cogito.domain.enums import (
    FactStatus,
    GapStatus,
    HypothesisStatus,
    PropositionStatus,
)
from cogito.domain.ids import (
    EpisodeId,
    EvidenceLinkId,
    FactId,
    GapId,
    HypothesisId,
    ObservationId,
    PropositionId,
)
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.goal import AcceptanceCriterion, GoalContract
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import Observation, ObservedProposition


NOW = datetime(2026, 1, 1, tzinfo=UTC)
EPISODE_ID = EpisodeId("00000000-0000-0000-0000-000000000001")
OBSERVATION_ID = ObservationId("00000000-0000-0000-0000-000000000002")
PROPOSITION_ID = PropositionId("00000000-0000-0000-0000-000000000003")


def test_domain_model_forbids_extra_fields_and_is_frozen() -> None:
    observation = Observation(
        id=OBSERVATION_ID,
        episode_id=EPISODE_ID,
        source="test",
        raw_content="listener reports port 3307",
        observed_at=NOW,
        created_at=NOW,
    )

    with pytest.raises(ValidationError):
        Observation(
            id=OBSERVATION_ID,
            episode_id=EPISODE_ID,
            source="test",
            raw_content="listener reports port 3307",
            observed_at=NOW,
            created_at=NOW,
            unexpected=True,
        )
    with pytest.raises(ValidationError):
        observation.source = "changed"

    changed = observation.model_copy(update={"source": "fixture"})
    assert observation.source == "test"
    assert changed.source == "fixture"


def test_goal_contract_preserves_version_and_validates_criteria() -> None:
    criterion = AcceptanceCriterion(
        id="criterion-1", statement="identify the listener port"
    )
    goal = GoalContract(
        objective="diagnose DB connectivity",
        hard_constraints=("read only",),
        acceptance_criteria=(criterion,),
        version=2,
    )

    assert goal.version == 2
    assert goal.acceptance_criteria == (criterion,)
    with pytest.raises(ValidationError):
        AcceptanceCriterion(id="", statement="valid statement")
    with pytest.raises(ValidationError):
        GoalContract(
            objective="diagnose",
            hard_constraints=(),
            acceptance_criteria=(),
            version=0,
        )


def test_observation_and_observed_proposition_are_distinct_types() -> None:
    observation = Observation(
        id=OBSERVATION_ID,
        episode_id=EPISODE_ID,
        source="fake-tool",
        raw_content="DB listens on 3307",
        observed_at=NOW,
        created_at=NOW,
    )
    proposition = ObservedProposition(
        id=PROPOSITION_ID,
        episode_id=EPISODE_ID,
        observation_id=observation.id,
        statement="DB listener port is 3307",
        subject="db.listener",
        predicate="port",
        value="3307",
        status=PropositionStatus.ACTIVE,
        observed_at=NOW,
        created_at=NOW,
    )

    assert type(observation) is not type(proposition)
    assert proposition.observation_id == observation.id


def test_fact_hypothesis_gap_and_evidence_validation() -> None:
    fact = Fact(
        id=FactId("00000000-0000-0000-0000-000000000004"),
        episode_id=EPISODE_ID,
        statement="configured DB port is 3306",
        evidence_refs=(PROPOSITION_ID,),
        status=FactStatus.ACTIVE,
        created_at=NOW,
    )
    hypothesis = Hypothesis(
        id=HypothesisId("00000000-0000-0000-0000-000000000005"),
        episode_id=EPISODE_ID,
        statement="port mismatch causes connectivity failure",
        target_problem="DB connectivity",
        evidence_refs=(EvidenceLinkId("00000000-0000-0000-0000-000000000006"),),
        prediction="client port differs from listener port",
        status=HypothesisStatus.SUPPORTED,
        created_at=NOW,
        updated_at=NOW,
    )
    gap = InformationGap(
        id=GapId("00000000-0000-0000-0000-000000000007"),
        episode_id=EPISODE_ID,
        question="Which port is listening?",
        why_it_matters="Discriminates the mismatch hypothesis",
        target_hypothesis_id=hypothesis.id,
        status=GapStatus.FOCUSED,
        created_at=NOW,
    )
    evidence = EvidenceLink(
        id=EvidenceLinkId("00000000-0000-0000-0000-000000000008"),
        episode_id=EPISODE_ID,
        proposition_id=PROPOSITION_ID,
        target_type="HYPOTHESIS",
        target_id=str(hypothesis.id),
        relation="SUPPORTS",
        reason="Observed listener differs from configured port",
        created_at=NOW,
    )

    assert fact.status is FactStatus.ACTIVE
    assert hypothesis.status is HypothesisStatus.SUPPORTED
    assert gap.status is GapStatus.FOCUSED
    assert evidence.target_type.value == "HYPOTHESIS"

    with pytest.raises(ValidationError):
        Hypothesis(
            id=hypothesis.id,
            episode_id=EPISODE_ID,
            statement="bad",
            target_problem="problem",
            evidence_refs=(),
            status="CERTAIN",
            created_at=NOW,
            updated_at=NOW,
        )
    with pytest.raises(ValidationError):
        InformationGap.model_validate({**gap.model_dump(), "status": "DONE"})
    with pytest.raises(ValidationError):
        EvidenceLink.model_validate({**evidence.model_dump(), "target_type": "MEMORY"})
