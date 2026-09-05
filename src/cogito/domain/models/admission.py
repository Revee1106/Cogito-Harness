from __future__ import annotations

from typing import Generic, TypeVar

from cogito.domain.base import DomainModel
from cogito.domain.enums import AdmissionDecision, AdmissionReasonCode
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact


ValueT = TypeVar("ValueT")


class AdmissionResult(DomainModel, Generic[ValueT]):
    """Auditable outcome; ADMIT reason codes may be non-fatal diagnostics."""

    decision: AdmissionDecision
    value: ValueT | None = None
    reason_codes: tuple[AdmissionReasonCode, ...] = ()
    public_reasons: tuple[str, ...] = ()


class AdmittedFactBundle(DomainModel):
    fact: Fact
    evidence_link: EvidenceLink
