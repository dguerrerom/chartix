# CLI Reference

The `chartix` command provides several subcommands:

## `list`

List all available charts.

```bash
chartix list
```

## `show`

Show the chart for a specific date.

```bash
chartix show --date YYYY-MM-DD [--provider PROVIDER] [--chart CHART]
```

**Options:**
- `--date` (required) – Date in `YYYY-MM-DD` format.
- `--provider` – Filter by provider name (e.g., `billboard`).
- `--chart` – Filter by chart name (e.g., `billboard-hot100`).

**Example:**
```bash
chartix show --date 1985-06-01 --chart billboard-hot100
```

## `search`

Search for an artist and/or song in the charts.

```bash
chartix search [--artist ARTIST] [--song SONG] [--date DATE] [--year YEAR] [--best]
```

**Options:**
- `--artist` – Artist name (fuzzy matched).
- `--song` – Song title (fuzzy matched).
- `--date` – Exact date (`YYYY-MM-DD`).
- `--year` – Exact year (ignored if `--date` given).
- `--best` – Return only the best rank for each song (ignored with `--date`).

At least one of `--artist` or `--song` is required. `--date` and `--year` are mutually exclusive.

**Example:**
```bash
chartix search --artist "Madonna" --best
```

## `anniversary`

Find #rank hits for the current week in previous years.

```bash
chartix anniversary [--date DATE] [--rank RANK]
```

**Options:**
- `--date` – Reference date (`YYYY-MM-DD`). Defaults to today.
- `--rank` – Chart position to retrieve. Defaults to 1.

**Example:**
```bash
chartix anniversary --rank 1
```

## `peak`

Find best rank for each song in a given year.

```bash
chartix peak --year YEAR [--rank RANK]
```

**Options:**
- `--year` (required) – Year to search (e.g., 1985).
- `--rank` – Target rank (default 10). Only songs that reached ≤ this rank are shown.

**Example:**
```bash
chartix peak --year 1988 --rank 10
```

## `calendar`

Generate a calendar of #1 hits aligned with weeks of the current year.

```bash
chartix calendar [--provider PROVIDER] [--chart CHART] [--year YEAR] [--output OUTPUT]
```

**Options:**
- `--provider` – Filter by provider name.
- `--chart` – Filter by chart name.
- `--year` – Target year (default current year).
- `--output` – Output CSV file path (defaults to `{year}_calendar.csv`).

The resulting CSV contains columns:
- `week` – ISO week number in the target year.
- `date` – Original chart date of the #1 hit.
- `event` – Formatted string: `"{song} by {artist} reaches #1 on the {chart}"`.

**Examples:**
```bash
chartix calendar --year 2025 --output 2025_calendar.csv
chartix calendar --chart billboard-hot100 --output hot100_calendar.csv
```

## `generate`

Generate Frictionless Data Packages from metadata. This command creates provider‑level `datapackage.json` files and the root `datapackage.json` catalog.

```bash
chartix generate
```

**Note:** This command should be run after modifying any `*-metadata.json` file.

## `build-index`

Build the search index from CSV files. The index is stored as `search_index.parquet` in the `data/` folder and is required for all query commands.

```bash
chartix build-index
```

**Note:** Run this after adding or modifying CSV data, or after running `generate`.