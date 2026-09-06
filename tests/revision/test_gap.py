import pytest
from cogito.domain.enums import GapStatus, EvidenceRelation, PropositionStatus
from .fixtures import NOW, state, replace_item


def evaluate(s=None, evidence_id="e4"):
    from cogito.domain.policies.revision_gap import GapResolutionPolicy
    return GapResolutionPolicy().evaluate(s or state(), evidence_id, now=NOW)


@pytest.mark.parametrize("status", [GapStatus.OPEN, GapStatus.FOCUSED])
def test_resolve_only_target_gap(status):
    s = replace_item(state(), "gaps", 0, status=status)
    result = evaluate(s)
    assert result.status == "MATERIAL_CHANGE"
    assert result.value.status == GapStatus.RESOLVED
    assert result.value.resolved_at == NOW
    assert result.event_type == "GAP_RESOLVED"
    assert result.payload["basis_evidence_ids"] == ["e4"]
    assert s.gaps[0].status == status


def test_duplicate_resolve_is_not_material():
    s = replace_item(state(), "gaps", 0, status=GapStatus.RESOLVED, resolved_at=NOW)
    assert evaluate(s).status == "NO_MATERIAL_CHANGE"


@pytest.mark.parametrize("field,index,updates,code", [
    ("gaps",0,{"status":GapStatus.INVALIDATED},"TARGET_STATUS_INVALID"),
    ("gaps",0,{"episode_id":"other"},"EPISODE_MISMATCH"),
    ("evidence_links",3,{"relation":EvidenceRelation.NEUTRAL},"EVIDENCE_RELATION_INVALID"),
    ("observed_propositions",3,{"status":PropositionStatus.RETRACTED},"PROPOSITION_INACTIVE"),
    ("evidence_links",3,{"target_id":"missing"},"TARGET_NOT_FOUND"),
])
def test_gap_structural_defenses(field,index,updates,code):
    result = evaluate(replace_item(state(), field,index,**updates))
    assert result.status == "DEFERRED" and code in result.reason_codes


def test_missing_evidence_does_not_resolve_gap():
    assert evaluate(evidence_id="absent").status == "DEFERRED"
