#!/usr/bin/env python3
"""
Core API for music charts data:
- Frictionless Data Package generation
- Search index building
- Query functions (anniversary hits, fuzzy search)
"""

import json
import logging
import re
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import polars as pl
import polars_distance as pld
from pydantic import AliasPath, BaseModel, Field

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
# Root data directory (default: ../data)
ROOT = Path(__file__).parent.parent.parent / "data"

# Fuzzy matching threshold for Damerau-Levenshtein distance
FUZZY_DISTANCE_THRESHOLD = 2

# Default ranks
DEFAULT_ANNIVERSARY_RANK = 1
DEFAULT_PEAK_RANK = 10

# Set up logging (basic config, can be overridden)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Text normalization
# ----------------------------------------------------------------------
def normalize_text(text: str) -> str:
    """Standardize text for search indexing and matching."""
    if not text:
        return ""
    # Lowercase
    s = text.lower()
    # Remove diacritics (Unicode NFKD → ASCII)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    # Strip content inside parentheses or brackets
    s = re.sub(r"[\(\[].*?[\)\]]", "", s)
    # Remove leading articles (English and Spanish)
    s = re.sub(r"^(the|a|an|el|la|los|las|un|una)\s+", "", s)
    # Replace common conjunctions and "featuring" tags with '&'
    s = re.sub(r"\b(and|with|feat|ft|featuring|pres|presents|y|con|e|et)\b", "&", s)
    # Keep only alphanumeric characters and '&'
    s = re.sub(r"[^a-z0-9&]", "", s)
    return s.strip()


def _remove_diacritics(text: str) -> str:
    """Remove diacritics from a string (used after native Polars steps)."""
    if not text:
        return text
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


# ----------------------------------------------------------------------
# Pydantic models for Frictionless catalog
# ----------------------------------------------------------------------
class ChartResource(BaseModel):
    """Represents a specific chart's data files and schema."""

    name: str
    path: str | list[str]
    frequency: str = Field(..., validation_alias=AliasPath("custom", "frequency"))


class ProviderPackage(BaseModel):
    """The datapackage.json within a provider folder."""

    name: str
    resources: list[ChartResource]


class CatalogProvider(BaseModel):
    """A provider entry in the master catalog."""

    name: str
    path: str
    charts: list[dict[str, Any]] = Field(..., validation_alias=AliasPath("custom", "charts"))


class MasterCatalog(BaseModel):
    """The root datapackage.json in the data directory."""

    resources: list[CatalogProvider]


# ----------------------------------------------------------------------
# Catalog helpers
# ----------------------------------------------------------------------
def _load_catalog() -> MasterCatalog:
    """Load and validate the master catalog."""
    catalog_path = ROOT / "datapackage.json"
    with open(catalog_path, encoding="utf-8") as f:
        return MasterCatalog.model_validate(json.load(f))


def list_charts() -> list[dict[str, Any]]:
    """Return all available charts across all providers."""
    cat = _load_catalog()
    # Flatten provider and chart data into a single list of dictionaries
    return [{"provider": p.name, **c} for p in cat.resources for c in p.charts]


