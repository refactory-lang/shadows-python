# Feature Specification: Tier A Core Python Shadow Libraries

**Feature Branch**: `001-tier-a-core-shadows`
**Created**: 2026-03-13
**Status**: Draft

## Overview

Tier A delivers the five most critical Python shadow libraries: API-identical Python wrappers whose implementations delegate to Rust crates via PyO3 and maturin. An import hook transparently redirects standard `import datetime`, `import re`, etc. to the Rust-backed shadows at runtime, requiring zero changes to application code.

### Shadow Crates

| Shadow Crate       | Python stdlib module | Rust backend       |
|--------------------|----------------------|--------------------|
| shadow-datetime    | `datetime`           | `chrono`           |
| shadow-re          | `re`                 | `regex`            |
| shadow-json        | `json`               | `serde_json`       |
| shadow-hashlib     | `hashlib`            | `sha2` + `md-5`    |
| shadow-decimal     | `decimal`            | `rust_decimal`     |

### Repository Layout

```
shadows-python/
  hook/
    __init__.py          # MetaPathFinder / Loader that intercepts stdlib imports
    _registry.py         # Maps module names to shadow packages
  rust/
    Cargo.toml           # Workspace with members = ["crates/*"]
    crates/
      shadow-datetime/
        Cargo.toml       # pyo3, chrono
        src/lib.rs        # #[pymodule] exposing datetime-compatible API
      shadow-re/
        Cargo.toml       # pyo3, regex
        src/lib.rs
      shadow-json/
        Cargo.toml       # pyo3, serde_json
        src/lib.rs
      shadow-hashlib/
        Cargo.toml       # pyo3, sha2, md-5
        src/lib.rs
      shadow-decimal/
        Cargo.toml       # pyo3, rust_decimal
        src/lib.rs
    tests/
      equivalence/
        test_datetime.py
        test_re.py
        test_json.py
        test_hashlib.py
        test_decimal.py
  conftest.py            # Activates import hook for pytest sessions
  pyproject.toml
```

---

## User Scenarios & Testing

### Scenario 1: Transparent import replacement

A developer writes standard Python code:

```python
from datetime import datetime, timedelta

now = datetime.now()
tomorrow = now + timedelta(days=1)
print(tomorrow.isoformat())
```

With the shadow hook active (via `conftest.py` or explicit `import hook`), `from datetime import datetime` loads `shadow-datetime` backed by `chrono`. The developer's code runs without modification and produces identical output to CPython's `datetime`.

**Test**: `rust/tests/equivalence/test_datetime.py`
- Create `datetime`, `date`, `time`, `timedelta` objects via shadow and via CPython stdlib.
- Compare `str()`, `repr()`, `isoformat()`, arithmetic results, `strftime()` output.
- Verify `isinstance` checks pass for the shadow types where feasible, or document divergence.

### Scenario 2: Regex pattern matching

A developer uses `re.compile`, `re.search`, `re.findall`, and `re.sub`:

```python
import re

pattern = re.compile(r"\b\w+@\w+\.\w+\b")
matches = pattern.findall("contact foo@bar.com or baz@qux.org")
assert matches == ["foo@bar.com", "baz@qux.org"]
```

The shadow hook routes `import re` to `shadow-re` backed by the Rust `regex` crate.

**Test**: `rust/tests/equivalence/test_re.py`
- Run identical regex operations through both CPython `re` and `shadow-re`.
- Cover `compile`, `search`, `match`, `fullmatch`, `findall`, `finditer`, `sub`, `subn`, `split`.
- Compare match objects: `.group()`, `.start()`, `.end()`, `.span()`, `.groups()`.
- Include edge cases: empty pattern, unicode, multiline, DOTALL flag.

### Scenario 3: JSON round-trip

```python
import json

data = {"key": [1, 2.5, True, None], "nested": {"a": "b"}}
encoded = json.dumps(data, sort_keys=True, indent=2)
decoded = json.loads(encoded)
assert decoded == data
```

**Test**: `rust/tests/equivalence/test_json.py`
- Round-trip primitives, nested structures, unicode strings.
- Verify `dumps` keyword arguments: `sort_keys`, `indent`, `ensure_ascii`, `separators`, `default`.
- Verify `loads` with `object_hook`, `parse_float`, `parse_int`.
- Compare error messages for malformed JSON.

### Scenario 4: Hash computation

```python
import hashlib

digest = hashlib.sha256(b"hello world").hexdigest()
assert digest == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
```

**Test**: `rust/tests/equivalence/test_hashlib.py`
- Compute `md5`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512` via both CPython and shadow.
- Test incremental `update()` calls and verify `hexdigest()` and `digest()` match.
- Test `hashlib.new("sha256", ...)` factory function.

### Scenario 5: Decimal arithmetic

```python
from decimal import Decimal, ROUND_HALF_UP

