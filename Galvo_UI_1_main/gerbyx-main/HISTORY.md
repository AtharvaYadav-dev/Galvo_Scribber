# History

## 0.2.3 (2026-03-23)

### Bug Fixes
* Robust handling of G04 comments and inline comments in tokenizer
* Gerber X3 attribute handling and negative macro parameters

## 0.2.0 (2026-03-07)

### New Features
* **Gerber X3 Support**:
  * Component reference designators (TO.C)
  * Component values (TO.CVal)
  * Inline comments with `#`
  * Explicit macro closing with `%AM*%`
  * Mandatory M02 end-of-file marker
  * Aperture blocks (AB) with full instantiation support
  * Delete attributes (TD) command
  * X3 validation with strict mode option
* **Gerber X2 Support**:
  * File attributes (TF)
  * Aperture attributes (TA)
  * Layer attributes (TO)
  * Macro apertures (AM)
  * Layer polarity (dark/clear)
* **Core Features**:
  * Shapely geometry generation
  * Built-in Matplotlib visualization
  * CLI tool for quick processing

### Performance Improvements
* **+38% speedup** on medium/large files
* **Optimizations**:
  * Pre-compiled regex patterns (90% reduction in re._compile calls)
  * Lazy geometries cache with on-demand calculation
  * Aperture shape cache for geometry reuse
  * Command lookup tables with O(1) set operations
  * Fast command dispatch with single slice `[:2]`
  * Batch union processing for large shape lists (>500 shapes)
* **Parsing**: +22% faster
* **Tokenization**: +13% faster
* **Small files**: +36% faster

### Security Fixes
* **CRITICAL: Remote Code Execution (RCE) - FIXED**
  * Removed `eval()` vulnerability in `_evaluate_expression()`
  * Implemented safe expression evaluator using Shunting-yard algorithm
  * Added whitelist validation for allowed characters
  * No access to Python builtins
  * Zero code execution risk

### Logging System
* Zero overhead logging with lazy evaluation
* Multiple levels: DEBUG, INFO, WARNING, ERROR
* Context managers for automatic timing
* Performance optimized with `is_debug_enabled()` checks
* No performance impact when debug disabled

### Documentation
* Added GERBER_X3_SUPPORT.md
* Added X3_NEW_FEATURES.md
* Added TESTING.md with 63 passing tests
* Added SECURITY.md with security policy
* Added SECURITY_FIX_EVAL.md with detailed fix documentation
* Added LOGGING_DOCUMENTATION.md
* Added comprehensive optimization documentation
* Performance analysis and benchmarks
* Complete documentation in docs/ folder

## 0.1.0 (2025-12-07)

* First release on PyPI
* Basic Gerber parsing functionality
* Shapely object generation