# ----------------------------------------------------------------------
# Search index building
# ----------------------------------------------------------------------
def build_search_index() -> None:
    """Aggregates all CSVs, normalizes search fields, and exports a Parquet index."""
    lfs = []
    # Iterate over providers from the master catalog
    for p_entry in _load_catalog().resources:
        # Load the provider's datapackage.json
        p_pkg_path = ROOT / p_entry.path
        with open(p_pkg_path, encoding="utf-8") as f:
            pkg = ProviderPackage.model_validate(json.load(f))
        # For each chart in the provider
        for res in pkg.resources:
            paths = [res.path] if isinstance(res.path, str) else res.path
            csv_files = [p_pkg_path.parent / p for p in paths]
            # Lazy scan the CSV files and project the needed columns
            lf = (
                pl.scan_csv(csv_files)
                .select(
                    [
                        pl.lit(p_entry.name).alias("provider"),
                        pl.lit(res.name).alias("chart"),
                        pl.lit(res.frequency).alias("frequency"),
                        pl.col("date").str.strptime(pl.Date, "%Y-%m-%d").alias("date"),
                        pl.col("this_week").cast(pl.Int64).alias("this_week"),
                        pl.col("artist"),
                        pl.col("song"),
                        # Hybrid normalization for artist_norm
                        pl.col("artist")
                        .str.to_lowercase()
                        .str.replace_all(r"[\(\[].*?[\)\]]", "")
                        .str.replace(r"^(the|a|an|el|la|los|las|un|una)\s+", "")
                        .str.replace_all(
                            r"\b(and|with|feat|ft|featuring|pres|presents|y|con|e|et)\b", "&"
                        )
                        .str.replace_all(r"[^a-z0-9&]", "")
                        .map_elements(_remove_diacritics, return_dtype=pl.String)
                        .alias("artist_norm"),
                        # Same for song_norm
                        pl.col("song")
                        .str.to_lowercase()
                        .str.replace_all(r"[\(\[].*?[\)\]]", "")
                        .str.replace(r"^(the|a|an|el|la|los|las|un|una)\s+", "")
                        .str.replace_all(
                            r"\b(and|with|feat|ft|featuring|pres|presents|y|con|e|et)\b", "&"
                        )
                        .str.replace_all(r"[^a-z0-9&]", "")
                        .map_elements(_remove_diacritics, return_dtype=pl.String)
                        .alias("song_norm"),
                    ]
                )
                .with_columns(
                    [
                        # Extract date components for efficient filtering
                        pl.col("date").dt.year().alias("year"),
                        pl.col("date").dt.month().alias("month"),
                        pl.col("date").dt.day().alias("day"),
                    ]
                )
            )
            lfs.append(lf)
    if not lfs:
        raise ValueError("No data found to index.")
    # Concatenate all lazy frames and write to Parquet
    index_path = ROOT / "search_index.parquet"
    pl.concat(lfs).sink_parquet(index_path)


