# Requirements Checklist: Tier A Core Python Shadow Libraries

**Feature Branch**: `001-tier-a-core-shadows`
**Last Updated**: 2026-03-13

## R1: PyO3 crate per shadow module

- [ ] `shadow-datetime` crate compiles as `#[pymodule]` via maturin
- [ ] `shadow-datetime` exposes `datetime`, `date`, `time`, `timedelta`, `timezone` classes
- [ ] `shadow-datetime` supports `now()`, `utcnow()`, `fromtimestamp()`, `strptime()`, `strftime()`, `isoformat()`, `replace()`, timedelta arithmetic
- [ ] `shadow-datetime` uses `chrono` as its Rust backend
- [ ] `shadow-re` crate compiles as `#[pymodule]` via maturin
- [ ] `shadow-re` exposes `compile`, `search`, `match`, `fullmatch`, `findall`, `finditer`, `sub`, `subn`, `split`, `escape`, `purge`
- [ ] `shadow-re` exposes `Match` object with `group`, `groups`, `groupdict`, `start`, `end`, `span`
- [ ] `shadow-re` supports flags: `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`, `ASCII`, `UNICODE`
- [ ] `shadow-re` uses `regex` as its Rust backend
- [ ] `shadow-json` crate compiles as `#[pymodule]` via maturin
- [ ] `shadow-json` exposes `dumps`, `loads`, `dump`, `load`
- [ ] `shadow-json` supports encoder kwargs: `sort_keys`, `indent`, `ensure_ascii`, `default`, `separators`, `cls`
- [ ] `shadow-json` supports decoder kwargs: `object_hook`, `object_pairs_hook`, `parse_float`, `parse_int`, `cls`
- [ ] `shadow-json` raises `JSONDecodeError` for malformed input
- [ ] `shadow-json` uses `serde_json` as its Rust backend
- [ ] `shadow-hashlib` crate compiles as `#[pymodule]` via maturin
- [ ] `shadow-hashlib` exposes `md5`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512`, `new`
- [ ] `shadow-hashlib` hash objects support `update`, `digest`, `hexdigest`, `copy`
- [ ] `shadow-hashlib` hash objects expose `name`, `digest_size`, `block_size` attributes
- [ ] `shadow-hashlib` uses `sha2` and `md-5` as its Rust backends
- [ ] `shadow-decimal` crate compiles as `#[pymodule]` via maturin
- [ ] `shadow-decimal` exposes `Decimal` constructor (from string, int, float, tuple)
- [ ] `shadow-decimal` supports arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- [ ] `shadow-decimal` supports `quantize`, `normalize`, `to_eng_string`, `as_tuple`, `compare`, `sqrt`, `ln`, `log10`, `exp`
- [ ] `shadow-decimal` exposes rounding constants: `ROUND_HALF_UP`, `ROUND_HALF_DOWN`, `ROUND_CEILING`, `ROUND_FLOOR`, `ROUND_HALF_EVEN`
- [ ] `shadow-decimal` supports `getcontext()` / `setcontext()` for precision and rounding mode
- [ ] `shadow-decimal` uses `rust_decimal` as its Rust backend
- [ ] All five crates compile on Python 3.10+
- [ ] All five crates build on Linux, macOS (arm64, x86_64), and Windows

## R2: Import hook

- [ ] `hook/__init__.py` implements `install()` function
- [ ] `install()` registers a `sys.meta_path` finder intercepting `datetime`, `re`, `json`, `hashlib`, `decimal`
- [ ] `hook/__init__.py` implements `uninstall()` function
- [ ] `uninstall()` removes the finder and restores original CPython modules
- [ ] `install()` is idempotent — calling it twice does not duplicate finders
- [ ] `hook/_registry.py` maps stdlib module names to shadow package import paths
- [ ] Registry design supports adding Tier B shadows without modifying hook logic

## R3: Equivalence test suite

- [ ] `rust/tests/equivalence/test_datetime.py` exists and covers Scenario 1 operations
- [ ] `rust/tests/equivalence/test_re.py` exists and covers Scenario 2 operations
- [ ] `rust/tests/equivalence/test_json.py` exists and covers Scenario 3 operations
- [ ] `rust/tests/equivalence/test_hashlib.py` exists and covers Scenario 4 operations
- [ ] `rust/tests/equivalence/test_decimal.py` exists and covers Scenario 5 operations
- [ ] Each test file runs identical operations through CPython stdlib and shadow implementation
- [ ] Each test file asserts identical return values (with floating-point tolerance where needed)
- [ ] Each test file asserts identical exception types for error cases
- [ ] Tests use `@pytest.mark.parametrize` for combinatorial coverage
- [ ] All tests pass via `pytest rust/tests/equivalence/` with `conftest.py` activating the hook

## R4: Build and packaging

- [ ] `maturin develop` builds all five crates into the local virtualenv
- [ ] `maturin build --release` produces wheel artifacts without errors
- [ ] `pyproject.toml` declares workspace and all five extension modules
- [ ] CI pipeline runs `maturin build`
- [ ] CI pipeline runs `pytest rust/tests/equivalence/`
- [ ] CI pipeline runs `cargo test`

## R5: API surface coverage

- [ ] shadow-datetime covers all methods listed in R5 of the spec
- [ ] shadow-re covers all functions, Match methods, and flags listed in R5 of the spec
- [ ] shadow-json covers all functions, kwargs, and error types listed in R5 of the spec
- [ ] shadow-hashlib covers all hash algorithms, methods, and attributes listed in R5 of the spec
- [ ] shadow-decimal covers all constructors, operators, methods, and context functions listed in R5 of the spec

## Success Criteria

- [ ] After `hook.install()`, `import datetime` loads shadow-datetime (verified via `__shadow__` attribute)
- [ ] `pytest rust/tests/equivalence/` exits 0 with all tests green
- [ ] `maturin build --release` produces wheels without errors
- [ ] `cargo test --workspace` passes all Rust-side unit tests
- [ ] Existing Python code runs without modification under the shadow hook
- [ ] `hook.uninstall()` restores CPython stdlib modules
- [ ] Shadow implementations are not slower than CPython stdlib for covered operations
