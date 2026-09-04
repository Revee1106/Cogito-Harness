from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from cogito.domain.enums import (
    AdmissionDecision,
    AdmissionReasonCode,
    FactBasis,
    FactStatus,
    PropositionStatus,
    SemanticEntailment,
)
from cogito.domain.ids import (
    EpisodeId,
    EvidenceLinkId,
    FactId,
    ObservationId,
    PropositionId,
)
from cogito.domain.models.draft import DraftTargetFactory
from cogito.domain.models.fact import Fact
from cogito.domain.models.observation import Observation, ObservedProposition
from cogito.domain.policies.fact import FactAdmissionPolicy
from cogito.domain.proposals.fact import FactProposal


NOW = datetime(2026, 1, 1, tzinfo=UTC)
EPISODE_ID = EpisodeId("episode-1")


def observation(
    source: str = "shell:netstat", *, episode_id: EpisodeId = EPISODE_ID
) -> Observation:
    return Observation(
        id=ObservationId("o1"),
        episode_id=episode_id,
        source=source,
        raw_content="mysqld LISTEN 0.0.0.0:3307",
        scope="host-A",
        observed_at=NOW,
        created_at=NOW,
    )


def proposition(
    *,
    episode_id: EpisodeId = EPISODE_ID,
    status: PropositionStatus = PropositionStatus.ACTIVE,
    scope: str | None = "host-A",
    predicate: str = "runtime_port",
) -> ObservedProposition:
    return ObservedProposition(
        id=PropositionId("p1"),
        episode_id=episode_id,
        observation_id=ObservationId("o1"),
        statement="mysqld listens on 3307 on host-A at T1",
        subject="mysqld",
        predicate=predicate,
        value=3307,
        scope=scope,
        observed_at=NOW,
        status=status,
        created_at=NOW,
    )


def proposal(
    *,
    basis: FactBasis = FactBasis.DIRECT_MEASUREMENT,
    entailment: SemanticEntailment = SemanticEntailment.EQUIVALENT_OR_NARROWER,
    scope: str | None = "host-A",
    valid_from: datetime | None = None,
    valid_to: datetime | None = None,
    predicate: str = "runtime_port",
    value=3307,
) -> FactProposal:
    return FactProposal(
        proposition_id=PropositionId("p1"),
        statement="mysqld runtime listener port is 3307",
        subject="mysqld",
        predicate=predicate,
        value=value,
        scope=scope,
        valid_from=valid_from,
        valid_to=valid_to,
        basis=basis,
        semantic_entailment=entailment,
    )


def evaluate(
    candidate: FactProposal,
    *,
    source_observation: Observation | None = None,
    source_proposition: ObservedProposition | None = None,
    existing_facts: tuple[Fact, ...] = (),
):
    draft = DraftTargetFactory.reserve_fact(
        EPISODE_ID, target_id=FactId("reserved-f1")
    )
    return FactAdmissionPolicy().evaluate(
        episode_id=EPISODE_ID,
        proposal=candidate,
        proposition=proposition() if source_proposition is None else source_proposition,
        observation=observation() if source_observation is None else source_observation,
        draft_target=draft,
        evidence_id=EvidenceLinkId("e1"),
        created_at=NOW,
        existing_facts=existing_facts,
    )


def test_equivalent_direct_measurement_admits_atomic_fact_and_evidence_bundle() -> None:
    result = evaluate(proposal())

    assert result.decision is AdmissionDecision.ADMIT
    assert result.value is not None
    assert result.value.fact.id == FactId("reserved-f1")
    assert result.value.fact.status is FactStatus.ACTIVE
    assert result.value.fact.basis is FactBasis.DIRECT_MEASUREMENT
    assert result.value.fact.valid_from == NOW
    assert result.value.fact.valid_to == NOW
    assert result.value.fact.evidence_refs == (EvidenceLinkId("e1"),)
    assert result.value.evidence_link.target_id == "reserved-f1"
    assert result.value.evidence_link.relation.value == "SUPPORTS"


