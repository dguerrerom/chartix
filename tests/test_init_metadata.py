import chartix

def test_package_metadata():
    """Check that package metadata is present."""
    assert chartix.__doc__ is not None
    assert "Chartix" in chartix.__doc__
    assert chartix.__version__ == "0.1.0"

def test_public_api_exports():
    """Check that key functions are exported in __init__."""
    expected_exports = [
        "DEFAULT_ANNIVERSARY_RANK",
        "DEFAULT_PEAK_RANK",
        "anniversary_hits",
        "best_rank_in_year",
        "build_search_index",
        "generate_frictionless_packages",
        "list_charts",
        "ones_calendar",
        "search_hits",
        "show_chart",
    ]
    for export in expected_exports:
        assert hasattr(chartix, export), f"Missing export: {export}"
