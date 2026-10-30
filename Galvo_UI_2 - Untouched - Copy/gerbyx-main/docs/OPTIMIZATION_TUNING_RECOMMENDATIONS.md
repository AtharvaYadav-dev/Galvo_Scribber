# 🔧 Tuning Batch Union - Recommendations

## 📊 Problem Identified

After real-world tests, we discovered that:
- ✅ **Parsing:** +22% faster
- ✅ **Tokenization:** +13% faster
- ⚠️ **Geometries:** -18% slower on medium file

**Cause:** Batch union has overhead on files with few geometries (256 shapes).

---

## 🎯 Solution: Adaptive Batching

### Proposed Implementation

```python
# src/gerbyx/processor.py

def _batch_union(self, shapes):
    """Batch unary_union with adaptive sizing"""
    if len(shapes) == 1:
        return shapes[0]

    # Adaptive threshold based on number of shapes
    if len(shapes) < 100:
        # Small files: direct union (faster)
        return unary_union(shapes)

    elif len(shapes) < 500:
        # Medium files: small batches
        batch_size = 50
        batches = []
        for i in range(0, len(shapes), batch_size):
            batch = shapes[i:i+batch_size]
            batches.append(unary_union(batch))
        return unary_union(batches)

    else:
        # Large files: large batches to avoid stack overflow
        batch_size = 100
        batches = []
        for i in range(0, len(shapes), batch_size):
            batch = shapes[i:i+batch_size]
            batches.append(unary_union(batch))
        return unary_union(batches)
```

---

## 📈 Expected Performance

### With Adaptive Batching

| File | Shapes | Strategy | Current Time | Expected Time | Improvement |
|--------|--------|----------|--------------|---------------|-------------|
| Small | 3 | Direct | 2.09 ms | 1.5 ms | +28% |
| Medium | 256 | Batch 50 | 1,638 ms | 1,200 ms | +27% |
| Large | >1000 | Batch 100| ~5s | ~3.5s | +30% |

---

## 🔧 Necessary Changes

### File: src/gerbyx/processor.py

**Replace the current `_batch_union` method with:**

```python
def _batch_union(self, shapes):
    """
    Batch unary_union with adaptive sizing to optimize performance.

    Strategy:
    - <100 shapes: direct union (batch overhead not worth it)
    - 100-500 shapes: batch of 50 (balance overhead/performance)
    - >500 shapes: batch of 100 (avoids stack overflow)
    """
    if len(shapes) == 1:
        return shapes[0]

    # Adaptive threshold
    if len(shapes) < 100:
        return unary_union(shapes)

    # Calculate optimal batch size
    if len(shapes) < 500:
        batch_size = 50
    else:
        batch_size = 100

    # Batch processing
    batches = []
    for i in range(0, len(shapes), batch_size):
        batch = shapes[i:i+batch_size]
        batches.append(unary_union(batch))

    return unary_union(batches)
```

---

## 🧪 Recommended Tests

### 1. File with Few Geometries (<100)
```python
# Test: gerber_x3_correct.gbr (3 shapes)
# Expected: Direct union, no overhead
```

### 2. File with Medium Geometries (100-500)
```python
# Test: copper_top.gbr (256 shapes)
# Expected: Batch 50, +27% speedup
```

### 3. File with Many Geometries (>500)
```python
# Test: large file (>1000 shapes)
# Expected: Batch 100, no stack overflow
```

---

## 📊 Performance Projections

### Total Speedup with Tuning

| File | Baseline | Phase 2 Current | Phase 2 Tuned | Improvement |
|--------------|----------|-----------------|---------------|-------------|
| Small (0.6KB) | 13 ms | 8.25 ms | **7 ms** | **+46%** ✅ |
| Medium (272KB)| 3,403 ms | 3,189 ms | **2,800 ms** | **+18%** ✅ |
| Large (10MB) | ~120s | ~112s | **~90s** | **+25%** ✅ |

---

## 💡 Further Optimizations

### 1. Cache Batch Results
```python
def _batch_union(self, shapes):
    # Cache for already processed batches
    cache_key = tuple(id(s) for s in shapes[:10])  # Sample
    if cache_key in self._batch_cache:
        return self._batch_cache[cache_key]

    result = self._do_batch_union(shapes)
    self._batch_cache[cache_key] = result
    return result
```

### 2. Parallel Batch Processing
```python
from concurrent.futures import ThreadPoolExecutor

def _batch_union_parallel(self, shapes):
    if len(shapes) < 500:
        return self._batch_union(shapes)

    with ThreadPoolExecutor(max_workers=4) as executor:
        batch_size = 100
        futures = []
        for i in range(0, len(shapes), batch_size):
            batch = shapes[i:i+batch_size]
            futures.append(executor.submit(unary_union, batch))

        batches = [f.result() for f in futures]
        return unary_union(batches)
```

---

## ✅ Implementation Checklist

- [ ] Modify `_batch_union()` in processor.py
- [ ] Test with small file (3 shapes)
- [ ] Test with medium file (256 shapes)
- [ ] Test with large file (>1000 shapes)
- [ ] Verify no stack overflow
- [ ] Benchmark before/after
- [ ] Update documentation

---

## 🎯 Expected Results

### After Tuning

**Total speedup on medium file: +18%** (vs +6% current)

```
Medium File (272 KB):
  Baseline:     3,403 ms  ████████████████████████████████████
  Phase 2 Now:  3,189 ms  ██████████████████████████████████
  Phase 2 Tuned: 2,800 ms  ████████████████████████████

  SPEEDUP: +18% (savings: 603 ms) ✅
```

---

## 📝 Implementation Notes

### Priority: HIGH
This optimization resolves the regression on geometries.

### Risk: LOW
- No breaking changes
- Backward compatible
- Only parameter tuning

### Effort: MINIMAL
- 1 method to modify
- 30 minutes of work
- Existing tests

---

## 🚀 Next Steps

1. **Implement adaptive batching** (30 min)
2. **Test with real files** (1 hour)
3. **Benchmark before/after** (30 min)
4. **Update documentation** (30 min)

**Total: 2.5 hours**

---

**Priority:** 🔴 HIGH
**Risk:** 🟢 LOW
**Effort:** 🟢 MINIMAL
**Impact:** 🟢 HIGH (+12% speedup)
