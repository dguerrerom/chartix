# API Reference

The `chartix` library provides a high-level Python API to interact with the music charts dataset. Most common operations are available directly from the top-level `chartix` package.

## Getting Started

To use the API, you typically want to import the query functions. The library uses [Polars](https://pola.rs/) for efficient data handling and returns results as Polars DataFrames.

### Basic Usage Example

```python
from chartix import search_hits

# Search for Madonna's best positions in all charts
df = search_hits(artist="Madonna", best_position=True)

# Print the results
print(df)
```

## Public API Entry Points

The following functions are the primary entry points for querying and managing the dataset:

- `search_hits`: Fuzzy search for artists and songs.
- `anniversary_hits`: Find historical hits for the current week.
- `best_rank_in_year`: Summarize peak positions for a given year.
- `show_chart`: Retrieve the full chart for a specific date.
- `list_charts`: List all available charts and their metadata.
- `ones_calendar`: Generate a calendar of #1 hits.
- `build_search_index`: (Re)build the search index from raw CSV files.
- `generate_frictionless_packages`: Generate Frictionless Data Packages from metadata.

---

## Full API Reference

The following is the full documentation for the `chartix.api` module, generated from docstrings.

::: chartix.api
