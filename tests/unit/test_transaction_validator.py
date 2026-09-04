from __future__ import annotations

from datetime import UTC, datetime

from cogito.domain.enums import (
    AdmissionReasonCode,
    ChangeKind,
    CognitiveObjectType,
    CognitiveTargetType,
    EvidenceRelation,
    FactBasis,
    FactStatus,
    HypothesisStatus,
)
from cogito.domain.ids import (
    EpisodeId,
    EvidenceLinkId,
    FactId,
    HypothesisId,
    ObservationId,
    PropositionId,
    TransactionId,
)
from cogito.domain.models.event import CognitiveTransaction, ObjectChange, RelationChange
from cogito.domain.models.evidence import EvidenceLink
from cogito.domain.models.fact import Fact
from cogito.domain.models.hypothesis import Hypothesis
from cogito.domain.models.observation import ObservedProposition
from cogito.domain.policies.transaction import CognitiveTransactionValidator


NOW = datetime(2026, 1, 1, tzinfo=UTC)
EPISODE_ID = EpisodeId("episode-1")


def proposition(
    proposition_id: str = "p1", *, episode_id: EpisodeId = EPISODE_ID
) -> ObservedProposition:
    return ObservedProposition(
        id=PropositionId(proposition_id),
        episode_id=episode_id,
        observation_id=ObservationId("o1"),
        statement="mysqld listens on 3307",
        observed_at=NOW,
        created_at=NOW,
    )


def fact(
    fact_id: str = "f1",
    *,
    evidence_refs: tuple[EvidenceLinkId, ...] = (EvidenceLinkId("e1"),),
    value=3307,
    status: FactStatus = FactStatus.ACTIVE,
) -> Fact:
    return Fact(
        id=FactId(fact_id),
        episode_id=EPISODE_ID,
        statement=f"runtime port is {value}",
        subject="mysqld",
        predicate="runtime_port",
        value=value,
        scope="host-A",
        valid_from=NOW,
        valid_to=NOW,
        basis=FactBasis.DIRECT_MEASUREMENT,
        evidence_refs=evidence_refs,
        status=status,
        created_at=NOW,
    )


def hypothesis(
    *,
    evidence_refs: tuple[EvidenceLinkId, ...] = (EvidenceLinkId("e1"),),
    status: HypothesisStatus = HypothesisStatus.PLAUSIBLE,
) -> Hypothesis:
    return Hypothesis(
        id=HypothesisId("h1"),
        episode_id=EPISODE_ID,
        statement="endpoint mismatch contributes to failure",
        target_problem="DB connectivity",
        evidence_refs=evidence_refs,
        prediction="using the listener endpoint removes refusal",
        status=status,
        created_at=NOW,
        updated_at=NOW,
    )


def relation(
    *,
    evidence_id: str = "e1",
    proposition_id: str = "p1",
    target_type: CognitiveTargetType = CognitiveTargetType.FACT,
    target_id: str = "f1",
    relation_type: EvidenceRelation = EvidenceRelation.SUPPORTS,
    episode_id: EpisodeId = EPISODE_ID,
) -> EvidenceLink:
    return EvidenceLink(
        id=EvidenceLinkId(evidence_id),
        episode_id=episode_id,
        proposition_id=PropositionId(proposition_id),
        target_type=target_type,
        target_id=target_id,
        relation=relation_type,
        reason="fixture",
        created_at=NOW,
    )


def create_change(value, object_type: CognitiveObjectType) -> ObjectChange:
    return ObjectChange(
        kind=ChangeKind.CREATE,
        object_type=object_type,
        object_id=str(value.id),
        value=value,
    )


def transaction(
    *,
    object_changes: tuple[ObjectChange, ...] = (),
    relation_changes: tuple[RelationChange, ...] = (),
) -> CognitiveTransaction:
    return CognitiveTransaction(
        id=TransactionId("tx1"),
        episode_id=EPISODE_ID,
        base_version=0,
        object_changes=object_changes,
        relation_changes=relation_changes,
    )


def validate(tx: CognitiveTransaction, *, current_objects=(), current_relations=()):
    return CognitiveTransactionValidator().validate(
        tx,
        current_objects=tuple(current_objects),
        current_relations=tuple(current_relations),
    )


def test_relation_may_target_fact_created_in_same_transaction() -> None:
    p1 = proposition()
    f1 = fact()
    link = relation()
    tx = transaction(
        object_changes=(
            create_change(p1, CognitiveObjectType.PROPOSITION),
            create_change(f1, CognitiveObjectType.FACT),
        ),
        relation_changes=(RelationChange(kind=ChangeKind.CREATE, value=link),),
    )

    result = validate(tx)

    assert result.valid is True
    assert result.reason_codes == ()


