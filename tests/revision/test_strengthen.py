import pytest
from pydantic import ValidationError

from cogito.domain.enums import HypothesisStatus, PropositionStatus, EvidenceRelation
from .fixtures import NOW, state, replace_item, event


def evaluate(s=None, **updates):
    from cogito.domain.proposals.revision import HypothesisStrengthenProposal
    from cogito.domain.policies.revision_hypothesis import HypothesisStrengthenPolicy
    args = dict(hypothesis_id="h1", evidence_link_ids=("e1",),
                support_basis="DIRECT_OBSERVATION", reason="measurement touches claim")
    args.update(updates)
    return HypothesisStrengthenPolicy().evaluate(s or state(), HypothesisStrengthenProposal(**args), now=NOW)


def test_direct_observation_strengthens_without_mutating_input():
    s = state()
    result = evaluate(s)
    assert result.status == "MATERIAL_CHANGE"
    assert result.value.status is HypothesisStatus.SUPPORTED
    assert s.hypotheses[0].status is HypothesisStatus.PLAUSIBLE
    assert result.event_type == "HYPOTHESIS_STRENGTHENED"


def test_new_support_is_material_but_consumed_subset_or_reordering_is_not():
    s = replace_item(state(), "hypotheses", 0, status=HypothesisStatus.SUPPORTED)
    assert evaluate(s, evidence_link_ids=("e2",)).status == "MATERIAL_CHANGE"
    first = evaluate(s, evidence_link_ids=("e1", "e2"))
    committed = event(first.event_type, first.payload, 20, tx="revision")
    s = s.model_copy(update={"cognitive_events":s.cognitive_events+(committed,)})
    for ids in (("e1",), ("e2", "e1"), ("e1", "e1")):
        assert evaluate(s, evidence_link_ids=ids).status == "NO_MATERIAL_CHANGE"


@pytest.mark.parametrize("field,index,updates,reason", [
    ("evidence_links",0,{"target_id":"other"},"EVIDENCE_TARGET_MISMATCH"),
    ("evidence_links",0,{"relation":EvidenceRelation.CONTRADICTS},"EVIDENCE_RELATION_INVALID"),
    ("observed_propositions",0,{"status":PropositionStatus.RETRACTED},"PROPOSITION_INACTIVE"),
    ("observed_propositions",0,{"episode_id":"other"},"EPISODE_MISMATCH"),
    ("evidence_links",0,{"episode_id":"other"},"EPISODE_MISMATCH"),
    ("hypotheses",0,{"episode_id":"other"},"EPISODE_MISMATCH"),
    ("hypotheses",0,{"status":HypothesisStatus.REJECTED},"TARGET_STATUS_INVALID"),
    ("recent_observations",0,{"source":"user speculation"},"INSUFFICIENT_REVISION_BASIS"),
])
def test_invalid_basis_cannot_strengthen(field,index,updates,reason):
    result = evaluate(replace_item(state(),field,index,**updates))
    assert result.status == "DEFERRED"
    assert reason in result.reason_codes


@pytest.mark.parametrize("ids", [("e1",), ("e1","e1")])
def test_corroboration_requires_distinct_propositions(ids):
    assert "INSUFFICIENT_CORROBORATION" in evaluate(
        evidence_link_ids=ids,support_basis="INDEPENDENT_CORROBORATION").reason_codes


def test_corroboration_checks_available_acquisition_paths():
    assert evaluate(evidence_link_ids=("e1","e2"),support_basis="INDEPENDENT_CORROBORATION").status == "MATERIAL_CHANGE"
    s = replace_item(state(),"recent_observations",1,source_ref="sensor-1")
    assert evaluate(s,evidence_link_ids=("e1","e2"),support_basis="INDEPENDENT_CORROBORATION").status == "DEFERRED"


def test_prediction_consistency_requires_prediction_and_never_confirms():
    assert evaluate(support_basis="PREDICTION_CONSISTENT").value.status == "SUPPORTED"
    s = replace_item(state(),"hypotheses",0,prediction=None)
    assert "MISSING_PREDICTION" in evaluate(s,support_basis="PREDICTION_CONSISTENT").reason_codes


def test_discriminative_evidence_uses_explicit_proposal():
    assert evaluate(support_basis="DISCRIMINATIVE_EVIDENCE").status == "MATERIAL_CHANGE"


@pytest.mark.parametrize("updates", [{"reason":"   "},{"support_basis":"CONFIDENCE"},{"evidence_link_ids":()}])
def test_proposal_rejects_invalid_shape(updates):
    with pytest.raises(ValidationError):
        evaluate(**updates)


def test_missing_target_and_evidence_are_explicit():
    assert "TARGET_NOT_FOUND" in evaluate(hypothesis_id="missing").reason_codes
    assert "EVIDENCE_NOT_FOUND" in evaluate(evidence_link_ids=("missing",)).reason_codes
