from typing import Protocol

from cogito.domain.models.action import ActionDecision, ActionResult


class ToolExecutor(Protocol):
    async def execute(self, action: ActionDecision) -> ActionResult: ...

