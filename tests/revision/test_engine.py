import pytest
from pydantic import ValidationError
from .fixtures import NOW, state, replace_item
from .test_fact import proposal as supersede


def strengthen(**updates):
    from cogito.domain.proposals.revision import HypothesisStrengthenProposal
    return HypothesisStrengthenProposal(**{**dict(hypothesis_id="h1", evidence_link_ids=("e1",),
        support_basis="DIRECT_OBSERVATION",reason="direct probe supports claim"),**updates})


def reject(**updates):
    from cogito.domain.proposals.revision import HypothesisRejectProposal
    return HypothesisRejectProposal(**{**dict(hypothesis_id="h1",evidence_link_ids=("e3",),
        rejection_basis="DIRECT_CONTRADICTION",semantic_directness="DIRECT",reason="direct falsification"),**updates})


def batch(**updates):
    from cogito.domain.models.revision import RevisionBatch
    return RevisionBatch(cause_id="probe-result", **updates)


def revise(s=None,b=None,base_version=2):
    from cogito.application.local_revision_engine import LocalRevisionEngine
    return LocalRevisionEngine().revise(s or state(), b or batch(), base_version, now=NOW)


def test_no_explicit_input_no_automatic_strengthen_reject_resolve_or_supersede():
    result = revise()
    assert result.status == "NO_MATERIAL_CHANGE" and result.transaction is None
    assert result.affected_object_ids == ()


def test_one_cause_one_atomic_transaction_and_explicit_targets_only():
    s = state()
    result = revise(s,batch(hypothesis_strengthen_proposals=(strengthen(),),
        gap_resolution_evidence_ids=("e4",),fact_supersede_proposals=(supersede(),)))
    tx = result.transaction
    assert result.status == "MATERIAL_CHANGE"
    assert tx.base_version == 2
    assert set(result.affected_object_ids) == {"h1","g1","f1"}
    assert len(tx.events) == len(tx.object_changes) == 3
    assert {e.cause_id for e in tx.events} == {"probe-result"}
    assert {e.transaction_id for e in tx.events} == {tx.id}
    assert [e.sequence for e in tx.events] == [20,21,22]
    assert {e.payload["object_id"] for e in tx.events} == {c.object_id for c in tx.object_changes}
    assert not tx.relation_changes
    assert s == state()  # pure builder, including goal/episode/focus/evidence


def test_deferred_member_defers_whole_cause():
    result = revise(b=batch(hypothesis_strengthen_proposals=(strengthen(),),
        hypothesis_reject_proposals=(reject(semantic_directness="AMBIGUOUS"),)))
    assert result.status == "DEFERRED" and result.transaction is None


def test_conflicting_same_target_revisions_not_prioritized():
    result = revise(b=batch(hypothesis_strengthen_proposals=(strengthen(),),
                           hypothesis_reject_proposals=(reject(),)))
    assert result.status == "DEFERRED" and result.transaction is None


def test_exact_duplicate_inputs_coalesce():
    result = revise(b=batch(hypothesis_strengthen_proposals=(strengthen(),strengthen())))
    assert len(result.transaction.events) == 1


def test_base_version_mismatch_never_builds_commit():
    result = revise(b=batch(hypothesis_strengthen_proposals=(strengthen(),)),base_version=1)
    assert result.status == "DEFERRED" and result.transaction is None


def test_cross_episode_batch_never_partially_builds():
    s = replace_item(state(),"gaps",0,episode_id="other")
    assert revise(s,batch(gap_resolution_evidence_ids=("e4",))).transaction is None


@pytest.mark.parametrize("status", ["MATERIAL_CHANGE","NO_MATERIAL_CHANGE","DEFERRED"])
def test_result_transaction_invariant(status):
    from cogito.domain.models.revision import RevisionResult
    tx = revise(b=batch(hypothesis_strengthen_proposals=(strengthen(),))).transaction
    with pytest.raises(ValidationError):
        RevisionResult(status=status,transaction=None if status == "MATERIAL_CHANGE" else tx)


def test_affected_ids_must_match_transaction():
    from cogito.domain.models.revision import RevisionResult
    tx = revise(b=batch(hypothesis_strengthen_proposals=(strengthen(),))).transaction
    with pytest.raises(ValidationError):
        RevisionResult(status="MATERIAL_CHANGE",transaction=tx,affected_object_ids=("unrelated",))


def test_batch_cannot_supersede_its_own_active_replacement():
    inputs = (
        supersede(temporal_basis="EXPLICIT_STATE_TRANSITION",transition_match="DIRECT"),
        supersede(fact_id="f2",replacement_fact_id="f1",basis_evidence_ids=("e5",),
                  temporal_basis="EXPLICIT_STATE_TRANSITION",transition_match="DIRECT"),
    )
    result = revise(b=batch(fact_supersede_proposals=inputs))
    assert result.status == "DEFERRED" and result.transaction is None


def test_story_zero_revision_boundary_routes_to_the_single_local_engine():
    from cogito.application.revision_engine import RevisionEngine
    from cogito.application.local_revision_engine import LocalRevisionEngine
    assert RevisionEngine is LocalRevisionEngine
