# CLI Reference

The `chartix` command-line interface allows you to query the music charts dataset, manage the search index, and generate data packages.

## Global Options

- `--help`: Show the help message and exit.

---

## `list`

List all available charts across all providers.

### Description
Displays a list of all charts currently supported by the dataset, including their provider, name, frequency, and date range.

### Usage
```bash
chartix list
```

### Options
- `--help`: Show this message and exit.

### Example
```bash
chartix list
```

---

## `search`

Search for an artist and/or song in the charts.

### Description
Performs a fuzzy search (Damerau-Levenshtein distance) for artists and songs across the dataset. You can filter by specific dates, years, providers, or charts.

### Usage
```bash
chartix search [OPTIONS]
```

### Options
- `--artist TEXT`: Artist name (fuzzy matched).
- `--song TEXT`: Song title (fuzzy matched).
- `--date TEXT`: Specific date (`YYYY-MM-DD`).
- `--year INTEGER`: Specific year (ignored if `--date` is provided).
- `--provider TEXT`: Filter by provider name (e.g., `billboard`).
- `--chart TEXT`: Filter by chart name (e.g., `billboard-hot100`).
- `--best`: Return only the best rank for each song (ignored when `--date` is provided).
- `--help`: Show this message and exit.

### Examples
```bash
# Search for Madonna's best positions in all charts
chartix search --artist "Madonna" --best

# Search for a specific song in 1985
chartix search --song "Like a Virgin" --year 1985

# Search for matches in a specific chart
chartix search --artist "Prince" --chart billboard-hot100
```

---

## `anniversary`

Find hits for the current week (or a reference date) in history.

### Description
Identifies songs that were at a specific rank during the same week in previous years. It automatically handles weekly, fortnightly, and monthly chart frequencies.

### Usage
```bash
chartix anniversary [OPTIONS]
```

### Options
- `--date TEXT`: Reference date (`YYYY-MM-DD`). Defaults to today.
- `--rank INTEGER`: Chart position to retrieve. Defaults to 1.
- `--provider TEXT`: Filter by provider name.
- `--chart TEXT`: Filter by chart name.
- `--help`: Show this message and exit.

### Example
```bash
# Find all #1 hits for this week in history
chartix anniversary --rank 1

# Find #5 hits for a specific historical date
chartix anniversary --date 1990-07-13 --rank 5
```

---

## `peak`

Find the best rank for each song in a given year.

### Description
Summarizes the peak positions achieved by songs within a specific calendar year.

### Usage
```bash
chartix peak --year YEAR [OPTIONS]
```

### Options
- `--year INTEGER`: Year to search (e.g., 1985). **[required]**
- `--rank INTEGER`: Target rank threshold. Only songs that reached this rank or better are shown. Defaults to 10.
- `--provider TEXT`: Filter by provider name.
- `--chart TEXT`: Filter by chart name.
- `--help`: Show this message and exit.

### Example
```bash
# Find all songs that reached the Top 10 in 1988
chartix peak --year 1988 --rank 10

# Find Top 5 hits in the Billboard Hot 100 for 1984
chartix peak --year 1984 --rank 5 --chart billboard-hot100
```

---

## `show`

Show chart(s) for a specific date.

### Description
Displays the full chart listing for all providers (or a specific one) on a given date.

### Usage
```bash
chartix show --date DATE [OPTIONS]
```

### Options
- `--date TEXT`: Date in `YYYY-MM-DD` format. **[required]**
- `--provider TEXT`: Filter by provider name.
- `--chart TEXT`: Filter by chart name.
- `--help`: Show this message and exit.

### Example
```bash
# Show all charts for January 1st, 1980
chartix show --date 1980-01-01

# Show only the Billboard Hot 100 for a specific date
chartix show --date 1985-07-13 --chart billboard-hot100
```

---

## `calendar`

Generate a calendar of #1 hits aligned with weeks of a target year.

### Description
Creates a CSV file where #1 hits from the past are mapped to the weeks of a target year (usually the current year). Only the first time a song reaches #1 on a specific chart is included.

### Usage
```bash
chartix calendar [OPTIONS]
```

### Options
- `--provider TEXT`: Filter by provider name.
- `--chart TEXT`: Filter by chart name.
- `--year INTEGER`: Target year for the calendar. Defaults to the current year.
- `--output TEXT`: Output CSV file path. Defaults to `{year}_calendar.csv`.
- `--help`: Show this message and exit.

### Example
```bash
# Generate a calendar for 2025 based on Billboard Hot 100 hits
chartix calendar --chart billboard-hot100 --year 2025 --output billboard_2025.csv
```

---

## `build-index`

Build the search index from CSV files.

### Description
Aggregates all CSV data files, normalizes text fields for fuzzy matching, and creates a `search_index.parquet` file in the `data/` directory. This index is required for all query commands.

### Usage
```bash
chartix build-index
```

### Options
- `--help`: Show this message and exit.

---

## `generate`

Generate Frictionless Data Packages from metadata.

### Description
Creates or updates `datapackage.json` files for each provider and a master `datapackage.json` catalog in the root `data/` directory based on `*-metadata.json` files.

### Usage
```bash
chartix generate
```

### Options
- `--help`: Show this message and exit.
