# Packaging and Installable Distribution

This project is packaged with **PEP 621 metadata** in `pyproject.toml` and can be built as a standard Python distribution.

## What defines the package

The installable package is described in `pyproject.toml`:

- `[project]`
  - `name = "gerbyx"`
  - `version = "0.3.0"`
  - `dependencies = [...]`
  - `requires-python = ">= 3.10"`
- `[project.scripts]`
  - `gerbyx = "gerbyx.cli:app"`

The actual Python package code lives under `src/gerbyx/`.
This is the **src layout**, which helps avoid accidentally importing local files instead of the installed package.

## What gets installed

When the package is built and installed:

- Python modules under `src/gerbyx/` become the importable package `gerbyx`
- the CLI entry point `gerbyx` is generated from `gerbyx.cli:app`
- runtime dependencies (`typer`, `Shapely`, `rich`) are installed
- optional plotting extra (`matplotlib`) is available via `pip install .[plot]`

## Build flow

### 1. Source tree
You work on the sources in:

- `src/gerbyx/`
- `pyproject.toml`
- optional docs/tests/scripts

### 2. Build backend resolution
A build frontend such as `python -m build`, `pip`, or `uv build` reads `pyproject.toml` and selects the configured/default build backend.

In practice this produces two common artifacts:

- **sdist** (`.tar.gz`) — source distribution
- **wheel** (`.whl`) — built/installable binary distribution for Python packages

### 3. Artifact generation
The build step creates a `dist/` directory with files like:

- `gerbyx-0.3.0.tar.gz`
- `gerbyx-0.3.0-py3-none-any.whl`

### 4. Installation
Installing the wheel or sdist makes `gerbyx` importable and exposes the `gerbyx` CLI command.

## Typical commands

### Build locally
```powershell
cd C:\TheAntFarmRepo\gerbyx
$env:PYTHONPATH = "src"
.\env\Scripts\python.exe -m pip install build
.\env\Scripts\python.exe -m build
```

### Install locally in editable mode
Useful during development because code changes are reflected without rebuilding:

```powershell
cd C:\TheAntFarmRepo\gerbyx
.\env\Scripts\python.exe -m pip install -e .
```

### Install built wheel
```powershell
cd C:\TheAntFarmRepo\gerbyx
.\env\Scripts\python.exe -m pip install .\dist\gerbyx-0.3.0-py3-none-any.whl
```

## Versioning workflow

When preparing a release:

1. Update `version` in `pyproject.toml`
2. Optionally update `HISTORY.md`
3. Run tests
4. Build distributions
5. Validate install from wheel
6. Publish to PyPI if desired

## Recommended release verification

Before publishing, verify all of these:

1. Clean test run
2. CLI runs from installed wheel
3. `import gerbyx` works in a clean environment
4. package metadata/version are correct
5. generated wheel contains the expected modules

## Practical difference: editable install vs wheel install

### Editable install (`pip install -e .`)
- best for development
- code is loaded from your working tree
- no rebuild needed after source edits

### Wheel install (`pip install dist/...whl`)
- best for release verification and real users
- installs a built artifact
- exactly what downstream users receive

## How the CLI executable is created

This line in `pyproject.toml`:

```toml
[project.scripts]
gerbyx = "gerbyx.cli:app"
```

tells the installer to create a command named `gerbyx` that invokes the Typer application exposed in `gerbyx.cli`.

So after installation, users can run:

```powershell
gerbyx --help
gerbyx some_file.gbr
gerbyx some_file.drl --format excellon
```

## Recommended release sequence for this repository

```powershell
cd C:\TheAntFarmRepo\gerbyx
.\env\Scripts\python.exe -m pytest tests\ -q
.\env\Scripts\python.exe -m pip install build
.\env\Scripts\python.exe -m build
.\env\Scripts\python.exe -m pip install --force-reinstall .\dist\gerbyx-0.3.0-py3-none-any.whl
gerbyx --help
```

## Notes for this repository

- tests are configured through `pyproject.toml`
- `src` layout is already in place
- the CLI is already distributable via `[project.scripts]`
- the new Excellon support is part of the same package: no separate distribution is needed