def test_reserved_target_without_corresponding_create_is_invalid() -> None:
    tx = transaction(
        relation_changes=(
            RelationChange(kind=ChangeKind.CREATE, value=relation(target_id="reserved-f")),
        )
    )

    result = validate(tx, current_objects=(proposition(),))

    assert result.valid is False
    assert AdmissionReasonCode.MISSING_DRAFT_OBJECT in result.reason_codes


def test_fact_evidence_ref_must_target_the_fact_itself() -> None:
    f1 = fact()
    wrong = relation(target_id="other-f")
    tx = transaction(
        object_changes=(create_change(f1, CognitiveObjectType.FACT),),
        relation_changes=(RelationChange(kind=ChangeKind.CREATE, value=wrong),),
    )

    result = validate(
        tx,
        current_objects=(proposition(), fact("other-f")),
    )

    assert AdmissionReasonCode.EVIDENCE_REFERENCE_INVALID in result.reason_codes


def test_hypothesis_requires_a_support_ref_targeting_itself() -> None:
    h1 = hypothesis()
    contradicts = relation(
        target_type=CognitiveTargetType.HYPOTHESIS,
        target_id="h1",
        relation_type=EvidenceRelation.CONTRADICTS,
    )
    tx = transaction(
        object_changes=(create_change(h1, CognitiveObjectType.HYPOTHESIS),),
        relation_changes=(RelationChange(kind=ChangeKind.CREATE, value=contradicts),),
    )

    result = validate(tx, current_objects=(proposition(),))

    assert AdmissionReasonCode.NO_SUPPORTING_EVIDENCE in result.reason_codes


def test_wrong_declared_target_type_and_cross_episode_relation_are_invalid() -> None:
    wrong_type = transaction(
        relation_changes=(
            RelationChange(
                kind=ChangeKind.CREATE,
                value=relation(target_type=CognitiveTargetType.HYPOTHESIS),
            ),
        )
    )
    cross_episode_link = relation(episode_id=EpisodeId("episode-2"))
    cross_episode = CognitiveTransaction.model_construct(
        id=TransactionId("tx-cross"),
        episode_id=EPISODE_ID,
        base_version=0,
        events=(),
        object_changes=(),
        relation_changes=(
            RelationChange(kind=ChangeKind.CREATE, value=cross_episode_link),
        ),
    )

    mismatch_result = validate(
        wrong_type, current_objects=(proposition(), fact())
    )
    episode_result = validate(
        cross_episode, current_objects=(proposition(), fact())
    )

    assert AdmissionReasonCode.TARGET_TYPE_MISMATCH in mismatch_result.reason_codes
    assert AdmissionReasonCode.EPISODE_MISMATCH in episode_result.reason_codes


def test_conflicting_object_changes_are_invalid() -> None:
    f1 = fact()
    duplicate = transaction(
        object_changes=(
            create_change(f1, CognitiveObjectType.FACT),
            create_change(f1, CognitiveObjectType.FACT),
        )
    )

    result = validate(duplicate)

    assert AdmissionReasonCode.CONFLICTING_OBJECT_CHANGES in result.reason_codes


def test_new_fact_and_hypothesis_lifecycle_states_are_restricted() -> None:
    superseded = transaction(
        object_changes=(
            create_change(
                fact(status=FactStatus.SUPERSEDED), CognitiveObjectType.FACT
            ),
        )
    )
    supported = transaction(
        object_changes=(
            create_change(
                hypothesis(status=HypothesisStatus.SUPPORTED),
                CognitiveObjectType.HYPOTHESIS,
            ),
        )
    )

    assert AdmissionReasonCode.INVALID_INITIAL_STATUS in validate(
        superseded
    ).reason_codes
    assert AdmissionReasonCode.INVALID_INITIAL_STATUS in validate(supported).reason_codes


def test_transaction_detects_fact_conflict_without_mutating_existing_fact() -> None:
    existing = fact("existing-f", value=3306)
    candidate = fact("new-f", value=3307)
    tx = transaction(
        object_changes=(create_change(candidate, CognitiveObjectType.FACT),)
    )

    result = validate(tx, current_objects=(existing,))

    assert AdmissionReasonCode.FACT_CONFLICT in result.reason_codes
    assert existing.status is FactStatus.ACTIVE
