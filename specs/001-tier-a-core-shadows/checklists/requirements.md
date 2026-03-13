# Requirements Checklist: Tier A Core Shadow Libraries

**Feature Branch**: `001-tier-a-core-shadows`
**Last Updated**: 2026-03-13

## Functional Requirements

### shadow-datetime (FR-001)
- [ ] PyO3 module `shadow_datetime` compiles and is importable
- [ ] `date` class with constructor `date(year, month, day)` and attributes `year`, `month`, `day`
- [ ] `date.today()`, `date.fromtimestamp()`, `date.fromisoformat()` class methods
- [ ] `date.isoformat()`, `date.strftime()`, `date.weekday()`, `date.isoweekday()` instance methods
- [ ] `time` class with constructor `time(hour, minute, second, microsecond, tzinfo)` and all attributes
- [ ] `datetime` class with full constructor and all attributes
- [ ] `datetime.now()`, `datetime.utcnow()`, `datetime.today()`, `datetime.fromtimestamp()` class methods
- [ ] `datetime.fromisoformat()`, `datetime.strptime()` parsing class methods
- [ ] `datetime.strftime()`, `datetime.isoformat()`, `datetime.timestamp()` instance methods
- [ ] `timedelta` class with constructor and arithmetic (`+`, `-`, `*`, `//`, `%`)
- [ ] `datetime + timedelta` and `datetime - datetime` arithmetic
- [ ] `timezone` class with `timezone.utc` and `timezone(offset)` constructor
- [ ] `MINYEAR` and `MAXYEAR` constants
- [ ] Comparison operators (`<`, `<=`, `==`, `!=`, `>=`, `>`) on all types
- [ ] `str()` and `repr()` output matches CPython format

### shadow-re (FR-002)
- [ ] PyO3 module `shadow_re` compiles and is importable
- [ ] `compile(pattern, flags=0)` returns a Pattern object
- [ ] `match(pattern, string, flags=0)` returns Match or None
- [ ] `search(pattern, string, flags=0)` returns Match or None
- [ ] `findall(pattern, string, flags=0)` returns list of strings/tuples
- [ ] `finditer(pattern, string, flags=0)` returns iterator of Match objects
- [ ] `sub(pattern, repl, string, count=0, flags=0)` returns string
- [ ] `subn(pattern, repl, string, count=0, flags=0)` returns (string, count)
- [ ] `split(pattern, string, maxsplit=0, flags=0)` returns list
- [ ] `escape(pattern)` returns escaped string
- [ ] Match object `.group()`, `.groups()`, `.groupdict()`, `.span()`, `.start()`, `.end()`
- [ ] Named groups via `(?P<name>...)` syntax
- [ ] Flag constants: `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`, `ASCII`, `UNICODE`
- [ ] `re.error` exception raised for invalid patterns
- [ ] Pattern object `.pattern`, `.flags`, `.groups`, `.groupindex` attributes

### shadow-json (FR-003)
- [ ] PyO3 module `shadow_json` compiles and is importable
- [ ] `dumps(obj)` serializes Python objects to JSON string
- [ ] `dumps()` supports `indent` (int or None)
- [ ] `dumps()` supports `sort_keys` (bool)
- [ ] `dumps()` supports `separators` (tuple)
- [ ] `dumps()` supports `default` (callable)
- [ ] `dumps()` supports `ensure_ascii` (bool)
- [ ] `loads(s)` deserializes JSON string to Python objects
- [ ] `loads()` supports `object_hook` (callable)
- [ ] `loads()` supports `parse_float` (callable)
- [ ] `dump(obj, fp)` writes to file-like object
- [ ] `load(fp)` reads from file-like object
- [ ] `JSONDecodeError` exception with `msg`, `doc`, `pos`, `lineno`, `colno` attributes
- [ ] Correct type mapping: JSON null -> None, true/false -> bool, number -> int/float, string -> str, array -> list, object -> dict

