# 🔒 Security Policy

## Supported Versions

| Version | Supported          | Security Status |
| ------- | ------------------ | --------------- |
| 0.2.x   | :white_check_mark: | Secure (eval() fixed) |
| 0.1.x   | :x:                | Vulnerable (eval()) |

**⚠️ CRITICAL: Version 0.1.x contains a Remote Code Execution vulnerability. Update to 0.2.x immediately!**

---

## Security Fixes

### Version 0.2.0 - Critical Security Fix

#### 🔴 CRITICAL: Remote Code Execution (RCE) - FIXED

**CVE:** N/A (preventive fix)
**Severity:** CRITICAL (CVSS 9.8)
**Status:** ✅ RESOLVED in v0.2.0

**Vulnerability:**
- `_evaluate_expression()` used `eval()` on user-controlled input
- Malicious Gerber files could execute arbitrary Python code
- Potential for system compromise

**Fix:**
- Replaced `eval()` with safe expression evaluator
- Implemented Shunting-yard algorithm for math expressions
- Whitelist validation for allowed characters
- No access to Python builtins

**Details:** See [SECURITY_FIX_EVAL.md](SECURITY_FIX_EVAL.md)

---

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email: [security contact - to be added]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Time

- **Critical:** 24 hours
- **High:** 48 hours
- **Medium:** 1 week
- **Low:** 2 weeks

---

## Security Best Practices

### For Users

#### 1. Always Use Latest Version
```bash
pip install --upgrade gerbyx
```

#### 2. Validate Input Files
```python
# Only process Gerber files from trusted sources
# Validate file format before processing
```

#### 3. Run in Sandboxed Environment
```bash
# Use Docker or virtual environment
docker run --rm -v $(pwd):/data gerbyx process file.gbr
```

#### 4. Limit File Size
```python
# Prevent DoS attacks
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
if os.path.getsize(file_path) > MAX_FILE_SIZE:
    raise ValueError("File too large")
```

### For Developers

#### 1. Never Use eval() or exec()
```python
# ❌ NEVER DO THIS
result = eval(user_input)

# ✅ DO THIS
result = safe_eval(user_input)
```

#### 2. Validate All Input
```python
# Whitelist approach
if not re.match(r'^[\d\.\+\-\*\/\(\)\s]+$', expr):
    raise ValueError("Invalid characters")
```

#### 3. Use Type Hints
```python
def process(data: str) -> float:
    # Type hints help catch errors early
    pass
```

#### 4. Run Security Tests
```bash
# Run security test suite
python test_safe_eval.py
```

---

## Known Security Considerations

### 1. File Parsing
**Risk:** Malformed Gerber files could cause crashes
**Mitigation:** Robust error handling, input validation
**Status:** ✅ Implemented

### 2. Memory Usage
**Risk:** Large files could cause memory exhaustion
**Mitigation:** Streaming processing, file size limits
**Status:** ⚠️ Partial (batch processing implemented)

### 3. Regular Expressions
**Risk:** ReDoS (Regular Expression Denial of Service)
**Mitigation:** Pre-compiled patterns, simple regex
**Status:** ✅ Implemented

### 4. Dependency Vulnerabilities
**Risk:** Vulnerable dependencies (Shapely, etc.)
**Mitigation:** Regular updates, security scanning
**Status:** ⚠️ Manual (automated scanning recommended)

---

## Security Checklist

### Code Review
- [x] No eval() or exec()
- [x] Input validation
- [x] Error handling
- [x] Type hints
- [x] Security tests

### Dependencies
- [ ] Automated vulnerability scanning (TODO)
- [ ] Regular updates
- [ ] Minimal dependencies

### Testing
- [x] Unit tests
- [x] Security tests
- [ ] Fuzzing (TODO)
- [ ] Penetration testing (TODO)

### Documentation
- [x] Security policy
- [x] Vulnerability disclosure
- [x] Best practices
- [x] Security fixes documented

---

## Security Tools

### Recommended Tools

#### 1. Bandit (Python Security Linter)
```bash
pip install bandit
bandit -r src/
```

#### 2. Safety (Dependency Scanner)
```bash
pip install safety
safety check
```

#### 3. Snyk (Vulnerability Scanner)
```bash
snyk test
```

#### 4. OWASP Dependency-Check
```bash
dependency-check --project gerbyx --scan .
```

---

## Threat Model

### Attack Vectors

#### 1. Malicious Gerber Files
**Threat:** Code injection via macro expressions
**Mitigation:** Safe expression evaluator
**Status:** ✅ MITIGATED

#### 2. Large Files (DoS)
**Threat:** Memory exhaustion, CPU overload
**Mitigation:** File size limits, batch processing
**Status:** ⚠️ PARTIAL

#### 3. Path Traversal
**Threat:** Access to files outside working directory
**Mitigation:** Path validation (if file I/O added)
**Status:** N/A (no file I/O currently)

#### 4. Dependency Vulnerabilities
**Threat:** Vulnerable third-party libraries
**Mitigation:** Regular updates, scanning
**Status:** ⚠️ MANUAL

---

## Security Roadmap

### Future Versions
- [ ] Automated dependency scanning
- [ ] Fuzzing test suite
- [ ] File size limits enforcement
- [ ] Sandboxing options
- [ ] Formal security audit
- [ ] Penetration testing
- [ ] Security certifications
- [ ] Bug bounty program

---

## Acknowledgments

### Tools Used
- Bandit - Python security linter
- Safety - Dependency scanner
- GitHub Security Advisories

---

## License

This security policy is part of the gerbyx project and is licensed under the MIT License.

---

**Last Updated:** 2026-03-07
**Version:** 0.2.0
**Status:** ✅ SECURE
