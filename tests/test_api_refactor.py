import pytest
import polars as pl
from chartix.api import build_search_index, show_chart, _get_index_path, _check_index_exists
import os

@pytest.fixture
def mock_index(tmp_path, monkeypatch):
    monkeypatch.setattr("chartix.api.ROOT", tmp_path)
    # Create a dummy datapackage.json and CSVs if needed, 
    # but maybe it's easier to just mock the index parquet file directly for some tests.
    pass

def test_show_chart_no_index(tmp_path, monkeypatch):
    monkeypatch.setattr("chartix.api.ROOT", tmp_path)
    # Ensure index does not exist
    if _check_index_exists():
         _get_index_path().unlink()
    
    df = show_chart("2023-01-01")
    assert isinstance(df, pl.DataFrame)
    assert df.is_empty()

def test_show_chart_invalid_date(tmp_path, monkeypatch):
    monkeypatch.setattr("chartix.api.ROOT", tmp_path)
    # Create dummy index
    index_path = _get_index_path()
    pl.DataFrame({"a": [1]}).write_parquet(index_path)
    
    df = show_chart("not-a-date")
    assert df.is_empty()
