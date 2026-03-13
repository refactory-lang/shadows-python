# Feature Specification: Tier A Core Shadow Libraries

**Feature Branch**: `001-tier-a-core-shadows`
**Created**: 2026-03-13
**Status**: Draft
**Input**: User description: "Implement Tier A (Core) Python shadow libraries - shadow-datetime (chrono), shadow-re (regex), shadow-json (serde_json), shadow-hashlib (sha2), shadow-decimal (rust_decimal) with PyO3 bindings and CPython equivalence tests"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import datetime transparently via shadow hook (Priority: P1)

A developer writes `import datetime` in their Python code. With the shadow hook activated (via `conftest.py` or explicit `activate()` call), the import is intercepted and the Rust-backed `shadow_datetime` module (powered by `chrono`) is loaded instead of CPython's `datetime`. The developer uses `datetime.datetime.now()`, `datetime.timedelta(days=5)`, `datetime.date.today()`, and all other standard datetime APIs exactly as before, with identical return types and behavior.

**Why this priority**: `datetime` is the most widely used stdlib module in the Tier A set. It exercises the full PyO3 class hierarchy (date, time, datetime, timedelta, timezone) and validates that the import hook mechanism works end-to-end.

**Independent Test**: Can be fully tested by activating the shadow hook, running `import datetime`, and verifying that `datetime.datetime.now()` returns a value equivalent to CPython's `datetime.datetime.now()` within a tolerance window. Delivers value as a standalone proof that Rust-backed shadows can transparently replace CPython modules.

**Acceptance Scenarios**:

1. **Given** the shadow hook is activated with tiers="A", **When** a developer writes `import datetime`, **Then** `sys.modules['datetime']` points to the shadow module backed by chrono, and `datetime.datetime(2024, 1, 15, 10, 30, 0)` produces an object whose `year`, `month`, `day`, `hour`, `minute`, `second` attributes match CPython's output exactly.
2. **Given** the shadow hook is activated, **When** a developer creates `datetime.timedelta(days=5, hours=3)` and adds it to `datetime.datetime(2024, 1, 1)`, **Then** the result equals `datetime.datetime(2024, 1, 6, 3, 0)`, identical to CPython behavior.
3. **Given** the shadow hook is activated, **When** a developer calls `datetime.datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")`, **Then** the formatted string matches CPython's output character-for-character.
4. **Given** the shadow hook is activated, **When** a developer calls `datetime.datetime.fromisoformat("2024-01-15T10:30:00")`, **Then** the returned object has the same attributes as CPython's equivalent call.

---

### User Story 2 - Use json.dumps/loads with shadow-json (Priority: P1)

A developer writes `import json` and calls `json.dumps({"key": [1, 2, 3]})` and `json.loads('{"key": [1, 2, 3]}')`. The shadow hook loads `shadow_json` backed by `serde_json`. All standard `json` module functions (`dumps`, `loads`, `dump`, `load`, `JSONEncoder`, `JSONDecoder`) behave identically to CPython's `json` module, including keyword arguments like `indent`, `sort_keys`, `separators`, and `default`.

**Why this priority**: JSON serialization is fundamental to nearly all Python applications. The API surface is relatively small (two core functions plus options), making it a high-value, achievable first target alongside datetime.

**Independent Test**: Can be tested by round-tripping complex nested data structures through `json.dumps` then `json.loads` and comparing output byte-for-byte with CPython's json module.

**Acceptance Scenarios**:

1. **Given** the shadow hook is activated, **When** `json.dumps({"b": 2, "a": 1}, sort_keys=True, indent=2)` is called, **Then** the output string is identical to CPython's output.
2. **Given** the shadow hook is activated, **When** `json.loads('{"key": [1, 2.5, true, null, "str"]}')` is called, **Then** the returned dict has identical types and values as CPython's output.
3. **Given** the shadow hook is activated, **When** `json.dumps(obj, default=str)` is called with a non-serializable object, **Then** the behavior matches CPython (calls `str()` on the object).
4. **Given** the shadow hook is activated, **When** `json.loads("invalid json")` is called, **Then** a `json.JSONDecodeError` is raised with a message consistent with CPython's error format.

---

### User Story 3 - Pattern matching with shadow-re (Priority: P1)

A developer writes `import re` and uses `re.compile()`, `re.match()`, `re.search()`, `re.findall()`, `re.sub()`, and `re.split()`. The shadow hook loads `shadow_re` backed by the Rust `regex` crate. Match objects support `.group()`, `.groups()`, `.span()`, `.start()`, `.end()`, and named groups via `(?P<name>...)` syntax.

