"""
Equivalence test template.

Each shadow library has a test file that runs the same assertions
with and without the import hook. Behavioural divergence is a bug.

Copy this template and adapt for each library.
"""
import pytest
import importlib
from refactory_shadows.hook import activate, deactivate


@pytest.fixture(params=["cpython", "shadow"])
def module_under_test(request):
    """Parametrized fixture: test against both CPython and shadow."""
    if request.param == "shadow":
        activate()
    else:
        deactivate()

    # Reload the module to pick up hook change
    # Replace 'datetime' with the target module name
    import datetime
    importlib.reload(datetime)
    yield datetime

    deactivate()


# Example equivalence test — replace with library-specific assertions
def test_equivalence_placeholder(module_under_test):
    """Placeholder — implement per-library equivalence tests."""
    assert module_under_test is not None
