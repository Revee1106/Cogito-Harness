from __future__ import annotations

from datetime import UTC, datetime

import pytest

from cogito.domain.enums import (
    AdmissionDecision,
    AdmissionReasonCode,
    CognitiveTargetType,
    EvidenceRelation,
    FactBasis,
    HypothesisStatus,
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
from cogito.domain.models.draft import DraftTargetFactory
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import ObservedProposition
from cogito.domain.policies.evidence import EvidenceAdmissionPolicy
from cogito.domain.proposals.evidence import EvidenceLinkProposal


NOW = datetime(2026, 1, 1, tzinfo=UTC)
EPISODE_ID = EpisodeId("episode-1")


def proposition(
    *, proposition_id: str = "p1", episode_id: EpisodeId = EPISODE_ID
) -> ObservedProposition:
    return ObservedProposition(
        id=PropositionId(proposition_id),
        episode_id=episode_id,
        observation_id=ObservationId(f"o-{proposition_id}"),
        statement="measured signal",
        observed_at=NOW,
        created_at=NOW,
    )


def fact(*, fact_id: str = "f1", episode_id: EpisodeId = EPISODE_ID) -> Fact:
    return Fact(
        id=FactId(fact_id),
        episode_id=episode_id,
        statement="measured fact",
        basis=FactBasis.DIRECT_MEASUREMENT,
        evidence_refs=(EvidenceLinkId("prior-evidence"),),
        created_at=NOW,
    )


def hypothesis(
    *, hypothesis_id: str = "h1", episode_id: EpisodeId = EPISODE_ID
) -> Hypothesis:
    return Hypothesis(
        id=HypothesisId(hypothesis_id),
        episode_id=episode_id,
        statement="candidate explanation",
        target_problem="problem",
        evidence_refs=(EvidenceLinkId("prior-evidence"),),
        prediction="testable outcome",
        status=HypothesisStatus.PLAUSIBLE,
        created_at=NOW,
        updated_at=NOW,
    )


def gap(*, gap_id: str = "g1", episode_id: EpisodeId = EPISODE_ID) -> InformationGap:
    return InformationGap(
        id=GapId(gap_id),
        episode_id=episode_id,
        question="what is missing?",
        why_it_matters="resolves the active inquiry",
        created_at=NOW,
    )


def admit(
    target,
    relation: EvidenceRelation,
    *,
    declared_type: CognitiveTargetType | None = None,
    propositions: tuple[ObservedProposition, ...] | None = None,
    existing: tuple[EvidenceLink, ...] = (),
    staged: tuple[EvidenceLink, ...] = (),
):
    target_type = declared_type or (
        target.target_type
        if hasattr(target, "target_type")
        else {
            Fact: CognitiveTargetType.FACT,
            Hypothesis: CognitiveTargetType.HYPOTHESIS,
            InformationGap: CognitiveTargetType.GAP,
        }[type(target)]
    )
    return EvidenceAdmissionPolicy().evaluate(
        episode_id=EPISODE_ID,
        proposal=EvidenceLinkProposal(
            proposition_id=PropositionId("p1"),
            target_type=target_type,
            target_id=target.target_id if hasattr(target, "target_id") else str(target.id),
            relation=relation,
            reason="fixture semantic evaluation",
        ),
        propositions=(proposition(),) if propositions is None else propositions,
        targets=(target,),
        existing_relations=existing,
        staged_relations=staged,
        evidence_id=EvidenceLinkId("e-new"),
        created_at=NOW,
    )


@pytest.mark.parametrize(
    ("target", "relation"),
    (
        (fact(), EvidenceRelation.SUPPORTS),
        (fact(), EvidenceRelation.CONTRADICTS),
        (hypothesis(), EvidenceRelation.SUPPORTS),
        (hypothesis(), EvidenceRelation.CONTRADICTS),
        (gap(), EvidenceRelation.RESOLVES),
    ),
)
def test_relation_matrix_admits_only_material_compatible_links(target, relation) -> None:
    result = admit(target, relation)

    assert result.decision is AdmissionDecision.ADMIT
    assert result.value is not None
    assert result.value.relation is relation


@pytest.mark.parametrize(
    ("target", "relation"),
    (
        (gap(), EvidenceRelation.SUPPORTS),
        (hypothesis(), EvidenceRelation.RESOLVES),
        (fact(), EvidenceRelation.RESOLVES),
    ),
)
def test_relation_matrix_rejects_illegal_combinations(target, relation) -> None:
    result = admit(target, relation)

    assert result.decision is AdmissionDecision.REJECT
    assert result.reason_codes == (AdmissionReasonCode.RELATION_NOT_ALLOWED,)


def test_neutral_is_a_non_committing_outcome() -> None:
    result = admit(fact(), EvidenceRelation.NEUTRAL)

    assert result.decision is AdmissionDecision.NO_NEW_ADMISSION
    assert result.value is None
    assert result.reason_codes == (AdmissionReasonCode.NEUTRAL_EVIDENCE,)


def test_missing_source_and_target_type_mismatch_are_rejected() -> None:
    missing = admit(fact(), EvidenceRelation.SUPPORTS, propositions=())
    mismatch = admit(
        fact(),
        EvidenceRelation.SUPPORTS,
        declared_type=CognitiveTargetType.HYPOTHESIS,
    )

    assert missing.reason_codes == (AdmissionReasonCode.SOURCE_NOT_FOUND,)
    assert mismatch.reason_codes == (AdmissionReasonCode.TARGET_TYPE_MISMATCH,)


def test_missing_target_and_cross_episode_are_rejected() -> None:
    missing_target = EvidenceAdmissionPolicy().evaluate(
        episode_id=EPISODE_ID,
        proposal=EvidenceLinkProposal(
            proposition_id=PropositionId("p1"),
            target_type=CognitiveTargetType.FACT,
            target_id="missing",
            relation=EvidenceRelation.SUPPORTS,
            reason="fixture",
        ),
        propositions=(proposition(),),
        targets=(),
        evidence_id=EvidenceLinkId("e-new"),
        created_at=NOW,
    )
    cross_episode = admit(
        fact(episode_id=EpisodeId("episode-2")), EvidenceRelation.SUPPORTS
    )

    assert missing_target.reason_codes == (AdmissionReasonCode.TARGET_NOT_FOUND,)
    assert cross_episode.reason_codes == (AdmissionReasonCode.EPISODE_MISMATCH,)


def test_duplicate_and_opposite_material_relation_are_not_admitted() -> None:
    prior = EvidenceLink(
        id=EvidenceLinkId("e-prior"),
        episode_id=EPISODE_ID,
        proposition_id=PropositionId("p1"),
        target_type=CognitiveTargetType.FACT,
        target_id="f1",
        relation=EvidenceRelation.SUPPORTS,
        reason="prior",
        created_at=NOW,
    )

    duplicate = admit(fact(), EvidenceRelation.SUPPORTS, existing=(prior,))
    conflict = admit(fact(), EvidenceRelation.CONTRADICTS, staged=(prior,))

    assert duplicate.decision is AdmissionDecision.NO_NEW_ADMISSION
    assert duplicate.reason_codes == (AdmissionReasonCode.DUPLICATE_EVIDENCE,)
    assert conflict.decision is AdmissionDecision.REJECT
    assert conflict.reason_codes == (AdmissionReasonCode.RELATION_CONFLICT,)


def test_reserved_draft_target_is_admissible_before_commit() -> None:
    draft = DraftTargetFactory.reserve_hypothesis(
        EPISODE_ID, target_id=HypothesisId("reserved-h1")
    )

    result = admit(draft, EvidenceRelation.SUPPORTS)

    assert result.decision is AdmissionDecision.ADMIT
    assert result.value is not None
    assert result.value.target_id == "reserved-h1"
    assert draft.committed is False
