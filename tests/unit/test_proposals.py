from __future__ import annotations

from cogito.domain.ids import EvidenceLinkId, HypothesisId, ObservationId, PropositionId
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import ObservedProposition
from cogito.domain.proposals.action import ActionProposal
from cogito.domain.proposals.contract import GoalInterpretationProposal
from cogito.domain.proposals.evidence import EvidenceLinkProposal
from cogito.domain.proposals.gap import GapProposal
from cogito.domain.proposals.hypothesis import HypothesisProposal
from cogito.domain.proposals.proposition import ObservedPropositionProposal


def test_all_proposals_omit_database_identity_and_timestamps() -> None:
    proposals = (
        GoalInterpretationProposal(
            objective="diagnose", hard_constraints=("read only",),
            acceptance_criteria=("root cause identified",)
        ),
        ObservedPropositionProposal(
            observation_id=ObservationId("o1"), statement="DB listens on 3307"
        ),
        EvidenceLinkProposal(
            proposition_id=PropositionId("p1"), target_type="HYPOTHESIS",
            target_id="h1", relation="SUPPORTS", reason="matches prediction"
        ),
        HypothesisProposal(
            statement="port mismatch", target_problem="connectivity",
            supporting_evidence_ids=(EvidenceLinkId("e1"),),
            prediction="ports differ"
        ),
        GapProposal(
            question="which port?", why_it_matters="tests mismatch",
            target_hypothesis_id=HypothesisId("h1")
        ),
        ActionProposal(
            kind="TOOL", purpose="inspect listener", expected_observation="listener port",
            tool_name="inspect_listener", arguments={}, risk="READ_ONLY"
        ),
    )

    for proposal in proposals:
        assert "id" not in type(proposal).model_fields
        assert "created_at" not in type(proposal).model_fields


def test_proposals_are_not_committed_domain_objects() -> None:
    assert not issubclass(ObservedPropositionProposal, ObservedProposition)
    assert not issubclass(EvidenceLinkProposal, EvidenceLink)
    assert not issubclass(HypothesisProposal, Hypothesis)
