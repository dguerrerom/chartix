# Chartix

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Chartix is a toolkit for querying and managing international music charts. It provides a CLI and a Python API for searching charts, finding anniversary hits, and building Frictionless Data Packages.

## Features

- **CLI** – Easily search for songs, see anniversary #1 hits, view charts for a specific date, and more.
- **Search Filtering** – Filter search results by chart provider or specific chart names using `--provider` and `--chart`.
- **Fuzzy Search** – Find songs even with slight misspellings using Damerau‑Levenshtein distance.
- **Flexible Data Structure** – Data is stored as annual CSV files with metadata in `*-metadata.json` files, following the Frictionless Data specification.
- **Fast Indexing** – Aggregates all CSV data into a fast Parquet index for efficient queries.

## Installation

### Requirements
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (recommended)

### Using uv (recommended)
```bash
git clone https://github.com/dguerrerom/chartix.git
cd chartix
uv sync
```

### Using pip
```bash
pip install -e .
```

## Quick Start

After installation, prepare the data and the search index:

```bash
# Generate Frictionless Data Packages from metadata
uv run chartix generate

# Build the search index (required for queries)
uv run chartix build-index
```

Once the index is ready, you can run queries:

```bash
# List all available charts
uv run chartix list

# Show the Billboard Hot 100 chart for June 1, 1985
uv run chartix show --date 1985-06-01 --chart billboard-hot100

# Find all songs by Madonna and show their best rank
uv run chartix search --artist "Madonna" --best

# Filter search by provider
uv run chartix search --artist "Madonna" --provider billboard

# Find #1 hits for this week in history (anniversary)
uv run chartix anniversary

# Show all songs that reached top 10 in 1988
uv run chartix peak --year 1988 --rank 10
```

For more details, run `uv run chartix --help`.

## Data Structure

The data is stored in the `data/` folder. See the [data README](data/README.md) for a detailed description of the folder layout, metadata files, and how to add or update data.

## Development

If you want to contribute or run the tests:

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy src
```

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Data is compiled from publicly available sources. For specific chart sources, please refer to the metadata files in the `data/` folder.