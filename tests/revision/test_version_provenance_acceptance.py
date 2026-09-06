import pytest

from cogito.domain.enums import ChangeKind, EventType, FactStatus
from cogito.domain.models.event import CognitiveTransaction, ObjectChange
from cogito.domain.policies.revision_fact import FactSupersedePolicy
from cogito.domain.policies.transaction import CognitiveTransactionValidationError
from .fixtures import NOW, event
from .test_engine import batch, strengthen, revise
from .test_fact import artifact_state, proposal
from .test_validation import validate
from .test_store_scenarios import seeded_store, run


def version_proposal(**updates):
    return proposal(**{**dict(temporal_basis="VERSIONED_ARTIFACT_SUCCESSION",
        artifact_identity="config/db",old_version=17,replacement_version=18),**updates})


@pytest.mark.parametrize("old_version,replacement_version", [(17,18),(0,999999),(18,17),(None,None)])
def test_proposal_versions_and_shared_source_ref_are_not_provenance(old_version,replacement_version):
    s = artifact_state()
    result = FactSupersedePolicy().evaluate(s,
        version_proposal(old_version=old_version,replacement_version=replacement_version),now=NOW)
    assert result.status == "DEFERRED" and result.value is None
    assert result.reason_codes == ("VERSION_PROVENANCE_INSUFFICIENT",)
    assert all(f.status == "ACTIVE" for f in s.facts)


@pytest.mark.parametrize("mixed", [False,True])
def test_version_provenance_gap_defers_whole_batch(mixed):
    s = artifact_state()
    inputs = dict(fact_supersede_proposals=(version_proposal(),))
    if mixed:
        inputs.update(hypothesis_strengthen_proposals=(strengthen(),),gap_resolution_evidence_ids=("e4",))
    result = revise(s,batch(**inputs))
    assert result.status == "DEFERRED" and result.transaction is None
    assert result.affected_object_ids == ()
    assert "VERSION_PROVENANCE_INSUFFICIENT" in result.reason_codes
    assert s == artifact_state()


def forged_version_transaction(s):
    p = version_proposal()
    old = s.facts[0]
    payload = dict(object_id=str(old.id),previous_status="ACTIVE",new_status="SUPERSEDED",
        basis_evidence_ids=["e6"],basis=p.temporal_basis.value,public_reason=p.reason,
        proposal=p.model_dump(mode="json"),replacement_fact_id="f2")
    ev = event(EventType.FACT_SUPERSEDED,payload,max(e.sequence for e in s.cognitive_events)+1,
               tx="forged-version",cause_id="artifact-proposal")
    return CognitiveTransaction(id="forged-version",episode_id=s.episode.id,
        base_version=s.episode.cognitive_version,events=(ev,),object_changes=(ObjectChange(
            kind=ChangeKind.UPDATE,object_type="FACT",object_id=str(old.id),
            value=old.model_copy(update={"status":FactStatus.SUPERSEDED})),))


def test_validator_cannot_accept_proposal_only_version_transaction():
    s = artifact_state()
    assert not validate(forged_version_transaction(s),s).valid


def test_store_rejects_forged_version_revision_without_any_state_change(tmp_path):
    store = seeded_store(tmp_path / "version-provenance.db",source_state=artifact_state())
    try:
        before = run(store.load_episode_state("ep"))
        with pytest.raises(CognitiveTransactionValidationError):
            run(store.commit_transaction(forged_version_transaction(before)))
        assert run(store.load_episode_state("ep")) == before
        assert all(f.status == "ACTIVE" for f in before.facts)
    finally:
        store.close()
