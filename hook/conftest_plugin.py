"""pytest plugin for automatic shadow library activation."""

def pytest_configure(config):
    from refactory_shadows.hook import activate
    tiers = config.getini("refactory_shadow_tiers") or "ABC"
    activate(tiers=tiers)
