#!/usr/bin/env python3
"""
Command-line interface for music charts dataset.
"""

import sys
from datetime import date, datetime

import click
import polars as pl
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from chartix.api import (
    DEFAULT_ANNIVERSARY_RANK,
    DEFAULT_PEAK_RANK,
    anniversary_hits,
    best_rank_in_year,
    build_search_index,
    generate_frictionless_packages,
    list_charts,
    search_hits,
    show_chart,
)

console = Console()


# ----------------------------------------------------------------------
# Helper functions (unchanged from original)
# ----------------------------------------------------------------------
def _print_chart_group_header(chart_key: str, current_chart: str | None) -> str:
    """Print chart header if chart changed, return new current chart."""
    if chart_key != current_chart:
        console.print(f"\n[bold yellow]{chart_key}[/bold yellow]")
        return chart_key
    return current_chart


# ----------------------------------------------------------------------
# Rendering functions (unchanged from original)
# ----------------------------------------------------------------------
def render_list(charts):
    """Display all available charts grouped by provider."""
    if not charts:
        console.print("[bold red]No charts found in the catalog.[/bold red]")
        return

    console.print(Panel.fit("[bold white]Available Music Charts Catalog[/bold white]"))

    sorted_charts = sorted(charts, key=lambda x: (x["provider"], x["name"]))
    current_provider = None
    for c in sorted_charts:
        if c["provider"] != current_provider:
            current_provider = c["provider"]
            console.print(f"\n[bold yellow]{current_provider}[/bold yellow]")

        name = f"[dim cyan]{c['name']:<30}[/dim cyan]"
        title = f"[dim white]{c['title']:<35}[/dim white]"
        freq = c["frequency"]
        start = c.get("start_date") or "????"
        end = c.get("end_date") or "Present"
        meta = f"[bold green]{freq:<10}[/bold green][dim green]{start} to {end}[/dim green]"

        console.print(f"  [blue]>[/blue]  {name}  {title}  {meta}")


def render_anniversary(df: pl.DataFrame, ref_date: str, rank: int):
    """Display #rank hits for the week in history."""
    if df.is_empty():
        console.print(f"[bold red]No #{rank} hits found.[/bold red]")
        return

    try:
        r_day = datetime.strptime(ref_date, "%Y-%m-%d")
    except ValueError:
        console.print(f"[bold red]Invalid date format: {ref_date}. Use YYYY-MM-DD.[/bold red]")
        return

    console.print(
        Panel.fit(
            f"[bold white]#{rank} Hits This Week in History\n[/bold white]"
            f"[white]Reference date: {r_day:%b %d, %Y}[/white]"
        )
    )

    current_year = None
    for row in df.iter_rows(named=True):
        if row["year"] != current_year:
            current_year = row["year"]
            console.print(f"\n[bold yellow]{current_year}[/bold yellow]")

        freq = row["frequency"]
        d = row["date"]
        if freq == "monthly":
            day_str = f"{d:%b} *"
        elif freq == "fortnightly":
            half = "H1" if d.day <= 14 else "H2"
            day_str = f"{d:%b} {half}"
        else:
            day_str = f"{d:%b %d}"

        day = f"[dim cyan]{day_str:<6}[/dim cyan]"
        line = f"[dim white]{row['artist']} - {row['song']}[/dim white]"
        meta = f"[dim green]{row['provider']} / {row['chart']}[/dim green] [bold green]({row['frequency']})[/bold green]"

        console.print(f"  [blue]>[/blue]  {day}  {line}  {meta}")


def render_search(
    df: pl.DataFrame,
    artist: str | None,
    song: str | None,
    date_str: str | None,
    year: int | None,
    best_position: bool,
):
    """Display search results (full records or best positions)."""
    # Build description string
    if artist and song:
        desc = f"'{artist} - {song}'"
    elif artist:
        desc = f"artist '{artist}'"
    else:
        desc = f"song '{song}'"

    if df.is_empty():
        console.print(f"[bold red]No occurrences found for {desc}.[/bold red]")
        return

    if best_position and date_str is None:
        console.print(Panel.fit(f"[bold white]Best Positions for {desc}[/bold white]"))
    else:
        console.print(Panel.fit(f"[bold white]Search Results: {desc}[/bold white]"))

    current_chart = None
    for row in df.iter_rows(named=True):
        chart_key = f"{row['provider']} / {row['chart']}"
        current_chart = _print_chart_group_header(chart_key, current_chart)

        if best_position and date_str is None:
            best_date = row["best_date"]
            date_str_f = f"[dim cyan]{best_date:%Y-%m-%d}[/dim cyan]"
            rank_str = f"[bold magenta]#{row['best_rank']:<3}[/bold magenta]"
            song_line = f"[dim white]{row['artist']} - {row['song']}[/dim white]"
            console.print(f"  [blue]>[/blue]  {date_str_f}  {rank_str}  {song_line}")
        else:
            d = row["date"]
            date_str_f = f"[dim cyan]{d:%Y-%m-%d}[/dim cyan]"
            rank_str = f"[bold magenta]#{row['this_week']:<4}[/bold magenta]"
            match_str = f"[dim white]{row['artist']} - {row['song']}[/dim white]"
            console.print(f"  [blue]>[/blue]  {date_str_f}  {rank_str}  {match_str}")


