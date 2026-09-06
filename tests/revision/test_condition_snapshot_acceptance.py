import pytest

from cogito.domain.enums import ChangeKind, EventType
from cogito.domain.models.event import CognitiveTransaction, ObjectChange, RelationChange
from cogito.domain.policies.transaction import (
    CognitiveTransactionValidationError, CognitiveTransactionValidator, OBJECT_TYPES,
)
from .fixtures import event, state
from .test_engine import batch, reject
from .test_store_scenarios import run, seeded_store, revise


CONDITION = "service responds on 3306"


def creation(condition, payload):
    s = state()
    h = s.hypotheses[0].model_copy(update={"disconfirming_condition":condition})
    tx = CognitiveTransaction(id="create-h",episode_id="ep",base_version=0,
        events=(event(EventType.HYPOTHESIS_CREATED,payload,tx="create-h"),
                event(EventType.EVIDENCE_LINK_ADMITTED,{"relation_id":"e1"},2,tx="create-h")),
        object_changes=(ObjectChange(kind=ChangeKind.CREATE,object_type=OBJECT_TYPES[type(h)],object_id="h1",value=h),),
        relation_changes=(RelationChange(kind=ChangeKind.CREATE,value=s.evidence_links[0]),))
    return tx, s


@pytest.mark.parametrize("condition,payload,valid", [
    (CONDITION,{"object_id":"h1","disconfirming_condition":CONDITION},True),
    (CONDITION,{"object_id":"h1"},False),
    (CONDITION,{"object_id":"h1","disconfirming_condition":"different condition"},False),
    (CONDITION,{"object_id":"h1","disconfirming_condition":None},False),
    (CONDITION,{"object_id":"h1","disconfirming_condition":" "},False),
    (None,{"object_id":"h1"},True),
    ("",{"object_id":"h1"},True),
    (" \t",{"object_id":"h1"},True),
])
def test_condition_creation_snapshot_invariant(condition,payload,valid):
    tx, s = creation(condition,payload)
    result = CognitiveTransactionValidator().validate(tx,current_objects=s.observed_propositions)
    assert result.valid is valid


def test_missing_condition_snapshot_cannot_commit(tmp_path):
    from cogito.adapters.sqlite.store import SQLiteCognitiveStore
    tx, s = creation(CONDITION,{"object_id":"h1"})
    p = s.observed_propositions[0]
    tx = tx.model_copy(update={"object_changes":(
        ObjectChange(kind=ChangeKind.CREATE,object_type=OBJECT_TYPES[type(p)],object_id=str(p.id),value=p),
        *tx.object_changes)})
    store = SQLiteCognitiveStore(tmp_path / "missing-snapshot.db")
    store.create_schema()
    try:
        run(store.create_episode(s.episode.model_copy(update={"cognitive_version":0})))
        with pytest.raises(CognitiveTransactionValidationError):
            run(store.commit_transaction(tx))
        after = run(store.load_episode_state("ep"))
        assert after.episode.cognitive_version == 0
        assert not after.hypotheses and not after.cognitive_events and not after.evidence_links
    finally:
        store.close()


def test_persisted_creation_snapshot_enables_later_condition_rejection(tmp_path):
    store = seeded_store(tmp_path / "condition-path.db")
    try:
        before = run(store.load_episode_state("ep"))
        snapshot = next(e for e in before.cognitive_events if e.event_type is EventType.HYPOTHESIS_CREATED)
        trigger = next(e for e in before.cognitive_events if e.payload.get("relation_id") == "e3")
        assert snapshot.payload["disconfirming_condition"] == before.hypotheses[0].disconfirming_condition
        assert snapshot.transaction_id != trigger.transaction_id and snapshot.sequence < trigger.sequence
        result = revise(store,batch(hypothesis_reject_proposals=(reject(rejection_basis="DISCONFIRMING_CONDITION_MET"),)))
        assert result.status == "MATERIAL_CHANGE"
        run(store.commit_transaction(result.transaction))
        after = run(store.load_episode_state("ep"))
        assert after.hypotheses[0].status == "REJECTED"
        assert after.evidence_links == before.evidence_links
    finally:
        store.close()
