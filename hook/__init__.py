"""
Refactory Shadow Library Import Hook.

Intercepts stdlib imports and loads Rust-backed shadow libraries transparently.
Activated by a single line in conftest.py or via the pytest plugin.

Usage:
    from refactory_shadows.hook import activate
    activate()  # Default: Priorities A-C (Ferrum-safe, no I/O)
    activate(priorities="ABCD")  # All priorities (general Refactory)
"""

import sys
import importlib

# Full shadow map — all 19 libraries
_SHADOW_MAP = {
    # Priority A — Core
    "datetime":     "refactory_shadows.chrono",
    "re":           "refactory_shadows.regex",
    "json":         "refactory_shadows.serde_json",
    "hashlib":      "refactory_shadows.digest",
    "decimal":      "refactory_shadows.rust_decimal",
    # Priority B — Data Structures
    "collections":  "refactory_shadows.collections",
    "math":         "refactory_shadows.math",
    "itertools":    "refactory_shadows.itertools",
    # Priority C — Utilities
    "uuid":         "refactory_shadows.uuid",
    "base64":       "refactory_shadows.base64",
    "csv":          "refactory_shadows.csv",
    "struct":       "refactory_shadows.byteorder",
    "urllib.parse":  "refactory_shadows.url",
    "ipaddress":    "refactory_shadows.ipaddress",
    "io":           "refactory_shadows.io",
    # Priority D — Refactory-General
    "logging":      "refactory_shadows.logging",
    "pathlib":      "refactory_shadows.pathlib",
    "os.path":      "refactory_shadows.pathlib",
    "requests":     "refactory_shadows.reqwest",
    "functools":    "refactory_shadows.functools",
}

_PRIORITY_MODULES = {
    "A": {"datetime", "re", "json", "hashlib", "decimal"},
    "B": {"collections", "math", "itertools"},
    "C": {"uuid", "base64", "csv", "struct", "urllib.parse", "ipaddress", "io"},
    "D": {"logging", "pathlib", "os.path", "requests", "functools"},
}


class ShadowImportHook:
    """Intercepts stdlib imports and loads Rust-backed shadows."""

    def __init__(self, active_modules: set[str]):
        self._active = {k: v for k, v in _SHADOW_MAP.items() if k in active_modules}

    def find_module(self, fullname, path=None):
        if fullname in self._active:
            return self
        return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        shadow_name = self._active[fullname]
        shadow_mod = importlib.import_module(shadow_name)
        sys.modules[fullname] = shadow_mod
        return shadow_mod


def activate(priorities: str = "ABC"):
    """
    Activate shadow library loading.

    Args:
        priorities: Which priorities to activate. Default "ABC" (Ferrum-safe).
                    Use "ABCD" for general Refactory use (includes I/O libraries).
    """
    active_modules: set[str] = set()
    for p in priorities.upper():
        active_modules |= _PRIORITY_MODULES.get(p, set())

    if not any(isinstance(h, ShadowImportHook) for h in sys.meta_path):
        sys.meta_path.insert(0, ShadowImportHook(active_modules))


def deactivate():
    """Remove the shadow import hook."""
    sys.meta_path[:] = [h for h in sys.meta_path if not isinstance(h, ShadowImportHook)]
