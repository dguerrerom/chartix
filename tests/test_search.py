import pytest
import polars as pl
from chartix.api import search_hits

def test_search_hits_provider_filter(temp_index):
    """Test search_hits with only provider filter."""
    # p1 has 3 entries: Artist A, Artist B, Leap Artist
    df = search_hits(provider="p1")
    assert len(df) == 3
    assert set(df["artist"]) == {"Artist A", "Artist B", "Leap Artist"}
    assert all(df["provider"] == "p1")

    # p2 has 1 entry: Artist C
    df = search_hits(provider="p2")
    assert len(df) == 1
    assert df["artist"][0] == "Artist C"
    assert df["provider"][0] == "p2"

def test_search_hits_chart_filter(temp_index):
    """Test search_hits with only chart filter."""
    # c1 has 3 entries
    df = search_hits(chart="c1")
    assert len(df) == 3
    assert all(df["chart"] == "c1")

    # c3 has 2 entries
    df = search_hits(chart="c3")
    assert len(df) == 2
    assert all(df["chart"] == "c3")

def test_search_hits_provider_and_chart_filter(temp_index):
    """Test search_hits with both provider and chart filters."""
    df = search_hits(provider="p1", chart="c1")
    assert len(df) == 3
    assert all((df["provider"] == "p1") & (df["chart"] == "c1"))

    # Non-existent combination
    df = search_hits(provider="p1", chart="c2")
    assert len(df) == 0

def test_search_hits_fuzzy_with_filters(temp_index):
    """Test fuzzy search combined with provider and chart filters."""
    # "Leap Artist" fuzzy matched with "Leap Artst" (dist=1)
    df = search_hits(artist="Leap Artst")
    assert len(df) == 1
    assert df["artist"][0] == "Leap Artist"

    # With correct provider filter
    df = search_hits(artist="Leap Artst", provider="p1")
    assert len(df) == 1
    assert df["artist"][0] == "Leap Artist"

    # With wrong provider filter
    df = search_hits(artist="Leap Artst", provider="p2")
    assert len(df) == 0

    # With correct chart filter
    df = search_hits(artist="Leap Artst", chart="c1")
    assert len(df) == 1
    assert df["artist"][0] == "Leap Artist"

def test_search_hits_best_position_with_filters(temp_index):
    """Test best_position=True combined with provider and chart filters."""
    # p1 has 3 songs, each appearing once in sample_data
    df = search_hits(provider="p1", best_position=True)
    assert len(df) == 3
    assert "best_rank" in df.columns
    assert "best_date" in df.columns
    assert all(df["provider"] == "p1")

    # Filter by chart as well
    df = search_hits(provider="p1", chart="c1", best_position=True)
    assert len(df) == 3
    assert all(df["chart"] == "c1")
