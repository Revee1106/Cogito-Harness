import pytest
from cogito.domain.enums import ChangeKind, EventType, HypothesisStatus
from cogito.domain.models.event import ObjectChange
from cogito.domain.policies.transaction import CognitiveTransactionValidator, OBJECT_TYPES
from .fixtures import state, event
from .test_engine import batch, revise, strengthen, reject
from .test_fact import proposal as supersede


def validate(tx,s=None):
    s = s or state()
    return CognitiveTransactionValidator().validate(tx,
        current_objects=(*s.recent_observations,*s.observed_propositions,*s.hypotheses,*s.gaps,*s.facts),
        current_relations=s.evidence_links,current_events=s.cognitive_events)


def transaction(kind):
    args = {
        "strengthen":dict(hypothesis_strengthen_proposals=(strengthen(),)),
        "reject":dict(hypothesis_reject_proposals=(reject(),)),
        "gap":dict(gap_resolution_evidence_ids=("e4",)),
        "fact":dict(fact_supersede_proposals=(supersede(),)),
    }
    return revise(b=batch(**args[kind])).transaction


@pytest.mark.parametrize("kind", ["strengthen","reject","gap","fact"])
def test_exact_known_material_updates_validate(kind):
    assert validate(transaction(kind)).valid


@pytest.mark.parametrize("kind", ["strengthen","reject","gap","fact"])
@pytest.mark.parametrize("defect", ["missing","wrong_id","wrong_old_status","wrong_new_status","wrong_evidence","orphan","mutated_object","duplicate_event"])
def test_revision_event_and_change_must_correspond_exactly(kind,defect):
    tx = transaction(kind)
    ev, change = tx.events[0],tx.object_changes[0]
    if defect == "missing":
        tx = tx.model_copy(update={"events":()})
    elif defect == "orphan":
        tx = tx.model_copy(update={"object_changes":()})
    elif defect == "duplicate_event":
        tx = tx.model_copy(update={"events":(ev,ev.model_copy(update={"id":"duplicate","sequence":ev.sequence+1}))})
    elif defect == "mutated_object":
        key = "question" if kind == "gap" else "statement"
        change = change.model_copy(update={"value":change.value.model_copy(update={key:"unrequested rewrite"})})
        tx = tx.model_copy(update={"object_changes":(change,)})
    else:
        key,value = {"wrong_id":("object_id","other"),"wrong_old_status":("previous_status","wrong"),
            "wrong_new_status":("new_status","wrong"),"wrong_evidence":("basis_evidence_ids",["missing"])}[defect]
        tx = tx.model_copy(update={"events":(ev.model_copy(update={"payload":{**ev.payload,key:value}}),)})
    assert not validate(tx).valid


def test_strengthen_history_prevents_duplicate_committed_update():
    tx = transaction("strengthen")
    s = state().model_copy(update={"hypotheses":(tx.object_changes[0].value,),
        "cognitive_events":(*state().cognitive_events,*tx.events)})
    ev = tx.events[0].model_copy(update={"payload":{**tx.events[0].payload,"previous_status":"SUPPORTED"}})
    assert not validate(tx.model_copy(update={"events":(ev,)}),s).valid


def test_condition_snapshot_cannot_be_fabricated_as_orphan_event():
    tx = transaction("strengthen")
    forged = event(EventType.HYPOTHESIS_CREATED, {"object_id":"h1","disconfirming_condition":"posthoc"},
                   sequence=21,tx=tx.id)
    assert not validate(tx.model_copy(update={"events":(*tx.events,forged)})).valid


def test_cannot_mix_source_invalidation_with_revision():
    from cogito.domain.enums import PropositionStatus
    tx = transaction("strengthen")
    p = state().observed_propositions[0].model_copy(update={"status":PropositionStatus.RETRACTED})
    change = ObjectChange(kind=ChangeKind.UPDATE,object_type=OBJECT_TYPES[type(p)],object_id=str(p.id),value=p)
    assert not validate(tx.model_copy(update={"object_changes":(*tx.object_changes,change)})).valid


def test_validator_rejects_batch_that_supersedes_its_replacement():
    tx = transaction("fact")
    reverse = revise(b=batch(fact_supersede_proposals=(supersede(fact_id="f2",replacement_fact_id="f1",
        basis_evidence_ids=("e5",),temporal_basis="EXPLICIT_STATE_TRANSITION",transition_match="DIRECT"),))).transaction
    ev = reverse.events[0].model_copy(update={"transaction_id":tx.id,"sequence":21})
    combined = tx.model_copy(update={"events":(*tx.events,ev),"object_changes":(*tx.object_changes,*reverse.object_changes)})
    assert not validate(combined).valid


@pytest.mark.parametrize("updates", [{"proposal":{}},{"replacement_fact_id":[]},{"basis_evidence_ids":None}])
def test_malformed_payload_is_invalid_not_a_validator_crash(updates):
    tx = transaction("fact")
    ev = tx.events[0].model_copy(update={"payload":{**tx.events[0].payload,**updates}})
    assert not validate(tx.model_copy(update={"events":(ev,)})).valid
