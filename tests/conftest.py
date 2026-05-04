import pytest
import polars as pl
from pathlib import Path
from datetime import date
from chartix.api import normalize_text

@pytest.fixture
def mock_index_path(tmp_path):
    """Fixture to provide a path for a temporary search index."""
    return tmp_path / "search_index.parquet"

@pytest.fixture
def sample_data():
    """Fixture providing sample chart data for indexing."""
    return [
        # Weekly chart
        {
            "provider": "p1",
            "chart": "c1",
            "frequency": "weekly",
            "date": date(1990, 1, 7), # Sunday
            "this_week": 1,
            "artist": "Artist A",
            "song": "Song A",
        },
        {
            "provider": "p1",
            "chart": "c1",
            "frequency": "weekly",
            "date": date(1991, 1, 6), # Sunday
            "this_week": 1,
            "artist": "Artist B",
            "song": "Song B",
        },
        # Monthly chart
        {
            "provider": "p2",
            "chart": "c2",
            "frequency": "monthly",
            "date": date(1990, 1, 1),
            "this_week": 1,
            "artist": "Artist C",
            "song": "Song C",
        },
        # Fortnightly chart
        {
            "provider": "p3",
            "chart": "c3",
            "frequency": "fortnightly",
            "date": date(1990, 1, 1),
            "this_week": 1,
            "artist": "Artist D",
            "song": "Song D",
        },
        {
            "provider": "p3",
            "chart": "c3",
            "frequency": "fortnightly",
            "date": date(1990, 1, 15),
            "this_week": 1,
            "artist": "Artist E",
            "song": "Song E",
        },
        # Leap year case
        {
            "provider": "p1",
            "chart": "c1",
            "frequency": "weekly",
            "date": date(1992, 2, 29),
            "this_week": 1,
            "artist": "Leap Artist",
            "song": "Leap Song",
        },
    ]

@pytest.fixture
def temp_index(mock_index_path, sample_data, monkeypatch):
    """Fixture that creates a temporary search index and mocks its path in the API."""
    df = pl.DataFrame(sample_data).with_columns([
        pl.col("date").cast(pl.Date),
        pl.col("this_week").cast(pl.Int64),
    ]).with_columns([
        pl.col("artist").map_elements(normalize_text, return_dtype=pl.String).alias("artist_norm"),
        pl.col("song").map_elements(normalize_text, return_dtype=pl.String).alias("song_norm"),
        pl.col("date").dt.year().alias("year").cast(pl.Int32),
        pl.col("date").dt.month().alias("month").cast(pl.Int32),
        pl.col("date").dt.day().alias("day").cast(pl.Int32),
    ])
    
    df.write_parquet(mock_index_path)
    
    # Monkeypatch ROOT or _get_index_path to use our temp index
    # Since _get_index_path uses ROOT, monkeypatching ROOT might be enough
    # but ROOT is a global constant in api.py. 
    # Let's monkeypatch _get_index_path instead.
    monkeypatch.setattr("chartix.api._get_index_path", lambda: mock_index_path)
    # Also monkeypatch _check_index_exists if needed, but it calls _get_index_path().exists()
    
    return mock_index_path
