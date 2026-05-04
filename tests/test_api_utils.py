import pytest
from datetime import date
from pathlib import Path
import polars as pl
from chartix.api import (
    _normalization_expression,
    _parse_date,
    _get_index_path,
    _check_index_exists,
    ROOT
)

def test_normalization_expression():
    df = pl.DataFrame({
        "artist": ["The Beatles (Remastered)", "Lady Gaga feat. Colby O'Donis", "Édith Piaf"]
    })
    
    # Expected results after normalization
    # "The Beatles (Remastered)" -> "beatles"
    # "Lady Gaga feat. Colby O'Donis" -> "ladygaga&colbyodonis"
    # "Édith Piaf" -> "edithpiaf"
    
    expr = _normalization_expression("artist").alias("artist_norm")
    result = df.select(expr)
    
    assert result["artist_norm"][0] == "beatles"
    assert result["artist_norm"][1] == "ladygaga&colbyodonis"
    assert result["artist_norm"][2] == "edithpiaf"

def test_parse_date():
    assert _parse_date("2023-01-01") == date(2023, 1, 1)
    assert _parse_date("invalid-date") is None
    assert _parse_date("") is None
    assert _parse_date(None) is None

def test_get_index_path():
    expected_path = ROOT / "search_index.parquet"
    assert _get_index_path() == expected_path

def test_check_index_exists(tmp_path, monkeypatch):
    # Mock ROOT to use a temporary directory
    monkeypatch.setattr("chartix.api.ROOT", tmp_path)
    
    assert _check_index_exists() is False
    
    index_path = tmp_path / "search_index.parquet"
    index_path.touch()
    
    assert _check_index_exists() is True
