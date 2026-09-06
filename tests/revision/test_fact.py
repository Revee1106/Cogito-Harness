from datetime import timedelta
import pytest
from pydantic import ValidationError
from cogito.domain.enums import FactStatus, FactBasis, PropositionStatus
from .fixtures import NOW, state, replace_item


def proposal(**updates):
    from cogito.domain.proposals.revision import FactSupersedeProposal
    args = dict(fact_id="f1", replacement_fact_id="f2", basis_evidence_ids=("e6",),
                temporal_basis="LATER_DIRECT_OBSERVATION", reason="later direct reading")
    args.update(updates)
    return FactSupersedeProposal(**args)


def evaluate(s=None, **updates):
    from cogito.domain.policies.revision_fact import FactSupersedePolicy
    return FactSupersedePolicy().evaluate(s or state(), proposal(**updates), now=NOW)


def test_later_world_observation_supersedes_old_only():
    s = state()
    result = evaluate(s)
    assert result.status == "MATERIAL_CHANGE"
    assert result.value.status == "SUPERSEDED"
    assert result.value.model_copy(update={"status":FactStatus.ACTIVE}) == s.facts[0]
    assert result.event_type == "FACT_SUPERSEDED"
    assert result.payload["replacement_fact_id"] == "f2"
    assert s.facts[1].status == "ACTIVE"


def test_created_at_alone_is_never_world_time():
    s = state()
    s = s.model_copy(update={
        "facts":tuple(f.model_copy(update={"valid_from":None,"valid_to":None,
                    "created_at":NOW+timedelta(days=i)}) for i,f in enumerate(s.facts)),
        "observed_propositions":tuple(p.model_copy(update={"observed_at":None}) for p in s.observed_propositions),
        "recent_observations":tuple(o.model_copy(update={"observed_at":None}) for o in s.recent_observations),
    })
    result = evaluate(s)
    assert result.status == "DEFERRED" and "TEMPORAL_BASIS_INSUFFICIENT" in result.reason_codes
    assert all(f.status == "ACTIVE" for f in s.facts)


@pytest.mark.parametrize("change", ["equal", "reverse", "overlap", "naive"])
def test_ambiguous_or_nonlater_time_defers(change):
    s = state()
    first = s.facts[0].valid_from
    if change == "equal":
        s = replace_item(s,"facts",1,valid_from=first,valid_to=first)
    elif change == "reverse":
        s = replace_item(s,"facts",1,valid_from=first-timedelta(days=1),valid_to=first)
    elif change == "overlap":
        s = replace_item(s,"facts",0,valid_to=first+timedelta(days=1))
    else:
        s = replace_item(s,"facts",0,valid_from=first.replace(tzinfo=None),valid_to=first.replace(tzinfo=None))
    assert evaluate(s).status == "DEFERRED"


def test_observed_at_fallback_not_ingestion_time():
    s = state()
    s = s.model_copy(update={"facts":tuple(f.model_copy(update={"valid_from":None,"valid_to":None}) for f in s.facts)})
    assert evaluate(s).status == "MATERIAL_CHANGE"


def test_explicit_transition_requires_explicit_match():
    assert evaluate(temporal_basis="EXPLICIT_STATE_TRANSITION").status == "DEFERRED"
    assert evaluate(temporal_basis="EXPLICIT_STATE_TRANSITION", transition_match="DIRECT").status == "MATERIAL_CHANGE"


def artifact_state():
    s = state()
    s = s.model_copy(update={"facts":tuple(f.model_copy(update={"basis":FactBasis.ARTIFACT_CONTENT}) for f in s.facts)})
    for i in (4,5):
        s = replace_item(s,"recent_observations",i,source="config artifact",source_ref="config/db")
    return s


def test_versioned_artifact_identity_and_proposal_order_are_not_sufficient():
    args = dict(temporal_basis="VERSIONED_ARTIFACT_SUCCESSION", artifact_identity="config/db",
                old_version=17,replacement_version=18)
    result = evaluate(artifact_state(),**args)
    assert result.status == "DEFERRED"
    assert result.reason_codes == ("VERSION_PROVENANCE_INSUFFICIENT",)
    assert evaluate(artifact_state(),**{**args,"replacement_version":16}).status == "DEFERRED"
    assert evaluate(artifact_state(),**{**args,"artifact_identity":"other"}).status == "DEFERRED"
    assert evaluate(artifact_state(),temporal_basis="VERSIONED_ARTIFACT_SUCCESSION").status == "DEFERRED"


def test_artifact_update_cannot_supersede_runtime():
    s = replace_item(artifact_state(),"facts",0,basis=FactBasis.DIRECT_MEASUREMENT)
    assert evaluate(s,temporal_basis="VERSIONED_ARTIFACT_SUCCESSION",artifact_identity="config/db",
                    old_version=17,replacement_version=18).status == "DEFERRED"


@pytest.mark.parametrize("field,index,updates", [
    ("facts",1,{"episode_id":"other"}),
    ("facts",1,{"status":FactStatus.RETRACTED}),
    ("facts",1,{"status":FactStatus.SUPERSEDED}),
    ("facts",1,{"subject":"other"}),
    ("facts",1,{"predicate":"other"}),
    ("facts",1,{"scope":"other"}),
    ("facts",1,{"scope":None}),
    ("observed_propositions",5,{"status":PropositionStatus.RETRACTED}),
    ("recent_observations",5,{"source":"user speculation"}),
    ("evidence_links",5,{"target_id":"f1"}),
    ("facts",1,{"evidence_refs":()}),
])
def test_fact_structural_defenses(field,index,updates):
    assert evaluate(replace_item(state(),field,index,**updates)).status == "DEFERRED"


def test_missing_self_and_unsupported_basis():
    assert evaluate(replacement_fact_id="missing").status == "DEFERRED"
    assert evaluate(replacement_fact_id="f1").status == "DEFERRED"
    with pytest.raises(ValidationError):
        evaluate(temporal_basis="LATEST_CREATED")
