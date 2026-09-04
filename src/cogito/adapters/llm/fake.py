from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from cogito.domain.base import ProposalModel
from cogito.ports.model_provider import ModelRequest, ProposalT, UnknownModelResponse


class FakeModelProvider:
    """Deterministic proposal source with no network behavior."""

    def __init__(self, responses: Mapping[str, ProposalModel | Mapping[str, Any]]) -> None:
        self._responses = dict(responses)
        self.received_requests: list[ModelRequest] = []

    async def propose(
        self, request: ModelRequest, response_model: type[ProposalT]
    ) -> ProposalT:
        self.received_requests.append(request)
        try:
            response = self._responses[request.input_key]
        except KeyError as error:
            raise UnknownModelResponse(request.input_key) from error
        if isinstance(response, response_model):
            return response
        if isinstance(response, ProposalModel):
            return response_model.model_validate(response.model_dump())
        return response_model.model_validate(response)