# ----------------------------------------------------------------------
# Anniversary hits
# ----------------------------------------------------------------------
def anniversary_hits(date_str: str | None = None, rank: int = 1) -> pl.DataFrame:
    """Find #rank hits for the current week in previous years using the index."""
    index_path = ROOT / "search_index.parquet"
    if not index_path.exists():
        logger.warning("Index not found. Please run `build-index` first.")
        return pl.DataFrame()

    # Parse reference date
    try:
        ref = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        logger.error(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")
        return pl.DataFrame()

    days_to_sunday = (ref.weekday() + 1) % 7
    week_start = ref - timedelta(days=days_to_sunday)
    week_end = week_start + timedelta(days=6)
    # Day-of-year numbers for the week boundaries (1-based)
    week_start_yday = week_start.timetuple().tm_yday
    week_end_yday = week_end.timetuple().tm_yday

    # For fortnightly charts, decide whether we are in the first half (1-14) or second half (15-31)
    ref_fortnight_day = 1 if ref.day <= 14 else 15

    # Scan the index and build conditions based on frequency
    lf = pl.scan_parquet(index_path)

    # Weekly condition: handle year wrap
    if week_start_yday <= week_end_yday:
        weekly_cond = (pl.col("frequency") == "weekly") & pl.col(
            "date"
        ).dt.ordinal_day().is_between(week_start_yday, week_end_yday)
    else:
        # Week wraps into next year: match days >= start OR <= end
        weekly_cond = (pl.col("frequency") == "weekly") & (
            (pl.col("date").dt.ordinal_day() >= week_start_yday)
            | (pl.col("date").dt.ordinal_day() <= week_end_yday)
        )

    monthly_cond = (pl.col("frequency") == "monthly") & (pl.col("month") == ref.month)
    fortnightly_cond = (
        (pl.col("frequency") == "fortnightly")
        & (pl.col("month") == ref.month)
        & (pl.col("day") == ref_fortnight_day)
    )

    # Apply filters: rank, frequency conditions, and year ≤ reference year
    df = (
        lf.filter(
            (pl.col("this_week") == rank)
            & (weekly_cond | monthly_cond | fortnightly_cond)
            & (pl.col("year") <= ref.year)
        )
        .select(["provider", "chart", "frequency", "year", "artist", "song", "date"])
        .collect()
    )

    return df.sort("year") if not df.is_empty() else pl.DataFrame()


# ----------------------------------------------------------------------
# Search hits (fuzzy matching)
# ----------------------------------------------------------------------
def search_hits(
    artist: str | None = None,
    song: str | None = None,
    date_str: str | None = None,
    year: int | None = None,
    best_position: bool = False,
) -> pl.DataFrame:
    """
    Search the index with fuzzy matching on artist/song (D-L ≤ FUZZY_DISTANCE_THRESHOLD)
    and exact filters on date/year.

    Args:
        artist: Artist name (fuzzy matched after normalization).
        song: Song title (fuzzy matched after normalization).
        date_str: Exact date YYYY-MM-DD.
        year: Exact year (ignored if date_str given).
        best_position: If True and date_str not given, return best rank per song.

    Returns:
        DataFrame with search results (individual rows or grouped best ranks).
    """
    index_path = ROOT / "search_index.parquet"
    if not index_path.exists():
        logger.warning("Index not found. Please run `build-index` first.")
        return pl.DataFrame()

    lf = pl.scan_parquet(index_path)

    # Apply fuzzy filters for artist and/or song
    if artist:
        q_artist = normalize_text(artist)
        lf = lf.filter(
            pld.col("artist_norm").dist_str.damerau_levenshtein(pl.lit(q_artist))
            <= FUZZY_DISTANCE_THRESHOLD
        )
    if song:
        q_song = normalize_text(song)
        lf = lf.filter(
            pld.col("song_norm").dist_str.damerau_levenshtein(pl.lit(q_song))
            <= FUZZY_DISTANCE_THRESHOLD
        )

    # Apply exact date/year filters
    if date_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")
            return pl.DataFrame()
        lf = lf.filter(pl.col("date") == d)
    elif year is not None:
        lf = lf.filter(pl.col("year") == year)

    if best_position and date_str is None:
        # Group by chart and song to get best rank and its earliest date
        df = (
            lf.group_by(["provider", "chart", "artist", "song"])
            .agg(
                [
                    pl.col("this_week").min().alias("best_rank"),
                    pl.col("date")
                    .filter(pl.col("this_week") == pl.col("this_week").min())
                    .min()
                    .alias("best_date"),
                ]
            )
            .sort("provider", "chart", "best_date")
            .collect()
        )
        return df
    else:
        # Return individual rows
        df = (
            lf.select(["provider", "chart", "date", "this_week", "artist", "song"])
            .sort(["provider", "chart", "date"])
            .collect()
        )
        return df


# ----------------------------------------------------------------------
# Best rank in year
# ----------------------------------------------------------------------
def best_rank_in_year(year: int, max_rank: int = DEFAULT_PEAK_RANK) -> pl.DataFrame:
    """
    For each chart, find songs that reached a rank <= max_rank in the given year,
    along with the best rank and the date it was achieved.

    Returns a DataFrame with columns:
        provider, chart, artist, song, best_rank, best_date
    """
    index_path = ROOT / "search_index.parquet"
    if not index_path.exists():
        logger.warning("Index not found. Please run `build-index` first.")
        return pl.DataFrame()

    # Scan the entire index (no year filter yet)
    lf = pl.scan_parquet(index_path)

    # Group by provider, chart, artist, song
    df = (
        lf.group_by(["provider", "chart", "artist", "song"])
        .agg(
            [
                pl.col("this_week").min().alias("best_rank"),
                # Get the earliest date among rows where this_week == best_rank
                pl.col("date")
                .filter(pl.col("this_week") == pl.col("this_week").min())
                .min()
                .alias("best_date"),
            ]
        )
        .filter((pl.col("best_rank") <= max_rank) & (pl.col("best_date").dt.year() == year))
        .sort(["provider", "chart", "artist", "best_rank", "song"])
        .collect()
    )
    return df


# ----------------------------------------------------------------------
# Chart(s) for a specific date
# ----------------------------------------------------------------------
def show_chart(
    date_str: str, provider: str | None = None, chart: str | None = None
) -> pl.DataFrame:
    """Return the chart(s) for a specific date, optionally filtered by provider and chart."""
    index_path = ROOT / "search_index.parquet"
    if not index_path.exists():
        logger.warning("Index not found. Please run `build-index` first.")
        return pl.DataFrame()

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logger.error(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")
        return pl.DataFrame()

    lf = pl.scan_parquet(index_path).filter(pl.col("date") == d)

    if provider:
        lf = lf.filter(pl.col("provider") == provider)
    if chart:
        lf = lf.filter(pl.col("chart") == chart)

    df = (
        lf.select(["provider", "chart", "this_week", "artist", "song", "date"])
        .sort(["provider", "chart", "this_week"])
        .collect()
    )
    return df


# ----------------------------------------------------------------------
# Generate CSV calendar of #1 hits of the current year
# ----------------------------------------------------------------------
def ones_calendar(
    provider: str | None = None,
    chart: str | None = None,
    year: int | None = None,
) -> pl.DataFrame:
    """
    Generate a calendar of #1 hits aligned with weeks of the target year.

    For each chart, only the first time a song reaches #1 is included.
    The output maps each hit's month/day to the target year and shows the
    ISO week number in that year.

    Args:
        provider: Filter by provider name (e.g., 'billboard').
        chart: Filter by chart name (e.g., 'billboard-hot100').
        year: Target year (defaults to current year).

    Returns:
        DataFrame with columns: week, date, event, sorted by week then date.
    """
    index_path = ROOT / "search_index.parquet"
    if not index_path.exists():
        logger.warning("Index not found. Please run `build-index` first.")
        return pl.DataFrame()

    target_year = year if year is not None else date.today().year
    is_leap = (target_year % 400 == 0) or (target_year % 4 == 0 and target_year % 100 != 0)

    # Scan the index lazily and filter for #1 entries.
    lf = pl.scan_parquet(index_path).filter(pl.col("this_week") == 1)

    if provider:
        lf = lf.filter(pl.col("provider") == provider)
    if chart:
        lf = lf.filter(pl.col("chart") == chart)

    # For each (provider, chart, artist, song), keep the earliest #1 date.
    df = (
        lf.group_by(["provider", "chart", "artist", "song"])
        .agg(pl.col("date").min().alias("date"))
        .select(["date", "artist", "song", "provider", "chart"])
        .collect()
    )

    if df.is_empty():
        logger.info("No #1 hits found with given filters.")
        return pl.DataFrame()

    df = df.with_columns(
        pl.col("date").dt.month().alias("month"),
        pl.col("date").dt.day().alias("day"),
    )

    # Adjust February 29 if target year is not a leap year.
    if not is_leap:
        df = df.with_columns(
            pl.when((pl.col("month") == 2) & (pl.col("day") == 29))
            .then(28)
            .otherwise(pl.col("day"))
            .alias("day")
        )

    # Build a date in the target year using the (possibly adjusted) month/day.
    df = df.with_columns(
        pl.date(
            year=pl.lit(target_year),
            month=pl.col("month"),
            day=pl.col("day"),
        ).alias("mapped_date")
    )

    # Compute ISO week number from the mapped date.
    df = df.with_columns(pl.col("mapped_date").dt.week().alias("week"))

    df = df.with_columns(
        (
            pl.col("song") + " by " + pl.col("artist") + " reaches #1 on the " + pl.col("chart")
        ).alias("event")
    )

    result = df.select(["week", "date", "event"]).sort(["week", "date"])

    return result


# ----------------------------------------------------------------------
# Frictionless Data Package generation
# ----------------------------------------------------------------------
def _load_json(path: Path) -> dict[str, Any]:
    """Load JSON from a file path."""
    with open(path, encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def _save_json(data: dict, path: Path) -> None:
    """Save a dictionary as formatted JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _find_metadata_file(provider_dir: Path) -> Path | None:
    """Find the first *-metadata.json inside a provider folder."""
    files = list(provider_dir.glob("*-metadata.json"))
    return files[0] if files else None


FIELD_TYPE_MAP = {
    "date": "date",
    "this_week": "integer",
    "last_week": "integer",
    "two_weeks_ago": "integer",
    "peak_position": "integer",
    "weeks_on_chart": "integer",
    "artist": "string",
    "song": "string",
    "composer": "string",
    "country": "string",
}


def _infer_field_type(field_name: str) -> str:
    """Return the Frictionless field type based on column name."""
    return FIELD_TYPE_MAP.get(field_name, "string")


def _build_tabular_schema(fields: list) -> dict:
    """Create a Table Schema from a list of field names."""
    return {"fields": [{"name": f, "type": _infer_field_type(f)} for f in fields]}


def _get_csv_paths(folder_name: str, provider_path: Path) -> list:
    """Return sorted list of relative paths to CSV files in a chart folder."""
    chart_dir = provider_path / folder_name
    return sorted(
        [str(p.relative_to(provider_path)).replace("\\", "/") for p in chart_dir.glob("*.csv")]
    )


def _create_provider_package(metadata_path: Path) -> dict:
    """Generate a provider-level datapackage.json from its metadata file."""
    metadata = _load_json(metadata_path)
    provider_path = metadata_path.parent
    resources = []
    for chart in metadata.get("charts", []):
        res = {
            "profile": "tabular-data-resource",
            "name": chart["prefix"],
            "title": chart["name"],
            "path": _get_csv_paths(chart["folder"], provider_path),
            "format": "csv",
            "mediatype": "text/csv",
            "dialect": {"delimiter": ","},
            "schema": _build_tabular_schema(chart["fields"]),
            "custom": {
                k: v for k, v in chart.items() if k not in ["name", "folder", "prefix", "fields"]
            },
        }
        resources.append(res)

    datapackage = {
        "profile": "tabular-data-package",
        "name": metadata["prefix"],
        "title": f"{metadata['name']} Charts Dataset",
        "resources": resources,
    }
    if metadata.get("country"):
        datapackage["country"] = metadata["country"]
    if metadata.get("url"):
        datapackage["url"] = metadata["url"]

    output_path = provider_path / "datapackage.json"
    _save_json(datapackage, output_path)
    return datapackage


def _build_catalog_resource(provider_dir: Path, data_root: Path, metadata_path: Path) -> dict:
    """Build a data-resource entry for the master catalog from a provider."""
    metadata = _load_json(metadata_path)
    relative_path = (provider_dir / "datapackage.json").relative_to(data_root)
    return {
        "profile": "data-resource",
        "name": provider_dir.name,
        "path": str(relative_path).replace("\\", "/"),
        "format": "json",
        "mediatype": "application/json",
        "title": metadata.get("name"),
        "custom": {
            "country": metadata.get("country"),
            "charts": [
                {
                    "name": c.get("prefix"),
                    "title": c.get("name"),
                    "frequency": c.get("frequency"),
                    "start_date": c.get("start_date"),
                    "end_date": c.get("end_date"),
                }
                for c in metadata.get("charts", [])
            ],
        },
    }


def generate_frictionless_packages(data_path: str = "data") -> None:
    """Generate provider datapackage.json files and the master catalog."""
    data_root = Path(data_path)
    catalog_resources = []
    for provider_dir in sorted(data_root.iterdir()):
        if not provider_dir.is_dir():
            continue
        metadata_file = _find_metadata_file(provider_dir)
        if not metadata_file:
            continue
        _create_provider_package(metadata_file)
        catalog_resources.append(_build_catalog_resource(provider_dir, data_root, metadata_file))

    catalog = {
        "profile": "data-package",
        "name": "international-music-charts-1980-1999",
        "title": "International Music Charts Dataset (1980-1999)",
        "description": "A collection of standardized music chart datasets from multiple providers.",
        "resources": catalog_resources,
    }
    catalog_path = data_root / "datapackage.json"
    _save_json(catalog, catalog_path)


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
__all__ = [
    "DEFAULT_ANNIVERSARY_RANK",
    "DEFAULT_PEAK_RANK",
    "anniversary_hits",
    "best_rank_in_year",
    "build_search_index",
    "generate_frictionless_packages",
    "list_charts",
    "search_hits",
    "show_chart",
]
