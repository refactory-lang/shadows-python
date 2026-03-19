<!-- codemod-skill-discovery:begin -->
## Codemod Skill Discovery
This section is managed by `codemod` CLI.

- Core skill: `.agents/skills/codemod/SKILL.md`
- Package skills: `.agents/skills/<package-skill>/SKILL.md`
- List installed Codemod skills: `npx codemod agent list --harness antigravity --format json`

<!-- codemod-skill-discovery:end -->

## Project: shadows-python

Python shadow libraries for the Refactory pipeline. Part of the [refactory-lang](https://github.com/refactory-lang) organization. Provides API-identical Python wrappers backed by target-language (Rust) implementations via PyO3/maturin FFI bindings. Tests exercise the real compiled code, eliminating assumed API equivalences.

### Architecture

- **Import hook** (`hook/`): Target-agnostic import hook that redirects Python imports to shadow implementations at runtime
  - `__init__.py`: `ShadowImportHook` class + `activate()` entry point
  - `conftest_plugin.py`: pytest plugin for automatic shadow activation
  - `tests/`: Hook unit tests
- **Rust target** (`rust/`): PyO3/maturin shadow crate workspace
  - `Cargo.toml`: Workspace root for 19 shadow crates
  - `crates/`: Individual shadow crates (e.g., `shadow-datetime` -> chrono, `shadow-re` -> regex)
  - `stage0-rules/`: ast-grep import rewrite rules for Stage 0
  - `tests/equivalence/`: CPython vs. shadow equivalence tests
- **Specs** (`specs/`): Implementation specifications

### Running

```bash
# Build Rust shadow crates
cd rust && maturin develop

# Run equivalence tests
cd rust && pytest tests/equivalence/

# Activate import hook in tests (add to conftest.py)
from refactory_shadows.hook import activate
activate()
```

### Key Files

| File | Purpose |
|------|---------|
| `hook/__init__.py` | `ShadowImportHook` + `activate()` |
| `hook/conftest_plugin.py` | pytest auto-activation plugin |
| `rust/Cargo.toml` | Shadow crate workspace root |
| `rust/crates/shadow-datetime/` | `datetime` -> `chrono` shadow |
| `rust/crates/shadow-re/` | `re` -> `regex` shadow |
| `rust/crates/shadow-json/` | `json` -> `serde_json` shadow |
| `rust/stage0-rules/` | ast-grep import rewrite rules |

### Shadow Library Inventory (19 crates)

Priority A (Core): datetime, re, json, hashlib, decimal
Priority B (Data): collections, math, itertools
Priority C (Util): uuid, base64, csv, struct, urllib, ipaddress, io
Priority D (General): logging, pathlib, requests, functools
