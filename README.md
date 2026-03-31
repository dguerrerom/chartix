# chartix

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A toolkit for querying and managing international music charts data (1980–1999). Provides a CLI and a Python API for searching charts, finding anniversary hits, and building Frictionless Data Packages.

## Features

- **CLI** – Easily search for songs, see anniversary #1 hits, view charts for a specific date, and more.
- **Fuzzy search** – Find songs even with slight misspellings using Damerau‑Levenshtein distance.
- **Flexible data structure** – Data is stored as annual CSV files with metadata in `*-metadata.json` files, following the Frictionless Data specification.
- **Build search index** – Aggregates all CSV data into a fast Parquet index for efficient queries.

## Installation

### Requirements
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

### Using uv (recommended)
```bash
git clone https://github.com/dguerrerom/chartix.git
cd chartix
uv venv
uv pip install -e .
```

### Using pip
```bash
pip install -e .
```

## First Steps

After installation, you must prepare the data and the search index:

```bash
# Generate Frictionless Data Packages from metadata
chartix generate

# Build the search index (required for queries)
chartix build-index
```

These commands need to be run only once (or whenever you add/change data).

## Quick Start

Once the index is ready, you can run queries:

```bash
# List all available charts
chartix list

# Show the Billboard Hot 100 chart for June 1, 1985
chartix show --date 1985-06-01 --chart billboard-hot100

# Find all songs by Madonna and show their best rank
chartix search --artist "Madonna" --best

# Find #1 hits for this week in history (anniversary)
chartix anniversary

# Show all songs that reached top 10 in 1988
chartix peak --year 1988 --rank 10
```

For more details, run `chartix --help`.

## Data Structure

The data is stored in the `data/` folder. See the [data README](data/README.md) for a detailed description of the folder layout, metadata files, and how to add or update data.

## Development

If you want to contribute or run the tests:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Lint and format
ruff check .
ruff format .

# Type check
mypy src
```

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Data is compiled from publicly available sources. For specific chart sources, please refer to the metadata files in the `data/` folder.