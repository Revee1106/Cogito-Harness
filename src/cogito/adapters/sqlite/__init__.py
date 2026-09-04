"""SQLite persistence adapter."""

from cogito.adapters.sqlite.migrations import upgrade_database
from cogito.adapters.sqlite.store import SQLiteCognitiveStore

__all__ = ["SQLiteCognitiveStore", "upgrade_database"]
