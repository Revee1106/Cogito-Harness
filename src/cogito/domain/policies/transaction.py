from __future__ import annotations

from collections import Counter

from cogito.domain.base import DomainModel
from cogito.domain.enums import (
    AdmissionReasonCode,
    ChangeKind,
    CognitiveObjectType,
    CognitiveTargetType,
    EvidenceRelation,
    FactStatus,
    HypothesisStatus,
)
from cogito.domain.models.action import ActionDecision
from cogito.domain.models.event import CognitiveObject, CognitiveTransaction
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.gap import InformationGap
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import Observation, ObservedProposition
from cogito.domain.policies.evidence import ALLOWED_RELATIONS
from cogito.domain.policies.fact import FactAdmissionPolicy


OBJECT_TYPES: dict[type[object], CognitiveObjectType] = {
    Observation: CognitiveObjectType.OBSERVATION,
    ObservedProposition: CognitiveObjectType.PROPOSITION,
    Fact: CognitiveObjectType.FACT,
    Hypothesis: CognitiveObjectType.HYPOTHESIS,
    InformationGap: CognitiveObjectType.INFORMATION_GAP,
    ActionDecision: CognitiveObjectType.ACTION,
}

TARGET_TYPES: dict[type[object], CognitiveTargetType] = {
    Fact: CognitiveTargetType.FACT,
    Hypothesis: CognitiveTargetType.HYPOTHESIS,
    InformationGap: CognitiveTargetType.GAP,
}


class TransactionValidationResult(DomainModel):
    valid: bool
    reason_codes: tuple[AdmissionReasonCode, ...] = ()
    public_reasons: tuple[str, ...] = ()


class CognitiveTransactionValidationError(ValueError):
    def __init__(self, result: TransactionValidationResult) -> None:
        self.result = result
        message = "; ".join(result.public_reasons) or "invalid cognitive transaction"
        super().__init__(message)


