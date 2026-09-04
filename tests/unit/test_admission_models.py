from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cogito.domain.enums import (
    AdmissionDecision,
    AdmissionReasonCode,
    FactAdmissionDecision,
    FactBasis,
    FactStatus,
    SemanticEntailment,
)
from cogito.domain.ids import EpisodeId, EvidenceLinkId, FactId
from cogito.domain.models.admission import AdmissionResult
from cogito.domain.models.fact import Fact


NOW = datetime(2026, 1, 1, tzinfo=UTC)


def test_story_1a_admission_vocabulary_is_explicit_and_non_numeric() -> None:
    assert {item.value for item in FactBasis} == {
        "SOURCE_REPORT",
        "ARTIFACT_CONTENT",
        "DIRECT_MEASUREMENT",
        "DETERMINISTIC_DERIVATION",
    }
    assert {item.value for item in SemanticEntailment} == {
        "EQUIVALENT_OR_NARROWER",
        "STRONGER_THAN_SOURCE",
        "AMBIGUOUS",
    }
    assert {item.value for item in FactAdmissionDecision} == {
        "ADMIT",
        "DEFER",
        "REJECT",
    }
    assert AdmissionDecision.NO_NEW_ADMISSION.value == "NO_NEW_ADMISSION"
    assert not any("SCORE" in item.name or "CONFIDENCE" in item.name for item in AdmissionReasonCode)


def test_admission_result_exposes_only_structured_public_reasons() -> None:
    result = AdmissionResult[str](
        decision=AdmissionDecision.REJECT,
        reason_codes=(AdmissionReasonCode.CLAIM_TOO_STRONG,),
        public_reasons=("candidate assertion is stronger than its source proposition",),
    )

    assert result.value is None
    assert result.reason_codes == (AdmissionReasonCode.CLAIM_TOO_STRONG,)
    assert "chain" not in result.model_dump()


def test_committed_fact_preserves_basis_and_validates_temporal_range() -> None:
    fact = Fact(
        id=FactId("fact-1"),
        episode_id=EpisodeId("episode-1"),
        statement="mysqld listens on 3307",
        basis=FactBasis.DIRECT_MEASUREMENT,
        evidence_refs=(EvidenceLinkId("evidence-1"),),
        status=FactStatus.ACTIVE,
        valid_from=NOW,
        valid_to=NOW,
        created_at=NOW,
    )

    assert fact.basis is FactBasis.DIRECT_MEASUREMENT
    with pytest.raises(ValidationError, match="valid_to"):
        Fact.model_validate(
            {
                **fact.model_dump(),
                "valid_from": NOW,
                "valid_to": datetime(2025, 1, 1, tzinfo=UTC),
            }
        )
