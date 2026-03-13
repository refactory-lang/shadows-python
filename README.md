<p align="center">
  <a href="https://github.com/refactory-lang"><img src="https://raw.githubusercontent.com/refactory-lang/.github/main/assets/refactory-logo.svg" alt="Refactory" width="300"></a>
</p>

# shadows-python

Python shadow libraries for the Refactory pipeline. API-identical wrappers for Python standard library modules, backed by target-language implementations.

**The principle:** If it's an importable Python module that maps to a target-language library, it gets a shadow library. Tests exercise the real target-language code via FFI bindings.

## Why Shadow Libraries?

In a traditional translation pipeline, an API mapping database translates between independent implementations: `datetime` → `chrono`, `re` → `regex`. Each entry is an *assumed equivalence* that no test verifies. Shadow libraries eliminate this:

1. **Development:** Developer writes `from datetime import datetime` — vanilla Python.
2. **Testing:** Import hook loads the target-language implementation via FFI. Tests exercise real compiled code.
3. **Translation:** Tier 0 rewrites imports. Tier 1 does a module-path rewrite. Zero semantic translation.

## Structure

```
shadows-python/
├── hook/                           # Shared import hook (target-agnostic)
│   ├── __init__.py                 # ShadowImportHook + activate()
│   └── conftest_plugin.py          # pytest auto-activation
├── rust/                           # Target: Rust (PyO3/maturin)
│   ├── Cargo.toml                  # Workspace root
│   ├── pyproject.toml              # Metapackage
│   ├── crates/                     # 19 PyO3 shadow crates
│   │   ├── shadow-datetime/        # datetime → chrono
│   │   ├── shadow-re/              # re → regex
│   │   ├── shadow-json/            # json → serde_json
│   │   └── ...
│   ├── tier0-rules/                # ast-grep import rewrite rules
│   └── tests/equivalence/          # CPython ↔ Shadow equivalence tests
├── go/                             # Target: Go (future)
└── README.md
```

## Shadow Library Inventory (Rust target)

### Tier A — Core

| Package | Python Module | Rust Crate |
|---------|--------------|------------|
| `shadow-datetime` | `datetime` | `chrono` |
| `shadow-re` | `re` | `regex` |
| `shadow-json` | `json` | `serde_json` |
| `shadow-hashlib` | `hashlib` | `sha2` + `md-5` |
| `shadow-decimal` | `decimal` | `rust_decimal` |

### Tier B — Data Structures

| Package | Python Module | Rust Crate |
|---------|--------------|------------|
| `shadow-collections` | `collections` | `indexmap` + `std` |
| `shadow-math` | `math` | `std` + `num-traits` |
| `shadow-itertools` | `itertools` | `itertools` |

### Tier C — Utilities

| Package | Python Module | Rust Crate |
|---------|--------------|------------|
| `shadow-uuid` | `uuid` | `uuid` |
| `shadow-base64` | `base64` | `base64` |
| `shadow-csv` | `csv` | `csv` |
| `shadow-struct` | `struct` | `byteorder` |
| `shadow-urllib` | `urllib.parse` | `url` |
| `shadow-ipaddress` | `ipaddress` | `std::net` |
| `shadow-io` | `io` | `std::io::Cursor` |

### Tier D — General

| Package | Python Module | Rust Crate |
|---------|--------------|------------|
| `shadow-logging` | `logging` | `log` + `tracing` |
| `shadow-pathlib` | `pathlib` | `std::path` |
| `shadow-requests` | `requests` | `reqwest` |
| `shadow-functools` | `functools` | `cached` |

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

## Adding a New Target Language

Create a new directory at the root (e.g. `go/`) with the target-specific build system and crate/package structure. The import hook and equivalence test templates are shared.

## License

Apache-2.0