def render_peak(df: pl.DataFrame, year: int, max_rank: int):
    """Display best ranks per song in a given year."""
    if df.is_empty():
        console.print(f"[bold red]No songs found in {year} with best rank ≤ {max_rank}.[/bold red]")
        return

    console.print(Panel.fit(f"[bold white]Best Ranks in {year} (≤ {max_rank})[/bold white]"))

    current_chart = None
    for row in df.iter_rows(named=True):
        chart_key = f"{row['provider']} / {row['chart']}"
        current_chart = _print_chart_group_header(chart_key, current_chart)
        best_date = row["best_date"]
        date_str = f"[dim cyan]{best_date:%Y-%m-%d}[/dim cyan]"
        rank_str = f"[bold magenta]#{row['best_rank']:<3}[/bold magenta]"
        song_line = f"[dim white]{row['artist']} - {row['song']}[/dim white]"
        console.print(f"  [blue]>[/blue]  {date_str}  {rank_str}  {song_line}")


def render_chart(df: pl.DataFrame, date_str: str, provider: str | None, chart: str | None):
    """Display the chart for a specific date."""
    if df.is_empty():
        console.print(f"[bold red]No chart data found for {date_str}.[/bold red]")
        if provider:
            console.print(f"Provider: {provider}")
        if chart:
            console.print(f"Chart: {chart}")
        return

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        console.print(f"[bold red]Invalid date format: {date_str}. Use YYYY-MM-DD.[/bold red]")
        return

    console.print(Panel.fit(f"[bold white]Hits of {d:%b %d, %Y}[bold white]"))

    current_chart = None
    for row in df.iter_rows(named=True):
        chart_key = f"{row['provider']} / {row['chart']}"
        current_chart = _print_chart_group_header(chart_key, current_chart)
        rank_str = f"[bold magenta]#{row['this_week']:<3}[/bold magenta]"
        song_line = f"[dim white]{row['artist']} - {row['song']}[/dim white]"
        console.print(f"  [blue]>[/blue]  {rank_str}  {song_line}")


def render_generate():
    """Generate Frictionless packages with progress spinner."""
    with Progress(
        SpinnerColumn(spinner_name="simpleDots"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Generating Frictionless packages...", total=None)
        try:
            generate_frictionless_packages()
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)
    console.print("Frictionless packages generated successfully.")


def render_build_index():
    """Build search index with progress spinner."""
    with Progress(
        SpinnerColumn(spinner_name="simpleDots"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Building search index...", total=None)
        try:
            build_search_index()
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)
    console.print("Search index built successfully.")


# ----------------------------------------------------------------------
# Click CLI
# ----------------------------------------------------------------------
@click.group()
def cli():
    """Query and manage the international music charts dataset."""
    pass


@cli.command()
def list():
    """List all available charts."""
    render_list(list_charts())


@cli.command()
@click.option("--date", "date_str", help="Reference date (YYYY-MM-DD). Defaults to today.")
@click.option(
    "--rank",
    type=int,
    default=DEFAULT_ANNIVERSARY_RANK,
    help=f"Chart position to retrieve. Defaults to {DEFAULT_ANNIVERSARY_RANK}.",
)
def anniversary(date_str, rank):
    """Find #1 (or another position) hits for this week in history."""
    ref = date_str if date_str is not None else date.today().strftime("%Y-%m-%d")
    render_anniversary(anniversary_hits(date_str, rank), ref, rank)


@cli.command()
@click.option("--artist", help="Artist name.")
@click.option("--song", help="Song title.")
@click.option("--date", help="Specific date (YYYY-MM-DD).")
@click.option("--year", type=int, help="Specific year.")
@click.option(
    "--best",
    "best_position",
    is_flag=True,
    help="Return only the best rank for each song (ignored with --date).",
)
def search(artist, song, date, year, best_position):
    """Search for an artist and/or song in the charts."""
    if not artist and not song:
        click.echo("Error: At least one of --artist or --song is required.", err=True)
        sys.exit(1)
    if date and year:
        click.echo("Error: --date and --year are mutually exclusive.", err=True)
        sys.exit(1)

    render_search(
        search_hits(
            artist=artist, song=song, date_str=date, year=year, best_position=best_position
        ),
        artist,
        song,
        date,
        year,
        best_position,
    )


@cli.command()
@click.option("--year", type=int, required=True, help="Year to search (e.g., 1985).")
@click.option(
    "--rank",
    type=int,
    default=DEFAULT_PEAK_RANK,
    help=f"Target rank (default {DEFAULT_PEAK_RANK}).",
)
def peak(year, rank):
    """Find best rank for each song in a given year."""
    render_peak(best_rank_in_year(year, rank), year, rank)


@cli.command()
@click.option("--date", required=True, help="Date (YYYY-MM-DD).")
@click.option("--provider", help="Filter by provider.")
@click.option("--chart", help="Filter by chart name.")
def show(date, provider, chart):
    """Show chart(s) for a specific date."""
    render_chart(show_chart(date_str=date, provider=provider, chart=chart), date, provider, chart)


@cli.command()
def generate():
    """Generate Frictionless Data Packages from metadata."""
    render_generate()


@cli.command(name="build-index")
def build_index():
    """Build search index from CSV files."""
    render_build_index()


if __name__ == "__main__":
    cli()
