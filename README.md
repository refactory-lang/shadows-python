# refactory-shadows

Python shadow libraries for the Refactory pipeline. PyO3/maturin packages that expose API-identical Rust-backed wrappers for Python standard library modules.

**The principle:** If it's an importable Python module that maps to a Rust crate, it gets a shadow library. The api-map.yaml should contain zero library-level entries — only builtin type methods and language construct transforms.

## Why Shadow Libraries?

In a traditional translation pipeline, an API mapping database translates between independent implementations: `datetime` → `chrono`, `re` → `regex`. Each entry is an *assumed equivalence* that no test verifies. Shadow libraries eliminate this:

1. **Development:** Developer writes `from datetime import datetime` — vanilla Python.
2. **Testing:** Import hook loads `chrono` via PyO3. Tests exercise real Rust code.
3. **Translation:** Tier 0 rewrites imports. Tier 1 does a module-path rewrite. Zero semantic translation.

## Shadow Library Inventory

### Tier A — Core (Ferrum-critical)

| Package | Python Module | Rust Crate | Status |
|---------|--------------|------------|--------|
| `shadow-datetime` | `datetime` | `chrono` | 🔲 Planned |
| `shadow-re` | `re` | `regex` | 🔲 Planned |
| `shadow-json` | `json` | `serde_json` | 🔲 Planned |
| `shadow-hashlib` | `hashlib` | `sha2` + `md-5` | 🔲 Planned |
| `shadow-decimal` | `decimal` | `rust_decimal` | 🔲 Planned |

### Tier B — Data Structures

| Package | Python Module | Rust Crate | Status |
|---------|--------------|------------|--------|
| `shadow-collections` | `collections` | `indexmap` + `std` | 🔲 Planned |
| `shadow-math` | `math` | `std` + `num-traits` | 🔲 Planned |
| `shadow-itertools` | `itertools` | `itertools` | 🔲 Planned |

### Tier C — Utilities

| Package | Python Module | Rust Crate | Status |
|---------|--------------|------------|--------|
| `shadow-uuid` | `uuid` | `uuid` | 🔲 Planned |
| `shadow-base64` | `base64` | `base64` | 🔲 Planned |
| `shadow-csv` | `csv` | `csv` | 🔲 Planned |
| `shadow-struct` | `struct` | `byteorder` | 🔲 Planned |
| `shadow-urllib` | `urllib.parse` | `url` | 🔲 Planned |
| `shadow-ipaddress` | `ipaddress` | `std::net` | 🔲 Planned |
| `shadow-io` | `io` | `std::io::Cursor` | 🔲 Planned |

### Tier D — Refactory-General (deferrable)

| Package | Python Module | Rust Crate | Status |
|---------|--------------|------------|--------|
| `shadow-logging` | `logging` | `log` + `tracing` | 🔲 Planned |
| `shadow-pathlib` | `pathlib` | `std::path` | 🔲 Planned |
| `shadow-requests` | `requests` | `reqwest` | 🔲 Planned |
| `shadow-functools` | `functools` | `cached` | 🔲 Planned |

## Architecture

```
refactory-shadows/
├── Cargo.toml                    # Workspace root
├── pyproject.toml                # Metapackage
├── crates/
│   ├── shadow-datetime/          # Each crate = one shadow library
│   │   ├── Cargo.toml
│   │   ├── src/lib.rs            # PyO3 module
│   │   └── python/               # Type stubs
│   ├── shadow-re/
│   └── ...
├── hook/                         # sys.meta_path import hook
│   ├── __init__.py
│   └── conftest_plugin.py        # pytest auto-activation
├── tier0-rules/
│   └── rewrite-imports.yml       # ast-grep rules (copied to python-to-rust)
└── tests/equivalence/            # Per-library CPython ↔ Shadow tests
```

## Import Hook

```python
# conftest.py — one line to activate
from refactory_shadows.hook import activate
activate()

# Developer code is unchanged:
from datetime import datetime
import re
import json
```

## License

Apache-2.0
