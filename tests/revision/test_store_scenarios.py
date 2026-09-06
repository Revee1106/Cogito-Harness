import asyncio
from datetime import timedelta
import pytest
from sqlalchemy.exc import SAWarning

from cogito.adapters.sqlite.store import SQLiteCognitiveStore
from cogito.domain.enums import ChangeKind, EventType
from cogito.domain.models.event import CognitiveTransaction, ObjectChange, RelationChange
from cogito.domain.policies.transaction import CognitiveTransactionValidationError, OBJECT_TYPES
from cogito.ports.cognitive_store import CognitiveVersionConflict, CognitiveStoreError
from .fixtures import NOW, state, event
from .test_engine import batch, strengthen, reject
from .test_fact import proposal as supersede


def run(coro):
    return asyncio.run(coro)


def seeded_store(path, *, ambiguous=False, source_state=None):
    store = SQLiteCognitiveStore(path)
    store.create_schema()
    s = source_state or state()
    if ambiguous:
        s = s.model_copy(update={"facts":tuple(f.model_copy(update={"valid_from":NOW,"valid_to":NOW}) for f in s.facts)})
    run(store.create_episode(s.episode.model_copy(update={"cognitive_version":0})))
    objects = (*s.recent_observations,*s.observed_propositions,*s.hypotheses,*s.gaps,*s.facts)
    sequence = 0
    for stage in (0,1):
        tx_id = f"seed-{stage}"
        selected = [o for o in objects if (str(o.id) in ("o3","p3")) == bool(stage)]
        links = [e for e in s.evidence_links if (str(e.id) == "e3") == bool(stage)]
        events = []
        for obj in selected:
            kind = {"Observation":EventType.OBSERVATION_ADDED,"ObservedProposition":EventType.PROPOSITION_ADDED,
                "Hypothesis":EventType.HYPOTHESIS_CREATED,"InformationGap":EventType.GAP_OPENED,
                "Fact":EventType.FACT_ADDED}[type(obj).__name__]
            payload = {"object_id":str(obj.id)}
            if kind is EventType.HYPOTHESIS_CREATED:
                payload["disconfirming_condition"] = obj.disconfirming_condition
            sequence += 1
            events.append(event(kind,payload,sequence,tx=tx_id))
        for link in links:
            sequence += 1
            events.append(event(EventType.EVIDENCE_LINK_ADMITTED,{"relation_id":str(link.id)},sequence,tx=tx_id))
        tx = CognitiveTransaction(id=tx_id,episode_id="ep",base_version=stage,events=tuple(events),
            object_changes=tuple(ObjectChange(kind=ChangeKind.CREATE,object_type=OBJECT_TYPES[type(o)],
                object_id=str(o.id),value=o) for o in selected),
            relation_changes=tuple(RelationChange(kind=ChangeKind.CREATE,value=e) for e in links))
        run(store.commit_transaction(tx))
    return store


def revise(store, b):
    from cogito.application.local_revision_engine import LocalRevisionEngine
    s = run(store.load_episode_state("ep"))
    return LocalRevisionEngine().revise(s,b,s.episode.cognitive_version,now=NOW+timedelta(days=1))


def test_store_hydrates_committed_relations_and_event_history(tmp_path):
    store = seeded_store(tmp_path / "state.db")
    try:
        s = run(store.load_episode_state("ep"))
        assert len(s.evidence_links) == 6
        assert s.cognitive_events == run(store.list_events("ep"))
    finally:
        store.close()


@pytest.mark.scenario
@pytest.mark.parametrize("scenario", ["A","B","C","D","E"])
def test_synthetic_revision_scenarios(tmp_path,scenario):
    store = seeded_store(tmp_path / f"scenario-{scenario}.db", ambiguous=scenario == "E")
    try:
        before = run(store.load_episode_state("ep"))
        inputs = {
            "A":dict(hypothesis_strengthen_proposals=(strengthen(),)),
            "B":dict(hypothesis_reject_proposals=(reject(rejection_basis="DISCONFIRMING_CONDITION_MET"),)),
            "C":dict(gap_resolution_evidence_ids=("e4",)),
            "D":dict(fact_supersede_proposals=(supersede(),)),
            "E":dict(fact_supersede_proposals=(supersede(),)),
        }[scenario]
        result = revise(store,batch(**inputs))
        if scenario == "E":
            assert result.status == "DEFERRED" and result.transaction is None
            assert "TEMPORAL_BASIS_INSUFFICIENT" in result.reason_codes
        else:
            assert result.status == "MATERIAL_CHANGE"
            # Building a result alone never writes to SQLite.
            assert run(store.load_episode_state("ep")) == before
            run(store.commit_transaction(result.transaction))
        after = run(store.load_episode_state("ep"))
        assert after.episode.cognitive_version == (2 if scenario == "E" else 3)
        if scenario != "E":
            repeated = revise(store,batch(**inputs))
            assert repeated.status == "NO_MATERIAL_CHANGE" and repeated.transaction is None
            assert run(store.load_episode_state("ep")) == after
        assert after.evidence_links == before.evidence_links
        assert after.cognitive_events[:len(before.cognitive_events)] == before.cognitive_events
        if scenario == "A":
            assert after.hypotheses[0].status == "SUPPORTED"
        elif scenario == "B":
            assert after.hypotheses[0].status == "REJECTED"
            assert after.hypotheses[0].evidence_refs == before.hypotheses[0].evidence_refs
        elif scenario == "C":
            assert after.gaps[0].status == "RESOLVED"
            assert after.goal_contract == before.goal_contract and after.focused_gap_id is None
            assert after.episode.status == before.episode.status
        elif scenario == "D":
            assert [(f.id,f.status) for f in after.facts] == [("f1","SUPERSEDED"),("f2","ACTIVE")]
        else:
            assert after == before and all(f.status == "ACTIVE" for f in after.facts)
    finally:
        store.close()


