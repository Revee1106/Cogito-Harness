from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EpisodeRecord(Base):
    __tablename__ = "episodes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    cognitive_version: Mapped[int] = mapped_column(Integer, nullable=False)
    goal_contract_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class GoalContractRecord(Base):
    __tablename__ = "goal_contracts"

    episode_id: Mapped[str] = mapped_column(
        ForeignKey("episodes.id"), primary_key=True
    )
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CognitiveEventRecord(Base):
    """Append-only event row exposed through insert/list adapter operations."""

    __tablename__ = "cognitive_events"
    __table_args__ = (
        UniqueConstraint("episode_id", "sequence", name="uq_event_episode_sequence"),
        Index("ix_cognitive_events_episode_sequence", "episode_id", "sequence"),
        Index("ix_cognitive_events_transaction_id", "transaction_id"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), nullable=False)
    transaction_id: Mapped[str] = mapped_column(String, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    cause_id: Mapped[str | None] = mapped_column(String, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CognitiveObjectRecord(Base):
    __tablename__ = "cognitive_objects"
    __table_args__ = (Index("ix_cognitive_objects_episode_type", "episode_id", "object_type"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), nullable=False)
    object_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CognitiveRelationRecord(Base):
    __tablename__ = "cognitive_relations"
    __table_args__ = (Index("ix_cognitive_relations_episode", "episode_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String, nullable=False)
    target_id: Mapped[str] = mapped_column(String, nullable=False)
    relation_type: Mapped[str] = mapped_column(String, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
