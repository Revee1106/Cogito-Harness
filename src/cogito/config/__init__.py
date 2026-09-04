from __future__ import annotations

import os
import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class StorageConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    sqlite_path: Path = Path(".cogito/cogito.db")


class CogitoConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    storage: StorageConfig = StorageConfig()


def load_config(path: Path | None = None) -> CogitoConfig:
    config_path = path or Path("cogito.toml")
    raw = {}
    if config_path.exists():
        with config_path.open("rb") as stream:
            raw = tomllib.load(stream)
    config = CogitoConfig.model_validate(raw)
    override = os.getenv("COGITO_SQLITE_PATH")
    if override:
        config = config.model_copy(
            update={"storage": config.storage.model_copy(update={"sqlite_path": Path(override)})}
        )
    return config

