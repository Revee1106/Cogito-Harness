from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cogito.domain.enums import (
    AdmissionDecision,
    AdmissionReasonCode,
    CognitiveTargetType,
    EvidenceRelation,
    HypothesisStatus,
)
from cogito.domain.ids import (
    EpisodeId,
    EvidenceLinkId,
    HypothesisId,
    ObservationId,
    PropositionId,
)
from cogito.domain.models.draft import DraftTargetFactory
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.observation import ObservedProposition
from cogito.domain.policies.hypothesis import HypothesisAdmissionPolicy
from cogito.domain.proposals.hypothesis import HypothesisProposal


NOW = datetime(2026, 1, 1, tzinfo=UTC)
EPISODE_ID = EpisodeId("episode-1")
DRAFT = DraftTargetFactory.reserve_hypothesis(
    EPISODE_ID, target_id=HypothesisId("reserved-h1")
)


def proposition(
    proposition_id: str, *, episode_id: EpisodeId = EPISODE_ID
) -> ObservedProposition:
    return ObservedProposition(
        id=PropositionId(proposition_id),
        episode_id=episode_id,
        observation_id=ObservationId(f"o-{proposition_id}"),
        statement=f"observed {proposition_id}",
        observed_at=NOW,
        created_at=NOW,
    )


def evidence(
    proposition_id: str,
    *,
    evidence_id: str = "e1",
    relation: EvidenceRelation = EvidenceRelation.SUPPORTS,
    episode_id: EpisodeId = EPISODE_ID,
) -> EvidenceLink:
    return EvidenceLink(
        id=EvidenceLinkId(evidence_id),
        episode_id=episode_id,
        proposition_id=PropositionId(proposition_id),
        target_type=CognitiveTargetType.HYPOTHESIS,
        target_id=DRAFT.target_id,
        relation=relation,
        reason="fixture semantic evaluation",
        created_at=NOW,
    )


def proposal(
    *,
    supporting: tuple[PropositionId, ...] = (PropositionId("p1"),),
    prediction: str | None = "using the actual endpoint removes refusal",
    disconfirming_condition: str | None = None,
) -> HypothesisProposal:
    return HypothesisProposal(
        statement="endpoint mismatch contributes to connectivity failure",
        target_problem="DB connectivity",
        supporting_proposition_ids=supporting,
        prediction=prediction,
        disconfirming_condition=disconfirming_condition,
    )


def evaluate(
    candidate: HypothesisProposal,
    *,
    propositions: tuple[ObservedProposition, ...] = (proposition("p1"),),
    relations: tuple[EvidenceLink, ...] = (evidence("p1"),),
):
    return HypothesisAdmissionPolicy().evaluate(
        episode_id=EPISODE_ID,
        proposal=candidate,
        draft_target=DRAFT,
        propositions=propositions,
        admitted_relations=relations,
        created_at=NOW,
    )


def test_no_candidate_proposition_is_rejected() -> None:
    result = evaluate(proposal(supporting=()), propositions=(), relations=())

    assert result.decision is AdmissionDecision.REJECT
    assert result.reason_codes == (AdmissionReasonCode.NO_SUPPORTING_PROPOSITION,)


def test_candidate_proposition_does_not_automatically_become_evidence() -> None:
    result = evaluate(proposal(), relations=())

    assert result.decision is AdmissionDecision.REJECT
    assert result.reason_codes == (AdmissionReasonCode.NO_SUPPORTING_EVIDENCE,)


def test_only_supports_relation_to_reserved_target_counts_as_admitted_evidence() -> None:
    contradicts = evaluate(
        proposal(),
        relations=(evidence("p1", relation=EvidenceRelation.CONTRADICTS),),
    )
    wrong_target = evidence("p1").model_copy(update={"target_id": "other-h"})
    other = evaluate(proposal(), relations=(wrong_target,))

    assert contradicts.reason_codes == (AdmissionReasonCode.NO_SUPPORTING_EVIDENCE,)
    assert other.reason_codes == (AdmissionReasonCode.NO_SUPPORTING_EVIDENCE,)


def test_cross_episode_proposition_or_evidence_is_rejected() -> None:
    other_episode = EpisodeId("episode-2")
    cross_source = evaluate(
        proposal(),
        propositions=(proposition("p1", episode_id=other_episode),),
    )
    cross_evidence = evaluate(
        proposal(),
        relations=(evidence("p1", episode_id=other_episode),),
    )

    assert cross_source.reason_codes == (AdmissionReasonCode.EPISODE_MISMATCH,)
    assert cross_evidence.reason_codes == (AdmissionReasonCode.EPISODE_MISMATCH,)


def test_missing_prediction_and_disconfirming_condition_is_rejected() -> None:
    result = evaluate(proposal(prediction=None, disconfirming_condition=None))

    assert result.reason_codes == (
        AdmissionReasonCode.MISSING_TESTABLE_EXPECTATION,
    )


def test_valid_evidence_backed_proposal_creates_only_plausible_hypothesis() -> None:
    result = evaluate(
        proposal(supporting=(PropositionId("p1"), PropositionId("p2"))),
        propositions=(proposition("p1"), proposition("p2")),
        relations=(evidence("p1", evidence_id="e1"), evidence("p2", evidence_id="e2")),
    )

    assert result.decision is AdmissionDecision.ADMIT
    assert result.value is not None
    assert result.value.id == HypothesisId("reserved-h1")
    assert result.value.status is HypothesisStatus.PLAUSIBLE
    assert result.value.evidence_refs == (
        EvidenceLinkId("e1"),
        EvidenceLinkId("e2"),
    )


@pytest.mark.parametrize("forbidden", ("SUPPORTED", "CONFIRMED", "REJECTED"))
def test_hypothesis_proposal_cannot_request_a_committed_status(forbidden: str) -> None:
    with pytest.raises(ValidationError):
        HypothesisProposal(
            statement="candidate",
            target_problem="problem",
            supporting_proposition_ids=(PropositionId("p1"),),
            prediction="test",
            status=forbidden,
        )
