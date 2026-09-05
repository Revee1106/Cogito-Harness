from __future__ import annotations

from cogito.domain.enums import FactBasis, SemanticEntailment
from cogito.domain.ids import HypothesisId, ObservationId, PropositionId
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import ObservedProposition
from cogito.domain.proposals.action import ActionProposal
from cogito.domain.proposals.contract import GoalInterpretationProposal
from cogito.domain.proposals.evidence import EvidenceLinkProposal
from cogito.domain.proposals.fact import FactProposal
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
            supporting_proposition_ids=(PropositionId("p1"),),
            prediction="ports differ"
        ),
        FactProposal(
            proposition_id=PropositionId("p1"),
            statement="DB listens on 3307",
            subject="db.listener",
            predicate="port",
            value=3307,
            scope="host-A",
            basis=FactBasis.DIRECT_MEASUREMENT,
            semantic_entailment=SemanticEntailment.EQUIVALENT_OR_NARROWER,
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


def test_hypothesis_proposal_names_candidate_propositions_not_evidence() -> None:
    proposal = HypothesisProposal(
        statement="endpoint mismatch contributes to connectivity failure",
        target_problem="DB connectivity",
        supporting_proposition_ids=(PropositionId("p1"), PropositionId("p2")),
        prediction="using the listener endpoint removes connection refusal",
    )

    assert proposal.supporting_proposition_ids == (
        PropositionId("p1"),
        PropositionId("p2"),
    )
    assert "supporting_evidence_ids" not in type(proposal).model_fields
