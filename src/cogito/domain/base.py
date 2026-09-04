from pydantic import BaseModel, ConfigDict


class DomainModel(BaseModel):
    """Base for committed, immutable-ish domain values."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class ProposalModel(BaseModel):
    """Base for uncommitted semantic-runtime proposals."""

    model_config = ConfigDict(frozen=True, extra="forbid")

