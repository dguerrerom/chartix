"""
Chartix: A library for querying and managing international music charts data.

This package provides tools for handling music chart data from various providers,
including Frictionless Data Package generation, search index building, and
advanced query capabilities like fuzzy search and anniversary hits.
"""

__version__ = "0.1.0"

from chartix.api import (
    DEFAULT_ANNIVERSARY_RANK,
    DEFAULT_PEAK_RANK,
    anniversary_hits,
    best_rank_in_year,
    build_search_index,
    generate_frictionless_packages,
    list_charts,
    ones_calendar,
    search_hits,
    show_chart,
)

__all__ = [
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
