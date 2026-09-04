from __future__ import annotations

from typing import cast

from cogito.domain.base import DomainModel
from cogito.domain.enums import CognitiveTargetType
from cogito.domain.ids import EpisodeId, FactId, HypothesisId, new_id


class DraftCognitiveTarget(DomainModel):
    """A transaction-local target reservation, not committed cognition."""

    episode_id: EpisodeId
    target_type: CognitiveTargetType
    target_id: str
    committed: bool = False


class DraftTargetFactory:
    @staticmethod
    def reserve_fact(
        episode_id: EpisodeId, *, target_id: FactId | None = None
    ) -> DraftCognitiveTarget:
        reserved = target_id or new_id(FactId)
        return DraftCognitiveTarget(
            episode_id=episode_id,
            target_type=CognitiveTargetType.FACT,
            target_id=str(reserved),
        )

    @staticmethod
    def reserve_hypothesis(
        episode_id: EpisodeId, *, target_id: HypothesisId | None = None
    ) -> DraftCognitiveTarget:
        reserved = target_id or new_id(HypothesisId)
        return DraftCognitiveTarget(
            episode_id=episode_id,
            target_type=CognitiveTargetType.HYPOTHESIS,
            target_id=str(reserved),
        )

    @staticmethod
    def as_fact_id(target: DraftCognitiveTarget) -> FactId:
        if target.target_type is not CognitiveTargetType.FACT:
            raise ValueError("draft target is not a Fact reservation")
        return cast(FactId, target.target_id)

    @staticmethod
    def as_hypothesis_id(target: DraftCognitiveTarget) -> HypothesisId:
        if target.target_type is not CognitiveTargetType.HYPOTHESIS:
            raise ValueError("draft target is not a Hypothesis reservation")
        return cast(HypothesisId, target.target_id)
