from __future__ import annotations

from datetime import UTC, datetime

from cogito.domain.ids import EpisodeId, ObservationId, new_id
from cogito.domain.models.action import ActionResult
from cogito.domain.models.observation import Observation


def action_result_to_observation(
    result: ActionResult,
    episode_id: EpisodeId,
    *,
    observed_at: datetime | None = None,
    created_at: datetime | None = None,
) -> Observation:
    """Explicitly cross the ActionResult -> Observation boundary."""

    now = datetime.now(UTC)
    content = result.raw_output if result.raw_output is not None else result.error
    return Observation(
        id=new_id(ObservationId),
        episode_id=episode_id,
        source=f"action-result:{result.action_id}",
        source_ref=str(result.action_id),
        raw_content=content or "no output",
        observed_at=observed_at or result.finished_at,
        created_at=created_at or now,
    )