price = Decimal("19.99")
tax = Decimal("0.0825")
total = (price * (1 + tax)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
assert total == Decimal("21.64")
```

**Test**: `rust/tests/equivalence/test_decimal.py`
- Arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**` between `Decimal` values.
- Rounding modes: `ROUND_HALF_UP`, `ROUND_HALF_DOWN`, `ROUND_CEILING`, `ROUND_FLOOR`, `ROUND_HALF_EVEN`.
- `quantize`, `normalize`, `to_eng_string`, `as_tuple`.
- Special values: `Decimal("Infinity")`, `Decimal("-0")`, `Decimal("NaN")`.

### Scenario 6: Import hook activation via conftest

A project adds `conftest.py` at the repo root:

```python
import hook
hook.install()
```

All subsequent `import datetime`, `import re`, `import json`, `import hashlib`, `from decimal import Decimal` in the test session resolve to shadow implementations.

**Test**: Verify that after `hook.install()`, `sys.modules["datetime"].__file__` (or equivalent marker) points to the shadow module, and after `hook.uninstall()`, the original CPython module is restored.

---

## Requirements

### R1: PyO3 crate per shadow module

Each of the five crates (`shadow-datetime`, `shadow-re`, `shadow-json`, `shadow-hashlib`, `shadow-decimal`) must:

1. Be a valid `#[pymodule]` compiled via maturin as a Python extension module (`.so` / `.pyd`).
2. Expose the same top-level names as the corresponding CPython stdlib module. At minimum, cover the functions and classes listed in the equivalence tests above.
3. Use the Rust backend crate listed in the table (chrono, regex, serde_json, sha2+md-5, rust_decimal).
4. Compile on Python 3.10+ with maturin 1.x on Linux, macOS (arm64 and x86_64), and Windows.

### R2: Import hook

`hook/__init__.py` must implement:

1. `install()` — registers a `sys.meta_path` finder that intercepts imports for `datetime`, `re`, `json`, `hashlib`, and `decimal`, loading the corresponding shadow crate instead.
2. `uninstall()` — removes the finder and restores original modules from a saved reference.
3. The hook must be idempotent: calling `install()` twice must not duplicate finders.
4. `hook/_registry.py` maps stdlib module names to shadow package import paths, making it straightforward to add Tier B shadows later.

### R3: Equivalence test suite

Each shadow crate must have a corresponding `rust/tests/equivalence/test_<module>.py` that:

1. Runs the same operations through both CPython stdlib and the shadow implementation.
2. Asserts identical return values (within floating-point tolerance where applicable).
3. Asserts identical exception types and messages for error cases (e.g., invalid regex, malformed JSON).
4. Uses `@pytest.mark.parametrize` for combinatorial coverage.
5. Is runnable via `pytest rust/tests/equivalence/` with no extra configuration beyond `conftest.py`.

### R4: Build and packaging

1. `maturin develop` builds all five crates into the local virtualenv.
2. `maturin build --release` produces wheel artifacts.
3. `pyproject.toml` declares the workspace and all five crates as extension modules.
4. CI must run: `maturin build`, `pytest rust/tests/equivalence/`, and `cargo test` (for any pure-Rust unit tests).

### R5: API surface — minimum coverage per crate

**shadow-datetime**: `datetime`, `date`, `time`, `timedelta`, `timezone`, `datetime.now()`, `datetime.utcnow()`, `datetime.fromtimestamp()`, `datetime.strptime()`, `strftime()`, `isoformat()`, `replace()`, arithmetic on `timedelta`.

**shadow-re**: `compile`, `search`, `match`, `fullmatch`, `findall`, `finditer`, `sub`, `subn`, `split`, `escape`, `purge`. `Match` object with `group`, `groups`, `groupdict`, `start`, `end`, `span`. Flags: `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`, `ASCII`, `UNICODE`.

**shadow-json**: `dumps`, `loads`, `dump`, `load`. Encoder keyword arguments: `sort_keys`, `indent`, `ensure_ascii`, `default`, `separators`, `cls`. Decoder keyword arguments: `object_hook`, `object_pairs_hook`, `parse_float`, `parse_int`, `cls`. `JSONDecodeError` exception.

**shadow-hashlib**: `md5`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512`, `new`. Hash object methods: `update`, `digest`, `hexdigest`, `copy`. Attributes: `name`, `digest_size`, `block_size`.

**shadow-decimal**: `Decimal` constructor (from string, int, float, tuple), arithmetic operators, `quantize`, `normalize`, `to_eng_string`, `as_tuple`, `compare`, `sqrt`, `ln`, `log10`, `exp`. Rounding constants. `DecimalException` hierarchy. `getcontext()` / `setcontext()` for precision and rounding mode.

---

## Success Criteria

1. **Transparent loading**: After `hook.install()`, `import datetime` loads the `shadow-datetime` module. Verified by checking a `__shadow__` attribute or module path.
2. **Equivalence tests pass**: `pytest rust/tests/equivalence/` exits 0 with all tests green across all five modules.
3. **Build succeeds**: `maturin build --release` produces wheels for the current platform without errors.
4. **Cargo tests pass**: `cargo test --workspace` in `rust/` passes all Rust-side unit tests.
5. **No application code changes**: Existing Python code using `datetime`, `re`, `json`, `hashlib`, and `decimal` runs without modification under the shadow hook.
6. **Hook is reversible**: `hook.uninstall()` restores CPython stdlib modules; subsequent imports use the originals.
7. **Performance parity or better**: Shadow implementations must not be slower than CPython stdlib for the operations covered in the equivalence tests (measured via `pytest-benchmark` or equivalent).
