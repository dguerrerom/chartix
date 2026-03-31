# Billboard Charts Data (1980–1999)

This folder contains the raw chart data for **Billboard** music charts in CSV format, covering the period **1980–1999**. The dataset is part of the `chartix` project and follows the [Frictionless Data](https://frictionlessdata.io/) specification for metadata.

## Overview

The dataset includes the following Billboard charts for the years 1980–1999:

| Provider prefix | Provider name | Country | Chart prefix | Chart name | Frequency |
|-----------------|---------------|---------|--------------|------------|-----------|
| billboard | Billboard | United States | billboard-hot100 | Billboard Hot 100 | weekly |
| billboard | Billboard | United States | billboard-latin | Billboard Hot Latin Songs | weekly |
| billboard | Billboard | United States | billboard-club | Billboard Dance Club Songs | weekly |

While some charts may have data outside the 1980–1999 range in their original sources, this repository only contains data for the 1980–1999 period.

## Folder Structure

Inside the `billboard/` folder you will find:

- A `billboard-metadata.json` file that serves as the **source of truth** for Billboard’s charts.
- A subfolder for **each chart**, named after the chart’s internal `prefix` (e.g., `billboard-hot100/`).

Within each chart folder, the data is split into **annual CSV files**, named `YYYY.csv` (e.g., `1985.csv`). Each annual file contains all entries for that chart during that year (weekly in this case).

Example structure (only years 1980–1999 shown):

```
data/
├── billboard/
│   ├── billboard-metadata.json
│   ├── billboard-hot100/
│   │   ├── 1980.csv
│   │   ├── 1981.csv
│   │   └── ...
│   │   └── 1999.csv
│   ├── billboard-latin/
│   │   ├── 1986.csv   (starting year for Latin chart)
│   │   ├── 1987.csv
│   │   └── ...
│   │   └── 1999.csv
│   └── billboard-club/
│       ├── 1980.csv
│       ├── 1981.csv
│       └── ...
│       └── 1999.csv
```

## Metadata File (`billboard-metadata.json`)

The `billboard-metadata.json` file defines the Billboard charts. It contains:

- **Provider‑level information** – `name`, `prefix`, `country`, `url` (if available).
- **Per‑chart information** under the `charts` key:
  - `prefix` – internal identifier (matches the chart folder name, e.g., `billboard-hot100`)
  - `name` – human‑readable chart title
  - `folder` – name of the folder where the CSV files are stored (usually the same as `prefix`)
  - `fields` – list of column names in the CSV
  - `frequency` – `weekly`, `monthly`, or `fortnightly`
  - `start_date` / `end_date` – ISO 8601 dates; for this repository, the data is limited to 1980–1999, even if the metadata shows longer ranges.

This metadata file is the **only file you should edit manually** if you need to adjust chart definitions (e.g., correct a column name, update date ranges). Do **not** edit the generated `datapackage.json` files directly.

## CSV Files

- **Naming:** Annual files are named `YYYY.csv` (e.g., `1985.csv`). All data for a given year is stored in the corresponding file.
- **Content:** Each row represents a chart entry for a specific date. Columns vary per chart but typically include:
  - `date` – YYYY-MM-DD
  - `this_week` – chart position (integer)
  - `artist` – artist name
  - `song` – song title
  - (optional) `last_week`, `peak_position`, `weeks_on_chart`, etc.

## Generated Files

### `datapackage.json` (provider‑level)
After editing `billboard-metadata.json`, run the `chartix generate` command. This will:

- Create a `datapackage.json` inside the `billboard/` folder.
- Update the root `data/datapackage.json` master catalog.

The provider‑level `datapackage.json` follows the [Frictionless Data Package](https://frictionlessdata.io/) specification and includes a full table schema for each CSV file.

### `search_index.parquet`
The command `chartix build-index` aggregates all CSV data into a single Parquet file. This index is used by the `search`, `anniversary`, `peak`, and `show` commands for fast, fuzzy‑matched queries. Whenever the CSV data changes, you should rebuild the index.

## Using the Data

- **Via the CLI** – Install the `chartix` package and run commands like:
  ```bash
  chartix show --date 1985-06-01 --chart billboard-hot100
  chartix search --artist "Madonna" --best
  ```

- **Programmatically** – Use the `chartix.api` module:
  ```python
  from chartix.api import search_hits
  df = search_hits(artist="Madonna", best_position=True)
  ```

- **Direct CSV access** – The raw CSV files are plain text and can be opened with any spreadsheet software or data analysis tool.

## Licensing and Attribution

The data is compiled from publicly available sources. Please refer to the original Billboard sources for attribution requirements.

## Maintenance Notes

- **Adding new data**:  
  1. Create a new chart folder (named after the chart’s prefix) inside `billboard/`.  
  2. Place the annual CSV files (named `YYYY.csv`) inside that folder.  
  3. Update `billboard-metadata.json` to include the new chart.  
  4. Run `chartix generate` to update the `datapackage.json` files.  
  5. Run `chartix build-index` to rebuild the search index.

- **Updating existing data**:  
  1. Replace or modify the relevant `YYYY.csv` files in the chart folder.  
  2. Rebuild the search index with `chartix build-index`.

- **Never edit `datapackage.json` directly** – always edit `billboard-metadata.json` and regenerate.

---

*This README is part of the `chartix` project. For more information, see the main project documentation.*