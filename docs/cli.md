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
chartix show --date YYYY-MM-DD --chart <chart-prefix>
```

Example:

```bash
chartix show --date 1985-06-01 --chart billboard-hot100
```

## `search`

Search for an artist and/or song.

```bash
chartix search --artist "Madonna" --best
```

Options:
- `--artist` – artist name (fuzzy matched)
- `--song` – song title (fuzzy matched)
- `--date` – exact date (YYYY-MM-DD)
- `--year` – exact year
- `--best` – return only the best rank per song

## `anniversary`

Find #rank hits for this week in history.

```bash
chartix anniversary --rank 1
```

Options:
- `--date` – reference date (default today)
- `--rank` – chart position (default 1)

## `peak`

Find best rank for each song in a given year.

```bash
chartix peak --year 1988 --rank 10
```

## `generate`

Generate Frictionless Data Packages from metadata.

```bash
chartix generate
```

## `build-index`

Build the search index from CSV files.

```bash
chartix build-index
```