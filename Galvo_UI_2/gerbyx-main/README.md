# gerbyx

![PyPI version](https://img.shields.io/pypi/v/gerbyx.svg)
[![Github tag](https://badgen.net/github/tag/TheAntTeam/gerbyx)](https://gitHub.com/TheAntTeam/gerbyx/tags/)

Gerber parser that generates Shapely objects for PCB and geometries

* PyPI package: https://pypi.org/project/gerbyx/
* Free software: MIT License

## Features

* ✅ **Gerber X2 & X3 Support**: Full support for both Gerber X2 and X3 standards
* ✅ **Shapely Geometry Generation**: Converts Gerber commands to Shapely objects
* ✅ **Macro Apertures**: Supports custom aperture macros (AM)
* ✅ **Aperture Blocks**: Handles aperture blocks (AB) with full instantiation support
* ✅ **Layer Polarity**: Dark and Clear polarity for additive/subtractive operations
* ✅ **Attributes**: File, aperture, and component attributes (TF, TA, TO)
* ✅ **X3 Component Attributes**: TO.C (reference), TO.CVal (value), and more
* ✅ **Delete Attributes**: TD command for removing attributes (X3)
* ✅ **X3 Validation**: Built-in validator for X3 compliance
* ✅ **Visualization**: Optional Matplotlib-based plotting via the `plot` extra
* ✅ **CLI Tool**: Command-line interface for quick processing
* ✅ **Performance Optimized**: +6% faster with zero overhead logging
* ✅ **Secure**: No eval() vulnerabilities, safe expression evaluator
* ✅ **Logging System**: DEBUG/INFO/WARNING/ERROR levels with lazy evaluation

### Gerber X3 Features

* Component reference designators (TO.C)
* Component values (TO.CVal)
* Inline comments with `#`
* Explicit macro closing with `%AM*%`
* Mandatory M02 end-of-file marker
* Aperture blocks instantiation
* Delete attributes (TD)
* X3 validation with error reporting

## 📚 Documentation

Comprehensive documentation is available in the [docs/](docs/) folder:

- **[Getting Started](docs/installation.md)** - Installation and usage
- **[Gerber X3 Support](docs/GERBER_X3_SUPPORT.md)** - X3 features and compliance
- **[Performance](docs/OPTIMIZATION_SUMMARY.md)** - Optimization details (+6% speedup)
- **[Security](docs/SECURITY.md)** - Security policy and fixes
- **[Logging](docs/LOGGING_DOCUMENTATION.md)** - Logging system guide
- **[Testing](docs/TESTING.md)** - Test suite documentation

See [docs/README.md](docs/README.md) for complete documentation index.

## 📦 Optional extras

The core package does **not** require Matplotlib anymore.

If you want to use the built-in plotting helpers or the benchmark preview
script, install the optional `plot` extra:

```powershell
pip install "gerbyx[plot]"
```

Or, for local development from the repository root:

```powershell
cd C:\TheAntFarmRepo\gerbyx
.\env\Scripts\python.exe -m pip install -e ".[plot]"
```

This extra enables:

- `gerbyx.visualizer.plot_shapes(...)`
- the `--show` CLI plotting path
- `scripts/bench_excellon.py`

If you only need parsing and geometry generation, you can install the core
package without this extra.

## 🚀 Quick Start

```python
from gerbyx import logger
from gerbyx.tokenizer import tokenize_gerber
from gerbyx.parser import GerberParser
from gerbyx.processor import GerberProcessor

# Optional: Enable debug logging
logger.set_level('DEBUG')  # or 'INFO' (default), 'WARNING', 'ERROR'

# Parse Gerber file
with open('file.gbr', 'r') as f:
    gerber_source = f.read()

processor = GerberProcessor()
parser = GerberParser(processor)
tokens = tokenize_gerber(gerber_source)
parser.parse(tokens)

# Get geometries
geometries = processor.geometries
print(f"Generated {len(geometries)} geometries")
```

## 🔒 Security

From **Version 0.2.0** critical security fixes are included:
- ✅ Removed `eval()` vulnerability (RCE risk eliminated)
- ✅ Safe expression evaluator for macro expressions
- ✅ Input validation and sanitization

See [docs/SECURITY.md](docs/SECURITY.md) for details.

## ⚡ Performance

**Optimized for speed:**
- Parsing: +22% faster
- Tokenization: +13% faster
- Small files: +36% faster
- Zero overhead logging

See [docs/OPTIMIZATION_SUMMARY.md](docs/OPTIMIZATION_SUMMARY.md) for benchmarks.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