**Why this priority**: Regular expressions are a core primitive used across all Python codebases. The `regex` crate is one of Rust's most mature libraries, making this a strong candidate for demonstrating performance benefits.

**Independent Test**: Can be tested by compiling patterns and matching against known inputs, then comparing all match object attributes with CPython's `re` module output.

**Acceptance Scenarios**:

1. **Given** the shadow hook is activated, **When** `re.findall(r'\d+', 'abc123def456')` is called, **Then** the result is `['123', '456']`, identical to CPython.
2. **Given** the shadow hook is activated, **When** `re.sub(r'(\w+)', r'\1_x', 'hello world')` is called, **Then** the result is `'hello_x world_x'`, identical to CPython.
3. **Given** the shadow hook is activated, **When** `re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})').match('2024-01')` is called, **Then** `m.group('year')` returns `'2024'` and `m.group('month')` returns `'01'`.
4. **Given** the shadow hook is activated, **When** `re.search(r'[invalid', 'text')` is called with an invalid pattern, **Then** `re.error` is raised, consistent with CPython.

---

### User Story 4 - Hashing with shadow-hashlib (Priority: P2)

A developer writes `import hashlib` and uses `hashlib.sha256(b"data").hexdigest()`, `hashlib.md5(b"data").hexdigest()`, `hashlib.new("sha512")`, and incremental hashing via `.update()`. The shadow hook loads `shadow_hashlib` backed by `sha2`, `md-5`, and `digest` crates.

**Why this priority**: Hashing is a frequently used utility but has a simpler API surface than datetime or re. It serves as a validation that the shadow approach works for stateful objects (hash objects accumulate data via `.update()`).

**Independent Test**: Can be tested by hashing known byte strings and comparing hex digest output character-for-character with CPython's hashlib.

**Acceptance Scenarios**:

1. **Given** the shadow hook is activated, **When** `hashlib.sha256(b"hello world").hexdigest()` is called, **Then** the result matches CPython's output exactly: `"b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"`.
2. **Given** the shadow hook is activated, **When** a hash object is created with `h = hashlib.sha256()`, then `h.update(b"hello ")` and `h.update(b"world")` are called, **Then** `h.hexdigest()` matches the single-call result above.
3. **Given** the shadow hook is activated, **When** `hashlib.new("sha512", b"test").hexdigest()` is called, **Then** the result matches CPython's output.
4. **Given** the shadow hook is activated, **When** `hashlib.md5(b"test").digest()` is called, **Then** the returned bytes match CPython's output.

---

### User Story 5 - Decimal arithmetic with shadow-decimal (Priority: P2)

A developer writes `from decimal import Decimal` and performs `Decimal("0.1") + Decimal("0.2")`, expecting `Decimal("0.3")` (not the floating-point `0.30000000000000004`). The shadow hook loads `shadow_decimal` backed by `rust_decimal`. Standard operations (add, subtract, multiply, divide, comparison, string conversion) all behave identically to CPython's `decimal.Decimal`.

**Why this priority**: Decimal is important for financial and scientific applications but has a more complex API surface (contexts, rounding modes, special values). It validates that the shadow approach handles operator overloading and rich comparison protocols.

**Independent Test**: Can be tested by performing arithmetic operations on Decimal values and comparing results with CPython's decimal module.

**Acceptance Scenarios**:

