from __future__ import annotations

from typing import Any, Protocol, TypeVar

from pydantic import BaseModel, ConfigDict

from cogito.domain.base import ProposalModel


ProposalT = TypeVar("ProposalT", bound=ProposalModel)


class ModelRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: str
    input_key: str
    context: dict[str, Any]


class UnknownModelResponse(LookupError):
    pass


class ModelProvider(Protocol):
    async def propose(
        self, request: ModelRequest, response_model: type[ProposalT]
    ) -> ProposalT: ...

