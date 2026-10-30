# 🔍 Gerbyx Performance Analysis

## 📊 Profiling Results

### Small File (0.6 KB - gerber_x3_correct.gbr)
- **Total:** 12.94 ms
- Tokenization: 0.36 ms (3%)
- Parsing: 9.95 ms (77%)
- Geometries: 2.63 ms (20%)

### Medium File (272 KB - copper_top.gbr)
- **Total:** 3,403 ms (3.4 seconds)
- Tokenization: 166 ms (5%)
- Parsing: 1,794 ms (53%)
- Geometries: 1,443 ms (42%)

---

## 🎯 Bottlenecks Identified

### 1. **Shapely Operations** (CRITICAL - 54% of time)
**Problem:** `unary_union` and `difference` are extremely slow
- `unary_union`: 831 ms (24%)
- `difference`: 516 ms (15%)
- `buffer`: 201 ms (6%)

**Impact:** Medium file 272KB → 1.5s just for Shapely operations

**Solutions:**
- ✅ **Cache repeated geometries** - Many apertures are used multiple times
- ✅ **Lazy evaluation** - Don't calculate `geometries` until requested
- ✅ **Batch operations** - Union geometries in batches instead of one by one
- ⚠️ **Alternatives to Shapely** - Consider faster libraries (e.g., pygeos)

---

### 2. **Regex Compilation** (MEDIUM - 10% of time)
**Problem:** Regexes are recompiled on every call
- 90,431 calls to `re._compile`
- 75,306 calls to `re.search`

**Impact:** ~326 ms on medium file

**Solutions:**
- ✅ **Pre-compile regex** - Compile once at the module level
- ✅ **Cache patterns** - Use `re.compile()` and reuse

---

### 3. **Coordinate Parsing** (MEDIUM - 15% of time)
**Problem:** `_handle_coordinates_and_dcode` called 15,061 times
- Each call makes 4 regex searches (X, Y, I, J, D)
- 60,244 calls to `get_val`

**Impact:** ~532 ms on medium file

**Solutions:**
- ✅ **Single regex** - A single pattern to capture all values
- ✅ **Parse once** - Cache results for identical statements

---

### 4. **Parser Overhead** (LOW - 5% of time)
**Problem:** stmt→param conversion and repeated checks
- 15,061 iterations with `any()` and `startswith()` checks

**Impact:** ~189 ms on medium file

**Solutions:**
- ✅ **Lookup table** - Use a dict instead of `any(startswith())`
- ✅ **Early exit** - Optimize for the most common conditions

---

## 🚀 Optimization Plan

### Phase 1: Quick Wins (High Impact, Low Effort)
**Estimated time:** 1-2 hours
**Expected speedup:** 20-30%

1. ✅ **Pre-compile regex** in the parser
   - Compile X, Y, I, J, D patterns once
   - Remove 90k calls to `re._compile`

2. ✅ **Lazy geometries**
   - Don't calculate `unary_union` until requested
   - Savings: 1.4s on medium file if visualization is not needed

3. ✅ **Cache aperture shapes**
   - Store geometries for already used apertures
   - Savings: ~200ms on files with repeated apertures

---

### Phase 2: Medium Optimizations (Medium Impact, Medium Effort)
**Estimated time:** 3-4 hours
**Expected speedup:** 30-40%

4. ✅ **Single regex for coordinates**
   - Unique pattern: `r'X([+-]?\d+\.?\d*)?Y([+-]?\d+\.?\d*)?I([+-]?\d+\.?\d*)?J([+-]?\d+\.?\d*)?D(\d+)?'`
   - Savings: ~300ms

5. ✅ **Batch geometry operations**
   - Accumulate shapes and do `unary_union` once
   - Savings: ~400ms

6. ✅ **Lookup table for commands**
   - Dict instead of `any(startswith())`
   - Savings: ~100ms

---

### Phase 3: Advanced Optimizations (High Impact, High Effort)
**Estimated time:** 8-10 hours
**Expected speedup:** 50-70%

7. ⚠️ **Parallel processing**
   - Tokenize and parse in parallel
   - Requires significant refactoring

8. ⚠️ **C extension for parsing**
   - Implement critical parser in Cython
   - 5-10x speedup but requires compilation

9. ⚠️ **Alternatives to Shapely**
   - Evaluate pygeos (10x faster)
   - Requires API change

---

## 📈 Expected Speedup

### Conservative Scenario (Phase 1 Only)
- Small file: 13ms → 10ms (23% faster)
- Medium file: 3.4s → 2.4s (30% faster)
- Large file (10MB): 120s → 84s (30% faster)

### Optimistic Scenario (Phase 1 + 2)
- Small file: 13ms → 8ms (38% faster)
- Medium file: 3.4s → 1.7s (50% faster)
- Large file (10MB): 120s → 60s (50% faster)

### Aggressive Scenario (All phases)
- Small file: 13ms → 5ms (62% faster)
- Medium file: 3.4s → 1.0s (70% faster)
- Large file (10MB): 120s → 36s (70% faster)

---

## 🎯 Recommendation

**Start with Phase 1 (Quick Wins):**
1. Pre-compile regex
2. Lazy geometries
3. Cache aperture shapes

**Benefits:**
- ✅ Low risk
- ✅ High impact (30% speedup)
- ✅ Little time (1-2 hours)
- ✅ No breaking changes

**Then evaluate Phase 2 if necessary.**

---

## 📝 Notes

- Current performance is already good for files < 1MB
- Optimizations are critical only for files > 10MB
- Shapely is the main bottleneck (not our code)
- Alternatives to Shapely require significant refactoring

---

## 🔬 Target Metrics

### Small File (< 1KB)
- ✅ Current: 13ms
- 🎯 Target: < 10ms
- ✅ **ALREADY ACCEPTABLE**

### Medium File (100KB - 1MB)
- ⚠️ Current: 3.4s for 272KB
- 🎯 Target: < 2s
- ⚠️ **IMPROVABLE**

### Large File (> 10MB)
- ❌ Estimated: ~120s for 10MB
- 🎯 Target: < 30s
- ❌ **OPTIMIZATION REQUIRED**
