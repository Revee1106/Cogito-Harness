from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import typer
from rich.console import Console
from rich.table import Table

from cogito.adapters.sqlite.store import SQLiteCognitiveStore
from cogito.config import load_config
from cogito.domain.enums import EpisodeStatus
from cogito.domain.ids import EpisodeId, new_id
from cogito.domain.models.episode import Episode
from cogito.domain.models.goal import AcceptanceCriterion, GoalContract
from cogito.ports.cognitive_store import EpisodeNotFound


app = typer.Typer(help="Cogito-Harness Story 0 kernel CLI.")
episode_app = typer.Typer(help="Create and inspect episodes.")
app.add_typer(episode_app, name="episode")
console = Console()


def _store() -> SQLiteCognitiveStore:
    return SQLiteCognitiveStore(load_config().storage.sqlite_path)


@app.command("init")
def initialize() -> None:
    """Create the five-table SQLite baseline."""

    store = _store()
    try:
        store.create_schema()
        console.print(f"Initialized Cogito store at [cyan]{store.path}[/cyan]")
    finally:
        store.close()


@episode_app.command("create")
def create_episode(
    goal: str = typer.Option(..., "--goal", help="Primary objective."),
    constraint: list[str] | None = typer.Option(None, "--constraint"),
    criterion: list[str] | None = typer.Option(None, "--criterion"),
) -> None:
    """Create an episode with an explicit version-1 goal contract."""

    store = _store()
    try:
        store.create_schema()
        now = datetime.now(UTC)
        episode = Episode(
            id=new_id(EpisodeId),
            status=EpisodeStatus.ACTIVE,
            cognitive_version=0,
            goal_contract_version=0,
            created_at=now,
            updated_at=now,
        )
        contract = GoalContract(
            objective=goal,
            hard_constraints=tuple(constraint or ()),
            acceptance_criteria=tuple(
                AcceptanceCriterion(id=f"criterion-{index}", statement=statement)
                for index, statement in enumerate(criterion or (), start=1)
            ),
            version=1,
        )
        asyncio.run(store.create_episode(episode))
        asyncio.run(store.append_goal_contract_version(episode.id, contract))
        console.print(f"Created episode [cyan]{episode.id}[/cyan]")
    finally:
        store.close()


@episode_app.command("show")
def show_episode(episode_id: str) -> None:
    """Display the committed state projection for one episode."""

    store = _store()
    try:
        state = asyncio.run(store.load_episode_state(EpisodeId(episode_id)))
    except EpisodeNotFound:
        console.print(f"[red]Episode not found:[/red] {episode_id}")
        raise typer.Exit(code=1) from None
    finally:
        store.close()

    table = Table(title="Cogito Episode", show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Episode", str(state.episode.id))
    table.add_row("Status", state.episode.status.value)
    table.add_row("Goal", state.goal_contract.objective if state.goal_contract else "—")
    table.add_row("Facts", str(len(state.facts)))
    table.add_row("Hypotheses", str(len(state.hypotheses)))
    table.add_row("Gaps", str(len(state.gaps)))
    table.add_row("Cognitive Version", str(state.episode.cognitive_version))
    console.print(table)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
