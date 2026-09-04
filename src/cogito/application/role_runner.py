from dataclasses import dataclass

from cogito.ports.model_provider import ModelProvider


@dataclass(frozen=True)
class RoleRunner:
    """Story 0 wiring point for provider-neutral semantic functions."""

    provider: ModelProvider