def test_stronger_claim_rejects_and_ambiguous_claim_defers() -> None:
    stronger = evaluate(
        proposal(entailment=SemanticEntailment.STRONGER_THAN_SOURCE)
    )
    ambiguous = evaluate(proposal(entailment=SemanticEntailment.AMBIGUOUS))

    assert stronger.decision is AdmissionDecision.REJECT
    assert stronger.reason_codes == (AdmissionReasonCode.CLAIM_TOO_STRONG,)
    assert ambiguous.decision is AdmissionDecision.DEFER
    assert ambiguous.reason_codes == (AdmissionReasonCode.SEMANTIC_AMBIGUITY,)


def test_missing_inactive_and_cross_episode_propositions_are_rejected() -> None:
    missing = FactAdmissionPolicy().evaluate(
        episode_id=EPISODE_ID,
        proposal=proposal(),
        proposition=None,
        observation=observation(),
        draft_target=DraftTargetFactory.reserve_fact(EPISODE_ID),
        evidence_id=EvidenceLinkId("e1"),
        created_at=NOW,
    )
    inactive = evaluate(
        proposal(),
        source_proposition=proposition(status=PropositionStatus.RETRACTED),
    )
    cross_episode = evaluate(
        proposal(),
        source_proposition=proposition(episode_id=EpisodeId("episode-2")),
    )

    assert missing.reason_codes == (AdmissionReasonCode.SOURCE_NOT_FOUND,)
    assert inactive.reason_codes == (AdmissionReasonCode.PROPOSITION_INACTIVE,)
    assert cross_episode.reason_codes == (AdmissionReasonCode.EPISODE_MISMATCH,)


def test_scope_expansion_and_temporal_overreach_are_rejected() -> None:
    expanded = evaluate(proposal(scope=None))
    overreach = evaluate(
        proposal(valid_from=NOW - timedelta(seconds=1), valid_to=NOW)
    )

    assert expanded.reason_codes == (AdmissionReasonCode.SCOPE_EXPANDED,)
    assert overreach.reason_codes == (AdmissionReasonCode.TEMPORAL_SCOPE_INVALID,)


@pytest.mark.parametrize(
    ("source", "basis"),
    (
        ("user-report", FactBasis.SOURCE_REPORT),
        ("artifact:application.yml", FactBasis.ARTIFACT_CONTENT),
        ("shell:netstat", FactBasis.DIRECT_MEASUREMENT),
        ("deterministic-rule:port-mismatch", FactBasis.DETERMINISTIC_DERIVATION),
    ),
)
def test_fact_basis_must_fit_the_source_context(source: str, basis: FactBasis) -> None:
    admitted = evaluate(proposal(basis=basis), source_observation=observation(source))
    mismatched = evaluate(
        proposal(basis=basis),
        source_observation=observation("unqualified-source"),
    )

    assert admitted.decision is AdmissionDecision.ADMIT
    assert mismatched.reason_codes == (
        AdmissionReasonCode.SOURCE_FITNESS_INSUFFICIENT,
    )


def test_fact_admission_rejects_new_causal_explanation() -> None:
    result = evaluate(proposal(predicate="causes", value="connectivity failure"))

    assert result.reason_codes == (AdmissionReasonCode.NON_EXPLANATORY_BOUNDARY,)


def test_overlapping_active_fact_with_incompatible_value_reports_conflict() -> None:
    existing = Fact(
        id=FactId("existing-fact"),
        episode_id=EPISODE_ID,
        statement="mysqld runtime listener port is 3306",
        subject="mysqld",
        predicate="runtime_port",
        value=3306,
        scope="host-A",
        valid_from=NOW,
        valid_to=NOW,
        basis=FactBasis.DIRECT_MEASUREMENT,
        evidence_refs=(EvidenceLinkId("existing-evidence"),),
        status=FactStatus.ACTIVE,
        created_at=NOW,
    )

    result = evaluate(proposal(value=3307), existing_facts=(existing,))

    assert result.decision is AdmissionDecision.REJECT
    assert result.reason_codes == (AdmissionReasonCode.FACT_CONFLICT,)
    assert existing.status is FactStatus.ACTIVE
