# Installation

## Using uv (recommended)

```bash
git clone https://github.com/dguerrerom/chartix.git
cd chartix
uv venv
uv pip install -e .
```

## Using pip

```bash
pip install -e .
```

## Development Installation

To also install development tools (pytest, mypy, ruff, mkdocs):

```bash
uv pip install -e ".[dev]"
```