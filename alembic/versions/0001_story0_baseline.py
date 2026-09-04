"""Create the five-table Story 0 persistence baseline."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0001_story0"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "episodes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("cognitive_version", sa.Integer(), nullable=False),
        sa.Column("goal_contract_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "goal_contracts",
        sa.Column("episode_id", sa.String(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"]),
        sa.PrimaryKeyConstraint("episode_id", "version"),
    )
    op.create_table(
        "cognitive_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("episode_id", sa.String(), nullable=False),
        sa.Column("transaction_id", sa.String(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("cause_id", sa.String(), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("episode_id", "sequence", name="uq_event_episode_sequence"),
    )
    op.create_index(
        "ix_cognitive_events_episode_sequence",
        "cognitive_events",
        ["episode_id", "sequence"],
        unique=False,
    )
    op.create_index(
        "ix_cognitive_events_transaction_id",
        "cognitive_events",
        ["transaction_id"],
        unique=False,
    )
    op.create_table(
        "cognitive_objects",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("episode_id", sa.String(), nullable=False),
        sa.Column("object_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cognitive_objects_episode_type",
        "cognitive_objects",
        ["episode_id", "object_type"],
        unique=False,
    )
    op.create_table(
        "cognitive_relations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("episode_id", sa.String(), nullable=False),
        sa.Column("source_id", sa.String(), nullable=False),
        sa.Column("target_id", sa.String(), nullable=False),
        sa.Column("relation_type", sa.String(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cognitive_relations_episode",
        "cognitive_relations",
        ["episode_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_cognitive_relations_episode", table_name="cognitive_relations")
    op.drop_table("cognitive_relations")
    op.drop_index("ix_cognitive_objects_episode_type", table_name="cognitive_objects")
    op.drop_table("cognitive_objects")
    op.drop_index("ix_cognitive_events_transaction_id", table_name="cognitive_events")
    op.drop_index("ix_cognitive_events_episode_sequence", table_name="cognitive_events")
    op.drop_table("cognitive_events")
    op.drop_table("goal_contracts")
    op.drop_table("episodes")

