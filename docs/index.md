# Welcome to Chartix

Chartix is a powerful toolkit for querying and managing international music charts data, specifically focused on the golden era of 1980–1999. Whether you're a data scientist, a music enthusiast, or a developer, Chartix provides the tools you need to explore historical music trends with ease.

## Quick Start

Get up and running in seconds:

1.  **Install Chartix**:
    ```bash
    git clone https://github.com/dguerrerom/chartix.git
    cd chartix
    uv sync
    ```

2.  **Prepare Data**:
    ```bash
    uv run chartix generate
    uv run chartix build-index
    ```

3.  **Run your first query**:
    ```bash
    # See what was hot on a specific date
    uv run chartix show --date 1985-06-13 --chart billboard-hot100
    
    # Search for your favorite artist
    uv run chartix search --artist "Madonna"
    ```

## Main Features

-   **🚀 Fuzzy Search**: Don't remember the exact spelling? Our fuzzy search finds songs and artists even with typos.
-   **📅 Anniversary Hits**: Discover which songs were topping the charts on this day 30 or 40 years ago.
-   **📊 Frictionless Data**: Data is stored in standardized CSV files with rich metadata, making it easy to use with other data analysis tools.
-   **🛠️ Robust CLI & API**: Use the command-line interface for quick lookups or integrate the Python API into your own projects.
-   **🌍 International Charts**: Support for Billboard Hot 100, Club, and Latin charts, with more to come.
