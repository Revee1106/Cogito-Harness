from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime

from cogito.domain.enums import ActionResultStatus
from cogito.domain.models.action import ActionDecision, ActionResult


class FakeToolExecutor:
    """In-memory tool fixture that cannot execute external operations."""

    def __init__(
        self,
        *,
        responses: Mapping[str, str] | None = None,
        errors: Mapping[str, str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._responses = dict(responses or {})
        self._errors = dict(errors or {})
        self._clock = clock or (lambda: datetime.now(UTC))
        self.received_actions: list[ActionDecision] = []

    @classmethod
    def success(
        cls,
        *,
        responses: Mapping[str, str],
        clock: Callable[[], datetime] | None = None,
    ) -> "FakeToolExecutor":
        return cls(responses=responses, clock=clock)

    @classmethod
    def failure(
        cls,
        *,
        errors: Mapping[str, str],
        clock: Callable[[], datetime] | None = None,
    ) -> "FakeToolExecutor":
        return cls(errors=errors, clock=clock)

    async def execute(self, action: ActionDecision) -> ActionResult:
        self.received_actions.append(action)
        started_at = self._clock()
        tool_name = action.tool_name or ""
        if tool_name in self._errors:
            return ActionResult(
                action_id=action.id,
                status=ActionResultStatus.FAILURE,
                error=self._errors[tool_name],
                started_at=started_at,
                finished_at=self._clock(),
            )
        if tool_name not in self._responses:
            return ActionResult(
                action_id=action.id,
                status=ActionResultStatus.FAILURE,
                error=f"no fake response configured for {tool_name!r}",
                started_at=started_at,
                finished_at=self._clock(),
            )
        return ActionResult(
            action_id=action.id,
            status=ActionResultStatus.SUCCESS,
            raw_output=self._responses[tool_name],
            started_at=started_at,
            finished_at=self._clock(),
        )

