from __future__ import annotations

from typing import NewType, TypeVar, cast
from uuid import uuid4


EpisodeId = NewType("EpisodeId", str)
ObservationId = NewType("ObservationId", str)
PropositionId = NewType("PropositionId", str)
FactId = NewType("FactId", str)
HypothesisId = NewType("HypothesisId", str)
GapId = NewType("GapId", str)
EvidenceLinkId = NewType("EvidenceLinkId", str)
ActionId = NewType("ActionId", str)
EventId = NewType("EventId", str)
TransactionId = NewType("TransactionId", str)

IdT = TypeVar("IdT")


def new_id(id_type: type[IdT]) -> IdT:
    """Create a UUID string wrapped in the requested strong ID type."""

    return cast(IdT, id_type(str(uuid4())))

