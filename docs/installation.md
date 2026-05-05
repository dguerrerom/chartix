# Installation & Setup

This guide will help you get Chartix up and running on your local machine.

## Prerequisites

-   **Python**: 3.13 or higher.
-   **uv**: We recommend using [uv](https://github.com/astral-sh/uv) for fast, reliable Python package and environment management.

## For Users

If you just want to use the Chartix CLI:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/dguerrerom/chartix.git
    cd chartix
    ```

2.  **Install dependencies and create environment**:
    ```bash
    uv sync
    ```

3.  **Run the CLI**:
    You can now use `uv run chartix` to execute commands.

## For Contributors

If you want to contribute to Chartix development:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/dguerrerom/chartix.git
    cd chartix
    ```

2.  **Install all dependencies (including dev tools)**:
    ```bash
    uv sync --all-extras
    ```

This will install `pytest`, `mypy`, `ruff`, and `mkdocs` alongside the core dependencies.

## Data Preparation

Before you can query any charts, you need to prepare the local data and search index.

1.  **Generate Data**:
    This command populates the `data/` directory with sample or external chart data (depending on configuration).
    ```bash
    uv run chartix generate
    ```

2.  **Build Search Index**:
    To enable fast fuzzy searching, you must build the search index:
    ```bash
    uv run chartix build-index
    ```

Once these steps are complete, you're ready to start exploring! Check out the [Quick Start](index.md#quick-start) for example commands.