class CognitiveTransactionValidator:
    """Validate cognitive consistency across current and transaction-local state."""

    def validate(
        self,
        transaction: CognitiveTransaction,
        *,
        current_objects: tuple[CognitiveObject, ...] = (),
        current_relations: tuple[EvidenceLink, ...] = (),
    ) -> TransactionValidationResult:
        issues: list[tuple[AdmissionReasonCode, str]] = []

        def add(code: AdmissionReasonCode, reason: str) -> None:
            if code not in {item[0] for item in issues}:
                issues.append((code, reason))

        for event in transaction.events:
            if (
                event.episode_id != transaction.episode_id
                or event.transaction_id != transaction.id
            ):
                add(
                    AdmissionReasonCode.EPISODE_MISMATCH,
                    "event envelope does not match the cognitive transaction",
                )

        ids = [change.object_id for change in transaction.object_changes]
        if any(count > 1 for count in Counter(ids).values()):
            add(
                AdmissionReasonCode.CONFLICTING_OBJECT_CHANGES,
                "one transaction cannot contain multiple changes for the same object",
            )

        object_by_id = {str(item.id): item for item in current_objects}
        created_objects: list[CognitiveObject] = []
        for change in transaction.object_changes:
            value = change.value
            if value.episode_id != transaction.episode_id:
                add(
                    AdmissionReasonCode.EPISODE_MISMATCH,
                    "object change belongs to another episode",
                )
            expected_object_type = OBJECT_TYPES.get(type(value))
            if expected_object_type is not change.object_type:
                add(
                    AdmissionReasonCode.COGNITIVE_STRUCTURE_INVALID,
                    "object change type does not match its domain value",
                )
            if change.kind is ChangeKind.UPDATE and change.object_id not in object_by_id:
                add(
                    AdmissionReasonCode.COGNITIVE_STRUCTURE_INVALID,
                    "transaction updates a missing cognitive object",
                )
            if change.kind is ChangeKind.CREATE:
                created_objects.append(value)
                if isinstance(value, Fact) and value.status is not FactStatus.ACTIVE:
                    add(
                        AdmissionReasonCode.INVALID_INITIAL_STATUS,
                        "Story 1A can create Facts only in ACTIVE state",
                    )
                if (
                    isinstance(value, Hypothesis)
                    and value.status is not HypothesisStatus.PLAUSIBLE
                ):
                    add(
                        AdmissionReasonCode.INVALID_INITIAL_STATUS,
                        "Story 1A can create Hypotheses only in PLAUSIBLE state",
                    )
            object_by_id[change.object_id] = value

        staged_relations: list[EvidenceLink] = []
        all_relations = list(current_relations)
        for change in transaction.relation_changes:
            link = change.value
            if change.kind is not ChangeKind.CREATE:
                add(
                    AdmissionReasonCode.RELATION_NOT_ALLOWED,
                    "Story 1A does not replace or invalidate EvidenceLinks",
                )
            if link.episode_id != transaction.episode_id:
                add(
                    AdmissionReasonCode.EPISODE_MISMATCH,
                    "EvidenceLink belongs to another episode",
                )
            source = object_by_id.get(str(link.proposition_id))
            if not isinstance(source, ObservedProposition):
                add(
                    AdmissionReasonCode.SOURCE_NOT_FOUND,
                    "EvidenceLink source proposition is missing",
                )
            elif source.episode_id != transaction.episode_id:
                add(
                    AdmissionReasonCode.EPISODE_MISMATCH,
                    "EvidenceLink source belongs to another episode",
                )
            target = object_by_id.get(link.target_id)
            if target is None:
                add(
                    AdmissionReasonCode.MISSING_DRAFT_OBJECT,
                    "reserved relation target has no corresponding committed CREATE",
                )
            else:
                actual_target_type = TARGET_TYPES.get(type(target))
                if actual_target_type is not link.target_type:
                    add(
                        AdmissionReasonCode.TARGET_TYPE_MISMATCH,
                        "EvidenceLink target_type does not match its domain object",
                    )
                if target.episode_id != transaction.episode_id:
                    add(
                        AdmissionReasonCode.EPISODE_MISMATCH,
                        "EvidenceLink target belongs to another episode",
                    )
                if (
                    actual_target_type is not None
                    and (
                        link.relation is EvidenceRelation.NEUTRAL
                        or link.relation not in ALLOWED_RELATIONS[actual_target_type]
                    )
                ):
                    add(
                        AdmissionReasonCode.RELATION_NOT_ALLOWED,
                        "Evidence relation is incompatible with its target",
                    )

            pair = tuple(
                item
                for item in all_relations + staged_relations
                if item.proposition_id == link.proposition_id
                and item.target_id == link.target_id
            )
            if any(item.relation is link.relation for item in pair):
                add(
                    AdmissionReasonCode.DUPLICATE_EVIDENCE,
                    "transaction would duplicate active Evidence",
                )
            opposites = {EvidenceRelation.SUPPORTS, EvidenceRelation.CONTRADICTS}
            if link.relation in opposites and any(
                item.relation in opposites and item.relation is not link.relation
                for item in pair
            ):
                add(
                    AdmissionReasonCode.RELATION_CONFLICT,
                    "transaction creates mutually exclusive active Evidence",
                )
            staged_relations.append(link)

        relation_by_id = {
            str(item.id): item for item in all_relations + staged_relations
        }
        for value in created_objects:
            if isinstance(value, Fact):
                referenced = tuple(
                    relation_by_id.get(str(reference))
                    for reference in value.evidence_refs
                )
                if not referenced or any(
                    item is None
                    or item.target_id != str(value.id)
                    or item.target_type is not CognitiveTargetType.FACT
                    or item.relation is not EvidenceRelation.SUPPORTS
                    for item in referenced
                ):
                    add(
                        AdmissionReasonCode.EVIDENCE_REFERENCE_INVALID,
                        "Fact evidence_refs must reference SUPPORTS links targeting itself",
                    )
            if isinstance(value, Hypothesis):
                referenced = tuple(
                    relation_by_id.get(str(reference))
                    for reference in value.evidence_refs
                )
                if any(item is None for item in referenced):
                    add(
                        AdmissionReasonCode.EVIDENCE_REFERENCE_INVALID,
                        "Hypothesis contains a missing EvidenceLink reference",
                    )
                if not any(
                    item is not None
                    and item.target_id == str(value.id)
                    and item.target_type is CognitiveTargetType.HYPOTHESIS
                    and item.relation is EvidenceRelation.SUPPORTS
                    for item in referenced
                ):
                    add(
                        AdmissionReasonCode.NO_SUPPORTING_EVIDENCE,
                        "Hypothesis needs a SUPPORTS EvidenceLink targeting itself",
                    )

        committed_facts = [item for item in current_objects if isinstance(item, Fact)]
        new_facts: list[Fact] = []
        for value in created_objects:
            if not isinstance(value, Fact):
                continue
            if any(
                FactAdmissionPolicy.facts_conflict(item, value)
                for item in committed_facts + new_facts
            ):
                add(
                    AdmissionReasonCode.FACT_CONFLICT,
                    "transaction introduces incompatible active Facts in overlapping scope and time",
                )
            new_facts.append(value)

        return TransactionValidationResult(
            valid=not issues,
            reason_codes=tuple(item[0] for item in issues),
            public_reasons=tuple(item[1] for item in issues),
        )

    def validate_or_raise(
        self,
        transaction: CognitiveTransaction,
        *,
        current_objects: tuple[CognitiveObject, ...] = (),
        current_relations: tuple[EvidenceLink, ...] = (),
    ) -> None:
        result = self.validate(
            transaction,
            current_objects=current_objects,
            current_relations=current_relations,
        )
        if not result.valid:
            raise CognitiveTransactionValidationError(result)
