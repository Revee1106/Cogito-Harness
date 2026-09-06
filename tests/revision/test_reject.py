import pytest
from pydantic import ValidationError
from cogito.domain.enums import HypothesisStatus, PropositionStatus, EvidenceRelation, EventType
from .fixtures import NOW, state, replace_item


def evaluate(s=None, **updates):
    from cogito.domain.proposals.revision import HypothesisRejectProposal
    from cogito.domain.policies.revision_hypothesis import HypothesisRejectPolicy
    args = dict(hypothesis_id="h1", evidence_link_ids=("e3",),
                rejection_basis="DIRECT_CONTRADICTION", semantic_directness="DIRECT",
                reason="directly falsifies the claim")
    args.update(updates)
    return HypothesisRejectPolicy().evaluate(s or state(), HypothesisRejectProposal(**args), now=NOW)


def test_direct_reject_preserves_support_and_records_basis():
    s = replace_item(state(),"hypotheses",0,status=HypothesisStatus.SUPPORTED)
    r = evaluate(s)
    assert r.status == "MATERIAL_CHANGE"
    assert r.value.status == "REJECTED"
    assert r.value.evidence_refs == s.hypotheses[0].evidence_refs
    assert r.payload["basis_evidence_ids"] == ["e3"]
    assert r.payload["basis"] == "DIRECT_CONTRADICTION"
    assert r.event_type == "HYPOTHESIS_REJECTED"
    assert s.evidence_links == state().evidence_links


@pytest.mark.parametrize("directness,reason", [
    ("NOT_DIRECT","INSUFFICIENT_REVISION_BASIS"),
    ("AMBIGUOUS","AMBIGUOUS_DIRECTNESS"),
])
def test_contradicts_is_not_sufficient(directness,reason):
    r = evaluate(semantic_directness=directness)
    assert r.status == "DEFERRED" and r.value is None
    assert reason in r.reason_codes


def test_default_directness_is_ambiguous():
    assert evaluate(semantic_directness=None).status == "DEFERRED"


def test_condition_proven_to_precede_all_triggering_evidence():
    assert evaluate(rejection_basis="DISCONFIRMING_CONDITION_MET").status == "MATERIAL_CHANGE"


@pytest.mark.parametrize("history_change", ["missing", "late", "same_transaction", "wrong_snapshot", "no_observation_event", "other_episode"])
def test_unproven_or_posthoc_condition_defers(history_change):
    s = state()
    history = list(s.cognitive_events)
    if history_change == "missing":
        history[0] = history[0].model_copy(update={"payload":{"object_id":"h1"}})
    elif history_change == "late":
        history[0] = history[0].model_copy(update={"sequence":100})
    elif history_change == "same_transaction":
        history[0] = history[0].model_copy(update={"transaction_id":"evidence"})
    elif history_change == "wrong_snapshot":
        history[0] = history[0].model_copy(update={"payload":{"object_id":"h1","disconfirming_condition":"posthoc"}})
    elif history_change == "no_observation_event":
        history = [e for e in history if not (e.event_type is EventType.OBSERVATION_ADDED and e.payload.get("object_id") == "o3")]
    else:
        history[0] = history[0].model_copy(update={"episode_id":"other"})
    r = evaluate(s.model_copy(update={"cognitive_events":tuple(history)}),rejection_basis="DISCONFIRMING_CONDITION_MET")
    assert r.status == "DEFERRED"
    assert "DISCONFIRMING_CONDITION_NOT_PRIOR" in r.reason_codes


def test_missing_condition_and_duplicate_rejection():
    s = replace_item(state(),"hypotheses",0,disconfirming_condition=None)
    assert "DISCONFIRMING_CONDITION_MISSING" in evaluate(s,rejection_basis="DISCONFIRMING_CONDITION_MET").reason_codes
    rejected = replace_item(state(),"hypotheses",0,status=HypothesisStatus.REJECTED)
    assert evaluate(rejected).status == "NO_MATERIAL_CHANGE"


@pytest.mark.parametrize("basis", ["BETTER_COMPETITOR","LOW_CONFIDENCE","INSUFFICIENT_SUPPORT","PREDICTION_FAILURE"])
def test_invalid_rejection_bases_are_unrepresentable(basis):
    with pytest.raises(ValidationError):
        evaluate(rejection_basis=basis)


@pytest.mark.parametrize("field,index,updates,code", [
    ("evidence_links",2,{"relation":EvidenceRelation.SUPPORTS},"EVIDENCE_RELATION_INVALID"),
    ("evidence_links",2,{"target_id":"other"},"EVIDENCE_TARGET_MISMATCH"),
    ("observed_propositions",2,{"status":PropositionStatus.SUPERSEDED},"PROPOSITION_INACTIVE"),
    ("evidence_links",2,{"episode_id":"other"},"EPISODE_MISMATCH"),
])
def test_reject_structural_defenses(field,index,updates,code):
    r = evaluate(replace_item(state(),field,index,**updates))
    assert r.status == "DEFERRED" and code in r.reason_codes


@pytest.mark.parametrize("updates", [{"subject":"another-server"},{"scope":"host-B"}])
def test_direct_label_does_not_override_obvious_entity_or_scope_mismatch(updates):
    s = replace_item(state(),"observed_propositions",2,**updates)
    assert evaluate(s).status == "DEFERRED"
