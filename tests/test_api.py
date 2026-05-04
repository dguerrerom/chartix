import pytest
import polars as pl
from datetime import date
from chartix.api import anniversary_hits, ones_calendar

def test_anniversary_hits_success(temp_index):
    # Search for anniversary hits on Jan 7, 2024
    # 1990-01-07 was a Sunday. 2024-01-07 is a Sunday.
    # The week of 2024-01-07 starts on 2024-01-07 (Sunday).
    # 1990-01-07 is ordinal day 7.
    # 1991-01-06 is ordinal day 6.
    # If we search for 2024-01-07, the week is 2024-01-07 to 2024-01-13.
    # Ordinal days for that week: 7 to 13.
    # So 1990-01-07 (day 7) should match. 1991-01-06 (day 6) should NOT match.
    
    df = anniversary_hits("2024-01-07")
    assert isinstance(df, pl.DataFrame)
    assert len(df) > 0
    assert "Artist A" in df["artist"].to_list()
    assert "Artist B" not in df["artist"].to_list()

def test_anniversary_hits_fallback_today(temp_index, monkeypatch):
    # Mock date.today() to return a specific date
    class MockDate(date):
        @classmethod
        def today(cls):
            return date(2024, 1, 7)
    
    monkeypatch.setattr("chartix.api.date", MockDate)
    
    df = anniversary_hits()
    assert isinstance(df, pl.DataFrame)
    assert len(df) > 0
    assert "Artist A" in df["artist"].to_list()

def test_anniversary_hits_no_index(monkeypatch, tmp_path):
    # Mock _get_index_path to a non-existent file
    missing_path = tmp_path / "non_existent.parquet"
    monkeypatch.setattr("chartix.api._get_index_path", lambda: missing_path)
    
    df = anniversary_hits("2024-01-07")
    assert isinstance(df, pl.DataFrame)
    assert df.is_empty()

def test_anniversary_hits_invalid_date(temp_index):
    df = anniversary_hits("not-a-date")
    assert isinstance(df, pl.DataFrame)
    assert df.is_empty()

def test_ones_calendar_basic(temp_index):
    # Test for year 2024
    df = ones_calendar(year=2024)
    assert isinstance(df, pl.DataFrame)
    assert not df.is_empty()
    assert "week" in df.columns
    assert "date" in df.columns
    assert "event" in df.columns

def test_ones_calendar_leap_year_adjustment(temp_index):
    # Leap Artist had a #1 on 1992-02-29
    # In 2023 (non-leap), it should be adjusted to 2023-02-28
    df = ones_calendar(year=2023)
    leap_hits = df.filter(pl.col("event").str.contains("Leap Artist"))
    assert not leap_hits.is_empty()
    assert leap_hits["date"][0] == date(2023, 2, 28)

def test_ones_calendar_iso_week(temp_index):
    # 2024-01-01 is a Monday.
    # 2024-01-07 is a Sunday.
    df = ones_calendar(year=2024)
    
    # Artist C: 1990-01-01 -> 2024-01-01. ISO Week 1.
    artist_c = df.filter(pl.col("event").str.contains("Artist C"))
    assert not artist_c.is_empty()
    assert artist_c["week"][0] == 1

    # Artist A: 1990-01-07 -> 2024-01-07. ISO Week 1.
    artist_a = df.filter(pl.col("event").str.contains("Artist A"))
    assert not artist_a.is_empty()
    assert artist_a["week"][0] == 1

def test_ones_calendar_filtering(temp_index):
    # Filter by provider
    df_p1 = ones_calendar(provider="p1", year=2024)
    assert all(df_p1["event"].str.contains("p1") == False) 
    # Wait, the event string is: pl.col("song") + " by " + pl.col("artist") + " reaches #1 on the " + pl.col("chart")
    # Chart names are c1, c2, c3.
    assert all(df_p1["event"].str.contains("c1"))
    assert not any(df_p1["event"].str.contains("c2"))