1. **Given** the shadow hook is activated, **When** `Decimal("0.1") + Decimal("0.2")` is computed, **Then** `str(result)` equals `"0.3"`, identical to CPython.
2. **Given** the shadow hook is activated, **When** `Decimal("10") / Decimal("3")` is computed, **Then** the result matches CPython's output given the same precision context.
3. **Given** the shadow hook is activated, **When** `Decimal("1.555").quantize(Decimal("0.01"))` is called, **Then** the result equals `Decimal("1.56")` (banker's rounding), identical to CPython.
4. **Given** the shadow hook is activated, **When** `Decimal("inf")`, `Decimal("-inf")`, and `Decimal("NaN")` are created, **Then** their `is_infinite()`, `is_nan()`, and comparison behaviors match CPython.

---

### User Story 6 - Equivalence test suite validates shadow == CPython (Priority: P1)

A developer or CI system runs `pytest rust/tests/equivalence/` which executes a comprehensive test suite comparing shadow module outputs against CPython module outputs for all Tier A libraries. Each test calls the same API on both the shadow and CPython implementations and asserts the results are equal. The test suite uses the conftest plugin to activate/deactivate the shadow hook as needed.

**Why this priority**: Without equivalence tests, there is no verifiable guarantee that the shadows behave identically to CPython. This is the primary quality gate for the entire shadow library approach.

**Independent Test**: Can be run independently with `pytest rust/tests/equivalence/ -v` and produces a clear pass/fail report for each API.

**Acceptance Scenarios**:

1. **Given** the equivalence test suite exists, **When** `pytest rust/tests/equivalence/test_datetime_equiv.py` is run, **Then** all tests pass, covering constructors, arithmetic, formatting, parsing, and timezone operations.
2. **Given** the equivalence test suite exists, **When** `pytest rust/tests/equivalence/test_json_equiv.py` is run, **Then** all tests pass, covering dumps/loads with various options, edge cases (empty, nested, unicode), and error cases.
3. **Given** the equivalence test suite exists, **When** `pytest rust/tests/equivalence/test_re_equiv.py` is run, **Then** all tests pass, covering compile, match, search, findall, sub, split, and named groups.
4. **Given** the equivalence test suite exists, **When** `pytest rust/tests/equivalence/test_hashlib_equiv.py` is run, **Then** all tests pass, covering all supported algorithms, incremental hashing, and digest formats.
5. **Given** the equivalence test suite exists, **When** `pytest rust/tests/equivalence/test_decimal_equiv.py` is run, **Then** all tests pass, covering arithmetic, rounding, special values, and string conversion.

---

### Edge Cases

- What happens when a developer imports a submodule like `from datetime import datetime`? The shadow must support attribute-level access, not just top-level module import.
- How does the system handle `re` patterns that use Python-specific syntax not supported by the Rust `regex` crate (e.g., lookbehind with variable-length patterns)? The shadow should raise the same exception type as CPython or document known incompatibilities.
- What happens when `json.dumps` receives a custom object with a custom `JSONEncoder` subclass? The shadow must either support the same protocol or raise a clear error.
- How does `hashlib.algorithms_available` behave? The shadow should return the set of algorithms actually implemented in the Rust backend, and `hashlib.algorithms_guaranteed` must match CPython's contract.
- What happens when `Decimal` operations exceed the precision supported by `rust_decimal` (28 significant digits)? The shadow should either match CPython's arbitrary precision or raise `InvalidOperation` with a clear message.
- What happens when the shadow hook is activated but the compiled `.so`/`.dylib` for a crate is missing (not yet built with maturin)? The import should fall back to CPython's stdlib with a warning, not crash.
- How does the system handle `pickle.dumps(datetime.datetime.now())` when datetime is a shadow? The pickled object must be deserializable in a non-shadow Python environment.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `shadow-datetime` MUST expose a PyO3 module named `shadow_datetime` that provides `date`, `time`, `datetime`, `timedelta`, `timezone`, and `MINYEAR`/`MAXYEAR` constants, backed by the `chrono` crate. All constructors, instance methods, class methods (`now()`, `today()`, `utcnow()`, `fromisoformat()`, `strptime()`, `strftime()`), arithmetic operators (`+`, `-` between datetime and timedelta), and comparison operators MUST produce results identical to CPython's `datetime` module.

- **FR-002**: `shadow-re` MUST expose a PyO3 module named `shadow_re` that provides `compile()`, `match()`, `search()`, `findall()`, `finditer()`, `sub()`, `subn()`, `split()`, `escape()`, `error`, and flag constants (`IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`, `ASCII`, `UNICODE`), backed by the Rust `regex` crate. Pattern objects and match objects MUST support the same methods and attributes as CPython's `re` module. Known incompatibilities with Python-specific regex features (e.g., lookbehind length limits) MUST be documented.

- **FR-003**: `shadow-json` MUST expose a PyO3 module named `shadow_json` that provides `dumps()`, `loads()`, `dump()`, `load()`, `JSONEncoder`, `JSONDecoder`, and `JSONDecodeError`, backed by `serde_json`. The `dumps()` function MUST support `indent`, `sort_keys`, `separators`, `default`, `ensure_ascii`, and `cls` keyword arguments. The `loads()` function MUST support `cls`, `object_hook`, `object_pairs_hook`, and `parse_float` keyword arguments. Output MUST be byte-identical to CPython's json module for the same inputs and options.

- **FR-004**: `shadow-hashlib` MUST expose a PyO3 module named `shadow_hashlib` that provides `md5()`, `sha1()`, `sha224()`, `sha256()`, `sha384()`, `sha512()`, and `new()` constructors, backed by `sha2`, `md-5`, and `digest` crates. Hash objects MUST support `.update(data)`, `.digest()`, `.hexdigest()`, `.copy()`, `.name`, `.digest_size`, and `.block_size` attributes. Output MUST be byte-identical to CPython's hashlib for the same inputs.

- **FR-005**: `shadow-decimal` MUST expose a PyO3 module named `shadow_decimal` that provides `Decimal` class, `getcontext()`, `setcontext()`, `localcontext()`, `BasicContext`, `ExtendedContext`, `DefaultContext`, and exception classes (`InvalidOperation`, `DivisionByZero`, `Overflow`, `Underflow`, `Inexact`, `Rounded`, `Subnormal`, `FloatOperation`, `DecimalException`), backed by `rust_decimal`. Arithmetic operators, comparison operators, `quantize()`, `to_eng_string()`, `is_nan()`, `is_infinite()`, `is_zero()`, `is_signed()`, and string conversion MUST match CPython behavior.

- **FR-006**: The import hook in `hook/__init__.py` MUST intercept `import datetime`, `import re`, `import json`, `import hashlib`, and `from decimal import Decimal` when activated with `tiers="A"`, loading the corresponding shadow modules transparently.

- **FR-007**: The `conftest_plugin.py` MUST activate the shadow hook automatically when pytest is run, allowing developers to control tiers via pytest configuration (`refactory_shadow_tiers` ini option).

- **FR-008**: Each of the 5 Tier A crates MUST build successfully with `maturin develop` from the `rust/` workspace root, producing importable Python extension modules.

- **FR-009**: An equivalence test suite MUST exist at `rust/tests/equivalence/` with one test file per Tier A crate (`test_datetime_equiv.py`, `test_re_equiv.py`, `test_json_equiv.py`, `test_hashlib_equiv.py`, `test_decimal_equiv.py`). Each test file MUST compare shadow module output against CPython stdlib output for a comprehensive set of API calls.

- **FR-010**: When a shadow module's compiled extension is unavailable (not built), the import hook MUST fall back to CPython's stdlib module and emit a warning via `warnings.warn()` rather than raising an ImportError.

### Key Entities

- **Shadow Module**: A compiled Rust extension (`.so` / `.dylib` / `.pyd`) that exposes the same Python API as a CPython stdlib module. Built via PyO3/maturin as a `cdylib` crate.
- **Import Hook (`ShadowImportHook`)**: A `sys.meta_path` finder/loader that intercepts stdlib imports and redirects them to shadow modules. Configured with a set of active tiers.
- **Equivalence Test**: A pytest test that calls the same API on both the shadow implementation and CPython's stdlib, asserting identical results. Tests are parametrized across input variations.
- **Tier**: A grouping of shadow modules by complexity and risk. Tier A (Core) includes datetime, re, json, hashlib, and decimal.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `import datetime` loads the chrono-backed shadow implementation when the hook is active, verified by checking `type(datetime.datetime).__module__` contains `shadow`.
- **SC-002**: `import re` loads the regex-backed shadow implementation, verified by `re.search(r'\d+', '123').group()` returning `'123'`.
- **SC-003**: `import json` loads the serde_json-backed shadow implementation, verified by `json.dumps({"a": 1}) == '{"a": 1}'`.
- **SC-004**: `import hashlib` loads the sha2-backed shadow implementation, verified by `hashlib.sha256(b"test").hexdigest()` matching the known hash.
- **SC-005**: `from decimal import Decimal` loads the rust_decimal-backed shadow implementation, verified by `str(Decimal("0.1") + Decimal("0.2")) == "0.3"`.
- **SC-006**: All 5 Tier A crates build successfully with `maturin develop` in under 120 seconds on a standard development machine.
- **SC-007**: The equivalence test suite (`pytest rust/tests/equivalence/`) passes with zero failures across all 5 Tier A crate test files.
- **SC-008**: The shadow import hook activates and deactivates cleanly without corrupting `sys.modules` or `sys.meta_path` state, verified by `deactivate()` restoring original import behavior.
- **SC-009**: No shadow module introduces a regression in import time greater than 50ms compared to CPython's stdlib module, measured via `time.time()` around import statements.