def test_strengthen_dedup_survives_store_reopen_and_new_support_is_material(tmp_path):
    path = tmp_path / "dedup.db"
    store = seeded_store(path)
    b = batch(hypothesis_strengthen_proposals=(strengthen(),))
    run(store.commit_transaction(revise(store,b).transaction))
    store.close()
    store = SQLiteCognitiveStore(path)
    try:
        assert revise(store,b).status == "NO_MATERIAL_CHANGE"
        new = batch(hypothesis_strengthen_proposals=(strengthen(evidence_link_ids=("e2",)),))
        result = revise(store,new)
        assert result.status == "MATERIAL_CHANGE"
        assert result.transaction.events[0].payload["previous_status"] == "SUPPORTED"
        run(store.commit_transaction(result.transaction))
        both = batch(hypothesis_strengthen_proposals=(strengthen(evidence_link_ids=("e2","e1")),))
        assert revise(store,both).transaction is None
        assert run(store.load_episode_state("ep")).episode.cognitive_version == 4
    finally:
        store.close()


def test_one_batch_commits_once_and_stale_version_cannot_repeat(tmp_path):
    store = seeded_store(tmp_path / "atomic.db")
    try:
        before = run(store.load_episode_state("ep"))
        result = revise(store,batch(hypothesis_strengthen_proposals=(strengthen(),),
            gap_resolution_evidence_ids=("e4",),fact_supersede_proposals=(supersede(),)))
        run(store.commit_transaction(result.transaction))
        after = run(store.load_episode_state("ep"))
        assert after.episode.cognitive_version == before.episode.cognitive_version+1
        assert len(after.cognitive_events) == len(before.cognitive_events)+3
        with pytest.raises(CognitiveVersionConflict):
            run(store.commit_transaction(result.transaction))
        assert run(store.load_episode_state("ep")) == after
    finally:
        store.close()


@pytest.mark.parametrize("defect", ["missing_event","wrong_payload","db_event_collision"])
def test_invalid_atomic_batch_leaves_no_partial_state_or_events(tmp_path,defect):
    store = seeded_store(tmp_path / f"rollback-{defect}.db")
    try:
        before = run(store.load_episode_state("ep"))
        tx = revise(store,batch(hypothesis_strengthen_proposals=(strengthen(),),gap_resolution_evidence_ids=("e4",))).transaction
        if defect == "missing_event":
            tx = tx.model_copy(update={"events":tx.events[:1]})
        else:
            ev = tx.events[1]
            update = {"id":"event-1"} if defect == "db_event_collision" else {"payload":{**ev.payload,"object_id":"wrong"}}
            tx = tx.model_copy(update={"events":(tx.events[0],ev.model_copy(update=update))})
        if defect == "db_event_collision":
            with pytest.warns(SAWarning, match="conflicts with persistent instance"):
                with pytest.raises(CognitiveStoreError):
                    run(store.commit_transaction(tx))
        else:
            with pytest.raises(CognitiveTransactionValidationError):
                run(store.commit_transaction(tx))
        assert run(store.load_episode_state("ep")) == before
    finally:
        store.close()


def test_legacy_missing_condition_snapshot_defers_without_fabrication(tmp_path):
    from cogito.application.local_revision_engine import LocalRevisionEngine
    store = seeded_store(tmp_path / "legacy.db")
    try:
        committed = run(store.load_episode_state("ep"))
        # Legacy read-view fixture only: do not bypass the new write invariant
        # or rewrite persisted history to manufacture a legacy database.
        legacy = committed.model_copy(update={"cognitive_events":tuple(
            e.model_copy(update={"payload":{"object_id":"h1"}})
            if e.event_type is EventType.HYPOTHESIS_CREATED else e
            for e in committed.cognitive_events)})
        result = LocalRevisionEngine().revise(legacy,
            batch(hypothesis_reject_proposals=(reject(rejection_basis="DISCONFIRMING_CONDITION_MET"),)),
            legacy.episode.cognitive_version,now=NOW)
        assert result.status == "DEFERRED" and "DISCONFIRMING_CONDITION_NOT_PRIOR" in result.reason_codes
        assert run(store.load_episode_state("ep")) == committed
    finally:
        store.close()