### shadow-hashlib (FR-004)
- [ ] PyO3 module `shadow_hashlib` compiles and is importable
- [ ] `sha256()` constructor with optional `data` argument
- [ ] `sha512()` constructor with optional `data` argument
- [ ] `sha384()` constructor with optional `data` argument
- [ ] `sha224()` constructor with optional `data` argument
- [ ] `sha1()` constructor with optional `data` argument
- [ ] `md5()` constructor with optional `data` argument
- [ ] `new(name, data=b"")` dynamic constructor
- [ ] Hash object `.update(data)` for incremental hashing
- [ ] Hash object `.digest()` returns bytes
- [ ] Hash object `.hexdigest()` returns hex string
- [ ] Hash object `.copy()` returns independent copy
- [ ] Hash object `.name` attribute
- [ ] Hash object `.digest_size` attribute
- [ ] Hash object `.block_size` attribute
- [ ] `algorithms_available` set attribute
- [ ] `algorithms_guaranteed` set attribute

### shadow-decimal (FR-005)
- [ ] PyO3 module `shadow_decimal` compiles and is importable
- [ ] `Decimal(value)` constructor from string, int, float, tuple
- [ ] Arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- [ ] Comparison operators: `<`, `<=`, `==`, `!=`, `>=`, `>`
- [ ] `quantize(exp, rounding=None)` method
- [ ] `to_eng_string()` method
- [ ] `is_nan()`, `is_infinite()`, `is_zero()`, `is_signed()` predicates
- [ ] `as_tuple()` returning DecimalTuple(sign, digits, exponent)
- [ ] `Decimal("inf")`, `Decimal("-inf")`, `Decimal("NaN")` special values
- [ ] `getcontext()` and `setcontext()` for precision/rounding control
- [ ] `localcontext()` context manager
- [ ] `str()` and `repr()` output matches CPython format
- [ ] Exception classes: `InvalidOperation`, `DivisionByZero`, `Overflow`

### Import Hook (FR-006, FR-007, FR-010)
- [ ] `activate(tiers="A")` intercepts all 5 Tier A module imports
- [ ] `deactivate()` restores original import behavior
- [ ] `from datetime import datetime` works (attribute-level access)
- [ ] `conftest_plugin.py` activates hook automatically during pytest
- [ ] Fallback to CPython stdlib with `warnings.warn()` when extension not available
- [ ] No corruption of `sys.modules` after activate/deactivate cycle

### Build (FR-008)
- [ ] `maturin develop` succeeds for shadow-datetime
- [ ] `maturin develop` succeeds for shadow-re
- [ ] `maturin develop` succeeds for shadow-json
- [ ] `maturin develop` succeeds for shadow-hashlib
- [ ] `maturin develop` succeeds for shadow-decimal
- [ ] All 5 crates compile without warnings in release mode

### Equivalence Tests (FR-009)
- [ ] `test_datetime_equiv.py` exists and covers constructors, arithmetic, formatting, parsing, timezones
- [ ] `test_re_equiv.py` exists and covers compile, match, search, findall, sub, split, named groups, flags
- [ ] `test_json_equiv.py` exists and covers dumps/loads with all option combinations, edge cases, errors
- [ ] `test_hashlib_equiv.py` exists and covers all algorithms, incremental hashing, digest/hexdigest, copy
- [ ] `test_decimal_equiv.py` exists and covers arithmetic, rounding, special values, context, string conversion
- [ ] Each test compares shadow output against CPython stdlib output
- [ ] All equivalence tests pass

## Success Criteria Verification

- [ ] SC-001: `type(datetime.datetime).__module__` contains `shadow` when hook active
- [ ] SC-002: `re.search(r'\d+', '123').group()` returns `'123'` via shadow
- [ ] SC-003: `json.dumps({"a": 1})` produces correct output via shadow
- [ ] SC-004: `hashlib.sha256(b"test").hexdigest()` matches known hash via shadow
- [ ] SC-005: `str(Decimal("0.1") + Decimal("0.2"))` equals `"0.3"` via shadow
- [ ] SC-006: All 5 crates build with `maturin develop` in under 120 seconds
- [ ] SC-007: `pytest rust/tests/equivalence/` passes with zero failures
- [ ] SC-008: activate/deactivate cycle leaves sys.modules/sys.meta_path clean
- [ ] SC-009: Import time overhead is under 50ms per shadow module
