from dataclasses import dataclass

from cogito.ports.cognitive_store import CognitiveStore


@dataclass(frozen=True)
class CognitiveScheduler:
    """Story 0 wiring point; cognitive-loop scheduling starts in later stories."""

    store: CognitiveStore

